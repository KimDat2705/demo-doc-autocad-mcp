# -*- coding: utf-8 -*-
"""KHOÁ tool lẻ chưa test — TẤT ĐỊNH, KHÔNG gọi Gemini, KHÔNG tốn phí.
Chạy:  python tests/test_misc_tools.py

Kiểm SHAPE + BẤT BIẾN (không bịa số kỳ vọng) của:
  dem_so_luong, tong_so_luong (có/không lọc), thong_ke_thep_hinh,
  liet_ke_block, liet_ke_sheet, liet_ke_layer  — trên KT/KC CT-A.
Bất biến dùng: tong == Σ breakdown; tập con; nhất quán đếm; kiểu dữ liệu.
Fixture thiếu -> BO QUA (không crash)."""
import os, sys, io
os.environ.setdefault("READFILE_MAX_MB", "300")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
from tools_core import Drawing

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
# Ten thu muc/file that giu NGOAI repo (gitignored) — xem corpus_local.example.py
try:
    from corpus_local import KT, KC
except Exception:
    KT = KC = ""

PASS = FAIL = SKIP = 0


def _emit(name, ok, extra=""):
    global PASS, FAIL
    okk = bool(ok)
    PASS += int(okk); FAIL += int(not okk)
    print("  [%s] %s%s" % ("OK" if okk else "FAIL", name, (" " + extra) if extra else ""))


def skip(nhom, ly_do):
    global SKIP
    SKIP += 1
    print("  [..] BO QUA %s — %s (KHONG phai da kiem)" % (nhom, ly_do))


def _isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def kiem_dem_so_luong(dwg, ten):
    print("[dem_so_luong] %s" % ten)
    # 1. Rỗng -> LỘ lỗi, so_lan_xuat_hien=None (KHÔNG bịa 0)
    r = dwg.dem_so_luong("")
    _emit("rỗng -> loi + so_lan_xuat_hien=None", r.get("loi") and r.get("so_lan_xuat_hien") is None)
    r = dwg.dem_so_luong("   ")
    _emit("chỉ khoảng trắng -> loi", r.get("loi") and r.get("so_lan_xuat_hien") is None)
    # 2. Từ khoá thật -> shape đầy đủ
    r = dwg.dem_so_luong("cửa")
    n = r.get("so_lan_xuat_hien")
    _emit("'cửa' -> so_lan_xuat_hien là int>=0", _isnum(n) and int(n) >= 0, "-> %s" % n)
    vd = r.get("vi_du")
    _emit("vi_du là list, <=8 mẫu (mẫu chứ không phải tất cả)", isinstance(vd, list) and len(vd) <= 8)
    _emit("mỗi vi_du có handle/layer/text", all(("handle" in e and "layer" in e and "text" in e) for e in vd))
    _emit("so_lan_xuat_hien >= số mẫu (mẫu là tập con)", _isnum(n) and int(n) >= len(vd))
    _emit("có ghi_chu chống bịa (số LẦN != số cấu kiện)", "tra_cuu_so_luong" in r.get("ghi_chu", ""))
    # 3. NHẤT QUÁN: đếm == len(search_texts) (cùng nguồn)
    st = dwg.search_texts("cửa")
    _emit("so_lan_xuat_hien == len(search_texts) (nhất quán nguồn)", int(n) == len(st), "-> %d vs %d" % (int(n), len(st)))
    # 4. Từ khoá chắc chắn vắng -> 0 (không bịa)
    r = dwg.dem_so_luong("ZZQWX_khong_ton_tai_9999")
    _emit("từ khoá GIẢ -> 0 (không bịa), vi_du rỗng", r.get("so_lan_xuat_hien") == 0 and r.get("vi_du") == [])


