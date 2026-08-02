# -*- coding: utf-8 -*-
"""KHOÁ nhánh ODA của dwgconv — TẤT ĐỊNH, KHÔNG cần cài ODA, KHÔNG mạng, KHÔNG API.
Chạy:  python tests/test_dwgconv.py

Mock/monkeypatch os.path.isfile / glob.glob / shutil.which / os.environ để tất định,
KHÔNG phụ thuộc máy có ODA hay không. Kiểm:
  A. find_oda() khi KHÔNG có ODA (không env, không candidate, không PATH) -> None, KHÔNG crash.
  B. find_oda() ưu tiên biến môi trường ODA_EXE khi trỏ tới file THẬT (tồn tại) -> trả đúng path.
  C. find_oda() với ODA_EXE trỏ tới đường dẫn KHÔNG tồn tại -> bỏ qua env, không có nguồn khác -> None.
  D. oda_available() phản ánh đúng find_oda().
  E. convert_dwg_to_dxf() khi KHÔNG có ODA -> NÉM RuntimeError CÓ NGHĨA (lộ 'ODA File Converter'),
     không lỗi mơ hồ, không crash kiểu khác.
  F. convert_dwg_to_dxf() khi CÓ ODA nhưng file .dwg không tồn tại -> RuntimeError lộ 'file .dwg'.
"""
import os, sys, io, glob, shutil, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import dwgconv

PASS = FAIL = 0


def _emit(name, ok, extra=""):
    global PASS, FAIL
    okk = bool(ok)
    PASS += int(okk)
    FAIL += int(not okk)
    print("  [%s] %s%s" % ("OK" if okk else "FAIL", name, (" " + extra) if extra else ""))


class _Patch:
    """Monkeypatch tất định các nguồn tìm ODA trong module dwgconv (khôi phục khi thoát)."""
    def __init__(self, isfile=None, which=None, glob_ret=None):
        self.isfile = isfile
        self.which = which
        self.glob_ret = glob_ret
        self._saved = {}

    def __enter__(self):
        self._saved["isfile"] = dwgconv.os.path.isfile
        self._saved["which"] = dwgconv.shutil.which
        self._saved["glob"] = dwgconv.glob.glob
        if self.isfile is not None:
            dwgconv.os.path.isfile = self.isfile
        if self.which is not None:
            dwgconv.shutil.which = self.which
        if self.glob_ret is not None:
            dwgconv.glob.glob = lambda *a, **k: list(self.glob_ret)
        return self

    def __exit__(self, *exc):
        dwgconv.os.path.isfile = self._saved["isfile"]
        dwgconv.shutil.which = self._saved["which"]
        dwgconv.glob.glob = self._saved["glob"]
        return False


def _clear_env():
    return dwgconv.os.environ.pop("ODA_EXE", None)


