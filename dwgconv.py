# -*- coding: utf-8 -*-
"""
dwgconv.py — Chuyen .dwg -> .dxf NGAY TREN SERVER bang ODA File Converter (CLI batch).

Chay duoc 2 noi voi cung mot code:
  * Windows (may local de test): goi thang ODAFileConverter.exe
  * Linux / Docker (cloud):       boc bang `xvfb-run -a` vi ODA la app Qt (can man hinh ao)

Cau hinh duong dan ODA:
  - Uu tien bien moi truong  ODA_EXE  (vd: D:\\Downloads\\ODAFileConverter.exe)
  - Neu khong co: tu do cac vi tri mac dinh theo he dieu hanh.

Quy uoc CLI cua ODA (che do batch, khong hien GUI lau):
  ODAFileConverter <inDir> <outDir> <version> <filetype> <recurse> <audit> [<filter>]
  vd: ODAFileConverter in out ACAD2018 DXF 0 0 *.DWG
"""
import os
import sys
import glob
import shutil
import tempfile
import subprocess

# Phien ban DXF dau ra: ACAD2018 (= AC1032) — dung dung cai da kiem chung.
OUT_VERSION = "ACAD2018"
CONVERT_TIMEOUT = 600  # giay; file lon (~100MB) co the lau

_WIN_CANDIDATES = [
    r"D:\Downloads\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter.exe",
]
_LINUX_CANDIDATES = [
    "/usr/bin/ODAFileConverter",
    "/usr/bin/ODAFileConverterApp",
    "/opt/ODAFileConverter/ODAFileConverter",
]


def find_oda():
    """Tra ve duong dan ODAFileConverter, hoac None neu khong tim thay."""
    env = os.environ.get("ODA_EXE")
    if env and os.path.isfile(env):
        return env
    if sys.platform.startswith("win"):
        cands = _WIN_CANDIDATES + glob.glob(
            r"C:\Program Files\ODA\*\ODAFileConverter.exe")
    else:
        cands = _LINUX_CANDIDATES
    for c in cands:
        if os.path.isfile(c):
            return c
    # tim trong PATH (Linux cai bang .deb se co trong /usr/bin)
    found = shutil.which("ODAFileConverter")
    return found


def oda_available():
    return find_oda() is not None


def convert_dwg_to_dxf(dwg_path, out_dir):
    """Chuyen 1 file .dwg -> .dxf. Tra ve duong dan .dxf trong out_dir.
    Nem RuntimeError voi thong bao tieng Viet de hien len giao dien."""
    exe = find_oda()
    if not exe:
        raise RuntimeError(
            "Server chua co ODA File Converter. (Local: dat bien ODA_EXE tro toi "
            "ODAFileConverter.exe; Cloud: cai trong Docker.)")
    if not os.path.isfile(dwg_path):
        raise RuntimeError("Khong tim thay file .dwg de chuyen doi.")

    work = tempfile.mkdtemp(prefix="oda_")
    in_dir = os.path.join(work, "in")
    tmp_out = os.path.join(work, "out")
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(tmp_out, exist_ok=True)
    base = os.path.basename(dwg_path)
    try:
        shutil.copy2(dwg_path, os.path.join(in_dir, base))
        cmd = [exe, in_dir, tmp_out, OUT_VERSION, "DXF", "0", "0", "*.DWG"]
        if not sys.platform.startswith("win"):
            # Linux: ODA la app Qt -> can man hinh ao
            cmd = ["xvfb-run", "-a", "--server-args=-screen 0 1024x768x24"] + cmd
        # ODA ghi config vao HOME -> dam bao co HOME ghi duoc (tren cloud chay root van OK,
        # nhung dat ro de chac chan). Bat ON font de tranh loi thieu font.
        env = dict(os.environ)
        env.setdefault("HOME", work)
        env.setdefault("XDG_RUNTIME_DIR", work)  # thu muc ghi duoc -> dep canh bao Qt headless
        proc_out = b""
        proc_rc = None
        try:
            proc = subprocess.run(cmd, timeout=CONVERT_TIMEOUT,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   env=env)
            proc_out = proc.stdout or b""
            proc_rc = proc.returncode
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "Chuyen doi .dwg qua lau (timeout). File co the qua lon/phuc tap.")
        except FileNotFoundError:
            raise RuntimeError(
                "Thieu 'xvfb-run' tren server (can cho ODA tren Linux).")

        outs = (glob.glob(os.path.join(tmp_out, "*.dxf"))
                + glob.glob(os.path.join(tmp_out, "*.DXF")))
        if not outs:
            tail = proc_out.decode("utf-8", "replace").strip()
            # Chi tiet ky thuat -> ghi vao log server (Render Logs) de chan doan,
            # KHONG lo cho nguoi dung cuoi (doi tac chi thay thong bao than thien).
            print("[dwgconv] ODA khong tao .dxf. rc=%s. Output ODA:\n%s"
                  % (proc_rc, tail or "(khong co)"), file=sys.stderr, flush=True)
            raise RuntimeError(
                "Khong doc duoc file .dwg nay (co the bi hong, bi khoa, hoac dinh dang "
                "khong ho tro). Hay thu file khac, hoac chuyen sang .dxf truoc khi tai len.")
        stem = os.path.splitext(base)[0] + ".dxf"
        final = os.path.join(out_dir, stem)
        os.makedirs(out_dir, exist_ok=True)
        if os.path.abspath(outs[0]) != os.path.abspath(final):
            shutil.copy2(outs[0], final)
        return final
    finally:
        shutil.rmtree(work, ignore_errors=True)
