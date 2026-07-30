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
MAX_SESSIONS = int(os.environ.get("MAX_SESSIONS", "4"))     # trần SỐ PHIÊN — phiên RỖNG chỉ ~965 byte (đo thật)
SESSION_TTL_MIN = int(os.environ.get("SESSION_TTL_MIN", "30"))
# ⚠ MAX_SESSIONS **KHÔNG PHẢI** trần RAM — đo thật (ma trận cap-vs-thread, 5/5 cấu hình): số bản vẽ nằm trong RAM
# bằng SỐ REQUEST ĐỒNG THỜI (gunicorn --threads), KHÔNG phụ thuộc cap này (cap=2/threads=4 vẫn ra 4 bản vẽ).
# Vì vậy hạ cap 4->2 tiết kiệm 0MB và còn MỞ 2 thread rảnh cho người mới -> tự bỏ lớp che mà threads==cap đang cho.
# Trần RAM thật sẽ là hạn mức SỐ BẢN VẼ (lát 2). Ở đây GIỮ 4.
LOCK_WAIT_S = int(os.environ.get("LOCK_WAIT_S", "3") or 3)  # trần chờ khoá PHIÊN (giây) — xem _tu_choi()

# Robustness L — KEEP-ALIVE + GIÁM SÁT. Render free ngủ sau ~15' idle -> cold-start; self-ping /health giữ THỨC
# (dùng RENDER_EXTERNAL_URL Render tự set -> traffic ngoài thật; chỉ chạy khi có URL = production, local/test KHÔNG kích).
# /health = endpoint NHẸ (no API/no bản vẽ) cho monitor ngoài (UptimeRobot...) + quan sát cơ bản (uptime/sessions/metrics).
START_TS = time.time()
_METRICS = {"uploads": 0, "asks": 0, "errors": 0, "tu_choi": 0}
# KEEPALIVE_MIN 10 -> 5: đo thật bằng đồng hồ ảo, chu kỳ 10' cho khoảng-2-ping 600s so với ngưỡng ngủ ~900s =>
# chịu được ĐÚNG 0 nhịp trượt (trượt 1 nhịp -> ping kế ở t=1200s > 900s -> máy ngủ). Chu kỳ 5' (300s) chịu 2 nhịp.
KEEPALIVE_MIN = int(os.environ.get("KEEPALIVE_MIN", "5"))           # 0 = tắt self-ping
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
    if s and s.get("bridge"):
        try:
            s["bridge"].close()
        except Exception:
            pass


def _try_close_session(sid):      # F-A — GỌI TRONG _SESS_LOCK: đóng phiên CHỈ KHI không đang phục vụ request (lock rảnh).
    """Bận (đang /upload hoặc /ask, giữ s['lock']) -> trả False, KHÔNG đóng — chống đóng subprocess GIỮA request đang
    chạy (cold-start 30-60s / .dwg-ODA tới 600s). acquire(blocking=False): rảnh -> đóng an toàn; bận -> bỏ qua."""
    s = SESSIONS.get(sid)
    if s is None:
        return True
    if not s["lock"].acquire(blocking=False):
        return False
    try:
        SESSIONS.pop(sid, None)
        if s.get("bridge"):
            try:
                s["bridge"].close()
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


def get_session():
    """Lấy (hoặc TẠO) phiên theo cookie 'sid'. Sweep TTL + enforce CAP (đóng LRU). Trả (sid, session) + stash
    g.sid để after_request set cookie. Bridge tạo LƯỜI ở /upload (phiên chưa upload -> KHÔNG tốn subprocess)."""
    now = time.time()
    sid = request.cookies.get("sid") or ""
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
            s = {"bridge": None, "summary": "", "history": [], "lock": threading.Lock(), "last": now, "artifacts": set()}
            SESSIONS[sid] = s
        s["last"] = now
    g.sid = sid
    return sid, s


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


