# -*- coding: utf-8 -*-
"""
vntext.py — Chuan hoa text doc tu DXF cho de doc:
  1) Ma AutoCAD:  %%C->Ø, %%D->°, %%P->±, %%U/%%O/%%K-> (bo gach chan/tren/giua)
  2) Ma dinh dang MTEXT: \f..; \W..; \p..; {..} -> bo
  3) Font cu TCVN3 (.VnTime/.VnTimeH) -> Unicode (bang ma chuan)
Luu y: day la GIAI MA TU DONG; vai chu hoa co the ra thuong (han che da biet cua TCVN3).
"""
import re
import unicodedata

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


# --- Ma dinh dang MTEXT, tach 3 ho vi CHUNG PHAI XU LY KHAC NHAU (A3, 2026-08-01) ---
# TOGGLE (bat/tat gach chan, gach tren, gach giua...): KHONG co tham so, KHONG co dau ';' ket thuc.
#   ⚠ PHAI go TRUOC ho THAM SO. Neu de _MT_PARAM chay truoc, no khop '\L' roi an tham tiep toi dau ';'
#   KE TIEP trong cau va NUOT LUON CHU THAT. Do corpus: '{\Lchi tiEt ch«n cèng btct d400; l=2m}'
#   -> to_unicode CU tra ve ' l=2m' (mat tron tieu de). 6 doan / 6 file bi nuot kieu nay.
_MT_TOGGLE = re.compile(r"\\[LlOoKkXx]")
# STACK '\S...;' = PHAN SO / CHI SO TREN-DUOI. Day la DU LIEU chu khong phai ma trinh bay:
#   '\S19/3;' = ngay 19/3  ·  '\S^ 1;' = chi so duoi 1  ·  '\S2^ ;' = mu 2 (cm2)
#   Bang cu xoa SACH chung: do duoc 406 doan \S / 81 chuoi / 7 file dang mat du lieu.
#   '^' = vach ngang chong tang (bo) · '#' = vach cheo phan so (-> '/').
_MT_STACK = re.compile(r"\\S([^;\\]*);")
_MT_PARAM = re.compile(r"\\[A-Za-z][^;\\]*;")   # \f..; \F..; \C..; \H..; \W..; \A..; \p..; \T..; \Q..;


def _stack_noi_dung(m):
    return m.group(1).replace("^", "").replace("#", "/").strip()


def _mtext_codes(s, sep=""):
    """Go ma dinh dang MTEXT.

    sep="" (MAC DINH — dung cho to_unicode): DAN lien. BAT BUOC phai la rong o day, vi nguoi ve
      hay che MOT tu/MOT so qua nhieu doan phong. Do mo phong bang khoang trang tren 3.491 chuoi
      mang ma: 24 chuoi / 6 file bi CHE DOI SO THAT — 'm¸c 200#'->'mac 2 0 0#' · '1760'->'176 0' ·
      '0.95'->'0.9'+'5' (dai so CAO DO) · 'F14'->'F 14'. Do la BIA so, nang hon loi dang vá.
    sep=" " (CHI dung cho NHANH THO cua so khop, qua ma_ve_trang): CHONG DINH chu. Neu go thanh
      rong o nhanh tho thi DE RA CHU KHONG CO THAT:
      '{\\f..;WC C}Hç{\\f..; T}HÊ{\\f..;P N}HÊ{\\f..;T LÀ }2700' -> 'wc cchcthepnhet la 2700'
      = tu nhien moc ra chu 'thep' giua mot ghi chu hoan thien kien truc, roi khop luon truy van
      'thep' / 'thong ke thep'. Nhanh 'vn' da ghep lien ho nen sep=" " o day KHONG lam mat gi.
    """
    s = s.replace("\\P", " ").replace("\\~", " ")   # \P xuong dong, \~ khoang trang khong ngat: DEU la khoang trang
    s = _MT_TOGGLE.sub(sep, s)
    s = _MT_STACK.sub(lambda m: sep + _stack_noi_dung(m) + sep, s)
    s = _MT_PARAM.sub(sep, s)
    s = re.sub(r"\\[A-Za-z]", sep, s)
    return s.replace("{", sep).replace("}", sep)