def main():
    global PASS, FAIL

    print("[A] find_oda() KHI KHÔNG CÓ ODA -> None (không env, không candidate, không PATH)")
    saved_env = _clear_env()
    try:
        with _Patch(isfile=lambda p: False, which=lambda n: None, glob_ret=[]):
            r = dwgconv.find_oda()
            _emit("find_oda() -> None khi không có nguồn nào", r is None, "-> %r" % r)
            _emit("oda_available() -> False", dwgconv.oda_available() is False)
    finally:
        if saved_env is not None:
            dwgconv.os.environ["ODA_EXE"] = saved_env

    print("[B] find_oda() ƯU TIÊN env ODA_EXE khi trỏ file THẬT (tồn tại)")
    tf = tempfile.NamedTemporaryFile(prefix="fake_oda_", suffix=".exe", delete=False)
    tf.close()
    fake_exe = tf.name
    saved_env = dwgconv.os.environ.get("ODA_EXE")
    try:
        dwgconv.os.environ["ODA_EXE"] = fake_exe
        # isfile THẬT (không patch) -> env trỏ file tồn tại -> trả về chính nó
        r = dwgconv.find_oda()
        _emit("find_oda() trả đúng ODA_EXE khi file tồn tại", r == fake_exe, "-> %r" % r)
        _emit("oda_available() -> True khi env hợp lệ", dwgconv.oda_available() is True)
    finally:
        if saved_env is None:
            dwgconv.os.environ.pop("ODA_EXE", None)
        else:
            dwgconv.os.environ["ODA_EXE"] = saved_env
        os.remove(fake_exe)

    print("[C] find_oda() với ODA_EXE TRỎ ĐƯỜNG DẪN KHÔNG TỒN TẠI -> bỏ qua env -> None")
    saved_env = dwgconv.os.environ.get("ODA_EXE")
    bogus = os.path.join(tempfile.gettempdir(), "khong_ton_tai_oda_xyz.exe")
    try:
        dwgconv.os.environ["ODA_EXE"] = bogus
        # isfile=False cho mọi thứ (kể cả env bogus), glob rỗng, which None -> None
        with _Patch(isfile=lambda p: False, which=lambda n: None, glob_ret=[]):
            r = dwgconv.find_oda()
            _emit("env trỏ path không tồn tại + không nguồn khác -> None", r is None, "-> %r" % r)
    finally:
        if saved_env is None:
            dwgconv.os.environ.pop("ODA_EXE", None)
        else:
            dwgconv.os.environ["ODA_EXE"] = saved_env

    print("[D] find_oda() TÌM ĐƯỢC qua PATH (shutil.which) khi env/candidate vắng")
    saved_env = _clear_env()
    try:
        with _Patch(isfile=lambda p: False, which=lambda n: "/usr/bin/ODAFileConverter", glob_ret=[]):
            r = dwgconv.find_oda()
            _emit("find_oda() dùng which() khi có trong PATH", r == "/usr/bin/ODAFileConverter", "-> %r" % r)
    finally:
        if saved_env is not None:
            dwgconv.os.environ["ODA_EXE"] = saved_env

    print("[E] convert_dwg_to_dxf() KHÔNG CÓ ODA -> RuntimeError CÓ NGHĨA (lộ 'ODA File Converter')")
    saved_find = dwgconv.find_oda
    try:
        dwgconv.find_oda = lambda: None
        threw = False
        msg = ""
        try:
            dwgconv.convert_dwg_to_dxf("bat_ky.dwg", tempfile.gettempdir())
        except RuntimeError as e:
            threw = True
            msg = str(e)
        except Exception as e:
            threw = False
            msg = "SAI LOẠI LỖI: %r" % e
        _emit("ném RuntimeError (không lỗi mơ hồ/crash khác)", threw, "-> %s" % msg[:60])
        _emit("thông báo LỘ 'ODA File Converter' (có nghĩa cho người dùng)",
              threw and "ODA File Converter" in msg)
    finally:
        dwgconv.find_oda = saved_find

    print("[F] convert_dwg_to_dxf() CÓ ODA nhưng file .dwg vắng -> RuntimeError lộ 'file .dwg'")
    saved_find = dwgconv.find_oda
    try:
        # giả có ODA (find_oda trả path bất kỳ) nhưng dwg_path không tồn tại -> báo lỗi rõ ràng
        dwgconv.find_oda = lambda: "/fake/ODAFileConverter"
        missing_dwg = os.path.join(tempfile.gettempdir(), "khong_co_that_12345.dwg")
        threw = False
        msg = ""
        try:
            dwgconv.convert_dwg_to_dxf(missing_dwg, tempfile.gettempdir())
        except RuntimeError as e:
            threw = True
            msg = str(e)
        except Exception as e:
            threw = False
            msg = "SAI LOẠI LỖI: %r" % e
        _emit("ném RuntimeError khi .dwg vắng", threw, "-> %s" % msg[:60])
        _emit("thông báo LỘ 'file .dwg' (không mơ hồ)", threw and ".dwg" in msg)
    finally:
        dwgconv.find_oda = saved_find

    print("[G] cmd goi ODA phai co AUDIT=1 (tham so thu 7) — KHOA bang so do A/B 148 file")
    # VI SAO KHOA: audit=0 khien .dwg loi cau truc van sinh .dxf nhung CUT (thieu ENDSEC) =>
    # convert tra ve file HONG ma khong bao gi (that bai IM LANG). Do A/B toan bo 148 file .dwg:
    # cuu 10/147, hong them 0, 2 file lech DUY NHAT `tong_doi_tuong` (cao_do/chu/dim/thep giu nguyen).
    # Ai ha ve "0" phai do lai va sua ca nay CO Y THUC.
    saved_find = dwgconv.find_oda
    saved_run = dwgconv.subprocess.run
    bat = {}
    # PHAI la file .dwg CO THAT: convert_dwg_to_dxf() goi shutil.copy2() TRUOC subprocess.run,
    # mock os.path.isfile khong du (copy2 van ném FileNotFoundError -> khong bao gio bat duoc cmd).
    _tmpd = tempfile.mkdtemp(prefix="tG_")
    _dwg = os.path.join(_tmpd, "x.dwg")
    with open(_dwg, "wb") as _fh:
        _fh.write(b"\x00")

    class _FakeProc(object):
        stdout = b""
        returncode = 0

    def _fake_run(cmd, **kw):
        bat["cmd"] = list(cmd)
        return _FakeProc()

    try:
        dwgconv.find_oda = lambda: "/fake/ODAFileConverter"
        dwgconv.subprocess.run = _fake_run
        try:
            # ODA gia khong sinh .dxf -> ham nem RuntimeError; ta chi can BAT duoc cmd
            dwgconv.convert_dwg_to_dxf(_dwg, tempfile.gettempdir())
        except Exception:
            pass
        cmd = bat.get("cmd") or []
        # bo tien to xvfb-run tren Linux de lay dung phan cmd cua ODA
        if "xvfb-run" in cmd:
            cmd = cmd[cmd.index("/fake/ODAFileConverter"):] if "/fake/ODAFileConverter" in cmd else cmd
        _emit("bat duoc cmd goi ODA", len(cmd) >= 8, "-> %d phan tu" % len(cmd))
        _emit("tham so RECURSE (thu 6) = '0' (chi 1 file, khong de quy)",
              len(cmd) >= 8 and cmd[5] == "0", "-> %r" % (cmd[5] if len(cmd) >= 8 else None))
        _emit("tham so AUDIT (thu 7) = '1' (KHONG duoc ha ve '0')",
              len(cmd) >= 8 and cmd[6] == "1", "-> %r" % (cmd[6] if len(cmd) >= 8 else None))
    finally:
        dwgconv.find_oda = saved_find
        dwgconv.subprocess.run = saved_run
        shutil.rmtree(_tmpd, ignore_errors=True)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
