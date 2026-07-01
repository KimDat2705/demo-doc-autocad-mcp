# -*- coding: utf-8 -*-
"""
mcp_bridge.py — CẦU NỐI Gemini <-> MCP server (cho host Flask của demo 2).

Vì sao tự viết bridge (không dùng auto-MCP của google-genai):
  - google-genai 2.10.0 deepcopy config CHỨA ClientSession -> lỗi (stream/lock không copy được).
  - Tự bridge: giữ 1 phiên MCP BỀN trên 1 vòng asyncio chạy luồng nền (không teardown mỗi request),
    Gemini dùng client ĐỒNG BỘ + FunctionDeclaration sinh từ MCP schema -> KHÔNG nhét session vào config.
  - Quan trọng nhất: GIỮ NGUYÊN vòng lặp tự điều khiển + mọi chốt CHỐNG BỊA của demo 1
    (số do code/tool, kèm handle, temperature=0, ép gọi tool, ranh giới năng lực).
"""
import os, sys, json, asyncio, threading

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE = os.path.dirname(os.path.abspath(__file__))


def _load_env():
    """Nạp GEMINI_API_KEY từ .env của demo 2, hoặc fallback .env demo 1 (cùng key)."""
    for p in (os.path.join(BASE, ".env"),
              os.path.normpath(os.path.join(BASE, "..", "demo_doc_autocad", ".env"))):
        if os.path.isfile(p):
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
# Mặc định gemini-2.5-flash: ỔN ĐỊNH + NHANH (2-8s) + quota free cao + chất lượng đủ tốt
# (giữ trap-refusal + answer multi-part). Đã thử 3.5-flash nhưng bản mới hay 503 "high demand"
# (timeout) -> không ổn cho đối tác. Pro preview thì quota ~25 req là cạn (429).
# -> 2.5-flash là cân bằng tốt nhất cho DEMO. Đổi qua env GEMINI_MODEL khi cần (vd 3.5-flash lúc hết tải).
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
# 14 (cũ 8): câu nhiều phần ("công trình gì, mấy tầng, mấy phòng") cần nhiều lượt gọi tool;
# Flash gọi tool kém gọn hơn Pro -> 8 lượt dễ hết -> AI bỏ cuộc dù data có sẵn. Nới rộng.
MAX_TURNS = int(os.environ.get("GEMINI_MAX_TURNS", "14"))

try:
    from google import genai
    from google.genai import types
    _GENAI_OK = True
except Exception:
    _GENAI_OK = False

USE_AI = (os.environ.get("USE_AI", "1") != "0") and _GENAI_OK and bool(API_KEY)


# ----------------------------------------------------------------------------
# BRIDGE: 1 phiên MCP bền trên vòng asyncio nền
# ----------------------------------------------------------------------------
class MCPBridge:
    def __init__(self, server_args, cwd=None, env=None):
        # Truyền env đầy đủ cho MCP server con (kế thừa os.environ + override) — để biến như
        # READFILE_MAX_MB/ODA_EXE/GEMINI tới được tiến trình con (mặc định mcp chỉ truyền 1 tập tối thiểu).
        self.sp = StdioServerParameters(command=sys.executable, args=server_args, cwd=cwd or BASE,
                                        env={**os.environ, **(env or {})})
        self.loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._err = None
        self._stop = None
        self.session = None
        self.tools = []
        threading.Thread(target=self._run, daemon=True).start()
        if not self._ready.wait(40):
            raise RuntimeError("Không khởi động được MCP server: %s" % (self._err or "timeout"))
        if self._err:
            raise RuntimeError("MCP server lỗi: %s" % self._err)

    def _run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._serve())
        except Exception as e:
            self._err = "%s: %s" % (type(e).__name__, e)
            self._ready.set()

    async def _serve(self):
        self._stop = asyncio.Event()
        async with stdio_client(self.sp) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                self.session = session
                self.tools = (await session.list_tools()).tools
                self._ready.set()
                await self._stop.wait()

    def call(self, name, args, timeout=120):
        fut = asyncio.run_coroutine_threadsafe(self.session.call_tool(name, args or {}), self.loop)
        res = fut.result(timeout=timeout)
        txt = "\n".join(getattr(c, "text", "") or "" for c in res.content)
        try:
            return json.loads(txt)
        except Exception:
            return {"ket_qua": txt}

    def close(self):
        if self._stop:
            self.loop.call_soon_threadsafe(self._stop.set)


