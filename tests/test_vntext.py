# -*- coding: utf-8 -*-
"""KHOA vntext.to_unicode — TAT DINH, KHONG goi Gemini/mang, KHONG fixture.
Chay:  python tests/test_vntext.py

Kiem theo tinh than chong-bia:
  A. MA AUTOCAD:  %%C->O-gach (duong kinh), %%D->do, %%P->cong-tru; gach chan/tren/giua bi bo.
  B. TCVN3 -> Unicode dung theo BANG MA THAT (khong bia cap input->output).
  C. GIU NGUYEN text da la Unicode dung ('BE TONG' co dau) — chong 'sua nham' chu da dung.
  D. RONG/None an toan (khong crash).
  E. _looks_tcvn3 — dau hieu font cu ben-garble: co ky tu SIG -> giai ma; khong co -> de nguyen.
Moi cap input->output doc TRUC TIEP tu bang ma _TCVN3 / logic vntext, KHONG bia."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import vntext

PASS = FAIL = 0


def _emit(name, ok, extra=""):
    global PASS, FAIL
    okk = bool(ok)
    PASS += int(okk)
    FAIL += int(not okk)
    print("  [%s] %s%s" % ("OK" if okk else "FAIL", name, (" " + extra) if extra else ""))


# Ky tu Unicode dich (dung ord de tat dinh, khong phu thuoc hien thi terminal)
DIAM = "Ø"   # O co gach — ky hieu duong kinh (%%C)
DEG = "°"    # do (%%D)
PM = "±"     # cong-tru (%%P)


def main():
    print("[A] MA AUTOCAD — %%C/%%D/%%P + gach chan/tren/giua")
    _emit("%%C16 -> duong kinh + so nguyen", vntext.to_unicode("%%C16") == DIAM + "16",
          "-> %r" % vntext.to_unicode("%%C16"))
    _emit("%%c16 (thuong) cung -> duong kinh", vntext.to_unicode("%%c16") == DIAM + "16")
    _emit("%%D -> do", vntext.to_unicode("%%D") == DEG)
    _emit("%%d (thuong) -> do", vntext.to_unicode("%%d") == DEG)
    _emit("%%P -> cong-tru", vntext.to_unicode("%%P") == PM)
    _emit("%%p (thuong) -> cong-tru", vntext.to_unicode("%%p") == PM)
    _emit("gach chan %%U..%%U bi bo, giu chu", vntext.to_unicode("%%Utext%%U") == "text")
    _emit("gach tren %%O va giua %%K bi bo", vntext.to_unicode("%%Oa%%Kb") == "ab")
    _emit("%%%% -> mot dau %%", vntext.to_unicode("50%%%") == "50%")
    _emit("phoi hop %%C va %%D trong 1 chuoi",
          vntext.to_unicode("%%C20 goc %%D45") == DIAM + "20 goc " + DEG + "45")

    print("[B] TCVN3 -> Unicode (cap input->output doc tu bang ma _TCVN3)")
    # chr(0xB5)='µ' la ky tu SIG (font cu) VA map -> 'à' theo bang. Xay tu goc, khong bia.
    _emit("chr(0xB5) -> a-huyen (a\\u0300)", vntext.to_unicode(chr(0xB5)) == "à",
          "-> %r" % vntext.to_unicode(chr(0xB5)))
    # 'S' + 0xB5 + 'n' -> 'Sàn' (chu 'san' — co dau hieu SIG nen giai ma)
    _emit("'S'+0xB5+'n' -> San (co dau)", vntext.to_unicode("S" + chr(0xB5) + "n") == "Sàn",
          "-> %r" % vntext.to_unicode("S" + chr(0xB5) + "n"))
    # _fix_case: tu VIET HOA toan bo ascii -> viet hoa luon ky tu co dau vua giai ma
    _emit("'S'+0xB5+'N' (viet hoa) -> SAN (a-huyen HOA)", vntext.to_unicode("S" + chr(0xB5) + "N") == "SÀN",
          "-> %r" % vntext.to_unicode("S" + chr(0xB5) + "N"))
    # Kiem TRUC TIEP _decode_tcvn3 tren vai byte then chot cua bang
    _emit("_decode 0xAE -> d-gach (đ)", vntext._decode_tcvn3(chr(0xAE)) == "đ")
    _emit("_decode 0xA7 -> D-gach HOA (Đ)", vntext._decode_tcvn3(chr(0xA7)) == "Đ")
    _emit("_decode 0xAA -> e-mu (ê)", vntext._decode_tcvn3(chr(0xAA)) == "ê")
    # Bang phai la anh xa 1-1 vao Unicode (khong trung gia tri -> khong nhap nhang giai ma)
    _emit("bang _TCVN3 khong co gia tri trung (anh xa 1-1)",
          len(set(vntext._TCVN3.values())) == len(vntext._TCVN3))

    print("[C] GIU NGUYEN Unicode dung — chong 'sua nham' chu da dung")
    _emit("'BE TONG' co dau giu NGUYEN (khong SIG -> khong giai ma)",
          vntext.to_unicode("BÊ TÔNG") == "BÊ TÔNG",
          "-> %r" % vntext.to_unicode("BÊ TÔNG"))
    _emit("ASCII thuong 'Cot C1' giu nguyen", vntext.to_unicode("Cot C1") == "Cot C1")
    _emit("ASCII 'BE TONG' (khong dau) giu nguyen", vntext.to_unicode("BE TONG") == "BE TONG")
    # chuan hoa khoang trang: nhieu space/tab -> 1 space (join(split))
    _emit("chuan hoa khoang trang thua -> 1 space",
          vntext.to_unicode("a   b\t c") == "a b c")

    print("[D] RONG / None AN TOAN (khong crash)")
    _emit("'' -> '' (khong crash)", vntext.to_unicode("") == "")
    _emit("None -> None (khong crash)", vntext.to_unicode(None) is None)

    print("[E] _looks_tcvn3 — dau hieu font cu BEN, khong bat nham")
    _emit("co 0xB5 (SIG) -> True (nhan dien font cu)", vntext._looks_tcvn3("x" + chr(0xB5)) is True)
    _emit("chu Unicode dung 'BE TONG' co dau -> False (KHONG giai ma nham)",
          vntext._looks_tcvn3("BÊ TÔNG") is False)
    _emit("ASCII thuan -> False", vntext._looks_tcvn3("Cot C1 abc") is False)
    # chr(0xC7)='Ç' co trong bang _TCVN3 nhung KHONG trong SIG -> mot minh KHONG kich giai ma
    # (tranh pha ky tu Latin hop le khong phai font cu) — dau hieu phai la ky tu 'hiem' rieng.
    _emit("0xC7 (co trong bang nhung khong SIG) -> False (dau hieu chon loc, khong vo bua)",
          vntext._looks_tcvn3(chr(0xC7)) is False)
    _emit("moi ky tu SIG deu nam trong khoang byte cao TCVN3 (>=0xA1)",
          all(ord(c) >= 0xA1 for c in vntext._SIG))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
