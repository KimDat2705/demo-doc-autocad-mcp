# -*- coding: utf-8 -*-
"""A3 — MÃ ĐỊNH DẠNG MTEXT/AutoCAD KHÔNG ĐƯỢC LÀM MỒI KHỚP ẢO. Tất định, offline, KHÔNG tốn API.

BUG GỐC (đo trên corpus thật): search_texts ghép nhánh THÔ chưa gỡ mã định dạng vào rổ so khớp
  hay = _norm(tx["vn"]) + " \\x01 " + _norm(tx["text"])
nên tên phông / mã màu / mã AutoCAD trở thành CHỮ để khớp:
  · tim_kiem("nhà để xe") = 3 kết quả khớp vào 'NHAØ XE GIAÙO VIEÂN' — bản vẽ KHÔNG có chữ "để";
    token 'de' đến từ 'Con-DE-nse' trong '\\fVNI-Helve-Condense|b0|i0|c0|p34;'
  · '%%C10' -> _norm -> '%%c10' nuốt trọn mã cấu kiện 'C1'  (kênh LỚN NHẤT: 29.728 lượt / 45 file)
  · '\\T1.0000;' khớp 'T1'  ·  '\\A1;' khớp 'A1'  ·  '\\W1;' làm 'tầng 1' trúng bản vẽ TẦNG 2
Dự án đã BIẾT lỗi này (chú thích tools_core.py:301-303: "lỗi CÓ SẴN của search_texts") nhưng chưa vá.

BA CHỖ VÁ, ĐI CÙNG MỘT LÁT (ship lẻ = ship lỗi):
  P1 vntext._mtext_codes  — gỡ mã TOGGLE trước (\\L\\O\\K ăn chữ tới dấu ';'), GIỮ nội dung \\S (phân số/chỉ số)
  P2 tools_core.search_texts — nhánh thô đi qua ma_ve_trang (gỡ mã -> KHOẢNG TRẮNG, đổi %%), fail-open
  P3 tools_core._build_qty_index — BỎ nhánh thô (đường DUY NHẤT nhánh thô sinh SỐ ra kết quả tool)

HAI CÂU TRẢ LỜI NGƯỢC NHAU VỀ 'GỠ THÀNH GÌ' — đo mới ra, đừng "sửa cho đồng bộ":
  · nhánh THÔ (P2) = KHOẢNG TRẮNG. Gỡ thành rỗng DÁN chữ và ĐẺ RA CHỮ KHÔNG CÓ THẬT:
    '{\\f…;WC C}Hç{\\f…; T}HÊ{\\f…;P N}HÊ{\\f…;T LÀ }2700' -> rỗng sinh ra chữ "thép" giữa ghi chú kiến trúc.
  · to_unicode (P1) = GIỮ RỖNG. Khoảng trắng ở đây CHẺ SỐ THẬT: 'mác 200#'->'mác 2 0 0#', '0.95'->'0.9'+'5'.

Chạy: python tests/test_ma_dinh_dang.py
"""
import os, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
os.environ.setdefault("READFILE_MAX_MB", "300")

import ezdxf                                    # noqa: E402
import tools_core as tc                         # noqa: E402
import vntext                                   # noqa: E402

PASS = FAIL = 0
_TMP = []


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def _dung(chuoi, mtext=True):
    """Dựng bản vẽ SYNTHETIC tất định. ezdxf.new() KHÔNG setup=True (setup tạo kiểu dáng mang hệ số 100)."""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    for i, s in enumerate(chuoi):
        if mtext:
            msp.add_mtext(s, dxfattribs={"layer": "GHICHU", "insert": (0, i * 10)})
        else:
            msp.add_text(s, dxfattribs={"layer": "GHICHU", "insert": (0, i * 10)})
    fd, path = tempfile.mkstemp(suffix=".dxf"); os.close(fd)
    doc.saveas(path)
    _TMP.append(path)
    return tc.Drawing(path)


def _so_kq(d, tu_khoa):
    return d.tim_kiem(tu_khoa=tu_khoa).get("so_ket_qua", -1)