# ----------------------------------------------------------------------------
# MCP tool schema -> google.genai FunctionDeclaration
# ----------------------------------------------------------------------------
_JT = {"string": "STRING", "integer": "INTEGER", "number": "NUMBER",
       "boolean": "BOOLEAN", "object": "OBJECT", "array": "ARRAY"}


def _schema(js):
    T = types.Type
    if not js:
        return types.Schema(type=T.OBJECT, properties={})
    props = {}
    for k, v in (js.get("properties") or {}).items():
        t = getattr(T, _JT.get(v.get("type", "string"), "STRING"))
        props[k] = types.Schema(type=t, description=(v.get("description") or v.get("title") or ""))
    return types.Schema(type=T.OBJECT, properties=props, required=js.get("required") or [])


def gemini_tools(mcp_tools):
    decls = []
    for t in mcp_tools:
        if t.name == "nap_ban_ve":   # host tự nạp, KHÔNG để LLM gọi
            continue
        decls.append(types.FunctionDeclaration(
            name=t.name, description=(t.description or "")[:1024], parameters=_schema(t.inputSchema)))
    return [types.Tool(function_declarations=decls)]


SYSTEM_PROMPT = (
    "Bạn là trợ lý đọc dữ liệu bản vẽ AutoCAD cho kỹ sư xây dựng, gọi CÔNG CỤ qua MCP. "
    "QUY TẮC BẮT BUỘC:\n"
    "★ PHÂN BIỆT 'con số KỸ THUẬT của file' (số đối tượng, số lần một chuỗi xuất hiện, số lần chèn block, "
    "số nhãn) với 'ĐẠI LƯỢNG THỰC TẾ của công trình' (số cấu kiện, kích thước, khối lượng). Khi nêu số kỹ "
    "thuật phải nói rõ bản chất; KHÔNG trình bày như số lượng thực tế. Mỗi công cụ trả 'ghi_chu' giải thích "
    "con số LÀ GÌ — đọc và truyền đúng.\n"
    "1. CHỈ trả lời dựa trên dữ liệu CÔNG CỤ trả về. Không suy đoán, không bịa, không dùng kiến thức ngoài file.\n"
    "2. Mọi con số phải lấy từ công cụ — GỌI CÔNG CỤ trước, đừng trả lời chay. KHÔNG tự cộng/trừ/tính.\n"
    "3. Hỏi 'CÓ BAO NHIÊU / SỐ LƯỢNG' cấu kiện -> tra_cuu_so_luong (nếu bản vẽ ghi sẵn SL=). "
    "Liệt kê loại+số lượng -> liet_ke_so_luong. Tổng cùng nhóm -> tong_so_luong. "
    "Thép tròn kg/thanh -> thong_ke_thep; thép hình/inox -> thong_ke_thep_hinh.\n"
    "4. Người dùng muốn 'CHỈ RA / ĐÁNH DẤU / XEM Ở ĐÂU / HIGHLIGHT' cấu kiện trên bản vẽ -> GỌI "
    "danh_dau_cau_kien (trả anh_id để hiển thị ảnh có khoanh đỏ). Truyền ĐÚNG cụm từ người dùng nêu "
    "(vd 'cửa D1', KHÔNG rút thành 'D1' kẻo bắt nhầm dầm D1). Sau khi gọi, nói ngắn gọn đã đánh dấu bao nhiêu vị trí.\n"
    "5. Nếu công cụ trả 0 kết quả/không có -> nói thẳng 'Không có thông tin này trong bản vẽ.' KHÔNG bịa.\n"
    "6. Với nội dung cụ thể, KÈM handle (vd [2A3F]) từ công cụ. KHÔNG bịa handle.\n"
    "7. Đường kính thép (Ø/D/phi) đã được công cụ tự quy 1 dạng. Mác bê tông ghi nhiều kiểu — nếu 1 từ khoá "
    "ra 0 kết quả, thử biến thể ('mác'/'B20'/'250#'/'M200') trước khi kết luận không có. Trích NGUYÊN VĂN chuỗi file ghi.\n"
    "8. Phân biệt 2 việc: (A) SUY DIỄN kích thước tổng thể từ hình học/toạ độ = KHÔNG làm được -> TỪ CHỐI; "
    "(B) ĐỌC một giá trị GHI SẴN trên bản vẽ = ĐƯỢC PHÉP (đó là đọc dữ liệu, không phải suy diễn).\n"
    "  • TỪ CHỐI (A): 'CÔNG TRÌNH DÀI/RỘNG/CAO/DIỆN TÍCH bao nhiêu m', 'CAO ĐỘ tầng X', 'khoảng cách giữa 2 trục/2 cột' "
    "-> nói 'chưa hỗ trợ suy ra kích thước/cao độ tổng thể từ hình học'. ⛔ KHÔNG lấy DIMENSION lớn nhất (vd 58800mm) làm "
    "'chiều dài công trình', KHÔNG lấy cao độ (+3.600) làm cao độ tầng.\n"
    "  • ĐƯỢC PHÉP (B) — hãy GỌI TOOL tìm_kiếm/thong_tin_kich_thuoc rồi trích: giá trị GHI SẴN trong ghi chú "
    "(diện tích lát gạch '591m2', độ dốc mái 'i=32%', bề dày lớp '100mm', đường kính ống 'DN80'), số lượng/giá trị/min-max "
    "của các ĐƯỜNG KÍCH THƯỚC (kèm caveat 'là giá trị trên đường kích thước, không phải kích thước tổng công trình'). "
    "Với các câu này TUYỆT ĐỐI KHÔNG từ chối kiểu 'chưa hỗ trợ' — phải TÌM và trích nguyên văn kèm handle.\n"
    "8b. THÉP: 'tổng thép' -> nêu RIÊNG thép tròn (thong_ke_thep) và thép hình (thong_ke_thep_hinh). "
    "⛔ TUYỆT ĐỐI KHÔNG cộng thép tròn + thép hình thành MỘT con số tổng (vd 564.8+3545.9). Mỗi bảng là một loại riêng; "
    "có thể còn thép ghi trong ghi chú text (xà gồ...) chưa vào bảng — nếu hỏi tổng, nói rõ gồm những phần nào, đừng tự gộp.\n"
    "10. TÍNH TOÁN (takeoff — giai đoạn 2): câu hỏi TÍNH đại lượng của MỘT CẤU KIỆN — 'TỔNG DIỆN TÍCH cửa D1', "
    "'THỂ TÍCH bê tông cột C1', 'VÁN KHUÔN cột C1' -> GỌI `tinh_dai_luong` (KHÔNG tự nhân/cộng). LƯU Ý: đây là ngoại lệ "
    "của luật 8 — 'diện tích/thể tích của MỘT CẤU KIỆN cụ thể' thì TÍNH được (khác 'diện tích/chiều dài TỔNG công trình' vẫn từ chối).\n"
    "  • Tool trả `co_ket_qua=true` -> trình bày KẾT QUẢ + `so_do_he_thong_tinh` (công thức + từng input + nguồn). Nếu có input "
    "`chua_chac` (GÁN VỊ TRÍ) -> nói rõ 'số này hệ thống TÍNH, phần kích thước lấy theo vị trí nên CHƯA CHẮC 100%, đối tác nên xác nhận'.\n"
    "  • Tool trả `can_bo_sung=true` (THIẾU số liệu) -> NÊU RÕ: đã có gì (`inputs_da_co` + giá trị), CÒN THIẾU gì (`inputs_thieu`), "
    "MỜI đối tác cấp số thiếu (nhập qua chat, đơn vị mm). TUYỆT ĐỐI KHÔNG bịa số thiếu.\n"
    "  • Đối tác cấp số thiếu (vd 'chiều cao cột C1 = 3.6m') -> GỌI LẠI `tinh_dai_luong` với `inputs_bo_sung` JSON quy về mm "
    "(vd '{\"chieu_cao\":3600}').\n"
    "9. Trả lời tiếng Việt, ngắn gọn, đúng vai kỹ sư."
)


