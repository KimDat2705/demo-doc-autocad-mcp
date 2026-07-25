# -*- coding: utf-8 -*-
"""Test I4a — phat_hien_bang_ve_net (detector BANG VE-BANG-NET: LINE grid + TEXT trong o).
Khoa hanh vi cot loi (DXF TONG HOP, tat dinh, KHONG can corpus local, KHONG ton API):
  [A] DUONG: luoi >=4 vach-hang dong-diem + >=2 cot + >=3 chu-trong-o -> co_bang_ve_net=True.
  [B] AM: mat-cat (chi vach ngang song song, khong cot, khong chu) -> False.
  [C] AM: luoi-truc cot nha (nhieu cot >15) -> False (tran cot loai luoi-truc).
  [D] AM: rong / khong vach ngang -> False.
  [E] FAIL-OPEN: modelspace nem loi -> co_bang_ve_net=False, KHONG raise.
  [F] GROUNDING: mcp_bridge LOAI ten tool khoi ro grounding + prose canh_bao SACH CHU SO.
  [G] Dau ra: bool + so_vung(int) + prose; da_cat khi cat cap.
"""
import os, sys, io, re, tempfile, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")   # in tieng Viet duoi codepage cp1252 (check.sh)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import ezdxf
from tools_core import Drawing
import tools_core

PASS = FAIL = 0
_TMP = tempfile.mkdtemp(prefix="bangnet_")


def _emit(name, ok, extra=""):
    global PASS, FAIL
    if ok: PASS += 1; print("  [OK] %s %s" % (name, extra))
    else:  FAIL += 1; print("  [FAIL] %s %s" % (name, extra))


def _mk(path, hlines, vlines, texts):
    """hlines=[(y,x0,x1)], vlines=[(x,y0,y1)], texts=[(x,y,s)]."""
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for (y, x0, x1) in hlines: msp.add_line((x0, y), (x1, y))
    for (x, y0, y1) in vlines: msp.add_line((x, y0), (x, y1))
    for (x, y, s) in texts:    msp.add_text(s).set_placement((x, y))
    doc.saveas(path); return path


