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

    # ══ MODEL BỊ KHAI TỬ (404) — bản vá 2026-08-07 ═══════════════════════════════════════
    # NỀN ĐO THẬT (ngày API được gia hạn): CẢ HAI model dự phòng cũ đều 404 —
    # 'gemini-2.0-flash' nguyên văn "This model ... is no longer available", 'gemini-1.5-flash'
    # "is not found". Trước vá: 404 không nằm trong fail-forward ⇒ một cú 429 trên model chính
    # làm CHẾT LUÔN request thay vì tụt model. Nhóm ca này khoá đúng lỗ đó.
    print("\n-- [404] model bị nhà cung cấp khai tử: PHẢI fail-forward, và PHẢI báo đúng loại --")
    e404 = ApiErr(404, "404 NOT_FOUND. This model models/gemini-2.0-flash is no longer available.")
    e404b = ApiErr(404, "404 NOT_FOUND. models/gemini-1.5-flash is not found for API version v1beta")
    ok("D1 nhận diện model chết (404 'no longer available')", B._model_chet(e404))
    ok("D2 nhận diện model chết (404 'is not found')", B._model_chet(e404b))
    ok("D3 ĐỐI CHỨNG: 404 KHÔNG bị nhận nhầm là quá tải (hai NGHĨA khác nhau)",
       not B._is_overloaded(e404))
    ok("D4 ĐỐI CHỨNG NGƯỢC: 429 vẫn là quá tải, KHÔNG phải model chết",
       B._is_overloaded(ApiErr(429)) and not B._model_chet(ApiErr(429)))
    ok("D5 ĐỐI CHỨNG: 400 (malformed) không thuộc CẢ HAI nhóm -> vẫn ném, không dò model",
       not B._is_overloaded(ApiErr(400)) and not B._model_chet(ApiErr(400)))

    _saveM = B.MODELS
    try:
        B.MODELS = ["m_chinh", "m_chet", "m_song"]
        cl = FakeClient({"m_chinh": ApiErr(429), "m_chet": e404, "m_song": "ok"})
        st = {}
        # ⚠ PHẢI BỌC try: gỡ bản vá fail-forward thì _gen_fallback NÉM ở model chết. Không bọc
        # thì ngoại lệ giết cả suite -> mất luôn D7-D10 và người đọc chỉ thấy "script chết",
        # không thấy ca nào hỏng. Tự kiểm ngược đã bắt đúng điểm yếu này của chính ca test.
        try:
            r = B._gen_fallback(cl, "x", None, st)
        except Exception as ex:
            r = "NÉM:%s" % type(ex).__name__
        # resp giả của FakeModels là {"_model": <tên>} — kiểm ĐÚNG model nào đã phục vụ,
        # chứ không kiểm chuỗi "ok" (bộ giả không trả chuỗi đó).
        ok("D6 chuỗi 429 -> model CHẾT -> model SỐNG: đi hết được tới model sống",
           r == {"_model": "m_song"} and st.get("i") == 2 and cl.models.calls == ["m_chinh", "m_chet", "m_song"],
           (r, st, cl.models.calls))
        ok("D7 vết `tried` ghi đủ cả hai model hỏng (thất bại phải LỘ)",
           [t[0] for t in st.get("tried", [])] == ["m_chinh", "m_chet"], st.get("tried"))
        # MỌI model đều chết -> phải NÉM (để caller trả câu 'lỗi cấu hình', không im lặng)
        st2 = {}
        cl2 = FakeClient({"m_chinh": e404, "m_chet": e404b, "m_song": e404})
        try:
            B._gen_fallback(cl2, "x", None, st2)
            ok("D8 mọi model chết -> phải NÉM", False, "không ném")
        except Exception as ex:
            ok("D8 mọi model chết -> NÉM đúng lỗi cuối (caller trả câu lỗi-cấu-hình)",
               B._model_chet(ex))
    finally:
        B.MODELS = _saveM

    ok("D9 chuỗi dự phòng MẶC ĐỊNH không còn chứa model đã khai tử",
       "gemini-2.0-flash" not in B._FALLBACK_DEFAULT and "gemini-1.5-flash" not in B._FALLBACK_DEFAULT,
       B._FALLBACK_DEFAULT)
    # Cùng THẾ HỆ với model chính: Gemini 3 đính thought-signature và từ chối chữ ký model khác,
    # nên đổi sang 3.x GIỮA CHỪNG một request sẽ 400. Ca này chặn việc vô tình nhét 3.x vào chuỗi.
    ok("D10 model dự phòng CÙNG THẾ HỆ với model chính (chống lỗi thought-signature khi đổi giữa chừng)",
       all(m.startswith("gemini-2.5") for m in B._FALLBACK_DEFAULT.split(",") if m.strip()),
       B._FALLBACK_DEFAULT)

    # ══ GĐ1.2 — ĐỔI MODEL GIỮA CHỪNG PHẢI CHẠY LẠI TỪ ĐẦU (thought signature) ═══════════
    # Gemini 3 đính chữ ký suy luận vào mỗi function_call và TỪ CHỐI chữ ký của model khác
    # ('Corrupted thought signature') ⇒ mang `contents` đã có lượt gọi tool sang model kế = 400.
    print("\n-- [E] đổi model khi ĐÃ gọi tool -> phải CHẠY LẠI TỪ ĐẦU, không mang contents cũ --")
    _saveM = B.MODELS
    try:
        B.MODELS = ["m1", "m2", "m3"]
        # (a) CHƯA gọi tool -> tụt model bình thường, KHÔNG ném tín hiệu (đường cũ giữ nguyên)
        cl = FakeClient({"m1": ApiErr(429), "m2": "ok"})
        st = {"i": 0, "da_goi_tool": False}
        r = B._gen_fallback(cl, "x", None, st)
        ok("E1 chưa gọi tool -> tụt model TẠI CHỖ (không chạy lại, không phí lượt)",
           r == {"_model": "m2"} and st.get("i") == 1, (r, st))
        # (b) ĐÃ gọi tool -> PHẢI ném tín hiệu chạy-lại, KHÔNG được gọi model kế với contents cũ
        cl2 = FakeClient({"m1": ApiErr(429), "m2": "ok"})
        st2 = {"i": 0, "da_goi_tool": True}
        try:
            B._gen_fallback(cl2, "contents_da_nhiem", None, st2)
            ok("E2 đã gọi tool -> phải ném _CanChayLaiTuDau", False, "không ném")
        except B._CanChayLaiTuDau as ex:
            ok("E2 đã gọi tool -> ném _CanChayLaiTuDau trỏ model KẾ",
               ex.chi_so_model == 1, ex.chi_so_model)
            ok("E3 ĐỐI CHỨNG QUYẾT ĐỊNH: model kế KHÔNG hề được gọi với contents nhiễm "
               "(chỉ m1 bị gọi)", cl2.models.calls == ["m1"], cl2.models.calls)
        # (c) lớp bọc tra_loi_ai: nhận tín hiệu -> chạy lại với model_bat_dau ĐÃ TIẾN
        goi = []
        _save1 = B._tra_loi_ai_mot_lan

        def _gia(bridge, q, fs="", hist=None, model_bat_dau=0):
            goi.append(model_bat_dau)
            if len(goi) == 1:
                raise B._CanChayLaiTuDau(1)
            return {"answer": "xong", "evidence": [], "ai": True}
        B._tra_loi_ai_mot_lan = _gia
        try:
            out = B.tra_loi_ai(None, "hỏi")
            ok("E4 lớp bọc chạy lại với model_bat_dau TIẾN LÊN (0 -> 1) rồi trả kết quả",
               out.get("answer") == "xong" and goi == [0, 1], (out, goi))
        finally:
            B._tra_loi_ai_mot_lan = _save1
        # (d) chống lặp vô hạn: tín hiệu KHÔNG tiến -> phải thoát, không quay vòng mãi
        goi2 = []

        def _gia2(bridge, q, fs="", hist=None, model_bat_dau=0):
            goi2.append(model_bat_dau)
            if len(goi2) < 9:
                raise B._CanChayLaiTuDau(0)      # tín hiệu KHÔNG tiến
            return {"answer": "cuoi", "evidence": [], "ai": True}
        B._tra_loi_ai_mot_lan = _gia2
        try:
            B.tra_loi_ai(None, "hỏi")
            ok("E5 tín hiệu không tiến -> KHÔNG lặp vô hạn (thoát sau ít lượt)",
               len(goi2) <= 3, goi2)
        except Exception as ex:
            ok("E5 tín hiệu không tiến -> KHÔNG lặp vô hạn", False, type(ex).__name__)
        finally:
            B._tra_loi_ai_mot_lan = _save1
    finally:
        B.MODELS = _saveM

    # ══ GĐ1.4 — THAM SỐ SINH RA ENV, MẶC ĐỊNH GIỮ NGUYÊN HÀNH VI CŨ ═════════════════════
    print("\n-- [F] tham số sinh ra env: mặc định PHẢI y hệt hành vi trước lát này --")
    ok("F1 temperature mặc định = 0 (lựa chọn CHỐNG BỊA cốt lõi, không được đổi ngầm)",
       B.GEN_TEMPERATURE == 0.0, B.GEN_TEMPERATURE)
    ok("F2 max_output_tokens mặc định = 8192 (không bỏ trống — bỏ trống là treo vô hạn)",
       B.GEN_MAX_OUTPUT_TOKENS == 8192, B.GEN_MAX_OUTPUT_TOKENS)
    ok("F3 thinking_level mặc định RỖNG -> KHÔNG truyền thinking_config (giữ mặc định model)",
       B.GEN_THINKING_LEVEL == "" and B._thinking_cfg() is None, B.GEN_THINKING_LEVEL)
    _sv = B.GEN_THINKING_LEVEL
    try:
        B.GEN_THINKING_LEVEL = "low"
        ok("F4 đặt env -> _thinking_cfg() dựng được ThinkingConfig (đo được mà không sửa code)",
           B._thinking_cfg() is not None)
    finally:
        B.GEN_THINKING_LEVEL = _sv
    ok("F5 _env_float chịu được giá trị rác (không làm chết tiến trình)",
       B._env_float("BIEN_KHONG_TON_TAI_XYZ", "0") == 0.0)

    # ══ 3 LỖI CAO 2026-08-07 — vá TRƯỚC khi đổi model 3.6-flash (nóng lên theo Gemini 3) ═══
    # Nhóm [T] — TIMEOUT: HttpRetryOptions chỉ retry theo MÃ HTTP mà timeout KHÔNG có mã HTTP
    # ⇒ trước vá: không fail-forward, và app.py phơi nguyên văn exception Python ra trình duyệt.
    # 3.6-flash chậm ×2,3 (trung vị 4,7s → 10,8s) nên đuôi phân phối tiến sát trần 60s/lượt.
    print("\n-- [T] timeout: fail-forward như quá tải + câu trung thực khi cạn chuỗi --")
    _ReadTimeout = type("ReadTimeout", (Exception,), {})   # mô phỏng httpx.ReadTimeout (nhận theo TÊN LỚP)
    ok("T1 TimeoutError -> hết giờ", B._het_gio(TimeoutError("timed out")))
    ok("T2 lớp tên ReadTimeout -> hết giờ (nhận theo TÊN LỚP, không cần import httpx)",
       B._het_gio(_ReadTimeout("The read operation timed out")))
    ok("T3 thông điệp 'deadline exceeded' trần (không mã HTTP) -> hết giờ",
       B._het_gio(Exception("Deadline Exceeded")))
    ok("T4 ĐỐI CHỨNG: 400/404-model-chết/safety KHÔNG phải hết giờ",
       not B._het_gio(ApiErr(400)) and not B._het_gio(e404) and not B._het_gio(Exception("SAFETY blocked")))
    ok("T5 ĐỐI CHỨNG: 429 đi đường quá-tải, _het_gio KHÔNG giẫm chân", not B._het_gio(ApiErr(429)))
    _saveM = B.MODELS
    try:
        B.MODELS = ["m1", "m2"]
        cl = FakeClient({"m1": _ReadTimeout("timed out"), "m2": "ok"})
        st = {"i": 0, "da_goi_tool": False}
        try:
            r = B._gen_fallback(cl, "x", None, st)
        except Exception as ex:
            r = "NÉM:%s" % type(ex).__name__
        ok("T6 timeout ở model chính -> TỤT model kế (fail-forward)",
           r == {"_model": "m2"} and cl.models.calls == ["m1", "m2"], (r, cl.models.calls))
        cl2 = FakeClient({"m1": _ReadTimeout("timed out"), "m2": "ok"})
        st2 = {"i": 0, "da_goi_tool": True}
        try:
            B._gen_fallback(cl2, "contents_nhiem", None, st2)
            ok("T7 timeout khi ĐÃ gọi tool -> phải chạy-lại-từ-đầu", False, "không ném")
        except B._CanChayLaiTuDau as ex:
            ok("T7 timeout khi ĐÃ gọi tool -> _CanChayLaiTuDau trỏ model kế, KHÔNG gửi contents nhiễm",
               ex.chi_so_model == 1 and cl2.models.calls == ["m1"], (ex.chi_so_model, cl2.models.calls))
        except Exception as ex:
            ok("T7 timeout khi ĐÃ gọi tool -> phải chạy-lại-từ-đầu", False, type(ex).__name__)
    finally:
        B.MODELS = _saveM
    # T8: cạn CHUỖI vì timeout -> tra_loi_ai phải trả CÂU trung thực, không để exception thô lên app.py
    _saveg, _savec = B._gen_fallback, B._get_client
    B._get_client = lambda: None

    def _fg_to(cl, co, cf, st):
        raise _ReadTimeout("The read operation timed out")
    B._gen_fallback = _fg_to
    try:
        r = B.tra_loi_ai(_Bridge(), "Đếm cột")
        ok("T8 cạn chuỗi vì timeout -> câu trung thực (không exception thô ra trình duyệt)",
           "quá chậm" in r.get("answer", "") and "ReadTimeout" not in r.get("answer", ""),
           str(r.get("answer"))[:90])
    except Exception as ex:
        ok("T8 cạn chuỗi vì timeout -> câu trung thực", False, "ném thô: %s" % type(ex).__name__)
    finally:
        B._gen_fallback, B._get_client = _saveg, _savec

    # Nhóm [C] — MAX_TOKENS mà VẪN CÓ text: trước vá, `if special and not text` VỨT cảnh báo
    # ⇒ câu CỤT được trả về như câu hoàn chỉnh (qua được cả grounding-guard vì số của nó có neo).
    # Vd vi phạm luật R8b của chính dự án: cắt sau vế 'thép tròn' thành khẳng định SAI không dấu vết.
    print("\n-- [C] MAX_TOKENS còn text: NỐI cảnh báo cắt; guard đã refuse thì KHÔNG nối --")
    _seqc = [0]

    def _lam_fg(script):
        def _fg2(cl, co, cf, st):
            r2 = script[min(_seqc[0], len(script) - 1)]
            _seqc[0] += 1
            return r2
        return _fg2
    _saveg, _savec, _savet = B._gen_fallback, B._get_client, B.MAX_TURNS
    B._get_client = lambda: None
    try:
        _seqc[0] = 0
        B._gen_fallback = _lam_fg([_R(_C([_P(text="Bản vẽ có bảng thép hình và bảng thép tròn.")],
                                          fin="MAX_TOKENS"))])
        r = B.tra_loi_ai(_Bridge(), "Có những bảng thép nào?")
        ok("C1 câu bị cắt -> GIỮ nội dung + NỐI cảnh báo bị cắt",
           "bảng thép hình" in r["answer"] and "bị CẮT" in r["answer"], r["answer"][:120])
        _seqc[0] = 0
        B._gen_fallback = _lam_fg([_R(_C([_P(text="Bản vẽ có bảng thép hình và bảng thép tròn.")],
                                          fin="STOP"))])
        r = B.tra_loi_ai(_Bridge(), "Có những bảng thép nào?")
        ok("C2 ĐỐI CHỨNG finish=STOP -> KHÔNG nối cảnh báo", "bị CẮT" not in r["answer"], r["answer"][:120])
        # C3: câu cụt mang SỐ KHÔNG NGUỒN -> guard refuse; cảnh báo cắt KHÔNG được nối vào câu refuse
        # (refuse không phải câu bị cắt — nối vào là gợi ý sai rằng 'bản vẽ có mà bị cắt mất').
        _seqc[0] = 0
        _r_cut_so = _R(_C([_P(text="Diện tích sàn 60.5 m2.")], fin="MAX_TOKENS"))
        B._gen_fallback = _lam_fg([_r_cut_so, _r_cut_so])   # lượt 1 dính nhắc 'chưa gọi tool', lượt 2 vào guard
        r = B.tra_loi_ai(_Bridge(), "Diện tích sàn?")
        ok("C3 guard refuse câu cụt-không-nguồn -> KHÔNG nối cảnh báo cắt vào câu refuse",
           "bị CẮT" not in r["answer"] and "60.5" not in r["answer"], r["answer"][:120])
        # C4: đường ÉP-TRẢ-LỜI cuối (hết MAX_TURNS) cũng phải nối cảnh báo — trước vá nó không đọc finish_reason
        _FC = type("FC", (), {"__init__": lambda s, n: (setattr(s, "name", n), setattr(s, "args", {}))[0]})
        _pf = _P(); _pf.function_call = _FC("tim_kiem")
        _seqc[0] = 0
        B.MAX_TURNS = 1
        B._gen_fallback = _lam_fg([_R(_C([_pf])),
                                   _R(_C([_P(text="Móng gồm đài móng và giằng móng.")], fin="MAX_TOKENS"))])
        r = B.tra_loi_ai(_Bridge(), "Móng gồm gì?")
        ok("C4 đường ép-trả-lời cuối: câu bị cắt cũng phải mang cảnh báo",
           "đài móng" in r["answer"] and "bị CẮT" in r["answer"], r["answer"][:120])
    finally:
        B._gen_fallback, B._get_client, B.MAX_TURNS = _saveg, _savec, _savet

    # Nhóm [M] — MAX_TOKENS RỖNG (thinking ăn hết ngân sách): trước vá là NGÕ CỤT — trả câu lỗi
    # ngay lượt đầu, không nhắc lại, trong khi nhắc-rỗng H.10 chỉ phủ ca finish_reason thường.
    print("\n-- [M] MAX_TOKENS rỗng: NHẮC 1 lần (trả lời ngắn gọn) rồi mới bó tay --")
    _saveg, _savec = B._gen_fallback, B._get_client
    B._get_client = lambda: None
    try:
        _seqc[0] = 0
        B._gen_fallback = _lam_fg([_R(_C([_P(thought=True)], fin="MAX_TOKENS")),
                                   _R(_C([_P(text="Có hai bảng thép trong bản vẽ.")]))])
        r = B.tra_loi_ai(_Bridge(), "Có mấy bảng thép?")
        ok("M1 MAX_TOKENS rỗng lượt đầu -> NHẮC rồi phục hồi câu trả lời",
           r["answer"] == "Có hai bảng thép trong bản vẽ." and _seqc[0] == 2, (r["answer"][:60], _seqc[0]))
        _seqc[0] = 0
        _r_mt = _R(_C([_P(thought=True)], fin="MAX_TOKENS"))
        B._gen_fallback = _lam_fg([_r_mt, _r_mt])
        r = B.tra_loi_ai(_Bridge(), "Có mấy bảng thép?")
        ok("M2 MAX_TOKENS rỗng CẢ 2 lượt -> báo bị cắt (nhắc ĐÚNG 1 lần, không lặp vô hạn)",
           "bị cắt" in r["answer"] and _seqc[0] == 2, (r["answer"][:60], _seqc[0]))
        _CN = type("CN", (), {"__init__": lambda s, fin: (setattr(s, "content", None),
                                                          setattr(s, "finish_reason", fin))[0]})
        _seqc[0] = 0
        B._gen_fallback = _lam_fg([_R(_CN("MAX_TOKENS")),
                                   _R(_C([_P(text="Có hai bảng thép trong bản vẽ.")]))])
        r = B.tra_loi_ai(_Bridge(), "Có mấy bảng thép?")
        ok("M3 MAX_TOKENS mà content=None -> cũng được nhắc-phục-hồi",
           r["answer"] == "Có hai bảng thép trong bản vẽ." and _seqc[0] == 2, (r["answer"][:60], _seqc[0]))
        _seqc[0] = 0
        B._gen_fallback = _lam_fg([_R(_C([_P(thought=True)], fin="SAFETY"))])
        r = B.tra_loi_ai(_Bridge(), "Có mấy bảng thép?")
        ok("M4 ĐỐI CHỨNG: SAFETY rỗng -> trả NGAY thông điệp bộ lọc, KHÔNG tốn lượt nhắc",
           "bộ lọc an toàn" in r["answer"] and _seqc[0] == 1, (r["answer"][:60], _seqc[0]))
    finally:
        B._gen_fallback, B._get_client = _saveg, _savec

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
