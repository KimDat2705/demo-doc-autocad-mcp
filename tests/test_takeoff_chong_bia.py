# -*- coding: utf-8 -*-
"""KHOÁ CHỐNG BỊA cho takeoff (GĐ2) — TẤT ĐỊNH, KHÔNG gọi Gemini, KHÔNG tốn phí.
Chạy:  python tests/test_takeoff_chong_bia.py

Kiểm 2 lớp:
  A. EXISTENCE — cấu kiện thật KHÔNG bị báo nhầm "không tìm thấy"; cấu kiện GIẢ bị bắt đúng (đa-domain).
  B. LỖ HỔNG   — cấp inputs_bo_sung cho mã KHÔNG tồn tại vẫn phải "không tìm thấy" (không tính số ảo);
                 mã thật + số bù -> tính được; mã TRỐNG = nhập tay thuần -> tính được.
(Bàn giao ngược demo 1 2026-07-02: siết existence NGAY CẢ KHI có inputs_bo_sung.)"""
import os, sys, io
os.environ.setdefault("READFILE_MAX_MB", "300")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
from tools_core import Drawing

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
KT = os.path.join(BASE, "BV+DT MN Gia Loc", "1. Kien truc MN Gia Loc.dxf")
KC = os.path.join(BASE, "BV+DT MN Gia Loc", "2. KetCau MN GiaLoc.dxf")
CUA = os.path.join(BASE, "0. Demo - Bang thong ke cua.dxf")

PASS = FAIL = 0


def loai(r):
    if r.get("khong_tim_thay"): return "vang"
    if r.get("sai_loai"): return "sailoai"
    if r.get("co_ket_qua"): return "tinh"
    if r.get("can_bo_sung"): return "thieu"
    return "khac"


def ck(dwg, ten, ma, bs, kyvong, note=""):
    """kyvong: 'vang'|'tinh'|'thieu', hoặc 'ton_tai' = bất cứ gì TRỪ 'vang'."""
    global PASS, FAIL
    lo = loai(dwg.tinh_dai_luong(ten, ma, bs))
    ok = (lo != "vang") if kyvong == "ton_tai" else (lo == kyvong)
    PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] %-24s ma=%-6s bs=%-12s -> %-5s (mong %s) %s"
          % ("OK" if ok else "FAIL", ten, ma or "«trống»", (bs or "-")[:12], lo, kyvong,
             "" if ok else "<<< " + note))


def main():
    global PASS, FAIL
    kt, kc = Drawing(KT), Drawing(KC)
    cua = Drawing(CUA) if os.path.isfile(CUA) else None

    print("[A] EXISTENCE — cấu kiện thật vs giả (đa-domain)")
    for ma in ["D1", "S1", "CM1"]: ck(kt, "diện tích cửa", ma, "", "ton_tai")
    for ma in ["GL9", "D99", "ZZ1"]: ck(kt, "diện tích cửa", ma, "", "vang")
    for ma in ["C1", "C4"]: ck(kc, "thể tích bê tông cột", ma, "", "ton_tai")
    for ma in ["C999", "GL9"]: ck(kc, "thể tích bê tông cột", ma, "", "vang")
    if cua:
        ck(cua, "diện tích cửa", "D1", "", "tinh", "fixture có bảng R×C -> confident, tính được")
        ck(cua, "diện tích cửa", "XY7", "", "vang")

    print("[B] LỖ HỔNG — inputs_bo_sung KHÔNG được cứu mã không tồn tại")
    ck(kc, "thể tích bê tông sàn", "SAN1", '{"dien_tich":50,"chieu_day":100}', "vang", "SAN1 vắng + số bù")
    ck(kt, "diện tích cửa", "GL9", '{"rong":800}', "vang", "GL9 vắng + số bù")
    ck(kc, "thể tích bê tông cột", "C1", '{"chieu_cao":3600}', "tinh", "C1 thật + số bù")
    ck(kc, "thể tích bê tông sàn", "", '{"dien_tich":50,"chieu_day":100}', "tinh", "mã trống = nhập tay")
    ck(kc, "thể tích bê tông cột", "C1", "", "thieu", "C1 thật, chưa cấp cao")

    print("[C] SAI LOẠI — mã có thật nhưng bản vẽ ghi là loại KHÁC")
    ck(kc, "thể tích bê tông móng", "DM-1", '{"chieu_cao":1000}', "sailoai", "DM-1 là DẦM, hỏi MÓNG")
    ck(kc, "thể tích bê tông móng", "DM-1", "", "sailoai", "DM-1 là DẦM, hỏi MÓNG (không số bù)")
    ck(kc, "thể tích bê tông dầm", "DM-1", "", "ton_tai", "DM-1 hỏi ĐÚNG loại DẦM -> KHÔNG chặn")

    print("[D] SMOKE — tính năng parity (tầng / tổng hợp / xuất Excel)")
    tang = kc.thong_tin_tang()
    ok = tang.get("co_cao_do") and tang.get("chieu_cao_tang_dien_hinh_m")
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] thong_tin_tang KC: cao_do=%s tầng=%sm" % ("OK" if ok else "FAIL",
          tang.get("co_cao_do"), tang.get("chieu_cao_tang_dien_hinh_m")))
    th = kc.tong_hop_khoi_luong()
    ok = th.get("co_du_lieu") and th.get("so_hang", 0) > 10
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] tong_hop_khoi_luong KC: %d hàng, %d cần bổ sung, %d giả định"
          % ("OK" if ok else "FAIL", th.get("so_hang", 0), len(th.get("can_bo_sung", [])), len(th.get("gia_dinh", []))))
    xl = kc.xuat_excel()
    import os as _os
    from tools_core import RENDER_DIR as _RD
    ok = bool(xl.get("file_id")) and _os.path.isfile(_os.path.join(_RD, xl.get("file_id", "x")))
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] xuat_excel KC: file_id=%s" % ("OK" if ok else "FAIL", xl.get("file_id")))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
