# -*- coding: utf-8 -*-
"""NGUỒN SỐ ĐO của đường kích thước — đọc ĐÚNG cái AutoCAD ghi, và không đọc nhầm LOẠI.
TẤT ĐỊNH, OFFLINE, KHÔNG tốn API. Bản vẽ SYNTHETIC (ezdxf) nên không phụ thuộc kho file gitignore.
Chạy:  python tests/test_so_do_dim.py

VÌ SAO CÓ SUITE NÀY (đo thật 2026-07-30, 78 file corpus / 64.436 đường kích thước):

(A) ĐƯỜNG ĐO GÓC bị coi là mm. `dimtype & 7 == 2` (góc) và `== 5` (góc 3 điểm) trả số đo bằng ĐỘ,
    nhưng vẫn bị đổ chung vào rổ kích thước. Chỉ 90/64.436 đường (0,14%) — nhưng ở
    '01-TD tuyen ong ap luc.dxf' chúng CHIẾM CHỖ "kích thước lớn nhất": máy báo **35.970,0 mm**
    cho một góc **359,7°** (359,7 × hệ số tỉ lệ 100), trong khi số đo lớn nhất AutoCAD tự lưu
    trong chính file đó là **212,1**. Sai ~170 lần, mà cùng lúc cờ co_dim_ty_le_do lại in câu
    TRẤN AN rằng các số này "khớp số IN trên bản vẽ" → vừa bịa số vừa chủ động trấn an.
    Lỗi này CÓ TRƯỚC bản vá hệ số tỉ lệ: không hệ số thì máy vẫn báo "359,7 mm" cho một góc.

(B) KHÔNG AI ĐỌC group code 42. AutoCAD ghi sẵn số đo THẬT của từng đường vào `actual_measurement`
    (DXF group code 42), có mặt **61.131/64.436 = 94,9%**. Phép thử KHÔNG THIÊN VỊ trên 54.735
    đường mà AutoCAD vẽ ra SỐ THUẦN: code42 đúng RIÊNG **2.936** ca · engine đúng RIÊNG **0** ca ·
    đúng cả hai 51.775 · không ai đúng 24. **Không một ca nào engine đúng mà code42 sai.**
    Tách theo loại: đường dài-XIÊN (aligned) engine chỉ đúng **600/1.613 = 37,2%** (62,8% sai);
    dài-thẳng 96,5%. Ngoài ra code42 cứu **607** đường mà `get_measurement()` trả 0.0 trong khi
    bản vẽ IN số thật — chúng đang bị cổng 'd > 0' vứt IM LẶNG.
    ⚠ code42 ĐÃ GỒM hệ số tỉ lệ → nhân _lf lần nữa là sai gấp bội.

⚠ ĐIỂM MÙ CỦA BỘ KIỂM CŨ (lý do phải có suite riêng): `ezdxf` khi render KHÔNG tự sinh code42, nên
mọi bản vẽ synthetic của suite test_ty_le_do đều đi đường hình học — bộ kiểm cũ MÙ hoàn toàn với
cả (A) lẫn (B). Suite này phải TỰ ĐẶT actual_measurement để chạm được nhánh đó.

⚠ RỦI RO TỒN DƯ ĐÃ ĐO, CHẤP NHẬN CÓ Ý THỨC: với DXF trước R2018, `dimtype == 5` từng dùng chung cho
ARC_DIMENSION (đo CHIỀU DÀI CUNG = mm, không phải góc). Toàn corpus chỉ có **7** đối tượng dimtype-5
(0,01%), nên sai lệch tối đa hai chiều đều không đáng kể. ezdxf hiện tải ARC_DIMENSION thành dxftype
RIÊNG nên đa số ca không đi vào nhánh này.
"""
import os, sys, io, math, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("READFILE_MAX_MB", "300")
os.environ.setdefault("HOC_LOG", "0")

import ezdxf
import tools_core as tc

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _luu(doc):
    p = os.path.join(tempfile.mkdtemp(), "t.dxf")
    doc.saveas(p)
    return p


