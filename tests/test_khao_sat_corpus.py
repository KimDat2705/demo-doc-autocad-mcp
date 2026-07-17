# -*- coding: utf-8 -*-
"""KHẢO SÁT CORPUS (khao_sat_corpus.py) — công cụ soi bản vẽ đối tác mới (GĐ4/P5/id135).
TẤT ĐỊNH, OFFLINE, KHÔNG cần corpus thật (dựng DXF tổng hợp), KHÔNG tốn API.
Chạy:  python tests/test_khao_sat_corpus.py

Kiểm: helper nhóm/tỷ-lệ/liệt-kê · ĐO RAM thật (khoá bug argtypes) · tracemalloc MẶC ĐỊNH TẮT (khoá bug
thổi RSS 2.1x) · mô hình baseline+delta · child đọc DXF tổng hợp · DXF hỏng -> LỘ lỗi không ném ·
.dwg thiếu ODA -> LỘ lỗi · parent fail-soft (1 file hỏng không giết phiên) · ngưỡng Render ·
tổng hợp nhóm tách file lỗi · KHÔNG mutate corpus gốc · báo cáo JSON · root sai -> exit 1."""
import os
import sys
import io
import json
import shutil
import tempfile

os.environ.setdefault("READFILE_MAX_MB", "500")
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)

import ezdxf
import khao_sat_corpus as KS

PASS = FAIL = SKIP = 0
_TMP = tempfile.mkdtemp(prefix="khaosat_")


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def skip(name):
    global SKIP
    SKIP += 1
    print("  [..] BO QUA %s (thieu fixture)" % name)


def _dxf_tot(path, n_text=5):
    """DXF hợp lệ nhỏ: 2 layer + text thường + 1 marker cao độ."""
    doc = ezdxf.new("R2010")
    doc.layers.add("KC_TEXT")
    doc.layers.add("KT_DIM")
    msp = doc.modelspace()
    for i in range(n_text):
        msp.add_text("NHAN-%d" % i, dxfattribs={"layer": "KC_TEXT"}).set_placement((i * 10.0, 0.0))
    msp.add_text("-1.850", dxfattribs={"layer": "KC_TEXT"}).set_placement((0.0, 50.0))
    msp.add_text("±0.000", dxfattribs={"layer": "KC_TEXT"}).set_placement((0.0, 60.0))
    doc.saveas(path)
    return path


def _dxf_hong(path):
    with open(path, "wb") as f:
        f.write(b"KHONG PHAI DXF \x00\x01\x02 rac rac rac" * 50)
    return path


