# -*- coding: utf-8 -*-
"""MCPBridge — VÒNG ĐỜI TIẾN TRÌNH CON: close(cho_giay) xác nhận chết + call() sau close KHÔNG TREO +
KHÔNG để tiến trình con MỒ CÔI khi spawn quá hạn. OFFLINE, KHÔNG tốn API (USE_AI không cần bật).
Chạy:  python tests/test_bridge_close.py

VÌ SAO CÓ SUITE NÀY (đo thật 2026-07-30, không phải suy đoán):
  - Mệnh đề cũ "close() fire-and-forget nên RAM cũ+mới chồng nhau" là SAI: con chết sau 0.198s (rảnh) đến
    2.022s (đang parse), 8 vòng spawn+close chỉ +2.3MB, 0 con mồ côi. => KHÔNG vá chỗ đó.
  - NHƯNG có 2 lỗ THẬT: (a) __init__ hết hạn -> ném RuntimeError, tiến trình con SỐNG MÃI (đo: còn sống sau
    40.0s + 15s, WS 9.1MB) và caller không bao giờ nhận được đối tượng để gọi close() -> mỗi lần đối tác bấm
    lại sinh thêm ~98MB, 2-3 lần là hết RAM; (b) close() đua với call() đang bay -> future bị bỏ rơi, call()
    NẰM CHỜ TRÒN timeout của nó (ở /upload là 600s).
"""
import os, sys, io, re, time, ctypes
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("USE_AI", "0")          # không cần Gemini cho suite này
import mcp_bridge as B

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


# --- Đếm tiến trình CON của chính tiến trình test (không cài psutil — giữ môi trường sạch) -------------------
def _so_con():
    """Số tiến trình con trực tiếp của PID này. Windows: CreateToolhelp32Snapshot. Linux: /proc/<pid>/stat."""
    me = os.getpid()
    if sys.platform == "win32":
        class PE32(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong),
                        ("th32ProcessID", ctypes.c_ulong), ("th32DefaultHeapID", ctypes.c_void_p),
                        ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
                        ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", ctypes.c_ulong), ("szExeFile", ctypes.c_char * 260)]
        k = ctypes.windll.kernel32
        snap = k.CreateToolhelp32Snapshot(0x2, 0)      # TH32CS_SNAPPROCESS
        if snap == -1:
            return -1
        try:
            e = PE32(); e.dwSize = ctypes.sizeof(PE32)
            n = 0
            got = k.Process32First(snap, ctypes.byref(e))
            while got:
                if e.th32ParentProcessID == me:
                    n += 1
                got = k.Process32Next(snap, ctypes.byref(e))
            return n
        finally:
            k.CloseHandle(snap)
    n = 0
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open("/proc/%s/stat" % d) as h:
                if int(h.read().rsplit(")", 1)[1].split()[1]) == me:
                    n += 1
        except Exception:
            continue
    return n


def _cho_con_ve(muc_tieu, han_giay=10.0):
    """Chờ số con TỤT về <= mục tiêu. Trả (số con cuối, giây đã chờ)."""
    t0 = time.time()
    while time.time() - t0 < han_giay:
        n = _so_con()
        if n <= muc_tieu:
            return n, round(time.time() - t0, 2)
        time.sleep(0.1)
    return _so_con(), round(time.time() - t0, 2)


