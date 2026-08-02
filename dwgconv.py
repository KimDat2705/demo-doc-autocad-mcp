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
  vd: ODAFileConverter in out ACAD2018 DXF 0 1 *.DWG
  ⚠ audit PHAI = 1: voi audit=0, .dwg co loi cau truc van sinh ra .dxf nhung CUT (thieu ENDSEC)
    => tra ve file hong MA KHONG BAO GI. Do A/B 148 file: cuu 10, hong them 0. Xem chu thich
    tai cho dat `cmd` trong convert_dwg_to_dxf() de biet day du so do va gia phai tra.
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
        # Tham so 7 = AUDIT. TRUOC la "0" -> voi .dwg co loi cau truc, ODA VAN sinh ra file .dxf
        # nhung CUT (thieu ENDSEC) => `outs` khong rong => ham nay tra ve file hong MA KHONG BAO GI,
        # nguoi dung chi thay loi kho hieu o tang tren. Do A/B TOAN BO 148 file .dwg
        # (92 corpus + 56 bo doi tac 2026-08-02), cung thu muc nguon, chi doi audit 0->1:
        #   CUU 10/147 file (6,8%) tu "khong doc duoc" -> doc duoc; HONG THEM 0
        #   123 file ca hai deu doc duoc: 121 file SO Y HET; 2 file lech DUY NHAT `tong_doi_tuong`
        #     (8531->8530 va 10701->10672) — cao_do/so_doan_chu/so_kich_thuoc/thep_tong_kg/
        #     so_marker_cd GIU NGUYEN het => audit chi bo doi tuong HONG, khong mat du lieu co nghia.
        #   14 file ca hai deu loi: TAT CA do tran 45MB cua chinh du an, khong lien quan convert.
        # Gia phai tra (do): +27,5% thoi gian tong (252,7s -> 322,2s cho 147 file = +0,47s/file);
        # file 36,33MB (lon nhat duoi tran 45MB): 24,3s -> 30,4s, con xa CONVERT_TIMEOUT=600s;
        # dxf dau ra CUNG kich thuoc 202,4MB => audit KHONG phinh file lanh.
        # Trong 10 file duoc cuu co `chinhcaodo.dwg` cua BO TB6 (988 doan chu, 200 marker cao do)
        # — corpus khong co ban .dxf cua no nen bug nay chua bao gio lo ra trong luc dev
        # (dev luon lam viec tren .dxf co san, KHONG di qua duong nay; chi upload .dwg moi di).
        cmd = [exe, in_dir, tmp_out, OUT_VERSION, "DXF", "0", "1", "*.DWG"]
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