def ma_ve_trang(s):
    """CHI dung cho NHANH THO cua so khop (tools_core.search_texts). KHONG dung de HIEN THI.

    Ly do ton tai: search_texts ghep ca chuoi THO vao ro so khop de con tim duoc chu ma
    _looks_tcvn3 lo tay lam hong (ban ve doi PHONG GIUA CHUNG). Nhung chuoi tho con nguyen
    ma dinh dang, nen TEN PHONG tro thanh CHU de khop:
      '\\fVNI-Helve-Condense|b0|i0|c0|p34;' -> 'Con-DE-nse' cho token 'de'
      -> tim_kiem('nha de xe') khop vao 'NHAØ XE GIAÙO VIEÂN' du ban ve KHONG co chu 'de'.
    Doi ca '%%' vi '%%C10' -> _norm -> '%%c10' nuot tron ma cau kien 'C1' (29.728 luot / 45 file).
    """
    if not s:
        return s
    return _autocad_codes(_mtext_codes(s, sep=" "))


# Ky tu "dau hieu" TCVN3 — gan nhu KHONG xuat hien trong tieng Viet Unicode chuan.
# Co dau hieu nay -> chac chan la font cu; khong co -> de nguyen (tranh pha chu da dung).
#
# TANG 1 (goc): cac o TCVN3 hien ra ky hieu Latin-1 (khong phai chu cai) — hoan toan khong nhap nhang.
_SIG_KY_HIEU = set("µ¶·¸¹»¼½¾¨©ª«¬\xad®¡¢£¤¥¦§")
# TANG 2 (them 2026-07-31): cac o TCVN3 hien ra CHU CAI Latin khong thuoc tieng Viet.
# ⚠ VI SAO PHAI THEM: _SIG cu chi phu dai byte 0xA1-0xBE, nen chuoi ma MOI o TCVN3 cua no deu nam
# 0xC6-0xFE thi KHONG bi phat hien -> giu nguyen garble. Do that 86 file / 285.413 chuoi:
# 9.680 chuoi / 73 file con garble, trong do 12.608 luot ky tu la 23 ky tu duoi day.
# Vi du song: 'diÖn tÝch' · 'bé' · 'THÐP' · 'cèt thÐp' — tat ca deu KHONG duoc nan truoc ban va.
# ⚠ CO Y LOAI TRU (dung them vao, se PHA chu dung):
#   · Chu Viet Unicode hop le trong dai Latin-1: À Á Â Ã È É Ê Ì Í Ò Ó Ô Õ Ù Ú Ý + ban thuong.
#   · Ky hieu KY THUAT trung o TCVN3: Ø(0xD8)='i-hoi' · ×(0xD7)='i-huyen' · ÷(0xF7)='u-nga'.
#     Ø la ky hieu DUONG KINH THEP, co mat khap noi — them vao la pha du lieu quan trong nhat.
# Do tren corpus: 0 luot ky tu con sot nao trung chu-Viet hoac ky-hieu-ky-thuat -> tang 2 khong
# lam rong dien nghi ngo sang vung nhap nhang.
# (KHONG co 'ð' 0xF0 va 'Ä/Å' 0xC4/0xC5: chung KHONG nam trong bang _TCVN3 nen lam dau hieu la
#  vo nghia — kich giai ma nhung chinh chung khong duoc doi. Chung thuoc HO MA KHAC, xem ghi chu cuoi file.)
_SIG_CHU_LATIN = set("ÆÇËÎÏÐÑÖÞßäåæçëîïñöûþ")
_SIG = _SIG_KY_HIEU | _SIG_CHU_LATIN

# 'Ð' (U+00D0 ETH) CO HAI NGHIA, phai tach truoc khi dung lam dau hieu:
#   (a) o TCVN3 0xD0 = 'é'  -> 'THÐP' = 'THÉP'  (Ð nam SAU chu cai)
#   (b) chu 'Đ' viet NHAI bang ETH cho giong -> 'Ðang XD' = 'Đang XD'  (Ð DAU tu, theo sau chu thuong)
# Phan biet bang VI TRI: trong van ban TCVN3 that, chu 'Đ' ma hoa la 0xA7 ('§') chu KHONG phai 0xD0,
# nen 'Ð' dau tu KHONG THE la TCVN3. Do corpus: bo qua viec nay thi 'Ðang XD' -> 'éang XD' (sai).
# Dieu kien DUY NHAT: Ð khong DINH SAU mot chu cai. Khong doi hoi gi ve ky tu DUNG SAU —
# tieng Viet khong co tu nao bat dau bang 'é', nen 'Ð' dau tu chac chan la 'Đ'. (Ban dau toi
# doi "theo sau la chu THUONG", do corpus cho 'Khu ÐT' -> 'Khu ÉT' sai; 'ĐT' = 'Đô Thi'.)
_ETH_DAU_TU = re.compile(r"(?<![A-Za-zÀ-ỹ])Ð")


