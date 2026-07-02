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
import os, re, time, uuid, logging, unicodedata
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
_TIETDIEN_RE = re.compile(r"(\d{2,4})\s*[x×*]\s*(\d{2,4})")  # '220x220', '(220 x 500)'

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


def _tok_bound(tok, lab):
    """Token có chữ số -> khớp RANH GIỚI TỪ, BỎ gạch ngang giữa chữ-số (C1 == C-1, ĐC3 == đc-3);
    vẫn chặn C-4 khớp nhầm C-40 (ranh giới). Token chữ -> substring (khớp font/ghép từ)."""
    if any(c.isdigit() for c in tok):
        t2 = tok.replace("-", "")
        l2 = re.sub(r"(?<=[a-zđ])-(?=\d)", "", lab)
        return re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(t2), l2) is not None
    return tok in lab


def _nd(val):
    """Input do ĐỐI TÁC cấp (không đọc từ file) — luôn ghi rõ nguồn."""
    try: g = float(val)
    except Exception: g = val
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
}

# Ánh xạ ngôn ngữ tự nhiên -> khoá công thức (LLM có thể truyền tên tự do).
_TEN_MAP = [
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
        self.levels = _build_levels(texts)                     # GĐ2c: cao độ -> chiều cao tầng điển hình
        self.stated_vol = _build_stated_volumes(texts)         # GĐ2d: m³ ghi sẵn trên bản vẽ

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
        cap = min(int(gioi_han or 40), 200)
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
        cap = min(int(gioi_han or 60), 200)
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
            tc = "cao" if ratio < 1.2 else ("trung_binh" if ratio < 3 else "thap")
            return {"gia_tri": di["value"], "handle": di["handle"], "khoang_cach": round(dist), "do_tin_cay": tc}
        return {"tim_thay_neo": True, "neo": chosen["neo"], "rong": _mk(chosen_b["ngang"]), "cao": _mk(chosen_b["doc"])}

    def _doc_tiet_dien(self, ma_cau_kien):
        """Đọc tiết diện 'AxB' từ chuỗi chứa mã cấu kiện (vd 'C1 (220x220)'). Phát hiện ĐA tiết diện
        (vd C4 có 220x500 VÀ 220x400) -> cờ nhieu_tiet_dien để engine cảnh báo. Trả dict hoặc None."""
        toks = [w for w in _norm_label(ma_cau_kien or "").split() if w]
        codes = [w for w in toks if any(c.isdigit() for c in w)]
        found = []
        for tx in self.texts:
            lab = _norm_label(tx["vn"])
            if codes and not all(_tok_bound(c, lab) for c in codes): continue
            m = _TIETDIEN_RE.search(tx["vn"])
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                if 50 <= a <= 5000 and 50 <= b <= 5000:
                    found.append((a, b, tx["handle"], tx["vn"].strip()))
        if not found: return None
        distinct = sorted(set((a, b) for a, b, _, _ in found))
        a, b, h, txt = found[0]
        return {"a": a, "b": b, "handle": h, "text": txt,
                "nhieu_tiet_dien": len(distinct) > 1, "so_tiet_dien": len(distinct), "cac_tiet_dien": distinct}

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
        gc = "tiết diện '%s'" % td["text"][:30]
        if td.get("nhieu_tiet_dien"):
            gc += " (⚠ có %d tiết diện %s — đang dùng cái đầu, đối tác xác nhận)" % (td["so_tiet_dien"], td["cac_tiet_dien"])
        return {"gia_tri": float(td[k]), "nguon": "doc_verbatim", "handle": td["handle"],
                "chua_chac": bool(td.get("nhieu_tiet_dien")),
                "do_tin_cay": "trung_binh" if td.get("nhieu_tiet_dien") else "cao", "giai_thich": gc}

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

    def _rs_chieu_day(self, ma, bs, ten=None):
        if ten and ten in bs: return _nd(bs[ten])
        rex = re.compile(r"\b(?:day|d)\s*[=:]?\s*(\d{2,4})\s*(?:mm)?")
        codes = [w for w in _norm_label(ma or "").split() if any(c.isdigit() for c in w)]
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
        rex = re.compile(r"(\d+(?:[.,]\d+)?)\s*m2")
        toks = [w for w in _norm_label(ma or "").split() if w]
        for tx in self.texts:
            nv = _norm_label(tx["vn"])
            if toks and not all(_tok_bound(t, nv) for t in toks): continue
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
                              "chua_chac": res.get("chua_chac", False), "giai_thich": res.get("giai_thich", "")})
        ten_dl = ("%s %s" % (F["ten"], ma_cau_kien)).strip()
        if thieu:
            # Cấu kiện tồn tại (đã qua cửa kiểm tra ở đầu hàm) nhưng THIẾU số liệu -> mời đối tác cấp.
            return {"dai_luong": ten_dl, "co_ket_qua": False, "can_bo_sung": True, "cach_tinh": F["cach_tinh"],
                    "inputs_da_co": da_co, "inputs_thieu": thieu,
                    "ghi_chu": "ĐÃ CÓ %d/%d số liệu. CÒN THIẾU: %s. Hãy nêu rõ cho đối tác biết đã có gì / thiếu gì, "
                               "mời đối tác cấp phần thiếu (nhập qua chat) rồi gọi lại để tính. TUYỆT ĐỐI KHÔNG tự bịa số thiếu."
                               % (len(da_co), len(F["inputs"]), ", ".join(t["ten"] for t in thieu))}
        kq = F["compute"](vals)
        chua_chac = any(x["chua_chac"] for x in da_co)
        so_do = ["%s = %s %s (%s%s)" % (x["ten"], (round(x["gia_tri"], 2)), x["don_vi"], x["nguon"],
                                        ", CHƯA CHẮC" if x["chua_chac"] else "") for x in da_co]
        so_do.append("→ %s = %s %s  [%s]" % (F["ten"], kq, F["don_vi"], F["cach_tinh"]))
        gc = ("Đây là SỐ DO HỆ THỐNG TÍNH (không phải số ghi sẵn trong file). "
              + ("Có input lấy theo GÁN VỊ TRÍ (đường kích thước gần cấu kiện) → CHƯA CHẮC đúng 100%; đối tác nên xác nhận."
                 if chua_chac else "Mọi input đọc trực tiếp từ file (đáng tin)."))
        return {"dai_luong": ten_dl, "co_ket_qua": True, "ket_qua": kq, "don_vi": F["don_vi"], "can_bo_sung": False,
                "cach_tinh": F["cach_tinh"], "inputs_da_co": da_co, "inputs_thieu": [],
                "so_do_he_thong_tinh": so_do, "ghi_chu": gc}

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
        """Liệt kê cấu kiện KẾT CẤU có tiết diện (mã lấy từ qty_index): [{code,a,b,handle,loai}]. Bỏ cửa."""
        out, seen = [], set()
        for e in (self.qty_index or []):
            for c in [w for w in e["label_norm"].split() if any(ch.isdigit() for ch in w)]:
                if c in seen: continue
                if self._door_size(c): continue          # cửa (bảng R×C) -> xử lý riêng
                td = self._doc_tiet_dien(c)
                if not td: continue
                seen.add(c)
                lo = self._loai_tu_ban_ve(c)
                typ = "cot" if "cot" in lo else ("dam" if "dam" in lo else None)
                out.append({"code": c, "a": td["a"], "b": td["b"], "handle": td["handle"], "loai": typ})
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
            sl = self._struct_qty(s["code"]); td = "%d×%d mm" % (s["a"], s["b"])
            # cột = loại xác định 'cot' HOẶC (chưa xác định loại VÀ mã dạng c<digit>, vd c1/c-1) -> chỉ để RA số
            # TẠM TÍNH (có gắn cờ giả định); KHÔNG override nếu bản vẽ đã ghi rõ loại khác (dam...).
            is_cot = (s["loai"] == "cot") or (s["loai"] is None and re.match(r"c-?\d", s["code"]) is not None)
            if is_cot and typ and sl:
                v = round(s["a"] / 1000.0 * s["b"] / 1000.0 * typ * sl, 3)
                rows.append({"hang_muc": "Cột %s (%s)" % (s["code"].upper(), td), "loai": "Thể tích BT", "gia_tri": v,
                             "don_vi": "m³", "nguon": "TẠM TÍNH (tiết diện×%.2fm/tầng×SL=%d)" % (typ, sl), "handle": s["handle"]})
                gia_dinh.append("Cột %s: giả định cao = 1 tầng (%.2fm) — xác nhận nếu khác." % (s["code"].upper(), typ))
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
        return {"co_du_lieu": bool(rows), "so_hang": len(rows), "bang": rows,
                "can_bo_sung": can_bs, "gia_dinh": gia_dinh,
                "ghi_chu": "BẢNG TỔNG HỢP SƠ BỘ. Cột 'nguon' cho biết số ĐỌC SẴN / HỆ THỐNG TÍNH / TẠM TÍNH (giả định). "
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