def main():
    print("[B.0] nền: đếm được tiến trình con + spawn mcp_server.py THẬT")
    goc = _so_con()
    ok("đếm tiến trình con hoạt động (>=0)", goc >= 0, goc)
    br = B.MCPBridge(["mcp_server.py"], cwd=ROOT)
    ok("bridge sẵn sàng + có tool", len(br.tools) >= 20, len(br.tools))
    ok("spawn ĐÚNG 1 tiến trình con", _so_con() == goc + 1, (goc, _so_con()))

    print("[B.1] close(cho_giay>0) -> XÁC NHẬN đã dừng (dùng cho đường nhường chỗ)")
    t0 = time.time()
    kq = br.close(cho_giay=5)
    dt = time.time() - t0
    ok("trả True (đã xác nhận luồng nền dừng)", kq is True, kq)
    ok("luồng nền KHÔNG còn sống", br._thread is not None and not br._thread.is_alive())
    n, cho = _cho_con_ve(goc)
    ok("tiến trình con đã biến mất", n == goc, (goc, n, cho))
    ok("không chờ quá trần đã yêu cầu", dt <= 6.0, round(dt, 2))

    print("[B.3] call() SAU close() -> ném NGAY, KHÔNG treo tròn timeout (bug đo thật: /upload treo 600s)")
    t0 = time.time()
    loi = None
    try:
        br.call("thong_tin_file", {}, timeout=30)
    except Exception as e:
        loi = e
    dt = time.time() - t0
    ok("ném lỗi thay vì trả về/treo", loi is not None, loi)
    ok("ném trong dưới 1 giây (không nằm chờ timeout=30)", dt < 1.0, round(dt, 3))
    # M4 — thông điệp này có thể đi vào rổ grounding qua vòng dispatch -> PHẢI sạch số.
    ok("thông điệp lỗi SẠCH SỐ (không bơm số lạ vào rổ chống-bịa)", re.search(r"\d", str(loi)) is None, str(loi))

    print("[B.2] close() KHÔNG tham số -> giữ hành vi CŨ: trả về ngay (không chặn _try_close_session)")
    br2 = B.MCPBridge(["mcp_server.py"], cwd=ROOT)
    t0 = time.time()
    r2 = br2.close()
    dt = time.time() - t0
    ok("trả về trong dưới 50 ms (fire-and-forget như cũ)", dt < 0.05, round(dt, 4))
    ok("trả về bool (hợp đồng mới, caller cũ bỏ qua được)", isinstance(r2, bool), r2)
    n, cho = _cho_con_ve(goc)
    ok("con vẫn TỰ chết (thư viện mcp tự dọn) dù không chờ", n == goc, (goc, n, cho))
    ok("gọi close() LẦN HAI không ném (vòng asyncio đã dừng)", br2.close() in (True, False))

    print("[B.6] LỖI NÉM TRONG TIẾN TRÌNH CON -> phải về đúng khoá 'loi' + SẠCH SỐ (qua đường truyền MCP THẬT)")
    # Đây là lỗi mức CHẶN red-team tìm ra: trước bản vá, MCPBridge.call BỎ cờ res.isError nên lỗi rơi vào
    # {"ket_qua": "Error executing tool ..."} -> (1) /upload kiểm res.get("loi") nên MÙ với mọi lỗi nạp thật và
    # hiện "✅ Đã nạp"; (2) text lỗi THÔ (pydantic nhét cả input_value=<số>) chảy vào rổ neo grounding.
    import mcp_bridge as MB
    br3 = B.MCPBridge(["mcp_server.py"], cwd=ROOT)
    try:
        rac = os.path.join(os.environ.get("TEMP") or HERE, "rt_file_rac_test.dxf")
        with open(rac, "wb") as h:
            h.write(b"KHONG PHAI DXF 12345 " * 40)
        r6 = br3.call("nap_ban_ve", {"path": rac})
        ok("trả dict có khoá 'loi' (không phải 'ket_qua')", isinstance(r6, dict) and "loi" in r6 and "ket_qua" not in r6, r6)
        ok("thông điệp SẠCH SỐ", re.search(r"\d", str(r6.get("loi", ""))) is None, r6)
        ok("rổ neo grounding RỖNG (không bơm số lạ cho guard chống bịa)", MB._collect_numbers(r6) == set(), MB._collect_numbers(r6))
        ok("KHÔNG rỉ đường dẫn máy chủ", "rt_file_rac_test" not in str(r6) and ":" not in str(r6.get("loi", "")).replace("này.", ""), r6)
        # Tham số SAI KIỂU: pydantic v2 nhét NGUYÊN giá trị vào thông điệp -> đây là đường model tự bơm số vào rổ
        r6b = br3.call("tim_kiem", {"gioi_han": "khong-phai-so-987654"})
        ok("tham số sai kiểu -> cũng về 'loi' sạch số, KHÔNG mang 987654 vào rổ",
           isinstance(r6b, dict) and "loi" in r6b and MB._collect_numbers(r6b) == set(), r6b)
        try:
            os.remove(rac)
        except OSError:
            pass
    finally:
        br3.close(cho_giay=5)
    n, cho = _cho_con_ve(goc)
    ok("dọn sạch sau B.6", n == goc, (goc, n, cho))

    print("[B.4] M1 — spawn QUÁ HẠN: ném lỗi VÀ KHÔNG để tiến trình con MỒ CÔI (lặp 3 vòng)")
    _rw = B.READY_WAIT_S
    B.READY_WAIT_S = 3.0            # ép đúng đường code hết hạn (máy local spawn quá nhanh để tái hiện tự nhiên)
    try:
        for vong in (1, 2, 3):
            loi2 = None
            try:
                # server GIẢ: chỉ ngủ, không bao giờ trả lời JSON-RPC -> _ready.wait() chắc chắn hết hạn
                B.MCPBridge(["-c", "import time;time.sleep(120)"], cwd=ROOT)
            except RuntimeError as e:
                loi2 = e
            ok("vòng %d: ném RuntimeError khi quá hạn" % vong, loi2 is not None, loi2)
            n, cho = _cho_con_ve(goc)
            ok("vòng %d: KHÔNG còn tiến trình con mồ côi" % vong, n == goc, (goc, n, cho))
    finally:
        B.READY_WAIT_S = _rw
    ok("MCP_READY_S đọc được từ env, mặc định >= 40s (40 hard-code cũ quá mỏng cho CPU chia sẻ)",
       isinstance(B.READY_WAIT_S, float) and B.READY_WAIT_S >= 40, B.READY_WAIT_S)
    n, cho = _cho_con_ve(goc)
    ok("kết thúc suite: 0 tiến trình con còn lại", n == goc, (goc, n, cho))

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