def _eth_lookalike(s):
    return _ETH_DAU_TU.sub("Đ", s)


# ==================================== HO MA VNI-Windows ====================================
# ⛔ CAU TRUC KHAC HAN TCVN3 — day la ly do chu thich cu ghi "KHONG nhet vao _TCVN3":
#    TCVN3 la bang 1:1 THAY KY TU. VNI la he [NGUYEN AM ASCII goc] + [KY TU DAU DUNG SAU]:
#       'PHOØNG' = P,H,O,Ø,N,G -> 'PHÒNG'   ·  'GIAÙO' = G,I,A,Ù,O -> 'GIÁO'
#    Ngoai ra co 5 ky tu la CHU DUC SAN dung MOT MINH (Ñ Ô Ö Æ Ò) — do la ly do 'NGHÆ'->'NGHỈ'
#    KHONG theo khuon nguyen-am+dau.
# QUY MO: 415 chuoi VNI. Truoc ban va: nan dung 0/415 = 0,0%; go "phong" ra 0 ket qua tren file
#    kien truc co 34 doan ghi 'PHOØNG HOÏC 1..18', trong khi CUNG file do "phong" (phan TCVN3) = 51
#    => engine KHONG hong, THIEU BANG MA. Suite test_vntext 53 PASS nhung 0/53 ca cham VNI
#    => cong KHONG THE do du ve nay chua bat dau.
_CIRC = "̂"; _BREVE = "̆"; _HORN = "̛"
_ACUTE = "́"; _GRAVE = "̀"; _HOOK = "̉"; _TILDE = "̃"; _DOT = "̣"

# --- BANG DAU: CHI 15 muc CO BANG CHUNG CHEO-FILE (tu giai ra phai xuat hien o FILE KHAC duoi
#     dang da dung). So cap kiem chung ghi kem. KHONG muc nao lay tu tri nho. ---
_VNI_DAU_HOA = {
    "Ù": ("", _ACUTE),        # Ù sac         (110 cap)  GIAÙO -> GIÁO
    "Ø": ("", _GRAVE),        # Ø huyen       ( 65)      PHOØNG -> PHÒNG
    "Û": ("", _HOOK),         # Û hoi         ( 49)      SÔÛ -> SỞ
    "Õ": ("", _TILDE),        # Õ nga         ( 19)      LOÃ -> LỖ
    "Ï": ("", _DOT),          # Ï nang        ( 62)      HOÏC -> HỌC
    "Â": (_CIRC, ""),         # Â mu          ( 56)      VIEÂN -> VIÊN
    "Á": (_CIRC, _ACUTE),     # Á mu+sac      ( 68)      KEÁT -> KẾT
    "À": (_CIRC, _GRAVE),     # À mu+huyen    ( 37)      TAÀNG -> TẦNG
    "Å": (_CIRC, _HOOK),      # Å mu+hoi      ( 21)      ÑEÅ -> ĐỂ
    "Ã": (_CIRC, _TILDE),     # Ã mu+nga      (  6)      NGUYEÃN -> NGUYỄN
    "Ä": (_CIRC, _DOT),       # Ä mu+nang     ( 48)      HUYEÄN -> HUYỆN
    "Ê": (_BREVE, ""),        # Ê trang       ( 10)      VAÊN -> VĂN
    "É": (_BREVE, _ACUTE),    # É trang+sac   ( 11)      SAÉT -> SẮT
    "È": (_BREVE, _GRAVE),    # È trang+huyen (  3)      BAÈNG -> BẰNG
    "Ë": (_BREVE, _DOT),      # Ë trang+nang  (  6)      MAËT -> MẶT
}
# ⛔ CO Y KHONG CO — HAI O SUY DOAN, do duoc la 0 BANG CHUNG (de rieng, KHONG dua vao):
#     0xCC 'Ì' = trang+hoi   ·   0xCD 'Í' = trang+nga
#   Do toan corpus: 0 luot chuoi co cap [a/A]+[Ì/Í] => them vao doi 0 chuoi o corpus NAY,
#   NHUNG tren ho so khac se BAN vao chu Viet DUNG: KÍCH 76 · KÍNH 33 · TRÌNH 27 · BÌNH 19.
#   Muon them: PHAI co cap raw->dung KIEM CHUNG DUOC. KHONG duoc them "cho doi xung ho trang".
# ⛔ Cac o khac cung da xet va LOAI vi 0 hoac NGUOC bang chung: Þ(0xDE) · Ó(0xD3) · Ú(0xDA) ·
#   '≥' · '·' (la dau dau dong; 724 chuoi TCVN3 dung no voi nghia 'ã') · 'Ư' (1 chung, va chuoi
#   lam chung do la chuoi TRON phong).

