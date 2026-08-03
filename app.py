# -*- coding: utf-8 -*-
"""
app.py — HOST của DEMO 2 (hướng MCP). Web Flask đóng vai "custom MCP host":
  upload .dwg/.dxf -> nạp vào MCP server -> Gemini hỏi-đáp QUA MCP -> trả lời + ẢNH KHOANH ĐỎ cấu kiện.

Khác demo 1: (1) kiến trúc MCP CHUẨN (server tách rời, cắm được Claude Desktop/Gemini CLI...);
            (2) TRỰC QUAN — thấy bản vẽ + highlight, không chỉ chữ. Vẫn deploy cloud (không cần AutoCAD).
Chạy: python app.py  ->  http://localhost:5050
"""
import os, sys, threading, uuid, time
from flask import Flask, request, jsonify, send_file, g
import mcp_bridge
from fileutil import cleanup_old_files          # Robustness J — dọn file TTL (nhẹ, không kéo ezdxf)

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE, "_uploads")
RENDER_DIR = os.path.join(BASE, "_renders")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

app = Flask(__name__)
app.json.ensure_ascii = False
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "150"))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
# Robustness I — giới hạn file PARSE (MB); KHỚP tools_core.READFILE_MAX_MB (cùng đọc env này) để chặn upload lớn
# SỚM ở tầng app (khỏi gọi MCP/convert/parse). MAX_CONTENT_LENGTH (150MB) là trần thô cho DWG NÉN; đây là trần PARSE.
READFILE_MAX_MB = int(os.environ.get("READFILE_MAX_MB", "45"))
# Robustness J — dọn file _uploads/_renders cũ hơn ngần này phút mỗi lần upload (0 = tắt). KHỚP tools_core.FILE_TTL_MIN.
FILE_TTL_MIN = int(os.environ.get("FILE_TTL_MIN", "60"))
# E6 — cookie sid cờ Secure GATE THEO ENV (mặc định OFF để local/test HTTP vẫn set được cookie; prod HTTPS đặt
# COOKIE_SECURE=true trong render.yaml). Bật Secure -> cookie sid không lộ qua kênh HTTP không mã hoá.
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "").lower() in ("1", "true", "yes")

MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", "6"))  # số lượt (mỗi lượt = 1 hỏi + 1 đáp) giữ lại

# Robustness K — STATE THEO SESSION (thay 1 Drawing/history GLOBAL): mỗi phiên trình duyệt có bridge RIÊNG
# (1 MCP subprocess = 1 Drawing) + summary + history + lock RIÊNG -> 2 người dùng KHÔNG đạp state nhau. Bound RAM
# bằng CAP (trần phiên đồng thời; đầy -> đóng phiên CŨ NHẤT/LRU) + TTL (đóng phiên nhàn rỗi, giải phóng subprocess).
SESSIONS = {}                     # sid -> {"bridge","summary","history","lock","last"}
_SESS_LOCK = threading.RLock()    # bảo vệ dict SESSIONS
def _env_int(ten, mac_dinh):
    """Đọc env số NGUYÊN, env RÁC -> mặc định. ⚠ TUYỆT ĐỐI không dùng int() trần cho các nút đã phơi trong
    render.yaml: gõ sai một chữ trên dashboard Render là `import app` NÉM = deploy FAIL 100% (rủi ro MỚI mà chính
    việc phơi các nút này tạo ra — red-team bắt được)."""
    try:
        return int(os.environ.get(ten, mac_dinh) or mac_dinh)
    except Exception:
        return int(mac_dinh)


MAX_SESSIONS = _env_int("MAX_SESSIONS", "4")     # trần SỐ PHIÊN — phiên RỖNG chỉ ~965 byte (đo thật)
SESSION_TTL_MIN = _env_int("SESSION_TTL_MIN", "30")
# ⚠ MAX_SESSIONS **KHÔNG PHẢI** trần RAM — đo thật (ma trận cap-vs-thread, 5/5 cấu hình): số bản vẽ nằm trong RAM
# bằng SỐ REQUEST ĐỒNG THỜI (gunicorn --threads), KHÔNG phụ thuộc cap này (cap=2/threads=4 vẫn ra 4 bản vẽ).
# Vì vậy hạ cap 4->2 tiết kiệm 0MB và còn MỞ 2 thread rảnh cho người mới -> tự bỏ lớp che mà threads==cap đang cho.
# Trần RAM thật sẽ là hạn mức SỐ BẢN VẼ (lát 2). Ở đây GIỮ 4.
# Trần chờ khoá PHIÊN (giây) — xem _tu_choi(). KẸP >= 0: `acquire(timeout=-1)` nghĩa là CHỜ VÔ HẠN, tức một số âm
# đặt trên dashboard sẽ TẮT ÂM THẦM đúng cái bản vá này dựng ra để chống nghẽn thread.
LOCK_WAIT_S = max(0, _env_int("LOCK_WAIT_S", "3"))

# TRẦN RAM THẬT: số BẢN VẼ được giữ trong RAM cùng lúc. Đo thật (Windows WorkingSet, gói free 512MB):
#   web 104.9MB + 1 bản vẽ .dxf 23.31MiB = 289.2MB  -> 394.1MB (77%)  · 2 bản vẽ như vậy -> 683MB = OOM
#   1 bản vẽ 39.28MiB (LỌT qua cổng 45MB) -> child 429.9MB -> tổng 534.8MB = đã vượt 512MB MỘT MÌNH
# => gói free chỉ chịu 1. Lên gói 2GB mới đặt 2-3 (và phải ĐO ram_mb thật ở /health trước khi nâng).
# 0 = TẮT gate hoàn toàn (về đúng hành vi trước bản vá) — dùng cho test và cho đường lùi khẩn cấp.
MAX_BAN_VE = _env_int("MAX_BAN_VE", "1")
CLOSE_WAIT_S = float(_env_int("CLOSE_WAIT_S", "5"))   # trần chờ XÁC NHẬN bản vẽ cũ đã ra khỏi RAM
NAP_HAN_S = _env_int("NAP_HAN_S", "1500")             # hạn tự lành của 1 suất đang nạp (>= 2x worst-case nạp .dwg)
DONG_HAN_S = _env_int("DONG_HAN_S", "60")             # hạn tự lành của cờ 'đang đóng' (chống tự khoá mình mãi)

