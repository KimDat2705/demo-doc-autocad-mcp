# -*- coding: utf-8 -*-
"""CHỮ IN GHI ĐÈ trên đường kích thước — LỘ chỗ chữ in KHÁC số máy đo được.
TẤT ĐỊNH, OFFLINE, KHÔNG tốn API. Bản vẽ SYNTHETIC (ezdxf) nên không phụ thuộc kho file gitignore.
Chạy:  python tests/test_chu_in_kich_thuoc.py

BỐI CẢNH: bản vẽ cho phép người vẽ GÕ ĐÈ chữ hiển thị của một đường kích thước. Khi chữ in không phải
con số máy đo được, số máy trả ra vẫn "trông như" kích thước bình thường — người đọc không có cách nào
biết. Ta CHỈ LỘ, TUYỆT ĐỐI KHÔNG đổi số nào.

ĐO THẬT (2026-07-31, 78 file corpus, sau khi đã loại đường đo GÓC và dùng số đo AutoCAD tự lưu):
  · 1.098 đường / 26 file bị luật bắt (khong_phai_so 987 · dieu_kien 100 · bieu_thuc 11)
  · Cờ 'lan rộng' (nối câu cảnh báo) bật ở **19/66 = 29%** file có đường kích thước — dưới trần 45%
    mà thiết kế đặt ra, nên GIỮ NGUYÊN ngưỡng.
  ⚠ Con số 837 dim/15 file trong tài liệu thiết kế cũ KHÔNG tái lập được — đừng dùng làm kỳ vọng.

VÌ SAO CẦN CẢ HAI MỆNH ĐỀ (đo thật, không phải phòng xa):
  · '02.Cap dien ngoai nha.dxf': luật phân loại bắt **0** đường, nhưng **66/66 = 100%** đường bị gõ đè
    -> chỉ nhánh 'hầu hết ghi đè' nhìn thấy file này. Bỏ mệnh đề đó là im lặng với đúng ca nguy hiểm.
  · '08.MAT CAT MUONG DAT CONG': 410/690 -> nhánh phân loại bắt, nhánh 'hầu hết' không đủ.

⚠ BẪY TEST ĐÃ TỪNG DẪM (giữ nguyên cả HAI biến thể khoảng trắng): nhãn chia khoảng/bậc thang trong
corpus viết '120x 15 Bậc =<>' (không cách quanh '='), còn biến thể '300 x 11 BËC = <>' (có cách) thì
luật xử lý khác. Test chỉ có biến thể CÓ CÁCH sẽ XANH trong khi corpus ĐỎ.
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


def _ve(cac_chu):
    """Bản vẽ có len(cac_chu) đường kích thước dài 1000. Phần tử None = KHÔNG gõ đè."""
    doc = ezdxf.new(); msp = doc.modelspace()
    for i, ch in enumerate(cac_chu):
        y = i * 100.0
        d = msp.add_linear_dim(base=(0, y + 50), p1=(0, y), p2=(1000, y))
        d.render()
        if ch is not None:
            d.dimension.dxf.text = ch
    p = os.path.join(tempfile.mkdtemp(), "t.dxf")
    doc.saveas(p)
    return p


def main():
    print("[C.1] BẢNG PHÂN LOẠI — lấy NGUYÊN VĂN từ corpus thật")
    bang = [
        # (chuỗi, nhãn mong đợi)
        ("h1", "khong_phai_so"), ("L", "khong_phai_so"), ("ØFs a100", "khong_phai_so"),
        ("15 BẬC x 120MM", "khong_phai_so"), ("L4M", "khong_phai_so"), ("B theo thùc tÕ", "khong_phai_so"),
        ("l min=<>", "dieu_kien"), ("h min=<>", "dieu_kien"), ("<=<>", "dieu_kien"), ("~<>", "dieu_kien"),
        ("320-<>", "bieu_thuc"), ("<>/2000", "bieu_thuc"), ("d+<>", "bieu_thuc"), ("400-<>", "bieu_thuc"),
        # ÂM — KHÔNG được bắt cờ
        ("5x150=<>", None), ("120x 15 Bậc =<>", None), ("300 x 11 BËC = <>", None), ("13*180=<>", None),
        ("7 tÇng x <>", None), ("{\\W0.6;<>}", None), ("%%C<>", None), ("<>", None),
        ("2100", None), ("5,5", None), ("13.600", None), ("3,000.09", None), ("2.76m", None),
    ]
    sai = [(s, tc._dang_chu_in(s), mong) for s, mong in bang if tc._dang_chu_in(s) != mong]
    ok("%d/%d chuỗi phân loại đúng" % (len(bang) - len(sai), len(bang)), not sai, sai[:6])

    print("[C.2] chuỗi ĐỔI FONT GIỮA CHỪNG phải ra số, không bị gắn cờ oan")
    raw = "{\\Fromans,vnd|c163;2\\Fromans,vnd|c0;5\\Fromans,vnd|c163;0}"
    ok("to_unicode ra '250'", tc.to_unicode(raw).strip() == "250", tc.to_unicode(raw))
    ok("và _dang_chu_in trả None (không báo động)", tc._dang_chu_in(raw) is None, tc._dang_chu_in(raw))

    print("[C.3] bản vẽ KHÔNG gõ đè -> KHÔNG cờ, KHÔNG câu cảnh báo (không nhiễu)")
    r = tc.Drawing(_ve([None] * 12)).thong_tin_kich_thuoc()
    ok("không có cờ nào", not any(k.startswith(("co_chu_in", "hau_het_chu", "canh_bao_kich")) for k in r), list(r))
    ok("ghi_chu không có cảnh báo", "⚠" not in r["ghi_chu"])

    print("[C.4] có chữ in đáng ngờ LAN RỘNG -> dựng cờ + nối câu")
    d = tc.Drawing(_ve(["ØFs a100"] * 12))
    r = d.thong_tin_kich_thuoc()
    ok("co_chu_in_khong_phai_so_do = True", r.get("co_chu_in_khong_phai_so_do") is True, r.get("co_chu_in_khong_phai_so_do"))
    ok("canh_bao_kich_thuoc_lan_rong = True", r.get("canh_bao_kich_thuoc_lan_rong") is True)
    ok("ghi_chu có nối câu cảnh báo", "ĐỐI CHIẾU TAY" in r["ghi_chu"])

    print("[C.5] mệnh đề 'HẦU HẾT GHI ĐÈ' — bắt được file mà luật phân loại MÙ")
    # mô phỏng '02.Cap dien ngoai nha.dxf': mọi đường đều gõ đè bằng SỐ THUẦN -> l8 = 0
    d = tc.Drawing(_ve(["300"] * 10))
    r = d.thong_tin_kich_thuoc()
    ok("luật phân loại KHÔNG bắt (số thuần)", "co_chu_in_khong_phai_so_do" not in r, list(r))
    ok("nhưng hau_het_chu_in_la_ghi_de = True", r.get("hau_het_chu_in_la_ghi_de") is True)
    ok("và vẫn nối câu cảnh báo", r.get("canh_bao_kich_thuoc_lan_rong") is True)

    print("[C.6] CỔNG LAN RỘNG — vài đường lẻ trong bản vẽ lớn thì KHÔNG kêu")
    d = tc.Drawing(_ve(["h1"] + [None] * 60))
    r = d.thong_tin_kich_thuoc()
    ok("vẫn dựng cờ 'có' (thông tin không mất)", r.get("co_chu_in_khong_phai_so_do") is True)
    ok("nhưng KHÔNG nối câu cảnh báo (1 đường/61 dưới ngưỡng)", "canh_bao_kich_thuoc_lan_rong" not in r, list(r))

    print("[C.7] KHÔNG ĐỔI BẤT KỲ SỐ NÀO — đây là bản vá CHỈ LỘ")
    a = tc.Drawing(_ve([None] * 6))
    b = tc.Drawing(_ve(["ØFs a100"] * 6))
    ok("cùng số đường kích thước", len(a.dims) == len(b.dims) == 6, (a.dims, b.dims))
    ok("cùng giá trị số đo (gõ đè KHÔNG làm dịch số)", sorted(a.dims) == sorted(b.dims), (a.dims, b.dims))
    ra, rb = a.thong_tin_kich_thuoc(), b.thong_tin_kich_thuoc()
    ok("nho_nhat/lon_nhat/pho_bien y hệt",
       (ra["nho_nhat_mm"], ra["lon_nhat_mm"], ra["gia_tri_pho_bien_mm"])
       == (rb["nho_nhat_mm"], rb["lon_nhat_mm"], rb["gia_tri_pho_bien_mm"]))

    print("[C.8] KIỂU + PROSE: cờ là BOOL, câu cảnh báo SẠCH CHỮ SỐ, KHÔNG trường đếm")
    r = tc.Drawing(_ve(["ØFs a100"] * 12)).thong_tin_kich_thuoc()
    for k in ("co_chu_in_khong_phai_so_do", "canh_bao_kich_thuoc_lan_rong"):
        ok("%s là bool thật" % k, isinstance(r.get(k), bool))
    them = r["ghi_chu"].split("⚠", 1)[1] if "⚠" in r["ghi_chu"] else ""
    ok("câu cảnh báo KHÔNG chứa chữ số", them and re.search(r"\d", them) is None, them[:80])
    ok("KHÔNG lộ trường ĐẾM nào (số đếm nở rổ neo)",
       not any(k for k in r if k.startswith(("so_chu_in", "so_ghi_de", "so_dim_chu", "so_vi_tri"))), list(r))

    print("[C.9] rổ neo grounding KHÔNG nở vì bản vá này")
    r0 = tc.Drawing(_ve([None] * 12)).thong_tin_kich_thuoc()
    ro1 = B._collect_numbers(B._strip_neo(r))
    ro0 = B._collect_numbers(B._strip_neo(r0))
    ok("cờ + câu cảnh báo không bơm số mới vào rổ", ro1 - ro0 == set(), sorted(ro1 - ro0))

    print("[C.10] FAIL-OPEN — bộ thu thập hỏng thì KHÔNG được nuốt đường kích thước")
    _goc = tc._thu_thap_chu_in

    def _no(*a, **k):
        raise RuntimeError("gia lap loi")

    try:
        tc._thu_thap_chu_in = _no
        d = tc.Drawing(_ve(["h1"] * 5))
        ok("vẫn đủ 5 đường kích thước", len(d.dims) == 5, d.dims)
        r = d.thong_tin_kich_thuoc()
        ok("và không dựng cờ (im lặng, KHÔNG báo oan)", "co_chu_in_khong_phai_so_do" not in r, list(r))
    finally:
        tc._thu_thap_chu_in = _goc

    print("[C.11] gọi UNBOUND với đối tượng giả (khuôn test_ole_canh_bao) -> KHÔNG AttributeError")

    # Đối tượng giả mang ĐÚNG bộ thuộc tính mà tests/test_ole_canh_bao.py cấp (ole_nhung/dims/dim_vals/
    # dim_top/doc) + method _gan_canh_bao_nhung mà nhánh 'không có dim' gọi tới. CỐ Ý không có
    # dim_chu_in_stat: nếu code truy cập thẳng thay vì getattr thì ca này vỡ.
    class _Gia:
        ole_nhung, dims, dim_vals, dim_top, doc = [], [], [], [], None

        def _gan_canh_bao_nhung(self, r):
            return r

    try:
        tc.Drawing.thong_tin_kich_thuoc(_Gia())
        ok("không ném AttributeError (bắt buộc dùng getattr)", True)
    except AttributeError as ex:
        ok("không ném AttributeError (bắt buộc dùng getattr)", False, ex)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
