# -*- coding: utf-8 -*-
"""GROUNDING-GUARD (id135) — chặn bịa CON SỐ ĐO-LƯỜNG không nguồn, AN TOÀN recall. TẤT ĐỊNH, OFFLINE,
KHÔNG gọi API (mock Gemini), KHÔNG cần file hạ tầng (file id135 không có trong corpus).
Chạy:  python tests/test_grounding_guard.py

Kiểm 2 tầng:
  A. UNIT — _answer_numbers / _is_grounded / _collect_numbers / _guard_text (trực tiếp).
  B. E2E-MOCK — tra_loi_ai với client giả: tool trả số X + answer chứa số Y -> guard BAN/KHÔNG theo grounding.
Nguyên tắc: chỉ TỪ CHỐI khi MỌI số (đo-lường lẫn đếm) đều KHÔNG truy được về RAW result tool. Số đếm trơn,
mã-hiệu (B20/M14/1/200/AxB), đổi đơn vị mm<->m, làm tròn -> KHÔNG bị từ chối nhầm (bảo vệ 60/198 câu n_ev=0 đúng)."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge as B

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


# ---- fake resp Gemini (không cần types thật cho phần đọc) ----
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
class _Bridge:
    def __init__(self, result): self.result, self.tools = result, []
    def call(self, name, args): return self.result


def run_e2e(tool_result, answer_text):
    """Mock 1 lượt gọi tool (trả tool_result) rồi 1 lượt trả text -> chạy qua tra_loi_ai, trả answer cuối."""
    script = [_Resp([_Part(function_call=_FC("tim_kiem", {}))]), _Resp([_Part(text=answer_text)])]
    st = {"n": 0}
    def fake_gen(client, contents, cfg, mstate):
        r = script[min(st["n"], len(script) - 1)]; st["n"] += 1
        return r
    _sc, _sg, _st = B._get_client, B._gen_fallback, B.gemini_tools
    B._get_client = lambda: object()
    B._gen_fallback = fake_gen
    B.gemini_tools = lambda t: []
    try:
        return B.tra_loi_ai(_Bridge(tool_result), "câu hỏi test")["answer"]
    finally:
        B._get_client, B._gen_fallback, B.gemini_tools = _sc, _sg, _st


def main():
    global PASS, FAIL
    R = B.REFUSE_MESSAGE

    print("[A] UNIT — trích số đo-lường (phân biệt đo-lường vs đếm vs mã-hiệu)")
    ok("id135 '-10m' -> [-10]", B._answer_numbers("Cao độ thấp nhất là -10m.")[1] == [-10.0])
    ok("đếm '8024 đối tượng, 2355 DIMENSION' -> [] (số nguyên trơn miễn)",
       B._answer_numbers("Bản vẽ có 8024 đối tượng, 2355 DIMENSION.")[1] == [])
    ok("thép 'Ø22 20 thanh 298.4 kg' -> có 298.4, KHÔNG có 22/20",
       298.4 in B._answer_numbers("Ø22 có 20 thanh, 298.4 kg.")[1]
       and 22.0 not in B._answer_numbers("Ø22 có 20 thanh, 298.4 kg.")[1]
       and 20.0 not in B._answer_numbers("Ø22 có 20 thanh, 298.4 kg.")[1])
    ok("mã-hiệu 'B20/M14/1/200/250x186' -> [] (miễn hết)",
       B._answer_numbers("Mác B20 (mác 250), thép M14, tỉ lệ 1/200, tiết diện 250x186x6x6.")[1] == [])
    ok("đếm '3 loại cửa' -> [] (miễn)", B._answer_numbers("Bản vẽ có 3 loại cửa.")[1] == [])
    ok("số nguyên có đơn vị vẫn là đo-lường ('58800 mm')", 58800.0 in B._answer_numbers("Dim lớn nhất 58800 mm.")[1])

    print("[A] UNIT — grounding (đổi đơn vị mm<->m + làm tròn + CÓ DẤU)")
    ok("3.6 truy được 3600 (÷1000)", B._is_grounded(3.6, {3600.0}))
    ok("298.4 truy được 298.44 (làm tròn 1%)", B._is_grounded(298.4, {298.44}))
    ok("58800 truy được 58800", B._is_grounded(58800.0, {58800.0}))
    ok("-10 KHÔNG truy được mốc dương {0,3.6,7.2} (id135 true-positive)", not B._is_grounded(-10.0, {0.0, 3.6, 7.2}))
    ok("-10 KHÔNG truy được +10 (khớp CÓ DẤU)", not B._is_grounded(-10.0, {10.0}))

    print("[A] UNIT — _collect_numbers gom số RAW result (kể cả trong chuỗi)")
    nums = B._collect_numbers({"cac_moc": [{"cao_do": 3.6}], "ghi_chu": "mốc +7.200", "typical_floor_h": 3.6})
    ok("gom giá trị số + số trong chuỗi", 3.6 in nums and 7.2 in nums)
    ok("bool KHÔNG lọt thành 1/0", B._collect_numbers({"co_bang": True, "x": False}) == set())

    print("[A.OLE] U3 — doc_bang_nhung KHÔNG vào rổ grounding (chống flooding sập guard)")
    # Red-team: số ô bảng OLE THÔ (hàng trăm giá trị chưa gán nhãn cột) nếu vào tool_numbers -> số BỊA nào cũng
    # khớp -> guard sập. Fix ở mcp_bridge (vòng tool-use): loại doc_bang_nhung khỏi union tool_numbers.
    _src = open(B.__file__, encoding="utf-8").read()
    # I4a (2026-07-25): exclude đổi từ `!= "doc_bang_nhung"` sang `not in (...)` để LOẠI THÊM phat_hien_bang_ve_net.
    # Grep-guard khoá: doc_bang_nhung VẪN bị loại (dù ở dạng tuple) + phat_hien_bang_ve_net cũng bị loại.
    ok("mcp_bridge LOẠI doc_bang_nhung khỏi tool_numbers (grep-guard)",
       ('fc.name != "doc_bang_nhung"' in _src) or ('not in ("doc_bang_nhung"' in _src))
    ok("mcp_bridge LOẠI phat_hien_bang_ve_net khỏi tool_numbers (I4a grep-guard)",
       '"phat_hien_bang_ve_net"' in _src and 'tool_numbers |= _collect_numbers' in _src)
    # chứng minh vì sao phải loại: 1 bảng OLE nhỏ đã bơm nhiều số vào pool
    _ole = {"so_bang": 1, "bang": [{"handle": "H1", "sheet": "Thep", "nguon": "ole:H1:Thep",
            "cac_hang": [["STT", "KL"], [1, 581.7], [2, 1963.9], [3, 5039.4]]}]}
    ok("_collect_numbers trên 1 bảng OLE bơm NHIỀU số (lý do phải loại)", len(B._collect_numbers(_ole)) >= 4)

    print("[A] UNIT — _guard_text quyết định (BAN chỉ khi mọi số vô căn cứ)")
    ok("BAN id135 (mốc dương, -10 vô căn cứ)", B._guard_text("Cao độ thấp nhất là -10m.", {0.0, 3.6, 7.2}) == R)
    ok("BAN id135 (tool rỗng)", B._guard_text("Cao độ thấp nhất là -10m.", set()) == R)
    ok("GIỮ đếm (8024 grounded)", B._guard_text("Có 8024 đối tượng.", {8024.0}) != R)
    ok("GIỮ thép grounded làm tròn", B._guard_text("Ø22 nặng 298.4 kg.", {298.44}) != R)
    ok("GIỮ đổi đơn vị (3.6m <- 3600)", B._guard_text("Chiều cao tầng 3.6m.", {3600.0}) != R)
    ok("GIỮ any-grounded (634 grounded, 1225 suy được tha)", B._guard_text("Mái 634 m2, ước sàn 1225 m2.", {634.0}) != R)
    ok("GIỮ câu ĐÃ từ chối (không biến thành lỗi khác)",
       B._guard_text("Không có thông tin này trong bản vẽ.", set()) == "Không có thông tin này trong bản vẽ.")
    ok("GIỮ mã-hiệu-only (không có số đo-lường)", B._guard_text("Mác B20 (mác 250), thép M14.", set()) != R)
    # VET: câu ĐẾM đúng + add-on đo-lường vô căn cứ -> GIỮ nhờ NEO là đếm grounded (chống nuke câu đúng)
    ok("GIỮ 'id91-shape' (3305 dim grounded neo, 4200mm vô căn cứ được tha)",
       B._guard_text("Bản vẽ có 3305 đường kích thước, giá trị 4200mm.", {3305.0}) != R)
    # VET: chiều cao tầng (derived) grounded vì tool trả typical_floor_h trong result
    ok("GIỮ chiều cao tầng 3.6m (typical_floor_h trong result)", B._guard_text("Chiều cao tầng là 3.6m.", {3.6}) != R)

    print("[B] E2E-MOCK — qua tra_loi_ai (tool giả + text giả)")
    ok("BAN: tool trả mốc {0,3.6,7.2}, answer 'cao độ -10m'",
       run_e2e({"cac_moc": [{"cao_do": 0.0}, {"cao_do": 3.6}, {"cao_do": 7.2}]}, "Cao độ thấp nhất là -10m.") == R)
    ok("BAN: tool rỗng {}, answer 'cao độ -10m'", run_e2e({}, "Cao độ thấp nhất (sâu nhất) là -10m.") == R)
    ok("GIỮ: tool trả {so_luong:59}, answer '59 đối tượng'",
       run_e2e({"so_luong": 59}, "Bản vẽ có 59 đối tượng DIMENSION.") != R)
    ok("GIỮ: tool trả {tong:8024,dim:2355}, answer '8024 đối tượng, 2355 DIMENSION'",
       run_e2e({"tong": 8024, "dim": 2355}, "Tổng 8024 đối tượng, 2355 DIMENSION.") != R)
    ok("GIỮ: tool trả 3600mm, answer '3.6m' (đổi đơn vị)",
       run_e2e({"kich_thuoc": [{"gia_tri": 3600, "don_vi": "mm"}]}, "Chiều cao là 3.6m.") != R)
    ok("GIỮ: tool trả kg 298.44, answer '298.4 kg' (làm tròn)",
       run_e2e({"thep": [{"duong_kinh": "Ø22", "kg": 298.44, "so_thanh": 20}]}, "Ø22 có 20 thanh, nặng 298.4 kg.") != R)
    ok("GIỮ: answer đếm '3 loại cửa' (không số đo-lường)", run_e2e({"danh_sach": ["D1", "D2", "D3"]}, "Có 3 loại cửa.") != R)
    ok("GIỮ: answer đã từ chối (guard không đụng)",
       run_e2e({}, "Không tìm thấy thông tin cao độ trong bản vẽ.") == "Không tìm thấy thông tin cao độ trong bản vẽ.")
    ok("GIỮ: any-grounded (634 grounded + 1225 suy)",
       run_e2e({"dien_tich": [{"m2": 634}]}, "Diện tích mái 634 m2, ước tính sàn 1225 m2.") != R)

    print("[I1b] VÁ LỖ: 'm2'/'m3' (viết SỐ, không mũ) trước bị _MAHIEU_RES ăn nhầm -> guard MÙ diện-tích/thể-tích bịa")
    ok("do_luong bắt '500 m2' (đơn vị viết số) — TRƯỚC vá = []",
       500.0 in B._answer_numbers("Diện tích sàn là 500 m2.")[1])
    ok("do_luong bắt '12 m3'", 12.0 in B._answer_numbers("Thể tích bê tông 12 m3.")[1])
    ok("do_luong bắt cả 'm2' lẫn 'm²' như nhau",
       B._answer_numbers("500 m2")[1] == B._answer_numbers("500 m²")[1] == [500.0])
    ok("BỊA 'Diện tích sàn 500 m2' (không grounded) -> CHẶN",
       run_e2e({"dien_tich": [{"m2": 634}]}, "Diện tích sàn là 500 m2.") == R)
    ok("BỊA 'thể tích 12 m3' (không grounded) -> CHẶN",
       run_e2e({"thep": [{"kg": 300}]}, "Thể tích bê tông là 12 m3.") == R)
    ok("BỊA 'm2' + handle [72721] KHÔNG che chở (bracket bị strip khỏi neo) -> CHẶN",
       run_e2e({"dien_tich": [{"m2": 634}]}, "Diện tích 500 m2 [72721].") == R)
    ok("GIỮ 'm2' ĐÚNG grounded (tool trả 634) -> KHÔNG chặn",
       run_e2e({"dien_tich": [{"m2": 634}]}, "Diện tích mái là 634 m2.") != R)
    ok("mã-hiệu vẫn KHÔNG lọt do_luong sau vá (B20/Ø22/250x186/1÷200)",
       B._answer_numbers("Mác B20, Ø22, tiết diện 250x186, tỉ lệ 1/200.")[1] == [])
    ok("số ĐẾM trơn '3 phòng' vẫn KHÔNG là đo-lường",
       B._answer_numbers("Bản vẽ có 3 phòng, 5 cửa.")[1] == [])
    # KHOÁ REGRESSION id77 (battery bắt): tiết diện 'AxB mm' KHÔNG được sinh do_luong nhầm từ số thứ 2 -> KHÔNG
    # bị từ chối oan. (Bản vá đầu tiên trích do_luong từ text gốc đã nuke 'Cột 220x220 mm' — sai; đã sửa.)
    ok("SECTION '220x220 mm' -> do_luong RỖNG (không nuke câu tiết diện đúng)",
       B._answer_numbers("Cột C1 tiết diện 220x220 mm [3A044].")[1] == [])
    ok("SECTION '900x2200 mm' -> do_luong RỖNG", B._answer_numbers("Cửa rộng 900x2200 mm.")[1] == [])
    ok("SECTION '220x220 mm' grounded 220 -> GIỮ (không CHẶN)",
       run_e2e({"tiet_dien": [{"a": 220, "b": 220}]}, "Cột C1 tiết diện 220x220 mm.") != R)

    if FAIL:
        print("\n%d PASS / %d FAIL" % (PASS, FAIL))
        return 1
    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
