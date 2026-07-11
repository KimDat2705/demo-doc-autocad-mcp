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
    ck(kc, "thể tích bê tông cột", "C1", "", "tinh", "C1 thật, chưa cấp cao -> NAY ước 1 tầng (task F), tính được (cờ giả định)")

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

    print("[N] TRỪ LỖ CỬA/CỬA SỔ khi xây tường & trát (task B) — số do CODE, chống bịa")
    def _emit(name, cond, extra=""):
        global PASS, FAIL
        okk = bool(cond); PASS += int(okk); FAIL += int(not okk)
        print("  [%s] %s%s" % ("OK" if okk else "FAIL", name, (" " + extra) if extra else ""))
    def _xay(dr, bs): return dr.tinh_dai_luong("khối lượng xây tường", "", bs)
    def _trat(dr, bs): return dr.tinh_dai_luong("diện tích trát", "", bs)
    # N.0 BACKWARD-COMPAT: không lo_cua / lo_cua rỗng -> số CŨ y hệt + KHÔNG thêm field mới
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200}')
    _emit("BC xây không lo_cua = 3.0 + KHÔNG field mới",
          r.get("co_ket_qua") and abs(r["ket_qua"] - 3.0) < 1e-9 and not any(k in r for k in ("gross", "khau_tru_lo", "chi_tiet_lo", "so_lo")),
          "-> %s" % r.get("ket_qua"))
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[]}')
    _emit("BC lo_cua=[] = 3.0 + KHÔNG field mới", r.get("co_ket_qua") and abs(r["ket_qua"] - 3.0) < 1e-9 and "khau_tru_lo" not in r)
    # N.1 TRỪ theo KÍCH THƯỚC TRỰC TIẾP (đối tác cấp; không cần bảng cửa)
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"rong":900,"cao":2200,"sl":1}]}')
    _emit("xây − trực tiếp 900×2200 = 2.604 (gross 3.0, khấu trừ 0.396)",
          r.get("co_ket_qua") and abs(r["ket_qua"] - 2.604) < 1e-6 and abs(r.get("gross", 0) - 3.0) < 1e-9 and abs(r.get("khau_tru_lo", 0) - 0.396) < 1e-6,
          "-> %s" % r.get("ket_qua"))
    r = _trat(kc, '{"chieu_dai":5000,"chieu_cao":3000,"so_mat":2,"lo_cua":[{"rong":900,"cao":2200,"sl":1}]}')
    _emit("trát − trực tiếp (so_mat=2) = 26.04", r.get("co_ket_qua") and abs(r["ket_qua"] - 26.04) < 1e-6, "-> %s" % r.get("ket_qua"))
    r = _trat(kc, '{"chieu_dai":5000,"chieu_cao":3000,"so_mat":1,"lo_cua":[{"rong":900,"cao":2200,"sl":1}]}')
    _emit("trát so_mat=1 cùng lỗ = 13.02 (trừ theo SỐ MẶT)", r.get("co_ket_qua") and abs(r["ket_qua"] - 13.02) < 1e-6, "-> %s" % r.get("ket_qua"))
    # N.2 TRỪ theo MÃ từ BẢNG THỐNG KÊ confident (fixture cua) + parity mã==trực tiếp
    if cua:
        r = _xay(cua, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"ma":"d2","sl":1}]}')
        c0 = (r.get("chi_tiet_lo") or [{}])[0]
        _emit("xây − mã D2 (bảng) = 2.604 + confident + handle + nguồn bảng",
              r.get("co_ket_qua") and abs(r["ket_qua"] - 2.604) < 1e-6 and c0.get("confident") and c0.get("handle") and c0.get("nguon") == "bang_thong_ke",
              "-> %s" % r.get("ket_qua"))
        r2 = _trat(cua, '{"chieu_dai":5000,"chieu_cao":3000,"so_mat":2,"lo_cua":[{"ma":"d2","so_luong":1}]}')
        _emit("trát − mã D2 (nhận 'so_luong') = 26.04", r2.get("co_ket_qua") and abs(r2["ket_qua"] - 26.04) < 1e-6, "-> %s" % r2.get("ket_qua"))
        rd = _xay(cua, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"rong":900,"cao":2200,"sl":1}]}')
        _emit("PARITY: mã D2 == kích thước trực tiếp 900×2200", r.get("co_ket_qua") and rd.get("co_ket_qua") and abs(r["ket_qua"] - rd["ket_qua"]) < 1e-9)
        r = _xay(cua, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"ma":"d99","sl":1}]}')
        _emit("mã lỗ GIẢ D99 -> khong_tim_thay, KHÔNG ket_qua", (not r.get("co_ket_qua")) and r.get("khong_tim_thay") and r.get("ket_qua") is None)
        r = _xay(cua, '{"chieu_dai":30000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"ma":"d2","sl":19}]}')
        _emit("over-count D2 sl=19 > 18 bản vẽ -> lo_vuot_so_luong", (not r.get("co_ket_qua")) and r.get("lo_vuot_so_luong"))
    else:
        print("  [..] BỎ QUA N.2 — không thấy fixture bảng cửa (%s)" % CUA)
    # N.3 CHỐNG BỊA — các ca phải BLOCK (kích thước trực tiếp trên kc, không cần bảng)
    r = _xay(kc, '{"chieu_dai":1000,"chieu_cao":2000,"be_day":100,"lo_cua":[{"rong":1300,"cao":2700,"sl":1}]}')
    _emit("lỗ ≥ tường -> lo_lon_hon_tuong, KHÔNG số âm", (not r.get("co_ket_qua")) and r.get("lo_lon_hon_tuong") and r.get("ket_qua") is None)
    for slbad in ["0", "-1", "1.5", "true"]:
        r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"rong":900,"cao":2200,"sl":%s}]}' % slbad)
        _emit("sl=%s -> block (so_lieu_khong_hop_le)" % slbad, (not r.get("co_ket_qua")) and r.get("so_lieu_khong_hop_le"))
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"rong":90,"cao":210,"sl":1}]}')
    _emit("lẫn ĐƠN VỊ 90×210 (cm) -> lo_don_vi_kha_nghi (không trừ)", (not r.get("co_ket_qua")) and r.get("lo_don_vi_kha_nghi"))
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"rong":900,"cao":2200}]}')
    _emit("thiếu sl -> block (KHÔNG mặc định 1)", (not r.get("co_ket_qua")) and r.get("so_lieu_khong_hop_le"))
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"ma":"d2","rong":900,"cao":2200,"sl":1}]}')
    _emit("khai CẢ mã LẪN kích thước -> lo_cua_khong_hop_le", (not r.get("co_ket_qua")) and r.get("lo_cua_khong_hop_le"))
    r = _xay(kc, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":"abc"}')
    _emit("lo_cua sai kiểu (chuỗi) -> lo_cua_khong_hop_le", (not r.get("co_ket_qua")) and r.get("lo_cua_khong_hop_le"))
    r = kc.tinh_dai_luong("khối lượng đào đất", "", '{"chieu_dai":10000,"chieu_rong":8000,"chieu_sau":2000,"lo_cua":[{"rong":900,"cao":2200,"sl":1}]}')
    _emit("lo_cua cho ĐÀO ĐẤT -> khong_ho_tro_tru_lo (LỘ, không âm thầm)", (not r.get("co_ket_qua")) and r.get("khong_ho_tro_tru_lo"))
    # N.4 HARDENING sau KIỂM CHỨNG ĐỐI KHÁNG (workflow đa-agent) — vá 4 lỗ hổng panel bắt được
    if cua:
        # (1) over-count LÁCH bằng tách 1 mã thành nhiều entry -> cộng dồn theo mã rồi mới so trần
        r = _xay(cua, '{"chieu_dai":100000,"chieu_cao":100000,"be_day":200,"lo_cua":[{"ma":"d2","sl":18},{"ma":"d2","sl":18}]}')
        _emit("over-count TÁCH mã d2 18+18=36 > 18 -> lo_vuot_so_luong (không trừ khống)", (not r.get("co_ket_qua")) and r.get("lo_vuot_so_luong"))
        r = _xay(cua, '{"chieu_dai":50000,"chieu_cao":5000,"be_day":200,"lo_cua":[{"ma":"d2","sl":9},{"ma":"d2","sl":9}]}')
        _emit("split HỢP LỆ d2 9+9=18 (=trần, tường lớn) -> tính, so_lo=18", r.get("co_ket_qua") and r.get("so_lo") == 18, "-> %s" % r.get("ket_qua"))
        # (3) sl vs so_luong mâu thuẫn -> block; trùng khớp -> tính
        r = _xay(cua, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"ma":"d1","sl":1,"so_luong":999}]}')
        _emit("sl≠so_luong (1 vs 999) mâu thuẫn -> lo_cua_khong_hop_le", (not r.get("co_ket_qua")) and r.get("lo_cua_khong_hop_le"))
        r = _xay(cua, '{"chieu_dai":5000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"ma":"d2","sl":2,"so_luong":2}]}')
        _emit("sl==so_luong (2==2) KHÔNG mâu thuẫn -> tính", r.get("co_ket_qua") and r.get("so_lo") == 2)
    # (2) net làm tròn về 0.0 (lỗ ≈ tường) -> BLOCK, TUYỆT ĐỐI không trả 0.0 như kết quả hợp lệ
    r = _xay(kc, '{"chieu_dai":2000,"chieu_cao":2000,"be_day":100,"lo_cua":[{"rong":1999,"cao":2000,"sl":1}]}')
    _emit("net≈0 (xây) làm tròn 0.0 -> lo_lon_hon_tuong, KHÔNG 0.0", (not r.get("co_ket_qua")) and r.get("lo_lon_hon_tuong") and r.get("ket_qua") is None)
    r = _trat(kc, '{"chieu_dai":3000,"chieu_cao":2000,"so_mat":1,"lo_cua":[{"rong":2999,"cao":2000,"sl":1}]}')
    _emit("net≈0 (trát) làm tròn 0.0 -> lo_lon_hon_tuong, KHÔNG 0.0", (not r.get("co_ket_qua")) and r.get("lo_lon_hon_tuong") and r.get("ket_qua") is None)
    # (4) sl khổng lồ dim-mode -> block sạch, so_lo KHÔNG là int rác 300 chữ số
    r = _xay(kc, '{"chieu_dai":20000,"chieu_cao":3000,"be_day":200,"lo_cua":[{"rong":9000,"cao":9000,"sl":1e300}]}')
    _emit("sl=1e300 -> block sạch, so_lo không phải int khổng lồ", (not r.get("co_ket_qua")) and len(str(r.get("so_lo"))) < 12)

    print("[O] LIỆT KÊ DIỆN TÍCH GHI SẴN (task C) — nhãn m² verbatim, không phân loại/không suy hình học")
    import tools_core as _TCo
    def _sa(txt):  # unit test builder tất định (không phụ thuộc file)
        return [e["m2"] for e in _TCo._build_stated_areas([{"vn": txt, "handle": "H", "layer": "L"}])]
    def _sae(txt):
        return _TCo._build_stated_areas([{"vn": txt, "handle": "H", "layer": "L"}])
    # O.1 UNIT — lọc nhiễu + đa-trị + thập phân + cờ keyword (data-independent)
    _emit("unit: '…250m2; …180m2' -> BẮT CẢ 250 & 180 (đa diện tích ngăn bởi ';')", sorted(_sa("dien tich 250m2; tang 2: 180m2")) == [180.0, 250.0])
    _emit("unit: '16 cọc//1m2' MẬT ĐỘ -> RỖNG (lookbehind '/')", _sa("16 coc//1m2") == [])
    _emit("unit: density CÓ KHOẢNG TRẮNG sau '/' ('16 cọc/ 1m2', '/  1m2') -> RỖNG (gộp '/ '->'/')", _sa("16 coc/ 1m2") == [] and _sa("16 coc/  1m2") == [])
    _emit("unit: đuôi thập phân KHÔNG bịa — '.../44,5m2' KHÔNG ra 4.5/8.1 (lookbehind [/.,digit])", _sa("x 100m2/44,5m2/38.1m2") == [100.0])
    _emit("unit: 'sơn 117m2/44,5m2/38.1m2' -> chỉ 117 (sub-area sau '/' còn trong verbatim)", _sa("son - dien tich 117m2/44,5m2/38.1m2") == [117.0])
    _emit("unit: mã 'DM2' & 'dm2(22x50)' -> RỖNG (không chữ số liền trước m2)", _sa("mc dam mong DM2") == [] and _sa("dm2(22x50)") == [])
    _emit("unit: '(m2)' đơn vị trần -> RỖNG", _sa("(m2)") == [])
    _emit("unit: thập phân dấu phẩy '77,5m2' -> 77.5", _sa("tuong xay - dien tich 77,5m2") == [77.5])
    _emit("unit: '634m2' 0-space + co_tu_khoa=True", _sae("mai ton dien tich 634m2")[0]["m2"] == 634.0 and _sae("mai ton dien tich 634m2")[0]["co_tu_khoa_dien_tich"])
    _emit("unit: nhãn không keyword 'dày 12mm: 3,3m2' -> liệt kê, co_tu_khoa=False", _sae("compact hpl day 12mm: 3,3m2")[0]["co_tu_khoa_dien_tich"] is False)
    # O.2 FILE THẬT — KT (nhiều nhãn), KC (lọc density)
    r = kt.liet_ke_dien_tich_ghi_san()
    _emit("KT: co_du_lieu + so_nhan>=15", r.get("co_du_lieu") and r.get("so_nhan", 0) >= 15, "-> %d nhãn, %d có keyword" % (r.get("so_nhan", 0), r.get("so_co_tu_khoa", 0)))
    _emit("KT: có mái 634 m² (co_tu_khoa=True) + mọi mục có handle", any(e["m2"] == 634 and e["co_tu_khoa_dien_tich"] for e in r["danh_sach"]) and all(e.get("handle") for e in r["danh_sach"]))
    _emit("KT: KHÔNG field tổng (không cộng gộp khác bản chất)", all(k not in r for k in ("tong", "tong_dien_tich", "tong_m2")))
    _emit("KT: sort — item đầu co_tu_khoa=True + m² lớn nhất (tất định)", r["danh_sach"][0]["co_tu_khoa_dien_tich"] and r["danh_sach"][0]["m2"] == max(e["m2"] for e in r["danh_sach"]))
    r = kc.liet_ke_dien_tich_ghi_san()
    _emit("KC: đọc 7.04 (KHÔNG lấy 16 mật độ, KHÔNG lấy 1 density)", any(abs(e["m2"] - 7.04) < 1e-6 for e in r["danh_sach"]) and not any(e["m2"] in (1.0, 16.0) for e in r["danh_sach"]))
    # O.3 tong_hop: loại riêng, KHÔNG cộng gộp
    th = kt.tong_hop_khoi_luong()
    _emit("tong_hop: có dòng loại 'Diện tích (ghi sẵn)' nhưng KHÔNG vào tong_phu",
          any(row["loai"] == "Diện tích (ghi sẵn)" for row in th["bang"]) and not any(x["loai"] == "Diện tích (ghi sẵn)" for x in th["tong_phu"]))
    # O.4 EMPTY (9T): 0 nhãn -> LỘ + gợi ý CẤP, không bịa
    P9O = os.path.join(BASE, "BV+DT nha 9 tang", "2. Ket Cau_NHA 9T.dxf")
    if os.path.isfile(P9O):
        r = Drawing(P9O).liet_ke_dien_tich_ghi_san()
        _emit("9T (0 nhãn) -> co_du_lieu=False + goi_y mời đối tác CẤP (không bịa/suy hình học)",
              (not r.get("co_du_lieu")) and r.get("so_nhan") == 0 and "CẤP" in r.get("goi_y", ""))
    else:
        print("  [..] BỎ QUA O.4 — không thấy file 9T")

    print("[P] ỨNG VIÊN gợi ý cho input thiếu (task D) — 1-click xác nhận, hệ KHÔNG tự cắm")
    import tools_core as _TCp
    _pu = lambda s: bool(_TCp._KG_PU_RE.search(s))
    # P.1 UNIT — per-unit detector bền garble (data-independent)
    _emit("per-unit: '(1 be):…= 8.62 kg' -> True", _pu("khung inox (1 be):13.42m= 8.62 kg"))
    _emit("per-unit: 'kg/bộ' -> True", _pu("8.62 kg/bo"))
    _emit("per-unit: '02 bộ bản lề' bare (phụ kiện) -> False (KHÔNG nhầm)", not _pu("ban le 02 bo, chot 01 bo"))
    _emit("per-unit: '( tính trên 1 cầu thang)' -> False ('1' không sát '(')", not _pu("( tinh tren 1 cau thang) 80,52 kg"))
    # P.2 kg_moi_bo trên KT inox S1 (ground truth 8.62)
    r = kt.tinh_dai_luong("khối lượng inox", "S1", "")
    thk = next((t for t in r.get("inputs_thieu", []) if t["ten"] == "kg_moi_bo"), None)
    uv = (thk or {}).get("ung_vien", [])
    _emit("KT inox S1: ung_vien 8.62 (trung_binh) ĐỨNG ĐẦU", bool(uv) and abs(uv[0]["gia_tri"] - 8.62) < 1e-6 and uv[0]["do_tin_cay"] == "trung_binh", "-> %s" % [(e["gia_tri"], e["do_tin_cay"]) for e in uv])
    _emit("ung_vien: verbatim + handle + la_goi_y + khoang_cach=None (verbatim, không proximity)",
          bool(uv) and uv[0].get("nguyen_van") and uv[0].get("handle") and uv[0].get("la_goi_y") and uv[0]["khoang_cach"] is None)
    _emit("ung_vien KHÔNG chứa 'TỔNG KHỐI LƯỢNG' (loại tổng)", not any("tong" in e["nguyen_van"].lower() for e in uv))
    _emit("KHÔNG tự cắm: 8.62 vắng inputs_da_co + co_ket_qua=False", (not r.get("co_ket_qua")) and not any(x["ten"] == "kg_moi_bo" for x in r.get("inputs_da_co", [])))
    _emit("ghi_chu: nêu 'ỨNG VIÊN' + 'KHÔNG tự cắm'", "ỨNG VIÊN" in r.get("ghi_chu", "") and "KHÔNG tự cắm" in r.get("ghi_chu", ""))
    r2 = kt.tinh_dai_luong("khối lượng inox", "S1", '{"kg_moi_bo":8.62}')
    _emit("XÁC NHẬN kg/bộ=8.62 -> tính 137.92 (đường xác nhận KHÔNG đổi)", r2.get("co_ket_qua") and abs(r2["ket_qua"] - 137.92) < 0.01)
    # P.3 ANTI-FAB (dispatch tất định, độc lập task F): chiều cao cột/móng KHÔNG có ứng viên dim (cao độ ≠ dim)
    _emit("dispatch chieu_cao cột (_rs_chieu_cao_cot) -> KHÔNG ung_vien (dim 220 là tiết diện, không phải cao)", kc._ung_vien_cho_input("C1", "chieu_cao", "_rs_chieu_cao_cot") == [])
    _emit("dispatch chieu_cao móng (_rs_chieu_cao_mong) -> KHÔNG ung_vien", kc._ung_vien_cho_input("M1", "chieu_cao", "_rs_chieu_cao_mong") == [])
    r = kc.tinh_dai_luong("diện tích trát", "", '{"chieu_dai":5000,"chieu_cao":3000}')
    ths = next((t for t in r.get("inputs_thieu", []) if t["ten"] == "so_mat"), None)
    _emit("so_mat (chọn 1/2, không đo được) -> KHÔNG ung_vien", ths is not None and not ths.get("ung_vien"))
    # P.4 dim finder: không mã -> [] (chống vơ dim toàn file); có mã -> loại 0.0 + 'thap' + khoảng cách
    _emit("_ung_vien_dim(ma='') -> [] (chống vơ dim toàn file)", kc._ung_vien_dim("", "ngang") == [])
    dc = kc._ung_vien_dim("C1", "ngang")
    _emit("_ung_vien_dim('C1'): mọi ứng viên value!=0, do_tin_cay='thap', khoang_cach int", all(e["gia_tri"] != 0.0 and e["do_tin_cay"] == "thap" and isinstance(e["khoang_cach"], int) for e in dc))

    print("[Q] ƯỚC CHIỀU CAO CỘT theo cao độ (task F) — giả định 1 tầng có CỜ, KHÔNG cho móng")
    import tools_core as _TCq
    # Q.1 KC C1 không cấp chiều cao -> ước 1 tầng (typical_floor_h=3.6m) -> tính + cờ giả định LỘ
    r = kc.tinh_dai_luong("thể tích bê tông cột", "C1", "")
    _emit("C1 (chưa cấp cao) -> ước 1 tầng, ket_qua≈4.704 (0.22×0.22×3.6×27)", r.get("co_ket_qua") and abs(r["ket_qua"] - 4.704) < 0.01, "-> %s" % r.get("ket_qua"))
    cc = next((x for x in r.get("inputs_da_co", []) if x["ten"] == "chieu_cao"), None)
    _emit("chieu_cao: nguon='suy_tu_cao_do' + gia_dinh_cao_tang + chua_chac (giả định LỘ)",
          cc is not None and cc["nguon"] == "suy_tu_cao_do" and cc.get("gia_dinh_cao_tang") and cc["chua_chac"])
    _emit("ghi_chu: có 'GIẢ ĐỊNH'+'tầng', KHÔNG có 'GÁN VỊ TRÍ' (thông điệp đúng, không nhầm gán-dim)",
          "GIẢ ĐỊNH" in r.get("ghi_chu", "") and "tầng" in r.get("ghi_chu", "") and "GÁN VỊ TRÍ" not in r.get("ghi_chu", ""))
    # Q.2 override đối tác cấp -> đường CŨ, KHÔNG giả định
    r = kc.tinh_dai_luong("thể tích bê tông cột", "C1", '{"chieu_cao":5000}')
    _emit("override chieu_cao=5000 -> 6.534, KHÔNG cờ giả định (đường cũ)", r.get("co_ket_qua") and abs(r["ket_qua"] - 6.534) < 0.01 and "GIẢ ĐỊNH cột cao" not in r.get("ghi_chu", ""), "-> %s" % r.get("ket_qua"))
    # Q.3 ván khuôn cột cũng ước (chung resolver _rs_chieu_cao_cot)
    r = kc.tinh_dai_luong("diện tích ván khuôn cột", "C1", "")
    _emit("ván khuôn cột C1 -> ước 1 tầng + cờ giả định", r.get("co_ket_qua") and "GIẢ ĐỊNH" in r.get("ghi_chu", ""))
    # Q.4 MÓNG KHÔNG ước — resolver RIÊNG _rs_chieu_cao_mong (hàng rào tất định ở tầng công thức)
    _emit("móng dùng resolver riêng '_rs_chieu_cao_mong'", _TCq._FORMULAS["the_tich_be_tong_mong"]["inputs"][2][2] == "_rs_chieu_cao_mong")
    _emit("_rs_chieu_cao_mong luôn None (không bs) -> móng HỎI như cũ (chiều cao móng ≠ 1 tầng)", kc._rs_chieu_cao_mong("M1", {}, "chieu_cao") is None)
    # Q.5 _la_cot phân biệt cột / móng / dầm / rỗng
    for ma, exp in [("C1", True), ("C4", True), ("DM-1", False), ("M1", False), ("", False)]:
        _emit("_la_cot(%r)=%s" % (ma, exp), kc._la_cot(ma) == exp)
    # Q.6 guard: có levels nhưng mã KHÔNG phải cột -> KHÔNG ước; và KHÔNG levels -> hỏi (không bịa)
    _emit("có levels nhưng mã M1 (không-cột) -> _rs_chieu_cao_cot None (không ước bừa)", kc._rs_chieu_cao_cot("M1", {}, "chieu_cao") is None)
    _sv = kc.levels; kc.levels = {}
    _emit("KHÔNG levels -> C1 _rs_chieu_cao_cot None (không bịa mặc định)", kc._rs_chieu_cao_cot("C1", {}, "chieu_cao") is None)
    kc.levels = _sv

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
