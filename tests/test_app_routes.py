# -*- coding: utf-8 -*-
"""GĐ2 — SMOKE các route Flask TẤT ĐỊNH (0 API, 0 subprocess): /, /config, /version, /health + upload lỗi-đầu-vào.
Các route này (trừ /health) trước KHÔNG có test. Route cần AI (/ask) + upload thành công (spawn MCP) đã phủ ở
test_session (FakeBridge) + test_mcp_stdio (transport thật). Ở đây chỉ smoke nhánh tất định + cửa 400.
Chạy: python tests/test_app_routes.py"""
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


def main():
    c = A.app.test_client()
    print("[R.1] GET / -> trang UI")
    r = c.get("/")
    ok("/ -> 200 + HTML demo", r.status_code == 200 and (b"DEMO" in r.data or b"MCP" in r.data), r.status_code)

    print("[R.2] GET /config -> {use_ai, model}")
    r = c.get("/config"); j = r.get_json()
    ok("/config -> 200 + có 'use_ai' (bool)", r.status_code == 200 and isinstance(j.get("use_ai"), bool), j)

    print("[R.3] GET /version -> {commit, sect_cm_max, has_section_index, models}")
    r = c.get("/version"); j = r.get_json()
    ok("/version -> 200 + có 'commit'", r.status_code == 200 and "commit" in j, j)
    ok("/version -> sect_cm_max=130 (cờ parity cm/mm đã có mặt)", j.get("sect_cm_max") == 130, j.get("sect_cm_max"))
    ok("/version -> has_section_index=True", j.get("has_section_index") is True)

    print("[R.4] GET /health -> {ok, uptime_s, sessions, metrics}")
    r = c.get("/health"); j = r.get_json()
    ok("/health -> 200 + ok=True + shape", r.status_code == 200 and j.get("ok") is True
       and isinstance(j.get("uptime_s"), int) and isinstance(j.get("metrics"), dict), j)

    print("[R.5] POST /upload — cửa 400 lỗi đầu vào (không cần bridge/AI)")
    r = c.post("/upload", data={}, content_type="multipart/form-data")
    ok("upload KHÔNG file -> 400", r.status_code == 400, r.status_code)
    r = c.post("/upload", data={"file": (io.BytesIO(b"x"), "abc.txt")}, content_type="multipart/form-data")
    ok("upload .txt (sai đuôi) -> 400 (chỉ .dxf/.dwg)", r.status_code == 400, r.status_code)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
