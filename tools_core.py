# -*- coding: utf-8 -*-
"""
tools_core.py — LÕI dùng chung cho demo 2 (hướng MCP).

Tái dùng NGUYÊN các thuật toán ĐỌC đã kiểm chứng của demo 1 (chống bịa, font TCVN3,
qty_index, bảng thép...) NHƯNG:
  - Gói thành lớp `Drawing` GIỮ luôn đối tượng ezdxf `doc` trong RAM -> để RENDER được.
  - Thêm năng lực TRỰC QUAN: render 1 VÙNG bản vẽ ra ảnh + KHOANH ĐỎ cấu kiện (highlight) —
    điều demo 1 (đọc file tĩnh, chỉ trả chữ) không làm được.

Module này KHÔNG phụ thuộc Flask/MCP -> dùng được cho cả MCP server lẫn host.
"""
import os, re, time, uuid, logging, unicodedata, math
from collections import Counter

import matplotlib
matplotlib.use("Agg")  # headless -> chạy trên cloud Linux không cần màn hình
logging.getLogger("ezdxf").setLevel(logging.ERROR)  # bớt log "skipped invisible/relative point" khi render
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, HatchPolicy

from vntext import to_unicode
from dwgconv import convert_dwg_to_dxf

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE, "_uploads")
RENDER_DIR = os.path.join(BASE, "_renders")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)
# Giới hạn .dxf đọc (MB) — giữ như demo 1 (an toàn RAM). Lên gói mạnh -> tăng env.
READFILE_MAX_MB = int(os.environ.get("READFILE_MAX_MB", "45"))

# ----------------------------------------------------------------------------
# CHUẨN HOÁ (port nguyên từ demo 1 app.py — đã test kỹ)
# ----------------------------------------------------------------------------
def unaccent(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()

_DIAM_RE = re.compile(r"(?:ø|φ|phi|d)\s*0*(\d+)")
_GARBLE_FOLD = str.maketrans({"ö": "u", "Ö": "U", "ä": "o", "Ä": "O",
                              "æ": "o", "Æ": "O", "õ": "e", "Õ": "E"})
def _garble_fold(s): return (s or "").translate(_GARBLE_FOLD)
def _norm(s): return _DIAM_RE.sub(lambda m: "ø" + m.group(1), unaccent(_garble_fold(s)))
def _norm_label(s): return unaccent(_garble_fold(s))

def _to_num(s):
    try:
        return float(str(s).replace(",", ".").strip())
    except Exception:
        return None

# ---- Bảng thống kê thép (port) ----
def _acc_thep(thep, att):
    tl = _to_num(att.get("TL"))
    if tl is None: return
    dk = str(att.get("DK") or "").strip()
    key = ("Ø%s" % dk) if dk else "Ø?"
    row = thep.setdefault(key, {"so_thanh": 0, "dai_m": 0.0, "kg": 0.0, "rows": 0})
    row["kg"] += tl; row["rows"] += 1
    sla = _to_num(att.get("SLA"))
    if sla is not None: row["so_thanh"] += int(sla)
    dt = _to_num(att.get("DT"))
    if dt is not None: row["dai_m"] += dt

def _acc_thep_hinh(thep_hinh, att):
    tl = _to_num(att.get("TL"))
    if tl is None: return
    show = (att.get("SHOW") or "").strip() or "(không tên)"
    row = thep_hinh.setdefault(show, {"so": 0, "kg": 0.0, "rows": 0})
    row["kg"] += tl; row["rows"] += 1
    sla = _to_num(att.get("SLA"))
    if sla is not None: row["so"] += int(sla)

# ---- Nhận diện số lượng (port) ----
_QTY_RE = re.compile(r"(?:so\s*luong|slg|qty)\s*[:=\-]?\s*0*(\d+)"
                     r"|\bsl\s*[:=\-]\s*0*(\d+)"
                     r"|tong\s*(?:so|cong)\b[^\d\n]{0,18}?0*(\d+)")
_QTY_STRIP = re.compile(r"(?:so\s*luong|slg|qty)\s*[:=\-]?\s*0*\d+\s*(?:bo|cai|cay|thanh|tam|vien|coc)?"
                        r"|\bsl\s*[:=\-]\s*0*\d+"
                        r"|tong\s*(?:so|cong)\b[^\d\n]{0,18}?0*\d+\s*(?:bo|cai|cay|thanh|tam|vien|coc)?")
_DIM_LABEL_RE = re.compile(r"^[()\s]*[lhrdøb]?\s*[=:]?\s*\d+([.,]\d+)?\s*(m|mm|cm)?[()\s]*$")
_CODE_TOKEN_RE = re.compile(r"[a-zđ]{1,4}-?\d+[a-z]?")
_UNIT_WORDS = set("bo cai cay tam vien coc phong thanh md kg tan m m2 m3 so luong slg qty cua tong".split())

def _qty_match(text_norm):
    m = _QTY_RE.search(text_norm)
    if not m: return None
    for g in m.groups():
        if g is not None: return int(g)
    return None

def _is_dim_label(n): return bool(_DIM_LABEL_RE.match((n or "").strip()))

def _looks_like_title(n):
    n = (n or "").strip()
    if not n or _is_dim_label(n): return False
    if _CODE_TOKEN_RE.search(n): return True
    return any(w not in _UNIT_WORDS for w in re.findall(r"[a-z]{2,}", n))


# ============================================================================
# GIAI ĐOẠN 2 — CẤU HÌNH ENGINE TÍNH TOÁN (takeoff)
# ============================================================================
_TIETDIEN_RE = re.compile(r"(\d{2,4})\s*[xX×*]\s*(\d{2,4})")  # '220x220', '(220 x 500)', '80X80' (X hoa)

# ---- ĐƠN VỊ tiết diện cm/mm (port demo 1: DATA-DRIVEN + ngưỡng 130 + cờ mơ hồ; KHÔNG 'mặc định mm') ----
# Bản vẽ VN thật tồn tại CẢ HAI quy ước và 0 file ghi rõ đơn vị: file cm cạnh ≤110 (nhà 9T: 22x40..80x80 cm),
# file mm cạnh ≥220 (Gia Lộc/fixture: 220x400 mm) -> KHOẢNG TRỐNG [111,219]; 130 nằm giữa + trên cạnh-cm lớn
# nhất quan sát (110) + dưới ngưỡng cần (140 phải ra mm). 'Mặc định mm' sẽ đọc sai 12 cột 9T (cm) thành 1/100.
_SECT_CM_MAX = 130
_SECT_PAIR_R = 1500   # bán kính ghép MÃ↔TIẾT DIỆN theo tọa độ (bảng cột: mã và 'AxB' ở text riêng)
# Tiết diện 'AxB' đứng riêng (kèm đơn vị mm/cm nếu có) + inline '(AxB)mm'. Cho X hoa/thường; đơn vị chỉ bắt khi
# TÁCH BIỆT (ranh giới từ) -> không grab 'mm' từ '(300x600)mm2' (bịa đơn vị từ token dài).
_SECT_STD_RE = re.compile(r"^\s*\(?\s*(\d{2,4})\s*[xX×*]\s*(\d{2,4})\s*\)?\s*([mMcC][mM])?\s*$")
_SECT_INLINE_RE = re.compile(r"\(\s*(\d{2,4})\s*[xX×*]\s*(\d{2,4})\s*\)\s*(?:([mMcC][mM])(?![A-Za-z0-9]))?")
# Mã cấu kiện KẾT CẤU (cột/dầm/đài/giằng): c/d/dm/dc/g/gm/m + '-' hoặc '.' + số + đuôi chữ (c-1, dm-1, d2.01a, gm.03b).
_STRUCTCODE_RE = re.compile(r"^\s*\(?\s*((?:dc|dm|gm|mc|d2|c|d|g|m)[-.]?\d+[a-z]?)\s*\)?\s*$", re.IGNORECASE)
_STRUCTCODE_INLINE_RE = re.compile(r"(?<![a-z0-9])((?:dc|dm|gm|mc|d2|c|d|g|m)[-.]?\d+[a-z]?)(?![a-z0-9])", re.IGNORECASE)

# ---- BẢNG THỐNG KÊ CỬA: ghép MÃ CỬA <-> KÍCH THƯỚC R×C (port từ demo 1 _build_size_index) ----
_DOOR_SIZE_RE = re.compile(r"^\s*\(?\s*(\d{2,5})\s*[x×*]\s*(\d{2,5})\s*\)?\s*(?:mm)?\s*$", re.IGNORECASE)
_DOOR_SIZE_INLINE_RE = re.compile(r"(?<![\d.])(\d{2,5})\s*[x×*]\s*(\d{2,5})(?![\d.])", re.IGNORECASE)
_DOOR_CODE_RE = re.compile(r"^\s*\(?\s*((?:sk|sw|vk|w|d|s)-?\d+[a-z]?)\s*\)?\s*$", re.IGNORECASE)
_DOOR_CODE_INLINE_RE = re.compile(r"(?<![a-z0-9])((?:sk|sw|vk|w|d|s)-?\d+[a-z]?)(?![a-z0-9])")
_DOOR_SIZE_MIN, _DOOR_SIZE_MAX, _DOOR_PAIR_R = 300, 9000, 1100
# Kích thước 1 Ô CỬA/CỬA SỔ/VÁCH hợp lý (mm) — dùng lọc dim khi gán-dim: loại dim chi tiết nhỏ (50mm)
# và dim công trình lớn (trục/nhịp 10m+). Rộng rãi để không loại nhầm vách kính lớn; không có dim hợp lý
# -> trả None (báo thiếu, KHÔNG bịa số phi lý).
_OPENING_DIM_LO, _OPENING_DIM_HI = 400, 6000
_SL_LO_MAX = 100000   # trần SL lỗ 1 lần khai (chống số vô lý/tràn: không tường nào có >100k lỗ)


def _plausible_door_size(w, h):
    """Loại gạch (600x600 max<1200), thép hộp (50x100). Cửa/cửa sổ thực: cạnh lớn ≥1200mm."""
    return _DOOR_SIZE_MIN <= w <= _DOOR_SIZE_MAX and _DOOR_SIZE_MIN <= h <= _DOOR_SIZE_MAX and max(w, h) >= 1200


def _build_door_size_index(texts):
    """Ghép MÃ CỬA <-> R×C từ bảng thống kê / ghi chú: mutual nearest neighbor + cổng tin cậy.
    confident=True CHỈ khi size NHẤT QUÁN (frac≥0.8) + ô gần (≤1000u) -> chống ghép lẫn. Port từ demo 1."""
    codes, sizes, inline = [], [], []
    for t in texts:
        s = (t.get("vn") or "").strip()
        x, y = t.get("x", 0.0), t.get("y", 0.0)
        mc = _DOOR_CODE_RE.match(s)
        if mc:
            codes.append({"code": mc.group(1).lower().replace(" ", ""), "x": x, "y": y, "handle": t["handle"]}); continue
        ms = _DOOR_SIZE_RE.match(s)
        if ms:
            w, h = int(ms.group(1)), int(ms.group(2))
            if _plausible_door_size(w, h): sizes.append({"w": w, "h": h, "x": x, "y": y, "handle": t["handle"]})
            continue
        sin = _DOOR_SIZE_INLINE_RE.findall(s)      # inline: đoạn chứa CẢ mã lẫn R×C, chỉ ghép khi DUY NHẤT 1+1
        if len(sin) == 1:
            cin = set(_DOOR_CODE_INLINE_RE.findall(_norm_label(s)))
            if len(cin) == 1:
                w, h = int(sin[0][0]), int(sin[0][1])
                if _plausible_door_size(w, h): inline.append({"code": next(iter(cin)), "w": w, "h": h, "handle": t["handle"]})

    def _near(item, pool):
        best, bd = None, 1e18
        for p in pool:
            d = ((item["x"] - p["x"]) ** 2 + (item["y"] - p["y"]) ** 2) ** 0.5
            if d < bd: bd, best = d, p
        return best, bd

    for sz in sizes: sz["_nc"], _ = _near(sz, codes)
    cand = {}
    for c in codes:
        sz, d = _near(c, sizes)
        if not sz or d > _DOOR_PAIR_R: continue
        if sz["_nc"] and sz["_nc"]["code"] == c["code"]:          # MUTUAL nearest -> cùng một mã cửa
            cand.setdefault(c["code"], []).append((sz["w"], sz["h"], d, sz["handle"]))
    for e in inline:                                              # inline = bằng chứng mạnh (dist=0)
        cand.setdefault(e["code"], []).append((e["w"], e["h"], 0.0, e["handle"]))
    out = []
    for code, lst in cand.items():
        whs = [(w, h) for w, h, _, _ in lst]
        cnt = Counter(whs); n = max(cnt.values())
        (w, h) = min(k for k, v in cnt.items() if v == n)         # tie-break tất định theo giá trị
        frac = n / len(whs)
        near = min(d for ww, hh, d, _ in lst if (ww, hh) == (w, h))
        handle = next(hd for ww, hh, d, hd in lst if (ww, hh) == (w, h))
        out.append({"code": code, "w": w, "h": h, "area_m2": round(w * h / 1e6, 2), "n": len(whs),
                    "frac": round(frac, 2), "near": round(near), "handle": handle,
                    "confident": frac >= 0.8 and near <= 1000})
    out.sort(key=lambda e: e["code"])
    return out


# ---- TIẾT DIỆN kết cấu: đơn vị cm/mm + ghép mã↔tiết diện theo tọa độ (port demo 1 _build_section_index) ----
def _is_structcode(code):
    """Mã có phải cấu kiện KẾT CẤU (cột/dầm/đài/giằng)? Loại token rác/vật liệu (vd 'hop-50x100x2', '(sl=2;')."""
    return bool(_STRUCTCODE_RE.match((code or "").strip()))


def _unit_ambiguous_sect(a, b):
    """Đơn vị THẬT SỰ nhập nhằng <=> CẢ HAI diễn giải cm & mm đều là tiết diện KHẢ DĨ (port demo 1 _unit_ambiguous):
    cm-interp khả dĩ khi cạnh lớn ≤2.0m; mm-interp khả dĩ khi cạnh nhỏ ≥40mm & cạnh lớn ≤2.0m. Bắt lệch 10-100×."""
    lo, hi = min(a, b), max(a, b)
    return hi <= 200 and (lo >= 40 and hi <= 2000)


def _sect_to_mm(a, b, stated=None):
    """Chuẩn hoá tiết diện (a,b) về mm-TƯƠNG ĐƯƠNG (cm ->×10). Trả (a_mm, b_mm, don_vi, suy_doan).
    - Đơn vị GHI RÕ (mm/cm) -> tin bản vẽ, suy_doan=False. - Không ghi -> suy đoán ngưỡng 130 (cm nếu max<130)."""
    su = (stated or "").strip().lower()
    if su in ("mm", "cm"):
        unit, sd = su, False
    else:
        unit, sd = ("cm" if max(a, b) < _SECT_CM_MAX else "mm"), _unit_ambiguous_sect(a, b)
    f = 10.0 if unit == "cm" else 1.0
    return int(round(a * f)), int(round(b * f)), unit, sd


def _plausible_section_mm(a_mm, b_mm):
    """Cổng hợp lý trên mm-TƯƠNG ĐƯƠNG (unit-aware; thay cổng '50<=a' cũ thiên mm loại nhầm cột cm nhỏ): 50..5000mm."""
    lo, hi = min(a_mm, b_mm), max(a_mm, b_mm)
    return 50 <= lo and hi <= 5000


def _build_section_index(texts):
    """Ghép MÃ kết cấu <-> TIẾT DIỆN 'AxB' qua TỌA ĐỘ (mutual nearest neighbor) + inline 'CODE (AxB)'.
    Đọc được bảng cột (mã và tiết diện ở text RIÊNG, vd nhà 9T 'c-3' ... '(80X80)') mà cách 'cùng-text' bỏ sót.
    Đơn vị: đọc GHI RÕ (mm/cm) nếu có, else SUY ĐOÁN ngưỡng 130. Mỗi entry: a,b = mm-TƯƠNG ĐƯƠNG (cm đã ×10)
    + a_raw/b_raw + don_vi + suy_doan_don_vi + confident + đa-tiết-diện. Port demo 1."""
    codes, secs, inline = [], [], []
    for t in texts:
        s = (t.get("vn") or "").strip()
        x, y = t.get("x", 0.0), t.get("y", 0.0)
        mc = _STRUCTCODE_RE.match(s)
        if mc:
            codes.append({"code": mc.group(1).lower().replace(" ", ""), "x": x, "y": y, "handle": t["handle"]}); continue
        ms = _SECT_STD_RE.match(s)
        if ms:
            a, b, u = int(ms.group(1)), int(ms.group(2)), (ms.group(3) or "").lower()
            amm, bmm, unit, sd = _sect_to_mm(a, b, u)
            if _plausible_section_mm(amm, bmm):
                secs.append({"a": amm, "b": bmm, "ar": a, "br": b, "u": unit, "sd": sd, "x": x, "y": y, "handle": t["handle"]})
            continue
        si = _SECT_INLINE_RE.findall(s)                      # inline: đoạn chứa CẢ mã lẫn tiết diện (ghép khi DUY NHẤT 1+1)
        if len(si) == 1:
            ci = set(_STRUCTCODE_INLINE_RE.findall(_norm_label(s)))
            if len(ci) == 1:
                a, b, u = int(si[0][0]), int(si[0][1]), (si[0][2] or "").lower()
                amm, bmm, unit, sd = _sect_to_mm(a, b, u)
                if _plausible_section_mm(amm, bmm):
                    inline.append({"code": next(iter(ci)), "a": amm, "b": bmm, "ar": a, "br": b, "u": unit, "sd": sd, "handle": t["handle"]})

    def _near(item, pool):
        best, bd = None, 1e18
        for p in pool:
            dd = ((item["x"] - p["x"]) ** 2 + (item["y"] - p["y"]) ** 2) ** 0.5
            if dd < bd: bd, best = dd, p
        return best, bd

    for sec in secs: sec["_nc"], _ = _near(sec, codes)
    cand = {}
    for c in codes:
        sec, dd = _near(c, secs)
        if not sec or dd > _SECT_PAIR_R: continue
        if sec["_nc"] and sec["_nc"]["code"] == c["code"]:          # MUTUAL nearest -> cùng một mã kết cấu
            cand.setdefault(c["code"], []).append((sec["a"], sec["b"], dd, sec["handle"], sec["u"], sec["sd"], sec["ar"], sec["br"]))
    for e in inline:                                                # inline = bằng chứng mạnh (dist=0)
        cand.setdefault(e["code"], []).append((e["a"], e["b"], 0.0, e["handle"], e["u"], e["sd"], e["ar"], e["br"]))

    out = []
    for code, lst in cand.items():
        abs_ = [(a, b) for a, b, *_ in lst]
        cnt = Counter(abs_); n = max(cnt.values())
        (a, b) = min(k for k, v in cnt.items() if v == n)          # tie-break tất định theo giá trị
        frac = n / len(abs_)
        near = min(d for aa, bb, d, *_ in lst if (aa, bb) == (a, b))
        pick = next(tp for tp in lst if (tp[0], tp[1]) == (a, b))
        _, _, _, handle, unit, sd, ar, br = pick
        distinct = sorted(set((tp[6], tp[7]) for tp in lst))       # (a_raw,b_raw) distinct -> cảnh báo đa tiết diện
        out.append({"code": code, "a": a, "b": b, "a_raw": ar, "b_raw": br, "don_vi": unit,
                    "suy_doan_don_vi": bool(sd), "n": len(abs_), "frac": round(frac, 2), "near": round(near),
                    "handle": handle, "nhieu_tiet_dien": len(set(abs_)) > 1, "so_tiet_dien": len(set(abs_)),
                    "cac_tiet_dien": distinct, "confident": frac >= 0.8 and near <= 1200})
    out.sort(key=lambda e: e["code"])
    return out


# ---- CAO ĐỘ -> CHIỀU CAO TẦNG điển hình (port từ demo 1 _build_levels) ----
_ELEV_RE = re.compile(r"^[+\-±]\s*\d{1,2}[.,]\d{2,3}$")                             # marker riêng: '+3.600', '±0.000'
_ELEV_IN_RE = re.compile(r"(?:([+±])|(?<![\w.])(-))\s*(\d{1,2}[.,]\d{3})(?![\d])")  # trong đoạn dài hơn
_FLOOR_H_LO, _FLOOR_H_HI = 2.5, 5.0   # chiều cao 1 TẦNG hợp lý (loại chiếu nghỉ/tầng lửng ~1.8, móng ~0.6)


def _parse_elev(sign, num):
    try: v = float(num.replace(",", "."))
    except Exception: return None
    return -v if sign == "-" else v


def _build_levels(texts):
    """Đọc CAO ĐỘ -> CHIỀU CAO TẦNG điển hình (mode hiệu cao độ trong [2.5,5]m, bền vững dù thiếu vài mức).
    Trả {levels,min,max,typical_floor_h,n_tang_est} hoặc {} nếu không có cao độ. Port từ demo 1."""
    vals = []
    for t in texts:
        s = (t.get("vn") or "").strip(); ss = s.replace(" ", "")
        if _ELEV_RE.match(ss):
            v = _parse_elev("-" if ss[0] == "-" else "+", ss.lstrip("+-±"))
            if v is not None: vals.append(round(v, 3))
        else:
            for m in _ELEV_IN_RE.finditer(s):
                v = _parse_elev("-" if m.group(2) else "+", m.group(3))
                if v is not None: vals.append(round(v, 3))
    if not vals: return {}
    cnt = Counter(vals)
    clusters = []                                            # gộp cao độ gần nhau (3.55/3.59/3.60 -> 1 mức)
    for v in sorted(cnt):
        if clusters and v - clusters[-1][-1] <= 0.15: clusters[-1].append(v)
        else: clusters.append([v])
    levels = sorted(max(cl, key=lambda x: cnt[x]) for cl in clusters if sum(cnt[x] for x in cl) >= 4)
    if len(levels) < 2: return {}
    gaps = [round(levels[i + 1] - levels[i], 3) for i in range(len(levels) - 1)]
    floor_gaps = [g for g in gaps if _FLOOR_H_LO <= g <= _FLOOR_H_HI]
    typical = Counter(floor_gaps).most_common(1)[0][0] if floor_gaps else None
    mx = max(levels)
    n_est = int(round(mx / typical)) if (typical and mx > 0) else None
    return {"levels": levels, "min": min(levels), "max": mx, "typical_floor_h": typical, "n_tang_est": n_est}


# ---- m³ GHI SẴN trên bản vẽ (port từ demo 1 _stated_volumes) ----
_M3_RE = re.compile(r"([\d][\d.,]*)\s*m\s*3\b|([\d][\d.,]*)\s*m³", re.IGNORECASE)
_M3_MIN = 5   # ngưỡng m³ tối thiểu (nhận cả khối lượng nhỏ 5-9 m³)
_M3_EXCLUDE_RE = re.compile(r"nuoc|vua|xi mang|ti le|dinh muc|keo|son|phu gia")  # ghi chú tỉ lệ/định mức -> loại

# --- Bóc tách kích thước tự do trong GHI CHÚ (Task B) — TRÍCH số, KHÔNG tự tính ---
_BT_3D = re.compile(r"(\d+(?:[.,]\d+)?)\s*[x×*]\s*(\d+(?:[.,]\d+)?)\s*[x×*]\s*(\d+(?:[.,]\d+)?)")
_BT_L = re.compile(r"\bl\s*=\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m)?", re.I)
_BT_M2 = re.compile(r"(\d+(?:[.,]\d+)?)\s{0,2}m2\b|(\d+(?:[.,]\d+)?)\s{0,2}m²", re.I)  # 'm2' liền, tránh 'm 2 tầng'
_BT_DAY = re.compile(r"\bday\s*[:=]?\s*(\d{2,4}(?:[.,]\d+)?)\b")          # dùng trên chuỗi _norm (không dấu)
# số lượng: 'SL: N' hoặc 'N viên/bộ/...'; (?!\s*/) loại '25 viên/m2' (MẬT ĐỘ, không phải tổng số)
_BT_SL = re.compile(r"(?:sl|so luong)\s*[:=]?\s*(\d+)|\b(\d+)\s*(?:vien|bo|cai|thanh|tam|cay)\b(?!\s*/)")


def _build_stated_volumes(texts):
    """m³ GHI SẴN trên bản vẽ (vd 'KHỐI LƯỢNG ĐÀO MÓNG: 860 M3') -> số ĐỌC sẵn, có handle. Port từ demo 1."""
    out, seen = [], set()
    for t in texts:
        vn = (t.get("vn") or "").strip()
        m = _M3_RE.search(vn)
        if not m: continue
        val = _to_num(m.group(1) or m.group(2))
        if not val or val < _M3_MIN: continue
        if _M3_EXCLUDE_RE.search(unaccent(vn)): continue
        key = (vn, round(val, 2))
        if key in seen: continue
        seen.add(key)
        out.append({"text": vn, "m3": val, "handle": t["handle"]})
    return out


# ---- m² GHI SẴN trên bản vẽ (Task C — liệt kê nhãn diện tích, KHÔNG suy hình học, KHÔNG phân loại) ----
# (?<![/.,\d]) chặn: MẬT ĐỘ '.../1m2' (số sau '/'), và ĐUÔI THẬP PHÂN/GIỮA-SỐ (số sau '.'/','/chữ-số) — nếu chỉ
# dùng (?<!/) thì '117m2/44,5m2' sẽ bịa ra '4.5'/'8.1' từ đuôi số. GIỮ diện tích thật ngăn bởi space/';' (vd
# 'tầng 1: 250m2; tầng 2: 180m2' -> cả 2). Mã 'DM2'/'dm2' tự loại (không CHỮ SỐ liền trước m2).
_STATED_M2_RE = re.compile(r"(?<![/.,\d])(\d+(?:[.,]\d+)?)\s{0,2}m2\b|(?<![/.,\d])(\d+(?:[.,]\d+)?)\s{0,2}m²", re.I)
_DT_KW_RE = re.compile(r"dien tich|\bs\s*=")   # cờ TIN CẬY (nhãn có 'diện tích'/'S=') — CHỈ để xếp ưu tiên, KHÔNG lọc


def _build_stated_areas(texts):
    """m² GHI SẴN trên bản vẽ (vd 'diện tích 634m2', 'S=6.36m2') -> số ĐỌC verbatim + handle (Task C).
    Mirror _build_stated_volumes. LỌC mật độ '/1m2'; KHÔNG đặt min (giữ diện tích nhỏ thật); KHÔNG phân loại
    type (mái/sơn/granit/sàn) — đối tác tự đối chiếu; co_tu_khoa_dien_tich = cờ tin cậy (nhãn có 'diện tích'/'S=').
    GIỚI HẠN CÓ CHỦ Ý (an toàn = thà DROP còn hơn BỊA): nhiều diện tích trong 1 nhãn ngăn bởi '/' hoặc ',' liền ->
    chỉ trị ĐẦU (đuôi sau '/'/',' bị lookbehind chặn để không bịa số thập phân/mật độ); ngăn bởi cách/';'/'và' -> đủ.
    Trị vẫn còn NGUYÊN VĂN ở 'text'. Không manifest trên file mẫu (mỗi nhãn là 1 entity riêng)."""
    out, seen = [], set()
    for t in texts:
        vn = (t.get("vn") or "").strip()
        if not vn: continue
        # gộp '/  1m2' -> '/1m2' để lookbehind chặn CẢ mật độ có khoảng trắng sau '/' (vd '16 cọc/ 1m2' -> bỏ '1');
        # match trên 'scan', nhưng LƯU 'vn' NGUYÊN VĂN làm text (chỉ dùng để lấy TRỊ, không đổi hiển thị).
        scan = re.sub(r"/\s+", "/", vn)
        kw = bool(_DT_KW_RE.search(unaccent(vn).lower()))
        for m in _STATED_M2_RE.finditer(scan):
            val = _to_num(m.group(1) or m.group(2))
            if not val or val <= 0: continue
            key = (vn, round(val, 2))
            if key in seen: continue
            seen.add(key)
            out.append({"text": vn, "m2": val, "handle": t["handle"],
                        "layer": t.get("layer") or "", "co_tu_khoa_dien_tich": kw})
    return out


def _tok_bound(tok, lab):
    """Token có chữ số -> khớp RANH GIỚI TỪ, BỎ gạch ngang giữa chữ-số (C1 == C-1, ĐC3 == đc-3);
    vẫn chặn C-4 khớp nhầm C-40 (ranh giới). Token chữ -> substring (khớp font/ghép từ)."""
    if any(c.isdigit() for c in tok):
        t2 = tok.replace("-", "")
        l2 = re.sub(r"(?<=[a-zđ])-(?=\d)", "", lab)
        return re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(t2), l2) is not None
    return tok in lab


