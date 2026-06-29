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
                    dims.append(v); dim_items.append({"handle": e.dxf.handle, "value": v})
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
            full = all(tok in lab for tok in toks)
            code = any(re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(c), lab) for c in codes) if codes else False
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

    def tom_tat(self):
        return {"name": self.name, "dxfversion": self.dxfversion, "so_layer": len(self.layers),
                "tong_doi_tuong": self.total, "so_doan_chu": len(self.texts),
                "so_kich_thuoc": len(self.dims), "so_nhan_tieu_de": len(self.sheets),
                "thep_tong_kg": self.thep.get("tong_kg", 0), "counts": self.counts}

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
