# -*- coding: utf-8 -*-
"""
SPIKE 2 — KIEN TRUC HOST THAT (se dung cho Flask demo 2):
  - 1 luong nen giu 1 vong asyncio BEN, so huu 1 phien MCP song suot doi app
    -> KHONG teardown moi request (het rac SSL/event-loop tren Windows).
  - Flask (dong bo) goi bridge.call(ten, args) -> chay tren vong nen, tra ket qua.
  - Gemini dung client DONG BO + FunctionDeclaration sinh tu MCP tool schema
    -> KHONG nhet ClientSession vao config (tranh bug deepcopy 2.10.0).
  - Vong lap tu dieu khien (giong ai_gemini.py) -> giu duoc moi chot chong bia.
Ket qua ghi ra spike_bridge_out.txt (UTF-8) de tranh loi console cp1252.
"""
import os, sys, asyncio, threading

HERE = os.path.dirname(os.path.abspath(__file__))
D1 = os.path.normpath(os.path.join(HERE, "..", "..", "demo_doc_autocad"))
envp = os.path.join(D1, ".env")
if os.path.isfile(envp):
    for line in open(envp, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-pro-preview")

from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LOG = open(os.path.join(HERE, "spike_bridge_out.txt"), "w", encoding="utf-8")
def log(*a): print(*a, file=LOG, flush=True)


class MCPBridge:
    """Giu 1 phien MCP song tren 1 vong asyncio chay trong luong nen rieng."""
    def __init__(self, server_params):
        self.sp = server_params
        self.loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._stop = None
        self.session = None
        self.tools = []
        threading.Thread(target=self._run, daemon=True).start()
        self._ready.wait(30)

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._serve())

    async def _serve(self):
        self._stop = asyncio.Event()
        async with stdio_client(self.sp) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                self.session = session
                self.tools = (await session.list_tools()).tools
                self._ready.set()
                await self._stop.wait()   # giu song den khi tat

    def call(self, name, args):
        fut = asyncio.run_coroutine_threadsafe(self.session.call_tool(name, args), self.loop)
        res = fut.result(timeout=60)
        # gop noi dung text tra ve
        out = []
        for c in res.content:
            out.append(getattr(c, "text", "") or "")
        return "\n".join(out)

    def close(self):
        self.loop.call_soon_threadsafe(self._stop.set)


_JTYPE = {"string": types.Type.STRING, "integer": types.Type.INTEGER,
          "number": types.Type.NUMBER, "boolean": types.Type.BOOLEAN,
          "object": types.Type.OBJECT, "array": types.Type.ARRAY}


def schema_from_json(js):
    """JSON Schema (MCP inputSchema) -> google.genai Schema (toi thieu, du cho demo)."""
    if not js:
        return types.Schema(type=types.Type.OBJECT, properties={})
    props = {}
    for k, v in (js.get("properties") or {}).items():
        props[k] = types.Schema(type=_JTYPE.get(v.get("type", "string"), types.Type.STRING),
                                description=v.get("description", ""))
    return types.Schema(type=types.Type.OBJECT, properties=props,
                        required=js.get("required") or [])


def gemini_tools(mcp_tools):
    decls = [types.FunctionDeclaration(name=t.name, description=(t.description or "")[:1000],
                                       parameters=schema_from_json(t.inputSchema)) for t in mcp_tools]
    return [types.Tool(function_declarations=decls)]


def main():
    if not KEY:
        log("THIEU KEY"); return
    log("Model:", MODEL)
    sp = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "mcp_demo_server.py")])
    bridge = MCPBridge(sp)
    log("MCP tools:", [t.name for t in bridge.tools])

    client = genai.Client(api_key=KEY)   # client DONG BO
    tools = gemini_tools(bridge.tools)
    cfg = types.GenerateContentConfig(
        system_instruction=("Ban la tro ly doc ban ve. Khi can so lieu, GOI cong cu. "
                            "Chi tra loi dua tren ket qua cong cu, khong bia."),
        tools=tools, temperature=0, max_output_tokens=8192,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    q = "Ban ve co bao nhieu bo cua D1 va bao nhieu bo cua SW?"
    log("\nHOI:", q)
    contents = [types.Content(role="user", parts=[types.Part(text=q)])]

    called = []
    for _ in range(6):
        resp = client.models.generate_content(model=MODEL, contents=contents, config=cfg)
        cand = (resp.candidates or [None])[0]
        fr = getattr(cand, "finish_reason", None)
        parts = (cand.content.parts or []) if (cand and cand.content) else []
        log("  [vong] finish=%s, so part=%d" % (getattr(fr, "name", fr), len(parts)))
        fcalls = [p.function_call for p in parts if getattr(p, "function_call", None)]
        if fcalls:
            contents.append(cand.content)
            rparts = []
            for fc in fcalls:
                args = dict(fc.args or {})
                result = bridge.call(fc.name, args)        # <-- goi QUA MCP that
                called.append((fc.name, args, result))
                log("  -> goi MCP tool %s%s => %s" % (fc.name, args, result))
                rparts.append(types.Part(function_response=types.FunctionResponse(
                    name=fc.name, response={"ket_qua": result})))
            contents.append(types.Content(role="user", parts=rparts))
            continue
        text = "".join(getattr(p, "text", "") or "" for p in parts if not getattr(p, "thought", False))
        log("\n== TRA LOI CUOI ==\n", text.strip())
        break

    log("\nSo lan goi MCP tool:", len(called))
    log("KET LUAN:", "DAT — bridge dong bo<->MCP<->Gemini chay OK, khong loi deepcopy/teardown"
        if called else "KHONG goi tool — kiem lai")
    bridge.close()
    LOG.close()
    print("Xong. Xem spike_bridge_out.txt")


if __name__ == "__main__":
    main()
