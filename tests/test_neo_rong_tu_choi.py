# -*- coding: utf-8 -*-
"""A2 — rổ neo RỖNG *vì CHÍNH SÁCH* thì KHÔNG được khẳng định "bản vẽ không có". Tất định, offline.

LỖI: tuple loại-trừ rổ neo (`mcp_bridge`, ~:975) khiến 4 tool cố ý không đóng góp số. Nếu model CHỈ gọi
tool trong tuple đó thì `tool_numbers` RỖNG ⇒ `_guard_text` trả REFUSE_MESSAGE = "Không có thông tin này
trong bản vẽ." — một KHẲNG ĐỊNH VỀ BẢN VẼ, và nó SAI khi bản vẽ thực sự có dữ liệu.
Đo: 3/1699 lượt (0,18%); ca id69 model gọi `tra_ky_hieu` -> từ chối, trong khi `ky_vong` = "Thép tròn,
4817 thanh / 25752.6 kg"; CÙNG câu đó lượt gọi `thong_ke_thep` thì TRẢ LỜI ĐÚNG ⇒ nguyên nhân là ROUTING.

⛔ ĐIỀU KIỆN RỘNG "rổ neo rỗng + đã gọi tool" = NO_GO, đã đo:
  · bắn trúng ĐÚNG lớp lỗi id135 (`tim_kiem` chạy THẬT trả `{}` rồi model bịa "-10m" — ở đó
    REFUSE_MESSAGE là câu ĐÚNG); làm vỡ `test_grounding_guard:137`
  · bắn trúng câu hỏi TỒN-TẠI (id139: `ky_vong` đòi nguyên văn "PHẢI NÓI RÕ KHÔNG CÓ", `loi_san='ảo giác'`)
  · REFUSE_MESSAGE gánh HAI vai: >=22/36 lượt REFUSE toàn corpus nằm trên id mà `ky_vong` ĐÒI khẳng
    định-vắng-mặt ⇒ một thông điệp không phục vụ được cả hai quần thể.

⇒ A2 chỉ kích cho lớp DIỄN GIẢI (`tra_ky_hieu`, `doc_chu_trang_in`) — payload là GIẢI NGHĨA / TIÊU ĐỀ,
  không phải nguồn số ⇒ rổ neo rỗng ở đó là do CHÍNH SÁCH.
  `doc_bang_nhung` / `phat_hien_bang_ve_net` CỐ Ý ĐỨNG NGOÀI: đầu ra hợp lệ của chúng CHÍNH LÀ "có/không
  có bảng" ⇒ khẳng định vắng mặt mới là đáp án.

📌 GIÁ TRỊ THẬT, NÓI THẲNG: bản vá KHÔNG lấy lại câu trả lời đúng nào (0/5 lượt kích đo được). Nó chỉ đổi
   một KHẲNG ĐỊNH SAI VỀ BẢN VẼ thành câu TRUNG THỰC.

⚠ HELPER: `run_e2e` của `test_grounding_guard.py` HARD-CODE tool "tim_kiem" nên KHÔNG tái hiện được lớp
  lỗi này — đó là lý do 6 file test hiện có đều mù. Suite này dùng helper CÓ THAM SỐ TÊN TOOL.

Chạy: python tests/test_neo_rong_tu_choi.py
"""
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import mcp_bridge as B   # noqa: E402

PASS = FAIL = 0
R = B.REFUSE_MESSAGE
KTD = getattr(B, "KHONG_TRA_DUOC", "<CHUA-VA>")   # để file chạy được cả TRƯỚC khi vá


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


class _FC:
    def __init__(self, name, args): self.name, self.args = name, args
class _Part:
    def __init__(self, text=None, function_call=None, thought=False):
        self.text, self.function_call, self.thought = text, function_call, thought
class _Content:
    def __init__(self, parts, role="model"): self.parts, self.role = parts, role
class _Cand:
    def __init__(self, parts, finish_reason=None):
        self.content, self.finish_reason = _Content(parts), finish_reason
class _Resp:
    def __init__(self, parts): self.candidates = [_Cand(parts)]
class _FakeTool:
    def __init__(self, name): self.name = name