def _nd(val):
    """Input do ĐỐI TÁC cấp (không đọc từ file) — luôn ghi rõ nguồn. bool/inf/nan -> GIỮ NGUYÊN giá trị thô
    (không ép float) để cổng kiểm 'số dương hợp lệ' ở tinh_dai_luong bắt là PHI SỐ (chống bịa: true->1.0, 1e400->inf)."""
    try:
        if isinstance(val, bool): raise ValueError        # True/False KHÔNG phải số kg/SL đối tác cấp
        g = float(val)
        if not math.isfinite(g): raise ValueError         # inf/nan -> phi số hợp lệ
    except Exception:
        g = val
    return {"gia_tri": g, "nguon": "nguoi_dung_cung_cap", "handle": None, "chua_chac": False,
            "do_tin_cay": "do_nguoi_dung", "giai_thich": "do đối tác cấp (không đọc từ file)"}


# Mỗi công thức: ten hiển thị, cách tính, đơn vị KQ, danh sách input (ten|đơn vị|resolver method|khoá inputs_bo_sung),
# và hàm compute nhận dict {ten_input: giá_trị_số}. CODE tính, không để LLM tính.
_FORMULAS = {
    "dien_tich_cua": {
        "ten": "Diện tích cửa", "don_vi": "m²",
        "cach_tinh": "rộng × cao × số_lượng ÷ 1.000.000",
        "inputs": [("rong", "mm", "_rs_rong", "rong"), ("cao", "mm", "_rs_cao", "cao"),
                   ("so_luong", "bộ", "_rs_so_luong", "so_luong")],
        "compute": lambda v: round(v["rong"] * v["cao"] * v["so_luong"] / 1e6, 2),
    },
    "the_tich_be_tong_cot": {
        "ten": "Thể tích bê tông cột", "don_vi": "m³",
        "cach_tinh": "canh_a × canh_b × chiều_cao × số_lượng ÷ 1.000.000.000",
        "inputs": [("canh_a", "mm", "_rs_canh_a", "canh_a"), ("canh_b", "mm", "_rs_canh_b", "canh_b"),
                   ("chieu_cao", "mm", "_rs_chieu_cao_cot", "chieu_cao"), ("so_luong", "cái", "_rs_so_luong", "so_luong")],
        "compute": lambda v: round(v["canh_a"] * v["canh_b"] * v["chieu_cao"] * v["so_luong"] / 1e9, 3),
    },
    "dien_tich_van_khuon_cot": {
        "ten": "Diện tích ván khuôn cột", "don_vi": "m²",
        "cach_tinh": "2 × (canh_a + canh_b) × chiều_cao × số_lượng ÷ 1.000.000",
        "inputs": [("canh_a", "mm", "_rs_canh_a", "canh_a"), ("canh_b", "mm", "_rs_canh_b", "canh_b"),
                   ("chieu_cao", "mm", "_rs_chieu_cao_cot", "chieu_cao"), ("so_luong", "cái", "_rs_so_luong", "so_luong")],
        "compute": lambda v: round(2 * (v["canh_a"] + v["canh_b"]) * v["chieu_cao"] * v["so_luong"] / 1e6, 2),
    },
    "the_tich_be_tong_dam": {
        "ten": "Thể tích bê tông dầm", "don_vi": "m³",
        "cach_tinh": "bề_rộng × chiều_cao × chiều_dài × số_lượng ÷ 1.000.000.000",
        "inputs": [("be_rong", "mm", "_rs_canh_a", "be_rong"), ("chieu_cao", "mm", "_rs_canh_b", "chieu_cao"),
                   ("chieu_dai", "mm", "_rs_chieu_dai", "chieu_dai"), ("so_luong", "cây", "_rs_so_luong", "so_luong")],
        "compute": lambda v: round(v["be_rong"] * v["chieu_cao"] * v["chieu_dai"] * v["so_luong"] / 1e9, 3),
    },
    "dien_tich_van_khuon_dam": {
        "ten": "Diện tích ván khuôn dầm", "don_vi": "m²",
        "cach_tinh": "(2 × chiều_cao + bề_rộng) × chiều_dài × số_lượng ÷ 1.000.000",
        "inputs": [("be_rong", "mm", "_rs_canh_a", "be_rong"), ("chieu_cao", "mm", "_rs_canh_b", "chieu_cao"),
                   ("chieu_dai", "mm", "_rs_chieu_dai", "chieu_dai"), ("so_luong", "cây", "_rs_so_luong", "so_luong")],
        "compute": lambda v: round((2 * v["chieu_cao"] + v["be_rong"]) * v["chieu_dai"] * v["so_luong"] / 1e6, 2),
    },
    "the_tich_be_tong_san": {
        "ten": "Thể tích bê tông sàn", "don_vi": "m³",
        "cach_tinh": "diện_tích(m²) × bề_dày(mm) ÷ 1000",
        "inputs": [("dien_tich", "m²", "_rs_dien_tich_ghi_san", "dien_tich"),
                   ("chieu_day", "mm", "_rs_chieu_day", "chieu_day")],
        "compute": lambda v: round(v["dien_tich"] * v["chieu_day"] / 1000.0, 3),
    },
    "the_tich_be_tong_mong": {
        "ten": "Thể tích bê tông móng", "don_vi": "m³",
        "cach_tinh": "canh_a × canh_b × chiều_cao × số_lượng ÷ 1.000.000.000",
        "inputs": [("canh_a", "mm", "_rs_canh_a", "canh_a"), ("canh_b", "mm", "_rs_canh_b", "canh_b"),
                   ("chieu_cao", "mm", "_rs_chieu_cao_cot", "chieu_cao"), ("so_luong", "cái", "_rs_so_luong", "so_luong")],
        "compute": lambda v: round(v["canh_a"] * v["canh_b"] * v["chieu_cao"] * v["so_luong"] / 1e9, 3),
    },
    # --- Nhóm 🔴 (đối tác chủ yếu nhập số; bản vẽ ít ghi mã+kích thước sẵn) — dựng SẴN công thức ---
    "xay_tuong": {
        "ten": "Khối lượng xây tường", "don_vi": "m³", "tru_lo": True,
        "cach_tinh": "dài × cao × bề_dày ÷ 1.000.000.000 (mm; TRỪ lỗ cửa/cửa sổ nếu đối tác khai 'lo_cua')",
        "inputs": [("chieu_dai", "mm", "_rs_bs_only", "chieu_dai"), ("chieu_cao", "mm", "_rs_bs_only", "chieu_cao"),
                   ("be_day", "mm", "_rs_chieu_day", "be_day")],
        "compute": lambda v: round(v["chieu_dai"] * v["chieu_cao"] * v["be_day"] / 1e9, 3),
    },
    "dien_tich_trat": {
        "ten": "Diện tích trát", "don_vi": "m²", "tru_lo": True,
        "cach_tinh": "dài × cao × số_mặt ÷ 1.000.000 (mm; TRỪ lỗ nếu đối tác khai 'lo_cua')",
        "inputs": [("chieu_dai", "mm", "_rs_bs_only", "chieu_dai"), ("chieu_cao", "mm", "_rs_bs_only", "chieu_cao"),
                   ("so_mat", "mặt", "_rs_bs_only", "so_mat")],
        "compute": lambda v: round(v["chieu_dai"] * v["chieu_cao"] * v["so_mat"] / 1e6, 2),
    },
    "khoi_luong_dao_dat": {
        "ten": "Khối lượng đào đất", "don_vi": "m³",
        "cach_tinh": "dài × rộng × sâu ÷ 1.000.000.000 (mm; hố chữ nhật, CHƯA tính hệ số taluy/mở rộng)",
        "inputs": [("chieu_dai", "mm", "_rs_bs_only", "chieu_dai"), ("chieu_rong", "mm", "_rs_bs_only", "chieu_rong"),
                   ("chieu_sau", "mm", "_rs_bs_only", "chieu_sau")],
        "compute": lambda v: round(v["chieu_dai"] * v["chieu_rong"] * v["chieu_sau"] / 1e9, 3),
    },
    "khoi_luong_dap_dat": {
        "ten": "Khối lượng đắp đất", "don_vi": "m³",
        "cach_tinh": "dài × rộng × chiều_cao_đắp ÷ 1.000.000.000 (mm; khối chữ nhật)",
        "inputs": [("chieu_dai", "mm", "_rs_bs_only", "chieu_dai"), ("chieu_rong", "mm", "_rs_bs_only", "chieu_rong"),
                   ("chieu_cao", "mm", "_rs_bs_only", "chieu_cao")],
        "compute": lambda v: round(v["chieu_dai"] * v["chieu_rong"] * v["chieu_cao"] / 1e9, 3),
    },
    # Khối lượng thép hình/INOX theo CẤU KIỆN: SL đọc từ bản vẽ × kg/bộ đối tác cấp. Dùng khi bản vẽ chỉ có
    # GHI CHÚ 'X kg/1 bộ' (không có bảng tách theo cửa) — vd 'inox cửa S1 = 16 bộ × 8.62 kg'. Chống bịa: KHÔNG
    # tự lấy kg từ ghi chú gán cho mã (tránh liên kết sai) -> đối tác cấp/ xác nhận kg/bộ; SL vắng -> hỏi.
    "khoi_luong_thep_hinh": {
        "ten": "Khối lượng thép hình/inox", "don_vi": "kg",
        "cach_tinh": "số_bộ × kg_mỗi_bộ (kg 1 bộ do ĐỐI TÁC cấp; số bộ ĐỌC từ nhãn số lượng trên bản vẽ)",
        "inputs": [("so_luong", "bộ", "_rs_so_luong", "so_luong"),
                   ("kg_moi_bo", "kg", "_rs_bs_only", "kg_moi_bo")],
        "compute": lambda v: round(v["so_luong"] * v["kg_moi_bo"], 2),
    },
}

