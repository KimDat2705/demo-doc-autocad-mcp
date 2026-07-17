# -*- coding: utf-8 -*-
"""khao_sat_corpus.py — KHẢO SÁT CORPUS bản vẽ đối tác (nền cho GĐ4 đa-domain / P5 / id135-E2E).

Trả lời 4 câu hỏi mà nút thắt "corpus ≥3 firm" đang chờ:
  1. CÓ GÌ?      — quét đệ quy, nhóm theo thư mục gốc, .dwg tự convert sang .dxf qua ODA (có cache).
  2. CHỊU TẢI?   — đo ĐỈNH RAM THẬT + kích thước → đối chiếu ngưỡng Render Free/Standard.
  3. ĐỌC ĐƯỢC?   — đếm layer/text/block/dim/sheet + qty THEO NGUỒN (bảng thống kê vs inline vs spatial).
  4. CÓ ỨNG VIÊN id135? — cao_do_min_max từng file → tìm file hạ tầng có mốc sâu để chạy E2E-thật.

THIẾT KẾ (vì sao mỗi file 1 SUBPROCESS):
  * Đỉnh RAM tiến trình là chỉ số MONOTONIC — nạp nhiều file trong 1 tiến trình thì đỉnh bị cộng dồn,
    số đo per-file sẽ SAI. Tiến trình riêng = số đo sạch cho từng file.
  * File lớn/hỏng có thể OOM/treo. Cô lập + timeout → 1 file xấu KHÔNG giết cả phiên khảo sát.

ETHOS (bám dự án):
  * THẤT BẠI PHẢI LỘ — file lỗi/timeout/thiếu ODA đều được ĐẾM + IN RÕ, không im lặng bỏ qua.
  * KHÔNG BỊA — chỉ báo cái ĐO được. Nhóm = THƯ MỤC GỐC, KHÔNG suy ra "đơn vị thiết kế"
    (tên thư mục không chứng minh được firm — việc gán firm là của NGƯỜI).
  * KHÔNG ĐỤNG corpus gốc — .dxf convert ra ghi vào --dxf-out (mặc định _khao_sat/), read-only với --root.

CHẠY:
  python tests/khao_sat_corpus.py                      # quét ../input_files, báo cáo ra _khao_sat/
  python tests/khao_sat_corpus.py --root "D:/duong/dan" --gioi-han 3
  python tests/khao_sat_corpus.py --json bao_cao.json --timeout 1200
"""
import os
import sys
import io
import json
import time
import glob
import argparse
import subprocess
from collections import Counter

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_PKG = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT_PKG)

# Ngưỡng SẢN XUẤT (đối chiếu, KHÔNG áp khi khảo sát local — local đọc thoải mái, miễn phí).
NGUONG = {
    "render_free_doc_mb": 45,      # READFILE_MAX_MB gói Free 512MB
    "render_standard_doc_mb": 200,  # READFILE_MAX_MB gói Standard 2GB (commit HELD)
    "ram_free_mb": 512,
    "ram_standard_mb": 2048,
}
MARK = "###KS_JSON###"   # mốc tách JSON khỏi cảnh báo ezdxf/ODA lẫn trên stdout
CAT_DXF = (".dxf",)
CAT_DWG = (".dwg",)
# Dưới ngưỡng này, hệ số RAM/DXF là RÁC: RAM bị baseline + granularity cấp phát lấn át
# (đo thật: DXF 0.02MB -> "75x"; DXF 25-114MB -> 6.9-8.0x). Chỉ ngoại suy từ file đủ lớn.
MIN_MB_HE_SO = 5.0


# ---------------------------------------------------------------- tiện ích chung
def _mb(path):
    try:
        return round(os.path.getsize(path) / 1048576.0, 2)
    except OSError:
        return None


def _ty_le(tu, mau):
    """Tỷ lệ an toàn: mẫu 0/None -> None (KHÔNG bịa số, KHÔNG chia 0)."""
    if not mau or tu is None:
        return None
    return round(float(tu) / float(mau), 2)


def _nhom_of(path, root):
    """Nhóm = THƯ MỤC GỐC ngay dưới root (file nằm thẳng root -> '(goc)').
    ⚠ Đây là NHÓM THƯ MỤC, KHÔNG phải 'đơn vị thiết kế' — gán firm là việc của người."""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    parts = rel.replace("\\", "/").split("/")
    return parts[0] if len(parts) > 1 else "(goc)"