@app.route("/health")
def health():
    """Robustness L — health check NHẸ (no API, no bản vẽ): cho Render healthCheckPath + monitor ngoài + self-ping.
    Trả trạng thái sống + quan sát cơ bản (uptime, số phiên đang mở, model, đếm request, trạng thái self-ping).
    ⚠ TUYỆT ĐỐI không lấy _SESS_LOCK ở đây (giữ /health miễn nhiễm tranh chấp khoá) và không bao giờ trả != 200:
    render.yaml dùng healthCheckPath=/health để GATE DEPLOY -> trả 500 vì self-ping lỗi = tự chặn deploy của mình.
    ⚠ KHÔNG đưa _KEEPALIVE_URL hay str(e) đầy đủ ra ngoài dạng URL — endpoint này KHÔNG xác thực."""
    ka = dict(_KEEPALIVE)
    ka["giay_tu_lan_ok_cuoi"] = round(time.time() - _KA_OK_TS) if _KA_OK_TS else None
    return jsonify({"ok": True, "uptime_s": round(time.time() - START_TS),
                    "sessions": len(SESSIONS), "use_ai": mcp_bridge.USE_AI,
                    "model": getattr(mcp_bridge, "MODEL", None), "metrics": dict(_METRICS),
                    "keepalive": ka})


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
        # PING TRƯỚC rồi mới ngủ: bản cũ ngủ trước nên ping ĐẦU TIÊN chỉ xảy ra ở t=chu_kỳ (đo thật t=600s) ->
        # cửa sổ mù ngay sau boot/deploy, đúng lúc dễ ngủ nhất.
        _loi_truoc = _KEEPALIVE["loi"]
        _keepalive_ping()
        # Tín hiệu thất bại lấy từ BỘ ĐẾM, KHÔNG từ giá trị trả về (_keepalive_ping LUÔN trả True khi có URL ->
        # viết `if not _keepalive_ping()` thì nhánh thử-lại-nhanh là MÃ CHẾT vĩnh viễn).
        that_bai = _KEEPALIVE["loi"] > _loi_truoc
        time.sleep(30 if that_bai else max(60, KEEPALIVE_MIN * 60))


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
    sid, s = get_session()          # Robustness K — bridge/summary/history theo PHIÊN (không đạp người khác)
    try:
        # Bounded lock — KHÔNG chờ khoá VÔ HẠN: đo thật, khoá bị giữ 12s làm request cùng phiên nằm 11.60s và
        # GIỮ CHẾT 1 trong 4 thread gunicorn -> ngưỡng vỡ của /health (Render chờ 5s) tới đúng ở N == --threads.
        if not s["lock"].acquire(timeout=LOCK_WAIT_S):
            _xoa_file(dest)
            return _tu_choi("Bản vẽ bạn gửi trước đang được xử lý. Xin đợi xong rồi thử lại.")
        try:                        # tuần tự hoá các request CÙNG phiên (khác phiên = khác bridge -> song song)
            if s["bridge"] is None:
                s["bridge"] = _make_bridge()
            res = s["bridge"].call("nap_ban_ve", {"path": dest}, timeout=600)
            if isinstance(res, dict) and res.get("loi"):
                return jsonify({"error": res["loi"]}), 500
            s["summary"] = "%s (AutoCAD %s), %s đối tượng, %s layer." % (
                res.get("name"), res.get("dxfversion"), res.get("tong_doi_tuong"), res.get("so_layer"))
            s["history"] = []       # nạp bản vẽ mới -> quên hội thoại cũ (CỦA PHIÊN NÀY)
        finally:
            s["lock"].release()
        _METRICS["uploads"] += 1    # L — đếm giám sát (hiện ở /health)
        return jsonify(res)
    except Exception as e:
        _METRICS["errors"] += 1
        print("[upload] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"error": "Lỗi xử lý file: %s" % e}), 500


@app.route("/ask", methods=["POST"])
def ask():
    q = (request.json or {}).get("q", "").strip()
    if not q:
        return jsonify({"answer": "Hãy nhập câu hỏi.", "evidence": [], "ai": True})
    if not mcp_bridge.USE_AI:
        return jsonify({"answer": "Chưa cấu hình GEMINI_API_KEY trên máy chủ.", "evidence": [], "ai": True})
    sid, s = get_session()          # Robustness K — bridge/summary/history của PHIÊN NÀY
    if s["bridge"] is None:
        return jsonify({"answer": "Chưa nạp bản vẽ cho phiên này. Hãy tải file .dxf/.dwg trước.",
                        "evidence": [], "ai": True})
    try:
        # Bounded lock (cùng lý do như /upload): 1 lượt hỏi AI giữ khoá hàng chục giây, người dùng bấm gửi lần nữa
        # KHÔNG được nằm chờ vô hạn và ăn thêm 1 thread.
        if not s["lock"].acquire(timeout=LOCK_WAIT_S):
            return _tu_choi("Máy chủ đang trả lời câu hỏi trước của bạn. Xin đợi câu trả lời hiện tại rồi hỏi tiếp.")
        try:                        # tuần tự hoá request cùng phiên (tránh 2 lượt đạp history/bridge)
            r = mcp_bridge.tra_loi_ai(s["bridge"], q, s["summary"], history=s["history"])
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
    if s is None or s.get("bridge") is None:
        # 'ly_do' + da_thu_hoi=False là BẮT BUỘC: nút ↩ Hoàn tác đọc DUY NHẤT r.ly_do, thiếu nó thì frontend rơi về
        # câu mặc định "Không gỡ được (có thể đã gỡ trước đó)" = người dùng TIN SAI là đã gỡ ('undo nói dối').
        _m = "Chưa nạp bản vẽ cho phiên này."
        return jsonify({"ok": False, "loi": _m, "ly_do": _m, "da_thu_hoi": False}), 400
    d = request.get_json(silent=True) or {}
    _th = d.get("thu_hoi")          # RT-fix (THẤP): ép kiểu CHẶT — chuỗi "false"/"0" là TRUTHY trong Python
    thu_hoi = (_th is True) or (isinstance(_th, str) and _th.strip().lower() in ("1", "true", "yes"))
    try:
        # Bounded lock — /ask giữ ĐÚNG khoá này suốt lượt hỏi AI: đo thật, bấm nút xác nhận ở tin nhắn CŨ trong lúc
        # đang gửi câu mới làm request nằm 11.60s (route GET danh-sách đã có timeout=3 từ trước, POST thì chưa).
        if not s["lock"].acquire(timeout=LOCK_WAIT_S):
            return _tu_choi("Máy chủ đang trả lời câu hỏi. Xin bấm lại sau vài giây.")
        try:                        # tuần tự hoá với /ask cùng phiên (1 subprocess/bridge)
            r = s["bridge"].call("xac_nhan_ky_hieu", {
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
    if s is None or s.get("bridge") is None:
        return jsonify({"so_muc": 0, "cac_muc": []})
    if not s["lock"].acquire(timeout=3):   # RT-fix (THẤP): không chờ VÔ HẠN sau /ask (30-60s) hay /upload .dwg
        return jsonify({"so_muc": 0, "cac_muc": [], "dang_ban": True})
    try:
        r = s["bridge"].call("danh_sach_xac_nhan", {})
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
<title>Demo 2 — Đọc & Trực quan hoá bản vẽ qua MCP</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Roboto,Arial,sans-serif;background:#0f1623;color:#e7edf5}
header{background:#13203a;border-bottom:1px solid #1f3354;padding:16px 22px}
header h1{font-size:18px;color:#7db4ff} header p{font-size:12.5px;color:#9fb2cc;margin-top:3px}
.badge{display:inline-block;background:#1d3a6b;color:#9fc6ff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;margin-left:8px}
.wrap{max-width:980px;margin:18px auto;padding:0 16px}
.card{background:#16203a;border:1px solid #25395f;border-radius:12px;padding:14px;margin-bottom:14px}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
input[type=text]{padding:10px;border-radius:8px;font-size:14px;background:#0f1828;color:#e7edf5;border:1px solid #2c426b}
button{padding:9px 14px;border:0;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;background:#2f7bf6;color:#fff}
button.sec{background:#22304d;color:#cdd9ee}
button:disabled{opacity:.5;cursor:default}
#sum{display:none;margin-top:12px;font-size:13px;color:#bcd0ec;line-height:1.7;border-top:1px dashed #28406a;padding-top:10px;white-space:pre-wrap}
#chips{display:none;gap:7px;flex-wrap:wrap;margin-top:8px}
.chip{background:#1b2c4d;border:1px solid #2e477a;color:#9fc6ff;padding:6px 11px;border-radius:18px;font-size:12.5px;cursor:pointer}
.chip:hover{background:#23396a}
#chat{min-height:240px;max-height:56vh;overflow:auto;padding:6px}
.msg{margin:9px 0;display:flex} .me{justify-content:flex-end}
.bub{max-width:88%;padding:10px 13px;border-radius:13px;white-space:pre-wrap;line-height:1.55;font-size:14px}
.me .bub{background:#2f7bf6;color:#fff;border-bottom-right-radius:4px}
.ai .bub{background:#13203a;border:1px solid #25395f;border-bottom-left-radius:4px;color:#e7edf5}
.ev{margin-top:8px;font-family:Consolas,monospace;font-size:12px}
.ev div{padding:4px 0;border-top:1px solid #25395f} .h{color:#5fd394;font-weight:600}
.evh{color:#7db4ff;font-weight:700;font-family:'Segoe UI',Arial,sans-serif;margin-top:6px;border-top:0!important}
.lay{color:#7f90ab}
.shot{margin-top:10px;border:1px solid #2e477a;border-radius:8px;overflow:hidden;background:#fff}
.shot img{width:100%;display:block;cursor:zoom-in}
.cap{font-size:11.5px;color:#9fb2cc;margin-top:5px}
.ask{display:flex;gap:8px;margin-top:6px}
.ask input{flex:1}
.muted{color:#7f90ab;font-size:12px;margin-top:8px}
.tag{display:inline-block;font-size:10.5px;font-weight:700;padding:1px 6px;border-radius:10px;margin-bottom:5px;background:#3a2c0e;color:#ffcf7a;border:1px solid #6b531c}
</style></head><body>
<header>
  <h1>🏗️ Đọc & Trực quan hoá bản vẽ AutoCAD <span class="badge">DEMO 2 · MCP</span></h1>
  <p>LLM (Gemini) kết nối công cụ đọc bản vẽ qua <b>Model Context Protocol</b>. Trả lời kèm <b>handle</b> truy nguồn, và <b>khoanh đỏ cấu kiện ngay trên bản vẽ</b> — không bịa, chạy trên cloud.</p>
</header>
<div class="wrap">
  <div class="card">
    <div class="row">
      <span style="font-weight:600;color:#7db4ff">📤 Tải bản vẽ (.dwg/.dxf): </span>
      <input type="file" id="up" accept=".dxf,.dwg" style="font-size:12px;color:#cdd9ee">
      <button class="sec" onclick="upload()">Tải lên &amp; nạp</button>
    </div>
    <div id="sum"></div>
    <div id="chips"></div>
  </div>
  <div class="card">
    <div id="chat"><div class="muted">👉 Tải một bản vẽ lên, rồi hỏi: “có bao nhiêu bộ cửa D1?”, “đánh dấu cửa D1 trên bản vẽ”, “khối lượng thép?”...</div></div>
    <div id="xnbox" style="display:none;margin-top:8px;padding:8px;border:1px dashed #a76;border-radius:8px"></div>
    <div class="ask">
      <input id="inp" type="text" placeholder="Hỏi tự do: “đánh dấu cửa D1”, “tổng số bộ cửa?”, “liệt kê sheet”..." disabled onkeydown="if(event.key==='Enter')send()">
      <button id="btnSend" onclick="send()" disabled>Gửi</button>
    </div>
  </div>
  <div class="muted">Hỗ trợ trực tiếp .dwg (tự chuyển đổi trên máy chủ) và .dxf. Mọi con số do công cụ tất định tính — kèm handle để truy nguồn.</div>
</div>
<script>
const $=id=>document.getElementById(id);
async function jget(u){return (await fetch(u)).json()}
/* M3 — jpost KHÔNG BAO GIỜ nem: trước đây .json() nem trên phản hồi KHÔNG-JSON (trang 500 HTML của Flask, 502 của
   Render, kết nối bị đóng) mà upload() lại KHÔNG có try/catch -> ô tóm tắt đứng MÃI ở '⏳ Đang tải lên & nạp...'.
   Trả về object có ĐỦ khoá mọi chỗ hiển thị đang đọc (error/answer/loi/ly_do/ok/da_thu_hoi) -> luôn hiện được CHỮ. */
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
function fileLink(fid){return fid?`<div class="cap"><a href="/file/${fid}" download style="color:#9ad9b4;font-weight:600">📥 Tải bảng tổng hợp (Excel .xlsx)</a></div>`:''}
function bot(t,ev,anh,tag,fid){let e=evHtml(ev),im=shot(anh),fl=fileLink(fid);
  let tg=tag?'<div class="tag">🤖 Gemini · qua MCP · số liệu &amp; handle do công cụ tính</div>':'';
  $('chat').innerHTML+=`<div class="msg ai"><div class="bub">${tg}${esc(t)}${im}${fl}${e}</div></div>`;$('chat').scrollTop=1e9;return $('chat').lastElementChild}
function showSum(d){let s=$('sum');if(d.error){s.style.display='block';s.textContent='⚠ '+d.error;return}
  let c=Object.entries(d.counts||{}).sort((a,b)=>b[1]-a[1]).slice(0,8).map(x=>x[0]+': '+x[1]).join('   ·   ');
  s.style.display='block';
  s.innerHTML=`<b>✅ Đã nạp:</b> ${esc(d.name)} (AutoCAD ${esc(d.dxfversion)})<br>• <b>${d.so_layer}</b> layer · <b>${d.tong_doi_tuong}</b> đối tượng · <b>${d.so_doan_chu}</b> đoạn chữ · <b>${d.so_kich_thuoc}</b> kích thước · thép <b>${d.thep_tong_kg}</b> kg<br><span class="lay">${esc(c)}</span>`;
  $('chips').style.display='flex';
  $('chips').innerHTML=['Đánh dấu cửa D1 trên bản vẽ','Có bao nhiêu bộ cửa D1?','Tổng số bộ cửa?','Khối lượng thép?','Liệt kê các sheet','Có bao nhiêu layer?']
    .map(t=>`<span class="chip" onclick="q('${t}')">${t}</span>`).join('');
  $('chat').innerHTML='';ready(true);taiDanhSach();   /* RT-fix (CAO-3): nạp file mới -> bảng phải phản ánh phiên MỚI (server đã reset), không giữ mục file cũ */
  bot('Đã nạp xong. Hỏi bất kỳ điều gì — tôi đọc dữ liệu thật qua MCP, và có thể KHOANH ĐỎ cấu kiện ngay trên bản vẽ.',null,null,false)}
async function upload(){let f=$('up').files[0];if(!f){alert('Hãy chọn file .dwg/.dxf');return}
  let dwg=f.name.toLowerCase().endsWith('.dwg');let fd=new FormData();fd.append('file',f);
  $('sum').style.display='block';$('sum').textContent=dwg?'⏳ Đang tải lên & chuyển đổi .dwg → nạp...':'⏳ Đang tải lên & nạp...';
  /* M3 — hàng rào THỨ HAI (jpost đã không nem): dù có gì bất ngờ, ô tóm tắt cũng phải hiện CHỮ chứ không đứng mãi */
  try{showSum(await jpost('/upload',fd,true))}
  catch(e){$('sum').textContent='⚠ Mất kết nối khi đang tải file lên. Xin kiểm tra mạng rồi bấm "Tải lên & nạp" lại.';ready(false)}}
function q(t){$('inp').value=t;send()}
/* L5 (kho kiến thức) — câu hỏi CONFIRM-ONLY: hệ hỏi với phương án soạn sẵn, CHỈ NGƯỜI bấm (POST /xac-nhan,
   không đi qua chat/AI). Nút bấm dùng data-attribute (esc cả dấu nháy) — chống chèn thuộc tính từ mã người gõ. */
let _kbSeq=0;
function kbHtml(qs){if(!qs||!qs.length)return '';
  return qs.map(k=>{let bid='kbq'+(++_kbSeq);
    let btns=(k.phuong_an||[]).map(o=>`<button data-id="${esc(k.id)}" data-opt="${esc(o.key)}" data-ma="${esc(k.ma||'')}" onclick="xacNhanBtn(this,'${bid}')" style="margin:3px 4px 0 0;padding:4px 10px;border-radius:8px;border:1px solid #4a5;background:#173;color:#cfe;cursor:pointer">${esc(o.label)}</button>`).join('');
    return `<div id="${bid}" style="margin-top:8px;padding:8px;border:1px dashed #4a5;border-radius:8px">`+
      `<div>❓ <b>${esc(k.cau_hoi)}</b></div>${btns}`+
      `<div class="cap">Chỉ bạn bấm được — AI không tự chọn. Hiệu lực trong phiên file đang mở; không thay đổi con số nào.</div></div>`}).join('')}
/* Bấm 1 phương án -> ghi nhận, rồi THAY bằng dòng kết quả + NÚT HOÀN TÁC (không xoá trắng khối như trước:
   trước đây bấm xong là mất hết đường quay lại, kể cả khi lỡ bấm 'khác/không chắc' làm ẩn câu hỏi cả phiên). */
async function xacNhanBtn(b,bid){let el=$(bid);if(!el)return;
  let id=b.dataset.id,opt=b.dataset.opt,ma=b.dataset.ma;
  try{let r=await jpost('/xac-nhan',{kb_id:id,option_key:opt,ma:ma});
    if(r.ok){el.innerHTML='<div>✔ '+esc(r.ghi_chu||'Đã ghi nhận.')+'</div>'+
        `<button data-id="${esc(id)}" data-ma="${esc(ma)}" onclick="hoanTacBtn(this,'${bid}')" style="margin-top:6px;padding:4px 10px;border-radius:8px;border:1px solid #a76;background:#432;color:#fed;cursor:pointer">↩ Hoàn tác</button>`;
      taiDanhSach()}
    else{el.innerHTML+='<div class="cap">⚠ '+esc(r.ly_do||r.loi||'Không ghi nhận được.')+'</div>'}}
  catch(e){el.innerHTML+='<div class="cap">⚠ Lỗi kết nối khi xác nhận.</div>'}}
/* Hoàn tác: gửi ĐÚNG cờ thu_hoi + đúng mã đã bấm; chỉ báo thành công khi server nói THẬT SỰ gỡ được
   (kiểm r.da_thu_hoi chứ KHÔNG kiểm r.ok — chống 'undo nói dối'). */
async function hoanTacBtn(b,bid){let el=$(bid);if(!el)return;
  try{let r=await jpost('/xac-nhan',{kb_id:b.dataset.id,ma:b.dataset.ma,option_key:'',thu_hoi:true});
    if(r.da_thu_hoi){el.innerHTML='<div>↩ '+esc(r.ghi_chu||'Đã gỡ xác nhận.')+'</div>'}
    else{el.innerHTML+='<div class="cap">⚠ '+esc(r.ly_do||'Không gỡ được (có thể đã gỡ trước đó).')+'</div>'}
    taiDanhSach()}
  catch(e){el.innerHTML+='<div class="cap">⚠ Lỗi kết nối khi hoàn tác.</div>'}}
/* Bảng THƯỜNG TRỰC 'phiên này đã xác nhận N mục' — gỡ được cả mục ở tin nhắn đã trôi lên trên,
   và cho người dùng sau thấy cú bấm người trước để lại (demo dùng chung, không đăng nhập). */
async function taiDanhSach(){let box=$('xnbox');if(!box)return;
  try{let r=await jget('/xac-nhan/danh-sach');
    if(!r.so_muc){box.style.display='none';box.innerHTML='';return}
    box.style.display='block';
    box.innerHTML='<div><b>🔖 Phiên này đã xác nhận '+r.so_muc+' mục</b> <span class="lay">(chỉ là ghi chú — không thay đổi con số nào)</span></div>'+
      r.cac_muc.map(m=>`<div style="margin-top:4px">• <b>${esc(m.ma||m.ky_hieu)}</b> — ${esc(m.nghia_mo_ta||m.nghia_key||'')} `+
        `<button data-id="${esc(m.kb_id)}" data-ma="${esc(m.ma)}" onclick="hoanTacDs(this)" style="padding:2px 8px;border-radius:6px;border:1px solid #a76;background:#432;color:#fed;cursor:pointer">↩ Gỡ</button></div>`).join('')}
  catch(e){}}
/* Nút Gỡ trong bảng: cũng phải kiểm r.da_thu_hoi (KHÔNG nuốt lỗi) — cùng luật với hoanTacBtn, nếu không thì
   server trả trung thực 'không gỡ được' mà người dùng thấy dòng cứ nằm đó, không hiểu vì sao. */
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
  taiDanhSach()}   /* RT-fix (CAO-3): tải/refresh trang -> hiện ngay xác nhận CÒN HIỆU LỰC (kể cả do người trước để lại) */
init();
</script></body></html>"""

if __name__ == "__main__":
    print("Demo 2 (MCP) chay tai: http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
