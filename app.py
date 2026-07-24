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
MAX_SESSIONS = int(os.environ.get("MAX_SESSIONS", "4"))
SESSION_TTL_MIN = int(os.environ.get("SESSION_TTL_MIN", "30"))

# Robustness L — KEEP-ALIVE + GIÁM SÁT. Render free ngủ sau ~15' idle -> cold-start; self-ping /health giữ THỨC
# (dùng RENDER_EXTERNAL_URL Render tự set -> traffic ngoài thật; chỉ chạy khi có URL = production, local/test KHÔNG kích).
# /health = endpoint NHẸ (no API/no bản vẽ) cho monitor ngoài (UptimeRobot...) + quan sát cơ bản (uptime/sessions/metrics).
START_TS = time.time()
_METRICS = {"uploads": 0, "asks": 0, "errors": 0}
KEEPALIVE_MIN = int(os.environ.get("KEEPALIVE_MIN", "10"))          # 0 = tắt self-ping
_KEEPALIVE_URL = (os.environ.get("KEEPALIVE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "").strip()


def _make_bridge():               # tách ra để test monkeypatch FakeBridge (khỏi spawn subprocess thật)
    return mcp_bridge.MCPBridge(["mcp_server.py"], cwd=BASE)


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
    for k in sorted(SESSIONS, key=lambda k: SESSIONS[k]["last"]):
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
    return jsonify(info)


@app.route("/health")
def health():
    """Robustness L — health check NHẸ (no API, no bản vẽ): cho Render healthCheckPath + monitor ngoài + self-ping.
    Trả trạng thái sống + quan sát cơ bản (uptime, số phiên đang mở, model, đếm request)."""
    return jsonify({"ok": True, "uptime_s": round(time.time() - START_TS),
                    "sessions": len(SESSIONS), "use_ai": mcp_bridge.USE_AI,
                    "model": getattr(mcp_bridge, "MODEL", None), "metrics": dict(_METRICS)})


def _keepalive_ping():
    """1 lần ping /health CỦA CHÍNH MÌNH qua URL công khai (traffic ngoài -> Render không ngủ). Nuốt lỗi.
    Trả True nếu có URL cấu hình (đã thử ping), False nếu không cấu hình (local/test -> không làm gì)."""
    if not _KEEPALIVE_URL:
        return False
    import urllib.request
    try:
        urllib.request.urlopen(_KEEPALIVE_URL.rstrip("/") + "/health", timeout=20).read(50)
    except Exception:
        pass
    return True


def _keepalive_loop():
    while True:
        time.sleep(max(60, KEEPALIVE_MIN * 60))
        _keepalive_ping()


def _start_keepalive():
    """Khởi động self-ping NỀN chỉ khi có URL công khai + KEEPALIVE_MIN>0 (production). Local/test: KHÔNG chạy."""
    if _KEEPALIVE_URL and KEEPALIVE_MIN > 0:
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
        with s["lock"]:             # tuần tự hoá các request CÙNG phiên (khác phiên = khác bridge -> song song)
            if s["bridge"] is None:
                s["bridge"] = _make_bridge()
            res = s["bridge"].call("nap_ban_ve", {"path": dest}, timeout=600)
            if isinstance(res, dict) and res.get("loi"):
                return jsonify({"error": res["loi"]}), 500
            s["summary"] = "%s (AutoCAD %s), %s đối tượng, %s layer." % (
                res.get("name"), res.get("dxfversion"), res.get("tong_doi_tuong"), res.get("so_layer"))
            s["history"] = []       # nạp bản vẽ mới -> quên hội thoại cũ (CỦA PHIÊN NÀY)
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
        with s["lock"]:             # tuần tự hoá request cùng phiên (tránh 2 lượt đạp history/bridge)
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
        _METRICS["asks"] += 1       # L — đếm giám sát (hiện ở /health)
        return jsonify(r)
    except Exception as e:
        _METRICS["errors"] += 1
        print("[ask] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"answer": "⚠ Lỗi khi hỏi AI: %s" % e, "evidence": [], "ai": True})


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
async function jpost(u,b,f){let o={method:'POST'};if(f){o.body=b}else{o.headers={'Content-Type':'application/json'};o.body=JSON.stringify(b)}return (await fetch(u,o)).json()}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
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
  $('chat').innerHTML='';ready(true);
  bot('Đã nạp xong. Hỏi bất kỳ điều gì — tôi đọc dữ liệu thật qua MCP, và có thể KHOANH ĐỎ cấu kiện ngay trên bản vẽ.',null,null,false)}
async function upload(){let f=$('up').files[0];if(!f){alert('Hãy chọn file .dwg/.dxf');return}
  let dwg=f.name.toLowerCase().endsWith('.dwg');let fd=new FormData();fd.append('file',f);
  $('sum').style.display='block';$('sum').textContent=dwg?'⏳ Đang tải lên & chuyển đổi .dwg → nạp...':'⏳ Đang tải lên & nạp...';
  showSum(await jpost('/upload',fd,true))}
function q(t){$('inp').value=t;send()}
async function send(){let t=$('inp').value.trim();if(!t)return;me(t);$('inp').value='';
  let ph=bot('🤖 AI đang đọc & tra cứu qua MCP… 0s');let bub=ph.querySelector('.bub');
  ready(false);let sec=0,tm=setInterval(()=>{sec++;bub.textContent='🤖 AI đang đọc & tra cứu qua MCP… '+sec+'s'},1000);
  try{let r=await jpost('/ask',{q:t});clearInterval(tm);ph.remove();bot(r.answer,r.evidence,r.anh_id,true,r.file_id)}
  catch(e){clearInterval(tm);ph.remove();bot('⚠ Lỗi kết nối máy chủ.')}
  ready(true);$('inp').focus()}
async function init(){try{let c=await jget('/config');if(!c.use_ai){bot('⚠ Máy chủ chưa cấu hình GEMINI_API_KEY.')}}catch(e){}}
init();
</script></body></html>"""

if __name__ == "__main__":
    print("Demo 2 (MCP) chay tai: http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