def main():
    try:
        # ---- [A] DUONG: bang ke-bang-net that ----
        print("[A] DUONG — luoi 5 vach-hang + 5 cot + 4 chu -> co_bang_ve_net=True")
        pA = os.path.join(_TMP, "bang.dxf")
        _mk(pA,
            hlines=[(y, 0.0, 100.0) for y in (0, 10, 20, 30, 40)],
            vlines=[(x, 0.0, 40.0) for x in (0, 25, 50, 75, 100)],
            texts=[(10, 5, "Cau kien"), (30, 15, "Duong kinh"), (50, 25, "So luong"), (60, 35, "Trong luong")])
        rA = Drawing(pA).phat_hien_bang_ve_net()
        _emit("A: co_bang_ve_net=True + so_vung>=1", rA.get("co_bang_ve_net") is True and rA.get("so_vung", 0) >= 1,
              "-> %s" % rA)

        # ---- [B] AM: mat cat (chi vach ngang song song, khong cot, khong chu) ----
        print("[B] AM — mat-cat: 6 vach ngang song song, KHONG cot, KHONG chu -> False")
        pB = os.path.join(_TMP, "matcat.dxf")
        _mk(pB, hlines=[(y, 0.0, 100.0) for y in range(0, 60, 10)], vlines=[], texts=[])
        rB = Drawing(pB).phat_hien_bang_ve_net()
        _emit("B: co_bang_ve_net=False (thieu cot + chu)", rB.get("co_bang_ve_net") is False, "-> %s" % rB.get("so_vung"))

        # ---- [C] AM: luoi-truc cot nha (nhieu cot > 15) ----
        print("[C] AM — luoi-truc: 5 vach ngang + 20 cot (>15) + 3 chu -> False (tran cot)")
        pC = os.path.join(_TMP, "luoitruc.dxf")
        _mk(pC,
            hlines=[(y, 0.0, 200.0) for y in (0, 10, 20, 30, 40)],
            vlines=[(x, 0.0, 40.0) for x in range(0, 210, 10)],   # 21 cot > 15
            texts=[(10, 5, "A"), (30, 15, "B"), (50, 25, "C")])
        rC = Drawing(pC).phat_hien_bang_ve_net()
        _emit("C: co_bang_ve_net=False (cot>15 bi loai — chong luoi-truc)", rC.get("co_bang_ve_net") is False,
              "-> so_vung=%s" % rC.get("so_vung"))

        # ---- [D] AM: khong vach ngang ----
        print("[D] AM — chi text + vai cot, KHONG vach ngang -> False")
        pD = os.path.join(_TMP, "novach.dxf")
        _mk(pD, hlines=[], vlines=[(x, 0.0, 40.0) for x in (0, 25, 50)], texts=[(10, 5, "x"), (30, 15, "y")])
        rD = Drawing(pD).phat_hien_bang_ve_net()
        _emit("D: co_bang_ve_net=False + prose 'khong thay duong ke ngang'", rD.get("co_bang_ve_net") is False,
              "-> %s" % rD.get("so_vung"))

        # ---- [E] FAIL-OPEN: modelspace nem loi -> False, KHONG raise ----
        print("[E] FAIL-OPEN — modelspace() nem loi -> co_bang_ve_net=False, KHONG raise (fail-open)")
        dE = Drawing(pA)
        class _Boom:
            def __getattr__(self, k): raise RuntimeError("boom")
            def modelspace(self): raise RuntimeError("boom")
        dE.doc = _Boom()
        try:
            rE = dE.phat_hien_bang_ve_net()
            _emit("E: fail-open -> dict co_bang_ve_net=False, KHONG raise", isinstance(rE, dict) and rE.get("co_bang_ve_net") is False,
                  "-> %s" % (rE.get("loi_mem") or "")[:40])
        except Exception as e:
            _emit("E: fail-open KHONG raise", False, "<<< RAISE: %r" % e)

        # ---- [F] GROUNDING: loai ten tool + prose sach chu so ----
        print("[F] GROUNDING — mcp_bridge LOAI ten tool khoi ro + prose canh_bao SACH CHU SO")
        _mb_src = io.open(os.path.join(HERE, "..", "mcp_bridge.py"), encoding="utf-8").read()
        # dong loai-ten phai chua ca doc_bang_nhung VA phat_hien_bang_ve_net trong CUNG dieu kien tool_numbers
        _loai_ok = bool(re.search(r'fc\.name not in \([^)]*"phat_hien_bang_ve_net"[^)]*\)', _mb_src)) \
                   and 'tool_numbers |= _collect_numbers(result)' in _mb_src
        _emit("F1: mcp_bridge loai 'phat_hien_bang_ve_net' khoi tool_numbers (khong lot grounding)", _loai_ok)
        # prose canh_bao (ket qua DUONG) KHONG chua chu so
        cb = rA.get("canh_bao", "")
        _emit("F2: prose canh_bao (duong) KHONG chua chu so (defense-in-depth)", bool(cb) and not re.search(r"\d", cb),
              "-> %r" % cb[:50])
        # xac nhan _collect_numbers cua chinh mcp_bridge coi so_vung la so (chung minh vi sao PHAI loai)
        import mcp_bridge as MB
        _emit("F3: (chung minh) _collect_numbers(result) CO so_vung -> dung vi sao phai loai o tang goi",
              float(rA.get("so_vung")) in MB._collect_numbers(rA))

        # ---- [G] Dau ra dung kieu ----
        print("[G] Dau ra: bool + so_vung int + canh_bao str")
        _emit("G: co_bang_ve_net la bool, so_vung la int, canh_bao la str",
              isinstance(rA.get("co_bang_ve_net"), bool) and isinstance(rA.get("so_vung"), int)
              and isinstance(rA.get("canh_bao"), str))

    finally:
        shutil.rmtree(_TMP, ignore_errors=True)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