# --- CHU DUC SAN, dung MOT MINH, KHONG bam vao nguyen am truoc (5 muc, deu co bang chung) ---
_VNI_CHU_HOA = {
    "Ñ": "Đ",            # Ñ -> Đ   (65 cap)
    "Ô": "O" + _HORN,         # Ô -> Ơ   (60)
    "Ö": "U" + _HORN,         # Ö -> Ư   (63)
    "Æ": "I" + _HOOK,         # Æ -> Ỉ   ( 6)   NGHÆ -> NGHỈ
    "Ò": "I" + _DOT,          # Ò -> Ị   ( 9)
}
_VNI_DAU = {}
for _k, _v in _VNI_DAU_HOA.items():
    _VNI_DAU[_k] = _v; _VNI_DAU[_k.lower()] = _v
_VNI_CHU = {}
for _k, _v in _VNI_CHU_HOA.items():
    _VNI_CHU[_k] = _v; _VNI_CHU[_k.lower()] = _v.lower()
_VNI_KY_TU = set(_VNI_DAU) | set(_VNI_CHU)

_NGUYEN_AM = set("aeiouyAEIOUY")
_NEN_VNI = _NGUYEN_AM | set("ÔÖôö")     # 'TRÖÔØNG': Ø bam vao 'Ô' vua giai ra 'Ơ'
_NEN_CIRC = set("aeoAEO")               # mu CHI dat tren a/e/o
_NEN_BREVE = set("aA")                  # trang CHI dat tren a

# BANG CHUNG CUNG: ky tu VNI ma KHONG THE la chu cai tieng Viet hop le. SUY RA, khong chon tay:
#   _VNI_KY_TU tru chu Viet Latin-1 (À Á Â Ã È É Ê Ì Í Ò Ó Ô Õ Ù Ú Ý), roi TRU THEM 'Ø'.
# ⛔ TRU 'Ø' vi chinh file nay da ghi: "Ø la ky hieu DUONG KINH THEP, co mat khap noi — them vao
#   la pha du lieu quan trong nhat". Do duoc: giu Ø lam bang-chung-cung thi
#   'TOÀ NHÀ HOÀ Ø20' bi nan thanh 'TỒ NHÀ HỒ Ø20' (pha chu Viet DUNG).
_VNI_CUNG = set("ÛÏÅÄËÑÖÆ")
_VNI_CUNG |= {c.lower() for c in _VNI_CUNG}

# Ky tu CHI thuoc TCVN3 (khong trung VNI) -> co mat la NHUONG nhanh TCVN3.
_VNI_VETO_TCVN3 = ({chr(k) for k in _TCVN3} | _SIG) - _VNI_KY_TU
# Chu Viet Unicode NGOAI Latin-1 -> chuoi DA la Unicode dung, KHONG dung cham.
_VNI_VETO_UNICODE = set(
    "ĂăĐđĨĩŨũƠơƯư"
    "ẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệ"
    "ỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰự"
    "ỲỳỴỵỶỷỸỹ")

_DAU_KEP = re.compile(r"([̛̣̀́̃̉̂̆])\1+")


