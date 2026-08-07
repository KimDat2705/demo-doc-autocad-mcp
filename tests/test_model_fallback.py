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
    # ⚠ D10 CŨ ĐÃ BỊ THAY (2026-08-07) — nó ghim chuỗi "gemini-2.5" và soi `_FALLBACK_DEFAULT`,
    # nên MÙ ĐÚNG CHIỀU NGUY HIỂM: đặt env GEMINI_MODEL=gemini-3.6-flash mà giữ dự phòng 2.5 thì
    # chuỗi THẬT trộn thế hệ nhưng cổng vẫn XANH; ngược lại sửa cho ĐÚNG (chuỗi 3.x) lại ĐỎ OAN.
    # Bản mới soi `MODELS` (đại lượng THẬT, đã gộp env) và so THẾ HỆ với chính `MODELS[0]`.
    # Xem nhóm [G] ở cuối file.

    # ══ [N] `_is_overloaded` KHỚP CHUỖI CON — số trong lỗi 400 bị nhận nhầm là quá tải ═══
    # Đo thật: '15042' chứa chuỗi con '504' ⇒ lỗi CẤU HÌNH VĨNH VIỄN bị xử như quá tải ⇒ máy
    # nói "thử lại sau ít phút" = SAI SỰ THẬT, chờ không hết. Gemini 3 sinh lỗi 400 mang SỐ
    # nhiều hơn hẳn 2.5 (đếm token / ngân sách / thought signature) nên lớp lỗi này nóng lên.
    print("\n-- [N] _is_overloaded: số nằm TRONG số khác không được tính là mã lỗi --")
    ok("N1 '400 ... token count 15042 exceeds limit' -> KHÔNG phải quá tải (bug: 15042 ⊃ 504)",
       not B._is_overloaded(Exception("400 INVALID_ARGUMENT: token count 15042 exceeds limit")))
    ok("N2 '400 ... maximum 502400 tokens' -> KHÔNG phải quá tải",
       not B._is_overloaded(Exception("400 INVALID_ARGUMENT: maximum 502400 tokens")))
    ok("N3 số thực '1.5039' -> KHÔNG phải quá tải", not B._is_overloaded(Exception("cost 1.5039 usd")))
    ok("N4 ĐỐI CHỨNG: '429 RESOURCE_EXHAUSTED' vẫn là quá tải",
       B._is_overloaded(Exception("429 RESOURCE_EXHAUSTED: quota")))
    ok("N5 ĐỐI CHỨNG: '503 model overloaded, high demand' vẫn là quá tải",
       B._is_overloaded(Exception("503 model overloaded, high demand")))
    ok("N6 ĐỐI CHỨNG: mã nằm trong JSON lỗi thật \"{'code': 429,\" vẫn bắt được",
       B._is_overloaded(Exception("ClientError: {'error': {'code': 429, 'status': 'RESOURCE_EXHAUSTED'}}")))
    ok("N7 ĐỐI CHỨNG: 'HTTP/1.1 503 Service Unavailable' vẫn bắt được",
       B._is_overloaded(Exception("HTTP/1.1 503 Service Unavailable")))
    ok("N8 ĐỐI CHỨNG: thuộc tính .code vẫn thắng chuỗi (đường chính, không đụng)",
       B._is_overloaded(ApiErr(503)) and not B._is_overloaded(ApiErr(400)))

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
    # ⛔ ĐÍNH CHÍNH 2026-08-07 — ĐỌC TRƯỚC KHI DỰA VÀO CA NÀY. `temperature=0` KHÔNG CÒN là
    # "hàng rào chống bịa" từ khi model chính lên Gemini 3: đo thật (prompt entropy cao, 5 lượt)
    # `gemini-2.5-flash` cho 1 đáp án/5 lần (tất định) còn `gemini-3.6-flash` cho 5 đáp án/5 lần
    # (tản hoàn toàn) ⇒ Gemini 3 BỎ QUA tham số này. Ca F1 nay chỉ khoá "code không đổi giá trị
    # NGẦM", KHÔNG còn khoá tính tất định. Chống bịa dựa HOÀN TOÀN vào hàng rào phía code
    # (grounding-guard / rổ neo). Vẫn TRUYỀN 0: vô hại hôm nay và đúng nếu chuỗi tụt về đời 2.x.
    ok("F1 temperature mặc định = 0 (⚠ Gemini 3 BỎ QUA — ca này chỉ khoá 'không đổi ngầm')",
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

    # ══ [G] CỔNG THẾ HỆ — thay D10 cũ (đo được là MÙ đúng chiều nguy hiểm) ═══════════════
    # Gemini 3 đính thought signature vào mỗi function_call và TỪ CHỐI chữ ký model khác.
    # Bản vá chạy-lại-từ-đầu ([E]) đỡ được nhánh CÓ GỌI TOOL, nhưng chạy lại = gọi lại TOÀN BỘ
    # tool (×2 thời gian, ×2 RAM, ×2 tác dụng phụ ghi ảnh/Excel). Nên chuỗi CÙNG THẾ HỆ vẫn là
    # cấu hình ĐÚNG: nó tránh hẳn đường chạy-lại thay vì chỉ xử lý được nó.
    print("\n-- [G] chuỗi model phải CÙNG THẾ HỆ — soi MODELS (đại lượng thật), không soi hằng --")
    ok("G1 _the_he đọc đúng đời model", [B._the_he(m) for m in
       ("gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash")]
       == ["3", "3", "2", "2"],
       [B._the_he(m) for m in ("gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash")])
    ok("G2 _the_he trả None cho tên không đọc được (KHÔNG đoán bừa)",
       B._the_he("mo-hinh-la") is None and B._the_he("") is None and B._the_he(None) is None)
    ok("G3 chuỗi 3.x thuần -> ĐẠT",
       B._chuoi_cung_the_he(["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]))
    # ⭐ CA QUYẾT ĐỊNH: đúng trạng thái mà cổng D10 CŨ để lọt (env đổi model chính, quên đổi dự phòng)
    ok("G4 ⭐ chuỗi TRỘN 3.6 -> 2.5-lite (D10 cũ để LỌT) -> phải BỊ BẮT",
       not B._chuoi_cung_the_he(["gemini-3.6-flash", "gemini-2.5-flash-lite"]))
    ok("G5 chuỗi 2.5 thuần (cấu hình CŨ) -> vẫn ĐẠT (bản mới không đỏ oan cấu hình cũ)",
       B._chuoi_cung_the_he(["gemini-2.5-flash", "gemini-2.5-flash-lite"]))
    ok("G6 chuỗi 1 model -> ĐẠT (không có gì để trộn)", B._chuoi_cung_the_he(["gemini-3.6-flash"]))
    ok("G7 tên không đọc được thế hệ -> KHÔNG ĐẠT (fail-closed, bắt khai báo rõ)",
       not B._chuoi_cung_the_he(["gemini-3.6-flash", "mo-hinh-la"]))
    # ⭐ G11 do TỰ-KIỂM-NGƯỢC bắt ra: G7 ở trên KHÔNG hề khoá được vế "trả None". Mutation đổi
    # `_the_he` từ None sang '0' vẫn để G7 XANH, vì '0' != '3' nên chuỗi vẫn bị coi là trộn.
    # Ca DUY NHẤT phân biệt được là CẢ HAI tên đều không đọc nổi: fail-closed thì False, còn
    # đoán-bừa-một-giá-trị-chung thì True. Không có ca này thì bất biến fail-closed là vô chủ.
    ok("G11 ⭐ CẢ CHUỖI không đọc được thế hệ -> vẫn KHÔNG ĐẠT (khoá đúng vế 'trả None')",
       not B._chuoi_cung_the_he(["mo-hinh-la", "mo-hinh-khac"]))
    # Soi CẤU HÌNH THẬT đang chạy — đây mới là thứ D10 lẽ ra phải kiểm từ đầu
    ok("G8 ⭐ MODELS THẬT (đã gộp env GEMINI_MODEL/GEMINI_FALLBACK_MODELS) cùng thế hệ",
       B._chuoi_cung_the_he(B.MODELS), B.MODELS)
    ok("G9 MODELS[0] == MODEL và không trùng lặp (giữ hợp đồng H.9)",
       B.MODELS[0] == B.MODEL and len(B.MODELS) == len(set(B.MODELS)), B.MODELS)
    ok("G10 mặc định code: model chính là 3.6-flash (GA, thay 2.5-flash)",
       B.MODEL == "gemini-3.6-flash" or os.environ.get("GEMINI_MODEL"), B.MODEL)

    # ══ [P] TÍN HIỆU CHẠY-LẠI KHÔNG ĐƯỢC NUỐT + contents NHIỄM PHẢI ĐƯỢC KHAI BÁO ════════
    print("\n-- [P] chạy-lại-từ-đầu: 2 đường nhắc phải khai contents nhiễm; lượt ép-cuối không nuốt --")
    _saveg, _savec, _savet = B._gen_fallback, B._get_client, B.MAX_TURNS
    B._get_client = lambda: None
    _cap = []

    def _fg_bat(cl, co, cf, st):
        """Ghi lại cờ da_goi_tool TẠI MỖI lượt để xem đường nhắc có khai báo nhiễm không."""
        _cap.append(bool(st.get("da_goi_tool")))
        i = len(_cap) - 1
        return _kb_script[min(i, len(_kb_script) - 1)]
    try:
        # (a) đường nhắc 'CHƯA gọi tool mà nêu số' — append cand.content của model ⇒ contents NHIỄM
        _cap[:] = []
        _kb_script = [_R(_C([_P(text="Có 12 cột.")])), _R(_C([_P(text="Không có thông tin này trong bản vẽ.")]))]
        B._gen_fallback = _fg_bat
        B.tra_loi_ai(_Bridge(), "Mấy cột?")
        ok("P1 sau nhắc 'chưa gọi tool' -> lượt sau PHẢI thấy da_goi_tool=True (contents đã nhiễm)",
           _cap == [False, True], _cap)
        # (b) đường nhắc RỖNG — cũng append cand.content
        _cap[:] = []
        _kb_script = [_R(_C([_P(thought=True)])), _R(_C([_P(text="Đã trả lời.")]))]
        B.tra_loi_ai(_Bridge(), "Hỏi gì đó")
        ok("P2 sau nhắc RỖNG -> lượt sau PHẢI thấy da_goi_tool=True",
           _cap == [False, True], _cap)
        # (c) ĐỐI CHỨNG: không nhắc lần nào thì KHÔNG được tự bật cờ
        _cap[:] = []
        _kb_script = [_R(_C([_P(text="Trả lời thẳng, không số.")]))]
        B.tra_loi_ai(_Bridge(), "Hỏi gì đó")
        ok("P3 ĐỐI CHỨNG: trả lời thẳng, không nhắc -> cờ vẫn False (không bật bừa)",
           _cap == [False], _cap)
        # (d) lượt ÉP-TRẢ-LỜI CUỐI: _CanChayLaiTuDau KHÔNG được `except Exception: pass` nuốt
        _FC2 = type("FC", (), {"__init__": lambda s, n: (setattr(s, "name", n), setattr(s, "args", {}))[0]})
        _pf2 = _P(); _pf2.function_call = _FC2("tim_kiem")
        B.MAX_TURNS = 1
        _lan = [0]

        def _fg_cuoi(cl, co, cf, st):
            _lan[0] += 1
            if _lan[0] == 1:
                st["da_goi_tool"] = True
                return _R(_C([_pf2]))          # lượt tool -> hết MAX_TURNS -> vào ép-trả-lời cuối
            raise B._CanChayLaiTuDau(1)        # lượt ép-cuối gặp 429 -> tín hiệu tụt model
        B._gen_fallback = _fg_cuoi
        _save1 = B._tra_loi_ai_mot_lan
        _bd = []
        _thuc = B._tra_loi_ai_mot_lan

        def _theo_doi(bridge, q, fs="", hist=None, model_bat_dau=0):
            _bd.append(model_bat_dau)
            if len(_bd) == 1:
                return _thuc(bridge, q, fs, hist, model_bat_dau)
            return {"answer": "đã chạy lại trên model kế", "evidence": [], "ai": True}
        B._tra_loi_ai_mot_lan = _theo_doi
        try:
            r = B.tra_loi_ai(_Bridge(), "Móng gồm gì?")
            ok("P4 ⭐ tín hiệu chạy-lại ở lượt ÉP-CUỐI không bị nuốt -> chạy lại trên model kế",
               r.get("answer") == "đã chạy lại trên model kế" and _bd == [0, 1], (r.get("answer"), _bd))
        finally:
            B._tra_loi_ai_mot_lan = _save1
    finally:
        B._gen_fallback, B._get_client, B.MAX_TURNS = _saveg, _savec, _savet

    # ══ [Q] TỤT MODEL PHẢI LỘ — không được âm thầm đổi chất lượng ═══════════════════════
    # 3.6-flash 164/172 số đúng vs 3.5-flash-lite 155/172 + BỊA HANDLE 2 ca. Một câu do model
    # dự phòng viết ra mà không phân biệt được = vi phạm "thất bại phải LỘ" của chính dự án.
    print("\n-- [Q] payload phải khai model NÀO đã trả lời --")
    _saveg, _savec, _saveM = B._gen_fallback, B._get_client, B.MODELS
    B._get_client = lambda: None
    try:
        B.MODELS = ["mChinh", "mPhu"]
        _st_gia = [0]

        def _fg_q(cl, co, cf, st):
            st["i"] = _st_gia[0]
            return _R(_C([_P(text="Bản vẽ có hai bảng thép.")]))
        B._gen_fallback = _fg_q
        _st_gia[0] = 0
        r = B.tra_loi_ai(_Bridge(), "Có bảng gì?")
        ok("Q1 chạy trên model CHÍNH -> payload khai đúng tên", r.get("model_da_dung") == "mChinh", r.get("model_da_dung"))
        _st_gia[0] = 1
        r = B.tra_loi_ai(_Bridge(), "Có bảng gì?")
        ok("Q2 ⭐ ĐÃ TỤT sang model phụ -> payload khai model PHỤ (không im lặng)",
           r.get("model_da_dung") == "mPhu", r.get("model_da_dung"))
        # Q3 do RED-TEAM bắt: bản đầu dùng MODELS[i] trần nên i=-1 trả model CUỐI (chỉ số âm
        # của Python) — trường dựng ra để LỘ sự thật mà khai SAI TÊN thì tệ hơn không khai.
        ok("Q3 ⭐ chỉ số RÁC (-1 / vượt trần / không phải int) -> trả None, KHÔNG đoán bừa",
           all(B._model_dang_dung(s) is None for s in
               ({"i": -1}, {"i": 99}, {"i": "x"}, {"i": None}, {"i": True})),
           [B._model_dang_dung(s) for s in ({"i": -1}, {"i": 99}, {"i": "x"}, {"i": None}, {"i": True})])
        # ⭐ Q4 — TRIPWIRE do RED-TEAM sinh ra. Tên model 'gemini-3.6-flash' CHỨA CHỮ SỐ, và
        # `_collect_numbers` trên nó cho ra {3.6} — đúng dải mà chính dự án dùng làm ca thử
        # ('3.6m' trong I3-U). Hôm nay nó VÔ HẠI vì rổ neo chỉ dựng từ RAW result của tool, không
        # từ payload trả về. Ca này KHOÁ điều đó lại: nếu ai đó về sau đưa `model_da_dung` vào
        # tool result / `ghi_chu` / rổ neo thì câu bịa '3.6' sẽ ĐƯỢC BẢO LÃNH và ca này ĐỎ.
        # Đây đúng khuôn "rổ neo bị bơm từ ngoài" — kênh thứ 5, chặn trước khi nó kịp mở.
        _FC3 = type("FC", (), {"__init__": lambda s, n: (setattr(s, "name", n), setattr(s, "args", {}))[0]})
        _pf3 = _P(); _pf3.function_call = _FC3("tim_kiem")
        _b_rong = type("BR", (), {"tools": [], "call": lambda s, *a, **k: {"ket_qua": []}})()
        _sq = [0]

        def _fg_bia(cl, co, cf, st):
            _sq[0] += 1
            return _R(_C([_pf3])) if _sq[0] == 1 else _R(_C([_P(text="Cao độ đáy móng là -3.6 m.")]))
        B._gen_fallback = _fg_bia
        r = B.tra_loi_ai(_b_rong, "Cao độ đáy móng?")
        ok("Q4 ⭐ tool KHÔNG trả số nào -> câu '-3.6 m' vẫn BỊ CHẶN (tên model không thành neo)",
           "3.6" not in r["answer"], r["answer"][:100])
    finally:
        B._gen_fallback, B._get_client, B.MODELS = _saveg, _savec, _saveM

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