def _dai(msp, y, dai=1000.0, he_so=None, c42=None):
    """1 đường kích thước DÀI-THẲNG. he_so -> khai DIMLFAC. c42 -> đặt số đo AutoCAD tự lưu."""
    ovr = None if he_so is None else {"dimlfac": he_so}
    d = msp.add_linear_dim(base=(0, y + 50), p1=(0, y), p2=(dai, y), override=ovr)
    d.render()
    if c42 is not None:
        d.dimension.dxf.actual_measurement = c42
    return d


def _goc(msp):
    """1 đường đo GÓC 90° (dimtype & 7 == 2). get_measurement() trả 90.0 = ĐỘ, không phải mm."""
    a = msp.add_angular_dim_2l(base=(60, 60), line1=((0, 0), (100, 0)), line2=((0, 0), (0, 100)))
    a.render()
    return a


def main():
    print("[N.1] ĐƯỜNG ĐO GÓC không được vào rổ kích thước (số đo của nó là ĐỘ)")
    doc = ezdxf.new(); msp = doc.modelspace()
    _goc(msp); _dai(msp, -200, 1000.0)
    d = tc.Drawing(_luu(doc))
    ok("chỉ còn 1 đường kích thước (đường góc bị loại)", len(d.dims) == 1, d.dims)
    ok("và đó là đường DÀI 1000, KHÔNG phải góc 90", abs(d.dims[0] - 1000.0) < 0.5, d.dims)
    ok("số 90 (độ) KHÔNG lọt vào rổ giá trị", all(abs(v - 90.0) > 0.5 for v in d.dim_vals), d.dim_vals)
    r = d.thong_tin_kich_thuoc()
    ok("so_duong_kich_thuoc đếm 1 (không đếm đường góc)", r.get("so_duong_kich_thuoc") == 1, r.get("so_duong_kich_thuoc"))
    ok("lon_nhat_mm = 1000, không bị góc chiếm chỗ", abs((r.get("lon_nhat_mm") or 0) - 1000.0) < 0.5, r.get("lon_nhat_mm"))

    print("[N.2] loại đường góc KHÔNG được làm hụt thống kê ĐỐI TƯỢNG (nó vẫn là 1 đối tượng trong file)")
    tk = d.thong_ke_doi_tuong()
    ok("vẫn đếm đủ 2 DIMENSION trong thống kê đối tượng",
       tk["theo_loai"].get("DIMENSION") == 2, tk["theo_loai"].get("DIMENSION"))

    print("[N.3] SỐ ĐO AutoCAD TỰ LƯU (group code 42) THẮNG số tính hình học")
    doc = ezdxf.new(); msp = doc.modelspace()
    _dai(msp, 0, 1000.0, c42=777.0)
    d = tc.Drawing(_luu(doc))
    ok("hình học 1000 nhưng file ghi 777 -> máy đọc 777", len(d.dims) == 1 and abs(d.dims[0] - 777.0) < 0.5, d.dims)

    print("[N.4] code42 ĐÃ gồm hệ số tỉ lệ -> TUYỆT ĐỐI không nhân hệ số lần nữa")
    doc = ezdxf.new(); msp = doc.modelspace()
    _dai(msp, 0, 1000.0, he_so=0.25, c42=777.0)
    d = tc.Drawing(_luu(doc))
    ok("có khai hệ số 0,25 + code42=777 -> vẫn 777 (KHÔNG ra 194,25)",
       len(d.dims) == 1 and abs(d.dims[0] - 777.0) < 0.5, d.dims)

    print("[N.5] code42 RÁC -> về đúng đường hình học cũ (chỉ THÊM thông tin, không bao giờ bớt)")
    for c42, ten in ((0.0, "0"), (-5.0, "âm"), (float("nan"), "NaN"), (float("inf"), "vô cực")):
        doc = ezdxf.new(); msp = doc.modelspace()
        _dai(msp, 0, 1000.0, c42=c42)
        d = tc.Drawing(_luu(doc))
        ok("code42 = %s -> giữ số hình học 1000" % ten,
           len(d.dims) == 1 and abs(d.dims[0] - 1000.0) < 0.5 and not math.isnan(d.dims[0]), d.dims)

    print("[N.6] code42 CỨU đường mà hình học đo ra 0.0 (đang bị cổng 'd > 0' vứt im lặng)")
    doc = ezdxf.new(); msp = doc.modelspace()
    _dai(msp, 0, 0.0, c42=550.0)          # p1 == p2 -> get_measurement() = 0.0
    _dai(msp, -200, 1000.0)
    d = tc.Drawing(_luu(doc))
    ok("đường đo-0 được khôi phục thành 550", any(abs(v - 550.0) < 0.5 for v in d.dims), d.dims)
    ok("và KHÔNG bị rụng khỏi rổ giá trị dùng được", any(abs(v - 550.0) < 0.5 for v in d.dim_vals), d.dim_vals)

    print("[N.7] KHÔNG có code42 -> hành vi CŨ nguyên vẹn (hệ số vẫn được áp)")
    doc = ezdxf.new(); msp = doc.modelspace()
    _dai(msp, 0, 1000.0, he_so=0.25)
    d = tc.Drawing(_luu(doc))
    ok("không code42 + hệ số 0,25 -> 250 (đúng như trước bản vá)",
       len(d.dims) == 1 and abs(d.dims[0] - 250.0) < 0.5, d.dims)

    print("[N.8] BỀN HƠN: hình học hỏng mà file có sẵn số đo thì KHÔNG mất đường kích thước")
    doc = ezdxf.new(); msp = doc.modelspace()
    _dai(msp, 0, 1000.0, c42=640.0)
    p = _luu(doc)
    _goc_gm = ezdxf.entities.Dimension.get_measurement

    def _no(self, *a, **k):
        raise RuntimeError("gia lap hinh hoc hong")

    try:
        ezdxf.entities.Dimension.get_measurement = _no
        d = tc.Drawing(p)
        ok("get_measurement ném lỗi nhưng có code42 -> vẫn giữ đường và đọc 640",
           len(d.dims) == 1 and abs(d.dims[0] - 640.0) < 0.5, d.dims)
    finally:
        ezdxf.entities.Dimension.get_measurement = _goc_gm

    print("[N.9] FAIL-OPEN: đọc hệ số hỏng vẫn không ảnh hưởng đường code42")
    doc = ezdxf.new(); msp = doc.modelspace()
    _dai(msp, 0, 1000.0, c42=333.0)
    p = _luu(doc)
    _goc_ov = ezdxf.entities.Dimension.override

    def _no2(self, *a, **k):
        raise RuntimeError("gia lap ezdxf cu")

    try:
        ezdxf.entities.Dimension.override = _no2
        d = tc.Drawing(p)
        ok("override ném lỗi -> vẫn đủ đường và vẫn đọc 333", len(d.dims) == 1 and abs(d.dims[0] - 333.0) < 0.5, d.dims)
    finally:
        ezdxf.entities.Dimension.override = _goc_ov

    print("[N.10] KHÔNG thêm trường số nào ra kết quả tool / rổ neo chống bịa không nở")
    import re
    import mcp_bridge as B
    doc = ezdxf.new(); msp = doc.modelspace()
    _goc(msp); _dai(msp, -200, 1000.0, c42=777.0)
    r = tc.Drawing(_luu(doc)).thong_tin_kich_thuoc()
    ok("không sinh khoá đếm kiểu 'so_dim_goc'/'so_code42'",
       not any(k for k in r if ("goc" in k or "code42" in k or "actual" in k)), list(r))
    ro = B._collect_numbers(r)
    ok("mọi số trong rổ đều truy được về số đo/thống kê đã có (không có 90 độ lọt vào)",
       90.0 not in ro, sorted(ro))
    ok("ghi_chu vẫn là chuỗi, không nhét số lạ", isinstance(r.get("ghi_chu"), str))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