def _dem_cap_vni(s):
    """Dem so cap [nguyen am][ky tu dau] HOP LE VE CHINH TA (cung kieu chu HOA/thuong, mu chi tren
    a/e/o, trang chi tren a). Day la DAU HIEU CAU TRUC — KHONG doc TEN PHONG o bat ky dau nao.
    ⛔ VI SAO KHONG DUOC DUNG TEN PHONG: 11 file khai phong 'vn_vni.shx'/'VNI-Helve-Condense.TTF'
      nhung RUOT LA TCVN3 va dang duoc nan DUNG. Dung ten phong lam cong = pha 107.764 chuoi dang
      chay tot. Va con BO SOT: 3/16 file duoc cuu KHONG he khai phong VNI."""
    n = 0
    for i in range(1, len(s)):
        c, p = s[i], s[i - 1]
        if c not in _VNI_DAU or p not in _NEN_VNI:
            continue
        mod, _tone = _VNI_DAU[c]
        if mod == _CIRC and p not in _NEN_CIRC:
            continue
        if mod == _BREVE and p not in _NEN_BREVE:
            continue
        if c.isupper() != p.isupper():
            continue
        n += 1
    return n


def _looks_vni(s):
    """3 PHU QUYET + 2 dieu kien duong. Moi dieu kien co SO do duoc:
    · veto Unicode  : chuoi da dung -> khong dung cham
    · veto TCVN3    : co ky tu CHI-thuoc-TCVN3 -> nhuong nhanh TCVN3 (do: 5/5 ca TCVN3 ra y het ban cu)
    · BANG CHUNG CUNG: phai co >=1 ky tu KHONG THE la chu Viet -> chan ho 'TOÀ/HOÀ' (ca phan chung
      that ma phan bien tim ra: 'TOÀ NHÀ HOÀ BÌNH' -> 'TỒ NHÀ HỒ BÌNH' o bien the KHONG co dieu kien nay)
    · NGUONG >=2 cap: ha xuong 1 do duoc PHA 316 luot ('CHñ NHIÖM THIÕT KÕ' -> 'CHĐ NHIƯM THĨT KÕ',
      24 luot/18 file)."""
    if any(c in _VNI_VETO_UNICODE for c in s):
        return False
    if any(c in _VNI_VETO_TCVN3 for c in s):
        return False
    if not any(c in _VNI_CUNG for c in s):
        return False
    return _dem_cap_vni(s) >= 2


def _decode_vni(s):
    out = []
    for c in s:
        if c in _VNI_CHU:                     # chu duc san: KHONG bam vao ky tu truoc do
            out.append(_VNI_CHU[c]); continue
        if c in _VNI_DAU and out:
            base = out[-1]
            if base and base[0] in _NGUYEN_AM:
                mod, tone = _VNI_DAU[c]
                if (mod != _CIRC or base[0] in _NEN_CIRC) and (mod != _BREVE or base[0] in _NEN_BREVE):
                    out[-1] = base + mod + tone
                    continue
        out.append(c)                         # ky tu NGOAI bang -> GIU NGUYEN, KHONG doan
    r = unicodedata.normalize("NFD", "".join(out))
    r = _DAU_KEP.sub(r"\1", r)                # nguoi ve go dau HAI LAN ('GIÔÙÙI'); do: 4 luot/1 file
    return unicodedata.normalize("NFC", r)
# ================================== het khoi VNI ==================================


def _looks_tcvn3(s):
    # ⚠ KHONG duoc phu quyet kieu "chuoi da co ky tu Unicode Viet thi bo qua ca chuoi".
    # Da thu va DO duoc la SAI: ban ve doi PHONG GIUA CHUNG ('{\f.VnTimeH…®…\fArial…Ư…}') nen
    # mot chuoi co the NUA TCVN3 NUA Unicode that ('MÆT C¾T §IÓN H×NH PHè vIỆT HÒA',
    # 'Cäc tiÕp ®Þa MẠ KẼM'). Phu quyet ca chuoi lam 27 chuoi HONG THEM tren corpus 86 file.
    # Dau hieu SIG von da khong xuat hien trong tieng Viet Unicode dung, nen tu no da du chat.
    return any(c in _SIG for c in s)


