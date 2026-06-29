# -*- coding: utf-8 -*-
"""
vntext.py — Chuan hoa text doc tu DXF cho de doc:
  1) Ma AutoCAD:  %%C->Ø, %%D->°, %%P->±, %%U/%%O/%%K-> (bo gach chan/tren/giua)
  2) Ma dinh dang MTEXT: \f..; \W..; \p..; {..} -> bo
  3) Font cu TCVN3 (.VnTime/.VnTimeH) -> Unicode (bang ma chuan)
Luu y: day la GIAI MA TU DONG; vai chu hoa co the ra thuong (han che da biet cua TCVN3).
"""
import re

# Bang ma TCVN3 (.VnTime): byte goc (ODA da doc thanh ky tu Latin-1 cung ma) -> Unicode
_TCVN3 = {
    0xB5: "à", 0xB8: "á", 0xB6: "ả", 0xB7: "ã", 0xB9: "ạ",
    0xA8: "ă", 0xBB: "ằ", 0xBE: "ắ", 0xBC: "ẳ", 0xBD: "ẵ", 0xC6: "ặ",
    0xA9: "â", 0xC7: "ầ", 0xCA: "ấ", 0xC8: "ẩ", 0xC9: "ẫ", 0xCB: "ậ",
    0xAE: "đ",
    0xCC: "è", 0xD0: "é", 0xCE: "ẻ", 0xCF: "ẽ", 0xD1: "ẹ",
    0xAA: "ê", 0xD2: "ề", 0xD5: "ế", 0xD3: "ể", 0xD4: "ễ", 0xD6: "ệ",
    0xD7: "ì", 0xDD: "í", 0xD8: "ỉ", 0xDC: "ĩ", 0xDE: "ị",
    0xDF: "ò", 0xE3: "ó", 0xE1: "ỏ", 0xE2: "õ", 0xE4: "ọ",
    0xAB: "ô", 0xE5: "ồ", 0xE8: "ố", 0xE6: "ổ", 0xE7: "ỗ", 0xE9: "ộ",
    0xAC: "ơ", 0xEA: "ờ", 0xED: "ớ", 0xEB: "ở", 0xEC: "ỡ", 0xEE: "ợ",
    0xEF: "ù", 0xF3: "ú", 0xF1: "ủ", 0xF2: "ũ", 0xF4: "ụ",
    0xAD: "ư", 0xF5: "ừ", 0xF8: "ứ", 0xF6: "ử", 0xF7: "ữ", 0xF9: "ự",
    0xFA: "ỳ", 0xFD: "ý", 0xFB: "ỷ", 0xFC: "ỹ", 0xFE: "ỵ",
    0xA1: "Ă", 0xA2: "Â", 0xA7: "Đ", 0xA3: "Ê", 0xA4: "Ô", 0xA5: "Ơ", 0xA6: "Ư",
}


def _decode_tcvn3(s):
    return "".join(_TCVN3.get(ord(c), c) for c in s)


def _fix_case(s):
    # Trong tu VIET HOA toan bo -> viet hoa luon ky tu co dau vua giai ma (TaNG -> TẦNG)
    def repl(m):
        w = m.group(0)
        ascii_letters = [c for c in w if c.isalpha() and ord(c) < 128]
        if ascii_letters and all(c.isupper() for c in ascii_letters):
            return w.upper()
        return w
    return re.sub(r"\S+", repl, s)


def _autocad_codes(s):
    s = s.replace("%%C", "Ø").replace("%%c", "Ø")
    s = s.replace("%%D", "°").replace("%%d", "°")
    s = s.replace("%%P", "±").replace("%%p", "±")
    s = re.sub(r"%%[uUoOkK]", "", s)   # gach chan/tren/giua -> bo dau
    s = s.replace("%%%", "%")
    return s


def _mtext_codes(s):
    s = s.replace("\\P", " ")
    s = re.sub(r"\\[A-Za-z][^;\\]*;", "", s)   # \f..; \W..; \A1; \H..; \p..;
    s = re.sub(r"\\[A-Za-z]", "", s)
    return s.replace("{", "").replace("}", "")


# Ky tu "dau hieu" TCVN3 — gan nhu KHONG xuat hien trong tieng Viet Unicode chuan.
# Co dau hieu nay -> chac chan la font cu; khong co -> de nguyen (tranh pha chu da dung).
_SIG = set("µ¶·¸¹»¼½¾¨©ª«¬\xad®¡¢£¤¥¦§")


def _looks_tcvn3(s):
    return any(c in _SIG for c in s)


def to_unicode(s):
    """Tra ve text de doc. CHI giai ma TCVN3 khi PHAT HIEN dau hieu font cu;
    text da la Unicode dung (vd 'BÊ TÔNG') giu NGUYEN, khong dung cham."""
    if not s:
        return s
    s = _mtext_codes(s)
    s = _autocad_codes(s)
    if _looks_tcvn3(s):
        s = _decode_tcvn3(s)
        s = _fix_case(s)
    return " ".join(s.split())
