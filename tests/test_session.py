# -*- coding: utf-8 -*-
"""Robustness K — TÁCH STATE THEO SESSION. TẤT ĐỊNH, OFFLINE, KHÔNG tốn API / KHÔNG spawn MCP subprocess.
Chạy:  python tests/test_session.py
Dùng Flask test_client (mỗi client = 1 cookie jar = 1 trình duyệt/phiên) + FakeBridge (mock, không subprocess)
+ fake tra_loi_ai (echo summary/history/bridge để chứng minh cô lập). Kiểm: 2 phiên KHÔNG đạp nhau, history
riêng, CAP đóng LRU, TTL đóng phiên nhàn rỗi, ask khi chưa nạp -> báo LỘ."""
import os, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import app as A

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


MADE = []            # theo dõi mọi FakeBridge đã tạo


class FakeBridge:
    def __init__(self):
        self.id = len(MADE) + 1
        self.closed = False
        MADE.append(self)

    def call(self, name, args, timeout=120):
        return {"name": os.path.basename(args.get("path", "x")), "dxfversion": "AC1032",
                "tong_doi_tuong": 10, "so_layer": 3}

    def close(self, cho_giay=0.0):
        # Chữ ký PHẢI khớp MCPBridge.close(cho_giay=0.0) — đường nhường-chỗ (lát 2) gọi close(cho_giay=N);
        # fake thiếu tham số thì ném TypeError NGOÀI try/except của route -> Flask trả 500 HTML, test sập kiểu khó đọc.
        self.closed = True
        return True


def _fake_tra_loi(bridge, q, summary="", history=None):
    return {"answer": "sum=%s|hist=%d|br=%d|q=%s" % (summary, len(history or []), getattr(bridge, "id", -1), q),
            "evidence": [], "ai": True}


def _reset():
    with A._SESS_LOCK:
        for sid in list(A.SESSIONS):
            A._close_session(sid)
    MADE.clear()


def _upload(client, fname):
    return client.post("/upload", data={"file": (io.BytesIO(b"0" * 100), fname)},
                       content_type="multipart/form-data")


def _ask(client, q):
    return client.post("/ask", json={"q": q})


