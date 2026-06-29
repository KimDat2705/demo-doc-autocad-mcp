# -*- coding: utf-8 -*-
"""
MCP server TOI THIEU (spike) — chung minh Gemini goi duoc tool qua chuan MCP (stdio).
Chay doc lap: python mcp_demo_server.py  (giao tiep qua stdin/stdout theo JSON-RPC).
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-doc-autocad")


@mcp.tool()
def dem_so_luong_cua(ma_cua: str) -> dict:
    """Tra so luong bo cua theo ma (du lieu gia lap cho spike).

    Args:
        ma_cua: ma cua, vi du 'D1', 'S1'.
    """
    data = {"D1": 24, "S1": 16, "SW": 16, "DW": 8}
    ma = (ma_cua or "").upper().strip()
    return {"ma_cua": ma, "so_luong_bo": data.get(ma, 0),
            "ghi_chu": "So lay tu nhan 'so luong: N bo' tren ban ve (du lieu gia lap spike)."}


if __name__ == "__main__":
    mcp.run()  # transport stdio mac dinh