class _Bridge:
    """Trả kết quả THEO TÊN TOOL (bản của test_grounding_guard trả cùng một dict cho mọi tool)."""
    def __init__(self, ket_theo_ten):
        self.ket = ket_theo_ten
        self.tools = [_FakeTool(n) for n in ket_theo_ten]   # L0: bridge phải khai báo tool nó dùng
        self.n_call = 0
    def call(self, name, args):
        self.n_call += 1
        return self.ket.get(name, {})


def e2e(ket_theo_ten, answer_text):
    """Mock 1 lượt gọi (có thể NHIỀU tool) rồi 1 lượt trả text -> chạy qua tra_loi_ai thật."""
    parts = [_Part(function_call=_FC(n, {})) for n in ket_theo_ten]
    script = [_Resp(parts), _Resp([_Part(text=answer_text)])]
    st = {"n": 0}
    def fake_gen(client, contents, cfg, mstate):
        r = script[min(st["n"], len(script) - 1)]; st["n"] += 1
        return r
    _sc, _sg, _st = B._get_client, B._gen_fallback, B.gemini_tools
    B._get_client = lambda: object()
    B._gen_fallback = fake_gen
    B.gemini_tools = lambda t: []
    try:
        return B.tra_loi_ai(_Bridge(ket_theo_ten), "câu hỏi test")["answer"]
    finally:
        B._get_client, B._gen_fallback, B.gemini_tools = _sc, _sg, _st


KY = {"ky_hieu": "Ø", "nghia": "đường kính thép tròn"}