def main():
    global PASS, FAIL
    # cài mock: bridge giả + tra_loi_ai giả + bật USE_AI
    _mk, _tl, _ua = A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI
    _ms, _ttl, _mbv = A.MAX_SESSIONS, A.SESSION_TTL_MIN, A.MAX_BAN_VE
    A._make_bridge = lambda: FakeBridge()
    A.mcp_bridge.tra_loi_ai = _fake_tra_loi
    A.mcp_bridge.USE_AI = True
    # ⚠ K.1-K.8 kiểm TRẦN SỐ PHIÊN + bất biến F-A, cần ≥2 phiên CÙNG giữ bản vẽ. Trần SỐ BẢN VẼ (MAX_BAN_VE,
    # mặc định 1 cho gói free 512MB) làm điều đó bất khả thi theo THIẾT KẾ — nên ở đây mở rộng nó ra.
    # TRẦN SỐ BẢN VẼ có suite RIÊNG: tests/test_admission.py (A.1-A.11), gồm cả ca "B upload đuổi bản vẽ của A".
    # Đặt cao (không phải 0) để đường code đếm/xin-suất VẪN được chạy trong mọi ca dưới đây.
    A.MAX_BAN_VE = 99
    upl = set()      # tên file test đã tạo trong _uploads (dọn cuối)
    try:
        print("[K.1] 2 PHIÊN cô lập — upload người B KHÔNG đạp bản vẽ/bridge người A")
        _reset()
        A.MAX_SESSIONS = 4
        ca, cb = A.app.test_client(), A.app.test_client()
        ra = _upload(ca, "aaa.dxf"); upl.add("aaa.dxf")
        rb = _upload(cb, "bbb.dxf"); upl.add("bbb.dxf")
        ok("A upload 200 + set cookie sid", ra.status_code == 200 and "sid=" in ra.headers.get("Set-Cookie", ""), ra.status_code)
        ok("B upload 200", rb.status_code == 200)
        ok("2 phiên riêng biệt trong SESSIONS", len(A.SESSIONS) == 2, len(A.SESSIONS))
        a1 = _ask(ca, "hoiA").get_json()["answer"]
        b1 = _ask(cb, "hoiB").get_json()["answer"]
        ok("A hỏi -> echo summary aaa.dxf (KHÔNG phải bbb)", "aaa.dxf" in a1 and "bbb.dxf" not in a1, a1)
        ok("B hỏi -> echo summary bbb.dxf", "bbb.dxf" in b1, b1)
        # PHÒNG THỦ: nếu 2 câu trên vỡ thì 'br=' không có trong answer -> split() ném IndexError và GIẾT cả suite
        # (23/25 assert im lặng, mất luôn độ phủ R11-IDOR/TTL/history). Kiểm trước rồi mới tách.
        if "br=" in a1 and "br=" in b1:
            bra = a1.split("br=")[1].split("|")[0]; brb = b1.split("br=")[1].split("|")[0]
            ok("A và B dùng BRIDGE KHÁC nhau (không chung subprocess)", bra != brb, "brA=%s brB=%s" % (bra, brb))
        else:
            ok("A và B dùng BRIDGE KHÁC nhau (không chung subprocess)", False, "thiếu 'br=': a1=%r b1=%r" % (a1, b1))

        print("[K.2] HISTORY theo phiên — lượt sau thấy lịch sử lượt trước, phiên khác độc lập")
        a2 = _ask(ca, "hoiA2").get_json()["answer"]
        ok("A lượt 2 thấy history=2 (từ lượt 1)", "hist=2" in a2, a2)
        b2 = _ask(cb, "hoiB2").get_json()["answer"]
        ok("B lượt 2 history=2 (độc lập với A)", "hist=2" in b2, b2)

        print("[K.3] CAP + LRU — vượt trần phiên -> đóng phiên CŨ NHẤT (giải phóng subprocess)")
        _reset()
        A.MAX_SESSIONS = 2
        c1, c2, c3 = A.app.test_client(), A.app.test_client(), A.app.test_client()
        _upload(c1, "s1.dxf"); upl.add("s1.dxf")
        _upload(c2, "s2.dxf"); upl.add("s2.dxf")
        _upload(c3, "s3.dxf"); upl.add("s3.dxf")   # phiên thứ 3 -> cap đầy -> đóng LRU
        ok("chỉ giữ MAX_SESSIONS=2 phiên", len(A.SESSIONS) == 2, len(A.SESSIONS))
        ok("đúng 1 bridge bị đóng (LRU evicted)", sum(b.closed for b in MADE) == 1, [b.closed for b in MADE])
        ok("bridge MỚI NHẤT (s3) còn sống", not MADE[-1].closed)

        print("[K.4] TTL — phiên nhàn rỗi quá hạn bị đóng khi có request mới")
        _reset()
        A.MAX_SESSIONS = 4
        A.SESSION_TTL_MIN = 1
        cx = A.app.test_client()
        _upload(cx, "old.dxf"); upl.add("old.dxf")
        sid_old = list(A.SESSIONS)[0]
        br_old = A.SESSIONS[sid_old]["bridge"]
        A.SESSIONS[sid_old]["last"] = time.time() - 9999   # lùi thời gian -> quá TTL
        cy = A.app.test_client()
        _upload(cy, "new.dxf"); upl.add("new.dxf")         # request mới -> sweep phiên cũ
        ok("phiên cũ quá TTL đã bị bỏ", sid_old not in A.SESSIONS)
        ok("bridge phiên cũ đã đóng (giải phóng subprocess)", br_old.closed)

        print("[K.5] ask khi CHƯA nạp bản vẽ -> báo LỘ (không crash, không dùng bridge người khác)")
        _reset()
        A.SESSION_TTL_MIN = 30
        cz = A.app.test_client()
        rz = _ask(cz, "hoi khi chua nap").get_json()
        ok("trả 'Chưa nạp bản vẽ cho phiên này'", "Chưa nạp bản vẽ" in rz.get("answer", ""), rz)
        ok("KHÔNG tạo bridge cho phiên chưa upload", len(MADE) == 0, len(MADE))

        print("[K.7 R11] IDOR — /image//file CHỈ phục vụ artifact CỦA phiên (chống cross-session fetch)")
        _reset()
        A.SESSION_TTL_MIN = 30
        _aid, _fid = "hl_r11test.png", "th_r11test.xlsx"
        A.mcp_bridge.tra_loi_ai = lambda b, q, summary="", history=None: {
            "answer": "x", "evidence": [], "anh_id": _aid, "file_id": _fid, "ai": True}
        _pa, _pf = os.path.join(A.RENDER_DIR, _aid), os.path.join(A.RENDER_DIR, _fid)
        with open(_pa, "wb") as _h: _h.write(b"\x89PNG\r\n\x1a\n")     # file THẬT -> qua cửa isfile (test CỔNG SỞ HỮU)
        with open(_pf, "wb") as _h: _h.write(b"PK\x03\x04")
        try:
            co, ce = A.app.test_client(), A.app.test_client()
            _upload(co, "own.dxf"); upl.add("own.dxf")
            _ask(co, "danh dau cua")          # owner ask -> artifact ghi vào phiên co
            ok("chủ phiên GET /image/<id> -> 200 (sở hữu)", co.get("/image/" + _aid).status_code == 200)
            ok("chủ phiên GET /file/<id> -> 200 (sở hữu)", co.get("/file/" + _fid).status_code == 200)
            ok("phiên KHÁC GET /image/<id> -> 404 (KHÔNG sở hữu, chống IDOR)", ce.get("/image/" + _aid).status_code == 404)
            ok("phiên KHÁC GET /file/<id> -> 404 (KHÔNG sở hữu, chống IDOR)", ce.get("/file/" + _fid).status_code == 404)
            ok("traversal /file/..%2fapp.py -> 404 (không sở hữu + basename)", A.app.test_client().get("/file/..%2fapp.py").status_code == 404)
        finally:
            A.mcp_bridge.tra_loi_ai = _fake_tra_loi
            for _p in (_pa, _pf):
                try: os.remove(_p)
                except OSError: pass

        print("[K.8 F-A] EVICT/TTL KHÔNG đóng phiên đang BẬN (chống đóng subprocess GIỮA request)")
        _reset()
        A.MAX_SESSIONS = 2
        A.SESSION_TTL_MIN = 30
        cb1, cb2 = A.app.test_client(), A.app.test_client()
        _upload(cb1, "busy.dxf"); upl.add("busy.dxf")
        _upload(cb2, "idle.dxf"); upl.add("idle.dxf")
        sid_busy = min(A.SESSIONS, key=lambda k: A.SESSIONS[k]["last"])
        s_busy = A.SESSIONS[sid_busy]; br_busy = s_busy["bridge"]
        s_busy["last"] = 1.0                 # ép CŨ NHẤT -> ứng viên LRU số 1
        s_busy["lock"].acquire()             # giả lập /ask ĐANG CHẠY (giữ lock)
        try:
            c3 = A.app.test_client()
            _upload(c3, "new1.dxf"); upl.add("new1.dxf")   # cap đầy -> evict, nhưng LRU đang BẬN
            ok("phiên BẬN (LRU, giữ lock) KHÔNG bị đóng giữa request", (not br_busy.closed) and sid_busy in A.SESSIONS)
            ok("phiên KHÁC (rảnh) bị đóng thay -> evict NÉ phiên bận", sum(b.closed for b in MADE) == 1)
        finally:
            s_busy["lock"].release()
        with A._SESS_LOCK:                    # nhả lock rồi -> đóng được bình thường
            _done = A._try_close_session(sid_busy)
        ok("sau khi request xong (nhả lock) -> _try_close_session đóng được (bridge.close)", _done is True and br_busy.closed)

        print("[K.6] hằng số MAX_SESSIONS/SESSION_TTL_MIN là int")
        ok("MAX_SESSIONS int", isinstance(A.MAX_SESSIONS, int))
        ok("SESSION_TTL_MIN int", isinstance(A.SESSION_TTL_MIN, int))

        # K.9 — KHOÁ Ý ĐỊNH "không request nào chờ khoá phiên VÔ HẠN". Đo thật trước bản vá: khoá bị giữ 12s làm
        # POST /xac-nhan trả về sau 11.60s và GIỮ CHẾT 1 trong 4 thread gunicorn -> /health vỡ ngưỡng 5s của Render.
        # Khoá TRẦN CHỜ (có giới hạn + trả JSON đủ khoá), KHÔNG khoá con số 3.
        print("[K.9] 3 route KHÔNG chờ khoá phiên VÔ HẠN + body từ chối đủ khoá cho frontend")
        _reset()
        A.MAX_SESSIONS, A.SESSION_TTL_MIN = 4, 30
        _lw = A.LOCK_WAIT_S
        A.LOCK_WAIT_S = 1                     # rút ngắn cho test nhanh
        _tc0 = A._METRICS["tu_choi"]
        try:
            c9 = A.app.test_client()
            _upload(c9, "k9.dxf"); upl.add("k9.dxf"); upl.add("k9b.dxf")
            s9 = list(A.SESSIONS.values())[0]
            s9["lock"].acquire()              # giả lập /ask ĐANG CHẠY (giữ khoá phiên)
            try:
                for ten, goi in (("/upload", lambda: _upload(c9, "k9b.dxf")),
                                 ("/ask", lambda: _ask(c9, "hi")),
                                 ("/xac-nhan", lambda: c9.post("/xac-nhan", json={"kb_id": "x", "option_key": "y", "ma": "z"}))):
                    t0 = time.perf_counter()
                    r9 = goi()
                    dt = time.perf_counter() - t0
                    j9 = r9.get_json() or {}
                    ok("%s: trả về trong <= trần chờ + 1s (KHÔNG nằm chờ vô hạn)" % ten, dt <= A.LOCK_WAIT_S + 1.0, round(dt, 2))
                    ok("%s: HTTP 503 bận — không 500, không treo" % ten, r9.status_code == 503, r9.status_code)
                    ok("%s: body đủ error+answer+loi+ly_do và da_thu_hoi=False (thiếu ly_do -> tái sinh 'undo nói dối')" % ten,
                       all(j9.get(k) for k in ("error", "answer", "loi", "ly_do")) and j9.get("da_thu_hoi") is False, j9)
            finally:
                s9["lock"].release()
            ok("mỗi lần từ chối đều được ĐẾM ở metrics.tu_choi (quan sát chặn oan sau khi deploy)",
               A._METRICS["tu_choi"] == _tc0 + 3, (_tc0, A._METRICS["tu_choi"]))
            r9b = _upload(c9, "k9b.dxf")      # khoá đã nhả -> phải nạp được bình thường trở lại
            ok("nhả khoá xong -> upload lại BÌNH THƯỜNG (trần chờ không dính vĩnh viễn)", r9b.status_code == 200, r9b.status_code)
        finally:
            A.LOCK_WAIT_S = _lw
    finally:
        _reset()
        A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI = _mk, _tl, _ua
        A.MAX_SESSIONS, A.SESSION_TTL_MIN, A.MAX_BAN_VE = _ms, _ttl, _mbv
        for nm in upl:
            for _f in os.listdir(A.UPLOAD_DIR):      # E6: file lưu dạng '<uuid>_<nm>' -> dọn theo hậu tố
                if _f == nm or _f.endswith("_" + nm):
                    try:
                        os.remove(os.path.join(A.UPLOAD_DIR, _f))
                    except OSError:
                        pass

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
