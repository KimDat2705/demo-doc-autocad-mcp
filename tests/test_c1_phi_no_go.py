# -*- coding: utf-8 -*-
"""C1 (ký hiệu Φ Hy Lạp) = **NO_GO CÓ SỐ**. Suite này KHOÁ BẤT BIẾN, KHÔNG khoá lỗ hổng.

Mục đích: nếu phiên sau có ai "vá" Φ bằng cách thêm Φ/φ vào `_MAHIEU_RES` (hoặc đổi mù Φ→Ø trong
`to_unicode`), suite này phải ĐỎ TRƯỚC KHI lên LIVE — vì đã đo được bản vá đó GIẾT CÂU ĐÚNG.

BA SỰ THẬT ĐÃ ĐO (wf_3e934400-206, 2026-08-01) — đọc trước khi định mở lại:

 1. TIỀN ĐỀ CỦA CẢ MỤC LÀ SAI. `_norm('Φ10') == _norm('Ø10') == 'ø10'` (unaccent có .lower() +
    _DIAM_RE, tools_core.py:46-51) ⇒ TÌM KIẾM ĐÃ KHỚP Φ RỒI. Lập luận "vá để tăng recall" = SAI.
    Rổ neo cũng bất biến với Φ↔Ø (cả hai nằm dải À-ỹ của lookbehind _NUM_IN_STR_RE) ⇒ lập luận
    "vá để sinh neo mới" cũng SAI.

 2. VÁ = PER-CLAIM THU NHỎ. `_MAHIEU_RES` chạy trên CÂU TRẢ LỜI (mcp_bridge.py:825), nên strip Φ
    đồng thời XOÁ SỐ ĐƯỜNG KÍNH khỏi rổ neo của câu trả lời ⇒ mọi câu TỔNG-HỢP/CỘNG-DỒN (đầu ra
    lõi của phần mềm bóc khối lượng) mất chỗ bám. Đo: giết 17/26 câu ĐÚNG, đổi lấy đóng 1/6 cách
    diễn đạt — mà mẫu bị đóng lại là mẫu Gemini ÍT DÙNG NHẤT (nó viết "đường kính 8 mm" / "phi 8",
    cả hai vẫn lọt 100%). Trùng đúng chốt cũ: per-claim đã NO_GO vì giết 96,7-100% câu ĐÚNG.

 3. SỰ CỐ THẬT = 0. 0 ký tự Φ trong 22 file log trả lời; 3 file mang Φ chưa từng chạy battery.
    Φ = 65 lượt / 3 file (KHÔNG phải 130 như một ghi chú trung gian từng viết).

ĐIỀU KIỆN DUY NHẤT ĐỂ MỞ LẠI: (i) đo giết-oan bằng câu SỐ DẪN XUẤT chứ không phải chuỗi nguồn,
(ii) chứng minh lợi ích còn lại sau khi trừ 5 mẫu câu bypass, (iii) có ≥1 ca Φ trong log trả lời THẬT.

Chạy: python tests/test_c1_phi_no_go.py
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import tools_core as tc      # noqa: E402
import mcp_bridge as mb      # noqa: E402

PASS = FAIL = 0


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def main():
    print("[C1] Φ = NO_GO có số — suite khoá BẤT BIẾN, không khoá lỗ hổng")

    # ── [P1] TIỀN ĐỀ: tìm kiếm ĐÃ khớp Φ, không cần vá gì ──────────────────────────────────────
    print("\n-- [P1] tìm kiếm đã khớp Φ sẵn (tiền đề 'vá để tăng recall' là SAI) --")
    for a, b in [("Φ10", "Ø10"), ("Φ6", "Ø6"), ("thép Φ12", "thép Ø12")]:
        _emit("P1: _norm(%r) == _norm(%r)" % (a, b), tc._norm(a) == tc._norm(b),
              "%r vs %r" % (tc._norm(a), tc._norm(b)))
    _emit("P1d: _norm('Φ10') ra đúng 'ø10'", tc._norm("Φ10") == "ø10", repr(tc._norm("Φ10")))

    # ── [P2] BẤT BIẾN CHÍNH: câu ĐÚNG mang Φ + SỐ DẪN XUẤT phải LUÔN đi qua guard ───────────────
    # Đây là ca mà bản vá bị bác sẽ giết. Nếu ai thêm Φ vào _MAHIEU_RES, 2 ca này ĐỎ.
    # ⚠ RỔ NEO PHẢI KHÔNG CHỨA SỐ TỔNG. Bản nháp đầu của ca này để 24331.67 vào rổ neo -> ca test
    # ĐI QUA ở CẢ HAI phía (có vá và không vá) = KHÔNG PHÂN BIỆT ĐƯỢC = ca test vô dụng.
    # Tổng cộng tay theo định nghĩa KHÔNG nằm trong rổ neo (tool không trả ra nó) — đó chính là
    # bản chất vấn đề: câu tổng bám vào các số THÀNH PHẦN (6, 8, 10) để được bảo lãnh.
    # Tự kiểm ngược đã chạy: thêm Φφ vào _MAHIEU_RES[4] -> ca P2a chuyển ĐI QUA -> BỊ CHẶN.
    print("\n-- [P2] câu ĐÚNG mang Φ phải đi qua guard (ca bản vá bị bác sẽ giết) --")
    neo = {6.0, 8.0, 10.0, 14.57, 65.66}          # KHÔNG có 24331.67
    cau_tong = "Tổng khối lượng thép Φ6, Φ8, Φ10 là 24331.67 kg."
    cau_doc = "Thép Φ6 nặng 14.57 kg, dài 65.66 mét."
    _emit("P2a: câu TỔNG-HỢP mang Φ KHÔNG bị chặn (ĐỎ nếu ai thêm Φ vào _MAHIEU_RES)",
          mb._guard_text(cau_tong, neo) != mb.REFUSE_MESSAGE)
    _emit("P2b: câu đọc thẳng mang Φ KHÔNG bị chặn", mb._guard_text(cau_doc, neo) != mb.REFUSE_MESSAGE)

    # P2c — GHI SỔ MỘT BẤT ĐỐI XỨNG CÓ SẴN, phát hiện khi tự kiểm ngược ca P2a.
    # CÙNG câu đó viết bằng Ø thì HÔM NAY ĐÃ BỊ CHẶN, vì Ø vốn nằm trong _MAHIEU_RES[4]
    # (`[A-Za-zØøĐđ]+[-.]?\d+...`). Tức lỗi "giết câu tổng-hợp ĐÚNG" KHÔNG PHẢI do bản vá Φ đẻ ra —
    # NÓ ĐÃ TỒN TẠI cho Ø. Bản vá bị bác chỉ MỞ RỘNG thiệt hại sẵn có sang Φ.
    # ⚠ KHOÁ hành vi hiện tại để nếu ai sửa nó thì phải sửa CÓ Ý THỨC, kèm phép đo riêng.
    # ⚠ CHƯA VÁ, CHƯA ĐO. Đây là ứng viên việc RIÊNG: "câu tổng-hợp đúng bị hàng rào giết vì mọi số
    #   thành phần đều bị strip như mã-hiệu". Xem session-handoff khối BA NO_GO.
    _emit("P2c: [ghi sổ] CÙNG câu viết bằng Ø thì HÔM NAY ĐÃ bị chặn (bất đối xứng Ø vs Φ có sẵn)",
          mb._guard_text("Tổng khối lượng thép Ø6, Ø8, Ø10 là 24331.67 kg.", neo) == mb.REFUSE_MESSAGE)

    # ── [P3] ĐỐI CHỨNG: hàng rào vẫn chặn câu BỊA (chống nới lỏng ANY-GROUNDED) ─────────────────
    print("\n-- [P3] đối chứng: hàng rào vẫn chặn câu bịa --")
    neo_hep = {6.0, 14.57}
    _emit("P3a: câu bịa số vô căn cứ vẫn BỊ CHẶN",
          mb._guard_text("Chiều dài cống là 777.3 m.", neo_hep) == mb.REFUSE_MESSAGE)
    _emit("P3b: rổ neo RỖNG + câu có số đo -> CHẶN",
          mb._guard_text("Chiều sâu đáy đài là -13.7 m.", set()) == mb.REFUSE_MESSAGE)

    # ── [P4] SOURCE-GUARD: Φ/φ KHÔNG được có mặt trong _MAHIEU_RES ─────────────────────────────
    print("\n-- [P4] source-guard: Φ/φ không được lọt vào lớp mã-hiệu --")
    mau = "".join(r.pattern for r in mb._MAHIEU_RES)
    _emit("P4a: 'Φ' (U+03A6) KHÔNG có trong _MAHIEU_RES", "Φ" not in mau, mau[:90])
    _emit("P4b: 'φ' (U+03C6) KHÔNG có trong _MAHIEU_RES", "φ" not in mau, mau[:90])
    vsrc = open(os.path.join(ROOT, "vntext.py"), encoding="utf-8").read()
    _emit("P4c: to_unicode KHÔNG đổi mù Φ->Ø", "Φ" not in vsrc.split("# ---")[0])

    # ── [P5] Φ đi qua to_unicode NGUYÊN VẸN (không bị nuốt, không bị đổi) ──────────────────────
    print("\n-- [P5] to_unicode giữ Φ nguyên vẹn --")
    import vntext
    for s in ["Trọng lượng thép có đường kính Φ10 = 4385.64 kg", "Φ8 a200", "thép Φ6"]:
        _emit("P5: to_unicode giữ Φ trong %r" % s[:34], "Φ" in vntext.to_unicode(s), vntext.to_unicode(s))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
