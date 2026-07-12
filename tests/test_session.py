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

    def close(self):
        self.closed = True


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
    _ms, _ttl = A.MAX_SESSIONS, A.SESSION_TTL_MIN
    A._make_bridge = lambda: FakeBridge()
    A.mcp_bridge.tra_loi_ai = _fake_tra_loi
    A.mcp_bridge.USE_AI = True
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
        bra = a1.split("br=")[1].split("|")[0]; brb = b1.split("br=")[1].split("|")[0]
        ok("A và B dùng BRIDGE KHÁC nhau (không chung subprocess)", bra != brb, "brA=%s brB=%s" % (bra, brb))

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

        print("[K.6] hằng số MAX_SESSIONS/SESSION_TTL_MIN là int")
        ok("MAX_SESSIONS int", isinstance(A.MAX_SESSIONS, int))
        ok("SESSION_TTL_MIN int", isinstance(A.SESSION_TTL_MIN, int))
    finally:
        _reset()
        A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI = _mk, _tl, _ua
        A.MAX_SESSIONS, A.SESSION_TTL_MIN = _ms, _ttl
        for nm in upl:
            try:
                os.remove(os.path.join(A.UPLOAD_DIR, nm))
            except OSError:
                pass

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
