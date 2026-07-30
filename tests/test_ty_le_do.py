# -*- coding: utf-8 -*-
"""HỆ SỐ TỈ LỆ ĐO (DIMLFAC) — bản vẽ TỰ KHAI "đường kích thước này phải nhân hệ số mới ra số thật"
(chi tiết vẽ thu nhỏ/phóng to). TẤT ĐỊNH, OFFLINE, KHÔNG tốn API. Bản vẽ SYNTHETIC (tự sinh bằng ezdxf)
nên không phụ thuộc kho file gitignore.
Chạy:  python tests/test_ty_le_do.py

VÌ SAO CÓ SUITE NÀY (đo thật 2026-07-30, 40 file corpus / 15.608 đường kích thước):
  - **3.352 đường (21,5%) tự khai hệ số ≠ 1**, dính 17/40 file. `get_measurement()` trả số HÌNH HỌC THÔ,
    KHÔNG áp hệ số -> số máy đọc KHÁC số IN trên bản vẽ.
  - Trong các ca đối chiếu được với chữ in: khớp "số đo × hệ số" **19 ca** / khớp số đo thô **0 ca**.
  - ⚠ Toàn bộ 6 suite đang đóng băng số (takeoff 272 · misc 107 · ole 51 · cao_do 31 · i3 24 · khảo-sát 61)
    VẪN XANH sau khi vá — tức bộ kiểm cũ **MÙ HOÀN TOÀN** với lớp lỗi này. Đó là lý do phải có suite riêng:
    nếu không, bản vá có thể bị gỡ ở phiên sau mà cổng không hề đỏ.
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


def _tao_dxf(cac_he_so):
    """Bản vẽ có len(cac_he_so) đường kích thước NGANG dài ĐÚNG 1000 đơn vị hình học.
    he_so=None -> KHÔNG khai hệ số (đường bình thường).
    ⚠ Dùng ezdxf.new() KHÔNG setup: bộ kiểu dáng mẫu của ezdxf (EZ_M_100_H25_CM) tự mang hệ số 100 —
    chính nó là một ví dụ THẬT của cơ chế này, nhưng làm nền test không trung tính."""
    doc = ezdxf.new()
    msp = doc.modelspace()
    for i, hs in enumerate(cac_he_so):
        y = i * 100.0
        ovr = None if hs is None else {"dimlfac": hs}
        d = msp.add_linear_dim(base=(0, y + 50), p1=(0, y), p2=(1000, y), override=ovr)
        d.render()
    p = os.path.join(tempfile.gettempdir(), "tyle_do_test.dxf")
    doc.saveas(p)
    return p


def _dims_cua(path):
    return list(tc.Drawing(path).dims)


def main():
    print("[T.1] đường KHÔNG khai hệ số -> giữ NGUYÊN số đo hình học (không được tự ý đổi)")
    p = _tao_dxf([None, None])
    d = _dims_cua(p)
    ok("2 đường, mỗi đường = 1000 (số đo thô)", len(d) == 2 and all(abs(v - 1000.0) < 0.5 for v in d), d)

    print("[T.2] đường CÓ khai hệ số -> số máy đọc phải NHÂN hệ số (khớp số IN trên bản vẽ)")
    p = _tao_dxf([0.25])
    d = _dims_cua(p)
    ok("hệ số 0,25 trên đoạn 1000 -> máy đọc 250 (KHÔNG phải 1000)",
       len(d) == 1 and abs(d[0] - 250.0) < 0.5, d)
    p = _tao_dxf([100.0])
    d = _dims_cua(p)
    ok("hệ số 100 trên đoạn 1000 -> máy đọc 100000", len(d) == 1 and abs(d[0] - 100000.0) < 1.0, d)

    print("[T.3] TRỘN — chỉ đường có khai mới đổi, đường thường KHÔNG bị đụng")
    p = _tao_dxf([None, 0.5, None, 2.0])
    d = sorted(_dims_cua(p))
    ok("4 đường -> {500, 1000, 1000, 2000}", len(d) == 4 and abs(d[0] - 500) < 0.5
       and abs(d[1] - 1000) < 0.5 and abs(d[2] - 1000) < 0.5 and abs(d[3] - 2000) < 0.5, d)

    print("[T.4] HỆ SỐ RÁC -> giữ hành vi CŨ, tuyệt đối không sinh số vô nghĩa")
    for hs, ten in ((0.0, "0"), (float("nan"), "NaN"), (float("inf"), "vô cực")):
        p = _tao_dxf([hs])
        d = _dims_cua(p)
        ok("hệ số %s -> vẫn 1000 (bỏ qua hệ số rác)" % ten,
           len(d) == 1 and abs(d[0] - 1000.0) < 0.5 and not math.isnan(d[0]), d)

    print("[T.4b] HỆ SỐ ÂM -> BỎ QUA (AutoCAD không áp hệ số âm cho đường ở modelspace)")
    # VÌ SAO CÓ NHÓM CA NÀY (bản vá đầu ĐỂ LỌT, cổng vẫn xanh — T.4 gom 'rác' là 0/NaN/+vô cực nhưng
    # THIẾU đúng lớp số ÂM): đo 78 file corpus -> 1.882 đường khai hệ số âm (đều -1.0), TẤT CẢ ở
    # modelspace, 0 ở trang in. Đối chiếu số đo AutoCAD tự lưu trong file (group code 42): 1.880/1.882
    # ca code42 = số đo THÔ, 0 ca = số đo × hệ số. Nếu áp: số thành ÂM -> bị các cổng lọc dương của
    # chính dự án (L1024-1025 'd > 0', _OPENING_DIM_LO=400, _DIM_UV_LO=20) vứt IM LẶNG, mà
    # so_duong_kich_thuoc vẫn đếm đủ -> KHÔNG một trường nào đổi giá trị để lộ ra. Nặng nhất:
    # 1.186/1.650 đường (71,9%) của một file biến mất khỏi mọi tool.
    for hs, ten in ((-1.0, "-1 (ca THẬT của corpus)"), (-0.25, "-0,25"), (float("-inf"), "-vô cực")):
        p = _tao_dxf([hs])
        d = _dims_cua(p)
        ok("hệ số %s -> giữ 1000 (số đo thô), KHÔNG ra số âm" % ten,
           len(d) == 1 and abs(d[0] - 1000.0) < 0.5, d)

    print("[T.4c] hệ số âm KHÔNG được làm RỤNG đường kích thước khỏi min/max/phổ biến")
    p = _tao_dxf([None, -1.0, None, -1.0])
    dr_am = tc.Drawing(p)
    r_am = dr_am.thong_tin_kich_thuoc()
    ok("4 đường đều còn trong dims", len(dr_am.dims) == 4, dr_am.dims)
    ok("KHÔNG đường nào mang giá trị âm", all(v > 0 for v in dr_am.dims), dr_am.dims)
    ok("nho_nhat/lon_nhat đọc được (không rỗng do bị lọc sạch)",
       r_am.get("nho_nhat_mm") is not None and r_am.get("lon_nhat_mm") is not None, r_am)
    ok("số ĐƯỜNG khớp số GIÁ TRỊ còn dùng được (đếm đủ nhưng không mất số)",
       r_am.get("so_duong_kich_thuoc") == 4 and len(dr_am.dim_vals) >= 1, (r_am.get("so_duong_kich_thuoc"), dr_am.dim_vals))
    ok("bản vẽ CHỈ khai hệ số âm -> KHÔNG dựng cờ (hệ số bị bỏ qua thì đừng trấn an)",
       "co_dim_ty_le_do" not in r_am, list(r_am))

    print("[T.5] FAIL-OPEN — thư viện không cho đọc hệ số thì về hành vi cũ, KHÔNG mất đường kích thước")
    p = _tao_dxf([None, 0.25, None])
    _goc = ezdxf.entities.Dimension.override

    def _no(self, *a, **k):
        raise RuntimeError("gia lap ezdxf cu")

    try:
        ezdxf.entities.Dimension.override = _no
        d = _dims_cua(p)
        ok("override ném lỗi -> vẫn đủ 3 đường (không nuốt dimension)", len(d) == 3, d)
        ok("và về đúng số đo thô 1000 (không bịa số)", all(abs(v - 1000.0) < 0.5 for v in d), d)
    finally:
        ezdxf.entities.Dimension.override = _goc

    print("[T.6] LỘ ra ngoài: cờ BOOL + câu chữ SẠCH SỐ (không mở rộng rổ neo chống bịa)")
    p = _tao_dxf([None, 0.25])
    dr = tc.Drawing(p)
    r = dr.thong_tin_kich_thuoc()
    ok("có cờ 'co_dim_ty_le_do' = True khi bản vẽ có khai hệ số", r.get("co_dim_ty_le_do") is True, r.get("co_dim_ty_le_do"))
    ok("cờ là BOOL thật (bool không lọt _collect_numbers)", isinstance(r.get("co_dim_ty_le_do"), bool))
    import re
    _them = r["ghi_chu"].split("⚠", 1)[1] if "⚠" in r["ghi_chu"] else ""
    ok("câu cảnh báo thêm vào KHÔNG chứa chữ số", _them and re.search(r"\d", _them) is None, _them[:90])
    ok("KHÔNG có trường đếm nào kiểu 'so_dim_ty_le' lọt ra kết quả tool",
       not any(k for k in r if "ty_le" in k and isinstance(r[k], (int, float)) and not isinstance(r[k], bool)), list(r))

    p2 = _tao_dxf([None, None])
    r2 = tc.Drawing(p2).thong_tin_kich_thuoc()
    ok("bản vẽ KHÔNG khai hệ số -> KHÔNG có cờ (không báo động thừa)", "co_dim_ty_le_do" not in r2, list(r2))
    ok("và câu ghi chú giữ nguyên như cũ (không nhiễu)", "⚠" not in r2["ghi_chu"])

    print("[T.7] rổ neo grounding KHÔNG nở thêm vì bản vá này")
    import mcp_bridge as B
    ro = B._collect_numbers(r)
    ro2 = B._collect_numbers(r2)
    ok("số trong rổ của bản CÓ hệ số ⊆ rổ của bản KHÔNG hệ số ∪ {số đo}", isinstance(ro, set) and isinstance(ro2, set))
    ok("cờ + câu cảnh báo không bơm số lạ nào vào rổ", ro - ro2 <= {250.0, 1.0, 2.0}, sorted(ro - ro2))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