# Ánh xạ ngôn ngữ tự nhiên -> khoá công thức (LLM có thể truyền tên tự do).
_TEN_MAP = [
    (("inox",), "khoi_luong_thep_hinh"),     # 'kg inox cửa S1' — CHECK inox TRƯỚC 'cua' (query có cả hai từ)
    (("thep hinh",), "khoi_luong_thep_hinh"),  # 'khối lượng thép hình'
    (("dao",), "khoi_luong_dao_dat"),        # 'đào đất', 'đào móng' (đào -> đất, đứng trước 'mong')
    (("dap",), "khoi_luong_dap_dat"),        # 'đắp đất', 'san lấp'
    (("xay",), "xay_tuong"),                 # 'khối lượng xây', 'xây tường'
    (("trat",), "dien_tich_trat"),           # 'diện tích trát', 'trát tường'
    (("van khuon", "cot"), "dien_tich_van_khuon_cot"),
    (("van khuon", "dam"), "dien_tich_van_khuon_dam"),
    (("cot",), "the_tich_be_tong_cot"),      # 'thể tích/bê tông cột'
    (("dam",), "the_tich_be_tong_dam"),
    (("san",), "the_tich_be_tong_san"),
    (("mong",), "the_tich_be_tong_mong"),
    (("cua",), "dien_tich_cua"),
]

# Loại cấu kiện KỲ VỌNG của mỗi công thức (để bắt 'sai loại': hỏi thể tích MÓNG cho một cái DẦM...).
# dien_tich_cua KHÔNG đưa vào -> cửa miễn kiểm loại (nhận diện cửa theo đường khác).
_FORMULA_LOAI = {
    "the_tich_be_tong_cot": "cot", "dien_tich_van_khuon_cot": "cot",
    "the_tich_be_tong_dam": "dam", "dien_tich_van_khuon_dam": "dam",
    "the_tich_be_tong_san": "san", "the_tich_be_tong_mong": "mong",
}
# Từ khoá LOẠI (không dấu) đứng NGAY TRƯỚC mã trong nhãn -> loại (vd 'DẦM DM-1'). Data-driven: dựa
# nhãn bản vẽ GHI RÕ, KHÔNG đoán theo prefix mã (tránh overfit quy ước tên).
_LOAI_KW = [("mong", "mong"), ("dam", "dam"), ("cot", "cot"), ("san", "san"),
            ("dai", "mong"), ("giang", "giang")]
_LOAI_VN = {"cot": "cột", "dam": "dầm", "san": "sàn", "mong": "móng", "giang": "giằng"}


def _chuan_hoa_ten_dai_luong(ten):
    """Map tên tự do -> khoá công thức. Trả None nếu không nhận ra."""
    t = (ten or "").strip()
    if t in _FORMULAS: return t
    tn = unaccent(t)
    for kws, key in _TEN_MAP:
        if all(k in tn for k in kws): return key
    return None


