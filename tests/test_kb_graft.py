# -*- coding: utf-8 -*-
"""L4 (kho kiến thức DEV-soạn — graft có GATE) — TẤT ĐỊNH, offline, DXF synthetic, KHÔNG cần corpus/API.
Khoá: gate bằng-chứng-dương (chỉ hỏi khi CHÍNH file có bằng chứng >1 nghĩa) + chống hỏi lặp + cap 1 câu/lượt
+ engine-đã-ghép-thì-không-hỏi + móc 'WORD - n.nnn' của cao_do_min_max + grounding sạch + degrade-safe + fail-open.
Chạy: python tests/test_kb_graft.py"""
import os, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("READFILE_MAX_MB", "300")

import ezdxf
import tools_core
import mcp_bridge as MB

PASS = FAIL = 0


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def lam(texts):
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for (x, y, s) in texts:
        msp.add_text(s).set_placement((x, y))
    p = os.path.join(tempfile.mkdtemp(), "t.dxf"); doc.saveas(p)
    return tools_core.Drawing(p)


def main():
    print("[L4] graft kho kiến thức: gate bằng-chứng-dương + confirm-only + không lọt grounding")

    # ---- [A] CẶP BẰNG CHỨNG: file có CẢ 'ĐC-1' LẪN 'DC-1' -> PHẢI hỏi (đúng ca corpus thật) ----
    dA = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1"), (0, 500, "L=800")])
    rA = dA.phan_loai_tin_hieu("ĐC-1")
    _emit("A1: phan_loai('ĐC-1') có '_kb' (câu hỏi confirm) khi cả 2 dạng raw cùng tồn tại", "_kb" in rA)
    kb = rA.get("_kb") or {}
    _emit("A2: cau_hoi nội-suy đúng ký hiệu ĐANG hỏi ('ĐC-1' trong câu)", "ĐC-1" in (kb.get("cau_hoi") or ""))
    _emit("A3: options gồm dai_coc/dam + khac_khong_chac (confirm-only, luôn có đường thoát)",
          {"dai_coc", "dam", "khac_khong_chac"} <= {o.get("key") for o in kb.get("phuong_an", [])})
    rA2 = dA.phan_loai_tin_hieu("ĐC-1")
    _emit("A4: hỏi LẠI cùng mã trong phiên -> chỉ note da_hoi_trong_phien (chống hỏi lặp RT4-4)",
          (rA2.get("_kb") or {}).get("da_hoi_trong_phien") is True and "cau_hoi" not in (rA2.get("_kb") or {}))
    rA3 = dA.doi_chieu_nghi_ngo("ĐC-1")
    _emit("A5: doi_chieu SAU khi đã hỏi -> KHÔNG lặp item kho (cap theo phiên xuyên tool)",
          not any(n.get("loai") == "đa nghĩa ký hiệu (kho kiến thức)" for n in rA3.get("nghi_ngo", [])))
    _emit("A6: kb_da_phat ghi (entry, option) đã phát — nền cho L5 xác nhận fail-closed",
          ("dc_dai_coc", "dai_coc") in dA.kb_da_phat and ("dc_dai_coc", "khac_khong_chac") in dA.kb_da_phat)

    # ---- [A'] doi_chieu là NGƯỜI HỎI ĐẦU -> item kho + '_kb' nằm TRONG item ----
    dA2 = lam([(0, 0, "ĐC-2"), (5000, 0, "DC-2")])
    rA4 = dA2.doi_chieu_nghi_ngo("ĐC-2")
    itk = [n for n in rA4.get("nghi_ngo", []) if n.get("loai") == "đa nghĩa ký hiệu (kho kiến thức)"]
    _emit("A7: doi_chieu hỏi đầu -> co_nghi_ngo=True + item 'đa nghĩa ký hiệu (kho kiến thức)' mang '_kb'",
          rA4.get("co_nghi_ngo") is True and len(itk) == 1 and "cau_hoi" in (itk[0].get("_kb") or {}))

    # ---- [B] KHÔNG BẰNG CHỨNG -> KHÔNG hỏi (chống bão-hỏi 50-80% đo được) ----
    dB = lam([(0, 0, "C2"), (0, 500, "C2"), (2000, 0, "C2")])
    _emit("B1: 'C2' đơn độc (không dạng đối, không 2-loại-index) -> phan_loai KHÔNG '_kb'",
          "_kb" not in dB.phan_loai_tin_hieu("C2"))
    _emit("B2: 'C2' đơn độc -> doi_chieu KHÔNG item kho",
          not any(n.get("loai") == "đa nghĩa ký hiệu (kho kiến thức)"
                  for n in dB.doi_chieu_nghi_ngo("C2").get("nghi_ngo", [])))

    # ---- [B'] ENGINE ĐÃ TỰ GHÉP 1 LOẠI -> KHÔNG hỏi dù có cặp bằng chứng ----
    dB2 = lam([(0, 0, "D2"), (5000, 0, "Đ2")])           # có cả d + dj trong file (bằng chứng cặp)
    dB2.section_index = [{"code": "d2", "handle": "X"}]   # giả lập engine đã ghép D2 vào tiết diện (1 loại)
    _emit("B3: engine đã ghép đúng 1 loại (section) -> suppression, KHÔNG hỏi",
          "_kb" not in dB2.phan_loai_tin_hieu("D2"))

    # ---- [C] MÓC 'WORD - n.nnn' (đường kích hoạt thật ca CH-2.700) ----
    dC = lam([(0, 0, "CH - 2.700"), (0, 900, "+3.600")])
    rC = dC.cao_do_min_max()
    kbc = rC.get("_kb") or {}
    _emit("C1: cao_do_min_max có canh_bao inline_cach + '_kb' câu hỏi",
          rC.get("co_cao_do") is True and any(c.get("dang") == "inline_cach" for c in rC.get("canh_bao", []))
          and "CH - 2.700" in (kbc.get("cau_hoi") or ""))
    _emit("C2: options đúng cặp nghĩa (cao_do_am / chieu_cao_kich_thuoc / khac_khong_chac)",
          {"cao_do_am", "chieu_cao_kich_thuoc", "khac_khong_chac"} == {o.get("key") for o in kbc.get("phuong_an", [])})
    _emit("C3: gọi lại -> da_hoi_trong_phien (không hỏi lặp)",
          (dC.cao_do_min_max().get("_kb") or {}).get("da_hoi_trong_phien") is True)
    dC2 = lam([(0, 0, "+3.600"), (0, 900, "-1.850")])
    _emit("C4: file KHÔNG có dạng cách -> KHÔNG '_kb' (không hỏi vô cớ)", "_kb" not in dC2.cao_do_min_max())

    # ---- [D] GROUNDING: '_kb' bị strip sạch, phần ngoài '_kb' giữ nguyên rổ ----
    base = MB._collect_numbers({k: v for k, v in rA.items() if k != "_kb"})
    strip = MB._collect_numbers(MB._strip_kb(rA))
    _emit("D1: rổ grounding sau _strip_kb == rổ của kết quả KHÔNG có '_kb' (kho góp đúng 0 số)", strip == base)
    _emit("D2: số file 'L=800' (ngoài _kb) VẪN trong rổ (không từ-chối-oan)",
          800.0 in MB._collect_numbers(MB._strip_kb(dA.tim_kiem("L=800") if hasattr(dA, "tim_kiem") else {"vn": "L=800"})))

    # ---- [E] DEGRADE-SAFE: tắt kho (_kienthuc=None) -> hành vi y hệt cũ, KHÔNG '_kb', KHÔNG crash ----
    _save = tools_core._kienthuc
    try:
        tools_core._kienthuc = None
        dE = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1"), (100, 300, "CH - 2.700"), (0, 900, "+3.600")])
        rE1, rE2, rE3 = dE.phan_loai_tin_hieu("ĐC-1"), dE.doi_chieu_nghi_ngo("ĐC-1"), dE.cao_do_min_max()
        _emit("E1: thiếu kho -> KHÔNG '_kb' ở cả 3 tool + không crash (hệ y hệt cũ)",
              "_kb" not in rE1 and "_kb" not in rE3
              and not any("_kb" in n for n in rE2.get("nghi_ngo", [])))
    finally:
        tools_core._kienthuc = _save

    # ---- [F] FAIL-OPEN: mã rác/emoji/rỗng -> không crash, không '_kb' ----
    rF1 = dA.phan_loai_tin_hieu("🔥🔥")
    rF2 = dA.phan_loai_tin_hieu("")
    _emit("F: mã rác/rỗng -> trả bình thường, không crash, không '_kb'",
          "_kb" not in rF1 and "_kb" not in rF2)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