def kiem_tong_so_luong(dwg, ten):
    print("[tong_so_luong] %s" % ten)
    # 1. KHÔNG lọc -> tong=None (không cộng gộp khác loại), cac_muc là list
    r = dwg.tong_so_luong()
    _emit("không lọc -> tong=None (chống gộp khác loại)", r.get("tong") is None)
    _emit("không lọc -> loc=None", r.get("loc") is None)
    cm = r.get("cac_muc")
    _emit("cac_muc là list, <=50", isinstance(cm, list) and len(cm) <= 50)
    _emit("so_muc là int, >= số mục hiển thị", _isnum(r.get("so_muc")) and int(r["so_muc"]) >= len(cm))
    _emit("mỗi mục có noi_dung/so_luong/handle", all(("noi_dung" in e and "so_luong" in e and "handle" in e) for e in cm))
    # 2. CÓ lọc 'cửa' -> tong là số, == Σ so_luong các mục (khi không bị cắt [:50])
    r = dwg.tong_so_luong(loc="cửa")
    _emit("lọc 'cửa' -> loc='cửa'", r.get("loc") == "cửa")
    tong = r.get("tong")
    muc = r.get("cac_muc") or []
    somuc = r.get("so_muc") or 0
    _emit("lọc -> tong là số (đã cộng)", _isnum(tong), "-> %s" % tong)
    if somuc <= 50:
        # cac_muc không bị cắt -> tong PHẢI == Σ breakdown (bất biến cốt lõi)
        s = sum(m["so_luong"] for m in muc)
        _emit("BẤT BIẾN: tong == Σ so_luong(cac_muc) [so_muc<=50]", _isnum(tong) and abs(tong - s) < 1e-9, "-> %s vs %s" % (tong, s))
    else:
        _emit("BẤT BIẾN: tong >= Σ so_luong(cac_muc[:50]) [bị cắt]", _isnum(tong) and tong >= sum(m["so_luong"] for m in muc))
    _emit("mọi so_luong >= 0 (không âm)", all(_isnum(m["so_luong"]) and m["so_luong"] >= 0 for m in muc))
    # 3. NHẤT QUÁN với liet_ke_so_luong: tong_so_luong GỘP cùng mã -> so_muc <= liet_ke so_muc
    lk = dwg.liet_ke_so_luong(loc="cửa")
    _emit("so_muc(tong, đã gộp mã) <= so_muc(liet_ke, chưa gộp)",
          somuc <= lk.get("so_muc", 0), "-> %d <= %d" % (somuc, lk.get("so_muc", 0)))
    # 4. Lọc GIẢ -> tong=0 hoặc so_muc=0 (không vơ cả bảng)
    r = dwg.tong_so_luong(loc="ZZQWX_khong_ton_tai_9999")
    _emit("lọc GIẢ -> so_muc=0, tong=0 (không vơ cả bảng)", r.get("so_muc") == 0 and r.get("tong") == 0)


def kiem_thong_ke_thep_hinh(dwg, ten):
    print("[thong_ke_thep_hinh] %s" % ten)
    r = dwg.thong_ke_thep_hinh()
    _emit("trả co_bang là bool", isinstance(r.get("co_bang"), bool))
    if r.get("co_bang"):
        theo = r.get("theo_tiet_dien")
        _emit("có bảng -> theo_tiet_dien là dict", isinstance(theo, dict))
        _emit("mỗi tiết diện có so_luong + khoi_luong_kg (số)",
              all(_isnum(v.get("so_luong")) and _isnum(v.get("khoi_luong_kg")) for v in theo.values()))
        _emit("tong_khoi_luong_kg là số >= 0", _isnum(r.get("tong_khoi_luong_kg")) and r["tong_khoi_luong_kg"] >= 0,
              "-> %s kg" % r.get("tong_khoi_luong_kg"))
        _emit("so_dong là số >= 0", _isnum(r.get("so_dong")) and r["so_dong"] >= 0)
    else:
        # NHÁNH KHÔNG-CÓ-BẢNG: phải LỘ (ghi_chu) + KHÔNG bịa tổng
        _emit("không bảng -> có ghi_chu + KHÔNG field tổng (không bịa)",
              bool(r.get("ghi_chu")) and all(k not in r for k in ("tong_khoi_luong_kg", "theo_tiet_dien", "so_dong")))


def kiem_liet_ke_block(dwg, ten):
    print("[liet_ke_block] %s" % ten)
    r = dwg.liet_ke_block()
    for k in ("so_loai_block", "so_loai_co_ten", "so_loai_noi_bo_an_danh"):
        _emit("%s là số >= 0" % k, _isnum(r.get(k)) and r[k] >= 0, "-> %s" % r.get(k))
    # BẤT BIẾN: có tên + nội bộ = tổng loại (phân hoạch trọn vẹn)
    _emit("BẤT BIẾN: co_ten + noi_bo_an_danh == so_loai_block",
          r["so_loai_co_ten"] + r["so_loai_noi_bo_an_danh"] == r["so_loai_block"],
          "-> %d + %d == %d" % (r["so_loai_co_ten"], r["so_loai_noi_bo_an_danh"], r["so_loai_block"]))
    top = r.get("top_block_co_ten")
    _emit("top_block_co_ten là dict, <=25 (chỉ top)", isinstance(top, dict) and len(top) <= 25)
    _emit("top <= số block có tên", len(top) <= r["so_loai_co_ten"])
    _emit("giá trị top là số đếm >= 1", all(_isnum(v) and v >= 1 for v in top.values()))