def _evidence_from(result, group):
    """Rút mọi item có 'handle' trong result -> evidence (gắn nhóm để UI hiển thị đúng cụm)."""
    ev = []
    def walk(v):
        if isinstance(v, dict):
            if "handle" in v and v.get("handle"):
                txt = v.get("text") or v.get("noi_dung") or v.get("title") or ""
                if "so_luong" in v and v.get("noi_dung"):
                    txt = "%s → %s" % (v["noi_dung"], v["so_luong"])
                ev.append({"handle": v["handle"], "layer": v.get("layer", "") or "",
                           "text": txt, "nhom": group})
            else:
                for x in v.values(): walk(x)
        elif isinstance(v, list):
            for x in v: walk(x)
    walk(result)
    return ev


def _flat_ev(evidence, per_group=20, total_cap=60):
    seen, groups, order = set(), {}, []
    for e in evidence:
        h, g = e.get("handle", ""), e.get("nhom", "")
        if h and (g, h) in seen: continue
        seen.add((g, h))
        groups.setdefault(g, [])
        if g not in order: order.append(g)
        if len(groups[g]) < per_group: groups[g].append(e)
    out = []
    for g in order:
        for e in groups[g]:
            out.append(e)
            if len(out) >= total_cap: return out
    return out


def _msg_finish(fr):
    n = getattr(fr, "name", str(fr)) if fr is not None else None
    if n == "MAX_TOKENS": return "AI bị cắt do trả lời quá dài. Hãy hỏi hẹp hơn."
    if n in ("SAFETY", "RECITATION", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII"):
        return "Nội dung bị bộ lọc an toàn của AI chặn (%s). Thử diễn đạt lại." % n
    if n == "MALFORMED_FUNCTION_CALL": return "AI gọi công cụ sai định dạng. Hãy thử hỏi lại."
    return None


_client = None
def _get_client():
    global _client
    if _client is None:
        http = types.HttpOptions(timeout=60000, retry_options=types.HttpRetryOptions(
            attempts=3, initial_delay=1.0, max_delay=8.0,
            http_status_codes=[429, 500, 502, 503, 504]))
        _client = genai.Client(api_key=API_KEY, http_options=http)
    return _client


def tra_loi_ai(bridge, q, file_summary=""):
    """Vòng hỏi-đáp: Gemini gọi MCP tool qua bridge. Trả {answer, evidence, anh_id, ai}."""
    tools = gemini_tools(bridge.tools)
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT + ("\n\nBản vẽ đang nạp: " + file_summary if file_summary else ""),
        tools=tools, temperature=0, max_output_tokens=8192,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
    client = _get_client()
    contents = [types.Content(role="user", parts=[types.Part(text=q)])]
    evidence, anh_id = [], None
    da_goi, da_nhac = False, False

    for _ in range(MAX_TURNS):
        resp = client.models.generate_content(model=MODEL, contents=contents, config=cfg)
        cand = (resp.candidates or [None])[0]
        if not cand or not cand.content:
            return {"answer": _msg_finish(getattr(cand, "finish_reason", None)) or
                    "AI tạm không trả về nội dung, vui lòng thử lại.",
                    "evidence": _flat_ev(evidence), "anh_id": anh_id, "ai": True}
        parts = cand.content.parts or []
        fcalls = [p.function_call for p in parts if getattr(p, "function_call", None)]
        if fcalls:
            da_goi = True
            contents.append(cand.content)
            rparts = []
            for fc in fcalls:
                args = dict(fc.args or {})
                try:
                    result = bridge.call(fc.name, args)
                except Exception as e:
                    result = {"loi": "Lỗi khi chạy công cụ: %s" % e}
                if isinstance(result, dict) and result.get("anh_id"):
                    anh_id = result["anh_id"]
                grp = fc.name + (": " + str(args.get("tu_khoa") or args.get("layer") or args.get("loc") or "")
                                 if any(k in args for k in ("tu_khoa", "layer", "loc")) else "")
                evidence.extend(_evidence_from(result, grp.strip(": ")))
                rparts.append(types.Part(function_response=types.FunctionResponse(name=fc.name, response=result)))
            contents.append(types.Content(role="user", parts=rparts))
            continue
        text = "".join(getattr(p, "text", "") or "" for p in parts if not getattr(p, "thought", False)).strip()
        special = _msg_finish(getattr(cand, "finish_reason", None))
        if special and not text:
            return {"answer": special, "evidence": _flat_ev(evidence), "anh_id": anh_id, "ai": True}
        if (not da_goi) and (not da_nhac) and any(c.isdigit() for c in text):
            da_nhac = True
            contents.append(cand.content)
            contents.append(types.Content(role="user", parts=[types.Part(text=(
                "Bạn nêu con số nhưng CHƯA gọi công cụ. Hãy GỌI công cụ phù hợp rồi trả lời lại theo kết quả. "
                "Không có công cụ phù hợp thì nói 'Không có thông tin này trong bản vẽ.'"))]))
            continue
        if not text:
            return {"answer": "AI không đưa ra nội dung, vui lòng thử lại.",
                    "evidence": _flat_ev(evidence), "anh_id": anh_id, "ai": True}
        return {"answer": text, "evidence": _flat_ev(evidence), "anh_id": anh_id, "ai": True}

    # Hết lượt tool mà chưa chốt (Flash hay LẶP gọi tool) -> ÉP trả lời NGAY từ dữ liệu ĐÃ thu,
    # KHÔNG gọi thêm tool, KHÔNG bỏ cuộc -> tránh "đọc thiếu" khi data thực ra đã có trong evidence.
    contents.append(types.Content(role="user", parts=[types.Part(text=(
        "Đã đủ dữ liệu từ các công cụ ở trên. HÃY TRẢ LỜI NGAY dựa trên kết quả công cụ đã thu được, "
        "KHÔNG gọi thêm công cụ nữa. Nếu một phần thật sự thiếu thì nói rõ phần đó, nhưng vẫn trả lời "
        "những gì đã có. TUYỆT ĐỐI KHÔNG nói 'câu hỏi cần quá nhiều bước'."))]))
    cfg_final = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT + ("\n\nBản vẽ đang nạp: " + file_summary if file_summary else ""),
        temperature=0, max_output_tokens=8192)   # KHÔNG truyền tools -> model buộc tự trả lời từ dữ liệu đã có
    try:
        resp = client.models.generate_content(model=MODEL, contents=contents, config=cfg_final)
        cand = (resp.candidates or [None])[0]
        parts = (cand.content.parts or []) if (cand and cand.content) else []
        text = "".join(getattr(p, "text", "") or "" for p in parts if not getattr(p, "thought", False)).strip()
        if text:
            return {"answer": text, "evidence": _flat_ev(evidence), "anh_id": anh_id, "ai": True}
    except Exception:
        pass
    return {"answer": "Câu hỏi cần tra cứu phức tạp. Hãy thử hỏi cụ thể từng phần (ví dụ hỏi riêng số lượng, riêng kích thước).",
            "evidence": _flat_ev(evidence), "anh_id": anh_id, "ai": True}
