# -*- coding: utf-8 -*-
"""Robustness H — CHUỖI MODEL DỰ PHÒNG (429/503) — test TẤT ĐỊNH, OFFLINE, KHÔNG gọi API (mock client).
Chạy:  python tests/test_model_fallback.py
Kiểm: nhận đúng lỗi quá-tải; nhảy model kế khi 429/503; NÉM khi hết model / lỗi khác; state không dò lại
model đã hỏng; chuỗi 1-model = hành vi cũ. (Không cần GEMINI_API_KEY — chỉ dùng logic thuần + client giả.)"""
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


class ApiErr(Exception):
    """Giả lập google.genai APIError: có .code = mã HTTP."""
    def __init__(self, code, msg=""):
        self.code = code
        super().__init__(msg or ("HTTP %d" % code))


class FakeModels:
    def __init__(self, script):
        self.script = script          # {model: "ok" | Exception-instance}
        self.calls = []

    def generate_content(self, model, contents, config):
        self.calls.append(model)
        beh = self.script.get(model, "ok")
        if beh == "ok":
            return {"_model": model}  # resp giả (chỉ cần khác None + phân biệt model)
        raise beh


class FakeClient:
    def __init__(self, script):
        self.models = FakeModels(script)


def main():
    global PASS, FAIL
    print("[H.1] _is_overloaded — nhận 429/503/5xx (đáng thử model khác), LOẠI lỗi khác")
    ok("429 -> overloaded", B._is_overloaded(ApiErr(429)))
    ok("503 -> overloaded", B._is_overloaded(ApiErr(503)))
    for c in (500, 502, 504):
        ok("%d -> overloaded" % c, B._is_overloaded(ApiErr(c)))
    ok("400 (bad request) -> KHÔNG", not B._is_overloaded(ApiErr(400)))
    ok("404 (model không tồn tại) -> KHÔNG", not B._is_overloaded(ApiErr(404)))
    ok("chuỗi 'RESOURCE_EXHAUSTED' -> overloaded", B._is_overloaded(Exception("429 RESOURCE_EXHAUSTED: quota")))
    ok("chuỗi '503 high demand' -> overloaded", B._is_overloaded(Exception("503 model overloaded, high demand")))
    ok("lỗi SAFETY thường -> KHÔNG (fallback không giúp)", not B._is_overloaded(Exception("SAFETY blocked content")))

    _save = B.MODELS
    B.MODELS = ["m0", "m1", "m2"]      # cố định để test tất định (độc lập env)
    try:
        print("[H.2] primary OK -> dùng m0, KHÔNG dò model khác")
        c = FakeClient({}); st = {"i": 0}
        r = B._gen_fallback(c, [], None, st)
        ok("resp m0 + calls=[m0] + i=0", r == {"_model": "m0"} and c.models.calls == ["m0"] and st["i"] == 0, c.models.calls)

        print("[H.3] primary 429 -> nhảy m1")
        c = FakeClient({"m0": ApiErr(429)}); st = {"i": 0}
        r = B._gen_fallback(c, [], None, st)
        ok("resp m1 + calls=[m0,m1] + i=1", r == {"_model": "m1"} and c.models.calls == ["m0", "m1"] and st["i"] == 1, c.models.calls)

        print("[H.4] m0=429 + m1=503 -> nhảy m2")
        c = FakeClient({"m0": ApiErr(429), "m1": ApiErr(503)}); st = {"i": 0}
        r = B._gen_fallback(c, [], None, st)
        ok("resp m2 + calls=[m0,m1,m2] + i=2", r == {"_model": "m2"} and c.models.calls == ["m0", "m1", "m2"] and st["i"] == 2, c.models.calls)

        print("[H.5] MỌI model quá tải -> NÉM lỗi quá-tải (app.py báo 'quá tải', KHÔNG bịa)")
        c = FakeClient({"m0": ApiErr(429), "m1": ApiErr(503), "m2": ApiErr(429)}); st = {"i": 0}
        raised = False
        try:
            B._gen_fallback(c, [], None, st)
        except Exception as e:
            raised = B._is_overloaded(e)
        ok("ném lỗi quá-tải + đã thử cả 3 model", raised and c.models.calls == ["m0", "m1", "m2"], c.models.calls)

        print("[H.6] lỗi 400 (không quá-tải) -> NÉM NGAY, KHÔNG nhảy model")
        c = FakeClient({"m0": ApiErr(400)}); st = {"i": 0}
        raised = False
        try:
            B._gen_fallback(c, [], None, st)
        except Exception as e:
            raised = not B._is_overloaded(e)
        ok("ném ngay + chỉ gọi m0 (fallback vô ích cho lỗi này)", raised and c.models.calls == ["m0"], c.models.calls)

        print("[H.7] state GIỮ model đang dùng — lượt sau KHÔNG dò lại model đã hỏng")
        c = FakeClient({"m0": ApiErr(429)}); st = {"i": 0}
        B._gen_fallback(c, [], None, st)          # lượt 1: m0 hỏng -> m1, i=1
        r = B._gen_fallback(c, [], None, st)      # lượt 2: bắt đầu từ m1
        ok("lượt 2 bắt đầu m1, KHÔNG gọi lại m0", r == {"_model": "m1"} and c.models.calls == ["m0", "m1", "m1"] and st["i"] == 1, c.models.calls)

        print("[H.8] chuỗi 1 model (không cấu hình phụ) -> hành vi CŨ: ném khi quá tải")
        B.MODELS = ["only"]
        c = FakeClient({"only": ApiErr(503)}); st = {"i": 0}
        raised = False
        try:
            B._gen_fallback(c, [], None, st)
        except Exception as e:
            raised = B._is_overloaded(e)
        ok("ném + chỉ gọi 'only' (không có model phụ để nhảy)", raised and c.models.calls == ["only"], c.models.calls)
    finally:
        B.MODELS = _save

    print("[H.9] cấu hình chuỗi — MODEL đứng ĐẦU, không trùng lặp, có model phụ mặc định")
    ok("MODELS[0] == MODEL", B.MODELS[0] == B.MODEL)
    ok("không trùng lặp trong chuỗi", len(B.MODELS) == len(set(B.MODELS)), B.MODELS)
    ok("_FALLBACK_DEFAULT có ≥1 model phụ", len([m for m in B._FALLBACK_DEFAULT.split(",") if m.strip()]) >= 1)

    print("[H.10] EMPTY-RESPONSE NUDGE — Gemini trả part 'thought' RỖNG lượt đầu -> NHẮC 1 lần rồi phục hồi (E2E bug)")
    class _P:                                     # fake Part (text/thought/function_call)
        def __init__(s, text="", thought=False): s.text = text; s.thought = thought; s.function_call = None
    class _CT:
        def __init__(s, parts): s.parts = parts
    class _C:
        def __init__(s, parts, fin=None): s.content = _CT(parts); s.finish_reason = fin
    class _R:
        def __init__(s, cand): s.candidates = [cand]
    class _Bridge:
        tools = []
        def call(s, *a, **k): return {}
    _scr = [[_R(_C([_P(thought=True)])), _R(_C([_P(text="Đã đánh dấu vị trí cửa trên bản vẽ.")]))]]  # rỗng->nhắc->text
    _seq = [0]
    _saveg, _savec = B._gen_fallback, B._get_client
    B._get_client = lambda: None
    def _fg(cl, co, cf, st):
        r = _scr[0][min(_seq[0], len(_scr[0]) - 1)]; _seq[0] += 1; return r
    B._gen_fallback = _fg
    try:
        r = B.tra_loi_ai(_Bridge(), "Đánh dấu cửa")
        ok("empty lượt đầu -> NHẮC rồi trả text (KHÔNG 'không đưa ra nội dung')",
           r["answer"] == "Đã đánh dấu vị trí cửa trên bản vẽ." and _seq[0] == 2, (r["answer"][:40], _seq[0]))
        _seq[0] = 0; _scr[0] = [_R(_C([_P(thought=True)])), _R(_C([_P(thought=True)]))]   # rỗng CẢ 2 lượt
        r = B.tra_loi_ai(_Bridge(), "Đánh dấu cửa")
        ok("empty CẢ 2 lượt -> mới báo 'không đưa ra nội dung' (nhắc ĐÚNG 1 lần, không lặp vô hạn)",
           "không đưa ra nội dung" in r["answer"] and _seq[0] == 2, (r["answer"][:40], _seq[0]))
    finally:
        B._gen_fallback, B._get_client = _saveg, _savec

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
