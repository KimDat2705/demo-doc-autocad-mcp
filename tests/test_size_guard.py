# -*- coding: utf-8 -*-
"""Robustness I — CHẶN FILE LỚN SỚM (trước convert/parse). TẤT ĐỊNH, OFFLINE, KHÔNG tốn API.
Chạy:  python tests/test_size_guard.py
Kiểm: raw > READFILE_MAX_MB -> RuntimeError NGAY (trước ezdxf.readfile, kể cả file rác); dưới ngưỡng -> nạp
được; app.py /upload trả 413 + DỌN file khi vượt (khỏi gọi MCP)."""
import os, sys, io, tempfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import tools_core

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _is_size_err(msg):
    return "giới hạn" in msg or "quá lớn" in msg


def main():
    global PASS, FAIL
    tmp = tempfile.mkdtemp(prefix="sizeguard_")
    try:
        import ezdxf
        small_dxf = os.path.join(tmp, "small.dxf"); ezdxf.new().saveas(small_dxf)   # DXF hợp lệ nhỏ
        junk = os.path.join(tmp, "junk.dxf")
        with open(junk, "wb") as fh: fh.write(b"x" * 200000)                        # 200KB rác (KHÔNG phải DXF)

        _save = tools_core.READFILE_MAX_MB
        try:
            print("[I.1] file RÁC raw > READFILE_MAX_MB -> RuntimeError size NGAY (chặn TRƯỚC parse ezdxf)")
            tools_core.READFILE_MAX_MB = 0.05      # 50KB
            msg = ""
            try:
                tools_core.Drawing(junk)           # 200KB > 50KB -> phải chặn trước khi ezdxf đọc file rác
            except Exception as e:
                msg = str(e)
            ok("RuntimeError SIZE (không phải lỗi parse ezdxf)", _is_size_err(msg), msg[:90])

            print("[I.2] DXF HỢP LỆ raw > limit -> vẫn bị chặn size (dù đọc được)")
            sdxf_mb = os.path.getsize(small_dxf) / (1024 * 1024)
            tools_core.READFILE_MAX_MB = sdxf_mb * 0.5   # ngưỡng DƯỚI size thật -> chắc chắn vượt
            msg = ""
            try:
                tools_core.Drawing(small_dxf)
            except Exception as e:
                msg = str(e)
            ok("DXF hợp lệ (~%.0fKB) > ngưỡng -> chặn size" % (sdxf_mb * 1024), _is_size_err(msg), msg[:90])

            print("[I.3] raw <= limit -> KHÔNG chặn size (nạp bình thường)")
            tools_core.READFILE_MAX_MB = 999
            no_size_block = False
            try:
                d = tools_core.Drawing(small_dxf)
                no_size_block = d is not None
            except Exception as e:
                no_size_block = not _is_size_err(str(e))   # lỗi KHÁC size -> vẫn coi 'size không chặn'
            ok("small.dxf dưới ngưỡng -> KHÔNG lỗi size", no_size_block)
        finally:
            tools_core.READFILE_MAX_MB = _save

        print("[I.4] app.py /upload: vượt giới hạn -> HTTP 413 + DỌN file (KHÔNG gọi MCP/convert)")
        import app as A
        _asave = A.READFILE_MAX_MB
        A.READFILE_MAX_MB = 0.0001            # ~100 bytes -> mọi file thật đều vượt
        try:
            c = A.app.test_client()
            fname = "sizeguard_tmp.dxf"
            resp = c.post("/upload", data={"file": (io.BytesIO(b"y" * 5000), fname)},
                          content_type="multipart/form-data")
            ok("HTTP 413 (payload too large)", resp.status_code == 413, resp.status_code)
            j = resp.get_json() or {}
            ok("thông báo lỗi nêu 'giới hạn'", "giới hạn" in (j.get("error") or ""), j)
            ok("file đã bị DỌN (không để rác trong _uploads)", not os.path.isfile(os.path.join(A.UPLOAD_DIR, fname)))
        finally:
            A.READFILE_MAX_MB = _asave

        print("[I.5] hằng số giới hạn — int, đọc env; app KHỚP tools_core")
        ok("tools_core.READFILE_MAX_MB là int", isinstance(tools_core.READFILE_MAX_MB, int))
        import app as A2
        ok("app.READFILE_MAX_MB là int", isinstance(A2.READFILE_MAX_MB, int))
        ok("app.READFILE_MAX_MB == tools_core.READFILE_MAX_MB (cùng env, không lệch)",
           A2.READFILE_MAX_MB == tools_core.READFILE_MAX_MB, "%s vs %s" % (A2.READFILE_MAX_MB, tools_core.READFILE_MAX_MB))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