def to_unicode(s):
    """Tra ve text de doc. CHI giai ma TCVN3 khi PHAT HIEN dau hieu font cu;
    text da la Unicode dung (vd 'BÊ TÔNG') giu NGUYEN, khong dung cham."""
    if not s:
        return s
    s = _mtext_codes(s)
    s = _eth_lookalike(s)      # 'Ðang' -> 'Đang' TRUOC khi Ð duoc dung lam dau hieu TCVN3
    # ⛔ NFC PHAI DUNG O DAY — TRUOC khi do dau hieu, khong duoc de o CUOI nhu ban truoc.
    #   Corpus co chuoi luu dang NFD ('CỐT' = C,O,U+0302,U+0301). Do dau hieu tren chuoi THO thi
    #   'BẢNG THỐNG KÊ CỐT THÉP' bi nan thanh 'BẢNG THỚNG KÊ CỚT THÉP'. Do: hong them 0 -> 19 luot.
    s = unicodedata.normalize("NFC", s)
    # ⚠ THU TU QUAN TRONG: giai ma phong cu TRUOC, doi ma AutoCAD SAU.
    # Truoc day _autocad_codes chay truoc, bien '%%C' thanh 'Ø' (U+00D8) — ma 0xD8 lai la o
    # 'i-hoi' trong bang TCVN3, nen buoc giai ma NUOT LUON ky tu duong kinh minh vua tao ra:
    # 'mÆt b»ng %%C20' -> 'mặt bằng ỉ20'. Tu pha du lieu cua chinh minh. '%%C' la ASCII thuan
    # nen di qua _decode_tcvn3 nguyen ven; doi sau thi an toan.
    # ⛔ VNI PHAI DUNG TRUOC TCVN3, va la 'elif' chu KHONG phai 2 lenh roi:
    #   350/415 chuoi VNI co mang it nhat 1 ky tu _SIG, nen truoc ban va chung DANG di nham nhanh
    #   TCVN3 va ra rac ('TRÖÔØNG…' -> 'TRỆỄỈNG…'). Dat VNI SAU la ban va VO HIEU tren ~84% ca.
    #   Hai nhanh KHONG va nhau THEO CAU TRUC: _looks_vni phu quyet moi ky tu CHI-thuoc-TCVN3.
    if _looks_vni(s):
        s = _decode_vni(s)
        s = _fix_case(s)
    elif _looks_tcvn3(s):
        s = _decode_tcvn3(s)
        s = _fix_case(s)
    s = _autocad_codes(s)
    # Unicode TO HOP DAU (NFD: 'ệ' = 'e' + U+0323 + U+0302) hien ra nhu chu thieu dau tren
    # nhieu duong xu ly va lam hong so sanh chuoi. Gop ve dang dung san (NFC). Do: 266 luot/86 file.
    s = unicodedata.normalize("NFC", s)
    return " ".join(s.split())


# ---------------------------------------------------------------------------------------------
# ĐO TOÀN CORPUS 86 file / 285.413 chuỗi (2026-07-31, mục 1.03) — TRƯỚC/SAU bản vá này:
#   được cứu (hết ký tự lạ)      8.913
#   HỎNG THÊM                        0      <- chiều nguy hiểm, đã kiểm sạch
#   đổi mà cả hai đều sạch          285      (NFC + đổi thứ tự %%C)
#   Ø bị nuốt thành 'ỉ'      152 -> 0
#
# ⚠ CÒN LẠI 768 chuỗi VẪN HỎNG — CỐ Ý CHƯA XỬ LÝ, không phải bỏ sót:
#   Chúng mang các ký tự Ä(0xC4) Å(0xC5) Û(0xDB) Φ(U+03A6) † „ ‚ Š — **KHÔNG nằm trong bảng
#   _TCVN3**, tức thuộc HỌ MÃ KHÁC (nhiều khả năng VNI-Windows hoặc phông tự chế của đơn vị vẽ).
#   Thêm chúng vào bảng TCVN3 là ĐOÁN: chưa có cặp raw->đúng nào được kiểm chứng. Muốn xử lý thì
#   phải dựng bảng mã riêng cho họ đó và đo lại như trên, KHÔNG nhét vào _TCVN3.
#   (Φ gần như chắc là người vẽ gõ 'phi' Hy Lạp thay cho Ø — nhưng 65 lượt, và sửa nó là đổi
#    KÝ HIỆU ĐƯỜNG KÍNH nên phải đo riêng, không làm kèm.)
#
# ⚠ GIỚI HẠN KHÔNG GỠ ĐƯỢC BẰNG CÁCH NÀY: chuỗi mà MỌI ô TCVN3 của nó đều trùng chữ Việt hợp lệ
#   thì KHÔNG có dấu hiệu nào để nhận ra — ví dụ 'bé' (TCVN3 của 'bộ') giữ nguyên là 'bé'. Đây là
#   nhập nhằng THẬT ở mức byte, không phải lỗi dò. Các tầng trên xử lý bằng ngữ cảnh (xem
#   chú thích '(1 bé)' ở tools_core).
# ---------------------------------------------------------------------------------------------
