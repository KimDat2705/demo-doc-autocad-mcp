# -*- coding: utf-8 -*-
"""VÙNG CHƯA ĐỌC TỚI — chữ nằm TRONG ĐỊNH NGHĨA khối/ký hiệu ĐƯỢC CHÈN.
TẤT ĐỊNH, OFFLINE, KHÔNG tốn API. Bản vẽ SYNTHETIC (ezdxf) nên không phụ thuộc kho file gitignore.
Chạy:  python tests/test_vung_chua_doc.py

VẤN ĐỀ: `self.texts` chỉ gom chữ ở modelspace. Chữ bên trong ĐỊNH NGHĨA khối thì công cụ tìm kiếm
KHÔNG BAO GIỜ thấy — và tệ hơn, nó trả 'không có' bằng giọng chắc chắn. Dữ liệu THẬT đang mất, đo được
trên corpus: 'SL:67', 'L=1600', 'DN-01, L=15000, SL:02', 'l=1100'.
Lát này CHỈ DỰNG CỜ BOOL (không trả chuỗi, không trả số) — đường ĐỌC là tool riêng ở lát sau.

ĐO THẬT trên corpus (2026-07-31, qua engine thật):
  · 4/4 ca dương bật đúng: '2.KC nha cong an'+'l=1100' (modelspace 0) · +'lt-02' (khối '*U459' chèn 9 lần)
    · 'Be nuoc PCCC'+'DN-01' (tra_cuu_so_luong trả co_ghi=False) · '04. Cong, tuong rao'+'SL:67'.
  · 5/5 ca âm ra 0 — KHÔNG khớp ảo.
  · TỈ LỆ NHIỄU (cặp file×từ-khoá mà truy vấn ĐÃ có kết quả đúng ở modelspace nhưng vẫn bị bắt cờ):
    **15,3% -> 0,0%** sau khi siết vế 'chèn ≥2 lần' chỉ áp cho truy vấn MANG MÃ. Ngưỡng thiết kế là 10%.
    Cả 4 ca dương vẫn bật sau khi siết.
  · Chi phí: dựng rổ bóng ≤0,11s, quét ≤0,03s — so với nạp file 7-12s.

⚠ HAI CÁI BẪY ĐÃ TRẢ GIÁ, ĐỪNG DẪM LẠI:
  1. **Khớp trên chuỗi RAW** (như `search_texts` đang làm ở nhánh thứ hai) tạo BẰNG CHỨNG ẢO: file
     '04. Cong, tuong rao.dxf' + từ khoá 'C1' cho **41 hit ảo** vì khớp vào mã màu '\\|c163\\|' của nhãn
     phong thuỷ. Rổ bóng CHỈ khớp trên to_unicode. Đây là lỗi CÓ SẴN của search_texts — không được
     "sửa cho đồng bộ" theo chiều xấu.
  2. **Loại cả họ khối tiền tố '*'** xoá mất ca thật: khối ẩn danh '*U459' được chèn 9 lần và chứa
     'lt-02' (9 lanh tô THẬT). Chỉ loại TƯỜNG MINH '*d…' / '*model_space' / '*paper_space'.

⚠ Câu nudge KHÔNG được chứa cụm 'không có'/'không tìm thấy' — chúng nằm trong `_REFUSAL_MARKERS`, nếu
model chép lại vào câu trả lời thì `_guard_text` THOÁT SỚM và bỏ kiểm TOÀN BÀI.
"""
import os, sys, io, re, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("READFILE_MAX_MB", "300")
os.environ.setdefault("HOC_LOG", "0")

import ezdxf
import tools_core as tc
import mcp_bridge as B

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _ve(khoi, chen, ms_text=(), attdef=None):
    """khoi = {ten: [chuỗi,...]}; chen = [(ten_khoi, so_lan),...]; ms_text = chữ ĐẶT THẲNG ở modelspace."""
    doc = ezdxf.new(); msp = doc.modelspace()
    for ten, cac_chu in khoi.items():
        b = doc.blocks.new(name=ten)
        for ch in cac_chu:
            b.add_text(ch, dxfattribs={"height": 2.5})
        if attdef and ten == attdef[0]:
            b.add_attdef(tag="TAG1", text=attdef[1], dxfattribs={"height": 2.5})
    for ten, n in chen:
        for i in range(n):
            msp.add_blockref(ten, (i * 10.0, 0))
    for i, t in enumerate(ms_text):
        msp.add_text(t, dxfattribs={"height": 2.5}).set_placement((0, 50 + i * 10))
    p = os.path.join(tempfile.mkdtemp(), "t.dxf")
    doc.saveas(p)
    return p