def main():
    print("[A] Helper tat dinh (nhom / ty le / liet ke / mb)")
    root = os.path.join(_TMP, "corpus")
    os.makedirs(os.path.join(root, "FirmA"), exist_ok=True)
    os.makedirs(os.path.join(root, "FirmB", "sub"), exist_ok=True)
    os.makedirs(os.path.join(root, "_dxf"), exist_ok=True)
    fa = _dxf_tot(os.path.join(root, "FirmA", "a.dxf"))
    fb = _dxf_tot(os.path.join(root, "FirmB", "sub", "b.dxf"))
    _dxf_tot(os.path.join(root, "_dxf", "cache.dxf"))          # phải bị loại trừ
    open(os.path.join(root, "FirmA", "ghichu.txt"), "w").close()  # không phải bản vẽ
    goc = _dxf_tot(os.path.join(root, "goc.dxf"))

    ok("_nhom_of: root/FirmA/a.dxf -> 'FirmA'", KS._nhom_of(fa, root) == "FirmA", KS._nhom_of(fa, root))
    ok("_nhom_of: long sau root/FirmB/sub/b.dxf -> 'FirmB'", KS._nhom_of(fb, root) == "FirmB", KS._nhom_of(fb, root))
    ok("_nhom_of: file tham root -> '(goc)'", KS._nhom_of(goc, root) == "(goc)", KS._nhom_of(goc, root))
    ok("_ty_le: mau 0 -> None (KHONG chia 0, KHONG bia)", KS._ty_le(10, 0) is None)
    ok("_ty_le: tu None -> None", KS._ty_le(None, 5) is None)
    ok("_ty_le: 174/25.2 = 6.9", KS._ty_le(174, 25.2) == 6.9, KS._ty_le(174, 25.2))
    ok("_mb: file khong ton tai -> None", KS._mb(os.path.join(_TMP, "khong_co.dxf")) is None)

    ds = KS.liet_ke_ban_ve(root, ["_dxf"])
    tens = sorted(os.path.basename(p) for p in ds)
    ok("liet_ke_ban_ve: thay a/b/goc, LOAI _dxf + .txt", tens == ["a.dxf", "b.dxf", "goc.dxf"], tens)
    ok("liet_ke_ban_ve: tat dinh (sorted, chay 2 lan giong nhau)",
       KS.liet_ke_ban_ve(root, ["_dxf"]) == ds)

    print("[B] DO RAM THAT — khoa bug argtypes (handle 64-bit bi cat -> im lang tra None)")
    ram = KS._peak_rss_mb()
    ok("_peak_rss_mb() tra so DUONG, khong None", isinstance(ram, float) and ram > 0, ram)
    ok("_cach_do_ram() noi ro cach do (khong mo ho)", isinstance(KS._cach_do_ram(), str) and len(KS._cach_do_ram()) > 5)

    print("[C] CHILD doc DXF tong hop -> schema + so lieu + mo hinh baseline/delta")
    r = KS._khao_sat_1_file(fa, os.path.join(_TMP, "out"), 500)
    ok("khong loi", r.get("loi") is None, r.get("loi"))
    for k in ("ten_file", "raw_mb", "dxf_mb", "so_layer", "so_text", "qty_so_muc", "cao_do",
              "ram_baseline_mb", "ram_peak_mb", "ram_delta_mb", "he_so_ram_tren_dxf", "so_residual"):
        ok("schema co truong '%s'" % k, k in r, sorted(r.keys()))
    ok("so_layer >= 2 (KC_TEXT + KT_DIM)", (r.get("so_layer") or 0) >= 2, r.get("so_layer"))
    ok("so_text >= 5", (r.get("so_text") or 0) >= 5, r.get("so_text"))
    ok("ram_delta = peak - baseline (nhat quan, >=0)",
       r["ram_delta_mb"] is not None and abs(r["ram_delta_mb"] - (r["ram_peak_mb"] - r["ram_baseline_mb"])) < 0.2
       and r["ram_delta_mb"] >= 0, (r["ram_baseline_mb"], r["ram_peak_mb"], r["ram_delta_mb"]))
    ok("cao_do doc duoc marker '-1.850' (noi thong xuong engine that)",
       (r.get("cao_do") or {}).get("thap_nhat_m") == -1.85, r.get("cao_do"))

    print("[D] tracemalloc MAC DINH TAT — khoa bug 'cong cu do lam phong RSS ~2.1x'")
    ok("mac dinh: ram_nhieu_boi_tracemalloc = False", r["ram_nhieu_boi_tracemalloc"] is False)
    ok("mac dinh: ram_python_mb = None (KHONG chay tracemalloc)", r["ram_python_mb"] is None, r["ram_python_mb"])
    r_tm = KS._khao_sat_1_file(fa, os.path.join(_TMP, "out"), 500, dung_tracemalloc=True)
    ok("bat --tracemalloc: co ram_python_mb + CO CO canh bao nhieu",
       r_tm["ram_python_mb"] is not None and r_tm["ram_nhieu_boi_tracemalloc"] is True,
       (r_tm["ram_python_mb"], r_tm["ram_nhieu_boi_tracemalloc"]))

    print("[E] DXF HONG -> LO loi, KHONG nem (fail-soft co bang chung)")
    hong = _dxf_hong(os.path.join(root, "FirmA", "hong.dxf"))
    rh = KS._khao_sat_1_file(hong, os.path.join(_TMP, "out"), 500)
    ok("co field 'loi' (khong im lang)", bool(rh.get("loi")), rh)
    ok("'loi_buoc' chi ro chet o buoc nao", rh.get("loi_buoc") in ("load", "convert", "doc", "cao_do"), rh.get("loi_buoc"))

    print("[F] .dwg khi THIEU ODA -> LO loi co nghia (khong nham la 'file hong')")
    import dwgconv
    that = dwgconv.oda_available
    try:
        dwgconv.oda_available = lambda: False
        fake_dwg = os.path.join(root, "FirmA", "gia.dwg")
        shutil.copy2(fa, fake_dwg)
        rd = KS._khao_sat_1_file(fake_dwg, os.path.join(_TMP, "out"), 500)
        ok("loi neu ro thieu ODA + cach khac phuc (ODA_EXE)",
           rd.get("loi") and "ODA" in rd["loi"] and "ODA_EXE" in rd["loi"], rd.get("loi"))
        ok("bao dung buoc 'convert'", rd.get("loi_buoc") == "convert", rd.get("loi_buoc"))
        os.remove(fake_dwg)
    finally:
        dwgconv.oda_available = that

    print("[G] _gan_nguong: doi chieu nguong SAN XUAT theo max(raw, dxf)")
    g1 = KS._gan_nguong({"raw_mb": 3.0, "dxf_mb": 25.0, "ram_peak_mb": 240.0})
    ok("25MB: Free OK + Standard OK", g1["render_free_doc_duoc"] and g1["render_standard_doc_duoc"])
    g2 = KS._gan_nguong({"raw_mb": 19.0, "dxf_mb": 112.0, "ram_peak_mb": 900.0})
    ok("dxf 112MB: Free KHONG (>45) nhung Standard OK (<=200)",
       g2["render_free_doc_duoc"] is False and g2["render_standard_doc_duoc"] is True)
    ok("RAM 900MB: vuot Free 512, chua vuot Standard 2048",
       g2["ram_vuot_free_512"] is True and g2["ram_vuot_standard_2048"] is False)
    g3 = KS._gan_nguong({"raw_mb": 260.0, "dxf_mb": 30.0, "ram_peak_mb": 2500.0})
    ok("raw 260MB (dxf nho hon): van CHAN o Standard — guard xet raw TRUOC convert",
       g3["render_standard_doc_duoc"] is False)
    ok("RAM 2500MB: vuot ca Standard 2048", g3["ram_vuot_standard_2048"] is True)
    g4 = KS._gan_nguong({"loi": "chet", "raw_mb": 1.0})
    ok("file LOI: khong gan ket luan chiu tai (khong bia)", "render_free_doc_duoc" not in g4)

    print("[H] _tong_hop_nhom: file LOI dem RIENG, KHONG cong vao so do")
    th = KS._tong_hop_nhom([
        {"_nhom": "X", "raw_mb": 2.0, "dxf_mb": 20.0, "ram_peak_mb": 200.0, "qty_so_muc": 5,
         "so_text": 10, "so_layer": 3, "co_bang_thong_ke": True, "cao_do": {"thap_nhat_m": -1.5}},
        {"_nhom": "X", "raw_mb": 3.0, "dxf_mb": 30.0, "ram_peak_mb": 400.0, "qty_so_muc": 7,
         "so_text": 20, "so_layer": 9, "co_bang_thong_ke": False, "cao_do": {"thap_nhat_m": -9.9}},
        {"_nhom": "X", "loi": "chet", "raw_mb": 999.0},
    ])["X"]
    ok("so_file=3 nhung so_file_loi=1 (LO, khong giau)", th["so_file"] == 3 and th["so_file_loi"] == 1, th)
    ok("raw/dxf KHONG cong file loi (2+3=5, 20+30=50)", th["raw_mb"] == 5.0 and th["dxf_mb"] == 50.0, th)
    ok("ram_peak_max = max(200,400) = 400", th["ram_peak_max_mb"] == 400.0, th)
    ok("co_bang_thong_ke = OR toan nhom", th["co_bang_thong_ke"] is True)
    ok("cao_do_thap_nhat = min(-1.5, -9.9) = -9.9", th["cao_do_thap_nhat_m"] == -9.9, th)

    print("[I] PARENT: fail-soft that (spawn subprocess) + KHONG mutate corpus goc")
    truoc = sorted(os.path.relpath(os.path.join(dp, f), root)
                   for dp, _, fs in os.walk(root) for f in fs)
    rep = KS.khao_sat(root, os.path.join(_TMP, "out2"), ["_dxf"], 500, timeout=300)
    ok("chay het MOI file du co file hong (fail-soft)", rep["meta"]["so_file"] == 4, rep["meta"])
    ok("dem dung so file loi = 1 (hong.dxf)", rep["meta"]["so_file_loi"] == 1, rep["meta"]["so_file_loi"])
    ok("file tot van co so do day du (khong bi file hong keo do)",
       sum(1 for r in rep["files"] if not r.get("loi") and r.get("so_layer")) == 3,
       [(r["ten_file"], r.get("loi")) for r in rep["files"]])
    ok("nhom dung: FirmA / FirmB / (goc)",
       {r["_nhom"] for r in rep["files"]} == {"FirmA", "FirmB", "(goc)"},
       {r["_nhom"] for r in rep["files"]})
    sau = sorted(os.path.relpath(os.path.join(dp, f), root)
                 for dp, _, fs in os.walk(root) for f in fs)
    ok("KHONG ghi gi vao corpus goc (read-only voi --root)", truoc == sau,
       set(sau) ^ set(truoc))
    ok("meta ghi ro cach do RAM + ODA + loai_tru (truy duoc nguon so)",
       rep["meta"].get("cach_do_ram") and "loai_tru" in rep["meta"] and "oda" in rep["meta"])

    print("[J] Bao cao JSON: ghi + doc lai duoc, du khoi")
    jf = os.path.join(_TMP, "bao_cao.json")
    rc = KS.main(["--root", root, "--dxf-out", os.path.join(_TMP, "out3"), "--json", jf,
                  "--timeout", "300", "--max-mb", "500"])
    ok("main() tra 0 khi khao sat xong (co file loi van 0 — day la CONG CU, khong phai gate)", rc == 0, rc)
    ok("file JSON ton tai", os.path.isfile(jf))
    rep2 = json.load(open(jf, encoding="utf-8"))
    ok("JSON du khoi meta/nguong/files/theo_nhom",
       {"meta", "nguong", "files", "theo_nhom"} <= set(rep2.keys()), sorted(rep2.keys()))
    ok("nguong ghi ro moc Render (45/200/512/2048) de doi chieu ve sau",
       rep2["nguong"]["render_free_doc_mb"] == 45 and rep2["nguong"]["render_standard_doc_mb"] == 200
       and rep2["nguong"]["ram_free_mb"] == 512 and rep2["nguong"]["ram_standard_mb"] == 2048)

    print("[K2] HE SO RAM: KHONG ngoai suy tu file nho (baseline lan at -> so RAC)")
    ok("MIN_MB_HE_SO ton tai va hop ly (>=1MB)", getattr(KS, "MIN_MB_HE_SO", 0) >= 1.0, getattr(KS, "MIN_MB_HE_SO", None))
    buf = io.StringIO()
    _stdout = sys.stdout
    try:
        sys.stdout = buf
        KS.in_bao_cao({
            "meta": {"thoi_diem": "t", "root": "r", "oda": "x", "cach_do_ram": "y",
                     "so_file": 1, "so_nhom": 1, "so_file_loi": 0},
            "nguong": KS.NGUONG,
            "files": [{"_nhom": "N", "ten_file": "tinhon.dxf", "raw_mb": 0.02, "dxf_mb": 0.02,
                       "ram_baseline_mb": 68.0, "ram_peak_mb": 69.5, "ram_delta_mb": 1.5,
                       "he_so_ram_tren_dxf": 75.0, "so_layer": 4, "so_text": 7, "qty_so_muc": 0,
                       "so_section_index": 0, "so_residual": 5, "cao_do": {}}],
            "theo_nhom": {},
        })
    finally:
        sys.stdout = _stdout
    txt = buf.getvalue()
    ok("file 0.02MB: KHONG in he so '75.0x' ra bao cao (chan so rac)", "75.0x" not in txt, txt[-400:])
    ok("thay vao do NOI RO thieu du lieu", "CHUA du du lieu" in txt, txt[-400:])

    print("[K] root SAI -> exit 1 + goi y ro (khong crash, khong im lang)")
    rc = KS.main(["--root", os.path.join(_TMP, "khong-ton-tai"), "--json", os.path.join(_TMP, "x.json")])
    ok("exit 1 khi thu muc corpus khong ton tai", rc == 1, rc)
    rong = os.path.join(_TMP, "rong")
    os.makedirs(rong, exist_ok=True)
    rc = KS.main(["--root", rong, "--json", os.path.join(_TMP, "y.json")])
    ok("exit 1 khi khong co file .dwg/.dxf nao (LO, khong bao 'thanh cong 0 file')", rc == 1, rc)

    if SKIP:
        print("CANH BAO: %d nhom BO QUA (thieu fixture)" % SKIP)
    print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP))
    return 1 if FAIL else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
