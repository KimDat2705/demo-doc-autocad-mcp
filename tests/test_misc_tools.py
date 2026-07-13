# -*- coding: utf-8 -*-
"""KHOÁ tool lẻ chưa test — TẤT ĐỊNH, KHÔNG gọi Gemini, KHÔNG tốn phí.
Chạy:  python tests/test_misc_tools.py

Kiểm SHAPE + BẤT BIẾN (không bịa số kỳ vọng) của:
  dem_so_luong, tong_so_luong (có/không lọc), thong_ke_thep_hinh,
  liet_ke_block, liet_ke_sheet, liet_ke_layer  — trên KT/KC Gia Lộc.
Bất biến dùng: tong == Σ breakdown; tập con; nhất quán đếm; kiểu dữ liệu.
Fixture thiếu -> BO QUA (không crash)."""
import os, sys, io
os.environ.setdefault("READFILE_MAX_MB", "300")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
from tools_core import Drawing

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
KT = os.path.join(BASE, "BV+DT MN Gia Loc", "1. Kien truc MN Gia Loc.dxf")
KC = os.path.join(BASE, "BV+DT MN Gia Loc", "2. KetCau MN GiaLoc.dxf")

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


def chay(dwg, ten):
    kiem_dem_so_luong(dwg, ten)
    kiem_tong_so_luong(dwg, ten)
    kiem_thong_ke_thep_hinh(dwg, ten)
    kiem_liet_ke_block(dwg, ten)
    kiem_liet_ke_sheet(dwg, ten)
    kiem_liet_ke_layer(dwg, ten)


def main():
    for path, ten in [(KT, "KT Gia Lộc"), (KC, "KC Gia Lộc")]:
        if not os.path.isfile(path):
            skip(ten, "khong thay fixture (%s)" % path)
            continue
        print("\n========== %s ==========" % ten)
        chay(Drawing(path), ten)

    print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
