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
    # Chống "trôi lệch ngầm": app.py ghi 1 mặc định, render.yaml ghi số khác (hoặc im lặng) mà không ai thấy.
    ok("render.yaml ghi TƯỜNG MINH KEEPALIVE_MIN + MAX_SESSIONS + LOCK_WAIT_S",
       all(("- key: %s" % k) in ry for k in ("KEEPALIVE_MIN", "MAX_SESSIONS", "LOCK_WAIT_S")))

    print("[L.6] HỎNG THẦM phải LỘ: /health có khối keepalive + bộ đếm ok/lỗi (KHÔNG phá hợp đồng L.3)")
    _u4, _snap, _ts = A._KEEPALIVE_URL, dict(A._KEEPALIVE), A._KA_OK_TS
    _uo3 = urllib.request.urlopen
    try:
        j2 = (A.app.test_client().get("/health").get_json() or {})
        ka = j2.get("keepalive")
        ok("/health có khối 'keepalive' là dict", isinstance(ka, dict), j2)
        ok("keepalive đủ khoá cau_hinh/chu_ky_phut/ok/loi/loi_cuoi/giay_tu_lan_ok_cuoi",
           isinstance(ka, dict) and all(k in ka for k in ("cau_hinh", "chu_ky_phut", "ok", "loi", "loi_cuoi", "giay_tu_lan_ok_cuoi")), ka)
        ok("ok/loi là int (đọc được từ ngoài, không cần vào máy chủ)",
           isinstance((ka or {}).get("ok"), int) and isinstance((ka or {}).get("loi"), int), ka)

        A._KEEPALIVE_URL = "http://fake.local"
        A._KEEPALIVE.update({"ok": 0, "loi": 0, "loi_cuoi": ""})

        def _raise2(url, timeout=0):
            raise OSError("server down")

        urllib.request.urlopen = _raise2
        _ret = A._keepalive_ping()
        ok("ping LỖI -> bộ đếm loi +1 và loi_cuoi khác rỗng (trước đây IM LẶNG hoàn toàn)",
           A._KEEPALIVE["loi"] == 1 and A._KEEPALIVE["loi_cuoi"] != "", dict(A._KEEPALIVE))
        ok("ping LỖI -> VẪN trả True (giữ nguyên hợp đồng L.3, không crash luồng nền)", _ret is True)
        ok("loi_cuoi CHỈ là TÊN loại lỗi (không nhét URL vào endpoint không xác thực)",
           A._KEEPALIVE["loi_cuoi"] == "OSError", A._KEEPALIVE["loi_cuoi"])
        ok("/health phơi loi>0 -> từ ngoài BIẾT self-ping đang chết",
           ((A.app.test_client().get("/health").get_json() or {}).get("keepalive") or {}).get("loi") == 1)
    finally:
        urllib.request.urlopen = _uo3
        A._KEEPALIVE_URL = _u4
        A._KEEPALIVE.clear(); A._KEEPALIVE.update(_snap)
        A._KA_OK_TS = _ts

    print("[L.7] _keepalive_loop: PING TRƯỚC rồi mới ngủ; nhịp = chu kỳ; ping LỖI -> thử lại NHANH")
    import time as _time
    _sl, _u5, _km, _snap2 = _time.sleep, A._KEEPALIVE_URL, A.KEEPALIVE_MIN, dict(A._KEEPALIVE)
    _uo4 = urllib.request.urlopen
    nhat_ky = []            # nhật ký THỨ TỰ: ("ping", n) / ("sleep", giây)

    class _Dung(Exception):
        pass

    try:
        A._KEEPALIVE_URL, A.KEEPALIVE_MIN = "http://fake.local", 5
        A._KEEPALIVE.update({"ok": 0, "loi": 0, "loi_cuoi": ""})
        dem = {"n": 0}

        class _R2:
            def read(self, n=0):
                return b""

        def _uo_dan(url, timeout=0):
            dem["n"] += 1
            nhat_ky.append(("ping", dem["n"]))
            if dem["n"] >= 3:       # 2 lần đầu OK, lần 3 LỖI -> phải thấy nhịp ngủ ngắn
                raise OSError("down")
            return _R2()

        def _sleep_ao(g):
            nhat_ky.append(("sleep", g))
            if len([x for x in nhat_ky if x[0] == "sleep"]) >= 3:
                raise _Dung()

        urllib.request.urlopen, _time.sleep = _uo_dan, _sleep_ao
        try:
            A._keepalive_loop()
        except _Dung:
            pass
        ngu = [g for k, g in nhat_ky if k == "sleep"]
        ok("việc ĐẦU TIÊN là PING, không phải ngủ (trước đây ping đầu chỉ xảy ra ở t=chu_kỳ)",
           bool(nhat_ky) and nhat_ky[0][0] == "ping", nhat_ky[:3])
        ok("2 nhịp đầu ngủ ĐÚNG chu kỳ 5 phút", ngu[:2] == [300, 300], ngu)
        ok("sau ping LỖI -> nhịp ngủ NGẮN lại (thử lại nhanh, không mất trọn 1 chu kỳ)",
           len(ngu) >= 3 and ngu[2] == 30, ngu)
        ok("tín hiệu thất bại lấy từ BỘ ĐẾM, không từ giá trị trả về (nếu lấy từ return thì nhánh này là mã chết)",
           A._KEEPALIVE["loi"] == 1 and A._KEEPALIVE["ok"] == 2, dict(A._KEEPALIVE))
    finally:
        urllib.request.urlopen, _time.sleep = _uo4, _sl
        A._KEEPALIVE_URL, A.KEEPALIVE_MIN = _u5, _km
        A._KEEPALIVE.clear(); A._KEEPALIVE.update(_snap2)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