def kiem_liet_ke_sheet(dwg, ten):
    print("[liet_ke_sheet] %s" % ten)
    r = dwg.liet_ke_sheet()
    ds = r.get("danh_sach")
    _emit("danh_sach là list", isinstance(ds, list))
    # BẤT BIẾN: so_tieu_de == len(danh_sach) (sau bỏ trùng)
    _emit("BẤT BIẾN: so_tieu_de == len(danh_sach)", r.get("so_tieu_de") == len(ds),
          "-> %s vs %d" % (r.get("so_tieu_de"), len(ds)))
    # BẤT BIẾN: bỏ trùng -> so_tieu_de <= so_nhan_tho
    _emit("BẤT BIẾN: so_tieu_de <= so_nhan_tho (bỏ trùng không tăng)",
          _isnum(r.get("so_tieu_de")) and _isnum(r.get("so_nhan_tho")) and r["so_tieu_de"] <= r["so_nhan_tho"],
          "-> %s <= %s" % (r.get("so_tieu_de"), r.get("so_nhan_tho")))
    _emit("mỗi mục có handle + title", all(("handle" in e and "title" in e) for e in ds))
    # bỏ trùng THẬT: không title trùng (chuẩn hoá lower/strip)
    keys = [e["title"].strip().lower() for e in ds]
    _emit("danh_sach KHÔNG còn title trùng (đã dedup)", len(keys) == len(set(keys)))


def kiem_liet_ke_layer(dwg, ten):
    print("[liet_ke_layer] %s" % ten)
    r = dwg.liet_ke_layer()
    ds = r.get("danh_sach")
    _emit("danh_sach là list", isinstance(ds, list))
    # BẤT BIẾN: so_layer == len(danh_sach)
    _emit("BẤT BIẾN: so_layer == len(danh_sach)", r.get("so_layer") == len(ds),
          "-> %s vs %d" % (r.get("so_layer"), len(ds)))
    _emit("so_layer >= 1 (file DXF luôn có layer '0')", _isnum(r.get("so_layer")) and r["so_layer"] >= 1)
    _emit("mỗi layer là chuỗi tên (không rỗng-None)", all(isinstance(x, str) for x in ds))
    _emit("có ghi_chu", bool(r.get("ghi_chu")))


def kiem_tim_kiem_bicat(dwg, ten):
    """I5 (2026-07-25): tim_kiem LỘ cờ bi_cat khi kết quả bị cắt (recall — thất bại phải lộ) + nudge sạch số."""
    import re as _re
    print("[tim_kiem I5 bi_cat] %s" % ten)
    kw = None
    for c in ("1", "a", "0", "m", "C", "e"):
        if dwg.tim_kiem(tu_khoa=c).get("so_ket_qua", 0) >= 2:
            kw = c; break
    if kw is None:
        _emit("tim_kiem-bicat: (bỏ qua) không có từ khoá >=2 kết quả", True); return
    r1 = dwg.tim_kiem(tu_khoa=kw, gioi_han=1)   # ép cắt: 1 < so_ket_qua
    _emit("gioi_han=1 (kết quả nhiều) -> bi_cat=True + hien_thi=1 + nudge 'BỊ CẮT' (thất bại phải lộ)",
          r1.get("bi_cat") is True and r1.get("hien_thi") == 1 and "BỊ CẮT" in r1.get("ghi_chu", ""),
          "-> so_ket_qua=%s" % r1.get("so_ket_qua"))
    _emit("bi_cat là bool (không lọt grounding)", isinstance(r1.get("bi_cat"), bool))
    _idx = r1.get("ghi_chu", "").find("BỊ CẮT")
    _emit("đoạn nudge KHÔNG chứa chữ số (số ở field so_ket_qua/hien_thi, không lọt grounding)",
          _idx >= 0 and not _re.search(r"\d", r1["ghi_chu"][_idx:]))
    r2 = dwg.tim_kiem(tu_khoa=kw, gioi_han=200)   # lấy hết khi <=200 -> bi_cat theo tổng
    _emit("gioi_han=200 -> bi_cat == (so_ket_qua>200) (lấy hết khi <=200)",
          r2.get("bi_cat") == (r2.get("so_ket_qua", 0) > 200))
    r3 = dwg.tim_kiem(tu_khoa=kw, gioi_han=-5)   # BẤT BIẾN cũ: giới hạn âm -> hien_thi=0
    _emit("gioi_han=-5 -> hien_thi=0 (giữ hành vi cũ, không cắt cụt âm)", r3.get("hien_thi") == 0)


