# -*- coding: utf-8 -*-
"""Robustness J — DỌN FILE TTL. TẤT ĐỊNH, OFFLINE, KHÔNG tốn API (dùng os.utime lão hoá file, không chờ).
Chạy:  python tests/test_file_ttl.py"""
import os, sys, io, time, tempfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
from fileutil import cleanup_old_files

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _mk(path, age_min):
    with open(path, "wb") as fh:
        fh.write(b"x")
    t = time.time() - age_min * 60
    os.utime(path, (t, t))


def main():
    global PASS, FAIL
    tmp = tempfile.mkdtemp(prefix="fttl_")
    try:
        old1 = os.path.join(tmp, "old1.png"); _mk(old1, 120)          # 2h cũ  -> xoá
        old2 = os.path.join(tmp, "old2.xlsx"); _mk(old2, 90)          # 90' cũ -> xoá
        fresh = os.path.join(tmp, "fresh.png"); _mk(fresh, 5)         # 5' -> GIỮ
        keepold = os.path.join(tmp, "keepme.png"); _mk(keepold, 120)  # cũ nhưng trong keep -> GIỮ
        sub = os.path.join(tmp, "sub"); os.makedirs(sub)             # thư mục con -> KHÔNG đụng
        subf = os.path.join(sub, "x.png"); _mk(subf, 120)

        print("[J.1] xoá file cũ > TTL; GIỮ file mới + file keep + thư mục con")
        removed, errors = cleanup_old_files([tmp], 60, keep=[keepold])
        ok("removed=2 (old1+old2), errors=0", removed == 2 and errors == 0, (removed, errors))
        ok("old1 đã xoá", not os.path.exists(old1))
        ok("old2 đã xoá", not os.path.exists(old2))
        ok("fresh (5') GIỮ", os.path.exists(fresh))
        ok("keepme (cũ nhưng keep) GIỮ", os.path.exists(keepold))
        ok("thư mục con + file trong đó KHÔNG bị đụng (không đệ quy)", os.path.isdir(sub) and os.path.exists(subf))

        print("[J.2] ttl_min <= 0 -> KHÔNG dọn (cho phép TẮT qua env FILE_TTL_MIN=0)")
        veryold = os.path.join(tmp, "veryold.png"); _mk(veryold, 999)
        r0, e0 = cleanup_old_files([tmp], 0)
        ok("ttl=0 -> (0,0) + veryold còn nguyên", r0 == 0 and e0 == 0 and os.path.exists(veryold))

        print("[J.3] thư mục KHÔNG tồn tại -> không crash")
        r1, e1 = cleanup_old_files([os.path.join(tmp, "khong_co_dau")], 60)
        ok("dir vắng -> (0,0), không ném", r1 == 0 and e1 == 0)

        print("[J.4] nhiều dir cùng lúc: quét MỌI dir được truyền (không chỉ dir đầu)")
        d2 = os.path.join(tmp, "d2"); os.makedirs(d2)
        a_path = os.path.join(d2, "a.png"); _mk(a_path, 120)   # cũ -> xoá
        b_path = os.path.join(d2, "b.png"); _mk(b_path, 1)     # mới -> giữ
        rr, ee = cleanup_old_files([tmp, d2], 60)
        ok("a.png(d2, cũ) xoá + b.png(d2, mới) giữ + có quét (rr>=1)",
           (not os.path.exists(a_path)) and os.path.exists(b_path) and rr >= 1, (rr, ee))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("[J.5] hằng số FILE_TTL_MIN — int, app KHỚP tools_core (cùng env)")
    import app as A, tools_core as T
    ok("tools_core.FILE_TTL_MIN là int", isinstance(T.FILE_TTL_MIN, int))
    ok("app.FILE_TTL_MIN là int", isinstance(A.FILE_TTL_MIN, int))
    ok("app.FILE_TTL_MIN == tools_core.FILE_TTL_MIN", A.FILE_TTL_MIN == T.FILE_TTL_MIN, "%s vs %s" % (A.FILE_TTL_MIN, T.FILE_TTL_MIN))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