class Drawing:
    """Một bản vẽ đã nạp: GIỮ doc (render) + dữ liệu trích xuất (tra cứu). Chống bịa: số do CODE."""

    def __init__(self, path):
        if path.lower().endswith(".dwg"):
            path = convert_dwg_to_dxf(path, UPLOAD_DIR)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > READFILE_MAX_MB:
            raise RuntimeError("File này quá lớn (~%.0fMB) so với gói máy chủ hiện tại. "
                               "Vui lòng thử file nhỏ hơn hoặc nâng cấp máy chủ." % size_mb)
        self.path = path
        self.name = os.path.basename(path)
        self.doc = ezdxf.readfile(path)          # GIỮ trong RAM để render
        self.dxfversion = self.doc.dxfversion
        self._extract()

    # ---------------- trích xuất (port _collect_entities + parse) ----------------
    def _extract(self):
        counts, texts, dims, dim_items = Counter(), [], [], []
        blocks, used_layers, thep, thep_hinh = Counter(), set(), {}, {}
        for e in self.doc.modelspace():
            t = e.dxftype(); counts[t] += 1
            try: used_layers.add(e.dxf.get("layer"))
            except Exception: pass
            if t in ("TEXT", "MTEXT"):
                raw = e.dxf.text if t == "TEXT" else e.text
                try: ins = e.dxf.insert; xx, yy = float(ins.x), float(ins.y)
                except Exception: xx = yy = 0.0
                texts.append({"handle": e.dxf.handle, "layer": e.dxf.get("layer"),
                              "text": raw, "vn": to_unicode(raw), "x": xx, "y": yy})
            elif t == "INSERT":
                try: bname = e.dxf.get("name") or ""
                except Exception: bname = ""
                if bname and not bname.startswith("*"): blocks[bname] += 1
                attmap = {}
                for att in e.attribs:
                    raw = att.dxf.text
                    try: ins = att.dxf.insert; xx, yy = float(ins.x), float(ins.y)
                    except Exception: xx = yy = 0.0
                    texts.append({"handle": att.dxf.handle, "layer": att.dxf.get("layer"),
                                  "text": raw, "vn": to_unicode(raw), "x": xx, "y": yy, "in_block": True})
                    try: attmap[att.dxf.tag] = raw
                    except Exception: pass
                if _to_num(attmap.get("TL")) is not None and any(k in attmap for k in ("SLA", "DAI", "DT")):
                    if "DK" in attmap: _acc_thep(thep, attmap)
                    elif "SHOW" in attmap: _acc_thep_hinh(thep_hinh, attmap)
            elif t == "DIMENSION":
                try:
                    v = round(float(e.get_measurement()), 1)
                    dims.append(v)
                    # GĐ2: thêm TOẠ ĐỘ (để gắn dim vào cấu kiện) + HƯỚNG (ngang=rộng / dọc=cao).
                    dx = dy = 0.0; co_td = False
                    for attr in ("text_midpoint", "defpoint", "defpoint2", "defpoint3"):
                        if e.dxf.hasattr(attr):
                            try:
                                p = e.dxf.get(attr); dx, dy = float(p[0]), float(p[1]); co_td = True; break
                            except Exception: pass
                    huong = "?"
                    try:
                        a = float(e.dxf.get("angle", 0.0)) % 180
                        if a < 15 or a > 165: huong = "ngang"
                        elif 75 < a < 105: huong = "doc"
                    except Exception: pass
                    if huong == "?" and e.dxf.hasattr("defpoint2") and e.dxf.hasattr("defpoint3"):
                        try:
                            p2 = e.dxf.defpoint2; p3 = e.dxf.defpoint3
                            huong = "ngang" if abs(float(p2[0]) - float(p3[0])) >= abs(float(p2[1]) - float(p3[1])) else "doc"
                        except Exception: pass
                    dim_items.append({"handle": e.dxf.handle, "value": v, "x": dx, "y": dy,
                                      "layer": e.dxf.get("layer"), "huong": huong, "khong_toa_do": not co_td})
                except Exception: pass

        self.texts = texts
        self.counts = dict(counts)
        self.blocks = dict(blocks)
        self.total = sum(counts.values())
        self.dims = dims
        self.dim_items = dim_items
        self.dim_vals = sorted({d for d in dims if d > 0})
        self.dim_top = Counter(round(d) for d in dims if d > 0).most_common(30)
        self.layers = [l.dxf.name for l in self.doc.layers]
        self.thep = {"by_dk": thep, "tong_kg": round(sum(v["kg"] for v in thep.values()), 1),
                     "so_dong": sum(v["rows"] for v in thep.values()), "co_bang": bool(thep)}
        self.thep_hinh = {"by_show": thep_hinh, "tong_kg": round(sum(v["kg"] for v in thep_hinh.values()), 1),
                          "so_dong": sum(v["rows"] for v in thep_hinh.values()), "co_bang": bool(thep_hinh)}
        sheets = [{"handle": tx["handle"], "title": tx["vn"], "y": tx.get("y", 0.0)}
                  for tx in texts if not tx.get("in_block")
                  and tx["text"].strip().startswith("%%U")
                  and len(tx["vn"].strip()) >= 2 and any(c.isalpha() for c in tx["vn"])]
        self.sheets = sheets
        self.sheets_sorted = sorted(sheets, key=lambda s: -s.get("y", 0.0))
        self.qty_index = self._build_qty_index(texts)
        self.door_size_index = _build_door_size_index(texts)   # GĐ2: R×C cửa từ bảng thống kê (confident)
        self.section_index = _build_section_index(texts)       # tiết diện kết cấu: ghép mã↔AxB theo tọa độ + đơn vị cm/mm
        self.levels = _build_levels(texts)                     # GĐ2c: cao độ -> chiều cao tầng điển hình
        self.stated_vol = _build_stated_volumes(texts)         # GĐ2d: m³ ghi sẵn trên bản vẽ
        self.stated_area = _build_stated_areas(texts)          # Task C: m² ghi sẵn (nhãn diện tích, verbatim)

    # ---------------- qty index (port) ----------------
    def _find_title_for_qty(self, info, i):
        x, y = info[i]["x"], info[i]["y"]
        above, row = [], []
        for j, u in enumerate(info):
            if j == i or u["qty"] is not None or not u["title"]: continue
            dx, dy = u["x"] - x, u["y"] - y
            if abs(dx) < 1500 and 0 < dy < 1200: above.append((abs(dx) + dy, j, u["code"]))
            elif abs(dy) < 300 and -2000 < dx < 0: row.append((abs(dx), j, u["code"]))
        for pool in (above, row):
            if pool:
                pool.sort(key=lambda r: (0 if r[2] else 1, r[0]))
                return info[pool[0][1]]["t"]
        return None

    def _build_qty_index(self, texts):
        info = []
        for t in texts:
            nv = _norm_label(t["vn"])
            info.append({"t": t, "x": t.get("x", 0.0), "y": t.get("y", 0.0), "nv": nv,
                         "qty": _qty_match(nv + " " + _norm_label(t.get("text", ""))),
                         "title": _looks_like_title(nv), "code": bool(_CODE_TOKEN_RE.search(nv))})
        idx = []
        for i, it in enumerate(info):
            if it["qty"] is None: continue
            t, nv, qty = it["t"], it["nv"], it["qty"]
            resid = _QTY_STRIP.sub(" ", nv)
            if not _is_dim_label(nv) and _looks_like_title(resid):
                idx.append({"label": t["vn"].strip(), "label_norm": nv, "so_luong": qty,
                            "handle": t["handle"], "qty_handle": t["handle"], "nguon": "inline",
                            "x": t.get("x", 0.0), "y": t.get("y", 0.0)})
                continue
            cand = self._find_title_for_qty(info, i)
            if cand:
                idx.append({"label": cand["vn"].strip(), "label_norm": _norm_label(cand["vn"]),
                            "so_luong": qty, "handle": cand["handle"], "qty_handle": t["handle"],
                            "nguon": "spatial", "x": cand.get("x", 0.0), "y": cand.get("y", 0.0)})
        return idx

    # ---------------- tra cứu cơ bản (port) ----------------
    def search_texts(self, term, layer=None):
        toks = [t for t in _norm(term).split() if t]
        ly = unaccent(layer) if layer else None
        out = []
        for tx in self.texts:
            if ly is not None and ly not in unaccent(tx.get("layer") or ""): continue
            if not toks: out.append(tx); continue
            hay = _norm(tx["vn"]) + " \x01 " + _norm(tx["text"])
            if all(t in hay for t in toks): out.append(tx)
        return out

    def tra_so_luong(self, keyword):
        idx = self.qty_index
        kw = _norm_label(keyword or "").strip()
        toks = [w for w in kw.split() if w]
        if not toks: return []
        codes = [w for w in toks if any(c.isdigit() for c in w)]
        out = []
        for e in idx:
            lab = e["label_norm"]
            full = all(_tok_bound(t, lab) for t in toks)          # ranh giới + bỏ gạch ngang (C1==C-1)
            code = any(_tok_bound(c, lab) for c in codes) if codes else False
            if full or code: out.append(dict(e, _score=2 if full else 1))
        out.sort(key=lambda x: -x["_score"])
        seen, res = set(), []
        for e in out:
            k = (e["label_norm"], e["so_luong"])
            if k not in seen: seen.add(k); res.append(e)
        return res[:20]

    # ============================================================
    # 13 CÔNG CỤ ĐỌC (port nguyên ai_gemini._build_executors — giữ ghi_chu chống bịa)
    # Mỗi tool trả dict; field chứa handle để host dựng evidence + để highlight dùng lại.
    # ============================================================
    def tim_kiem(self, tu_khoa=None, layer=None, gioi_han=40, **_):
        tk = (tu_khoa or "").strip(); ly = (layer or "").strip()
        if not tk and not ly:
            return {"loi": "Cần ít nhất một từ khoá hoặc tên layer để tìm.", "so_ket_qua": 0, "ket_qua": []}
        hits = self.search_texts(tk, layer=ly or None)
        cap = max(0, min(int(gioi_han or 40), 200))   # gioi_han âm -> 0 (không cắt cụt bằng slice âm)
        ket = [{"handle": h["handle"], "layer": h.get("layer") or "", "text": h["vn"]} for h in hits[:cap]]
        return {"tu_khoa": tk or None, "layer": ly or None, "so_ket_qua": len(hits),
                "hien_thi": len(ket), "ket_qua": ket,
                "ghi_chu": "so_ket_qua = số ĐOẠN CHỮ khớp từ khoá (có thể gồm khớp một phần); "
                           "đọc nội dung để xác nhận, KHÔNG coi là số lượng cấu kiện."}

    def dem_so_luong(self, tu_khoa=None, **_):
        tk = (tu_khoa or "").strip()
        if not tk: return {"loi": "Thiếu từ khoá cụ thể để đếm.", "so_lan_xuat_hien": None}
        hits = self.search_texts(tk)
        mau = [{"handle": h["handle"], "layer": h.get("layer") or "", "text": h["vn"]} for h in hits[:8]]
        return {"tu_khoa": tk, "so_lan_xuat_hien": len(hits), "vi_du": mau,
                "ghi_chu": "Đây là SỐ LẦN chuỗi xuất hiện, KHÔNG phải số lượng cấu kiện thật. "
                           "Câu hỏi 'có bao nhiêu cấu kiện' phải dùng tra_cuu_so_luong."}

    def tra_cuu_so_luong(self, tu_khoa=None, **_):
        tk = (tu_khoa or "").strip()
        if not tk: return {"loi": "Thiếu tên cấu kiện cần tra số lượng.", "co_ghi_so_luong": False}
        matches = self.tra_so_luong(tk)
        stated = [{"noi_dung": m["label"], "so_luong": m["so_luong"], "handle": m["handle"],
                   "qty_handle": m.get("qty_handle", m["handle"])} for m in matches]
        if stated:
            return {"tu_khoa": tk, "co_ghi_so_luong": True, "so_muc_co_ghi": len(stated),
                    "danh_sach_so_luong": stated[:40],
                    "ghi_chu": "Số lượng do BẢN VẼ GHI RÕ (nhãn 'số lượng: N bộ' hoặc 'SL='). Số THẬT."}
        return {"tu_khoa": tk, "co_ghi_so_luong": False, "so_muc_co_ghi": 0, "danh_sach_so_luong": [],
                "ghi_chu": ("Bản vẽ KHÔNG ghi sẵn số lượng cho '%s'. KHÔNG lấy số lần xuất hiện làm số lượng. "
                            "Thử mã cấu kiện ngắn (vd 'D1'). Nếu thật sự không ghi -> cần bóc tách." % tk)}

    def liet_ke_so_luong(self, loc=None, **_):
        idx = self.qty_index or []
        items = self.tra_so_luong(loc) if (loc or "").strip() else idx
        if (loc or "").strip() and len(items) < 2: items = idx
        ds = [{"noi_dung": e["label"], "so_luong": e["so_luong"],
               "handle": e.get("qty_handle", e["handle"])} for e in items]
        return {"so_muc": len(ds), "danh_sach": ds[:60],
                "ghi_chu": "Các mục CÓ GHI SỐ LƯỢNG (nhãn 'số lượng: N bộ'/'SL='). Tên có thể lỗi font "
                           "('cöa'='cửa'). Số THẬT ghi trên bản vẽ, không phải đếm chữ."}

    def tong_so_luong(self, loc=None, **_):
        items = self.tra_so_luong(loc) if (loc or "").strip() else (self.qty_index or [])
        seen, muc = set(), []
        for e in items:
            cs = re.findall(r"[a-zđ]+-?\d+[a-z]?", e["label_norm"])
            code = cs[-1] if cs else e["label_norm"]
            if code in seen: continue
            seen.add(code)
            muc.append({"noi_dung": e["label"], "so_luong": e["so_luong"],
                        "handle": e.get("qty_handle", e["handle"])})
        return {"loc": loc or None, "so_muc": len(muc), "tong": sum(m["so_luong"] for m in muc),
                "cac_muc": muc[:50],
                "ghi_chu": "TỔNG do hệ thống CỘNG (đã gộp mục cùng mã tránh đếm trùng). Kiểm cac_muc: "
                           "nếu có mục không thuộc nhóm hỏi thì trừ ra. Số từng mục là số THẬT trên bản vẽ."}

    def thong_ke_thep(self, duong_kinh=None, **_):
        th = self.thep or {}; by = th.get("by_dk") or {}
        if not by:
            return {"co_bang_thong_ke": False,
                    "ghi_chu": "Bản vẽ không có bảng thống kê thép đọc được (block TK_*)."}
        dk = (str(duong_kinh) if duong_kinh is not None else "").strip()
        for ch in ("Ø", "ø", "φ", "phi", "D", "d"): dk = dk.replace(ch, "")
        dk = dk.strip()
        _n = _to_num(dk)
        if _n is not None and float(_n).is_integer(): dk = str(int(_n))   # '16.0'/16.0 -> '16' (khớp key 'Ø16')
        if dk:
            key = "Ø%s" % dk; row = by.get(key)
            if not row:
                return {"co_bang_thong_ke": True, "duong_kinh": key, "co_trong_bang": False,
                        "ghi_chu": "Không có thép %s. Các cỡ có: %s" % (key, ", ".join(by.keys()))}
            return {"co_bang_thong_ke": True, "duong_kinh": key, "co_trong_bang": True,
                    "so_thanh": row["so_thanh"], "tong_chieu_dai_m": round(row["dai_m"], 1),
                    "khoi_luong_kg": round(row["kg"], 1),
                    "ghi_chu": "Số từ BẢNG THỐNG KÊ THÉP trong file (kỹ sư lập) — số THẬT, không đếm chữ."}
        theo = {k: {"so_thanh": v["so_thanh"], "tong_chieu_dai_m": round(v["dai_m"], 1),
                    "khoi_luong_kg": round(v["kg"], 1)} for k, v in sorted(by.items(), key=lambda x: -x[1]["kg"])}
        th_hinh = self.thep_hinh or {}; canh_bao = ""
        if th_hinh.get("co_bang"):
            canh_bao = (" Ngoài ra còn bảng thép hình/inox ~%.1f kg (gọi thong_ke_thep_hinh) — CHƯA cộng vào."
                        % th_hinh.get("tong_kg", 0))
        return {"co_bang_thong_ke": True, "tong_khoi_luong_kg": round(th.get("tong_kg", 0), 1),
                "so_dong_thong_ke": th.get("so_dong", 0), "theo_duong_kinh": theo,
                "ghi_chu": "Tổng CỐT THÉP TRÒN theo bảng thống kê — số THẬT. CHỈ gồm cốt thép tròn." + canh_bao}

    def thong_ke_thep_hinh(self, **_):
        th = self.thep_hinh or {}; by = th.get("by_show") or {}
        if not by:
            return {"co_bang": False, "ghi_chu": "Bản vẽ không có bảng thép hình/inox đọc được."}
        theo = {k: {"so_luong": v["so"], "khoi_luong_kg": round(v["kg"], 1)}
                for k, v in sorted(by.items(), key=lambda x: -x[1]["kg"])}
        return {"co_bang": True, "tong_khoi_luong_kg": round(th.get("tong_kg", 0), 1),
                "so_dong": th.get("so_dong", 0), "theo_tiet_dien": theo,
                "ghi_chu": "Tổng THÉP HÌNH/INOX/xà gồ theo bảng (số THẬT). RIÊNG với cốt thép tròn."}

    def liet_ke_chu_theo_layer(self, layer=None, gioi_han=60, **_):
        ly = (layer or "").strip()
        if not ly: return {"loi": "Thiếu tên layer cần liệt kê.", "so_doan_chu": 0, "ket_qua": []}
        hits = self.search_texts("", layer=ly)
        cap = max(0, min(int(gioi_han or 60), 200))
        ket = [{"handle": h["handle"], "layer": h.get("layer") or "", "text": h["vn"]} for h in hits[:cap]]
        return {"layer": ly, "so_doan_chu": len(hits), "hien_thi": len(ket), "ket_qua": ket}

    def liet_ke_sheet(self, **_):
        sh = self.sheets_sorted or self.sheets
        seen, ds = set(), []
        for s in sh:
            k = s["title"].strip().lower()
            if k in seen: continue
            seen.add(k); ds.append({"handle": s["handle"], "title": s["title"]})
        return {"so_tieu_de": len(ds), "so_nhan_tho": len(sh), "danh_sach": ds,
                "ghi_chu": "NHÃN TIÊU ĐỀ phát hiện theo chữ gạch chân — gồm cả tiêu đề chi tiết, "
                           "có thể KHÁC số tờ in. Đã bỏ trùng (so_nhan_tho = trước khi bỏ trùng)."}

    def liet_ke_layer(self, **_):
        return {"so_layer": len(self.layers), "danh_sach": self.layers,
                "ghi_chu": "Số layer ĐỊNH NGHĨA trong file (có thể gồm layer rỗng)."}

    @staticmethod
    def _is_block_noi_bo(n):
        nl = (n or "").lower()
        return (n.startswith("A$") or n.startswith("*") or bool(re.fullmatch(r"[0-9]+", n))
                or not any(v in nl for v in "aeiou"))

    def liet_ke_block(self, **_):
        b = self.blocks
        named = {n: c for n, c in b.items() if not self._is_block_noi_bo(n)}
        anon = {n: c for n, c in b.items() if self._is_block_noi_bo(n)}
        top = dict(sorted(named.items(), key=lambda x: -x[1])[:25])
        return {"so_loai_block": len(b), "so_loai_co_ten": len(named),
                "so_loai_noi_bo_an_danh": len(anon), "top_block_co_ten": top,
                "ghi_chu": "SỐ LẦN CHÈN block/ký hiệu (trục, nút thép, khung tên...). KHÔNG phải số cấu kiện."}

    def thong_ke_doi_tuong(self, **_):
        return {"tong_doi_tuong": self.total,
                "theo_loai": dict(sorted(self.counts.items(), key=lambda x: -x[1])),
                "ghi_chu": "Số ĐỐI TƯỢNG hình học/chữ (LINE, TEXT, DIMENSION, INSERT...). "
                           "KHÔNG phải số cấu kiện; INSERT là số lần chèn block."}

    def thong_tin_kich_thuoc(self, **_):
        dv = self.dim_vals
        pho_bien = [{"mm": int(v), "so_lan": n} for v, n in self.dim_top]
        return {"so_duong_kich_thuoc": len(self.dims),
                "nho_nhat_mm": dv[0] if dv else None, "lon_nhat_mm": dv[-1] if dv else None,
                "gia_tri_pho_bien_mm": pho_bien,
                "ghi_chu": "Đường kích thước (DIMENSION). gia_tri_pho_bien_mm = giá trị xuất hiện NHIỀU NHẤT "
                           "(thường là bước cột/nhịp). Giá trị lớn nhất KHÔNG chắc là kích thước tổng công trình."}

    def thong_tin_tang(self, **_):
        """GĐ2c: BÁO cao độ + chiều cao tầng điển hình + số tầng ƯỚC TÍNH. KHÔNG tự bơm vào tính toán (an toàn)."""
        lv = getattr(self, "levels", None) or {}
        if not lv.get("levels"):
            return {"co_cao_do": False,
                    "ghi_chu": "Bản vẽ không có mốc cao độ (±0.000, +3.600...) đọc được → chưa suy được chiều cao tầng."}
        return {"co_cao_do": True, "so_moc_cao_do": len(lv["levels"]),
                "cao_do_thap_nhat_m": lv["min"], "cao_do_cao_nhat_m": lv["max"],
                "chieu_cao_tang_dien_hinh_m": lv["typical_floor_h"], "so_tang_uoc_tinh": lv["n_tang_est"],
                "cac_cao_do_m": lv["levels"],
                "ghi_chu": "Cao độ là số ĐỌC trên bản vẽ. Chiều cao tầng = HIỆU cao độ liền kề (hệ thống tính). "
                           "Số tầng là ƯỚC TÍNH (cao độ cao nhất ÷ chiều cao tầng); tầng lửng/chiếu nghỉ có thể khác. "
                           "Muốn TÍNH thể tích cột theo chiều cao tầng, đối tác xác nhận rồi nhập (vd 'cột C1 cao 3.6m')."}

    def boc_tach_kich_thuoc(self, tu_khoa=None, gioi_han=30, **_):
        """BÓC TÁCH số đo từ GHI CHÚ tự do (vd 'thảm đá (6x2x0.3)m L=56m', 'gạch 190x190x65mm'):
        trả NGUYÊN VĂN + số đã tách (3D, L, m², m³, bề dày, số lượng) + handle. KHÔNG tự tính khối lượng
        (nhiều 'AxBxC' là kích thước VẬT LIỆU) — chống bịa. Muốn tính thì đối tác xác nhận rồi gọi tinh_dai_luong."""
        tk = (tu_khoa or "").strip()
        if not tk:
            return {"loi": "Cần từ khoá (vd 'thảm đá', 'gạch', 'đá granit') để bóc tách kích thước.", "so_ket_qua": 0}
        cap = max(0, min(int(gioi_han or 30), 100))
        out = []
        for h in self.search_texts(tk):
            vn = h["vn"]; nv = _norm(vn); da = {}
            d3 = []
            for m in _BT_3D.finditer(vn):
                # chuẩn hoá đuôi ĐỒNG NHẤT: bỏ dấu + strip ')' & khoảng trắng, rồi phân loại; loại chữ số/²³
                # khỏi nhánh 'm' (m2/m3 KHÔNG phải đơn vị dài; 'mầu' KHÔNG phải mét). Chống nhầm vật liệu -> mét.
                t = unaccent(re.sub(r"^\)?\s*", "", vn[m.end():m.end() + 4]))
                dv = ("mm" if t.startswith("mm") else "cm" if t.startswith("cm")
                      else "m" if re.match(r"m(?![a-z0-9²³])", t) else "?")
                d3.append({"a": _to_num(m.group(1)), "b": _to_num(m.group(2)), "c": _to_num(m.group(3)), "don_vi": dv})
            if d3: da["kich_thuoc_3d"] = d3
            mL = _BT_L.search(vn)
            if mL: da["chieu_dai"] = {"gia_tri": _to_num(mL.group(1)), "don_vi": (mL.group(2) or "?").lower()}
            mA = _BT_M2.search(vn)
            if mA: da["dien_tich_m2"] = _to_num(mA.group(1) or mA.group(2))
            mV = _M3_RE.search(vn)
            if mV: da["the_tich_m3"] = _to_num(mV.group(1) or mV.group(2))
            mD = _BT_DAY.search(nv)
            if mD: da["be_day_mm"] = _to_num(mD.group(1))
            mS = _BT_SL.search(nv)
            if mS: da["so_luong"] = int(mS.group(1) or mS.group(2))
            if da:
                out.append({"handle": h["handle"], "layer": h.get("layer") or "", "text": vn.strip(), "da_tach": da})
            if len(out) >= cap: break
        return {"tu_khoa": tk, "so_ket_qua": len(out), "ket_qua": out,
                "ghi_chu": "Đã BÓC TÁCH số đo từ ghi chú (kèm NGUYÊN VĂN + handle). ⚠ 'don_vi' là PHỎNG ĐOÁN theo đơn vị "
                           "ghi liền số (mm/cm/m/?) — cần đối tác XÁC NHẬN, KHÔNG coi là căn cứ 'vật liệu hay cấu kiện'. "
                           "Nhiều chuỗi 'AxBxC' (nhất là mm) là KÍCH THƯỚC VẬT LIỆU (gạch/thép/tấm), KHÔNG phải khối lượng. "
                           "Hệ KHÔNG tự tính (chống bịa). Muốn tính: đối tác xác nhận số rồi gọi tinh_dai_luong. m²/m³ là số ĐỌC thật."}

    def liet_ke_dien_tich_ghi_san(self, **_):
        """Task C: LIỆT KÊ mọi nhãn 'X m²' GHI SẴN trên bản vẽ (số ĐỌC + NGUYÊN VĂN + handle) để đối tác ĐỐI CHIẾU
        / CẤP diện tích sàn. CHỈ đọc nhãn ghi sẵn — KHÔNG phân loại (mái/sơn/granit/sàn), KHÔNG suy từ hình học,
        KHÔNG cộng gộp. Mật độ 'N/m²' đã lọc. co_tu_khoa_dien_tich = cờ tin cậy (nhãn có 'diện tích'/'S=')."""
        items = list(getattr(self, "stated_area", None) or [])
        items.sort(key=lambda e: (not e["co_tu_khoa_dien_tich"], -e["m2"], e["handle"] or ""))
        if not items:
            return {"co_du_lieu": False, "so_nhan": 0, "danh_sach": [],
                    "goi_y": "Bản vẽ KHÔNG có nhãn 'X m²' đọc được. Nếu cần diện tích (vd diện tích sàn), đề nghị ĐỐI TÁC "
                             "CẤP con số qua chat — hệ KHÔNG suy diện tích từ hình học (chống bịa).",
                    "ghi_chu": "Không tìm thấy nhãn diện tích ghi sẵn nào trong bản vẽ."}
        so_kw = sum(1 for e in items if e["co_tu_khoa_dien_tich"])
        return {"co_du_lieu": True, "so_nhan": len(items), "so_co_tu_khoa": so_kw, "danh_sach": items,
                "ghi_chu": "LIỆT KÊ các nhãn 'X m²' GHI SẴN (số do CODE đọc, text NGUYÊN VĂN + handle + layer). "
                           "⚠ Nhãn HỖN TẠP (có thể là diện tích mái/sơn/lát/tường/ô-trống...) — hệ KHÔNG phân loại và "
                           "TUYỆT ĐỐI KHÔNG khẳng định bất kỳ nhãn nào là 'DIỆN TÍCH SÀN'. Đối tác tự đối chiếu qua handle "
                           "rồi CHỌN/CẤP con số đúng. 'co_tu_khoa_dien_tich'=true = nhãn có chữ 'diện tích'/'S=' (chủ đích "
                           "diện tích, độ tin cao hơn) NHƯNG vẫn không nghĩa là sàn. TUYỆT ĐỐI KHÔNG cộng gộp các trị "
                           "(khác bản chất). Hệ KHÔNG suy diện tích từ HÌNH HỌC — thiếu thì đối tác CẤP. Lưu ý: nếu MỘT "
                           "nhãn chứa NHIỀU diện tích ngăn bởi '/' hoặc ',' LIỀN (không cách) thì chỉ trị ĐẦU được tách "
                           "tự động — đối tác đọc NGUYÊN VĂN (text) để lấy đủ (ngăn bởi dấu cách/';'/'và' thì tách đủ)."}

    def tom_tat(self):
        return {"name": self.name, "dxfversion": self.dxfversion, "so_layer": len(self.layers),
                "tong_doi_tuong": self.total, "so_doan_chu": len(self.texts),
                "so_kich_thuoc": len(self.dims), "so_nhan_tieu_de": len(self.sheets),
                "thep_tong_kg": self.thep.get("tong_kg", 0), "counts": self.counts}

    # ============================================================
    # GIAI ĐOẠN 2 — ENGINE TÍNH TOÁN (takeoff). CODE lấy input + CODE tính, LLM chỉ điều phối.
    # ============================================================
    def _neo_score(self, c, word_toks):
        """Điểm NEO: +3 nếu khớp cả từ mô tả (vd 'cửa'), +2 nếu là nhãn CỬA (gán-dim chỉ dùng cho cửa)
        -> ưu tiên neo đúng, tránh TRỤC LƯỚI 'D1' / GHI CHÚ. Điểm cao = neo đáng tin hơn."""
        s = 0
        if word_toks and all(_tok_bound(w, c["lab"]) for w in word_toks): s += 3
        if "cua" in c["lab"]: s += 2
        return s

    def _neo_ung_vien(self, match_toks):
        """Ứng viên NEO: qty_index khớp ALL match_toks (ưu tiên), không có -> quét texts. match_toks là
        token MÃ (có chữ số) -> ỔN ĐỊNH, không lệ thuộc từ mô tả thừa ('đi'/'cửa')."""
        cands = [{"x": q.get("x", 0.0), "y": q.get("y", 0.0), "lab": q["label_norm"], "neo": q.get("label") or q["label_norm"]}
                 for q in self.qty_index if all(_tok_bound(t, q["label_norm"]) for t in match_toks)]
        if not cands:
            for tx in self.texts:
                lab = _norm_label(tx["vn"])
                if all(_tok_bound(t, lab) for t in match_toks) and (tx.get("x") or tx.get("y")):
                    cands.append({"x": tx["x"], "y": tx["y"], "lab": lab, "neo": tx["vn"]})
        return cands

    def _gan_dim_cau_kien(self, ma_cau_kien, R=8000.0):
        """Gắn ĐƯỜNG KÍCH THƯỚC vào CỬA theo VỊ TRÍ: chọn NEO ổn định (theo mã, ưu tiên nhãn cửa), lấy dim
        NGANG (rộng) + DỌC (cao) gần nhất, GIÁ TRỊ HỢP LÝ cho ô cửa, trong bán kính R. Heuristic -> 'chưa chắc'.
        Không có dim hợp lý -> None (báo thiếu, KHÔNG lấy dim trục/chi tiết phi lý)."""
        toks = [w for w in _norm_label(ma_cau_kien or "").split() if w]
        if not toks: return {"tim_thay_neo": False}
        code_toks = [t for t in toks if any(c.isdigit() for c in t)]
        word_toks = [t for t in toks if not any(c.isdigit() for c in t)]
        cands = self._neo_ung_vien(code_toks or toks)        # có mã -> khớp theo MÃ (bền với từ thừa)
        if not cands: return {"tim_thay_neo": False}

        def _pair_at(ax, ay):
            best = {"ngang": None, "doc": None}
            for di in self.dim_items:
                if di.get("khong_toa_do"): continue
                h = di.get("huong")
                if h not in ("ngang", "doc"): continue
                if not (_OPENING_DIM_LO <= di["value"] <= _OPENING_DIM_HI): continue   # loại dim phi lý
                dist = ((di["x"] - ax) ** 2 + (di["y"] - ay) ** 2) ** 0.5
                if dist > R: continue
                if best[h] is None or dist < best[h][0]: best[h] = (dist, di)
            return best

        def _quality(b):                                     # đủ cả 2 dim > tổng khoảng cách nhỏ
            found = (1 if b["ngang"] else 0) + (1 if b["doc"] else 0)
            dsum = (b["ngang"][0] if b["ngang"] else R) + (b["doc"][0] if b["doc"] else R)
            return (found, -dsum)

        # trong các neo ĐIỂM CAO NHẤT, chọn neo có CẶP DIM tốt nhất (xử lý cửa vẽ cạnh nhau)
        top_score = max(self._neo_score(c, word_toks) for c in cands)
        top = [c for c in cands if self._neo_score(c, word_toks) == top_score]
        chosen, chosen_b = None, None
        for c in top:
            b = _pair_at(c["x"], c["y"])
            if chosen is None or _quality(b) > _quality(chosen_b):
                chosen, chosen_b = c, b

        def _mk(pair):
            if not pair: return None
            dist, di = pair
            ratio = dist / max(di["value"], 1.0)
            tc = "trung_binh" if ratio < 3 else "thap"    # gán-dim luôn 'chưa chắc' -> KHÔNG gắn nhãn 'cao' (mâu thuẫn)
            return {"gia_tri": di["value"], "handle": di["handle"], "khoang_cach": round(dist), "do_tin_cay": tc}
        return {"tim_thay_neo": True, "neo": chosen["neo"], "rong": _mk(chosen_b["ngang"]), "cao": _mk(chosen_b["doc"])}

    def _doc_tiet_dien(self, ma_cau_kien):
        """Đọc tiết diện của mã cấu kiện. ƯU TIÊN section_index (ghép tọa độ + inline, có đơn vị cm/mm ghi rõ/suy đoán);
        fallback quét CÙNG-TEXT (cũng suy đoán đơn vị + cổng unit-aware). a,b = mm-TƯƠNG ĐƯƠNG (cm đã ×10, để công
        thức ÷1e6/1e9 tính đúng) + a_raw/b_raw + don_vi + suy_doan_don_vi + nhieu_tiet_dien. None nếu không đọc được."""
        codes = [w for w in _norm_label(ma_cau_kien or "").split() if any(c.isdigit() for c in w)]
        if not codes: return None
        for e in (getattr(self, "section_index", None) or []):     # 1) section_index (đọc được cả bảng cột 9T)
            if any(_tok_bound(c, e["code"]) for c in codes):
                return {"a": e["a"], "b": e["b"], "a_raw": e["a_raw"], "b_raw": e["b_raw"], "don_vi": e["don_vi"],
                        "suy_doan_don_vi": e["suy_doan_don_vi"], "handle": e["handle"],
                        "text": "%s (%dx%d %s)" % (e["code"].upper(), e["a_raw"], e["b_raw"], e["don_vi"]),
                        "nhieu_tiet_dien": e["nhieu_tiet_dien"], "so_tiet_dien": e["so_tiet_dien"],
                        "cac_tiet_dien": e["cac_tiet_dien"]}
        found = []                                                 # 2) fallback cùng-text (mã+AxB chung 1 đoạn chữ)
        for tx in self.texts:
            lab = _norm_label(tx["vn"])
            if not all(_tok_bound(c, lab) for c in codes): continue
            mi = _SECT_INLINE_RE.search(tx["vn"]); m = mi or _TIETDIEN_RE.search(tx["vn"])
            if not m: continue
            a, b = int(m.group(1)), int(m.group(2))
            amm, bmm, unit, sd = _sect_to_mm(a, b, (mi.group(3) or "").lower() if mi else "")
            if _plausible_section_mm(amm, bmm):
                found.append((amm, bmm, a, b, unit, sd, tx["handle"], tx["vn"].strip()))
        if not found: return None
        distinct = sorted(set((f[2], f[3]) for f in found))
        amm, bmm, ar, br, unit, sd, h, txt = found[0]
        return {"a": amm, "b": bmm, "a_raw": ar, "b_raw": br, "don_vi": unit, "suy_doan_don_vi": sd, "handle": h,
                "text": txt, "nhieu_tiet_dien": len(distinct) > 1, "so_tiet_dien": len(distinct), "cac_tiet_dien": distinct}

    # ---- Resolver: (ma, bs, ten) -> dict provenance hoặc None. Ưu tiên số ĐỐI TÁC cấp (bs[ten]). ----
    def _rs_so_luong(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        r = self.tra_so_luong(ma)
        if r:
            return {"gia_tri": float(r[0]["so_luong"]), "nguon": "doc_verbatim",
                    "handle": r[0].get("qty_handle") or r[0]["handle"], "chua_chac": False, "do_tin_cay": "cao",
                    "giai_thich": "nhãn số lượng '%s'" % r[0]["label"][:40]}
        return None

    def _door_size(self, ma):
        """Tra R×C của mã cửa từ door_size_index (bảng thống kê) — chỉ trả entry CONFIDENT."""
        idx = getattr(self, "door_size_index", None) or []
        codes = [w for w in _norm_label(ma or "").split() if any(c.isdigit() for c in w)]
        if not codes: return None
        for e in idx:
            if e.get("confident") and any(_tok_bound(c, e["code"]) for c in codes):
                return e
        return None

    @staticmethod
    def _sl_hop_le(v):
        """SL lỗ HỢP LỆ = số NGUYÊN DƯƠNG hữu hạn, <= _SL_LO_MAX (từ chối bool/inf/nan/0/âm/thập-phân/vô-lý).
        Chống bịa SL lỗ + chống tràn số/int khổng lồ lọt vào response."""
        return (isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                and 0 < v <= _SL_LO_MAX and float(v).is_integer())

    def _resolve_lo_cua(self, lo_cua_raw):
        """Giải danh sách LỖ CỬA/CỬA SỔ đối tác khai (task B) — TẤT ĐỊNH, CHỐNG BỊA.
        Mỗi lỗ đúng MỘT mode: theo MÃ ({ma, sl|so_luong}) -> tra kích thước từ door_size_index CONFIDENT
        (verify được, có handle); HOẶC kích thước trực tiếp ({rong, cao, sl|so_luong} mm) -> đối tác cấp.
        SL do ĐỐI TÁC khai (code KHÔNG tự đoán cửa nào thuộc tường nào). BẤT KỲ lỗ nào không giải được
        -> TRẢ LỖI (không im lặng bỏ = tránh trừ sót -> vượt khối lượng; không bịa size = tránh trừ khống).
        Trả: ('skip', None) | ('loi', dict_lỗi) | ('ok', {sum_area_mm2, so_lo, chi_tiet})."""
        if not isinstance(lo_cua_raw, list):
            return ("loi", {"lo_cua_khong_hop_le": True,
                            "ghi_chu": "'lo_cua' phải là DANH SÁCH lỗ, vd [{\"ma\":\"D2\",\"sl\":1}] hoặc "
                                       "[{\"rong\":900,\"cao\":2200,\"sl\":1}]. Không đoán — mời đối tác khai lại."})
        sum_area = 0.0
        so_lo = 0
        chi_tiet = []
        per_code = {}          # cộng dồn SL theo MÃ để so với trần _door_qty_for (chống lách bằng cách tách mã thành nhiều entry)
        for i, item in enumerate(lo_cua_raw):
            nhan = "lỗ #%d" % (i + 1)
            if not isinstance(item, dict):
                return ("loi", {"lo_cua_khong_hop_le": True,
                                "ghi_chu": "%s không hợp lệ (mỗi lỗ phải là một đối tượng {ma/kích thước, sl})." % nhan})
            ma = str(item.get("ma") or "").strip()
            co_kt = ("rong" in item) or ("cao" in item)
            if ma and co_kt:
                return ("loi", {"lo_cua_khong_hop_le": True,
                                "ghi_chu": "%s khai CẢ mã LẪN kích thước (rong/cao) — nhập nhằng. Chọn MỘT: theo mã "
                                           "(code tra bảng) HOẶC kích thước trực tiếp (mm)." % nhan})
            if not ma and not co_kt:
                return ("loi", {"lo_cua_khong_hop_le": True,
                                "ghi_chu": "%s thiếu CẢ mã LẪN kích thước — cần 'ma' (tra bảng) hoặc 'rong'+'cao' (mm)." % nhan})
            if ("sl" in item) and ("so_luong" in item) and item["sl"] != item["so_luong"]:
                return ("loi", {"lo_cua_khong_hop_le": True,
                                "ghi_chu": "%s khai CẢ 'sl' (%r) LẪN 'so_luong' (%r) MÂU THUẪN — mỗi lỗ chỉ một số lượng. "
                                           "Khai lại rõ một giá trị." % (nhan, item.get("sl"), item.get("so_luong"))})
            sl_raw = item.get("sl", item.get("so_luong"))
            sl_val = _nd(sl_raw)["gia_tri"] if sl_raw is not None else None
            if not self._sl_hop_le(sl_val):
                return ("loi", {"so_lieu_khong_hop_le": ["lo_cua[%d].sl" % i], "can_bo_sung": True,
                                "ghi_chu": "%s có SỐ LƯỢNG không hợp lệ (%r) — SL lỗ phải là SỐ NGUYÊN DƯƠNG. "
                                           "Không mặc định, không đoán — mời đối tác khai rõ 'sl'." % (nhan, sl_raw)})
            sl = int(sl_val)
            if ma:
                ton_tai, kiem_tra_duoc = self._cau_kien_hien_dien(ma)
                if kiem_tra_duoc and not ton_tai:               # mã LỖ GIẢ -> không trừ khống (đối xứng cấu kiện)
                    return ("loi", {"khong_tim_thay": True, "lo_khong_tim_thay": [ma.upper()],
                                    "ghi_chu": "%s: mã lỗ '%s' KHÔNG có trong bản vẽ — KHÔNG trừ khống. Kiểm lại mã, "
                                               "hoặc khai kích thước lỗ trực tiếp (rong×cao mm)." % (nhan, ma.upper())})
                d = self._door_size(ma)                          # CHỈ entry CONFIDENT; None -> KHÔNG bịa size
                if not d:
                    return ("loi", {"khong_tra_duoc_size": True, "lo_khong_tra_duoc": [ma.upper()], "can_bo_sung": True,
                                    "ghi_chu": "%s: bản vẽ có nhắc '%s' nhưng KHÔNG có kích thước R×C ĐỦ TIN (bảng thống kê "
                                               "confident) — KHÔNG đoán size. Mời đối tác khai rong×cao (mm) trực tiếp hoặc "
                                               "xác nhận mã. (Bảng cửa có thể ở file khác — nạp file bảng thống kê cửa.)" % (nhan, ma.upper())})
                w, h, handle, code = float(d["w"]), float(d["h"]), d["handle"], d["code"]
                per_code[code] = per_code.get(code, 0) + sl        # cộng dồn theo MÃ (chống tách 1 mã thành nhiều entry để lách trần)
                tong_sl = self._door_qty_for(code)                 # TRẦN verify-được: TỔNG khai > tổng SL bản vẽ = vô lý
                if isinstance(tong_sl, (int, float)) and not isinstance(tong_sl, bool) and math.isfinite(tong_sl) and per_code[code] > tong_sl:
                    return ("loi", {"lo_vuot_so_luong": True,
                                    "ghi_chu": "%s: TỔNG khai %d lỗ '%s' (cộng mọi dòng cùng mã) nhưng bản vẽ chỉ có %d '%s' "
                                               "(đọc từ nhãn SL) — mâu thuẫn. Kiểm lại số lượng lỗ." % (nhan, per_code[code], ma.upper(), int(tong_sl), ma.upper())})
                nguon, confident = "bang_thong_ke", True
                giai_thich = "R×C bảng thống kê cửa '%d×%d'" % (int(w), int(h))
            else:
                w = _nd(item.get("rong"))["gia_tri"]
                h = _nd(item.get("cao"))["gia_tri"]
                xau = [nm for nm, val in (("rong", w), ("cao", h))
                       if not (isinstance(val, (int, float)) and not isinstance(val, bool) and math.isfinite(val) and val > 0)]
                if xau:
                    return ("loi", {"so_lieu_khong_hop_le": ["lo_cua[%d].%s" % (i, k) for k in xau], "can_bo_sung": True,
                                    "ghi_chu": "%s có kích thước không hợp lệ (%s) — rong/cao phải là SỐ DƯƠNG (mm)." % (nhan, ", ".join(xau))})
                if not _plausible_door_size(w, h):               # cổng đơn vị: bắt lẫn cm/mm (90×210 thay 900×2100)
                    return ("loi", {"lo_don_vi_kha_nghi": True, "can_bo_sung": True,
                                    "ghi_chu": "%s: kích thước %g×%g KHÔNG hợp lý cho một ô cửa/cửa sổ (mm) — cạnh lớn phải "
                                               "≥1200mm và ≤9000mm. Kiểm ĐƠN VỊ (nhập mm, không phải cm)." % (nhan, w, h)})
                handle, nguon, confident = None, "nguoi_dung_cung_cap", False
                giai_thich = "kích thước đối tác cấp %g×%g mm (không đọc từ file)" % (w, h)
            sum_area += w * h * sl
            so_lo += sl
            chi_tiet.append({"ma": ma.upper() or None, "rong": int(round(w)), "cao": int(round(h)), "sl": sl,
                             "dien_tich_1_lo_m2": round(w * h / 1e6, 2), "nguon": nguon, "handle": handle,
                             "confident": confident, "giai_thich": giai_thich})
        if not chi_tiet:                                          # lo_cua = [] -> coi như không khai lỗ
            return ("skip", None)
        if not math.isfinite(sum_area):
            return ("loi", {"so_lieu_khong_hop_le": ["lo_cua"], "can_bo_sung": True,
                            "ghi_chu": "Tổng diện tích lỗ tràn số/không hữu hạn — kiểm lại kích thước, số lượng lỗ."})
        return ("ok", {"sum_area_mm2": sum_area, "so_lo": so_lo, "chi_tiet": chi_tiet})

    def _rs_rong(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        d = self._door_size(ma)     # ƯU TIÊN: bảng thống kê cửa (đọc verbatim, ĐÁNG TIN) trước gán-dim
        if d: return {"gia_tri": float(d["w"]), "nguon": "bang_thong_ke", "handle": d["handle"], "chua_chac": False,
                      "do_tin_cay": "cao", "giai_thich": "R×C bảng thống kê cửa '%dx%d'" % (d["w"], d["h"])}
        g = self._gan_dim_cau_kien(ma); r = g.get("rong")
        if r: return {"gia_tri": r["gia_tri"], "nguon": "gan_vi_tri", "handle": r["handle"], "chua_chac": True,
                      "do_tin_cay": r["do_tin_cay"], "giai_thich": "đường kích thước NGANG gần cấu kiện (cách %d)" % r["khoang_cach"]}
        return None

    def _rs_cao(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        d = self._door_size(ma)     # ƯU TIÊN: bảng thống kê cửa trước gán-dim
        if d: return {"gia_tri": float(d["h"]), "nguon": "bang_thong_ke", "handle": d["handle"], "chua_chac": False,
                      "do_tin_cay": "cao", "giai_thich": "R×C bảng thống kê cửa '%dx%d'" % (d["w"], d["h"])}
        g = self._gan_dim_cau_kien(ma); c = g.get("cao")
        if c: return {"gia_tri": c["gia_tri"], "nguon": "gan_vi_tri", "handle": c["handle"], "chua_chac": True,
                      "do_tin_cay": c["do_tin_cay"], "giai_thich": "đường kích thước DỌC gần cấu kiện (cách %d)" % c["khoang_cach"]}
        return None

    def _td_prov(self, td, k):
        sd = bool(td.get("suy_doan_don_vi")); nhieu = bool(td.get("nhieu_tiet_dien"))
        gc = "tiết diện '%s'" % td["text"][:30]
        if sd:
            gc += " (⚠ đơn vị %s là SUY ĐOÁN cm/mm — bản vẽ không ghi rõ, sai quy ước sẽ lệch 100×)" % td.get("don_vi", "?")
        if nhieu:
            gc += " (⚠ có %d tiết diện %s — đang dùng cái đầu, đối tác xác nhận)" % (td["so_tiet_dien"], td["cac_tiet_dien"])
        return {"gia_tri": float(td[k]), "nguon": "doc_verbatim", "handle": td["handle"],
                "chua_chac": nhieu or sd, "suy_doan_don_vi": sd,
                "do_tin_cay": "trung_binh" if (nhieu or sd) else "cao", "giai_thich": gc}

    def _rs_canh_a(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        td = self._doc_tiet_dien(ma)
        return self._td_prov(td, "a") if td else None

    def _rs_canh_b(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        td = self._doc_tiet_dien(ma)
        return self._td_prov(td, "b") if td else None

    def _rs_chieu_cao_cot(self, ma, bs, ten=None):
        # chiều cao cột/móng KHÔNG đọc tự động (là chênh cao độ) -> đối tác nhập
        if ten and ten in bs: return _nd(bs[ten])
        return None

    def _rs_chieu_dai(self, ma, bs, ten=None):
        # ⛔ BẪY: L trong file thường là L-THÉP (gồm nối), KHÔNG phải L-nhịp bê tông -> KHÔNG tự lấy, để đối tác nhập.
        if ten and ten in bs: return _nd(bs[ten])
        return None

    def _rs_bs_only(self, ma, bs, ten=None):
        # Input CHỈ do ĐỐI TÁC cấp — không đọc tự động từ file (vd dài/cao/rộng/sâu tường, hố đào, số mặt trát).
        # Bản vẽ hiếm ghi mã+kích thước sẵn cho các đại lượng này -> luôn chờ đối tác nhập (chống bịa).
        if ten and ten in bs: return _nd(bs[ten])
        return None

    def _rs_chieu_day(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        codes = [w for w in _norm_label(ma or "").split() if any(c.isdigit() for c in w)]
        if not codes:
            return None            # KHÔNG có mã cụ thể -> KHÔNG quét cả file lấy 'dày' bất kỳ (chống bịa) -> đối tác nhập
        rex = re.compile(r"\b(?:day|d)\s*[=:]?\s*(\d{2,4})\s*(?:mm)?")
        for tx in self.texts:
            nv = _norm_label(tx["vn"])
            if codes and not all(_tok_bound(c, nv) for c in codes): continue
            if "day" not in nv and "ban day" not in nv: continue
            m = rex.search(nv)
            if m and 50 <= int(m.group(1)) <= 1000:
                return {"gia_tri": float(m.group(1)), "nguon": "doc_verbatim", "handle": tx["handle"],
                        "chua_chac": False, "do_tin_cay": "trung_binh", "giai_thich": "bề dày ghi '%s'" % tx["vn"][:30]}
        return None

    def _rs_dien_tich_ghi_san(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        toks = [w for w in _norm_label(ma or "").split() if w]
        if not toks:
            return None            # KHÔNG có mã cụ thể -> KHÔNG quét cả file vơ 'diện tích Xm2' bất kỳ (chống bịa
                                   # diện tích sàn từ số vô chủ) -> đối tác nhập dien_tich qua chat. Đồng bộ _rs_chieu_day.
        rex = re.compile(r"(\d+(?:[.,]\d+)?)\s*m2")
        for tx in self.texts:
            nv = _norm_label(tx["vn"])
            if not all(_tok_bound(t, nv) for t in toks): continue
            m = rex.search(nv)
            if m and "dien tich" in nv:
                return {"gia_tri": float(m.group(1).replace(",", ".")), "nguon": "doc_verbatim", "handle": tx["handle"],
                        "chua_chac": False, "do_tin_cay": "cao", "giai_thich": "diện tích ghi '%s'" % tx["vn"][:40]}
        return None

    def _cau_kien_hien_dien(self, ma_cau_kien):
        """Kiểm tra TẤT ĐỊNH: mã cấu kiện có XUẤT HIỆN trong bản vẽ không (dựa token MÃ có chữ số).
        Trả (ton_tai, kiem_tra_duoc). kiem_tra_duoc=False khi mã KHÔNG có token chữ số -> không đủ
        căn cứ khẳng định vắng mặt -> KHÔNG chặn (tránh false-negative). Dùng chung _norm_label +
        _tok_bound với mọi resolver, nên resolver đọc được thì hàm này CHẮC CHẮN thấy (không mâu thuẫn)."""
        toks = [w for w in _norm_label(ma_cau_kien or "").split() if w]
        codes = [w for w in toks if any(c.isdigit() for c in w)]
        if not codes:
            # Mã KHÔNG có token chữ số (vd 'GHOSTINOX') -> vẫn có thể là mã BỊA. Kiểm token CHỮ: nếu KHÔNG token
            # nào (dù chữ) xuất hiện ở BẤT KỲ text nào -> khẳng định vắng mặt (chặn). Nếu có ≥1 token hiện diện
            # (vd 'inox','cửa' — từ thật) -> không đủ căn cứ chặn (giữ nguyên hành vi cũ, tránh false-negative).
            alpha = [w for w in toks if any(c.isalpha() for c in w)]
            if alpha and not any(_tok_bound(w, _norm_label(tx["vn"])) for tx in self.texts for w in alpha):
                return False, True
            return True, False
        for tx in self.texts:
            lab = _norm_label(tx["vn"])
            if all(_tok_bound(c, lab) for c in codes):
                return True, True
        return False, True

    def _loai_tu_ban_ve(self, ma_cau_kien):
        """Suy LOẠI cấu kiện theo NHÃN bản vẽ: tìm text có 'TỪ-LOẠI <mã>' liền nhau (vd 'DẦM DM-1' -> {dam}).
        Data-driven (dựa nhãn GHI RÕ, KHÔNG đoán theo prefix mã -> tránh overfit). Trả set loại; RỖNG nếu
        bản vẽ không ghi loại liền mã -> KHÔNG kết luận (không chặn). Chỉ để bắt hỏi SAI LOẠI cấu kiện."""
        _sd = lambda s: re.sub(r"(?<=[a-zđ])-(?=\d)", "", s)   # 'dm-1' -> 'dm1' (giống _tok_bound)
        codes = [_sd(w) for w in _norm_label(ma_cau_kien or "").split() if any(c.isdigit() for c in w)]
        if not codes:
            return set()
        loai = set()
        for tx in self.texts:
            nv = _sd(_norm_label(tx["vn"]))
            for kw, typ in _LOAI_KW:
                if typ in loai:
                    continue
                if any(re.search(r"\b%s\b[\s:().]{0,3}%s\b" % (kw, re.escape(c)), nv) for c in codes):
                    loai.add(typ)
        return loai

    def tinh_dai_luong(self, ten_dai_luong, ma_cau_kien="", inputs_bo_sung="", **_):
        """TÍNH đại lượng từ số liệu CÓ SẴN. Đủ input -> tính + sơ đồ; thiếu -> inputs_da_co + inputs_thieu.
        Cấu kiện KHÔNG có trong bản vẽ -> khong_tim_thay (không mời nhập số cho thứ không tồn tại)."""
        key = _chuan_hoa_ten_dai_luong(ten_dai_luong)
        if not key:
            return {"co_ket_qua": False, "loi": "Chưa hỗ trợ tính '%s'." % ten_dai_luong,
                    "cac_dai_luong_ho_tro": [f["ten"] for f in _FORMULAS.values()]}
        F = _FORMULAS[key]
        # CẢNH BÁO LỆCH ĐẠI LƯỢNG: hỏi 'thể tích'/'diện tích' nhưng công thức khớp chỉ tính được KHỐI LƯỢNG (kg)
        # — vd 'thể tích inox' -> khoi_luong_thep_hinh. KHÔNG đổi số, nhưng phải LỘ để đối tác không nhầm m³/m² với kg.
        _tnq = unaccent(ten_dai_luong or "").lower()
        canh_bao_dv = ""
        if F["don_vi"] == "kg" and ("the tich" in _tnq or "dien tich" in _tnq):
            canh_bao_dv = (" ⚠ Bạn hỏi '%s' nhưng '%s' chỉ tính được KHỐI LƯỢNG (kg), KHÔNG phải m³/m² — đã tính theo "
                           "khối lượng; xác nhận nếu bạn cần đại lượng khác." % ((ten_dai_luong or "").strip(), F["ten"]))
        # CHỐNG BỊA (siết): người dùng nêu MÃ cụ thể mà mã đó KHÔNG có trong bản vẽ -> KHÔNG tìm thấy,
        # BẤT KỂ có inputs_bo_sung hay không (tuyệt đối không tính cho cấu kiện không tồn tại — vd 'SAN1'
        # với dien_tich/chieu_day do đối tác cấp vẫn ra số ảo). Chỉ cho tính thủ công thuần khi ma_cau_kien
        # để trống (kiem_tra_duoc=False -> người dùng chủ ý nhập tay, không gắn với cấu kiện cụ thể nào).
        ton_tai, kiem_tra_duoc = self._cau_kien_hien_dien(ma_cau_kien)
        if kiem_tra_duoc and not ton_tai:
            return {"dai_luong": ("%s %s" % (F["ten"], ma_cau_kien)).strip(), "co_ket_qua": False,
                    "khong_tim_thay": True, "can_bo_sung": False, "ma_cau_kien": ma_cau_kien,
                    "ghi_chu": "KHÔNG tìm thấy cấu kiện '%s' trong bản vẽ (mã không xuất hiện ở bất kỳ đoạn chữ nào). "
                               "Hãy nói thẳng với đối tác: cấu kiện này KHÔNG có trong file — TUYỆT ĐỐI KHÔNG hỏi "
                               "kích thước/số lượng để tính (KỂ CẢ khi đối tác đã cấp số). Đề nghị kiểm tra lại mã, "
                               "hoặc xem các mã có sẵn (liet_ke_so_luong / tra_cuu_so_luong)." % (ma_cau_kien or "?")}
        # CHỐNG SAI LOẠI: mã tồn tại nhưng bản vẽ ghi rõ nó là LOẠI KHÁC (vd hỏi thể tích MÓNG cho 'DM-1'
        # mà bản vẽ ghi 'DẦM DM-1') -> từ chối, không lấy tiết diện dầm tính móng. Chỉ chặn khi có BẰNG CHỨNG
        # loại xung đột (loai_thuc khác rỗng và không chứa loại kỳ vọng); bản vẽ không ghi loại -> vẫn tính.
        loai_ky_vong = _FORMULA_LOAI.get(key)
        if loai_ky_vong and ma_cau_kien:
            loai_thuc = self._loai_tu_ban_ve(ma_cau_kien)
            if loai_thuc and loai_ky_vong not in loai_thuc:
                return {"dai_luong": ("%s %s" % (F["ten"], ma_cau_kien)).strip(), "co_ket_qua": False,
                        "sai_loai": True, "can_bo_sung": False, "ma_cau_kien": ma_cau_kien,
                        "loai_thuc_te": sorted(_LOAI_VN.get(x, x) for x in loai_thuc),
                        "ghi_chu": "Bản vẽ ghi '%s' là loại %s, KHÔNG phải %s. KHÔNG tính '%s' cho mã này (tránh lấy "
                                   "kích thước loại khác). Hãy báo đối tác có thể đã nhầm loại cấu kiện, đề nghị hỏi đúng loại."
                                   % (ma_cau_kien, "/".join(sorted(_LOAI_VN.get(x, x) for x in loai_thuc)),
                                      _LOAI_VN.get(loai_ky_vong, loai_ky_vong), F["ten"])}
        bs = {}
        if inputs_bo_sung:
            try:
                import json as _json
                bs = _json.loads(inputs_bo_sung) if isinstance(inputs_bo_sung, str) else dict(inputs_bo_sung)
            except Exception: bs = {}
        # Task B — LỖ CỬA/CỬA SỔ: CHỈ 'xây tường' & 'diện tích trát' hỗ trợ 'lo_cua'. Truyền cho công thức khác
        # (đào/bê tông...) -> LỘ rõ (không âm thầm bỏ qua để đối tác tưởng đã trừ). lo_cua rỗng/None -> bỏ qua.
        if bs.get("lo_cua") and not F.get("tru_lo"):
            return {"dai_luong": ("%s %s" % (F["ten"], ma_cau_kien)).strip(), "co_ket_qua": False, "can_bo_sung": False,
                    "khong_ho_tro_tru_lo": True,
                    "ghi_chu": "'%s' KHÔNG hỗ trợ trừ lỗ cửa/cửa sổ — chỉ 'khối lượng xây tường' và 'diện tích trát' "
                               "nhận 'lo_cua'. Bỏ 'lo_cua' khỏi yêu cầu này." % F["ten"]}
        da_co, thieu, vals = [], [], {}
        for ten, dv, rs_name, _bs_key in F["inputs"]:
            res = getattr(self, rs_name)(ma_cau_kien, bs, ten)
            if res is None:
                thieu.append({"ten": ten, "don_vi": dv,
                              "cach_cung_cap": "đối tác nhập qua chat, vd '%s %s = ...'" % (ten.replace("_", " "), ma_cau_kien or "")})
            else:
                vals[ten] = res["gia_tri"]
                da_co.append({"ten": ten, "gia_tri": res["gia_tri"], "don_vi": dv, "nguon": res["nguon"],
                              "handle": res.get("handle"), "do_tin_cay": res.get("do_tin_cay"),
                              "chua_chac": res.get("chua_chac", False), "suy_doan_don_vi": res.get("suy_doan_don_vi", False),
                              "giai_thich": res.get("giai_thich", "")})
        ten_dl = ("%s %s" % (F["ten"], ma_cau_kien)).strip()
        if thieu:
            # Cấu kiện tồn tại (đã qua cửa kiểm tra ở đầu hàm) nhưng THIẾU số liệu -> mời đối tác cấp.
            # E) GỢI Ý m³ GHI SẴN liên quan: bản vẽ đã ghi sẵn khối lượng (vd 'ĐÀO MÓNG 860 M3') mà hệ ĐÃ đọc (stated_vol)
            # -> nêu để đối tác ĐỐI CHIẾU trước khi nhập kích thước (dùng lại dữ liệu đã đọc; nguyên văn + handle, KHÔNG tự tính).
            _kw = {"khoi_luong_dao_dat": ("dao",), "khoi_luong_dap_dat": ("dap", "san lap"),
                   "xay_tuong": ("xay",), "dien_tich_trat": ("trat",),
                   "the_tich_be_tong_cot": ("be tong", "btct"), "the_tich_be_tong_dam": ("be tong", "btct"),
                   "the_tich_be_tong_san": ("be tong", "btct", "san"), "the_tich_be_tong_mong": ("be tong", "btct", "mong")}
            goi_y = [{"text": sv["text"].strip(), "gia_tri": sv["m3"], "don_vi": "m³", "handle": sv["handle"]}
                     for sv in (getattr(self, "stated_vol", None) or [])
                     if any(k in unaccent(sv["text"]).lower() for k in _kw.get(key, ()))]
            gc = ("ĐÃ CÓ %d/%d số liệu. CÒN THIẾU: %s. Hãy nêu rõ cho đối tác biết đã có gì / thiếu gì, mời đối tác cấp "
                  "phần thiếu (nhập qua chat) rồi gọi lại để tính. TUYỆT ĐỐI KHÔNG tự bịa số thiếu."
                  % (len(da_co), len(F["inputs"]), ", ".join(t["ten"] for t in thieu)))
            r = {"dai_luong": ten_dl, "co_ket_qua": False, "can_bo_sung": True, "cach_tinh": F["cach_tinh"],
                 "inputs_da_co": da_co, "inputs_thieu": thieu}
            if goi_y:
                r["goi_y_ghi_san"] = goi_y
                gc += (" ⚠ Bản vẽ có GHI SẴN khối lượng liên quan: %s — nếu ĐÚNG là con số đối tác cần thì DÙNG LUÔN "
                       "(số đọc sẵn, có handle), khỏi nhập kích thước; nếu là hạng mục KHÁC thì bỏ qua."
                       % "; ".join("'%s'=%s m³[%s]" % (g["text"][:40], g["gia_tri"], g["handle"]) for g in goi_y))
            r["ghi_chu"] = gc
            return r
        # CHỐNG CRASH + SỐ VÔ LÝ: đối tác có thể nhập 'abc' / số âm / 0 qua chat. Mọi input phải là SỐ DƯƠNG hợp lệ;
        # nếu không -> KHÔNG tính (báo số liệu không hợp lệ, mời nhập lại) — tránh TypeError và đại lượng ÂM.
        xau = [x["ten"] for x in da_co
               if not (isinstance(x["gia_tri"], (int, float)) and not isinstance(x["gia_tri"], bool)
                       and math.isfinite(x["gia_tri"]) and x["gia_tri"] > 0)]
        if xau:
            return {"dai_luong": ten_dl, "co_ket_qua": False, "can_bo_sung": True, "so_lieu_khong_hop_le": xau,
                    "cach_tinh": F["cach_tinh"], "inputs_da_co": [x for x in da_co if x["ten"] not in xau],
                    "inputs_thieu": [{"ten": t, "don_vi": "mm", "cach_cung_cap": "nhập lại SỐ DƯƠNG (mm), vd '%s = 3600'" % t} for t in xau],
                    "ghi_chu": "Số liệu KHÔNG HỢP LỆ (phải là SỐ DƯƠNG > 0, đơn vị mm): %s. Đề nghị đối tác nhập lại đúng số."
                               % ", ".join(xau)}
        kq = F["compute"](vals)
        # CHỐNG BỊA (kết quả): input hữu hạn vẫn có thể TRÀN SỐ khi nhân (vd 16 × 1e308 = inf). Không bao giờ
        # trả 'kết quả' vô cực/NaN -> báo không hợp lệ (đối kháng: 4 giám định độc lập bắt lỗ hổng này).
        if not (isinstance(kq, (int, float)) and not isinstance(kq, bool) and math.isfinite(kq)):
            return {"dai_luong": ten_dl, "co_ket_qua": False, "can_bo_sung": True, "so_lieu_khong_hop_le": ["ket_qua"],
                    "cach_tinh": F["cach_tinh"], "inputs_da_co": da_co, "inputs_thieu": [],
                    "ghi_chu": "Kết quả tính ra KHÔNG hợp lệ (vô cực/tràn số) — số liệu đầu vào quá lớn/bất thường. "
                               "Đề nghị đối tác kiểm lại các số đã nhập (KHÔNG trả số vô nghĩa)."}
        # Task B — TRỪ LỖ cửa/cửa sổ: kq ở trên là GROSS (số cũ). Chỉ khi đối tác khai 'lo_cua' cho xay_tuong/
        # dien_tich_trat mới trừ; KHÔNG có lo_cua -> tru_extra=None -> giữ NGUYÊN kq cũ + KHÔNG thêm field (76 test không đổi).
        tru_extra = None
        if F.get("tru_lo") and bs.get("lo_cua"):
            st_lo, data_lo = self._resolve_lo_cua(bs["lo_cua"])
            if st_lo == "loi":
                r = {"dai_luong": ten_dl, "co_ket_qua": False, "can_bo_sung": True, "don_vi": F["don_vi"],
                     "cach_tinh": F["cach_tinh"], "gross_tham_khao": kq, "inputs_da_co": da_co, "inputs_thieu": []}
                r.update(data_lo)     # gắn cờ lỗi CỤ THỂ (khong_tim_thay/khong_tra_duoc_size/lo_vuot_so_luong/... + ghi_chu)
                return r
            if st_lo == "ok":
                if key == "xay_tuong":
                    prec, mul = 3, vals["be_day"] / 1e9
                    gross_raw = vals["chieu_dai"] * vals["chieu_cao"] * vals["be_day"] / 1e9
                else:                 # dien_tich_trat: lỗ khoét trên MỖI mặt trát -> nhân CHUNG so_mat của tường
                    prec, mul = 2, vals["so_mat"] / 1e6
                    gross_raw = vals["chieu_dai"] * vals["chieu_cao"] * vals["so_mat"] / 1e6
                ded_raw = data_lo["sum_area_mm2"] * mul
                net_raw = gross_raw - ded_raw
                net = round(net_raw, prec) if math.isfinite(net_raw) else net_raw
                # LỘ khi lỗ ≥ tường: kiểm SAU làm tròn (net<=0) — chặn CẢ ca net_raw>0 nhưng làm tròn về 0.0
                # (lỗ ≈ tường). TUYỆT ĐỐI không trả số 0/âm như 'kết quả hợp lệ'.
                if not math.isfinite(net_raw) or net <= 0:
                    return {"dai_luong": ten_dl, "co_ket_qua": False, "can_bo_sung": True, "don_vi": F["don_vi"],
                            "cach_tinh": F["cach_tinh"], "lo_lon_hon_tuong": True, "gross": kq,
                            "khau_tru_lo": round(ded_raw, prec), "so_lo": data_lo["so_lo"], "chi_tiet_lo": data_lo["chi_tiet"],
                            "ghi_chu": "TỔNG lỗ khấu trừ (%s %s) ≥ gross (%s %s) sau làm tròn — lỗ ≥ (hoặc ≈) tường, KHÔNG "
                                       "trả số 0/âm. Kiểm lại kích thước/số lượng lỗ hoặc kích thước tường."
                                       % (round(ded_raw, prec), F["don_vi"], kq, F["don_vi"])}
                tru_extra = {"gross": kq, "khau_tru_lo": round(ded_raw, prec),
                             "so_lo": data_lo["so_lo"], "chi_tiet_lo": data_lo["chi_tiet"]}
                kq = net   # ket_qua = NET (đã trừ lỗ)
        chua_chac = any(x["chua_chac"] for x in da_co)
        suy_dv = any(x.get("suy_doan_don_vi") for x in da_co)
        so_do = ["%s = %s %s (%s%s)" % (x["ten"], (round(x["gia_tri"], 2)), x["don_vi"], x["nguon"],
                                        ", CHƯA CHẮC" if x["chua_chac"] else "") for x in da_co]
        if tru_extra:
            so_do.append("gross (chưa trừ lỗ) = %s %s  [%s]" % (tru_extra["gross"], F["don_vi"], F["cach_tinh"]))
            for c in tru_extra["chi_tiet_lo"]:
                so_do.append("  − lỗ %s: %d×%d mm × %d (%s%s)" % (c["ma"] or "KT", c["rong"], c["cao"], c["sl"],
                             c["nguon"], (", handle=%s" % c["handle"]) if c["handle"] else ""))
            so_do.append("→ %s = gross − khấu trừ lỗ (%s %s) = %s %s"
                         % (F["ten"], tru_extra["khau_tru_lo"], F["don_vi"], kq, F["don_vi"]))
        else:
            so_do.append("→ %s = %s %s  [%s]" % (F["ten"], kq, F["don_vi"], F["cach_tinh"]))
        gc = ("Đây là SỐ DO HỆ THỐNG TÍNH (không phải số ghi sẵn trong file). "
              + ("Có input lấy theo GÁN VỊ TRÍ (đường kích thước gần cấu kiện) → CHƯA CHẮC đúng 100%; đối tác nên xác nhận."
                 if chua_chac else "Mọi input đọc trực tiếp từ file (đáng tin).")
              + (" ⚠ ĐƠN VỊ tiết diện (cm/mm) là SUY ĐOÁN theo kích thước (bản vẽ không ghi rõ) — nếu sai quy ước, "
                 "kết quả lệch 100×; đề nghị đối tác xác nhận đơn vị." if suy_dv else "")
              + canh_bao_dv)
        if tru_extra:
            gc += (" ĐÃ TRỪ %d lỗ cửa/cửa sổ (khấu trừ %s %s; gross %s %s). SỐ LƯỢNG lỗ do ĐỐI TÁC khai, KÍCH THƯỚC lỗ "
                   "do CODE (bảng thống kê)/đối tác cấp — hệ KHÔNG tự đoán cửa nào thuộc tường nào. Reveal/bệ cửa (mặt bên "
                   "lỗ) CHƯA cộng." % (tru_extra["so_lo"], tru_extra["khau_tru_lo"], F["don_vi"], tru_extra["gross"], F["don_vi"]))
        resp = {"dai_luong": ten_dl, "co_ket_qua": True, "ket_qua": kq, "don_vi": F["don_vi"], "can_bo_sung": False,
                "cach_tinh": F["cach_tinh"], "inputs_da_co": da_co, "inputs_thieu": [],
                "so_do_he_thong_tinh": so_do, "ghi_chu": gc}
        if tru_extra:
            resp["gross"] = tru_extra["gross"]; resp["khau_tru_lo"] = tru_extra["khau_tru_lo"]
            resp["so_lo"] = tru_extra["so_lo"]; resp["chi_tiet_lo"] = tru_extra["chi_tiet_lo"]
        return resp

    # ---- GĐ2d: BẢNG TỔNG HỢP khối lượng sơ bộ (gộp mọi số ĐỌC/TÍNH được, minh bạch NGUỒN) ----
    def _door_qty_for(self, code):
        """SL của MÃ CỬA (ưu tiên mục có 'cửa/vách/kính'; mơ hồ -> None)."""
        q = self.tra_so_luong(code)
        if not q: return None
        cua = [r for r in q if re.search(r"\bcua\b|vach|kinh", r["label_norm"])]
        if cua: return cua[0]["so_luong"]
        return q[0]["so_luong"] if len(q) == 1 else None

    def _struct_qty(self, code):
        """SL cấu kiện KẾT CẤU theo mã (loại mục cửa/vách để không lấy nhầm)."""
        q = self.tra_so_luong(code)
        if not q: return None
        nd = [r for r in q if not re.search(r"\bcua\b|vach|kinh", r["label_norm"])]
        pick = nd or q
        return pick[0]["so_luong"] if pick else None

    def _enum_structural_sections(self):
        """Liệt kê cấu kiện KẾT CẤU có tiết diện (mã lấy từ qty_index). a,b = mm-TƯƠNG ĐƯƠNG (cm đã ×10);
        kèm a_raw/b_raw/don_vi/suy_doan_don_vi để hiển thị. Bỏ cửa + token rác/vật liệu (chỉ mã kết cấu thật)."""
        out, seen = [], set()
        for e in (self.qty_index or []):
            for c in [w for w in e["label_norm"].split() if any(ch.isdigit() for ch in w)]:
                if c in seen: continue
                if not _is_structcode(c): continue       # loại token rác/vật liệu (vd 'hop-50x100x2', '(sl=2;')
                if self._door_size(c): continue          # cửa (bảng R×C) -> xử lý riêng
                td = self._doc_tiet_dien(c)
                if not td: continue
                seen.add(c)
                lo = self._loai_tu_ban_ve(c)
                typ = "cot" if "cot" in lo else ("dam" if "dam" in lo else None)
                out.append({"code": c, "a": td["a"], "b": td["b"], "a_raw": td.get("a_raw", td["a"]),
                            "b_raw": td.get("b_raw", td["b"]), "don_vi": td.get("don_vi", "mm"),
                            "suy_doan_don_vi": bool(td.get("suy_doan_don_vi")), "handle": td["handle"], "loai": typ})
        return out

    def tong_hop_khoi_luong(self, **_):
        """GĐ2d: gộp SL + diện tích cửa + thể tích cột/dầm + thép + m³ ghi sẵn + tầng thành 1 BẢNG,
        mỗi hàng ghi NGUỒN (đọc sẵn / hệ thống tính / tạm tính) + liệt kê 'cần bổ sung' + 'giả định'. Chống bịa."""
        rows, can_bs, gia_dinh = [], [], []
        seen = set()
        for e in (self.qty_index or []):                 # 1) SỐ LƯỢNG (đọc sẵn nhãn SL)
            k = (e["label_norm"], e["so_luong"])
            if k in seen: continue
            seen.add(k)
            rows.append({"hang_muc": e["label"].strip()[:44], "loai": "Số lượng", "gia_tri": e["so_luong"],
                         "don_vi": "bộ/cái", "nguon": "đọc sẵn (nhãn SL)", "handle": e.get("qty_handle", e["handle"])})
        for d in [x for x in (self.door_size_index or []) if x["confident"]]:   # 2) DIỆN TÍCH CỬA (R×C bảng)
            sl = self._door_qty_for(d["code"])
            rows.append({"hang_muc": "Cửa %s (%d×%d)" % (d["code"].upper(), d["w"], d["h"]), "loai": "Diện tích",
                         "gia_tri": round(d["area_m2"] * sl, 2) if sl else d["area_m2"], "don_vi": "m²",
                         "nguon": "hệ thống tính R×C×SL" if sl else "hệ thống tính R×C/cửa (thiếu SL)", "handle": d["handle"]})
            if not sl: can_bs.append("Cửa %s: thiếu SỐ LƯỢNG -> chỉ tính được diện tích/1 cửa." % d["code"].upper())
        typ = (getattr(self, "levels", None) or {}).get("typical_floor_h")     # 3) THỂ TÍCH BT cột/dầm
        for s in self._enum_structural_sections():
            sl = self._struct_qty(s["code"])
            td = "%d×%d %s%s" % (s["a_raw"], s["b_raw"], s["don_vi"], " (đv suy đoán)" if s.get("suy_doan_don_vi") else "")
            # cột = loại xác định 'cot' HOẶC (chưa xác định loại VÀ mã dạng c<digit>, vd c1/c-1) -> chỉ để RA số
            # TẠM TÍNH (có gắn cờ giả định); KHÔNG override nếu bản vẽ đã ghi rõ loại khác (dam...).
            is_cot = (s["loai"] == "cot") or (s["loai"] is None and re.match(r"c-?\d", s["code"]) is not None)
            if is_cot and typ and sl:
                v = round(s["a"] / 1000.0 * s["b"] / 1000.0 * typ * sl, 3)
                rows.append({"hang_muc": "Cột %s (%s)" % (s["code"].upper(), td), "loai": "Thể tích BT", "gia_tri": v,
                             "don_vi": "m³", "nguon": "TẠM TÍNH (tiết diện×%.2fm/tầng×SL=%d)" % (typ, sl), "handle": s["handle"]})
                gia_dinh.append("Cột %s: giả định cao = 1 tầng (%.2fm) — xác nhận nếu khác." % (s["code"].upper(), typ))
                if s.get("suy_doan_don_vi"):
                    gia_dinh.append("Cột %s: đơn vị tiết diện '%s' là SUY ĐOÁN (bản vẽ không ghi mm/cm) — sai quy ước lệch 100×, cần xác nhận."
                                    % (s["code"].upper(), s["don_vi"]))
            else:
                rows.append({"hang_muc": "%s (%s)" % (s["code"].upper(), td), "loai": "Tiết diện", "gia_tri": td,
                             "don_vi": "", "nguon": "đọc sẵn" + ("" if sl is None else ", SL=%d" % sl), "handle": s["handle"]})
                need = ("chiều dài" if not is_cot else ("số lượng" if typ else "chiều cao tầng"))
                can_bs.append("Thể tích %s: cần %s để tính." % (s["code"].upper(), need))
        if self.thep.get("co_bang"):                     # 4) THÉP
            rows.append({"hang_muc": "Cốt thép tròn (tổng)", "loai": "Khối lượng", "gia_tri": self.thep["tong_kg"],
                         "don_vi": "kg", "nguon": "đọc bảng thống kê thép", "handle": ""})
        if self.thep_hinh.get("co_bang"):
            rows.append({"hang_muc": "Thép hình/inox (tổng)", "loai": "Khối lượng", "gia_tri": self.thep_hinh["tong_kg"],
                         "don_vi": "kg", "nguon": "đọc bảng thống kê", "handle": ""})
        for sv in (getattr(self, "stated_vol", None) or []):   # 5) m³ GHI SẴN
            rows.append({"hang_muc": sv["text"][:44], "loai": "Khối lượng (ghi sẵn)", "gia_tri": sv["m3"],
                         "don_vi": "m³", "nguon": "đọc sẵn trên bản vẽ", "handle": sv["handle"]})
        lv = getattr(self, "levels", None) or {}          # 6) TẦNG
        if lv.get("typical_floor_h"):
            rows.append({"hang_muc": "Chiều cao tầng điển hình (số tầng ước tính: %s)" % lv.get("n_tang_est"),
                         "loai": "Cao độ/tầng", "gia_tri": lv["typical_floor_h"], "don_vi": "m",
                         "nguon": "hệ thống tính (hiệu cao độ)", "handle": ""})
        for sa in (getattr(self, "stated_area", None) or []):   # 7) DIỆN TÍCH GHI SẴN (Task C) — nhãn m² đọc verbatim
            rows.append({"hang_muc": sa["text"][:44], "loai": "Diện tích (ghi sẵn)", "gia_tri": sa["m2"], "don_vi": "m²",
                         "nguon": "đọc sẵn trên bản vẽ" + (" (có 'diện tích')" if sa["co_tu_khoa_dien_tich"] else " (chưa rõ loại)"),
                         "handle": sa["handle"]})
        # TỔNG PHỤ theo (LOẠI, ĐƠN VỊ): CODE cộng các dòng cùng loại+đơn vị (số đã có nguồn). Nhóm theo (loai,don_vi)
        # để KHÔNG gộp nhầm khác bản chất (Thể tích BT m³ ≠ Khối lượng ghi sẵn/đào móng m³); ô 'gia_tri' dạng chuỗi (tiết diện) bỏ qua.
        _tp = {}
        # 'Diện tích (ghi sẵn)' KHÔNG cộng: nhãn HỖN TẠP (mái+sơn+granit...) cộng lại vô nghĩa (Task C). Như 'Cao độ/tầng'.
        _khong_cong = {"Cao độ/tầng", "Diện tích (ghi sẵn)"}
        for r in rows:
            v = r.get("gia_tri")
            if r["loai"] not in _khong_cong and isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
                a = _tp.setdefault((r["loai"], r.get("don_vi") or ""), [0.0, 0]); a[0] += v; a[1] += 1
        tong_phu = [{"loai": lo, "don_vi": dv, "tong": round(t, 2), "so_dong": n} for (lo, dv), (t, n) in _tp.items()]
        return {"co_du_lieu": bool(rows), "so_hang": len(rows), "bang": rows, "tong_phu": tong_phu,
                "can_bo_sung": can_bs, "gia_dinh": gia_dinh,
                "ghi_chu": "BẢNG TỔNG HỢP SƠ BỘ. Cột 'nguon' cho biết số ĐỌC SẴN / HỆ THỐNG TÍNH / TẠM TÍNH (giả định). "
                           "'tong_phu' = TỔNG theo từng (loại, đơn vị) do HỆ THỐNG cộng (vd tổng bê tông m³, tổng thép kg) — "
                           "TRÌNH BÀY các tổng này cho đối tác; lưu ý mỗi tổng thuộc 1 loại riêng, KHÔNG gộp khác đơn vị/khác loại. "
                           "'can_bo_sung' = mục còn thiếu số liệu để tính; 'gia_dinh' = giả định đã dùng. KHÔNG coi là dự "
                           "toán chốt — chỉ gồm cấu kiện có nhãn đọc được. Xuất Excel để rà soát/hoàn thiện."}

    def xuat_excel(self, **_):
        """GĐ2d: ghi BẢNG TỔNG HỢP ra file .xlsx trong _renders/, trả file_id (host cho tải qua /file/<id>).
        Song song cách trả anh_id của ảnh PNG — hợp kiến trúc MCP (trả path, host phục vụ file)."""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill
        except Exception:
            return {"loi": "Máy chủ chưa cài openpyxl để xuất Excel (thêm 'openpyxl' vào requirements)."}
        th = self.tong_hop_khoi_luong()
        wb = Workbook(); ws = wb.active; ws.title = "Tong hop khoi luong"
        ws.append(["STT", "Hạng mục", "Loại", "Giá trị", "Đơn vị", "Nguồn", "Handle"])
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="2F5496")
        for i, r in enumerate(th["bang"], 1):
            ws.append([i, r["hang_muc"], r["loai"], r["gia_tri"], r["don_vi"], r["nguon"], r.get("handle", "")])
        ws.append([]); ws.append(["TỔNG PHỤ (hệ thống cộng theo LOẠI + ĐƠN VỊ):"])
        ws["A%d" % ws.max_row].font = Font(bold=True)
        for tp in th.get("tong_phu", []):
            row = ["", "TỔNG %s" % tp["loai"], "", tp["tong"], tp["don_vi"], "%d dòng cộng lại" % tp["so_dong"], ""]
            ws.append(row)
            for c in ws[ws.max_row]: c.font = Font(bold=True)
        ws.append([]); ws.append(["CẦN BỔ SUNG (còn thiếu số liệu để tính):"])
        for x in th["can_bo_sung"]: ws.append(["", x])
        ws.append([]); ws.append(["GIẢ ĐỊNH ĐÃ DÙNG:"])
        for x in th["gia_dinh"]: ws.append(["", x])
        ws.append([]); ws.append(["Ghi chú:", th["ghi_chu"]])
        for col, w in zip("ABCDEFG", [5, 42, 18, 12, 8, 34, 10]):
            ws.column_dimensions[col].width = w
        fid = "th_%s.xlsx" % uuid.uuid4().hex[:10]
        wb.save(os.path.join(RENDER_DIR, fid))
        return {"file_id": fid, "ten_file": "tong_hop_khoi_luong.xlsx", "so_hang": th["so_hang"],
                "ghi_chu": "Đã xuất bảng tổng hợp ra Excel (%d hàng). Host cho đối tác TẢI qua file_id. "
                           "Số liệu & nguồn như tong_hop_khoi_luong (bảng SƠ BỘ, không phải dự toán chốt)." % th["so_hang"]}

    # ============================================================
    # RENDER + HIGHLIGHT (mới — điểm khác biệt cốt lõi của demo 2)
    # ============================================================
    _CFG = Configuration(hatch_policy=HatchPolicy.IGNORE, min_lineweight=0.3)

    @staticmethod
    def _quick_point(e):
        d = e.dxf
        for attr in ("insert", "center", "start", "location"):
            if d.hasattr(attr):
                try: p = d.get(attr); return float(p[0]), float(p[1])
                except Exception: pass
        try:
            if e.dxftype() == "LWPOLYLINE":
                pts = list(e.get_points())
                if pts: return float(pts[0][0]), float(pts[0][1])
        except Exception: pass
        return None

    def _entities_in_window(self, window, hard_cap=20000):
        x0, y0, x1, y1 = window
        out = []
        for e in self.doc.modelspace():
            p = self._quick_point(e)
            if p is None: continue
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
                out.append(e)
                if len(out) >= hard_cap: break
        return out

    def render_region(self, window, highlights=None, dpi=110, max_px_in=16):
        """Render CHỈ entity trong window=(x0,y0,x1,y1) + khoanh đỏ highlights[{x,y}]. Trả path PNG."""
        ents = self._entities_in_window(window)
        w = max(window[2] - window[0], 1.0); h = max(window[3] - window[1], 1.0)
        aspect = h / w
        fig = plt.figure(figsize=(max_px_in, max(3, min(max_px_in * aspect, 22))))
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
        Frontend(RenderContext(self.doc), MatplotlibBackend(ax), config=self._CFG).draw_entities(ents)
        ax.set_xlim(window[0], window[2]); ax.set_ylim(window[1], window[3]); ax.set_aspect("equal")
        if highlights:
            r = max(w, h) * 0.02
            for hl in highlights:
                ax.add_patch(plt.Rectangle((hl["x"] - r, hl["y"] - r), 2 * r, 2 * r,
                                           fill=False, edgecolor="red", linewidth=2.0))
        fid = "hl_%s.png" % uuid.uuid4().hex[:10]
        fpath = os.path.join(RENDER_DIR, fid)
        fig.savefig(fpath, dpi=dpi); plt.close(fig)
        return fid, fpath, len(ents)

    @staticmethod
    def _largest_cluster(hits):
        """Gom các vị trí khớp thành cụm (greedy theo khoảng cách thích nghi) -> trả CỤM ĐÔNG NHẤT.
        Tránh render 1 cửa sổ trải khắp file (nhãn nằm rải nhiều sheet/chi tiết -> ảnh méo, chữ nhỏ)."""
        if len(hits) <= 1:
            return hits, 1
        xs = [h["x"] for h in hits]; ys = [h["y"] for h in hits]
        span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
        thr = max(span * 0.08, 8000.0)   # cùng cụm nếu gần nhau theo cả x,y
        clusters = []
        for p in hits:
            for c in clusters:
                if any(abs(p["x"] - q["x"]) < thr and abs(p["y"] - q["y"]) < thr for q in c):
                    c.append(p); break
            else:
                clusters.append([p])
        clusters.sort(key=len, reverse=True)
        return clusters[0], len(clusters)

    def highlight(self, tu_khoa=None, layer=None, gioi_han=80):
        """Tìm cấu kiện khớp + KHOANH ĐỎ trên ảnh bản vẽ. Trả {so_ket_qua, anh_id, vi_tri, ghi_chu}.
        Nếu các vị trí trải rộng nhiều cụm -> render CỤM ĐÔNG NHẤT để ảnh luôn rõ."""
        tk = (tu_khoa or "").strip(); ly = (layer or "").strip()
        if not tk and not ly:
            return {"loi": "Cần từ khoá hoặc layer để đánh dấu.", "so_ket_qua": 0}
        all_hits = [h for h in self.search_texts(tk, layer=ly or None) if (h.get("x") or h.get("y"))]
        if not all_hits:
            return {"so_ket_qua": 0, "anh_id": None,
                    "ghi_chu": "Không tìm thấy '%s' (có toạ độ) để đánh dấu." % (tk or ly)}
        all_hits = all_hits[:gioi_han]
        shown, n_clusters = self._largest_cluster(all_hits)
        xs = [h["x"] for h in shown]; ys = [h["y"] for h in shown]
        mx, Mx, my, My = min(xs), max(xs), min(ys), max(ys)
        padx = max((Mx - mx) * 0.15, 3000); pady = max((My - my) * 0.15, 3000)
        window = (mx - padx, my - pady, Mx + padx, My + pady)
        fid, _, n_ent = self.render_region(window, highlights=shown)
        vi_tri = [{"handle": h["handle"], "text": h["vn"], "layer": h.get("layer") or ""} for h in shown[:40]]
        cum = ("" if n_clusters <= 1 else
               " (ảnh phóng to CỤM ĐÔNG NHẤT %d/%d vị trí; các vị trí khác nằm ở chi tiết/sheet khác)"
               % (len(shown), len(all_hits)))
        return {"so_ket_qua": len(all_hits), "so_danh_dau_tren_anh": len(shown), "anh_id": fid,
                "so_entity_ve": n_ent, "vi_tri": vi_tri,
                "ghi_chu": ("Đã KHOANH ĐỎ vị trí nhãn '%s' trên ảnh bản vẽ (anh_id)%s. Đây là SỐ LẦN nhãn xuất "
                            "hiện trên hình, KHÔNG phải số lượng cấu kiện thật — số lượng thật xem tra_cuu_so_luong."
                            % (tk or ly, cum))}