def main():
    print("[W.1] DƯƠNG — chữ chỉ nằm trong khối ĐƯỢC CHÈN, modelspace rỗng -> BẬT cờ")
    d = tc.Drawing(_ve({"KYHIEU_A": ["SL:67", "L=1600"]}, [("KYHIEU_A", 1)]))
    r = d.tim_kiem(tu_khoa="SL:67")
    ok("tim_kiem vẫn trả 0 kết quả (KHÔNG đổi hành vi cũ)", r.get("so_ket_qua") == 0, r.get("so_ket_qua"))
    ok("nhưng dựng cờ co_o_vung_chua_doc", r.get("co_o_vung_chua_doc") is True, list(r))
    ok("và nối câu nudge", "chưa đọc tới" in r["ghi_chu"])

    print("[W.2] ÂM — khối MỒ CÔI (định nghĩa nhưng CHƯA TỪNG chèn) -> KHÔNG bao giờ báo")
    # ca độc đã đo: khối mồ côi ghi '156 cọc' trong khi bản vẽ sống ghi '131 CỌC'
    d = tc.Drawing(_ve({"KHOI_CHET": ["coc 350x350", "156 coc"]}, []))
    r = d.tim_kiem(tu_khoa="156")
    ok("không dựng cờ (nguồn không tin được thì KHÔNG trả)", "co_o_vung_chua_doc" not in r, list(r))

    print("[W.3] ÂM — khối nhãn DIMENSION '*D…' bị loại TƯỜNG MINH (máy đã đọc qua đường dimension)")
    d = tc.Drawing(_ve({"*D99": ["12300"]}, [("*D99", 3)]))
    r = d.tim_kiem(tu_khoa="12300")
    ok("không dựng cờ cho khối *D", "co_o_vung_chua_doc" not in r, list(r))

    print("[W.4] DƯƠNG — khối ẨN DANH '*U…' được chèn thì PHẢI GIỮ (đừng loại cả họ '*')")
    d = tc.Drawing(_ve({"*U459": ["lt-02"]}, [("*U459", 9)]))
    r = d.tim_kiem(tu_khoa="lt-02")
    ok("dựng cờ cho khối *U được chèn", r.get("co_o_vung_chua_doc") is True, list(r))

    print("[W.5] CỔNG KÉP — truy vấn ĐÃ có kết quả + khối chèn ĐÚNG 1 lần -> IM LẶNG (không hedging thừa)")
    d = tc.Drawing(_ve({"K1": ["D1 cua di"]}, [("K1", 1)], ms_text=("D1 cua di go",)))
    r = d.tim_kiem(tu_khoa="D1")
    ok("có kết quả ở modelspace", (r.get("so_ket_qua") or 0) > 0, r.get("so_ket_qua"))
    ok("KHÔNG dựng cờ", "co_o_vung_chua_doc" not in r, list(r))

    print("[W.6] CỔNG KÉP — đã có kết quả + khối chèn ≥2 lần + truy vấn MANG MÃ -> BẬT (bắt đếm hụt)")
    d = tc.Drawing(_ve({"K2": ["g3", "g3", "g3"]}, [("K2", 5)], ms_text=("g3",)))
    r = d.tim_kiem(tu_khoa="g3")
    ok("có kết quả ở modelspace", (r.get("so_ket_qua") or 0) > 0, r.get("so_ket_qua"))
    ok("và VẪN dựng cờ (máy đếm 1 trong khi khối chèn 5 lần)", r.get("co_o_vung_chua_doc") is True, list(r))

    print("[W.7] SIẾT NHIỄU — đã có kết quả + chèn ≥2 lần nhưng truy vấn KHÔNG mang mã -> IM LẶNG")
    # đo thật: để vế này bắn cho mọi từ khoá thì nhiễu 15,3% (>ngưỡng 10%); siết xong còn 0,0%
    d = tc.Drawing(_ve({"K3": ["be tong lot"]}, [("K3", 5)], ms_text=("be tong mac 250",)))
    r = d.tim_kiem(tu_khoa="be tong")
    ok("có kết quả ở modelspace", (r.get("so_ket_qua") or 0) > 0, r.get("so_ket_qua"))
    ok("KHÔNG dựng cờ cho từ vật liệu chung", "co_o_vung_chua_doc" not in r, list(r))

    print("[W.8] khối LỒNG NHAU vẫn với tới được")
    doc = ezdxf.new(); msp = doc.modelspace()
    trong = doc.blocks.new(name="TRONG"); trong.add_text("l=1100", dxfattribs={"height": 2.5})
    ngoai = doc.blocks.new(name="NGOAI"); ngoai.add_blockref("TRONG", (0, 0))
    msp.add_blockref("NGOAI", (0, 0))
    p = os.path.join(tempfile.mkdtemp(), "n.dxf"); doc.saveas(p)
    r = tc.Drawing(p).tim_kiem(tu_khoa="l=1100")
    ok("chữ trong khối lồng 2 tầng vẫn được thấy", r.get("co_o_vung_chua_doc") is True, list(r))

    print("[W.9] khối TỰ THAM CHIẾU -> KHÔNG treo (chặn độ sâu)")
    doc = ezdxf.new(); msp = doc.modelspace()
    b = doc.blocks.new(name="VONG"); b.add_text("xyz", dxfattribs={"height": 2.5})
    b.add_blockref("VONG", (0, 0))
    msp.add_blockref("VONG", (0, 0))
    p = os.path.join(tempfile.mkdtemp(), "v.dxf"); doc.saveas(p)
    import time as _t
    _t0 = _t.time()
    r = tc.Drawing(p).tim_kiem(tu_khoa="xyz")
    ok("chạy xong dưới 10 giây (không vòng vô hạn)", _t.time() - _t0 < 10.0, _t.time() - _t0)
    ok("và vẫn dựng cờ", r.get("co_o_vung_chua_doc") is True, list(r))

    print("[W.10] KHÔNG lấy ATTDEF (khuôn thuộc tính — giá trị thật đã đọc qua ATTRIB ở modelspace)")
    d = tc.Drawing(_ve({"KA": ["abc"]}, [("KA", 2)], attdef=("KA", "GIATRI_ATTDEF_9")))
    ds, _ = d._vcd_bong()
    ok("không chuỗi nào trong rổ bóng đến từ ATTDEF",
       not any("attdef" in it["hay"] for it in ds), [it["hay"] for it in ds][:5])

    print("[W.11] KIỂU + PROSE: cờ BOOL, câu SẠCH SỐ, KHÔNG chứa cụm gây TẮT hàng rào chống bịa")
    d = tc.Drawing(_ve({"KB": ["SL:67"]}, [("KB", 1)]))
    r = d.tim_kiem(tu_khoa="SL:67")
    ok("cờ là bool thật", isinstance(r.get("co_o_vung_chua_doc"), bool))
    ok("câu nudge KHÔNG chứa chữ số", re.search(r"\d", tc._VCD_CAU_NUDGE) is None, tc._VCD_CAU_NUDGE[:60])
    thap = tc._VCD_CAU_NUDGE.lower()
    ok("câu nudge KHÔNG chứa marker từ-chối (sẽ TẮT _guard_text toàn bài)",
       not any(m in thap for m in B._REFUSAL_MARKERS), [m for m in B._REFUSAL_MARKERS if m in thap])

    print("[W.12] rổ neo grounding KHÔNG nở vì cờ này")
    d0 = tc.Drawing(_ve({"KC": ["zzz"]}, [("KC", 1)]))
    r_khong = d0.tim_kiem(tu_khoa="SL:67")
    ro_co = B._collect_numbers(B._strip_neo(r))
    ro_khong = B._collect_numbers(B._strip_neo(r_khong))
    ok("cờ + câu nudge không bơm số mới vào rổ", ro_co - ro_khong == set(), sorted(ro_co - ro_khong))

    print("[W.13] 4 TOOL đều có cờ — gồm nhánh ÂM của tra_cuu_so_luong (ca 'DN-01' đã đo)")
    d = tc.Drawing(_ve({"KD": ["DN-01, L=15000, SL:02"]}, [("KD", 1)]))
    r1 = d.tra_cuu_so_luong(tu_khoa="DN-01")
    ok("tra_cuu_so_luong: co_ghi_so_luong vẫn False (KHÔNG đổi số)", r1.get("co_ghi_so_luong") is False)
    ok("tra_cuu_so_luong: có cờ", r1.get("co_o_vung_chua_doc") is True, list(r1))
    ok("dem_so_luong: có cờ", d.dem_so_luong(tu_khoa="DN-01").get("co_o_vung_chua_doc") is True)
    ok("liet_ke_so_luong (lọc không khớp): có cờ",
       d.liet_ke_so_luong(loc="DN-01").get("co_o_vung_chua_doc") is True)

    print("[W.14] FAIL-OPEN — đọc khối ném lỗi thì hệ y hệt như trước, KHÔNG cờ, KHÔNG vỡ")
    d = tc.Drawing(_ve({"KE": ["SL:67"]}, [("KE", 1)]))
    _goc = tc.Drawing._vcd_dem_chen

    def _no(self):
        raise RuntimeError("gia lap loi doc khoi")

    try:
        tc.Drawing._vcd_dem_chen = _no
        d2 = tc.Drawing(_ve({"KE": ["SL:67"]}, [("KE", 1)]))
        r2 = d2.tim_kiem(tu_khoa="SL:67")
        ok("không ném lỗi, schema cũ nguyên vẹn", r2.get("so_ket_qua") == 0 and "ket_qua" in r2, list(r2))
        ok("và KHÔNG dựng cờ (im lặng an toàn)", "co_o_vung_chua_doc" not in r2, list(r2))
    finally:
        tc.Drawing._vcd_dem_chen = _goc

    print("[W.15] từ khoá RỖNG -> không quét, không thêm khoá")
    r = d.tim_kiem(layer="0")
    ok("không có cờ khi chỉ lọc layer", "co_o_vung_chua_doc" not in r, list(r))

    print("[W.15b] CHẶN KHỚP MẢNH VỤN + CHẶN SUBSTRING (red-team implementation bắt được)")
    # (1) Tu khoa SO khop MANH VUN cua phan le / mau so ti le: do thuc te tu khoa '100' bat co o 11 file
    #     chi vi KHUNG TEN in TI LE BAN VE '1/100'. `_tok_bound` khong chan duoc vi '/', '.', ':' deu la
    #     ranh gioi hop le. Doi tac hoi mot kich thuoc pho bien tren ban ve BINH THUONG se bi dan hedging.
    # (2) Token KHONG mang chu so roi ve SUBSTRING TRAN -> 'cong' khop 'congtrinh'.
    K = tc.Drawing._vcd_tok_khop
    for tok, hay, mong, vi_sao in [
        ("100", "ti le 1/100", False, "mẫu số tỉ lệ"),
        ("100", "ti le 1:100", False, "tỉ lệ dấu hai chấm"),
        ("100", "cao do 3.100", False, "phần lẻ thập phân"),
        ("100", "l=100", True, "số THẬT phải giữ"),
        ("cong", "congtrinh abc", False, "substring — phải chặn"),
        ("cua", "cuaso", False, "substring — phải chặn"),
        ("cong", "cong, tuong rao", True, "khớp ĐÚNG TỪ phải giữ"),
        ("l=1100", "l=1100", True, "ca dương thật"),
        ("dn-01", "dn-01, l=15000, sl:02", True, "ca dương thật"),
    ]:
        ok("%r trong %r -> %s (%s)" % (tok, hay, mong, vi_sao), K(tok, hay) is mong, K(tok, hay))

    print("[W.16] KHÔNG khớp trên chuỗi RAW — chống BẰNG CHỨNG ẢO (ca 41 hit)")
    doc = ezdxf.new(); msp = doc.modelspace()
    b = doc.blocks.new(name="KF")
    b.add_mtext("\\pxqc;{\\fArial|b0|i0|c163|p34;BAI TUYET}", dxfattribs={"char_height": 2.5})
    msp.add_blockref("KF", (0, 0))
    p = os.path.join(tempfile.mkdtemp(), "raw.dxf"); doc.saveas(p)
    r = tc.Drawing(p).tim_kiem(tu_khoa="C1")
    ok("mã màu '|c163|' KHÔNG tạo hit ảo cho từ khoá 'C1'", "co_o_vung_chua_doc" not in r, list(r))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
