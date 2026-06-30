# -*- coding: utf-8 -*-
"""Kiểm chứng TẤT ĐỊNH các giả thuyết 'đọc thiếu' (không Gemini) -> chỉ rõ bug THẬT tầng tool."""
import os, sys, io
os.environ["READFILE_MAX_MB"] = "300"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from tools_core import Drawing

KT = r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/1. Kien truc MN Gia Loc.dxf"
KC = r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/2. KetCau MN GiaLoc.dxf"
HT = r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/demo_doc_autocad/_uploads/rachmop.dxf"


def show(title, val):
    print("  -", title, "->", val)


print("############ KIẾN TRÚC ############")
kt = Drawing(KT)
print("[G1] SL conventions — lan can LC1 (SL: 5):")
for code in ["LC1", "LC2", "LC8", "vách kính VK1"]:
    r = kt.tra_so_luong(code)
    show("tra_so_luong('%s')" % code, [(m["label"][:30], m["so_luong"]) for m in r[:3]] or "RỖNG")

print("[G2] Xà gồ thép hộp 40x80x2mm 2472.64kg (nằm trong TEXT note):")
show("thong_ke_thep_hinh có 2472?", any(abs(v["kg"] - 2472.64) < 1 for v in (kt.thep_hinh.get("by_show") or {}).values()))
sg = kt.search_texts("xà gồ")
show("search('xà gồ') số kết quả", len(sg))
for h in sg[:3]: show("  text", h["vn"][:70])

print("[G3] Mác bê tông (text rời):")
for kw in ["mác", "cấp độ bền", "B20"]:
    show("search('%s')" % kw, len(kt.search_texts(kw)))

print("[G4] Mác thép CB400-V / CB240 (text note):")
show("search('CB400')", len(kt.search_texts("CB400")))
show("search('cb240')", len(kt.search_texts("cb240")))

print("[G5] thong_ke_thep ghi_chu có cảnh báo thép hình không (chống đọc-sai tổng):")
tt = kt.thong_ke_thep()
show("tong_khoi_luong_kg", tt.get("tong_khoi_luong_kg"))
show("ghi_chu nhắc thép hình?", "thép hình" in tt.get("ghi_chu", ""))

print("\n############ KẾT CẤU ############")
kc = Drawing(KC)
print("[G6] SL-25 (gạch ngang) — ĐC-3:")
for code in ["ĐC-3", "DC-3", "ĐC-1", "C-1", "C-4"]:
    r = kc.tra_so_luong(code)
    show("tra_so_luong('%s')" % code, [(m["label"][:28], m["so_luong"]) for m in r[:2]] or "RỖNG")

print("[G7] Tổng số cọc 131 (text note):")
r = kc.tra_so_luong("cọc")
show("tra_so_luong('cọc')", [(m["label"][:40], m["so_luong"]) for m in r[:3]] or "RỖNG")
show("search('tổng số cọc')", [h["vn"][:50] for h in kc.search_texts("tổng số cọc")[:2]])

print("[G8] C4 có 2 tiết diện (220x500 và 220x400):")
c4 = [h["vn"] for h in kc.search_texts("C4") if "220" in h["vn"]]
show("search('C4') có tiết diện", list(dict.fromkeys(c4))[:6])

print("[G9] thép tổng: tròn vs hình:")
show("thep tròn tong_kg", kc.thep.get("tong_kg"))
show("thep hình tong_kg", kc.thep_hinh.get("tong_kg"))

print("[G10] Đường kính thép nhiều kg nhất (bẫy: Ø10 chứ không phải Ø22):")
by = kc.thep.get("by_dk") or {}
top = sorted(by.items(), key=lambda x: -x[1]["kg"])[:3]
show("top kg", [(k, round(v["kg"], 1)) for k, v in top])

print("\n############ HẠ TẦNG ############")
ht = Drawing(HT)
print("[G11] Cọc font 'Cäc' vs 'Coc' — search('cọc') bắt cả hai?")
cc = ht.search_texts("cọc")
show("search('cọc') số kết quả", len(cc))
import re
variants = set()
for h in cc:
    m = re.findall(r"[Cc][äöo][cs]?[:]?", h["text"][:6])
    variants.add(h["text"][:5])
show("vài biến thể raw", list(variants)[:8])

print("[G12] Thép ống DN80, Thép Ø10 (text, KHÔNG bảng):")
show("thong_ke_thep có bảng?", ht.thong_ke_thep().get("co_bang_thong_ke"))
show("search('thép ống')", [h["vn"][:40] for h in ht.search_texts("thép ống")[:3]])
show("search('DN80')", len(ht.search_texts("DN80")))

print("[G13] Mác BT M200/M150 (text):")
show("search('M200')", [h["vn"][:40] for h in ht.search_texts("M200")[:2]])
show("search('Khối BT đúc sẵn')", [h["vn"][:50] for h in ht.search_texts("Khối BT đúc sẵn")[:2]])

print("\nXONG gap_verify.")
