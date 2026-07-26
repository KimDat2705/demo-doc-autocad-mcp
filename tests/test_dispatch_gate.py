# -*- coding: utf-8 -*-
"""L0 (kho kiến thức 2026-07-26) — GATE DISPATCH-SIDE: TẤT ĐỊNH, offline, KHÔNG tốn API.
Bối cảnh: _TOOL_KHONG_CHO_LLM chỉ lọc DECLARATION (gemini_tools); vòng dispatch của tra_loi_ai trước đây
thi hành MỌI fc.name model phát -> model/chữ-trong-file có thể gọi tool host-only (hoc_quy_uoc/nap_ban_ve/
thu_hoi_quy_uoc/kiem_tra_handle) bằng cách phát đúng TÊN. L0 chặn TRƯỚC bridge.call.
Chạy: python tests/test_dispatch_gate.py"""
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

PASS = FAIL = 0


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


class _FakeTool:
    def __init__(self, name):
        self.name = name; self.description = ""
        self.inputSchema = {"type": "object", "properties": {}}


def main():
    print("[L0] gate dispatch-side: chỉ thi hành tool ĐÃ khai báo cho LLM")
    import mcp_bridge

    names = ["nap_ban_ve", "tinh_dai_luong", "hoi_de_hoc", "doi_chieu_nghi_ngo",
             "hoc_quy_uoc", "thu_hoi_quy_uoc", "kiem_tra_handle", "tim_kiem"]
    fake = [_FakeTool(n) for n in names]

    # ---- [G1] _ten_tool_cho_llm: loại ĐỦ 4 tool host-only, giữ tool đọc ----
    ten = mcp_bridge._ten_tool_cho_llm(fake)
    _emit("G1a: 4 tool host-only KHÔNG trong tập dispatch",
          ten.isdisjoint({"nap_ban_ve", "hoc_quy_uoc", "thu_hoi_quy_uoc", "kiem_tra_handle"}), str(ten))
    _emit("G1b: tool đọc (tinh_dai_luong/hoi_de_hoc/tim_kiem) CÓ trong tập dispatch",
          {"tinh_dai_luong", "hoi_de_hoc", "doi_chieu_nghi_ngo", "tim_kiem"} <= ten)
    _emit("G1c: tên LẠ (model bịa tên tool) KHÔNG trong tập dispatch", "tool_la_abc" not in ten)
    _emit("G1d: tools rỗng/None -> tập rỗng (fail-closed, không crash)",
          mcp_bridge._ten_tool_cho_llm([]) == set() and mcp_bridge._ten_tool_cho_llm(None) == set())

    # ---- [G2] tập dispatch KHỚP tập declaration (không lệch 2 hàng rào) ----
    decls = mcp_bridge.gemini_tools(fake)
    exposed = {d.name for t in decls for d in t.function_declarations}
    _emit("G2: tập dispatch == tập declaration (2 hàng rào không lệch nhau)", ten == exposed,
          "dispatch=%s declaration=%s" % (sorted(ten), sorted(exposed)))

    # ---- [G3] kết quả từ chối: SẠCH SỐ + không nuôi grounding + dict tươi ----
    r1, r2 = mcp_bridge._loi_tool_host_only(), mcp_bridge._loi_tool_host_only()
    _emit("G3a: câu từ chối KHÔNG chứa chữ số (không thành mỏ neo grounding)",
          not re.search(r"\d", " ".join(str(v) for v in r1.values())))
    _emit("G3b: _collect_numbers(kết quả từ chối) == rỗng (đo THẬT qua hàm thật)",
          mcp_bridge._collect_numbers(r1) == set())
    _emit("G3c: mỗi lần gọi trả dict TƯƠI (chống mutate lây giữa các lượt)", r1 is not r2 and r1 == r2)

    # ---- [G4] source-guard: gate đứng TRƯỚC bridge.call trong vòng fcalls của tra_loi_ai ----
    src = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    i_loop = src.find("for fc in fcalls:")
    i_gate = src.find("fc.name not in _ten_llm", i_loop)
    i_call = src.find("bridge.call(fc.name", i_loop)
    _emit("G4a: trong vòng fcalls, gate 'fc.name not in _ten_llm' đứng TRƯỚC bridge.call",
          0 < i_loop < i_gate < i_call, "loop=%d gate=%d call=%d" % (i_loop, i_gate, i_call))
    i_set = src.find("_ten_llm = _ten_tool_cho_llm(bridge.tools)")
    _emit("G4b: tra_loi_ai khởi tạo _ten_llm từ bridge.tools (không hardcode danh sách)", i_set > 0)
    # nhánh từ chối phải TỰ append FunctionResponse rồi continue (model vẫn nhận phản hồi, hội thoại không gãy)
    i_resp = src.find("_loi_tool_host_only()", i_loop)
    i_cont = src.find("continue", i_resp)
    i_next_try = src.find("try:", i_resp)
    _emit("G4c: nhánh từ chối append FunctionResponse + continue TRƯỚC nhánh try/bridge.call",
          0 < i_resp < i_cont < i_next_try)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