# Robustness L — KEEP-ALIVE + GIÁM SÁT. Render free ngủ sau ~15' idle -> cold-start; self-ping /health giữ THỨC
# (dùng RENDER_EXTERNAL_URL Render tự set -> traffic ngoài thật; chỉ chạy khi có URL = production, local/test KHÔNG kích).
# /health = endpoint NHẸ (no API/no bản vẽ) cho monitor ngoài (UptimeRobot...) + quan sát cơ bản (uptime/sessions/metrics).
START_TS = time.time()
_METRICS = {"uploads": 0, "asks": 0, "errors": 0, "tu_choi": 0}
# KEEPALIVE_MIN 10 -> 5: đo thật bằng đồng hồ ảo, chu kỳ 10' cho khoảng-2-ping 600s so với ngưỡng ngủ ~900s =>
# chịu được ĐÚNG 0 nhịp trượt (trượt 1 nhịp -> ping kế ở t=1200s > 900s -> máy ngủ). Chu kỳ 5' (300s) chịu 2 nhịp.
KEEPALIVE_MIN = _env_int("KEEPALIVE_MIN", "5")                      # 0 = tắt self-ping (env rác -> 5, không sập boot)
_KEEPALIVE_URL = (os.environ.get("KEEPALIVE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "").strip()
# Chống "hỏng thầm": đo thật -> _keepalive_ping() trả True KỂ CẢ khi lỗi, stderr in ra 0 ký tự, không bộ đếm nào
# => từ bên ngoài KHÔNG THỂ phân biệt "ping đều 6 tháng" với "ping chết từ ngày đầu". Bộ đếm này phơi ở /health.
_KEEPALIVE = {"cau_hinh": False, "chu_ky_phut": 0, "ok": 0, "loi": 0, "loi_cuoi": ""}
_KA_OK_TS = 0.0


def _make_bridge():               # tách ra để test monkeypatch FakeBridge (khỏi spawn subprocess thật)
    return mcp_bridge.MCPBridge(["mcp_server.py"], cwd=BASE)


def _xoa_file(p):                 # dọn file vừa lưu khi request bị TỪ CHỐI (cùng khuôn nhánh 413)
    try:
        os.remove(p)
    except OSError:
        pass


def _nap_that_bai(s):
    """Nạp file mới THẤT BẠI. mcp_server.nap_ban_ve giờ bỏ bản vẽ CŨ TRƯỚC khi dựng bản MỚI (tiết kiệm 123.9MB
    đỉnh RAM) — đánh đổi: nạp lỗi thì bản vẽ cũ đã BỐC HƠI. Host TUYỆT ĐỐI không được giữ summary/history của
    bản vẽ không còn tồn tại: nếu giữ, Gemini nhận mô tả một bản vẽ đã mất = BỊA CÓ HỆ THỐNG (tệ hơn báo lỗi).
    Cũng NHẢ luôn tiến trình con: nó không còn bản vẽ nào mà vẫn ăn ~98MB (đo thật) — RAM VÔ HÌNH mà bộ đếm
    theo 'có bản vẽ' không thấy. Lần upload sau tự spawn lại (đo thật 2.06-17.97s)."""
    br = s.get("bridge")
    s["bridge"] = None
    s["co_ban_ve"] = False
    s["nap_loi"] = True
    s["summary"] = ""
    s["history"] = []
    if br is not None:
        try:
            br.close()              # fire-and-forget (đo thật 0.0000s); con tự chết trong 0.198-2.022s
        except Exception:
            pass


def _msg_khong_ban_ve(s):
    """Câu NÓI THẬT khi phiên không có bản vẽ trong RAM. Dùng ở HAI chỗ trong /ask (trước khi lấy khoá VÀ sau khi
    lấy khoá — xem TOCTOU bên dưới) nên phải tách ra, không nhân bản chuỗi kẻo 2 chỗ trôi lệch nhau."""
    if s.get("da_nhuong"):
        return ("Bản vẽ của phiên này đã được nhường cho người khác để đủ bộ nhớ máy chủ (gói miễn phí chỉ "
                "đọc được một bản vẽ cùng lúc). Xin tải lại file bạn muốn xem.")
    if s.get("nap_loi"):
        return ("Bản vẽ trước đã được giải phóng khỏi bộ nhớ máy chủ khi nạp file mới thất bại. "
                "Xin tải lại file bạn muốn xem.")
    # Phiên CHƯA TỪNG upload: GIỮ NGUYÊN VĂN câu cũ (hợp đồng K.5 của test_session).
    return "Chưa nạp bản vẽ cho phiên này. Hãy tải file .dxf/.dwg trước."


def _msg_so_xn(s):
    """Câu NÓI THẬT cho kênh xác nhận (sổ xác nhận sống trong tiến trình con -> bản vẽ ra khỏi RAM là sổ mất)."""
    if s and (s.get("nap_loi") or s.get("da_nhuong")):
        return ("Bản vẽ không còn trong bộ nhớ máy chủ nên sổ xác nhận của phiên đã reset. "
                "Xin tải lại file rồi xác nhận tiếp.")
    return "Chưa nạp bản vẽ cho phiên này."


def _tu_choi(msg, ma=503):
    """Body TỪ CHỐI dùng chung. PHẢI đủ CẢ 4 khoá chữ vì frontend đọc 4 khoá KHÁC NHAU ở 4 chỗ:
    showSum đọc 'error' · send() đọc 'answer' · hoanTacBtn đọc DUY NHẤT 'ly_do' (+ 'da_thu_hoi') ·
    hoanTacDs đọc 'ly_do'||'loi'. Thiếu 'ly_do' -> người bấm ↩ Hoàn tác đọc câu mặc định "Không gỡ được
    (có thể đã gỡ trước đó)" = TIN SAI là đã gỡ -> tái sinh đúng bug 'undo nói dối' đã vá 2026-07-27.
    'da_thu_hoi': False để frontend KHÔNG báo gỡ thành công. Chuỗi này đi ra TRÌNH DUYỆT, không vào rổ grounding."""
    _METRICS["tu_choi"] += 1
    return jsonify({"error": msg, "answer": msg, "loi": msg, "ly_do": msg,
                    "ok": False, "da_thu_hoi": False, "dang_ban": True, "evidence": [], "ai": True}), ma


def _close_session(sid):          # GỌI TRONG _SESS_LOCK: bỏ phiên + đóng bridge (giải phóng subprocess/RAM). ÉP đóng.
    s = SESSIONS.pop(sid, None)
    if s:
        for _br in (s.get("bridge"), s.get("dang_dong")):   # 'dang_dong' = bridge đang chờ xác nhận chết
            if _br:
                try:
                    _br.close()
                except Exception:
                    pass


def _try_close_session(sid):      # F-A — GỌI TRONG _SESS_LOCK: đóng phiên CHỈ KHI không đang phục vụ request (lock rảnh).
    """Bận (đang /upload hoặc /ask, giữ s['lock']) -> trả False, KHÔNG đóng — chống đóng subprocess GIỮA request đang
    chạy (cold-start 30-60s / .dwg-ODA tới 600s). acquire(blocking=False): rảnh -> đóng an toàn; bận -> bỏ qua."""
    s = SESSIONS.get(sid)
    if s is None:
        return True
    # KHÔNG BAO GIỜ pop phiên đang có request /upload BAY. Red-team (CAO) tái hiện: trong cửa sổ chờ _dong_cho_chac
    # (tới CLOSE_WAIT_S) phiên đã có SUẤT, bridge=None và KHÔNG giữ s['lock'] -> khoá sort mới (ưu tiên phiên rỗng)
    # biến nó thành MÓN NGON NHẤT cho LRU; pop xong /upload vẫn nạp bản vẽ vào dict MỒ CÔI rồi trả '✅ Đã nạp'
    # trong khi câu hỏi kế tiếp là 'Chưa nạp bản vẽ' — và 149-430MB đó KHÔNG ai đếm được nữa.
    if s.get("nap_dem") and s.get("nap_tu") and time.time() - s["nap_tu"] < NAP_HAN_S:
        return False
    if not s["lock"].acquire(blocking=False):
        return False
    try:
        SESSIONS.pop(sid, None)
        for _br in (s.get("bridge"), s.get("dang_dong")):   # đóng CẢ bridge đang chờ xác nhận chết (khỏi mồ côi)
            if _br:
                try:
                    _br.close()
                except Exception:
                    pass
    finally:
        s["lock"].release()
    return True


def _evict_one_lru():             # F-A — đóng 1 phiên CŨ NHẤT KHÔNG bận (nhường chỗ). MỌI phiên bận -> False (cho vượt cap tạm).
    # ƯU TIÊN đuổi phiên RỖNG (bridge=None, ~965 byte) TRƯỚC phiên đang giữ bản vẽ (đo thật 149-430MB): trước đây
    # chỉ sort theo 'last' nên 4 lượt khách VÔ DANH mới vào có thể đẩy mất bản vẽ của đối tác đang xem (phiên cũ nhất).
    for k in sorted(SESSIONS, key=lambda k: (SESSIONS[k].get("bridge") is not None, SESSIONS[k]["last"])):
        if _try_close_session(k):
            return True
    return False


def _dem_ban_ve():
    """GỌI TRONG _SESS_LOCK. Số 'chỗ RAM bản vẽ' đang bị chiếm. ĐẾM LẠI TỪ SỰ THẬT mỗi lần — TUYỆT ĐỐI không
    dùng biến đếm: rỉ 1 lần là khoá app VĨNH VIỄN (mọi người sau đó ăn 503 trong khi RAM trống trơn — red-team
    đã làm vỡ bản thiết kế đầu đúng theo kịch bản này, bằng 1 request sai đuôi file).
    Mặc định co_ban_ve=True cho phiên dựng TAY (test) -> đếm BẢO THỦ, thà chặn hơn thà tràn."""
    now, n = time.time(), 0
    for v in SESSIONS.values():
        if v.get("dang_dong") is not None:
            n += 1              # bridge đã ra lệnh đóng nhưng CHƯA xác nhận chết -> VẪN tính là đang giữ RAM
        elif v.get("bridge") is not None and v.get("co_ban_ve", True):
            n += 1
        elif v.get("nap_dem") and v.get("nap_tu") and now - v["nap_tu"] < NAP_HAN_S:
            n += 1              # đang nạp: ĐẾM REQUEST ĐANG BAY (nap_dem), có hạn NAP_HAN_S để suất tự lành
    return n


def _don_dang_dong():
    """GỌI TRONG _SESS_LOCK. close(cho_giay=0) KHÔNG CHẶN (đo thật: trả về trong 0.0000s) -> chỉ hỏi 'luồng nền
    đã dừng chưa'. Chết rồi -> gỡ cờ, nhả suất.
    ⚠ HẠN TỰ LÀNH (red-team CAO): bản đầu chỉ gỡ cờ khi close() CHỊU trả True. Nếu tiến trình con cứng đầu thì cờ
    nằm mãi -> trong buổi demo 2 máy (không có khách mới để kích LRU) KHÔNG AI nạp được nữa cho tới hết TTL phiên
    (30 phút), trong khi câu thông báo lại hứa 'thử lại sau mười giây'. Quá hạn thì GỠ: lệnh đóng đã phát từ
    trước, giữ mãi là app tự chặn CHÍNH MÌNH."""
    now = time.time()
    for v in SESSIONS.values():
        br = v.get("dang_dong")
        if br is None:
            continue
        try:
            xong = bool(br.close())
        except Exception:
            xong = True                                 # không hỏi được -> coi như đã xong, đừng tự khoá mình
        if xong or (now - (v.get("dong_tu") or now) > DONG_HAN_S):
            v["dang_dong"] = None
            v["dong_tu"] = 0.0


def _giu_suat(s, now):
    """GỌI TRONG _SESS_LOCK. ĐẾM số request /upload ĐANG BAY của phiên, không phải đặt 1 ô thời gian.
    ⚠ ĐÂY LÀ BẢN VÁ LỖI MỨC CHẶN do chính lát 2 sinh ra (3 lăng kính red-team độc lập tái hiện): với 1 ô vô hướng,
    request thứ HAI của CÙNG phiên (đối tác bấm 'Tải lên & nạp' hai lần, hoặc mở 2 tab) thua khoá -> 503 -> `finally`
    của NÓ xoá cờ đang-nạp của request ANH EM đang parse -> _dem_ban_ve() tụt về 0 -> phiên KHÁC xin được suất ->
    2 bản vẽ cùng RAM = ĐÚNG cái OOM mà gate này tồn tại để chặn (đo thật: 4 người = 4 bản vẽ)."""
    s["nap_dem"] = s.get("nap_dem", 0) + 1
    if not s.get("nap_tu"):
        s["nap_tu"] = now                               # GIỮ mốc SỚM NHẤT -> hạn NAP_HAN_S vẫn tự lành được


def _xin_suat(s):
    """GỌI TRONG _SESS_LOCK, NGAY sau khi lấy/tạo phiên (cùng MỘT ảnh chụp — tách 2 lần giữ khoá thì red-team đo
    được 2 bản vẽ cùng RAM dù trần là 1). Trả ('ok'|'ban', da_giu_suat, phien_bi_nhuong)."""
    if MAX_BAN_VE <= 0:
        return "ok", False, None                        # gate TẮT = hành vi trước bản vá
    _don_dang_dong()
    now = time.time()
    if s.get("co_ban_ve") or s.get("nap_dem") or (s.get("nap_tu") and now - s["nap_tu"] < NAP_HAN_S):
        _giu_suat(s, now)                               # nạp LẠI trong CÙNG phiên: bản cũ được bỏ trước (mục 6)
        return "ok", False, None                        # -> không chiếm thêm chỗ, KHÔNG cần xin suất mới
    if _dem_ban_ve() < MAX_BAN_VE:
        _giu_suat(s, now)
        return "ok", True, None
    for k in sorted(SESSIONS, key=lambda k: SESSIONS[k]["last"]):    # đầy -> thử NHƯỜNG (cũ nhất trước)
        v = SESSIONS[k]
        if v is s or not v.get("co_ban_ve", True) or v.get("dang_dong") is not None:
            continue
        if v.get("nap_dem") and v.get("nap_tu") and now - v["nap_tu"] < NAP_HAN_S:
            continue                                    # request của CHÍNH nó đang bay -> KHÔNG được nhường (TOCTOU)
        if not v["lock"].acquire(blocking=False):
            continue                                    # F-A: đang phục vụ request -> bỏ qua, KHÔNG giết giữa đường
        try:
            # GIỮ phiên trong SESSIONS (không pop): giữ 'artifacts' (ảnh khoanh đỏ đã hiện không thành 404) và
            # giữ chỗ ghi cờ để /ask + /xac-nhan NÓI THẬT. Việc đóng thật làm NGOÀI _SESS_LOCK.
            v["dang_dong"] = v.get("bridge")
            v["dong_tu"] = now                          # mốc để _don_dang_dong tự lành (xem DONG_HAN_S)
            v["bridge"] = None
            v["co_ban_ve"] = False
            v["summary"] = ""
            v["history"] = []
            v["da_nhuong"] = True
        finally:
            v["lock"].release()
        _giu_suat(s, now)
        return "ok", True, v
    return "ban", False, None


def _tra_suat(s):
    """Nhả MỘT lượt đang-nạp. PHẢI gọi trong finally bao CẢ hàm /upload — mọi đường ra (400/413/503/500/exception).
    Chỉ xoá mốc thời gian khi KHÔNG CÒN request nào của phiên đang bay (xem _giu_suat: đây là nửa còn lại của
    bản vá lỗi CHẶN 'một cú bấm hai lần phá được trần bản vẽ')."""
    if s is None:
        return
    with _SESS_LOCK:
        s["nap_dem"] = max(0, s.get("nap_dem", 0) - 1)
        if not s["nap_dem"]:
            s["nap_tu"] = 0.0


def _dong_cho_chac(br):
    """Đóng + XÁC NHẬN đã chết. ⚠ TUYỆT ĐỐI gọi NGOÀI _SESS_LOCK — đo thật: close() ngủ 5s trong _SESS_LOCK làm
    request KHÔNG liên quan của người khác (/image) chậm 4.50s và người mới chậm 5.01s."""
    if br is None:
        return True
    try:
        return bool(br.close(cho_giay=CLOSE_WAIT_S))
    except Exception as e:
        print("[nhuong] close loi %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return False


def get_session(xin_suat=False):
    """Lấy (hoặc TẠO) phiên theo cookie 'sid'. Sweep TTL + enforce CAP (đóng LRU). Trả (sid, session) + stash
    g.sid để after_request set cookie. Bridge tạo LƯỜI ở /upload (phiên chưa upload -> KHÔNG tốn subprocess).
    xin_suat=True (chỉ /upload): xin luôn SUẤT BẢN VẼ trong CÙNG lần giữ _SESS_LOCK -> trả 5 phần tử."""
    now = time.time()
    sid = request.cookies.get("sid") or ""
    ket, da_giu, s_cu = "ok", False, None
    with _SESS_LOCK:
        if SESSION_TTL_MIN > 0:                        # đóng phiên quá hạn (giải phóng subprocess nhàn rỗi)
            cutoff = now - SESSION_TTL_MIN * 60
            for k in [k for k, v in SESSIONS.items() if v["last"] < cutoff]:
                _try_close_session(k)                  # F-A: bận -> BỎ QUA (quét lần sau), KHÔNG giết request đang chạy
        s = SESSIONS.get(sid)
        if s is None:
            sid = uuid.uuid4().hex
            while len(SESSIONS) >= MAX_SESSIONS:        # cap đầy -> đóng phiên CŨ NHẤT KHÔNG BẬN (LRU)
                if not _evict_one_lru():               # F-A: MỌI phiên đang bận -> cho vượt cap TẠM (không giết request)
                    break
            s = {"bridge": None, "summary": "", "history": [], "lock": threading.Lock(), "last": now,
                 "artifacts": set(), "co_ban_ve": False, "nap_tu": 0.0, "nap_dem": 0, "dang_dong": None,
                 "dong_tu": 0.0, "da_nhuong": False, "nap_loi": False}
            SESSIONS[sid] = s
        s["last"] = now
        if xin_suat:
            ket, da_giu, s_cu = _xin_suat(s)
    g.sid = sid
    return (sid, s, ket, da_giu, s_cu) if xin_suat else (sid, s)


@app.after_request
def _attach_sid(resp):
    sid = getattr(g, "sid", None)
    if sid:
        resp.set_cookie("sid", sid, max_age=(SESSION_TTL_MIN * 60 or 1800), httponly=True, samesite="Lax", secure=COOKIE_SECURE)
    return resp


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File vượt quá %d MB." % MAX_UPLOAD_MB}), 413


@app.route("/")
def index():
    return PAGE


@app.route("/config")
def config():
    return jsonify({"use_ai": mcp_bridge.USE_AI, "model": mcp_bridge.MODEL if mcp_bridge.USE_AI else None})


@app.route("/version")
def version():
    """Verify qua HTTP: commit đã deploy (Render đặt RENDER_GIT_COMMIT) + cờ code cm/mm mới có mặt.
    Không cần nạp bản vẽ, không tốn API. sect_cm_max=130 & has_section_index=true -> bản parity cm/mm đã lên."""
    info = {"commit": os.environ.get("RENDER_GIT_COMMIT", "unknown")}
    try:
        import tools_core
        info["sect_cm_max"] = getattr(tools_core, "_SECT_CM_MAX", None)
        info["has_section_index"] = hasattr(tools_core, "_build_section_index")
    except Exception as e:
        info["tools_core_error"] = "%s: %s" % (type(e).__name__, e)
    info["models"] = getattr(mcp_bridge, "MODELS", None)   # H: chuỗi model dự phòng 429/503 (verify đã deploy)
    # I9: định danh SYSTEM_PROMPT đã deploy (version = ý người; hash = sự thật byte, phát hiện trôi text)
    info["prompt_version"] = getattr(mcp_bridge, "PROMPT_VERSION", None)
    info["prompt_hash"] = getattr(mcp_bridge, "PROMPT_HASH", None)
    try:                                     # L1 (kho kiến thức): định danh KHO đã deploy — degrade-safe (thiếu file vẫn chạy)
        import kienthuc
        info["kb_version"] = kienthuc.KB_VERSION
        info["kb_hash"] = kienthuc.KB_HASH
    except Exception:
        info["kb_version"] = info["kb_hash"] = None
    return jsonify(info)


_RAM_CACHE = {"ts": 0.0, "mb": None}


def _ram_container_mb():
    """RSS container đọc từ cgroup (Linux/Render); None trên Windows/local. CHỈ ĐỂ QUAN SÁT — TUYỆT ĐỐI không
    dùng làm cổng chặn. Đọc 'anon' (cgroup v2) / 'rss' (v1) để NÉ page-cache: memory.current tính cả page-cache
    nên 1 file .dxf 40MB vừa đọc làm số phồng lên, đọc nhầm sẽ tưởng sắp OOM. Cache 2s cho /health siêu nhẹ."""
    now = time.time()
    if now - _RAM_CACHE["ts"] < 2:
        return _RAM_CACHE["mb"]
    mb = None
    for p, k in (("/sys/fs/cgroup/memory.stat", "anon "), ("/sys/fs/cgroup/memory/memory.stat", "rss ")):
        try:
            with open(p) as h:
                for line in h:
                    if line.startswith(k):
                        mb = round(int(line.split()[1]) / 1048576, 1)
                        break
            if mb is not None:
                break
        except Exception:
            continue
    _RAM_CACHE["ts"], _RAM_CACHE["mb"] = now, mb
    return mb


@app.route("/health")
def health():
    """Robustness L — health check NHẸ (no API, no bản vẽ): cho Render healthCheckPath + monitor ngoài + self-ping.
    Trả trạng thái sống + quan sát cơ bản (uptime, số phiên đang mở, model, đếm request, trạng thái self-ping).
    ⚠ TUYỆT ĐỐI không lấy _SESS_LOCK ở đây (giữ /health miễn nhiễm tranh chấp khoá) và không bao giờ trả != 200:
    render.yaml dùng healthCheckPath=/health để GATE DEPLOY -> trả 500 vì self-ping lỗi = tự chặn deploy của mình.
    ⚠ KHÔNG đưa _KEEPALIVE_URL hay str(e) đầy đủ ra ngoài dạng URL — endpoint này KHÔNG xác thực."""
    now = time.time()
    ka = dict(_KEEPALIVE)
    ka["giay_tu_lan_ok_cuoi"] = round(now - _KA_OK_TS) if _KA_OK_TS else None
    try:
        ss = list(SESSIONS.values())        # KHÔNG lấy _SESS_LOCK; dict đang đổi -> bỏ nhịp chứ không chặn /health
    except RuntimeError:
        ss = []
    return jsonify({"ok": True, "uptime_s": round(now - START_TS),
                    "sessions": len(SESSIONS), "use_ai": mcp_bridge.USE_AI,
                    "model": getattr(mcp_bridge, "MODEL", None), "metrics": dict(_METRICS),
                    "keepalive": ka,
                    # M2 — SAU KHI DEPLOY đây là đường MIỄN PHÍ DUY NHẤT để biết: gate có kích không, có chặn oan
                    # không (metrics.tu_choi), và RAM LINUX THẬT là bao nhiêu. Mọi số đo trước bản vá là Windows
                    # WorkingSet, KHÔNG phải cgroup RSS của Render -> ngân sách MB tới giờ vẫn là SUY LUẬN.
                    "ban_ve": sum(1 for v in ss if v.get("bridge") is not None and v.get("co_ban_ve", True)),
                    "dang_nap": sum(1 for v in ss if v.get("nap_dem") and v.get("nap_tu")
                                    and now - v["nap_tu"] < NAP_HAN_S),
                    "dang_dong": sum(1 for v in ss if v.get("dang_dong") is not None),
                    "max_ban_ve": MAX_BAN_VE, "ram_mb": _ram_container_mb()})


def _keepalive_ping():
    """1 lần ping /health CỦA CHÍNH MÌNH qua URL công khai (traffic ngoài -> Render không ngủ). Nuốt lỗi.
    Trả True nếu có URL cấu hình (đã thử ping), False nếu không cấu hình (local/test -> không làm gì).
    ⚠ GIÁ TRỊ TRẢ VỀ LÀ HỢP ĐỒNG CỐ Ý (test_health L.3): True = 'đã THỬ ping', KỂ CẢ khi ping lỗi — để 1 lỗi mạng
    không làm chết luồng nền. Muốn biết ping thành/bại thì đọc _KEEPALIVE (bộ đếm), TUYỆT ĐỐI không đổi return."""
    if not _KEEPALIVE_URL:
        return False
    import urllib.request
    global _KA_OK_TS
    try:
        urllib.request.urlopen(_KEEPALIVE_URL.rstrip("/") + "/health", timeout=20).read(50)
        _KEEPALIVE["ok"] += 1
        _KA_OK_TS = time.time()
    except Exception as e:
        _KEEPALIVE["loi"] += 1
        # /health là endpoint KHÔNG xác thực -> CHỈ phơi TÊN LOẠI lỗi. Thông điệp đầy đủ của urllib có thể nhét
        # nguyên URL (kể cả query) mà env KEEPALIVE_URL cho phép trỏ địa chỉ khác RENDER_EXTERNAL_URL -> ra stderr.
        _KEEPALIVE["loi_cuoi"] = type(e).__name__
        if _KEEPALIVE["loi"] == 1 or _KEEPALIVE["loi"] % 10 == 0:     # lần đầu rồi mỗi 10 lần (chống spam log)
            print("[keepalive] LOI lan %d: %s: %s" % (_KEEPALIVE["loi"], type(e).__name__, e), file=sys.stderr, flush=True)
    return True


def _keepalive_loop():
    while True:
        # ⚠ THÂN VÒNG PHẢI CÓ LƯỚI: 1 ngoại lệ bất ngờ ở đây làm luồng nền CHẾT VĨNH VIỄN -> tính năng giữ-thức
        # tắt LẶNG LẼ trong khi /health vẫn báo lành. Đó ĐÚNG là khuôn "hỏng thầm" mà chính vòng này đi vá
        # (red-team bắt được: bản đầu của tôi mắc lại đúng lỗi nó đang chữa).
        try:
            # PING TRƯỚC rồi mới ngủ: bản cũ ngủ trước nên ping ĐẦU TIÊN chỉ xảy ra ở t=chu_kỳ (đo thật t=600s) ->
            # cửa sổ mù ngay sau boot/deploy, đúng lúc dễ ngủ nhất.
            _loi_truoc = _KEEPALIVE["loi"]
            _keepalive_ping()
            # Tín hiệu thất bại lấy từ BỘ ĐẾM, KHÔNG từ giá trị trả về (_keepalive_ping LUÔN trả True khi có URL ->
            # viết `if not _keepalive_ping()` thì nhánh thử-lại-nhanh là MÃ CHẾT vĩnh viễn).
            that_bai = _KEEPALIVE["loi"] > _loi_truoc
            nghi = 30 if that_bai else max(60, KEEPALIVE_MIN * 60)
        except Exception as e:
            _KEEPALIVE["loi"] += 1
            _KEEPALIVE["loi_cuoi"] = type(e).__name__
            print("[keepalive] LOI VONG LAP %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
            nghi = 60
        time.sleep(nghi)


def _start_keepalive():
    """Khởi động self-ping NỀN chỉ khi có URL công khai + KEEPALIVE_MIN>0 (production). Local/test: KHÔNG chạy.
    ⚠ Ping đầu tiên nằm BÊN TRONG luồng nền — gọi ping ĐỒNG BỘ ở đây sẽ chặn boot tới 20s (timeout của urlopen),
    tức làm NẶNG thêm chính cảnh báo health-check 5s đang muốn vá."""
    if _KEEPALIVE_URL and KEEPALIVE_MIN > 0:
        _KEEPALIVE["cau_hinh"] = True
        _KEEPALIVE["chu_ky_phut"] = KEEPALIVE_MIN
        threading.Thread(target=_keepalive_loop, daemon=True).start()
        print("[keepalive] self-ping %s/health moi %d phut" % (_KEEPALIVE_URL, KEEPALIVE_MIN), file=sys.stderr, flush=True)


_start_keepalive()


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    name = (f.filename or "").lower() if f else ""
    if not f or not (name.endswith(".dxf") or name.endswith(".dwg")):
        return jsonify({"error": "Chỉ nhận file .dxf hoặc .dwg."}), 400
    # Robustness J — DỌN file cũ mỗi lần upload (bound đĩa qua nhiều phiên): xoá _uploads/_renders quá TTL.
    cleanup_old_files([UPLOAD_DIR, RENDER_DIR], FILE_TTL_MIN)
    # E6 — tên đích DUY NHẤT theo uuid (GIỮ tên gốc làm hậu tố để vẫn là substring khi hiển thị): 2 phiên upload
    # trùng tên (vd 'plan.dwg') KHÔNG còn ghi đè cùng 1 path -> phiên A không bị phiên B đạp file đang render.
    dest = os.path.join(UPLOAD_DIR, uuid.uuid4().hex + "_" + os.path.basename(f.filename))
    f.save(dest)
    # Robustness I — CHẶN SỚM: file đã lưu > giới hạn parse -> loại NGAY (khỏi gọi MCP/convert/parse ~600s)
    # + DỌN file rác luôn (liên quan J). DWG NÉN dưới ngưỡng vẫn qua -> tools_core kiểm lại sau convert.
    raw_mb = os.path.getsize(dest) / (1024 * 1024)
    if raw_mb > READFILE_MAX_MB:
        try:
            os.remove(dest)
        except OSError:
            pass
        return jsonify({"error": "File tải lên (~%.0fMB) vượt giới hạn %dMB của gói máy chủ. Vui lòng thử file nhỏ hơn."
                        % (raw_mb, READFILE_MAX_MB)}), 413
    # GATE SỐ BẢN VẼ đặt ở ĐÂY — SAU cả 3 cửa rẻ (đuôi file -> lưu file -> trần MB). Đặt trước thì red-team đo
    # được: 1 request .txt cũng ĐUỔI được bản vẽ của đối tác, và 1 request sai đuôi làm cờ 'đang nạp' rỉ VĨNH VIỄN
    # (mọi người sau đó ăn 503 trong khi RAM trống). Đặt trước cũng KHÔNG tiết kiệm băng thông (tầng WSGI đã hút
    # hết body rồi mới tới view) nên không mua được gì.
    sid, s, ket, da_giu, s_cu = get_session(xin_suat=True)
    try:
        if ket == "ban":
            _xoa_file(dest)
            # NÓI ĐÚNG THỦ PHẠM: chỗ RAM có thể đang bị chính bản vẽ CŨ CỦA PHIÊN NÀY giữ (đang được giải phóng),
            # nói "cho người khác" trong ca đó là SAI sự thật.
            if s.get("dang_dong") is not None:
                return _tu_choi("Máy chủ đang giải phóng bộ nhớ của bản vẽ trước trong phiên của bạn. "
                                "Xin thử lại sau ít phút.")
            return _tu_choi("Máy chủ (gói miễn phí) chỉ đọc được một bản vẽ cùng lúc và đang đọc bản vẽ cho "
                            "người khác. Xin đợi khoảng một phút rồi bấm 'Tải lên & nạp' lại.")
        if s_cu is not None:
            # NHƯỜNG CHỖ: bản vẽ cũ PHẢI ra khỏi RAM TRƯỚC khi spawn tiến trình con mới, nếu không thì đúng lúc
            # giao thời có 2 bản vẽ cùng RAM = chính cái ta đang chặn. Không xác nhận được -> fail-closed, và
            # bridge đó VẪN được đếm (cờ 'dang_dong') nên không thành RAM vô hình.
            br_cu = s_cu.get("dang_dong")
            if not _dong_cho_chac(br_cu):
                _xoa_file(dest)
                # KHÔNG hứa mốc thời gian cụ thể: nếu tiến trình con cứng đầu thì cờ chỉ tự gỡ sau DONG_HAN_S.
                return _tu_choi("Máy chủ đang giải phóng bộ nhớ của bản vẽ trước. Xin thử lại sau ít phút; "
                                "nếu vẫn chưa được thì tải lại trang.")
            with _SESS_LOCK:
                if s_cu.get("dang_dong") is br_cu:
                    s_cu["dang_dong"] = None
        # Bounded lock — KHÔNG chờ khoá VÔ HẠN: đo thật, khoá bị giữ 12s làm request cùng phiên nằm 11.60s và
        # GIỮ CHẾT 1 trong 4 thread gunicorn -> ngưỡng vỡ của /health (Render chờ 5s) tới đúng ở N == --threads.
        if not s["lock"].acquire(timeout=LOCK_WAIT_S):
            _xoa_file(dest)
            return _tu_choi("Bản vẽ bạn gửi trước đang được xử lý. Xin đợi xong rồi thử lại.")
        try:                        # tuần tự hoá các request CÙNG phiên (khác phiên = khác bridge -> song song)
            with _SESS_LOCK:        # phiên có thể đã bị LRU/TTL pop trong lúc ta chờ khoá -> nạp vào dict MỒ CÔI
                con_song = SESSIONS.get(sid) is s
            if not con_song:
                return _tu_choi("Phiên của bạn đã hết hiệu lực. Xin tải lại trang rồi nạp lại bản vẽ.", 409)
            if s["bridge"] is None:
                s["bridge"] = _make_bridge()
            res = s["bridge"].call("nap_ban_ve", {"path": dest}, timeout=600)
            # ĐÒI DẤU HIỆU THÀNH CÔNG, đừng đòi dấu hiệu thất bại. `nap_ban_ve` KHÔNG trả {'loi'} khi lỗi — nó NÉM
            # (đã vá ở mcp_bridge.call: isError -> {'loi'}), nhưng vẫn giữ vành đai thứ hai theo HÌNH DẠNG: bản
            # tóm tắt thành công LUÔN có 'name'. Trước bản vá này, mọi lỗi nạp thật đều ra HTTP 200 '✅ Đã nạp'
            # kèm summary 'None (AutoCAD None), None đối tượng' — và summary đó được bơm vào prompt của Gemini.
            if (not isinstance(res, dict)) or res.get("loi") or res.get("name") is None:
                print("[upload] nap that bai: %r" % (res,), file=sys.stderr, flush=True)
                _nap_that_bai(s)    # bản vẽ CŨ đã bốc hơi ở tiến trình con -> đừng giữ mô tả của nó
                # KHÔNG trả nguyên văn 'ket_qua' ra trình duyệt: nó chứa đường dẫn tuyệt đối trên máy chủ.
                return jsonify({"error": "Không nạp được bản vẽ này (file có thể hỏng, không phải DXF/DWG hợp lệ, "
                                         "hoặc quá lớn sau khi chuyển đổi). Chi tiết đã ghi ở log máy chủ.",
                                "reset_xac_nhan": True}), 500
            s["summary"] = "%s (AutoCAD %s), %s đối tượng, %s layer." % (
                res.get("name"), res.get("dxfversion"), res.get("tong_doi_tuong"), res.get("so_layer"))
            s["history"] = []       # nạp bản vẽ mới -> quên hội thoại cũ (CỦA PHIÊN NÀY)
            s["co_ban_ve"] = True   # CÓ bản vẽ trong RAM (khác `bridge is not None`: nạp lỗi thì bridge còn, bản vẽ không)
            # GỠ CẢ HAI cờ lý do: không gỡ 'da_nhuong' thì lần mất bản vẽ SAU (vì lý do khác) vẫn báo "đã được
            # nhường cho người khác" = nói SAI lý do (red-team, mức TB).
            s["nap_loi"] = s["da_nhuong"] = False
        finally:
            s["lock"].release()
        _METRICS["uploads"] += 1    # L — đếm giám sát (hiện ở /health)
        return jsonify(res)
    except Exception as e:
        _METRICS["errors"] += 1
        _nap_that_bai(s)
        print("[upload] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"error": "Lỗi xử lý file: %s" % e, "reset_xac_nhan": True}), 500
    finally:
        _tra_suat(s)                # BẮT BUỘC bao CẢ HÀM: mọi đường ra đều phải nhả cờ 'đang nạp', kể cả 503/500


@app.route("/ask", methods=["POST"])
def ask():
    q = (request.json or {}).get("q", "").strip()
    if not q:
        return jsonify({"answer": "Hãy nhập câu hỏi.", "evidence": [], "ai": True})
    if not mcp_bridge.USE_AI:
        return jsonify({"answer": "Chưa cấu hình GEMINI_API_KEY trên máy chủ.", "evidence": [], "ai": True})
    sid, s = get_session()          # Robustness K — bridge/summary/history của PHIÊN NÀY
    if s["bridge"] is None or not s.get("co_ban_ve", True):
        return jsonify({"answer": _msg_khong_ban_ve(s), "evidence": [], "ai": True})
    try:
        # Bounded lock (cùng lý do như /upload): 1 lượt hỏi AI giữ khoá hàng chục giây, người dùng bấm gửi lần nữa
        # KHÔNG được nằm chờ vô hạn và ăn thêm 1 thread.
        if not s["lock"].acquire(timeout=LOCK_WAIT_S):
            # KHÔNG đoán nguyên nhân: khoá này có thể đang bị /upload (tải bản vẽ) giữ, không chỉ /ask.
            return _tu_choi("Phiên của bạn đang xử lý một việc khác (tải bản vẽ hoặc câu hỏi trước). "
                            "Xin đợi xong rồi hỏi tiếp.")
        try:                        # tuần tự hoá request cùng phiên (tránh 2 lượt đạp history/bridge)
            # TOCTOU: cửa kiểm 'bridge is None' ở trên nằm TRƯỚC khi lấy khoá, mà đường NHƯỜNG CHỖ (và _nap_that_bai)
            # đặt bridge=None khi khoá đang RẢNH -> request xếp hàng tới LOCK_WAIT_S có thể lọt qua cửa rồi mới thấy
            # None. ĐỌC LẠI 1 LẦN vào biến cục bộ + KIỂM LẠI (che MỌI kẻ đóng, không chỉ đường nhường).
            br = s.get("bridge")
            if br is None or not s.get("co_ban_ve", True):
                return jsonify({"answer": _msg_khong_ban_ve(s), "evidence": [], "ai": True})
            r = mcp_bridge.tra_loi_ai(br, q, s["summary"], history=s["history"])
            for _k in ("anh_id", "file_id"):   # R11: ghi nhận artifact CỦA phiên -> /image//file chỉ phục vụ id thuộc phiên này (chống IDOR)
                _v = r.get(_k) if isinstance(r, dict) else None
                if _v: s["artifacts"].add(os.path.basename(str(_v)))
            # Ghi lại lượt này vào lịch sử (chỉ hỏi + đáp cuối) + cắt giữ N lượt gần nhất.
            s["history"].append({"role": "user", "text": q})
            # I1: LƯU answer_goc (SẠCH, chưa nối cảnh báo handle) vào history — nếu lưu answer đã-nối thì lượt sau
            # model đọc lời tự-chê của chính nó -> có thể NGỪNG trích handle -> sập điểm bán hàng "trả lời kèm handle".
            s["history"].append({"role": "model", "text": (r.get("answer_goc") or r.get("answer", ""))})
            del s["history"][:-2 * MAX_HISTORY_TURNS]
        finally:
            s["lock"].release()
        _METRICS["asks"] += 1       # L — đếm giám sát (hiện ở /health)
        return jsonify(r)
    except Exception as e:
        _METRICS["errors"] += 1
        print("[ask] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"answer": "⚠ Lỗi khi hỏi AI: %s" % e, "evidence": [], "ai": True})


def _phien_hien_co():
    """RT-fix (CAO-2) — LẤY phiên theo cookie mà KHÔNG TẠO MỚI. get_session() luôn tạo phiên + đẩy LRU, nên
    các route xác nhận (nhất là GET danh-sách) từng có thể bị 4 lượt gọi VÔ DANH đuổi mất phiên đang mở bản
    vẽ của đối tác (MAX_SESSIONS=4). Cùng khuôn với _artifact_owned: chỉ tra cookie, refresh 'last' để phiên
    không hết hạn giữa lúc đang thao tác. Trả None nếu không có phiên."""
    sid = request.cookies.get("sid") or ""
    with _SESS_LOCK:
        s = SESSIONS.get(sid)
        if s is None:
            return None
        s["last"] = time.time()
        return s


@app.route("/xac-nhan", methods=["POST"])
def xac_nhan():
    """L5 (kho kiến thức, CONFIRM-ONLY) — kênh xác nhận CỦA NGƯỜI: nút bấm frontend gọi THẲNG endpoint này
    -> bridge.call host-side, KHÔNG đi qua chat/Gemini (tool 'xac_nhan_ky_hieu' nằm trong _TOOL_KHONG_CHO_LLM
    + gate dispatch L0 chặn) -> AI không thể tự bấm thay đối tác bằng bất kỳ đường nào. Fail-closed ở tầng
    Drawing (kb_id + option ∈ ENUM + câu hỏi ĐÃ phát trong phiên). KHÔNG đổi số — chỉ nhãn theo PHIÊN file."""
    s = _phien_hien_co()            # RT-fix (CAO-2): KHÔNG tạo phiên mới từ route xác nhận
    if s is None or s.get("bridge") is None or not s.get("co_ban_ve", True):
        # 'ly_do' + da_thu_hoi=False là BẮT BUỘC: nút ↩ Hoàn tác đọc DUY NHẤT r.ly_do, thiếu nó thì frontend rơi về
        # câu mặc định "Không gỡ được (có thể đã gỡ trước đó)" = người dùng TIN SAI là đã gỡ ('undo nói dối').
        _m = _msg_so_xn(s)
        return jsonify({"ok": False, "loi": _m, "ly_do": _m, "da_thu_hoi": False}), 400
    d = request.get_json(silent=True) or {}
    _th = d.get("thu_hoi")          # RT-fix (THẤP): ép kiểu CHẶT — chuỗi "false"/"0" là TRUTHY trong Python
    thu_hoi = (_th is True) or (isinstance(_th, str) and _th.strip().lower() in ("1", "true", "yes"))
    try:
        # Bounded lock — /ask giữ ĐÚNG khoá này suốt lượt hỏi AI: đo thật, bấm nút xác nhận ở tin nhắn CŨ trong lúc
        # đang gửi câu mới làm request nằm 11.60s (route GET danh-sách đã có timeout=3 từ trước, POST thì chưa).
        if not s["lock"].acquire(timeout=LOCK_WAIT_S):
            return _tu_choi("Phiên của bạn đang xử lý một việc khác. Xin bấm lại sau vài giây.")
        try:                        # tuần tự hoá với /ask cùng phiên (1 subprocess/bridge)
            br = s.get("bridge")    # TOCTOU: đọc LẠI dưới khoá rồi kiểm lại (xem ghi chú ở /ask)
            if br is None or not s.get("co_ban_ve", True):
                _m = _msg_so_xn(s)
                return jsonify({"ok": False, "loi": _m, "ly_do": _m, "da_thu_hoi": False}), 400
            r = br.call("xac_nhan_ky_hieu", {
                "kb_id": str(d.get("kb_id") or ""), "option_key": str(d.get("option_key") or ""),
                "ma": str(d.get("ma") or ""), "thu_hoi": thu_hoi})
        finally:
            s["lock"].release()
        return jsonify(r if isinstance(r, dict) else {"ok": False})
    except Exception as e:
        _METRICS["errors"] += 1
        print("[xac-nhan] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        _m = "Lỗi khi ghi nhận xác nhận: %s" % e
        return jsonify({"ok": False, "loi": _m, "ly_do": _m, "da_thu_hoi": False}), 500


@app.route("/xac-nhan/danh-sach")
def xac_nhan_danh_sach():
    """L5-fix (lát 2) — sổ xác nhận CÒN HIỆU LỰC của phiên, cho giao diện hiện bảng + nút Hoàn tác từng mục.
    CHỈ ĐỌC, host-only (tool 'danh_sach_xac_nhan' nằm trong _TOOL_KHONG_CHO_LLM + gate dispatch L0)."""
    s = _phien_hien_co()            # RT-fix (CAO-2): route CHỈ-ĐỌC này TUYỆT ĐỐI không được tạo phiên/đẩy LRU
    if s is None or s.get("bridge") is None or not s.get("co_ban_ve", True):
        # 'da_reset': sổ xác nhận sống trong tiến trình con -> bản vẽ ra khỏi RAM là sổ MẤT. Trước đây frontend
        # chỉ thấy so_muc=0 rồi ẨN bảng ÂM THẦM (tái sinh đúng RT-fix CAO-3) -> phải LỘ lý do cho người bấm nút.
        return jsonify({"so_muc": 0, "cac_muc": [],
                        "da_reset": bool(s and (s.get("nap_loi") or s.get("da_nhuong")))})
    if not s["lock"].acquire(timeout=3):   # RT-fix (THẤP): không chờ VÔ HẠN sau /ask (30-60s) hay /upload .dwg
        return jsonify({"so_muc": 0, "cac_muc": [], "dang_ban": True})
    try:
        br = s.get("bridge")        # TOCTOU: đọc LẠI dưới khoá rồi kiểm lại (xem ghi chú ở /ask)
        if br is None or not s.get("co_ban_ve", True):
            return jsonify({"so_muc": 0, "cac_muc": [],
                            "da_reset": bool(s.get("nap_loi") or s.get("da_nhuong"))})
        r = br.call("danh_sach_xac_nhan", {})
        return jsonify(r if isinstance(r, dict) else {"so_muc": 0, "cac_muc": []})
    except Exception as e:
        print("[xac-nhan/danh-sach] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"so_muc": 0, "cac_muc": []})
    finally:
        s["lock"].release()


def _artifact_owned(art_id):
    """R11 — chống IDOR: True nếu artifact-id (basename) THUỘC phiên hiện tại (cookie sid). KHÔNG tạo phiên mới cho
    asset request; refresh 'last' để phiên không TTL-hết trong lúc tải asset. Phiên khác/không cookie -> False -> 404."""
    base = os.path.basename(art_id or "")
    if not base:
        return False
    sid = request.cookies.get("sid") or ""
    with _SESS_LOCK:
        s = SESSIONS.get(sid)
        if s is None:
            return False
        s["last"] = time.time()
        return base in s.get("artifacts", ())


@app.route("/image/<anh_id>")
def image(anh_id):
    if not _artifact_owned(anh_id):   # R11: chỉ phục vụ ảnh CỦA phiên (chống IDOR cross-session)
        return jsonify({"error": "Không có ảnh."}), 404
    p = os.path.join(RENDER_DIR, os.path.basename(anh_id))
    if not os.path.isfile(p):
        return jsonify({"error": "Không có ảnh."}), 404
    return send_file(p, mimetype="image/png")


@app.route("/file/<file_id>")
def download_file(file_id):
    if not _artifact_owned(file_id):   # R11: chỉ phục vụ file CỦA phiên (chống IDOR cross-session)
        return jsonify({"error": "Không có file."}), 404
    p = os.path.join(RENDER_DIR, os.path.basename(file_id))
    if not os.path.isfile(p):
        return jsonify({"error": "Không có file."}), 404
    return send_file(p, as_attachment=True, download_name="tong_hop_khoi_luong.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


PAGE = r"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SynthBuild AI — Hệ Thống Tự Động Đọc Bản Vẽ AutoCAD & Lập Dự Toán</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-dark: #070b14;
  --bg-card: #0e1626;
  --bg-card-hover: #131e33;
  --border-card: #182844;
  --border-light: #22385e;
  --cyan-main: #00f2ff;
  --cyan-glow: rgba(0, 242, 255, 0.35);
  --text-main: #e2e9f5;
  --text-muted: #7387a8;
  --text-dim: #4d5f7c;
  --sidebar-width: 250px;
  --accent-green: #00e699;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-dark);
  color: var(--text-main);
  display: flex;
  height: 100vh;
  overflow: hidden;
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(10, 16, 28, 0.6); }
::-webkit-scrollbar-thumb { background: #1e3254; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00f2ff; }

.sidebar {
  width: var(--sidebar-width);
  background: #090e1a;
  border-right: 1px solid var(--border-card);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px 16px;
  user-select: none;
  z-index: 10;
}
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 36px; padding: 0 8px; }
.brand-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #00f2ff, #0066ff);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 15px var(--cyan-glow);
}
.brand-icon svg { width: 22px; height: 22px; fill: #070b14; }
.brand-text h2 { font-family: 'Outfit', sans-serif; font-size: 19px; font-weight: 800; color: #fff; line-height: 1.1; }
.brand-text span { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: var(--cyan-main); text-transform: uppercase; }

.nav-menu { display: flex; flex-direction: column; gap: 8px; }
.nav-item {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 16px; border-radius: 10px;
  font-size: 13.5px; font-weight: 600; color: var(--text-muted);
  cursor: pointer; transition: all 0.25s ease; border: 1px solid transparent;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.nav-item svg { width: 18px; height: 18px; fill: currentColor; transition: transform 0.2s; }
.nav-item:hover { color: var(--cyan-main); background: rgba(0, 242, 255, 0.05); border-color: rgba(0, 242, 255, 0.15); }
.nav-item:hover svg { transform: scale(1.1); }
.nav-item.active {
  color: var(--cyan-main);
  background: linear-gradient(90deg, rgba(0, 242, 255, 0.12), rgba(0, 242, 255, 0.02));
  border-left: 3px solid var(--cyan-main);
  box-shadow: inset 0 0 12px rgba(0, 242, 255, 0.08);
}

.btn-new-analysis {
  background: var(--cyan-main); color: #070b14;
  border: none; border-radius: 8px; padding: 14px;
  font-family: 'Outfit', sans-serif; font-size: 13px; font-weight: 800;
  letter-spacing: 1px; text-transform: uppercase; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 0 20px rgba(0, 242, 255, 0.4); transition: all 0.25s ease; margin-top: 20px;
}
.btn-new-analysis:hover { background: #33f5ff; transform: translateY(-2px); box-shadow: 0 0 25px rgba(0, 242, 255, 0.6); }

.main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: radial-gradient(circle at 50% 0%, #0e172a 0%, #070b14 70%); }
.topbar {
  height: 64px; border-bottom: 1px solid var(--border-card);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px; background: rgba(9, 14, 26, 0.8); backdrop-filter: blur(10px);
}
.search-box {
  display: flex; align-items: center; gap: 10px;
  background: #0b111e; border: 1px solid var(--border-card);
  border-radius: 20px; padding: 8px 18px; width: 360px; transition: border-color 0.2s;
}
.search-box:focus-within { border-color: var(--cyan-main); }
.search-box svg { fill: var(--text-muted); width: 16px; height: 16px; }
.search-box input { background: none; border: none; outline: none; color: #fff; font-size: 13px; width: 100%; }

.topbar-right { display: flex; align-items: center; gap: 20px; }
.ai-status-pill {
  display: flex; align-items: center; gap: 8px;
  background: rgba(0, 230, 153, 0.1); border: 1px solid rgba(0, 230, 153, 0.3);
  color: var(--accent-green); padding: 6px 14px; border-radius: 20px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.8px;
}
.ai-status-dot {
  width: 8px; height: 8px; background: var(--accent-green);
  border-radius: 50%; box-shadow: 0 0 10px var(--accent-green); animation: pulse 2s infinite;
}
@keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }

.top-icons { display: flex; align-items: center; gap: 14px; color: var(--text-muted); }
.top-icon-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; position: relative; transition: color 0.2s; }
.top-icon-btn:hover { color: var(--cyan-main); }
.top-icon-btn svg { width: 20px; height: 20px; fill: currentColor; }
.badge-dot { position: absolute; top: -2px; right: -2px; width: 8px; height: 8px; background: #ff4757; border-radius: 50%; }

.user-profile { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 34px; height: 34px; border-radius: 50%; border: 2px solid var(--cyan-main); object-fit: cover; box-shadow: 0 0 10px var(--cyan-glow); }
.user-info { display: flex; flex-direction: column; }
.user-name { font-size: 12px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }
.user-role { font-size: 10px; color: var(--text-muted); }

.content-area { flex: 1; overflow-y: auto; padding: 24px 28px; display: none; }
.content-area.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

.dashboard-grid { display: grid; grid-template-columns: 2.2fr 1fr; gap: 20px; }
.metrics-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 20px; position: relative; overflow: hidden; transition: border-color 0.25s; }
.stat-card:hover { border-color: var(--border-light); }
.stat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.stat-title { font-size: 11px; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; }
.stat-icon { color: var(--cyan-main); opacity: 0.8; }
.stat-value { font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 700; color: #fff; line-height: 1; margin-bottom: 8px; }
.stat-value span { font-size: 13px; font-weight: 600; color: var(--accent-green); margin-left: 6px; }
.stat-progress-bar { height: 4px; background: rgba(255, 255, 255, 0.08); border-radius: 2px; overflow: hidden; margin-top: 12px; }
.stat-progress-fill { height: 100%; background: linear-gradient(90deg, var(--cyan-main), #0066ff); border-radius: 2px; }
.segmented-bars { display: flex; gap: 4px; margin-top: 12px; }
.segment { height: 4px; flex: 1; background: var(--cyan-main); border-radius: 2px; }
.segment.dim { opacity: 0.2; }

.chart-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
.chart-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.chart-title h3 { font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 4px; }
.chart-title p { font-size: 11px; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; }
.toggle-group { display: flex; background: #080d17; border: 1px solid var(--border-card); border-radius: 6px; padding: 3px; }
.toggle-btn { padding: 6px 14px; font-size: 11px; font-weight: 700; color: var(--text-muted); background: none; border: none; cursor: pointer; border-radius: 4px; transition: all 0.2s; }
.toggle-btn.active { background: var(--cyan-main); color: #070b14; box-shadow: 0 0 10px var(--cyan-glow); }

.svg-chart-container { position: relative; width: 100%; height: 220px; margin-bottom: 20px; }
.chart-footer-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.05); }
.sub-stat-item label { font-size: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.8px; display: block; margin-bottom: 4px; }
.sub-stat-item val { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; color: #fff; }
.sub-stat-item val.cyan { color: var(--cyan-main); text-shadow: 0 0 10px var(--cyan-glow); }

.right-panel { display: flex; flex-direction: column; gap: 20px; }
.recent-drawings-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 20px; }
.card-top-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.card-top-head h4 { font-size: 12px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.link-btn { font-size: 11px; color: var(--cyan-main); text-decoration: none; cursor: pointer; }
.drawing-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
.drawing-item { display: flex; align-items: center; gap: 12px; background: #0a111f; border: 1px solid rgba(255, 255, 255, 0.04); padding: 10px; border-radius: 8px; }
.drawing-thumb { width: 46px; height: 46px; background: #152238; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
.drawing-info h5 { font-size: 13px; font-weight: 600; color: #fff; margin-bottom: 2px; }
.drawing-info p { font-size: 11px; color: var(--text-muted); }
.status-tag { font-size: 10px; font-weight: 700; color: var(--accent-green); display: flex; align-items: center; gap: 4px; margin-top: 4px; }
.status-tag.scanning { color: var(--cyan-main); }
.btn-sync-all { width: 100%; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.2); color: var(--cyan-main); border-radius: 8px; padding: 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
.btn-sync-all:hover { background: rgba(0, 242, 255, 0.18); border-color: var(--cyan-main); }

.assistant-widget { background: linear-gradient(145deg, #0e1729, #14223d); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 12px; padding: 20px; position: relative; box-shadow: 0 0 20px rgba(0, 0, 0, 0.4); }
.assistant-head { display: flex; align-items: center; gap: 10px; color: var(--cyan-main); margin-bottom: 12px; }
.assistant-head h4 { font-family: 'Outfit', sans-serif; font-size: 16px; font-weight: 700; color: #fff; }
.assistant-msg { font-size: 12.5px; color: var(--text-main); line-height: 1.5; margin-bottom: 16px; }
.assistant-actions { display: flex; gap: 10px; }
.btn-action-primary { flex: 1; background: var(--cyan-main); color: #070b14; border: none; border-radius: 6px; padding: 10px; font-size: 11px; font-weight: 800; cursor: pointer; }
.btn-action-sec { flex: 1; background: none; border: 1px solid var(--border-card); color: var(--text-muted); border-radius: 6px; padding: 10px; font-size: 11px; font-weight: 700; cursor: pointer; }

.cad-reader-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
.upload-zone-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; padding-bottom: 16px; border-bottom: 1px solid var(--border-card); }
.upload-btn-styled { background: linear-gradient(135deg, #1e355c, #132442); border: 1px solid var(--cyan-main); color: var(--cyan-main); padding: 10px 20px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 0 10px var(--cyan-glow); transition: all 0.2s; }
.upload-btn-styled:hover { background: var(--cyan-main); color: #070b14; }

#sum { display: none; margin-top: 14px; font-size: 13px; color: #c5d6f0; line-height: 1.7; background: #080e1a; border: 1px solid var(--border-card); border-radius: 8px; padding: 14px; white-space: pre-wrap; }
#chips { display: none; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.chip { background: #0e1d36; border: 1px solid #1f3763; color: #9ac2ff; padding: 7px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.chip:hover { background: #162c54; border-color: var(--cyan-main); color: #fff; }

.chat-box-container { background: #080d19; border: 1px solid var(--border-card); border-radius: 12px; display: flex; flex-direction: column; height: 520px; overflow: hidden; }
#chat { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
.msg { display: flex; flex-direction: column; }
.msg.me { align-items: flex-end; }
.msg.ai { align-items: flex-start; }
.bub { max-width: 85%; padding: 12px 16px; border-radius: 12px; font-size: 13.5px; line-height: 1.6; white-space: pre-wrap; }
.me .bub { background: linear-gradient(135deg, #0088ff, #0055cc); color: #fff; border-bottom-right-radius: 2px; }
.ai .bub { background: #0f192c; border: 1px solid var(--border-card); color: var(--text-main); border-bottom-left-radius: 2px; }
.ev { margin-top: 10px; font-family: 'Consolas', monospace; font-size: 11.5px; background: #070b14; padding: 10px; border-radius: 6px; border: 1px solid var(--border-card); }
.ev div { padding: 3px 0; border-top: 1px solid #16243d; }
.h { color: var(--accent-green); font-weight: 700; }
.lay { color: var(--text-muted); }
.shot { margin-top: 12px; border: 1px solid var(--cyan-main); border-radius: 8px; overflow: hidden; background: #000; box-shadow: 0 0 15px var(--cyan-glow); }
.shot img { width: 100%; display: block; cursor: zoom-in; }
.cap { font-size: 11px; color: var(--text-muted); margin-top: 6px; }

.ask-bar { padding: 14px; background: #0b1222; border-top: 1px solid var(--border-card); display: flex; gap: 10px; }
.ask-bar input { flex: 1; background: #060a12; border: 1px solid var(--border-card); border-radius: 8px; padding: 12px 16px; color: #fff; font-size: 13.5px; outline: none; }
.ask-bar input:focus { border-color: var(--cyan-main); }
.ask-bar button { background: var(--cyan-main); color: #070b14; border: none; border-radius: 8px; padding: 0 24px; font-weight: 800; font-size: 13px; cursor: pointer; }
.ask-bar button:disabled { opacity: 0.4; cursor: not-allowed; }

.table-header-bar { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }
.breadcrumb { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.breadcrumb span { color: var(--cyan-main); }
.table-title h2 { font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 800; color: #fff; }
.table-subtitle { font-size: 11px; color: var(--text-muted); font-weight: 600; }
.table-actions { display: flex; gap: 10px; }
.btn-table-action { background: #0f192d; border: 1px solid var(--border-card); color: var(--text-main); padding: 10px 18px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-table-action:hover { border-color: var(--cyan-main); color: var(--cyan-main); }

.estimate-table-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; overflow: hidden; margin-bottom: 60px; }
.custom-table { width: 100%; border-collapse: collapse; text-align: left; }
.custom-table th { background: #090f1d; padding: 14px 18px; font-size: 11px; font-weight: 700; color: var(--cyan-main); letter-spacing: 0.8px; text-transform: uppercase; border-bottom: 1px solid var(--border-card); }
.custom-table td { padding: 14px 18px; font-size: 13px; color: var(--text-main); border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
.custom-table tr:hover td { background: rgba(0, 242, 255, 0.02); }
.tag-code { font-family: 'Space Grotesk', monospace; color: #8aa4cc; font-size: 12px; }

.sticky-bottom-summary {
  position: fixed; bottom: 0; left: var(--sidebar-width); right: 0;
  height: 64px; background: rgba(7, 11, 20, 0.95); backdrop-filter: blur(12px);
  border-top: 1px solid var(--border-card); display: flex; align-items: center;
  justify-content: space-between; padding: 0 28px; z-index: 100;
}
.summary-metric { display: flex; align-items: center; gap: 12px; }
.summary-metric label { font-size: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; }
.summary-metric val { font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; color: #fff; }
.total-val { font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; color: var(--cyan-main); text-shadow: 0 0 15px var(--cyan-glow); }

.reports-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.reports-grid-2 { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; margin-bottom: 20px; }
.report-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 20px; }

.material-bar-list { display: flex; flex-direction: column; gap: 16px; margin-top: 30px; }
.material-item { display: flex; flex-direction: column; gap: 6px; }
.material-meta { display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: var(--text-muted); }
.material-bar-bg { height: 6px; background: rgba(255, 255, 255, 0.06); border-radius: 3px; overflow: hidden; }
.material-bar-fill { height: 100%; background: var(--cyan-main); border-radius: 3px; }

.donut-container { display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; height: 180px; }
.donut-center-text { position: absolute; text-align: center; }
.donut-center-text h4 { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 800; color: #fff; }
.donut-center-text p { font-size: 9px; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; }

.pie-legend { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.legend-row { display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; padding: 6px 0; border-bottom: 1px dashed rgba(255, 255, 255, 0.05); }

.reports-bottom-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px; }
.insight-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 12px; padding: 18px; }
.insight-card h5 { font-size: 11px; font-weight: 700; color: var(--cyan-main); letter-spacing: 0.8px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.insight-card p { font-size: 12px; color: var(--text-main); line-height: 1.5; }
</style>
</head>
<body>

<aside class="sidebar">
  <div>
    <div class="brand">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
      </div>
      <div class="brand-text">
        <h2>SynthBuild AI</h2>
        <span>DỰ TOÁN CHÍNH XÁC</span>
      </div>
    </div>

    <nav class="nav-menu">
      <div class="nav-item active" onclick="switchTab('dashboard', this)">
        <svg viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>
        BẢNG ĐIỀU KHIỂN
      </div>
      <div class="nav-item" onclick="switchTab('cad-reader', this)">
        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
        TRÌNH ĐỌC BẢN VẼ
      </div>
      <div class="nav-item" onclick="switchTab('estimate', this)">
        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
        DỰ TOÁN
      </div>
      <div class="nav-item" onclick="switchTab('reports', this)">
        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
        BÁO CÁO
      </div>
    </nav>
  </div>

  <button class="btn-new-analysis" onclick="switchTab('cad-reader', document.querySelectorAll('.nav-item')[1])">
    <span>+</span> PHÂN TÍCH MỚI
  </button>
</aside>

<div class="main-wrapper">
  <header class="topbar">
    <div class="search-box">
      <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
      <input type="text" placeholder="Tìm kiếm dự án hoặc bản vẽ...">
    </div>

    <div class="topbar-right">
      <div class="ai-status-pill">
        <div class="ai-status-dot"></div>
        AI HOẠT ĐỘNG
      </div>

      <div class="top-icons">
        <button class="top-icon-btn"><svg viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg></button>
        <button class="top-icon-btn"><svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg></button>
        <button class="top-icon-btn">
          <svg viewBox="0 0 24 24"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/></svg>
          <span class="badge-dot"></span>
        </button>
      </div>

      <div class="user-profile">
        <img class="user-avatar" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80" alt="User Avatar">
        <div class="user-info">
          <span class="user-name">QUẢN_TRỊ_HT</span>
          <span class="user-role">CẤP ĐỘ 04</span>
        </div>
      </div>
    </div>
  </header>

  <div id="tab-dashboard" class="content-area active">
    <div class="dashboard-grid">
      <div>
        <div class="metrics-row">
          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-title">TỔNG DỰ ÁN</span>
              <span class="stat-icon">❖</span>
            </div>
            <div class="stat-value">1.284 <span>+12.5%</span></div>
            <div class="stat-progress-bar"><div class="stat-progress-fill" style="width: 65%;"></div></div>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-title">ĐỘ CHÍNH XÁC QUÉT AI</span>
              <span class="stat-icon">◎</span>
            </div>
            <div class="stat-value">99,82% <span style="color:#7387a8;font-size:11px">ĐỘ TIN CẬY</span></div>
            <div class="segmented-bars">
              <div class="segment"></div><div class="segment"></div><div class="segment"></div><div class="segment"></div><div class="segment dim"></div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-title">TỔNG GIÁ TRỊ DỰ TOÁN</span>
              <span class="stat-icon">▤</span>
            </div>
            <div class="stat-value" style="color:var(--cyan-main)">$42,8M <span style="color:#7387a8;font-size:11px">USD</span></div>
            <div class="stat-progress-bar"><div class="stat-progress-fill" style="width: 88%; background: var(--cyan-main);"></div></div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <h3>Phân Tích Xu Hướng Chi Phí</h3>
              <p>CHI PHÍ DỰ KIẾN VS THỰC TẾ</p>
            </div>
            <div class="toggle-group">
              <button class="toggle-btn">HÀNG TUẦN</button>
              <button class="toggle-btn active">HÀNG THÁNG</button>
            </div>
          </div>

          <div class="svg-chart-container">
            <svg width="100%" height="100%" viewBox="0 0 600 200" preserveAspectRatio="none">
              <defs>
                <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#00f2ff" stop-opacity="0.3"/>
                  <stop offset="100%" stop-color="#00f2ff" stop-opacity="0.0"/>
                </linearGradient>
              </defs>
              <path d="M 0,160 Q 150,150 300,165 T 600,140" fill="none" stroke="#22385e" stroke-width="1.5" stroke-dasharray="4,4"/>
              <path d="M 0,170 C 100,160 150,110 250,150 C 320,170 360,70 450,130 C 520,180 560,90 600,70" fill="none" stroke="#00f2ff" stroke-width="3" filter="drop-shadow(0px 0px 8px rgba(0,242,255,0.8))"/>
              <path d="M 0,170 C 100,160 150,110 250,150 C 320,170 360,70 450,130 C 520,180 560,90 600,70 L 600,200 L 0,200 Z" fill="url(#chartGrad)"/>
            </svg>

            <div style="position:absolute; top:35%; left:58%; background:#0a1324; border:1px solid var(--cyan-main); padding:6px 12px; border-radius:6px; box-shadow:0 0 15px var(--cyan-glow);">
              <div style="font-size:9px; font-weight:700; color:var(--text-muted);">ĐỈNH ĐIỂM HIỆN TẠI</div>
              <div style="font-family:'Space Grotesk'; font-size:14px; font-weight:700; color:#fff;">$1,2M <span style="color:var(--accent-green);font-size:10px">▲ 4%</span></div>
            </div>
          </div>

          <div class="chart-footer-stats">
            <div class="sub-stat-item">
              <label>TỶ LỆ LỖI TRUNG BÌNH</label>
              <val>0,024%</val>
            </div>
            <div class="sub-stat-item">
              <label>TỐC ĐỘ DỰ TOÁN</label>
              <val>14,2s/bản vẽ</val>
            </div>
            <div class="sub-stat-item">
              <label>PHÂN BỔ NGUỒN LỰC</label>
              <val>82%</val>
            </div>
            <div class="sub-stat-item">
              <label>TÌNH TRẠNG HỆ THỐNG</label>
              <val class="cyan">TỐI ƯU</val>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="recent-drawings-card">
          <div class="card-top-head">
            <h4>BẢN VẼ GẦN ĐÂY</h4>
            <a class="link-btn">Xem Tất Cả</a>
          </div>

          <div class="drawing-list">
            <div class="drawing-item">
              <div class="drawing-thumb">📐</div>
              <div class="drawing-info">
                <h5>Skyline_T6...</h5>
                <p>DỰ TOÁN: $4,2M</p>
                <div class="status-tag">● ĐÃ XỬ LÝ</div>
              </div>
            </div>

            <div class="drawing-item">
              <div class="drawing-thumb">⚙️</div>
              <div class="drawing-info">
                <h5>HVAC_Centr...</h5>
                <p>DỰ TOÁN: $840K</p>
                <div class="status-tag scanning">● ĐANG QUÉT...</div>
              </div>
            </div>

            <div class="drawing-item">
              <div class="drawing-thumb">🏗️</div>
              <div class="drawing-info">
                <h5>Foundation...</h5>
                <p>DỰ TOÁN: $1,1M</p>
                <div class="status-tag">● ĐÃ XỬ LÝ</div>
              </div>
            </div>
          </div>

          <button class="btn-sync-all">⚡ ĐỒNG BỘ TẤT CẢ GẦN ĐÂY</button>
        </div>

        <div class="assistant-widget">
          <div class="assistant-head">
            <span>✨</span>
            <h4>Trợ Lý Synth</h4>
          </div>
          <p class="assistant-msg">"Tôi đã phát hiện sai lệch 14% trong chi phí vật liệu cho 'Skyline_T6'. Bạn có muốn tôi tính toán lại theo giá thị trường hiện tại không?"</p>
          <div class="assistant-actions">
            <button class="btn-action-primary">TÍNH TOÁN LẠI</button>
            <button class="btn-action-sec">BỎ QUA</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div id="tab-cad-reader" class="content-area">
    <div class="cad-reader-card">
      <div class="upload-zone-row">
        <label class="upload-btn-styled" for="up">
          📤 TẢI FILE AUTOCAD (.DWG / .DXF)
        </label>
        <input type="file" id="up" accept=".dxf,.dwg" style="display:none" onchange="upload()">
        <button class="btn-action-primary" id="btnUp" onclick="upload()" style="padding:10px 20px;">Tải lên &amp; Nạp</button>
      </div>

      <div id="sum"></div>
      <div id="chips"></div>
    </div>

    <div class="chat-box-container">
      <div id="chat">
        <div style="color:var(--text-muted); font-size:13px; text-align:center; margin-top:40px;">
          👉 Tải một bản vẽ lên, rồi hỏi: <i>“có bao nhiêu bộ cửa D1?”</i>, <i>“đánh dấu cửa D1 trên bản vẽ”</i>, <i>“khối lượng thép?”</i>...
        </div>
      </div>
      <div id="xnbox" style="display:none;margin:8px 16px;padding:10px;border:1px dashed var(--cyan-main);border-radius:8px;background:rgba(0,242,255,0.03)"></div>

      <div class="ask-bar">
        <input id="inp" type="text" placeholder="Hỏi tự do: “đánh dấu cửa D1”, “tổng số bộ cửa?”, “liệt kê sheet”..." disabled onkeydown="if(event.key==='Enter')send()">
        <button id="btnSend" onclick="send()" disabled>GỬI</button>
      </div>
    </div>
  </div>

  <div id="tab-estimate" class="content-area">
    <div class="table-header-bar">
      <div>
        <div class="breadcrumb">Bảng điều khiển / <span>Dự toán</span></div>
        <div class="table-title"><h2>Bảng bóc tách khối lượng</h2></div>
        <div class="table-subtitle">Mã dự án: SYNTH-4029-B | Hiệu chỉnh 21.05.2024</div>
      </div>
      <div class="table-actions">
        <button class="btn-table-action">📥 Xuất Excel/PDF</button>
        <button class="btn-table-action">⚡ Bộ lọc</button>
      </div>
    </div>

    <div class="estimate-table-card">
      <table class="custom-table">
        <thead>
          <tr>
            <th>Mã hiệu</th>
            <th>Diễn giải</th>
            <th>Số lượng</th>
            <th>Đơn vị</th>
            <th>Đơn giá ($)</th>
            <th>Thành tiền ($)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="tag-code">BT.1002</td>
            <td>Bê tông lót móng M100 đá 4x6</td>
            <td>45,80</td>
            <td>m³</td>
            <td>68,00</td>
            <td>3.114,40</td>
          </tr>
          <tr>
            <td class="tag-code">BT.2001</td>
            <td>Bê tông móng M300 đá 1x2</td>
            <td>182,40</td>
            <td>m³</td>
            <td>95,00</td>
            <td>17.328,00</td>
          </tr>
          <tr>
            <td class="tag-code">TP.1016</td>
            <td>Thép cốt tròn Ø16mm CB300-V</td>
            <td>14.850,00</td>
            <td>kg</td>
            <td>0,85</td>
            <td>12.622,50</td>
          </tr>
          <tr>
            <td class="tag-code">TP.1020</td>
            <td>Thép cốt tròn Ø20mm CB400-V</td>
            <td>28.400,00</td>
            <td>kg</td>
            <td>0,88</td>
            <td>24.992,00</td>
          </tr>
          <tr>
            <td class="tag-code">CUA.D1</td>
            <td>Cửa nhôm kính Xingfa hệ 55 (D1)</td>
            <td>38,00</td>
            <td>bộ</td>
            <td>240,00</td>
            <td>9.120,00</td>
          </tr>
          <tr>
            <td class="tag-code">CUA.D2</td>
            <td>Cửa gỗ công nghiệp MDF Melamine (D2)</td>
            <td>64,00</td>
            <td>bộ</td>
            <td>180,00</td>
            <td>11.520,00</td>
          </tr>
          <tr>
            <td class="tag-code">TG.3001</td>
            <td>Xây tường gạch đặc M75 dày 220mm</td>
            <td>320,50</td>
            <td>m³</td>
            <td>72,00</td>
            <td>23.076,00</td>
          </tr>
          <tr>
            <td class="tag-code">LAT.401</td>
            <td>Lát gạch Granit bóng kính 600x600</td>
            <td>1.250,00</td>
            <td>m²</td>
            <td>18,50</td>
            <td>23.125,00</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="sticky-bottom-summary">
      <div style="display:flex; gap:36px;">
        <div class="summary-metric">
          <label>SỐ DÒNG</label>
          <val>124</val>
        </div>
        <div class="summary-metric">
          <label>ĐỘ TIN CẬY</label>
          <div style="display:flex; align-items:center; gap:8px;">
            <val>98.4%</val>
            <div style="width:60px; height:4px; background:#16243d; border-radius:2px;"><div style="width:98%; height:100%; background:var(--accent-green);"></div></div>
          </div>
        </div>
      </div>
      <div>
        <span style="font-size:10px; font-weight:700; color:var(--text-muted); letter-spacing:1px; margin-right:12px;">TỔNG CỘNG DỰ TOÁN</span>
        <span class="total-val">$567.618,00</span>
      </div>
    </div>
  </div>

  <div id="tab-reports" class="content-area">
    <div class="reports-header">
      <div>
        <div class="breadcrumb">/ ROOT / PHÂN TÍCH / <span>TRỰC QUAN</span></div>
        <h2 style="font-family:'Outfit'; font-size:28px; font-weight:800; color:#fff;">Báo cáo phân tích thông minh</h2>
      </div>
      <div class="toggle-group">
        <button class="toggle-btn">XUẤT PDF</button>
        <button class="toggle-btn active">TRỰC TIẾP</button>
      </div>
    </div>

    <div class="reports-grid-2">
      <div class="report-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h4 style="font-size:11px; font-weight:700; color:var(--cyan-main); letter-spacing:1px;">PHÂN TÍCH KHỐI LƯỢNG VẬT TƯ</h4>
            <p style="font-size:10px; color:var(--text-muted);">PHÂN BỔ THEO LĨNH VỰC [TẤN]</p>
          </div>
          <span style="color:var(--cyan-main)">📈</span>
        </div>

        <div class="material-bar-list">
          <div class="material-item">
            <div class="material-meta"><span>THÉP</span><span>420 TẤN</span></div>
            <div class="material-bar-bg"><div class="material-bar-fill" style="width:75%;"></div></div>
          </div>
          <div class="material-item">
            <div class="material-meta"><span>BÊ TÔNG</span><span>1.280 TẤN</span></div>
            <div class="material-bar-bg"><div class="material-bar-fill" style="width:90%;"></div></div>
          </div>
          <div class="material-item">
            <div class="material-meta"><span>GẠCH ĐÁ</span><span>650 TẤN</span></div>
            <div class="material-bar-bg"><div class="material-bar-fill" style="width:45%;"></div></div>
          </div>
          <div class="material-item">
            <div class="material-meta"><span>GỖ</span><span>85 TẤN</span></div>
            <div class="material-bar-bg"><div class="material-bar-fill" style="width:20%;"></div></div>
          </div>
        </div>
      </div>

      <div class="report-card">
        <h4 style="font-size:11px; font-weight:700; color:var(--cyan-main); letter-spacing:1px; margin-bottom:4px;">PHÂN BỔ CHI PHÍ</h4>
        <p style="font-size:10px; color:var(--text-muted); margin-bottom:20px;">TỶ TRỌNG THỜI GIAN THỰC</p>

        <div class="donut-container">
          <svg width="160" height="160" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#101a2d" stroke-width="12"/>
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#00f2ff" stroke-width="12" stroke-dasharray="251.2" stroke-dashoffset="100" transform="rotate(-90 50 50)"/>
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#0088ff" stroke-width="12" stroke-dasharray="251.2" stroke-dashoffset="180" transform="rotate(-90 50 50)"/>
          </svg>
          <div class="donut-center-text">
            <h4>$2.4M</h4>
            <p>TỔNG DỰ TOÁN</p>
          </div>
        </div>

        <div class="pie-legend">
          <div class="legend-row">
            <span style="color:#00f2ff">■ THÉP_KẾT_CẤU</span>
            <span>42%</span>
          </div>
          <div class="legend-row">
            <span style="color:#0088ff">■ BÊ_TÔNG_CHUNG</span>
            <span>38%</span>
          </div>
          <div class="legend-row">
            <span style="color:#66a3ff">■ TƯỜNG_GẠCH</span>
            <span>20%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="reports-bottom-cards">
      <div class="insight-card">
        <h5>💡 ĐỀ XUẤT TỪ AI</h5>
        <p>Giá thép dự kiến tăng 4% trong Quý 3. Hệ thống đề xuất thu mua sớm để duy trì mức hiệu quả biến động 11.8%.</p>
      </div>

      <div class="insight-card">
        <h5>🔄 LẦN ĐỒNG BỘ CUỐI</h5>
        <p>Dữ liệu thị trường toàn cầu đã đồng bộ 14 phút trước. Giá nhà thầu địa phương đã cập nhật cho Khu vực 7B.</p>
      </div>

      <div class="insight-card">
        <h5>🛡️ CHẤT LƯỢNG MÃ</h5>
        <p>Đã xác minh 100% không ảo giác số liệu. Độ trễ hệ thống phản hồi cực nhanh 12ms.</p>
      </div>
    </div>
  </div>
</div>

<script>
function switchTab(tabId, el) {
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  document.querySelectorAll('.content-area').forEach(area => area.classList.remove('active'));
  if (el) el.classList.add('active');
  const target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');
}

const $=id=>document.getElementById(id);
async function jget(u){return (await fetch(u)).json()}
async function jpost(u,b,f){let o={method:'POST'};if(f){o.body=b}else{o.headers={'Content-Type':'application/json'};o.body=JSON.stringify(b)}
  let ez=m=>({error:m,answer:m,loi:m,ly_do:m,ok:false,da_thu_hoi:false,evidence:[]});
  try{let r=await fetch(u,o);try{return await r.json()}catch(e){return ez('⚠ Máy chủ trả về phản hồi không đọc được (HTTP '+r.status+'). Xin thử lại.')}}
  catch(e){return ez('⚠ Không kết nối được máy chủ. Xin kiểm tra mạng rồi thử lại.')}}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function ready(on){$('inp').disabled=!on;$('btnSend').disabled=!on}
function me(t){$('chat').innerHTML+=`<div class="msg me"><div class="bub">${esc(t)}</div></div>`;$('chat').scrollTop=1e9}
function evHtml(ev){if(!ev||!ev.length)return '';
  let g={},order=[];ev.forEach(x=>{let k=x.nhom||'';if(!(k in g)){g[k]=[];order.push(k)}g[k].push(x)});
  let multi=order.length>1||(order.length===1&&order[0]);
  return '<div class="ev">'+order.map(k=>{let head=(multi&&k)?`<div class="evh">▸ ${esc(k)}</div>`:'';
    return head+g[k].map(x=>`<div><span class="h">[${esc(x.handle)}]</span> <span class="lay">${esc(x.layer)}</span> — ${esc(x.text)}</div>`).join('')}).join('')+'</div>'}
function shot(id){return id?`<div class="shot"><img src="/image/${id}?t=${Date.now()}" onclick="window.open(this.src)"></div><div class="cap">🔴 Ảnh bản vẽ — khoanh đỏ vị trí cấu kiện (bấm để phóng to)</div>`:''}
function fileLink(fid){return fid?`<div class="cap"><a href="/file/${fid}" download style="color:var(--cyan-main);font-weight:700">📥 Tải bảng tổng hợp (Excel .xlsx)</a></div>`:''}
function bot(t,ev,anh,tag,fid){let e=evHtml(ev),im=shot(anh),fl=fileLink(fid);
  let tg=tag?'<div class="tag" style="display:inline-block;font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:10px;margin-bottom:8px;background:rgba(0,242,255,0.1);color:var(--cyan-main);border:1px solid rgba(0,242,255,0.3)">🤖 SynthBuild AI · MCP Engine · Ground-Truth Verified</div>':'';
  $('chat').innerHTML+=`<div class="msg ai"><div class="bub">${tg}${esc(t)}${im}${fl}${e}</div></div>`;$('chat').scrollTop=1e9;return $('chat').lastElementChild}
function showSum(d){let s=$('sum');if(d.error){s.style.display='block';s.textContent='⚠ '+d.error;if(d.reset_xac_nhan){ready(false);taiDanhSach()}return}
  let c=Object.entries(d.counts||{}).sort((a,b)=>b[1]-a[1]).slice(0,8).map(x=>x[0]+': '+x[1]).join('   ·   ');
  s.style.display='block';
  s.innerHTML=`<b>✅ Đã nạp:</b> ${esc(d.name)} (AutoCAD ${esc(d.dxfversion)})<br>• <b>${d.so_layer}</b> layer · <b>${d.tong_doi_tuong}</b> đối tượng · <b>${d.so_doan_chu}</b> đoạn chữ · <b>${d.so_kich_thuoc}</b> kích thước · thép <b>${d.thep_tong_kg}</b> kg<br><span class="lay">${esc(c)}</span>`;
  $('chips').style.display='flex';
  $('chips').innerHTML=['Đánh dấu cửa D1 trên bản vẽ','Có bao nhiêu bộ cửa D1?','Tổng số bộ cửa?','Khối lượng thép?','Liệt kê các sheet','Có bao nhiêu layer?']
    .map(t=>`<span class="chip" onclick="q('${t}')">${t}</span>`).join('');
  $('chat').innerHTML='';ready(true);taiDanhSach();
  bot('Đã nạp xong. Bạn có thể hỏi bất kỳ câu hỏi nào về bản vẽ — AI đọc dữ liệu vector thật qua MCP và khoanh đỏ cấu kiện trên hình ảnh.',null,null,false)}
async function upload(){let f=$('up').files[0];if(!f){alert('Hãy chọn file .dwg/.dxf');return}
  let dwg=f.name.toLowerCase().endsWith('.dwg');let fd=new FormData();fd.append('file',f);
  $('sum').style.display='block';$('sum').textContent=dwg?'⏳ Đang tải lên & chuyển đổi .dwg → nạp...':'⏳ Đang tải lên & nạp...';
  let bu=$('btnUp');if(bu){bu.disabled=true}
  try{showSum(await jpost('/upload',fd,true))}
  catch(e){$('sum').textContent='⚠ Mất kết nối khi đang tải file lên. Xin thử lại.';ready(false)}
  finally{if(bu){bu.disabled=false}}}
function q(t){$('inp').value=t;send()}
let _kbSeq=0;
function kbHtml(qs){if(!qs||!qs.length)return '';
  return qs.map(k=>{let bid='kbq'+(++_kbSeq);
    let btns=(k.phuong_an||[]).map(o=>`<button data-id="${esc(k.id)}" data-opt="${esc(o.key)}" data-ma="${esc(k.ma||'')}" onclick="xacNhanBtn(this,'${bid}')" style="margin:4px 6px 0 0;padding:5px 12px;border-radius:6px;border:1px solid var(--cyan-main);background:rgba(0,242,255,0.1);color:var(--cyan-main);cursor:pointer">${esc(o.label)}</button>`).join('');
    return `<div id="${bid}" style="margin-top:10px;padding:10px;border:1px dashed var(--cyan-main);border-radius:8px;background:rgba(0,242,255,0.02)">`+
      `<div>❓ <b>${esc(k.cau_hoi)}</b></div>${btns}`+
      `<div class="cap">Chỉ bạn bấm được — AI không tự chọn. Hiệu lực trong phiên file đang mở.</div></div>`}).join('')}
async function xacNhanBtn(b,bid){let el=$(bid);if(!el)return;
  let id=b.dataset.id,opt=b.dataset.opt,ma=b.dataset.ma;
  try{let r=await jpost('/xac-nhan',{kb_id:id,option_key:opt,ma:ma});
    if(r.ok){el.innerHTML='<div>✔ '+esc(r.ghi_chu||'Đã ghi nhận.')+'</div>'+
        `<button data-id="${esc(id)}" data-ma="${esc(ma)}" onclick="hoanTacBtn(this,'${bid}')" style="margin-top:6px;padding:4px 10px;border-radius:6px;border:1px solid #a76;background:#432;color:#fed;cursor:pointer">↩ Hoàn tác</button>`;
      taiDanhSach()}
    else{el.innerHTML+='<div class="cap">⚠ '+esc(r.ly_do||r.loi||'Không ghi nhận được.')+'</div>'}}
  catch(e){el.innerHTML+='<div class="cap">⚠ Lỗi kết nối khi xác nhận.</div>'}}
async function hoanTacBtn(b,bid){let el=$(bid);if(!el)return;
  try{let r=await jpost('/xac-nhan',{kb_id:b.dataset.id,ma:b.dataset.ma,option_key:'',thu_hoi:true});
    if(r.da_thu_hoi){el.innerHTML='<div>↩ '+esc(r.ghi_chu||'Đã gỡ xác nhận.')+'</div>'}
    else{el.innerHTML+='<div class="cap">⚠ '+esc(r.ly_do||'Không gỡ được.')+'</div>'}
    taiDanhSach()}
  catch(e){el.innerHTML+='<div class="cap">⚠ Lỗi kết nối khi hoàn tác.</div>'}}
async function taiDanhSach(){let box=$('xnbox');if(!box)return;
  try{let r=await jget('/xac-nhan/danh-sach');
    if(r.dang_ban){return}
    if(!r.so_muc){if(r.da_reset){box.style.display='block';box.innerHTML='<div class="cap">ℹ Bản vẽ không còn trong bộ nhớ máy chủ.</div>'}else{box.style.display='none';box.innerHTML=''}return}
    box.style.display='block';
    box.innerHTML='<div><b>🔖 Phiên này đã xác nhận '+r.so_muc+' mục</b></div>'+
      r.cac_muc.map(m=>`<div style="margin-top:4px">• <b>${esc(m.ma||m.ky_hieu)}</b> — ${esc(m.nghia_mo_ta||m.nghia_key||'')} `+
        `<button data-id="${esc(m.kb_id)}" data-ma="${esc(m.ma)}" onclick="hoanTacDs(this)" style="padding:2px 8px;border-radius:4px;border:1px solid #a76;background:#432;color:#fed;cursor:pointer">↩ Gỡ</button></div>`).join('')}
  catch(e){}}
async function hoanTacDs(b){let box=$('xnbox');
  try{let r=await jpost('/xac-nhan',{kb_id:b.dataset.id,ma:b.dataset.ma,option_key:'',thu_hoi:true});
    if(!r.da_thu_hoi&&box){box.innerHTML+='<div class="cap">⚠ '+esc(r.ly_do||r.loi||'Không gỡ được mục này.')+'</div>'}}
  catch(e){if(box){box.innerHTML+='<div class="cap">⚠ Lỗi kết nối khi gỡ.</div>'}}
  taiDanhSach()}
async function send(){let t=$('inp').value.trim();if(!t)return;me(t);$('inp').value='';
  let ph=bot('🤖 AI đang đọc & tra cứu qua MCP… 0s');let bub=ph.querySelector('.bub');
  ready(false);let sec=0,tm=setInterval(()=>{sec++;bub.textContent='🤖 AI đang đọc & tra cứu qua MCP… '+sec+'s'},1000);
  try{let r=await jpost('/ask',{q:t});clearInterval(tm);ph.remove();
    let el=bot(r.answer,r.evidence,r.anh_id,true,r.file_id);
    if(r.kb_cau_hoi&&r.kb_cau_hoi.length&&el){el.querySelector('.bub').innerHTML+=kbHtml(r.kb_cau_hoi);$('chat').scrollTop=1e9}}
  catch(e){clearInterval(tm);ph.remove();bot('⚠ Lỗi kết nối máy chủ.')}
  ready(true);$('inp').focus()}
async function init(){try{let c=await jget('/config');if(!c.use_ai){bot('⚠ Máy chủ chưa cấu hình GEMINI_API_KEY.')}}catch(e){}
  taiDanhSach()}
init();
</script>
</body>
</html>"""
if __name__ == "__main__":
    print("Demo 2 (MCP) chay tai: http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
