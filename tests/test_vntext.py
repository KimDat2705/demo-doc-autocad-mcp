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
import os, sys, io, unicodedata
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
    # ⚠ HOP DONG DOI 2026-07-31 (1.03) — SIET CHAT HON, khong phai noi long.
    # CU: dau hieu chi gom o TCVN3 hien ra KY HIEU Latin-1 (0xA1-0xBE). Hau qua do duoc tren
    # 86 file / 285.413 chuoi: 9.680 chuoi / 73 file van garble vi MOI o TCVN3 cua chung deu
    # nam 0xC6-0xFE ('diÖn tÝch', 'THÐP', 'cèt thÐp'). 12.608 luot ky tu thuoc 23 ky tu Latin
    # KHONG phai chu Viet — do corpus: 0 luot trung chu-Viet, 0 luot trung ky-hieu-ky-thuat.
    # MOI: them 23 ky tu do (tang 2), NHUNG van loai tru dut khoat vung nhap nhang.
    _emit("0xC7 'Ç' (chu Latin khong phai chu Viet) -> True (dau hieu tang 2)",
          vntext._looks_tcvn3(chr(0xC7)) is True)
    for cp, ten in ((0xD8, "Ø duong kinh thep"), (0xD7, "× nhan"), (0xF7, "÷ chia")):
        _emit("%s (0x%02X) KHONG duoc lam dau hieu — pha ky hieu ky thuat" % (ten, cp),
              chr(cp) not in vntext._SIG)
    for cp, ten in ((0xC9, "É"), (0xDD, "Ý"), (0xE9, "é"), (0xED, "í"), (0xF4, "ô")):
        _emit("%s (0x%02X) la CHU VIET hop le -> KHONG duoc lam dau hieu" % (ten, cp),
              chr(cp) not in vntext._SIG)
    _emit("moi ky tu SIG deu nam trong khoang byte cao TCVN3 (>=0xA1)",
          all(ord(c) >= 0xA1 for c in vntext._SIG))
    _emit("moi ky tu SIG deu CO trong bang _TCVN3 (khong bia dau hieu ngoai bang)",
          all(ord(c) in vntext._TCVN3 for c in vntext._SIG))

    print("[F] CAU TRUC: chuoi DA la Unicode Viet thi TUYET DOI khong giai ma lai")
    # Van ban TCVN3 doc theo Latin-1 KHONG THE sinh ky tu > U+00FF. Co ky tu >= U+0100
    # (ế ộ ằ ữ đ ơ ư…) => da la Unicode dung. Day la dau hieu CAU TRUC, khong phai tu khoa.
    _emit("'DIỆN TÍCH Ø20' -> khong kich giai ma", vntext._looks_tcvn3("DIỆN TÍCH Ø20") is False)
    _emit("'Ý KIẾN' giu nguyen", vntext.to_unicode("Ý KIẾN") == "Ý KIẾN")
    _emit("'BÊ TÔNG CỐT THÉP' giu nguyen",
          vntext.to_unicode("BÊ TÔNG CỐT THÉP") == "BÊ TÔNG CỐT THÉP")

    print("[G] THU TU: giai ma TCVN3 TRUOC, doi ma AutoCAD SAU (chong tu nuot Ø)")
    # LOI THAT da song trong san pham: _autocad_codes chay TRUOC bien '%%C'->'Ø' (U+00D8), ma
    # 0xD8 la o 'ỉ' trong bang TCVN3 -> buoc giai ma NUOT ky tu duong kinh vua tao ra.
    # Bang chung corpus (KT CT-A): raw 'thÐp %%C10 neo xµ gå' -> CU 'thép ỉ10' / MOI 'thép Ø10'.
    _emit("'mÆt b»ng %%C20 a200' -> 'mặt bằng Ø20 a200' (Ø song sot)",
          vntext.to_unicode("mÆt b»ng %%C20 a200") == "mặt bằng Ø20 a200",
          vntext.to_unicode("mÆt b»ng %%C20 a200"))
    _emit("'thÐp %%C10 neo xµ gå' -> 'thép Ø10 neo xà gồ' (ca THAT trong corpus)",
          vntext.to_unicode("thÐp %%C10 neo xµ gå") == "thép Ø10 neo xà gồ",
          vntext.to_unicode("thÐp %%C10 neo xµ gå"))
    _emit("chuoi khong garble van doi %%C binh thuong", vntext.to_unicode("%%C22") == "Ø22")

    print("[I] 'Ð' (U+00D0) CO HAI NGHIA — phan biet bang VI TRI, khong bang tu khoa")
    # Bug that bat duoc trong chinh vong va nay: chi them 'Ð' vao dau hieu thi 'Ðang XD' -> 'éang XD'.
    # Trong TCVN3 chu 'Đ' ma hoa la 0xA7 ('§'), KHONG phai 0xD0 -> 'Ð' DAU TU khong the la TCVN3.
    _emit("'Ðang XD' -> 'Đang XD' (Ð dau tu = chu Đ viet nhai)",
          vntext.to_unicode("Ðang XD") == "Đang XD", vntext.to_unicode("Ðang XD"))
    _emit("'Ðông Anh' -> 'Đông Anh'", vntext.to_unicode("Ðông Anh") == "Đông Anh",
          vntext.to_unicode("Ðông Anh"))
    _emit("'THÐP' -> 'THÉP' (Ð sau chu cai = o TCVN3 'é')",
          vntext.to_unicode("THÐP") == "THÉP", vntext.to_unicode("THÐP"))
    _emit("'kÐo dµi' -> 'kéo dài'", vntext.to_unicode("kÐo dµi") == "kéo dài",
          vntext.to_unicode("kÐo dµi"))
    # Ca THAT trong corpus: luat ban dau doi "theo sau la chu THUONG" nen bo sot 'ÐT' viet hoa.
    _emit("'Ðất Khu ÐT Việt Hoà' -> 'Đất Khu ĐT Việt Hoà' (Ð truoc CHU HOA cung la Đ)",
          vntext.to_unicode("Ðất Khu ÐT Việt Hoà") == "Đất Khu ĐT Việt Hoà",
          vntext.to_unicode("Ðất Khu ÐT Việt Hoà"))
    _emit("'x· §«ng' -> 'xã Đông' (chu Đ THAT trong TCVN3 la 0xA7 '§')",
          vntext.to_unicode("x· §«ng") == "xã Đông", vntext.to_unicode("x· §«ng"))

    print("[K] CHUOI TRON nua-TCVN3 nua-Unicode (ban ve doi PHONG giua chung)")
    # Ban ve that co MTEXT dang '{\\f.VnTimeH…®…\\fArial…Ư…}' -> mot chuoi 2 bang ma.
    # Tung thu phu quyet "co ky tu Unicode Viet thi bo qua ca chuoi": DO duoc la lam 27 chuoi
    # HONG THEM tren corpus 86 file. Phan TCVN3 VAN phai duoc nan.
    _emit("'Cäc tiÕp ®Þa MẠ KẼM' -> phan TCVN3 duoc nan, phan Unicode giu nguyen",
          vntext.to_unicode("Cäc tiÕp ®Þa MẠ KẼM") == "Cọc tiếp địa MẠ KẼM",
          vntext.to_unicode("Cäc tiÕp ®Þa MẠ KẼM"))
    _emit("'x· LƯƠNG ®iÒn' -> 'xã LƯƠNG điền'",
          vntext.to_unicode("x· LƯƠNG ®iÒn") == "xã LƯƠNG điền",
          vntext.to_unicode("x· LƯƠNG ®iÒn"))
    _emit("KHONG phu quyet ca chuoi khi thay ky tu Unicode Viet",
          vntext._looks_tcvn3("Cäc tiÕp ®Þa MẠ KẼM") is True)

    print("[H] Unicode TO HOP DAU (NFD) -> gop ve NFC")
    nfd = "die" + "̣" + "n t" + "i" + "́" + "ch"      # 'diện tích' dang tach dau
    _emit("NFD -> NFC (do corpus: 266 luot/86 file)",
          vntext.to_unicode(nfd) == unicodedata.normalize("NFC", nfd) and "̣" not in vntext.to_unicode(nfd))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
