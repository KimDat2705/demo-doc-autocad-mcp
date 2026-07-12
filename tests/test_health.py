# -*- coding: utf-8 -*-
"""Robustness L — KEEP-ALIVE + GIÁM SÁT. TẤT ĐỊNH, OFFLINE, KHÔNG tốn API / KHÔNG spawn subprocess.
Chạy:  python tests/test_health.py
Kiểm: /health trả JSON nhẹ (no API); metrics tăng sau upload/ask; self-ping CHỈ chạy khi có URL (nuốt lỗi),
local/test KHÔNG kích; render.yaml healthCheckPath=/health."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import app as A

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


class FakeBridge:
    def __init__(self):
        self.closed = False

    def call(self, name, args, timeout=120):
        return {"name": "x", "dxfversion": "AC1032", "tong_doi_tuong": 1, "so_layer": 1}

    def close(self):
        self.closed = True


def _fake_tra_loi(bridge, q, summary="", history=None):
    return {"answer": "ok", "evidence": [], "ai": True}


def main():
    global PASS, FAIL
    print("[L.1] /health -> 200 + JSON NHẸ (no API, no bản vẽ)")
    r = A.app.test_client().get("/health")
    j = r.get_json() or {}
    ok("HTTP 200", r.status_code == 200, r.status_code)
    ok("ok=True + uptime_s/sessions int + model/use_ai + metrics dict",
       j.get("ok") is True and isinstance(j.get("uptime_s"), int) and isinstance(j.get("sessions"), int)
       and "model" in j and "use_ai" in j and isinstance(j.get("metrics"), dict), j)
    ok("metrics có uploads/asks/errors", all(k in (j.get("metrics") or {}) for k in ("uploads", "asks", "errors")), j.get("metrics"))

    print("[L.2] metrics TĂNG sau upload + ask (giám sát)")
    _mk, _tl, _ua = A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI
    A._make_bridge = lambda: FakeBridge()
    A.mcp_bridge.tra_loi_ai = _fake_tra_loi
    A.mcp_bridge.USE_AI = True
    before = dict(A._METRICS)
    upl = None
    try:
        cc = A.app.test_client()
        cc.post("/upload", data={"file": (io.BytesIO(b"0" * 50), "lh.dxf")}, content_type="multipart/form-data"); upl = "lh.dxf"
        cc.post("/ask", json={"q": "hi"})
    finally:
        A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI = _mk, _tl, _ua
        with A._SESS_LOCK:
            for sid in list(A.SESSIONS):
                A._close_session(sid)
        if upl:
            try:
                os.remove(os.path.join(A.UPLOAD_DIR, upl))
            except OSError:
                pass
    ok("uploads +1", A._METRICS["uploads"] == before["uploads"] + 1, (before["uploads"], A._METRICS["uploads"]))
    ok("asks +1", A._METRICS["asks"] == before["asks"] + 1, (before["asks"], A._METRICS["asks"]))

    print("[L.3] self-ping: KHÔNG ping khi CHƯA cấu hình URL; ping /health khi CÓ (nuốt lỗi)")
    _u = A._KEEPALIVE_URL
    import urllib.request
    _uo = urllib.request.urlopen
    try:
        A._KEEPALIVE_URL = ""
        ok("URL rỗng (local/test) -> _keepalive_ping()=False (KHÔNG ping)", A._keepalive_ping() is False)
        A._KEEPALIVE_URL = "http://fake.local"
        hit = {}

        class _Resp:
            def read(self, n=0):
                return b""

        def _fake_urlopen(url, timeout=0):
            hit["url"] = url
            return _Resp()

        urllib.request.urlopen = _fake_urlopen
        ok("có URL -> ping ĐÚNG <url>/health + trả True", A._keepalive_ping() is True and hit.get("url") == "http://fake.local/health", hit)

        def _raise(url, timeout=0):
            raise OSError("server down")

        urllib.request.urlopen = _raise
        ok("urlopen LỖI -> vẫn True (nuốt lỗi, không crash luồng nền)", A._keepalive_ping() is True)
    finally:
        urllib.request.urlopen = _uo
        A._KEEPALIVE_URL = _u

    print("[L.4] _start_keepalive an toàn khi CHƯA cấu hình (không start thread / không crash)")
    _u2 = A._KEEPALIVE_URL
    A._KEEPALIVE_URL = ""
    try:
        A._start_keepalive()
        ok("gọi _start_keepalive() URL rỗng -> không lỗi", True)
    finally:
        A._KEEPALIVE_URL = _u2

    print("[L.5] hằng số KEEPALIVE_MIN int; render.yaml healthCheckPath=/health")
    ok("KEEPALIVE_MIN int", isinstance(A.KEEPALIVE_MIN, int))
    ry = open(os.path.join(HERE, "..", "render.yaml"), encoding="utf-8").read()
    ok("render.yaml healthCheckPath: /health", "healthCheckPath: /health" in ry)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