def main():
    print("[A3] mã định dạng MTEXT/AutoCAD không được làm mồi khớp ảo")

    # =========================================================================
    # [A] KHỚP ẢO BỊ CHẶN — mỗi ca một KÊNH MỒI khác nhau, chuỗi lấy từ corpus thật
    # =========================================================================
    print("\n-- [A] khớp ảo bị chặn (7 ca) --")
    ao = [
        ("A1 tên phông (ca BUG GỐC)",
         r"\pxqc;{\fVNI-Helve-Condense|b1|i0|c0|p2;NHAØ XE GIAÙO VIEÂN}", "nhà để xe"),
        ("A2 codepage |c163|", r"{\fArial|b0|i0|c163|p34;BẠI TUYỆT}", "C1"),
        ("A3 mã màu \\Fhoatbif|c128;", r"\Fhoatbif|c128;ghi chú chung", "C1"),
        ("A4 mã AutoCAD %%C (kênh lớn nhất)", "- cèt thÐp <%%C10", "C1"),
        ("A5 \\W1; làm 'tầng 1' trúng TẦNG 2", r"{\W1;mÆt b»ng tÇng 2}", "tầng 1"),
        ("A6 \\H2x; làm 'tầng 2' trúng TẦNG 3", r"{\H2x;\LMẶT BẰNG KẾT CẤU TẦNG 3\H0.5x;\P}", "tầng 2"),
        # ⚠ chuỗi PHẢI chứa 'CỘT' — nếu không, ca đậu vì token 'cot' vắng mặt chứ không vì bản vá.
        # (Bản nháp đầu của ca này đậu SẴN trước khi vá = ca test vô dụng.)
        ("A7 \\T1.0000; khớp 'T1'", r"\T1.0000000000;CỘT BIÊN TRỤC A", "cột T1"),
    ]
    for ten, chuoi, tk in ao:
        d = _dung([chuoi])
        n = _so_kq(d, tk)
        _emit("%s: tim_kiem(%r) == 0" % (ten, tk), n == 0, "được %s" % n)

    # =========================================================================
    # [B] NỘI DUNG THẬT VẪN TÌM RA — chiều nguy hiểm nhất của mọi bản vá lọc
    # =========================================================================
    print("\n-- [B] nội dung thật vẫn tìm ra (9 ca) --")

    # B1 — ca CHỨNG MINH KHÔNG ĐƯỢC BỎ NHÁNH THÔ. Bản vẽ đổi PHÔNG GIỮA CHỪNG nên _looks_tcvn3
    # bắn trên cả chuỗi và _decode_tcvn3 làm hỏng phần Unicode vốn ĐÚNG ('HÒA': Ò=0xD2 -> 'ề').
    # Chỉ nhánh THÔ còn giữ được chữ đọc được. File thật 35,9 MB trong vận hành.
    d = _dung([r"MÆT C¾T §IÓN H×NH PHè vIỆT HÒA"])
    _emit("B1: trộn phông — 'Việt Hòa' VẪN tìm ra (nhánh thô phải sống)", _so_kq(d, "Việt Hòa") >= 1)

    # B2/B3 — toggle \L bị regex tham số NUỐT TRỌN tiêu đề tới dấu ';' (6 đoạn / 6 file corpus)
    s_L = r"{\Lchi tiÕt ch«n cèng btct d400; l=2m}"
    d = _dung([s_L])
    _emit("B2: toggle \\L — 'chi tiết' vẫn tìm ra", _so_kq(d, "chi tiết") >= 1)
    vn_L = vntext.to_unicode(s_L)
    _emit("B3: to_unicode KHÔNG còn nuốt tiêu đề sau \\L", "chi ti" in vn_L and "cèng" not in vn_L, vn_L)

    # B4-B8 — \S (phân số / chỉ số trên-dưới) là DỮ LIỆU, không phải mã: 406 đoạn / 81 chuỗi / 7 file
    # đang bị XOÁ SẠCH hôm nay.
    for ten, s, mong in [
        ("B4 \\S chỉ số dưới D1", r"\A1;(D{\H0.7x;\S^ 1;})", "D1"),
        ("B5 \\S Lneo1", r"L{\H0.7x;\S^ neo1;} 3Dd", "neo1"),
        ("B6 \\S ngày 19/3", r"vÝ ngµy \S19/3;/2011", "19/3"),
        ("B7 \\S mũ cm2", r"R\H0.7x;\S2^ ;=115kG/cm\S2^ ;", "cm2"),
        ("B8 \\S chỉ số Rb", r"R{\H0.7x;\S^ b;}=8.5mpa", "Rb"),
    ]:
        vn = vntext.to_unicode(s)
        _emit("%s: to_unicode giữ %r" % (ten, mong), mong in vn.replace(" ", ""), vn)

    d = _dung([r"{\H2x;\LMẶT BẰNG KẾT CẤU TẦNG 3\H0.5x;\P}"])
    _emit("B9: tầng ĐÚNG vẫn ra (chặn vá quá tay)", _so_kq(d, "tầng 3") >= 1)

    # =========================================================================
    # [C] CHỮ DÍNH KHI GỠ MÃ — cả hai chiều, hai chỗ hai câu trả lời NGƯỢC nhau
    # =========================================================================
    print("\n-- [C] chữ dính khi gỡ mã (4 ca) --")

    # C1/C2 — nhánh THÔ phải gỡ thành KHOẢNG TRẮNG, nếu gỡ thành rỗng thì ĐẺ RA CHỮ KHÔNG CÓ THẬT
    d = _dung([r"_ trÇn {\f.VnTime;WC C}Hç{\f.VnTime; T}HÊ{\f.VnTime;P N}HÊ{\f.VnTime;T LÀ }2700"])
    _emit("C1: gỡ mã KHÔNG được đẻ ra chữ 'thép' (rỗng sẽ dán thành 'cthepn')", _so_kq(d, "thép") == 0)
    d = _dung([r"6 Lç {\Fiso9|c0;%%C}22"])
    _emit("C2: gỡ mã KHÔNG được đẻ ra mã cột 'C2'", _so_kq(d, "C2") == 0)

    # C3/C4 — to_unicode phải GIỮ RỖNG, dùng khoảng trắng ở đây là CHẺ SỐ THẬT
    v = vntext.to_unicode(r"m{\H1x;}¸c 200#")
    _emit("C3: to_unicode KHÔNG chẻ số ('mác 200#' chứ không 'mác 2 0 0#')", "200" in v, v)
    v = vntext.to_unicode(r"{\H1x;}F14")
    _emit("C4: to_unicode KHÔNG chẻ mã cấu kiện ('F14' chứ không 'F 14')", "F14" in v, v)

    # =========================================================================
    # [D] FAIL-OPEN — mất kết quả nguy hiểm hơn thêm hit ảo
    # =========================================================================
    print("\n-- [D] fail-open (4 ca) --")
    d = _dung([r"{\fArial|b0 MÓNG BĂNG M1"])          # mã CỤT, không có dấu ';'
    _emit("D1: mã cụt không ném, vẫn tìm được nội dung", _so_kq(d, "móng băng") >= 1)
    d = _dung([r"THE\SP KHONG PHAI MTEXT"], mtext=False)
    _emit("D2: dấu '\\' trong TEXT thường không làm mất chuỗi", _so_kq(d, "khong phai") >= 1)
    for x in ("", None):
        try:
            vntext.ma_ve_trang(x); ok = True
        except Exception as ex:
            ok = False
        _emit("D3: ma_ve_trang(%r) không ném" % (x,), ok)
    goc = vntext.ma_ve_trang
    try:
        vntext.ma_ve_trang = lambda s: (_ for _ in ()).throw(RuntimeError("bom"))
        tc.ma_ve_trang = vntext.ma_ve_trang
        d = _dung([r"{\fArial;MÓNG CỌC M2}"])
        _emit("D4: ma_ve_trang NÉM -> về hành vi CŨ, KHÔNG trả rỗng, KHÔNG crash",
              _so_kq(d, "móng cọc") >= 1)
    finally:
        vntext.ma_ve_trang = goc
        tc.ma_ve_trang = goc

    # =========================================================================
    # [E] 'vn' KHÔNG ĐỔI NGOÀI PHẠM VI — chặn rủi ro R3 (vn nuôi ~20 index + rổ neo)
    # =========================================================================
    print("\n-- [E] vn không đổi ngoài phạm vi (6 ca) --")
    d = _dung(["CAO ĐỘ ĐÁY ĐÀI -13.700", r"{\fArial|b0|i0|c0|p34;CỐT SÀN +3.600}", "MẶT ĐẤT TỰ NHIÊN -0.450"])
    # ⚠ TÊN KHOÁ PHẢI ĐÚNG. Bản nháp đầu dùng 'nho_nhat' (không tồn tại) -> E1 đỏ oan, và E2 so
    # None==None nên XANH VĨNH VIỄN = ca test tautology. Đây đúng bẫy "bộ trích hỏng" của dự án:
    # số quá đẹp / ca luôn xanh là dấu hiệu hỏng, không phải tin mừng.
    cd = d.cao_do_min_max()
    _emit("E1: cao_do_min_max KHÔNG đổi số khi có mã định dạng",
          cd.get("cao_do_thap_nhat_m") == -13.7 and cd.get("so_marker") == 3, str(cd)[:150])
    d2 = _dung(["CAO ĐỘ ĐÁY ĐÀI -13.700", "CỐT SÀN +3.600", "MẶT ĐẤT TỰ NHIÊN -0.450"])
    cd2 = d2.cao_do_min_max()
    _emit("E2: cao_do_min_max giống hệt bản KHÔNG có mã (so trên KHOÁ CÓ THẬT)",
          cd.get("cao_do_thap_nhat_m") == cd2.get("cao_do_thap_nhat_m") is not None
          and cd.get("so_marker") == cd2.get("so_marker"),
          "%s vs %s" % (cd.get("cao_do_thap_nhat_m"), cd2.get("cao_do_thap_nhat_m")))
    _emit("E3: thong_tin_kich_thuoc không ném khi có mã", isinstance(d.thong_tin_kich_thuoc(), dict))
    _emit("E4: %%U (nhận diện sheet) KHÔNG bị đụng — dòng 1283 dùng nhánh thô là CỐ Ý",
          "%%U" in open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read())

    # E5 — P3: nhánh thô là đường DUY NHẤT nhánh thô sinh SỐ ra kết quả tool.
    # '{\f.VnAvantH|b1|i1|c0|p34;Tæng céng}' làm _QTY_RE hút chữ số '1' của '|b1|' -> đẻ "Tổng cộng = 1".
    d = _dung([r"{\f.VnAvantH|b1|i1|c0|p34;Tæng céng}"])
    q = d.tra_so_luong("tổng cộng")
    _emit("E5: qty KHÔNG còn bịa 'Tổng cộng = 1' từ mã phông '|b1|'",
          not any(e.get("so_luong") == 1 for e in (q or [])), str(q)[:140])
    src = open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read()
    _emit("E6: _build_qty_index KHÔNG còn ghép nhánh thô",
          '_qty_match(nv + " " + _norm_label(t.get("text"' not in src)

    # =========================================================================
    # [F] SOURCE-GUARD — khoá đúng hình dạng bản vá, chống hồi quy im lặng
    # =========================================================================
    print("\n-- [F] source-guard (4 ca) --")
    vsrc = open(os.path.join(ROOT, "vntext.py"), encoding="utf-8").read()
    _emit("F1: vntext có ma_ve_trang (dùng RIÊNG cho nhánh thô, không dùng để hiển thị)",
          "def ma_ve_trang(" in vsrc)
    _emit("F2: _mtext_codes có tham số sep, MẶC ĐỊNH rỗng (to_unicode giữ nguyên hành vi dán liền)",
          'def _mtext_codes(s, sep="")' in vsrc)
    _emit("F3: toggle gỡ TRƯỚC tham số (nếu ngược lại, \\L ăn chữ tới dấu ';')",
          vsrc.index("_MT_TOGGLE.sub") < vsrc.index("_MT_PARAM.sub"))
    _emit("F4: search_texts gỡ mã ở nhánh thô + có cổng rẻ (99,6% chuỗi không trả tiền regex)",
          "_tho_khop(tx[\"text\"])" in src and 'if not s or ("\\\\" not in s' in src)

    for p in _TMP:
        try: os.remove(p)
        except Exception: pass

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