def _peak_rss_mb():
    """ĐỈNH RAM tiến trình (RSS/WorkingSet) — chỉ số quyết định trần Render.
    Windows: PeakWorkingSetSize · Linux: ru_maxrss(KB) · macOS: ru_maxrss(bytes). None nếu không đo được.

    ⚠ BẮT BUỘC khai báo argtypes/restype: mặc định ctypes coi giá trị trả về của GetCurrentProcess là
    C int 32-bit, nên pseudo-handle (HANDLE)-1 bị CẮT khi truyền vào tham số HANDLE 64-bit -> API trả 0
    -> mất số đo (đã tái hiện thật). Không có argtypes thì hàm này im lặng trả None."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            from ctypes import wintypes

            class _PMC(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            k32.GetCurrentProcess.argtypes = []
            h = k32.GetCurrentProcess()

            fn = None
            try:
                fn = ctypes.WinDLL("psapi.dll", use_last_error=True).GetProcessMemoryInfo
            except Exception:
                fn = getattr(k32, "K32GetProcessMemoryInfo", None)   # Win7+ có bản trong kernel32
            if fn is None:
                return None
            fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
            fn.restype = wintypes.BOOL

            c = _PMC()
            c.cb = ctypes.sizeof(_PMC)
            if fn(h, ctypes.byref(c), c.cb):
                return round(c.PeakWorkingSetSize / 1048576.0, 1)
        except Exception:
            return None
        return None
    try:
        import resource
        m = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return round(m / 1024.0 if sys.platform.startswith("linux") else m / 1048576.0, 1)
    except Exception:
        return None


def _cach_do_ram():
    if sys.platform.startswith("win"):
        return "Windows PeakWorkingSetSize (psapi)"
    if sys.platform.startswith("linux"):
        return "Linux ru_maxrss (RUSAGE_SELF)"
    return "ru_maxrss (RUSAGE_SELF)"


def liet_ke_ban_ve(root, loai_tru):
    """Mọi .dwg/.dxf dưới root (đệ quy), bỏ thư mục trong loai_tru. Sắp xếp tất định."""
    ra = []
    bo = {x.lower() for x in loai_tru}
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d.lower() not in bo)
        for fn in sorted(fns):
            if os.path.splitext(fn)[1].lower() in CAT_DXF + CAT_DWG:
                ra.append(os.path.join(dp, fn))
    return ra


# ---------------------------------------------------------------- CHILD: khảo sát 1 file
def _khao_sat_1_file(path, dxf_out, max_mb, dung_tracemalloc=False):
    """Chạy TRONG TIẾN TRÌNH CON. Trả dict hồ sơ 1 file. Mọi lỗi -> field 'loi' (LỘ, không ném).

    ⚠ tracemalloc MẶC ĐỊNH TẮT: đã ĐO THẬT — bật tracemalloc làm RSS đỉnh PHỒNG ~2.1x
    (cùng file: tắt=241MB/6.9x · bật=510MB/17.6x) vì nó lưu vết mọi allocation của ezdxf.
    RSS là thứ quyết định trần Render -> để bật mặc định là tự bịa số chịu tải cao gấp ~2.5x."""
    os.environ["READFILE_MAX_MB"] = str(max_mb)   # local đọc thoải mái; ngưỡng prod đối chiếu ở parent
    rec = {
        "duong_dan": path, "ten_file": os.path.basename(path),
        "ext": os.path.splitext(path)[1].lower(),
        "raw_mb": _mb(path), "dxf_mb": None, "convert_s": None, "convert_cache": False,
        "load_s": None, "ram_baseline_mb": None, "ram_peak_mb": None, "ram_delta_mb": None,
        "he_so_ram_tren_dxf": None, "ram_python_mb": None,
        "ram_nhieu_boi_tracemalloc": bool(dung_tracemalloc),
        "loi": None, "loi_buoc": None,
    }
    dxf_path = path
    try:
        if rec["ext"] in CAT_DWG:
            rec["loi_buoc"] = "convert"
            import dwgconv
            if not dwgconv.oda_available():
                rec["loi"] = ("Chua co ODA File Converter -> khong doc duoc .dwg. "
                              "Dat bien moi truong ODA_EXE tro toi ODAFileConverter.exe.")
                return rec
            os.makedirs(dxf_out, exist_ok=True)
            cached = os.path.join(dxf_out, os.path.splitext(os.path.basename(path))[0] + ".dxf")
            if os.path.isfile(cached) and os.path.getmtime(cached) >= os.path.getmtime(path):
                dxf_path, rec["convert_cache"] = cached, True   # dùng lại, khỏi convert 600s
            else:
                t0 = time.time()
                dxf_path = dwgconv.convert_dwg_to_dxf(path, dxf_out)
                rec["convert_s"] = round(time.time() - t0, 1)
        rec["dxf_mb"] = _mb(dxf_path)
        rec["dxf_path"] = dxf_path

        rec["loi_buoc"] = "load"
        import tools_core as tc                       # import TRƯỚC khi chốt baseline (matplotlib+ezdxf ~67MB cố định)
        tm = None
        if dung_tracemalloc:
            import tracemalloc as tm
            tm.start()
        rec["ram_baseline_mb"] = _peak_rss_mb()       # nền: interpreter + import, CHƯA nạp bản vẽ
        t0 = time.time()
        d = tc.Drawing(dxf_path)
        rec["load_s"] = round(time.time() - t0, 1)
        if tm is not None:
            rec["ram_python_mb"] = round(tm.get_traced_memory()[1] / 1048576.0, 1)
            tm.stop()
        rec["ram_peak_mb"] = _peak_rss_mb()
        if rec["ram_peak_mb"] is not None and rec["ram_baseline_mb"] is not None:
            # DELTA = giá RAM THỰC của riêng bản vẽ này. Ngoại suy phải dùng delta, KHÔNG dùng peak/dxf:
            # peak gồm baseline cố định nên peak/dxf phồng giả ở file nhỏ (25MB -> 'x20' trong khi biên chỉ x6.9).
            rec["ram_delta_mb"] = round(rec["ram_peak_mb"] - rec["ram_baseline_mb"], 1)
            rec["he_so_ram_tren_dxf"] = _ty_le(rec["ram_delta_mb"], rec["dxf_mb"])

        rec["loi_buoc"] = "doc"
        uniq = {(t.get("vn") or "").strip().lower() for t in d.texts}
        uniq.discard("")
        qty_nguon = Counter(e.get("nguon") for e in d.qty_index)
        rec.update({
            "dxfversion": d.dxfversion, "tong_doi_tuong": d.total,
            "so_layer": len(d.layers), "so_text": len(d.texts), "so_text_duy_nhat": len(uniq),
            "so_block": len(d.blocks), "so_dim": len(d.dims), "so_sheet": len(d.sheets),
            "qty_so_muc": len(d.qty_index),
            "qty_theo_nguon": dict(qty_nguon),
            "co_bang_thong_ke": bool(qty_nguon.get("bảng thống kê (cột TỔNG)", 0)),
            "so_section_index": len(getattr(d, "section_index", {}) or {}),
            "so_door_size_index": len(getattr(d, "door_size_index", {}) or {}),
            "so_stated_vol": len(getattr(d, "stated_vol", []) or []),
            "so_stated_area": len(getattr(d, "stated_area", []) or []),
            "thep_kg": (d.thep or {}).get("tong_kg"),
            "thep_hinh_kg": (d.thep_hinh or {}).get("tong_kg"),
        })
        try:
            rec["so_residual"] = len(d._residual_texts())   # tín hiệu GAP recall (text chưa bộ nào hiểu)
        except Exception as e:
            rec["so_residual"] = None
            rec["canh_bao_residual"] = str(e)[:200]

        rec["loi_buoc"] = "cao_do"
        cd = d.cao_do_min_max()
        tn = cd.get("thap_nhat") or {}
        vals = cd.get("tat_ca_cao_do_m") or []
        # GAP tới giá trị kế tiếp = bằng chứng "extreme CÔ LẬP". Mốc sâu THẬT thường có mốc khác gần
        # (đáy đài/đáy lót); rác thì đứng một mình cách cả chục mét. Ghi lại để NGƯỜI phán, tool không tự loại.
        rec["cao_do"] = {
            "co_cao_do": cd.get("co_cao_do"), "so_marker": cd.get("so_marker"),
            "thap_nhat_m": cd.get("cao_do_thap_nhat_m"), "cao_nhat_m": cd.get("cao_do_cao_nhat_m"),
            "thap_nhat_handle": tn.get("handle"), "thap_nhat_nguyen_van": tn.get("nguyen_van"),
            "thap_nhat_layer": tn.get("layer"), "thap_nhat_dang": tn.get("dang"),
            "thap_nhat_nghi_ngo": tn.get("nghi_ngo"),
            "cao_nhat_nghi_ngo": (cd.get("cao_nhat") or {}).get("nghi_ngo"),
            "cao_do_ke_tiep_m": vals[1] if len(vals) >= 2 else None,
            "gap_toi_ke_tiep_m": round(vals[1] - vals[0], 3) if len(vals) >= 2 else None,
            "so_canh_bao": len(cd.get("canh_bao") or []),
        }
        rec["loi_buoc"] = None
    except MemoryError:
        rec["loi"] = "HET RAM khi doc file nay (MemoryError)."
    except Exception as e:
        rec["loi"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    return rec


# ---------------------------------------------------------------- PARENT
def _chay_child(path, dxf_out, max_mb, timeout, dung_tracemalloc=False):
    """Spawn tiến trình con khảo sát 1 file. Timeout/crash -> bản ghi lỗi (LỘ), KHÔNG ném lên."""
    cmd = [sys.executable, os.path.abspath(__file__), "--_child", path,
           "--dxf-out", dxf_out, "--_max-mb", str(max_mb)]
    if dung_tracemalloc:
        cmd.append("--tracemalloc")
    base = {"duong_dan": path, "ten_file": os.path.basename(path),
            "ext": os.path.splitext(path)[1].lower(), "raw_mb": _mb(path)}
    try:
        p = subprocess.run(cmd, timeout=timeout, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, cwd=ROOT_PKG)
    except subprocess.TimeoutExpired:
        base["loi"] = "TIMEOUT > %ss (file qua lon/phuc tap, hoac ODA treo)." % timeout
        return base
    out = (p.stdout or b"").decode("utf-8", "replace")
    if MARK in out:
        try:
            return json.loads(out.split(MARK, 1)[1].strip())
        except Exception as e:
            base["loi"] = "Khong doc duoc JSON tu tien trinh con: %s" % e
            return base
    err = (p.stderr or b"").decode("utf-8", "replace").strip()
    base["loi"] = ("Tien trinh con CHET (rc=%s) — nhieu kha nang OOM/crash native. %s"
                   % (p.returncode, ("stderr: " + err[-300:]) if err else "(khong co stderr)"))
    return base


def _tong_hop_nhom(files):
    """Gộp theo nhóm thư mục. Chỉ cộng cái ĐO được; file lỗi đếm riêng (không giấu)."""
    ra = {}
    for r in files:
        g = ra.setdefault(r["_nhom"], {
            "so_file": 0, "so_file_loi": 0, "raw_mb": 0.0, "dxf_mb": 0.0,
            "ram_peak_max_mb": None, "co_bang_thong_ke": False,
            "qty_so_muc": 0, "so_text": 0, "so_layer_max": 0, "cao_do_thap_nhat_m": None,
        })
        g["so_file"] += 1
        if r.get("loi"):
            g["so_file_loi"] += 1
            continue
        g["raw_mb"] = round(g["raw_mb"] + (r.get("raw_mb") or 0), 2)
        g["dxf_mb"] = round(g["dxf_mb"] + (r.get("dxf_mb") or 0), 2)
        if r.get("ram_peak_mb") is not None:
            g["ram_peak_max_mb"] = max(g["ram_peak_max_mb"] or 0, r["ram_peak_mb"])
        g["co_bang_thong_ke"] = g["co_bang_thong_ke"] or bool(r.get("co_bang_thong_ke"))
        g["qty_so_muc"] += r.get("qty_so_muc") or 0
        g["so_text"] += r.get("so_text") or 0
        g["so_layer_max"] = max(g["so_layer_max"], r.get("so_layer") or 0)
        tn = (r.get("cao_do") or {}).get("thap_nhat_m")
        if tn is not None:
            g["cao_do_thap_nhat_m"] = tn if g["cao_do_thap_nhat_m"] is None else min(g["cao_do_thap_nhat_m"], tn)
    return ra


def _gan_nguong(r):
    """Đối chiếu ngưỡng SẢN XUẤT. Guard chặn theo raw TRƯỚC convert, rồi theo dxf sau convert (Robustness I)."""
    if r.get("loi"):
        return r
    kt = [x for x in (r.get("raw_mb"), r.get("dxf_mb")) if x is not None]
    lon_nhat = max(kt) if kt else None
    r["render_free_doc_duoc"] = (lon_nhat is not None and lon_nhat <= NGUONG["render_free_doc_mb"])
    r["render_standard_doc_duoc"] = (lon_nhat is not None and lon_nhat <= NGUONG["render_standard_doc_mb"])
    ram = r.get("ram_peak_mb")
    r["ram_vuot_free_512"] = (ram is not None and ram > NGUONG["ram_free_mb"])
    r["ram_vuot_standard_2048"] = (ram is not None and ram > NGUONG["ram_standard_mb"])
    return r


def khao_sat(root, dxf_out, loai_tru, max_mb, timeout, gioi_han=0, dung_tracemalloc=False):
    """Khảo sát toàn corpus. Trả (report_dict). KHÔNG ném khi 1 file lỗi (fail-soft, lỗi được LỘ)."""
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        raise RuntimeError("Khong tim thay thu muc corpus: %s" % root)
    paths = liet_ke_ban_ve(root, loai_tru)
    if gioi_han:
        paths = paths[:gioi_han]
    try:
        import dwgconv
        oda = dwgconv.find_oda()
    except Exception:
        oda = None

    files = []
    for i, p in enumerate(paths, 1):
        nhom = _nhom_of(p, root)
        print("  [%d/%d] %s / %s ..." % (i, len(paths), nhom, os.path.basename(p)), flush=True)
        out_dir = os.path.join(dxf_out, nhom)
        r = _chay_child(p, out_dir, max_mb, timeout, dung_tracemalloc)
        r["_nhom"] = nhom
        files.append(_gan_nguong(r))
        if r.get("loi"):
            print("        !! LOI: %s" % r["loi"], flush=True)
        else:
            print("        raw=%sMB dxf=%sMB RAM=%sMB(+%s) layer=%s text=%s qty=%s%s"
                  % (r.get("raw_mb"), r.get("dxf_mb"), r.get("ram_peak_mb"), r.get("ram_delta_mb"),
                     r.get("so_layer"), r.get("so_text"), r.get("qty_so_muc"),
                     " BANG-TK" if r.get("co_bang_thong_ke") else ""), flush=True)

    return {
        "meta": {
            "root": root, "thoi_diem": time.strftime("%Y-%m-%d %H:%M:%S"),
            "so_file": len(files), "so_file_loi": sum(1 for r in files if r.get("loi")),
            "so_nhom": len({r["_nhom"] for r in files}),
            "oda": oda, "platform": sys.platform, "cach_do_ram": _cach_do_ram(),
            "loai_tru": list(loai_tru), "read_max_mb_khi_khao_sat": max_mb,
        },
        "nguong": NGUONG,
        "files": files,
        "theo_nhom": _tong_hop_nhom(files),
    }


def in_bao_cao(rep):
    """In tóm tắt người đọc được. Lỗi in TRƯỚC (thất bại phải lộ, không chôn cuối)."""
    m, nh = rep["meta"], rep["theo_nhom"]
    print("\n" + "=" * 78)
    print("KHAO SAT CORPUS — %s" % m["thoi_diem"])
    print("  root       : %s" % m["root"])
    print("  ODA        : %s" % (m["oda"] or "KHONG CO (khong doc duoc .dwg)"))
    print("  do RAM     : %s" % m["cach_do_ram"])
    print("  file/nhom  : %d file / %d nhom thu muc   (LOI: %d)" % (m["so_file"], m["so_nhom"], m["so_file_loi"]))
    print("=" * 78)

    loi = [r for r in rep["files"] if r.get("loi")]
    if loi:
        print("\n!! %d FILE LOI — KHONG doc duoc (thay vi giau, liet ke ro):" % len(loi))
        for r in loi:
            print("   - %s / %s\n       %s" % (r.get("_nhom"), r["ten_file"], r["loi"]))

    print("\n--- THEO NHOM THU MUC (chu y: nhom != don vi thiet ke, can NGUOI xac nhan) ---")
    print("  %-34s %5s %8s %8s %8s %6s %s" % ("NHOM", "FILE", "RAW_MB", "DXF_MB", "RAM_MAX", "QTY", "BANG-TK"))
    for g, v in sorted(nh.items()):
        print("  %-34s %5s %8s %8s %8s %6s %s"
              % (g[:34], "%d%s" % (v["so_file"], ("(-%d)" % v["so_file_loi"]) if v["so_file_loi"] else ""),
                 v["raw_mb"], v["dxf_mb"], v["ram_peak_max_mb"], v["qty_so_muc"],
                 "CO" if v["co_bang_thong_ke"] else "-"))

    ok = [r for r in rep["files"] if not r.get("loi")]
    if ok:
        mat_ram = [r for r in ok if r.get("ram_peak_mb") is None]
        if mat_ram:
            print("\n!! KHONG DO DUOC RAM cho %d/%d file -> KHONG dung bao cao nay de chot goi Render."
                  % (len(mat_ram), len(ok)))
            print("   (RAM la rang buoc quyet dinh chi phi — thieu so do thi ket luan chiu tai VO NGHIA.)")

        print("\n--- CHIU TAI vs NGUONG SAN XUAT ---")
        n = rep["nguong"]
        free_no = [r for r in ok if not r.get("render_free_doc_duoc")]
        std_no = [r for r in ok if not r.get("render_standard_doc_duoc")]
        ram_no = [r for r in ok if r.get("ram_vuot_standard_2048")]
        print("  Render FREE (doc <=%dMB, RAM %dMB) : %d/%d file KHONG doc duoc"
              % (n["render_free_doc_mb"], n["ram_free_mb"], len(free_no), len(ok)))
        print("  Render STANDARD (doc <=%dMB, RAM %dMB): %d/%d file KHONG doc duoc"
              % (n["render_standard_doc_mb"], n["ram_standard_mb"], len(std_no), len(ok)))
        print("  Vuot RAM 2GB (ke ca Standard)        : %d file" % len(ram_no))
        for r in std_no:
            print("     - QUA LON cho Standard: %s (raw=%sMB dxf=%sMB)" % (r["ten_file"], r.get("raw_mb"), r.get("dxf_mb")))

        # Chỉ ngoại suy từ file ĐỦ LỚN — file nhỏ cho hệ số rác (baseline lấn át), in ra sẽ đánh lừa.
        du_lon = [r for r in ok if (r.get("dxf_mb") or 0) >= MIN_MB_HE_SO and r.get("he_so_ram_tren_dxf")]
        hs = [r["he_so_ram_tren_dxf"] for r in du_lon]
        bl = [r["ram_baseline_mb"] for r in ok if r.get("ram_baseline_mb") is not None]
        print("\n  MO HINH RAM (dung cai nay de ngoai suy, DUNG lay peak/dxf):")
        print("     RAM_dinh ~= BASELINE (%.0fMB: interpreter+matplotlib+ezdxf) + HE_SO x kich_thuoc_DXF"
              % (sum(bl) / len(bl) if bl else 0))
        if hs:
            print("     HE_SO bien: min=%.1fx max=%.1fx  (tu %d file >=%.0fMB; moc cu trong memory ghi ~5.8x)"
                  % (min(hs), max(hs), len(du_lon), MIN_MB_HE_SO))
            bo = len(ok) - len(du_lon)
            if bo:
                print("     (%d file <%.0fMB KHONG dua vao he so — RAM bi baseline/granularity lan at)" % (bo, MIN_MB_HE_SO))
        else:
            print("     CHUA du du lieu: 0 file >=%.0fMB -> KHONG ngoai suy duoc he so (thieu thi noi thieu)."
                  % MIN_MB_HE_SO)
        if any(r.get("ram_nhieu_boi_tracemalloc") for r in ok):
            print("     !! CO --tracemalloc: RSS PHONG ~2.1x -> KHONG dung so nay de chot goi Render.")
        print("  ⚠ Peak do o day = tien trinh CHI nap 1 ban ve. Production con: Flask/app + toi da")
        print("    MAX_SESSIONS ban ve song song trong RAM -> phai cong them truoc khi chot goi.")

        print("\n--- DOC DUOC GI (tin hieu OVERFIT: bo doc co an tren firm MOI khong) ---")
        print("  %-30s %7s %7s %6s %6s %7s %8s" % ("FILE", "LAYER", "TEXT", "QTY", "TIET-D", "BANG-TK", "RESIDUAL"))
        for r in ok:
            print("  %-30s %7s %7s %6s %6s %7s %8s"
                  % (r["ten_file"][:30], r.get("so_layer"), r.get("so_text"), r.get("qty_so_muc"),
                     r.get("so_section_index"), "CO" if r.get("co_bang_thong_ke") else "-",
                     r.get("so_residual")))

        print("\n--- UNG VIEN id135 (E2E-that: can file co MOC SAU, vd -14.26) ---")
        print("  %-30s %9s %9s %6s %9s %s" % ("FILE", "MIN", "MAX", "NGHI?", "KE-TIEP", "GAP"))
        uv = sorted([r for r in ok if (r.get("cao_do") or {}).get("thap_nhat_m") is not None],
                    key=lambda r: r["cao_do"]["thap_nhat_m"])
        if not uv:
            print("  (khong file nao doc duoc cao do)")
        for r in uv[:10]:
            cd = r["cao_do"]
            print("  %-30s %9s %9s %6s %9s %s"
                  % (r["ten_file"][:30], cd["thap_nhat_m"], cd["cao_nhat_m"],
                     "NGHI" if cd.get("thap_nhat_nghi_ngo") else "-",
                     cd.get("cao_do_ke_tiep_m"), cd.get("gap_toi_ke_tiep_m")))
        # MIN bị cờ nghi_ngo = ứng viên SAI-TỰ-TIN: tool vẫn trả nó làm câu trả lời chính.
        ng = [r for r in uv if (r.get("cao_do") or {}).get("thap_nhat_nghi_ngo")]
        if ng:
            print("\n  !! %d file co MIN bi co 'nghi_ngo' (extreme CO LAP/inline) — tool VAN dat lam" % len(ng))
            print("     cao_do_thap_nhat_m. Doi chieu thu cong TRUOC khi tin:")
            for r in ng:
                cd = r["cao_do"]
                print("       - %s: min=%s (gap %sm toi %s) layer=%r dang=%s"
                      % (r["ten_file"][:44], cd["thap_nhat_m"], cd.get("gap_toi_ke_tiep_m"),
                         cd.get("cao_do_ke_tiep_m"), cd.get("thap_nhat_layer"), cd.get("thap_nhat_dang")))
    print("")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Khao sat corpus ban ve doi tac (GD4/P5/id135).")
    ap.add_argument("--root", default=os.path.normpath(os.path.join(ROOT_PKG, "..", "input_files")))
    ap.add_argument("--dxf-out", default=os.path.normpath(os.path.join(ROOT_PKG, "_khao_sat", "_dxf")))
    ap.add_argument("--json", default=None, help="Duong dan bao cao JSON (mac dinh _khao_sat/bao_cao.json)")
    ap.add_argument("--loai-tru", default="_dxf,__pycache__,_uploads,_renders",
                    help="Ten thu muc BO QUA (phay). Mac dinh bo _dxf = cache convert cua corpus cu.")
    ap.add_argument("--timeout", type=int, default=1200, help="Giay toi da cho 1 file (ODA 600s + parse).")
    ap.add_argument("--max-mb", type=int, default=4000, help="READFILE_MAX_MB khi khao sat LOCAL (doc thoai mai).")
    ap.add_argument("--gioi-han", type=int, default=0, help="Chi khao sat N file dau (smoke).")
    ap.add_argument("--tracemalloc", action="store_true",
                    help="Do them RAM Python-heap. CANH BAO: lam RSS phong ~2.1x -> so chiu tai KHONG dung de chot goi Render.")
    # cờ nội bộ cho tiến trình con
    ap.add_argument("--_child", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--_max-mb", type=int, default=4000, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)

    if a._child:
        rec = _khao_sat_1_file(a._child, a.dxf_out, a._max_mb, a.tracemalloc)
        sys.stdout.write("\n" + MARK + "\n" + json.dumps(rec, ensure_ascii=False))
        sys.stdout.flush()
        return 0

    try:
        rep = khao_sat(a.root, a.dxf_out, [x.strip() for x in a.loai_tru.split(",") if x.strip()],
                       a.max_mb, a.timeout, a.gioi_han, a.tracemalloc)
    except RuntimeError as e:
        print("LOI: %s" % e)
        print("Goi y: chep cac thu muc ban ve doi tac vao %s roi chay lai." % a.root)
        return 1
    if not rep["files"]:
        print("LOI: khong tim thay file .dwg/.dxf nao duoi %s" % os.path.abspath(a.root))
        return 1

    in_bao_cao(rep)
    out = a.json or os.path.join(ROOT_PKG, "_khao_sat", "bao_cao.json")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print("Bao cao JSON -> %s" % out)
    if rep["meta"]["so_file_loi"]:
        print("CANH BAO: %d/%d file KHONG doc duoc (xem muc LOI o tren)."
              % (rep["meta"]["so_file_loi"], rep["meta"]["so_file"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
