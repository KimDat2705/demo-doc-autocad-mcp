# -*- coding: utf-8 -*-
"""
app.py — HOST của DEMO 2 (hướng MCP). Web Flask đóng vai "custom MCP host":
  upload .dwg/.dxf -> nạp vào MCP server -> Gemini hỏi-đáp QUA MCP -> trả lời + ẢNH KHOANH ĐỎ cấu kiện.

Khác demo 1: (1) kiến trúc MCP CHUẨN (server tách rời, cắm được Claude Desktop/Gemini CLI...);
            (2) TRỰC QUAN — thấy bản vẽ + highlight, không chỉ chữ. Vẫn deploy cloud (không cần AutoCAD).
Chạy: python app.py  ->  http://localhost:5050
"""
import os, sys
from flask import Flask, request, jsonify, send_file
import mcp_bridge

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE, "_uploads")
RENDER_DIR = os.path.join(BASE, "_renders")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

app = Flask(__name__)
app.json.ensure_ascii = False
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "150"))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

BRIDGE = None          # phiên MCP bền (lười khởi tạo)
SUMMARY = ""           # tóm tắt bản vẽ đang nạp (đưa vào system prompt)
CHAT_HISTORY = []      # lịch sử hội thoại [{role,text}] — để nhớ ngữ cảnh (đối tác nhập bù số thiếu ở lượt sau)
MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", "6"))  # số lượt (mỗi lượt = 1 hỏi + 1 đáp) giữ lại


def get_bridge():
    global BRIDGE
    if BRIDGE is None:
        BRIDGE = mcp_bridge.MCPBridge(["mcp_server.py"], cwd=BASE)
    return BRIDGE


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File vượt quá %d MB." % MAX_UPLOAD_MB}), 413


@app.route("/")
def index():
    return PAGE


@app.route("/config")
def config():
    return jsonify({"use_ai": mcp_bridge.USE_AI, "model": mcp_bridge.MODEL if mcp_bridge.USE_AI else None})


@app.route("/upload", methods=["POST"])
def upload():
    global SUMMARY
    f = request.files.get("file")
    name = (f.filename or "").lower() if f else ""
    if not f or not (name.endswith(".dxf") or name.endswith(".dwg")):
        return jsonify({"error": "Chỉ nhận file .dxf hoặc .dwg."}), 400
    dest = os.path.join(UPLOAD_DIR, os.path.basename(f.filename))
    f.save(dest)
    try:
        res = get_bridge().call("nap_ban_ve", {"path": dest}, timeout=600)
        if isinstance(res, dict) and res.get("loi"):
            return jsonify({"error": res["loi"]}), 500
        SUMMARY = "%s (AutoCAD %s), %s đối tượng, %s layer." % (
            res.get("name"), res.get("dxfversion"), res.get("tong_doi_tuong"), res.get("so_layer"))
        CHAT_HISTORY.clear()   # nạp bản vẽ mới -> quên hội thoại cũ
        return jsonify(res)
    except Exception as e:
        print("[upload] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"error": "Lỗi xử lý file: %s" % e}), 500


@app.route("/ask", methods=["POST"])
def ask():
    q = (request.json or {}).get("q", "").strip()
    if not q:
        return jsonify({"answer": "Hãy nhập câu hỏi.", "evidence": [], "ai": True})
    if not mcp_bridge.USE_AI:
        return jsonify({"answer": "Chưa cấu hình GEMINI_API_KEY trên máy chủ.", "evidence": [], "ai": True})
    try:
        r = mcp_bridge.tra_loi_ai(get_bridge(), q, SUMMARY, history=CHAT_HISTORY)
        # Ghi lại lượt này vào lịch sử (chỉ hỏi + đáp cuối) + cắt giữ N lượt gần nhất.
        CHAT_HISTORY.append({"role": "user", "text": q})
        CHAT_HISTORY.append({"role": "model", "text": r.get("answer", "")})
        del CHAT_HISTORY[:-2 * MAX_HISTORY_TURNS]
        return jsonify(r)
    except Exception as e:
        print("[ask] %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return jsonify({"answer": "⚠ Lỗi khi hỏi AI: %s" % e, "evidence": [], "ai": True})


@app.route("/image/<anh_id>")
def image(anh_id):
    p = os.path.join(RENDER_DIR, os.path.basename(anh_id))
    if not os.path.isfile(p):
        return jsonify({"error": "Không có ảnh."}), 404
    return send_file(p, mimetype="image/png")


@app.route("/file/<file_id>")
def download_file(file_id):
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
