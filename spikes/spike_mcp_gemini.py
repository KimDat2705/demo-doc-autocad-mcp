# -*- coding: utf-8 -*-
"""
SPIKE 1 — Gemini (google-genai 2.10.0) goi MCP server qua stdio (duong A, local).
Kiem chung: SDK truyen ClientSession vao tools=[session] + tu dong goi tool (AFC).
Chay: python spike_mcp_gemini.py
"""
import os, sys, asyncio

# Nap GEMINI_API_KEY tu .env cua demo 1 (KHONG hardcode key)
D1 = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "demo_doc_autocad"))
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


async def main():
    if not KEY:
        print("THIEU GEMINI_API_KEY (.env cua demo 1)."); return
    print("Model:", MODEL)
    server = StdioServerParameters(command=sys.executable,
                                   args=[os.path.join(os.path.dirname(__file__), "mcp_demo_server.py")])
    client = genai.Client(api_key=KEY)
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            print("MCP tools server cung cap:", [t.name for t in listed.tools])

            q = "Ban ve co bao nhieu bo cua D1 va bao nhieu bo cua S1?"
            print("\nHOI:", q)
            resp = await client.aio.models.generate_content(
                model=MODEL,
                contents=q,
                config=types.GenerateContentConfig(tools=[session], temperature=0),
            )
            print("\n== TRA LOI ==\n", resp.text)
            afc = getattr(resp, "automatic_function_calling_history", None)
            n = len(afc) if afc else 0
            print("\nAFC history (so buoc tu dong goi tool):", n)
            # liet ke ten tool da goi tu lich su (neu co)
            called = []
            for c in (afc or []):
                for p in getattr(c, "parts", []) or []:
                    fc = getattr(p, "function_call", None)
                    if fc:
                        called.append(fc.name)
            print("Tool da goi:", called or "(khong thay trong history)")
            print("\nKET LUAN: ", "DAT — Gemini goi MCP tool qua stdio OK" if (called or n) else
                  "Tra loi khong qua tool — kiem lai")


if __name__ == "__main__":
    asyncio.run(main())