def kiem_tok_bound_regress():
    """Pattern A (2026-07-26) — no-regression BIÊN (fixture-independent): mã có gạch-sau-chữ-số ('D2-4')
    giờ khớp nhãn 'd2-4 (SL=..)' NHƯNG ranh giới vẫn chặn C-4≠C-40, D2-2≠D2-2A; C-1==C1 giữ nguyên."""
    from tools_core import _tok_bound
    print("[_tok_bound A no-regress]")
    _emit("A: 'd2-4' khớp 'd2-4 (sl= 05)' (FIX recall id73/93/103)", _tok_bound("d2-4", "d2-4 (sl= 05, l= 12.82m)"))
    _emit("A: 'd2-2' khớp 'd2-2 (sl= 02)'", _tok_bound("d2-2", "d2-2 (sl= 02, l= 59.02m)"))
    _emit("A: 'd2' (HỌ) VẪN khớp 'd2-1' (không phá prefix họ — chống regress tong_so_luong)", _tok_bound("d2", "dam d2-1"))
    _emit("A: 'd2' KHÔNG khớp 'd20' (họ ≠ mã liền số)", not _tok_bound("d2", "cot d20"))
    _emit("A: 'c-1' == 'c1' (giữ nguyên, không regress)", _tok_bound("c-1", "c1 mong don"))
    _emit("A: 'c-4' KHÔNG khớp 'c-40' (ranh giới con)", not _tok_bound("c-4", "cot c-40 chi tiet"))
    _emit("A: 'd2-2' KHÔNG khớp 'd2-2a' (ranh giới con)", not _tok_bound("d2-2", "dam d2-2a"))


def kiem_recall_fixes(dwg, ten):
    """Recall fixes 2026-07-26: B thong_tin_file (metadata) / C bang_con (subtotal riêng bảng) / A e2e (D2-x, chỉ KC)."""
    print("[recall-fixes A/B/C] %s" % ten)
    tf = dwg.thong_tin_file()
    _emit("B thong_tin_file: name+dxfversion+so_layer(>=1)+ghi_chu (vá id39/107)",
          bool(tf.get("name")) and bool(tf.get("dxfversion")) and _isnum(tf.get("so_layer"))
          and tf["so_layer"] >= 1 and bool(tf.get("ghi_chu")), "-> %s / %s" % (tf.get("name"), tf.get("dxfversion")))
    bc = dwg.thong_ke_thep_hinh().get("bang_con")
    _emit("C bang_con: None hoặc list mỗi mục tong_kg(số>0)+handle+nguyen_van (đọc verbatim, không bịa)",
          bc is None or (isinstance(bc, list) and all(_isnum(b.get("tong_kg")) and b["tong_kg"] > 0
                          and b.get("handle") and b.get("nguyen_van") for b in bc)))
    if "KC" in ten:
        det, okA = [], True
        for ma in ("D2-4", "D2-7", "D2-2"):
            ds = (dwg.tra_cuu_so_luong(tu_khoa=ma).get("danh_sach_so_luong") or [])
            has = bool(ds) and _isnum(ds[0].get("so_luong"))
            okA = okA and has; det.append("%s=%s" % (ma, ds[0].get("so_luong") if ds else None))
        _emit("A recall e2e: tra_cuu D2-4/D2-7/D2-2 -> có so_luong (id73/93/103)", okA, "-> " + ", ".join(det))
    if "KT" in ten:
        kgs = [b.get("tong_kg") for b in (dwg.thong_ke_thep_hinh().get("bang_con") or [])]
        _emit("C KT: bang_con có 2163.02 (thép hình id22) + 161.21 (inox304 id32)",
              any(abs((v or 0) - 2163.02) < 0.1 for v in kgs) and any(abs((v or 0) - 161.21) < 0.1 for v in kgs),
              "-> %d subtotal" % len(kgs))


def chay(dwg, ten):
    kiem_dem_so_luong(dwg, ten)
    kiem_tong_so_luong(dwg, ten)
    kiem_thong_ke_thep_hinh(dwg, ten)
    kiem_liet_ke_block(dwg, ten)
    kiem_liet_ke_sheet(dwg, ten)
    kiem_liet_ke_layer(dwg, ten)
    kiem_tim_kiem_bicat(dwg, ten)
    kiem_recall_fixes(dwg, ten)


def main():
    kiem_tok_bound_regress()   # A no-regression BIÊN (fixture-independent) — chạy 1 lần
    for path, ten in [(KT, "KT CT-A"), (KC, "KC CT-A")]:
        if not os.path.isfile(path):
            skip(ten, "khong thay fixture (%s)" % path)
            continue
        print("\n========== %s ==========" % ten)
        chay(Drawing(path), ten)

    print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