def main():
    print("[A2] rổ neo rỗng vì CHÍNH SÁCH -> câu trung thực, KHÔNG khẳng định 'bản vẽ không có'")

    # ══ [D] PHÂN BIỆT ĐƯỢC — mọi ca dưới đây PHẢI ĐỎ nếu gỡ bản vá ═══════════════════════════════
    print("\n-- [D] phân biệt được (đỏ trước khi vá) --")
    a = e2e({"tra_ky_hieu": KY}, "Thép Ø10 là thép tròn, đường kính 10 mm.")
    ok("D1: chỉ gọi tool DIỄN GIẢI -> KHÔNG còn khẳng định 'bản vẽ không có'", a != R, a[:70])
    ok("D2: ... mà là câu TRUNG THỰC 'chưa tra được'", a == KTD, a[:70])
    b = e2e({"doc_chu_trang_in": {"tieu_de": "MẶT BẰNG"}},
            "Bản vẽ là mặt bằng, tỉ lệ 1 trên 100, cao 3 m.")
    ok("D3: tool #35 doc_chu_trang_in cũng thuộc lớp DIỄN GIẢI", b == KTD, b[:70])
    ok("D4: hằng KHONG_TRA_DUOC tồn tại", hasattr(B, "KHONG_TRA_DUOC"))

    src = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    tup = set(re.findall(r'"([a-z_]+)"', re.search(r"fc\.name not in \(([^)]*)\)", src, re.S).group(1)))
    ok("D-drift: _TOOL_DIEN_GIAI ⊆ tuple loại-trừ rổ neo (chống trôi thầm khi tuple đổi)",
       set(B._TOOL_DIEN_GIAI) <= tup, "%s vs %s" % (set(B._TOOL_DIEN_GIAI), tup))
    ok("D-gate: _apply_i1 miễn trừ CẢ hai thông điệp (không dựa vào may)",
       "in (REFUSE_MESSAGE, KHONG_TRA_DUOC)" in src)
    ok("D-site: bản vá cắm ở CẢ HAI call-site của _guard_text",
       src.count("_a2_khong_tra_duoc(_goc, text, tool_numbers, ten_tool_da_goi)") == 2,
       str(src.count("_a2_khong_tra_duoc(_goc,")))

    # ══ [G] CHỐNG HỒI QUY — xanh cả TRƯỚC lẫn SAU, đây là đối chứng chống-mở-rộng ════════════════
    print("\n-- [G] chống hồi quy: A2 KHÔNG được lan sang các lớp khác --")
    ok("G1: id135 gốc — tim_kiem chạy THẬT trả {} + model bịa '-10m' -> VẪN từ chối",
       e2e({"tim_kiem": {}}, "Cao độ thấp nhất là -10m.") == R)
    ok("G2: id139 — doc_bang_nhung là tool PHÁT HIỆN TỒN TẠI -> GIỮ khẳng định vắng mặt",
       e2e({"doc_bang_nhung": {"so_bang": 1}},
           "Bản vẽ có 1 đối tượng nhúng (có thể là bảng thống kê).") == R)
    # ⚠ Câu phải THẬT SỰ kích guard. Bản nháp đầu dùng "2 vùng giống bảng" -> `_answer_numbers` cho
    # do_luong RỖNG ("vùng" không nằm trong danh sách danh từ ĐẾM) -> guard thoát sớm ở `if not do_luong`
    # -> A2 không bao giờ chạy -> ca test ĐỎ vì assert sai, KHÔNG phải vì code sai. Dùng "bảng" (CÓ trong
    # danh sách) thì guard mới kích và ca mới kiểm được đúng điều cần kiểm.
    ok("G3: phat_hien_bang_ve_net cũng là PHÁT HIỆN TỒN TẠI -> GIỮ khẳng định vắng mặt",
       e2e({"phat_hien_bang_ve_net": {"so_vung": 2}}, "Bản vẽ có 2 bảng thống kê.") == R)
    ok("G3b: câu KHÔNG kích guard (danh từ ngoài danh sách đếm) -> A2 cũng không đụng",
       e2e({"phat_hien_bang_ve_net": {"so_vung": 2}},
           "Bản vẽ có 2 vùng giống bảng.") not in (R, KTD))
    ok("G4: BẪY — model TỰ nói nguyên văn câu từ chối -> KHÔNG ghi đè lời từ chối trung thực",
       e2e({"tra_ky_hieu": KY}, R) == R)
    c = e2e({"tra_ky_hieu": KY}, "Thép Ø10 là thép tròn.")
    ok("G5: câu ĐỊNH TÍNH (không số đo) -> guard không kích, A2 cũng không đụng", c not in (R, KTD), c[:60])
    d = e2e({"tra_ky_hieu": KY, "thong_ke_thep": {"tong_kg": 25752.6}},
            "Tổng khối lượng thép là 25752.6 kg.")
    ok("G6: TRỘN có tool CÓ SỐ + câu grounded -> giữ nguyên", d not in (R, KTD), d[:60])
    e = e2e({"tra_ky_hieu": KY, "tim_kiem": {}}, "Cao độ đáy đài là -13.7 m.")
    ok("G7: TRỘN với tim_kiem (⊄ DIỄN GIẢI) + câu bịa -> VẪN từ chối", e == R, e[:60])
    ok("G8: tool CÓ SỐ nhưng model bịa số khác -> VẪN từ chối",
       e2e({"thong_ke_thep": {"tong_kg": 25752.6}}, "Tổng khối lượng là 999.9 kg.") == R)
    f = e2e({"tinh_dai_luong": {"loi": "chưa hỗ trợ đại lượng này"}},
            "Tôi chưa hỗ trợ tính chiều dài dầm.")
    ok("G9: tool ngoài tuple, câu tự-từ-chối -> không đụng", f not in (KTD,), f[:60])

    # ══ [M] HÌNH DẠNG THÔNG ĐIỆP + đối chứng ÂM ═════════════════════════════════════════════════
    print("\n-- [M] hình dạng thông điệp (chống nới cửa id135) --")
    ok("M1: KHÔNG chứa chữ số nào", not any(ch.isdigit() for ch in KTD), KTD)
    ok("M2: _answer_numbers trả RỖNG", B._answer_numbers(KTD) == ([], []))
    ok("M3: ĐIỂM BẤT ĐỘNG — không tự huỷ ở vòng guard sau", B._guard_text(KTD, set()) == KTD)
    ok("M4: KHÔNG khẳng định bản vẽ thiếu dữ liệu",
       "không có" not in KTD.lower() and "bản vẽ không" not in KTD.lower(), KTD)
    ok("M5: có chỉ dẫn người dùng làm gì tiếp", "hỏi lại" in KTD.lower())
    # đối chứng ÂM: chứng minh M1-M3 KHÔNG phải tautology (một chuỗi khác sẽ TRƯỢT)
    xau = "Không tra được, cao độ là -5 m."
    ok("M6: đối chứng ÂM — chuỗi có số thì TRƯỢT M1/M2 (bộ kiểm phân biệt được)",
       any(ch.isdigit() for ch in xau) and B._answer_numbers(xau) != ([], []))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
