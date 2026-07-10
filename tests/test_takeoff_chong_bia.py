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

    print("[E] GÁN-DIM ỔN ĐỊNH (TODO #3) — biến thể chuỗi mã CÙNG cho 1 kết quả")
    variants = ["D1", "cửa D1", "cửa đi D1", "cua di d1"]
    kq = [kt.tinh_dai_luong("diện tích cửa", v, "") for v in variants]
    vals = {round(r["ket_qua"], 2) for r in kq if r.get("co_ket_qua")}
    stable = len(vals) == 1 and all(r.get("co_ket_qua") for r in kq)
    PASS, FAIL = PASS + int(stable), FAIL + int(not stable)
    print("  [%s] diện tích cửa D1 (4 biến thể) -> %s m² (mong 1 giá trị duy nhất)"
          % ("OK" if stable else "FAIL", sorted(vals)))

    print("[F] ĐẠI LƯỢNG MỚI (xây/trát/đào-đắp) + BÓC TÁCH")
    ck(kc, "khối lượng xây tường", "", '{"chieu_dai":5000,"chieu_cao":3000,"be_day":220}', "tinh", "xây đủ số")
    ck(kc, "diện tích trát", "", '{"chieu_dai":5000,"chieu_cao":3000,"so_mat":2}', "tinh", "trát đủ số")
    ck(kc, "khối lượng đào đất", "", '{"chieu_dai":10000,"chieu_rong":8000,"chieu_sau":2000}', "tinh", "đào đủ số")
    ck(kc, "khối lượng đào đất", "", "", "thieu", "đào chưa có số -> hỏi (không bịa)")
    ck(kc, "khối lượng đắp đất", "", '{"chieu_dai":10000,"chieu_rong":8000,"chieu_cao":500}', "tinh", "đắp đủ số")
    bt = kt.boc_tach_kich_thuoc("granit")
    ok = bt.get("so_ket_qua", 0) > 0 and any("dien_tich_m2" in e["da_tach"] for e in bt["ket_qua"])
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] bóc tách 'granit' KT: %d ghi chú, có diện tích m²" % ("OK" if ok else "FAIL", bt.get("so_ket_qua", 0)))

    print("[G] SAU KIỂM CHỨNG ĐỐI KHÁNG — vá lỗ hổng (chống bịa bề dày + đơn vị bóc tách)")
    # Fix A: xây tường thiếu bề dày -> HỎI (không quét file lấy 'dày' bừa)
    ck(kc, "khối lượng xây tường", "", '{"chieu_dai":5000,"chieu_cao":3000}', "thieu", "thiếu bề dày -> hỏi, KHÔNG bịa")
    ck(kc, "thể tích bê tông sàn", "", '{"dien_tich":50}', "thieu", "sàn thiếu bề dày -> hỏi, KHÔNG bịa")
    # Fix B: kích thước VẬT LIỆU nhỏ (mọi cạnh < 1000mm) KHÔNG được gắn nhầm đơn vị 'm'
    mm_ok = all(not (d["don_vi"] == "m" and all((x or 0) < 1000 for x in (d["a"], d["b"], d["c"])))
                for e in kt.boc_tach_kich_thuoc("gạch").get("ket_qua", [])
                for d in e["da_tach"].get("kich_thuoc_3d", []))
    PASS, FAIL = PASS + int(mm_ok), FAIL + int(not mm_ok)
    print("  [%s] bóc tách 'gạch': không kích thước vật liệu nhỏ nào bị gắn nhầm đơn vị 'm'" % ("OK" if mm_ok else "FAIL"))

    print("[H] SAU AUDIT — vá 5 bug (crash phi số / số âm / do_tin_cay / thép float / gioi_han âm)")
    r1 = kc.tinh_dai_luong("khối lượng đào đất", "", '{"chieu_dai":"abc","chieu_rong":2000,"chieu_sau":1500}')
    r2 = kc.tinh_dai_luong("thể tích bê tông cột", "C1", '{"chieu_cao":-3600}')
    for tag, r in [("phi số", r1), ("số âm", r2)]:
        ok = not r.get("co_ket_qua")
        PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
        print("  [%s] input %s -> KHÔNG ra kết quả (co_ket_qua=%s)" % ("OK" if ok else "FAIL", tag, r.get("co_ket_qua")))
    tc = (kt._gan_dim_cau_kien("D2").get("cao") or {}).get("do_tin_cay")
    ok = tc != "cao"; PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] gán-dim do_tin_cay='%s' (chưa-chắc KHÔNG gắn 'cao')" % ("OK" if ok else "FAIL", tc))
    ok = kc.thong_ke_thep(duong_kinh=16.0).get("co_trong_bang") is True
    PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] thong_ke_thep(16.0 float) tìm được Ø16" % ("OK" if ok else "FAIL"))
    ok = kt.tim_kiem(tu_khoa="dam", gioi_han=-5).get("hien_thi") == 0
    PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] gioi_han âm -> 0 (không cắt cụt bằng slice âm)" % ("OK" if ok else "FAIL"))

    print("[I] ĐƠN VỊ cm/mm + ĐỌC BẢNG CỘT 9T (parity demo 1: data-driven + ngưỡng 130 + ghép tọa độ)")
    import tools_core as _TC
    # I.1 SUY ĐOÁN đơn vị TẤT ĐỊNH (thuần, không cần file): cm nếu max<130, else mm; đơn vị GHI RÕ -> tin.
    for (a, b, st), exp in [((80, 80, ""), "cm"), ((220, 220, ""), "mm"), ((140, 140, ""), "mm"),
                            ((50, 110, ""), "cm"), ((160, 160, "cm"), "cm"), ((300, 600, ""), "mm")]:
        u = _TC._sect_to_mm(a, b, st)[2]; ok = (u == exp)
        PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
        print("  [%s] _sect_to_mm(%d,%d,%r) đơn vị=%s (mong %s)" % ("OK" if ok else "FAIL", a, b, st, u, exp))
    # I.2 Nhà 9T (quy ước cm): trước đây MÙ (báo thiếu). Nay đọc được cột + tính ĐÚNG (không lệch 100×).
    P9 = os.path.join(BASE, "BV+DT nha 9 tang", "2. Ket Cau_NHA 9T.dxf")
    if os.path.isfile(P9):
        n9 = Drawing(P9)
        ccm = [e for e in n9.section_index if e["code"].startswith("c-") and e["don_vi"] == "cm"]
        ok = len(ccm) >= 3; PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
        print("  [%s] 9T: đọc %d cột đơn vị CM (mong ≥3; trước fix = 0, mù hoàn toàn)" % ("OK" if ok else "FAIL", len(ccm)))
        c3 = next((e for e in n9.section_index if e["code"] == "c-3"), None)
        ok = bool(c3) and c3["a"] == 800 and c3["b"] == 800 and c3["don_vi"] == "cm"
        PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
        print("  [%s] 9T C-3 = 80×80 cm -> 800×800 mm-tương-đương (không đọc thành 80mm)" % ("OK" if ok else "FAIL"))
        r = n9.tinh_dai_luong("thể tích bê tông cột", "C-3", '{"chieu_cao":3600}')
        okv = r.get("co_ket_qua") and abs(r["ket_qua"] - 23.04) < 0.01   # KHỚP demo 1 (cross-consistency)
        PASS, FAIL = PASS + int(bool(okv)), FAIL + int(not okv)
        print("  [%s] 9T C-3 thể tích (cao 3.6m) = %s m³ (mong 23.04 = KHỚP demo 1, KHÔNG 0.023 lệch 100×)"
              % ("OK" if okv else "FAIL", r.get("ket_qua")))
        okf = r.get("co_ket_qua") and "SUY ĐOÁN" in r.get("ghi_chu", "")
        PASS, FAIL = PASS + int(bool(okf)), FAIL + int(not okf)
        print("  [%s] 9T C-3: có CẢNH BÁO đơn vị suy đoán cm/mm (chống bịa: chưa chắc phải lộ)" % ("OK" if okf else "FAIL"))
    else:
        print("  [..] BỎ QUA I.2 — không thấy file 9T (%s)" % P9)
    # I.3 Gia Lộc (quy ước mm): KHÔNG regression — vẫn đọc mm, KHÔNG cảnh báo nhiễu, thể tích C1 giữ nguyên.
    c1 = kc._doc_tiet_dien("C1")
    ok = c1 and c1["a"] == 220 and c1["don_vi"] == "mm" and not c1.get("suy_doan_don_vi")
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] Gia Lộc C1 = 220×220 mm, KHÔNG cảnh báo suy đoán (file mm sạch)" % ("OK" if ok else "FAIL"))
    r = kc.tinh_dai_luong("thể tích bê tông cột", "C1", '{"chieu_cao":3600}')
    ok = r.get("co_ket_qua") and abs(r["ket_qua"] - 4.704) < 0.01
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] Gia Lộc C1 thể tích = %s m³ (mong 4.704 — không đổi sau fix)" % ("OK" if ok else "FAIL", r.get("ket_qua")))

    print("[J] KHỐI LƯỢNG INOX/THÉP HÌNH = SL(đọc) × kg/bộ(đối tác cấp) — vá theo feedback đối tác")
    import tools_core as _TCj
    # J.1 ĐỊNH TUYẾN tên: 'kg inox cửa S1' phải ra công thức inox (KHÔNG nhầm 'diện tích cửa' dù có chữ 'cửa')
    for q, exp in [("khối lượng inox", "khoi_luong_thep_hinh"), ("tổng số kg inox trên cửa S1", "khoi_luong_thep_hinh"),
                   ("khối lượng thép hình", "khoi_luong_thep_hinh"), ("diện tích cửa S1", "dien_tich_cua")]:
        got = _TCj._chuan_hoa_ten_dai_luong(q); ok = (got == exp)
        PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
        print("  [%s] map %r -> %s (mong %s)" % ("OK" if ok else "FAIL", q[:26], got, exp))
    # J.2 KT Gia Lộc: S1 = 16 bộ (ĐỌC) × 8.62 kg/bộ (đối tác cấp) = 137.92 kg — đúng câu hỏi đối tác
    r = kt.tinh_dai_luong("khối lượng inox", "S1", '{"kg_moi_bo":8.62}')
    ok = r.get("co_ket_qua") and abs(r["ket_qua"] - 137.92) < 0.01
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] inox S1 = 16×8.62 = %s kg (mong 137.92)" % ("OK" if ok else "FAIL", r.get("ket_qua")))
    ok = r.get("co_ket_qua") and any(x["ten"] == "so_luong" and x["nguon"] == "doc_verbatim" for x in r.get("inputs_da_co", []))
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] số bộ (16) ĐỌC tự động từ bản vẽ, kg/bộ do đối tác cấp" % ("OK" if ok else "FAIL"))
    # J.3–J.5 CHỐNG BỊA: thiếu kg/bộ -> hỏi (KHÔNG bịa từ ghi chú); mã giả -> không tìm thấy; kg âm -> không hợp lệ
    ck(kt, "khối lượng inox", "S1", "", "thieu", "thiếu kg/bộ -> HỎI, không tự lấy '8.62' từ ghi chú (chống bịa liên kết)")
    ck(kt, "khối lượng inox", "ZZ9", '{"kg_moi_bo":8.62}', "vang", "mã inox giả + số bù -> vẫn không tìm thấy")
    r = kt.tinh_dai_luong("khối lượng inox", "S1", '{"kg_moi_bo":-5}')
    ok = not r.get("co_ket_qua")
    PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] inox kg/bộ ÂM -> KHÔNG ra kết quả (không bịa số âm)" % ("OK" if ok else "FAIL"))

    print("[K] HARDENING chống bịa (kiểm chứng ĐỐI KHÁNG workflow) — inf / tràn số / bool KHÔNG được lọt")
    for tag, bs in [("kg/bộ = inf (1e400)", '{"kg_moi_bo":1e400}'), ("tràn số hữu hạn 1e308", '{"kg_moi_bo":1e308}'),
                    ("kg/bộ = true (bool phi số)", '{"kg_moi_bo":true}'),
                    ("so_luong ghi đè = 'inf'", '{"so_luong":"inf","kg_moi_bo":8.62}'), ("kg/bộ = 'nan'", '{"kg_moi_bo":"nan"}')]:
        r = kt.tinh_dai_luong("khối lượng inox", "S1", bs)
        ok = (not r.get("co_ket_qua")) and r.get("ket_qua") is None
        PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
        print("  [%s] %-30s -> CHẶN (co_ket_qua=%s, ket_qua=%r)" % ("OK" if ok else "FAIL", tag, r.get("co_ket_qua"), r.get("ket_qua")))
    r = kt.tinh_dai_luong("khối lượng inox", "S1", '{"kg_moi_bo":8.62}')   # hardening KHÔNG chặn nhầm số hợp lệ
    ok = r.get("co_ket_qua") and abs(r["ket_qua"] - 137.92) < 0.01
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] số HỢP LỆ 8.62 vẫn tính đúng 137.92 sau hardening" % ("OK" if ok else "FAIL"))

    print("[L] CHỐNG BỊA (roadmap đối kháng) — mã toàn chữ giả / sàn tự-vơ diện tích / lệch đại lượng")
    # L.1 mã TOÀN CHỮ giả -> không tìm thấy cho MỌI công thức (không chỉ inox); mã THẬT không bị chặn nhầm
    ck(kt, "khối lượng inox", "GHOSTINOX", '{"so_luong":10,"kg_moi_bo":8.62}', "vang", "mã toàn chữ giả -> vang (không bịa kg)")
    ck(kc, "thể tích bê tông cột", "INOXGHOST", '{"canh_a":220,"canh_b":220,"chieu_cao":3600,"so_luong":1}', "vang", "mã toàn chữ giả -> vang (không bịa m³)")
    ck(kt, "khối lượng inox", "S1", '{"kg_moi_bo":8.62}', "tinh", "mã THẬT S1 KHÔNG bị chặn nhầm")
    # L.2 'thể tích bê tông sàn' mã TRỐNG KHÔNG tự quét cả file vơ 'diện tích Xm2' bất kỳ
    ck(kc, "thể tích bê tông sàn", "", '{"chieu_day":150}', "thieu", "sàn mã trống -> THIẾU (không tự vơ diện tích sàn)")
    ck(kc, "thể tích bê tông sàn", "", '{"dien_tich":50,"chieu_day":100}', "tinh", "sàn NHẬP TAY đủ số -> vẫn tính")
    # L.3 'thể tích inox' tính kg NHƯNG phải LỘ cảnh báo lệch đại lượng (m³ vs kg)
    r = kt.tinh_dai_luong("thể tích inox", "S1", '{"kg_moi_bo":8.62}')
    ok = r.get("co_ket_qua") and "⚠" in r.get("ghi_chu", "") and "KHỐI LƯỢNG" in r.get("ghi_chu", "")
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] 'thể tích inox' -> tính kg + CẢNH BÁO lệch đại lượng (chưa chắc phải lộ)" % ("OK" if ok else "FAIL"))

    print("[M] CỦNG CỐ — TỔNG PHỤ (A) + GỢI Ý m³ ghi sẵn (E)")
    th = kc.tong_hop_khoi_luong()
    tp = th.get("tong_phu", [])
    ok = isinstance(tp, list) and len(tp) > 0 and all(("tong" in x and "don_vi" in x) for x in tp)
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] A: tong_hop có 'tong_phu' (%d nhóm tổng theo loại+đơn vị)" % ("OK" if ok else "FAIL", len(tp)))
    m3 = [x for x in tp if x["don_vi"] == "m³"]
    ok = len(m3) >= 2   # Thể tích BT (16.93) và Khối lượng ghi sẵn/đào móng (860) phải là 2 dòng RIÊNG, không gộp
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] A: tổng m³ KHÔNG gộp nhầm khác loại (%d dòng m³ riêng)" % ("OK" if ok else "FAIL", len(m3)))
    ok = all(x["loai"] != "Cao độ/tầng" for x in tp)   # loại trị vô nghĩa khỏi tổng
    PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] A: KHÔNG cộng 'Cao độ/tầng' (trị không phải để tổng)" % ("OK" if ok else "FAIL"))
    r = kc.tinh_dai_luong("khối lượng đào đất", "", "")
    gy = r.get("goi_y_ghi_san") or []
    ok = r.get("can_bo_sung") and any(abs(g["gia_tri"] - 860.0) < 0.01 for g in gy) and "860" in r.get("ghi_chu", "")
    PASS, FAIL = PASS + int(bool(ok)), FAIL + int(not ok)
    print("  [%s] E: đào đất thiếu số -> gợi ý '860 m³ ghi sẵn' (dùng data đã đọc, có handle)" % ("OK" if ok else "FAIL"))
    ok = not (kc.tinh_dai_luong("diện tích trát", "", "").get("goi_y_ghi_san"))
    PASS, FAIL = PASS + int(ok), FAIL + int(not ok)
    print("  [%s] E: trát (không m³ liên quan) -> KHÔNG gợi ý nhiễu" % ("OK" if ok else "FAIL"))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
