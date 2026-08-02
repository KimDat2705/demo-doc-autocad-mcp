# -*- coding: utf-8 -*-
"""VNI-Windows — bảng mã + cổng nhận diện CẤU TRÚC. Tất định, offline, KHÔNG tốn API.

VÌ SAO CÓ: mục 1.03 có tiêu đề BA VẾ ("nắn phông cũ: VNI, TCVN3 còn sót, Ø vỡ") nhưng vế VNI có
0 DÒNG CODE — `grep VNI` chỉ ra CHÚ THÍCH. Nắn đúng 0/415 chuỗi = 0,0%. Gõ "phòng" ra 0 kết quả
trên file có 34 đoạn 'PHOØNG HOÏC 1..18', trong khi CÙNG file "phòng" (phần TCVN3) = 51
=> engine KHÔNG hỏng, THIẾU BẢNG MÃ. Suite test_vntext 53 PASS nhưng 0/53 ca chạm VNI
=> cổng KHÔNG THỂ đỏ dù vế này chưa bắt đầu. Suite NÀY đóng lỗ hổng đó.

⛔ CẤU TRÚC KHÁC HẲN TCVN3: TCVN3 là bảng 1:1 thay ký tự; VNI là [NGUYÊN ÂM] + [KÝ TỰ DẤU ĐỨNG SAU]
   ('PHOØNG' = P,H,O,Ø,N,G -> 'PHÒNG'), cộng 5 CHỮ ĐÚC SẴN đứng một mình (Ñ Ô Ö Æ Ò) — đó là lý do
   'NGHÆ'->'NGHỈ' không theo khuôn nguyên-âm+dấu.

⛔ CỔNG: 3 PHỦ QUYẾT + 2 điều kiện dương. Điều kiện "BẰNG CHỨNG CỨNG" (>=1 ký tự KHÔNG THỂ là chữ
   Việt) là thứ chặn CẢ MỘT LỚP PHÁ mà phản biện tìm ra: nếu thiếu nó thì
   'TOÀ NHÀ HOÀ BÌNH' -> 'TỒ NHÀ HỒ BÌNH' (phá chữ Việt ĐÚNG).
   ⚠ GIÁ PHẢI TRẢ, ĐO ĐƯỢC: bỏ sót 93/945 = 9,8% chuỗi VNI mà mọi ký tự dấu đều trùng chữ Việt
     hợp lệ ('PHOØNG AÊN', 'THEÙP SAØN', 'BEÂ TOÂNG LOÙT'). Đây là ĐÁNH ĐỔI CÓ Ý THỨC:
     đúng-đắn đổi lấy recall. Đừng gỡ điều kiện này để "vớt thêm".

TỰ KIỂM NGƯỢC TOÀN CORPUS (910.574 chuỗi/98 file, một lượt tính cả trước lẫn sau):
   852 chuỗi riêng biệt đổi · 0 ca "sau tệ hơn" · **0/852 chuỗi thiếu bằng chứng cứng**
   (=> `truoc` CHẮC CHẮN là garble, bảo đảm CẤU TRÚC chứ không phải may)
   773/852 chuỗi cũng khớp `_looks_tcvn3` nhưng nhánh đó đang cho RÁC ('MAẬT CAẪT II-II')
   => xác nhận VNI PHẢI chạy TRƯỚC TCVN3.

Chạy: python tests/test_vni.py
"""
import os, sys, io, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import vntext as v   # noqa: E402

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def main():
    print("[VNI] bảng mã VNI-Windows + cổng nhận diện cấu trúc")

    # ══ [A] GIẢI MÃ ĐÚNG — phải ĐỎ trước khi vá ═══════════════════════════════════════════
    print("\n-- [A] giải mã đúng (phân biệt được) --")
    for raw, mong in [
        ("PHOØNG HOÏC 1", "PHÒNG HỌC 1"),
        ("PHOØNG HOÏC 18", "PHÒNG HỌC 18"),
        ("PHOØNG GIAÙO DUÏC VAØ ÑAØO TAÏO HUYEÄN GIA LOÄC",
         "PHÒNG GIÁO DỤC VÀ ĐÀO TẠO HUYỆN GIA LỘC"),
        ("TRÖÔØNG TRUNG HOÏC CÔ SÔÛ GIA KHAÙNH", "TRƯỜNG TRUNG HỌC CƠ SỞ GIA KHÁNH"),
        ("PHOØNG NGHÆ GIAÙO VIEÂN 1", "PHÒNG NGHỈ GIÁO VIÊN 1"),
        ("%%UMAËT CAÉT I-I", "MẶT CẮT I-I"),
        ("SOÁ LÖÔÏNG", "SỐ LƯỢNG"),
        ("SAÛNH THOÂNG TIN", "SẢNH THÔNG TIN"),
        ("%%UCHI TIEÁT MUÕI COÏC", "CHI TIẾT MŨI CỌC"),
        ("SOÁ 17, DÖÔNG VAÊN AN, P.AN PHUÙ, Q.2. TP.HCM", "SỐ 17, DƯƠNG VĂN AN, P.AN PHÚ, Q.2. TP.HCM"),
        ("{\\fVNI-Helve-Condense|b1|i0|c0|p2;GIÔÙI HAÏN CHÒU LÖÛA CUÛA KEÁT CAÁU NHAØ}",
         "GIỚI HẠN CHỊU LỬA CỦA KẾT CẤU NHÀ"),
        # ---- VỚT TẦNG 2 (bằng-chứng ÂM TIẾT, wf_666cedfd 2026-08-02): VNI THIẾU bằng-chứng-cứng
        #      ký tự — trước đây bị E3 cũ khoá ở trạng thái BỎ SÓT; nay phải giải đúng. Đo corpus:
        #      vớt 78/79 chuỗi (180/181 lượt), 0 vớt-sai, 0 phá-chữ-đúng, 0 lệch số. ----
        ("PHOØNG AÊN", "PHÒNG ĂN"),
        ("THEÙP SAØN Ø20a200", "THÉP SÀN Ø20a200"),
        ("XAØ GOÀ", "XÀ GỒ"),                                  # GOÀ thô-hợp-lệ (A) đi theo G 'XAØ'
        ("GOÃ CHOÁNG CAÂY D=40MM", "GỖ CHỐNG CÂY D=40MM"),     # 'choáng' là từ thật -> A, vẫn vớt
        # 2 ca SỐ-NHẠY (khoá hồi quy an-toàn-số của lăng kính V1):
        ("3-2. GIA COÁ LOÃ SAØN", "3-2. GIA CỐ LỖ SÀN"),       # dấu '-' trước số giữ nguyên
        ("SAÉT TRAÙNG KEÕM Ø49x1.2MM", "SẮT TRÁNG KẼM Ø49x1.2MM"),  # Ø+số dính chữ x + thập phân
    ]:
        got = v.to_unicode(raw)
        ok("A: %r" % raw[:40], got == mong, got)

    # ══ [B] CHỐNG TÁI PHÁT — ca phản chứng đã BÁC biến thể không có bằng-chứng-cứng ═══════
    print("\n-- [B] chống tái phát: chữ Việt ĐÚNG phải giữ nguyên tuyệt đối --")
    for s in ["TOÀ NHÀ HOÀ BÌNH", "CÔNG TRÌNH HOÀ BÌNH - TOÀ B", "PHÒNG HOÀ TOÀ",
              "CÔNG TY HOÀ AN - TOÀ ÁN", "TOÀ NHÀ HOÀ Ø20"]:
        ok("B: %r giữ nguyên" % s[:32], v.to_unicode(s) == s, v.to_unicode(s))

    # ══ [C] KHÔNG ĐƯỢC ĐỤNG ═════════════════════════════════════════════════════════════
    print("\n-- [C] TCVN3 / Unicode đúng / ký hiệu: y hệt bản cũ --")
    for raw, mong in [("diÖn tÝch", "diện tích"), ("cèt thÐp", "cốt thép"),
                      ("MÆt b»ng tÇng 1", "Mặt bằng tầng 1"),
                      ("CHñ NHIÖM THIÕT KÕ", "CHỦ NHIỆM THIẾT KẾ"),
                      ("CHI TIÕT CäC", "CHI TIẾT CỌC")]:
        ok("C-tcvn3: %r" % raw[:24], v.to_unicode(raw) == mong, v.to_unicode(raw))
    for s in ["AN TOÀN LAO ĐỘNG", "BÊN NGOÀI", "ĐIỀU HOÀ", "BÊ TÔNG CỐT THÉP",
              "HOÀN THIỆN", "BẢNG THỐNG KÊ CỐT THÉP"]:
        ok("C-unicode: %r" % s[:26], v.to_unicode(s) == s, v.to_unicode(s))
    nfd = unicodedata.normalize("NFD", "BẢNG THỐNG KÊ CỐT THÉP")
    ok("C-NFD: chuỗi NFD KHÔNG bị nắn (NFC phải chạy TRƯỚC khi dò)",
       v.to_unicode(nfd) == "BẢNG THỐNG KÊ CỐT THÉP", v.to_unicode(nfd))
    for raw, mong in [("%%C20", "Ø20"), ("THÉP Ø20a200", "THÉP Ø20a200"),
                      ("MAŠ„T D‚A†‰T", "MAŠ„T D‚A†‰T")]:   # họ mã THỨ BA -> giữ nguyên
        ok("C-kyhieu: %r" % raw[:20], v.to_unicode(raw) == mong, v.to_unicode(raw))

    # ══ [D] SOURCE-GUARD — khoá từng quyết định thiết kế, mỗi cái có SỐ ══════════════════
    print("\n-- [D] source-guard: khoá quyết định thiết kế --")
    ok("D1: 0xCC 'Ì' và 0xCD 'Í' KHÔNG có trong bảng (0 bằng chứng; thêm vào sẽ bắn "
       "KÍCH 76 · KÍNH 33 · TRÌNH 27 · BÌNH 19)",
       "Ì" not in v._VNI_DAU and "Í" not in v._VNI_DAU)
    ok("D2: 'Ø' KHÔNG nằm trong tập BẰNG CHỨNG CỨNG (Ø là ký hiệu ĐƯỜNG KÍNH THÉP)",
       "Ø" not in v._VNI_CUNG)
    ok("D3: ngưỡng >=2 cặp (hạ xuống 1 đo được PHÁ 316 lượt)",
       v._dem_cap_vni("GIAÙO") == 1 and not v._looks_vni("cèt thÐp aØ200"))
    src = open(os.path.join(ROOT, "vntext.py"), encoding="utf-8").read()
    ok("D4: VNI chạy TRƯỚC TCVN3 và là elif (350/415 chuỗi VNI mang ký tự _SIG)",
       src.index("if _looks_vni(s):") < src.index("elif _looks_tcvn3(s):"))
    ok("D5: NFC chạy TRƯỚC khi dò dấu hiệu (để sau -> hỏng thêm 19 lượt)",
       src.index('s = unicodedata.normalize("NFC", s)') < src.index("if _looks_vni(s):"))
    ok("D6: cổng KHÔNG nhận tham số tên phông (11 file khai VNI mà ruột TCVN3)",
       "def _looks_vni(s):" in src and "font" not in src.split("def _looks_vni")[1][:400].lower())
    ok("D7: ký tự ĐƠN (Ñ Ö Æ Ò Ô) KHÔNG tính vào ngưỡng cặp (tính vào -> phá 3.237 lượt)",
       v._dem_cap_vni("ÑÖÆÒÔ") == 0, str(v._dem_cap_vni("ÑÖÆÒÔ")))
    ok("D8: _decode_vni GIỮ NGUYÊN ký tự ngoài bảng (không đoán)",
       "MAŠ„T" in v._decode_vni("MAŠ„T"))
    ok("D9: vớt tầng 2 đứng SAU TCVN3 (elif thứ ba) — TCVN3 không-veto không-cứng phải được "
       "nhánh TCVN3 ăn trước, lọt vào recovery sẽ bị giải VNI ra rác",
       src.index("elif _looks_tcvn3(s):") < src.index("elif _vni_recovery(s):"))
    than_rec = src.split("def _vni_recovery")[1].split("def _looks_tcvn3")[0]
    ok("D10: 'Ø' KHÔNG xuất hiện trong thân _vni_recovery (không được thành điều kiện dương — "
       "Ø là ký hiệu đường kính thép, cùng lý do D2)",
       "Ø" not in than_rec, than_rec[:60])

    # ══ [E] ĐỐI CHỨNG chống-tautology + GIỚI HẠN ĐÃ BIẾT ════════════════════════════════
    print("\n-- [E] đối chứng + giới hạn đã biết --")
    ok("E1: cổng CÓ THỂ trả False (không phải luôn bắn)", not v._looks_vni("BÊ TÔNG CỐT THÉP"))
    ok("E2: cổng CÓ THỂ trả True (không phải luôn im)", v._looks_vni("PHOØNG HOÏC 1"))
    # ⚠ E3 CŨ (khoá bỏ-sót 9,8%) ĐÃ ĐƯỢC SỬA CÓ Ý THỨC 2026-08-02 (wf_666cedfd) — đúng thủ tục
    #   chính nó đòi: vớt tầng 2 bằng bằng-chứng ÂM TIẾT, VÀ đã đo lại lớp TOÀ/HOÀ trên toàn corpus
    #   (0 phá, nhóm [B] vẫn khoá). CƠ CẤU BỎ-SÓT MỚI sau vớt (đo 2026-08-02, corpus 91 file):
    #   79 mục tiêu -> vớt 78; còn sót có tên: 1 ca 'T.CHIEÀU DAØI (M)' (dấu chấm nội bộ token)
    #   + lớp cặp=1 ('QUY CAÙCH') + lớp mang Ì/Í oan ('CHUÛ TRÌ THIEÁT KEÁ') chờ lát Ì/Í riêng.
    ok("E3: [vớt tầng 2] VNI thiếu bằng-chứng-cứng nhưng >=1 token vô-nghĩa-thô giải ra "
       "âm tiết hợp lệ và 0 token hỏng-sau-giải -> PHẢI giải",
       v.to_unicode("PHOØNG AÊN") == "PHÒNG ĂN", v.to_unicode("PHOØNG AÊN"))
    ok("E3b: [giới hạn - ngưỡng] cặp=1 vẫn KHÔNG giải ('QUY CAÙCH' chịu sót để ngưỡng >=2 "
       "tiếp tục che 'CèNG THIÕT KÕ' 40 lượt; hạ ngưỡng phải ĐO LẠI, không suy)",
       v.to_unicode("QUY CAÙCH") == "QUY CAÙCH", v.to_unicode("QUY CAÙCH"))
    ok("E3c: [giới hạn - 0 token G] chuỗi toàn token thô-hợp-lệ KHÔNG giải (lớp TOÀ/HOÀ)",
       v.to_unicode("TOÀ NHÀ HOÀ") == "TOÀ NHÀ HOÀ", v.to_unicode("TOÀ NHÀ HOÀ"))
    ok("E3d: [giới hạn - None] token có dấu chấm NỘI BỘ ('T.CHIEÀU') rơi vào None -> XẤU -> "
       "cả chuỗi KHÔNG giải (1 lượt corpus; muốn vớt phải tách lõi theo dấu chấm + ĐO LẠI)",
       v.to_unicode("T.CHIEÀU DAØI (M)") == "T.CHIEÀU DAØI (M)", v.to_unicode("T.CHIEÀU DAØI (M)"))
    # ⚠ E3e — RESIDUAL CÓ CHỦ ĐÍCH (lăng kính V3 đòi ghi tường minh, KHÔNG phải bug mới):
    #   chuỗi TRỘN chữ-Việt-đúng + VNI thật ('TOÀ NHÀ THEÙP') SẼ bắn và kéo 'TOÀ'->'TỒ'.
    #   Corpus đo được 0 ca dạng này; và nhánh bằng-chứng-cứng HIỆN HÀNH cũng xử y hệt
    #   ('KHOÁ CÖÛA THEÙP' bị _looks_vni kéo nguyên chuỗi từ trước). Khoá để ai đổi phải đo.
    ok("E3e: [residual đã biết] chuỗi trộn Việt-đúng + VNI bắn cả chuỗi (0 ca trên corpus; "
       "hành vi ĐỒNG NHẤT với nhánh bằng-chứng-cứng hiện hành)",
       v.to_unicode("TOÀ NHÀ THEÙP") == "TỒ NHÀ THÉP", v.to_unicode("TOÀ NHÀ THEÙP"))
    ok("E4: bảng dấu 15 mục + chữ đúc sẵn 5 mục (mỗi mục có bằng chứng chéo-file)",
       len(v._VNI_DAU_HOA) == 15 and len(v._VNI_CHU_HOA) == 5,
       "%d/%d" % (len(v._VNI_DAU_HOA), len(v._VNI_CHU_HOA)))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
