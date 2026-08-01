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
    # ⚠ THU TU QUAN TRONG: giai ma TCVN3 TRUOC, doi ma AutoCAD SAU.
    # Truoc day _autocad_codes chay truoc, bien '%%C' thanh 'Ø' (U+00D8) — ma 0xD8 lai la o
    # 'i-hoi' trong bang TCVN3, nen buoc giai ma NUOT LUON ky tu duong kinh minh vua tao ra:
    # 'mÆt b»ng %%C20' -> 'mặt bằng ỉ20'. Tu pha du lieu cua chinh minh. '%%C' la ASCII thuan
    # nen di qua _decode_tcvn3 nguyen ven; doi sau thi an toan.
    if _looks_tcvn3(s):
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
