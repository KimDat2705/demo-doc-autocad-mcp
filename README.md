# Demo 2 — Đọc & Trực quan hoá bản vẽ AutoCAD qua MCP

Demo thứ 2 (độc lập demo 1), theo hướng **MCP (Model Context Protocol)** sếp đề xuất — nhưng
làm theo cách **deploy được lên cloud** (không cần AutoCAD live).

## Khác gì demo 1?
| | Demo 1 (`demo_doc_autocad/`) | **Demo 2 (folder này)** |
|---|---|---|
| Kiến trúc | 13 hàm Python gắn cứng trong app Gemini | **MCP server CHUẨN, độc lập** (`mcp_server.py`) — cắm được Claude Desktop / Gemini CLI / Cursor |
| Trải nghiệm | Chỉ trả CHỮ + handle | **Thấy bản vẽ + KHOANH ĐỎ cấu kiện** (render ảnh) |
| Deploy | Cloud (Render) ✓ | Cloud (Render) ✓ — vẫn không cần AutoCAD |
| Chống bịa | Số do code + handle | Giữ NGUYÊN (số do code/tool + handle + phân biệt kỹ thuật/thực tế) |

## Kiến trúc
```
Trình duyệt ──HTTP──> app.py (Flask, custom MCP host)
                         │  mcp_bridge.py: 1 phiên MCP BỀN (luồng nền + asyncio),
                         │  Gemini (google-genai, ĐỒNG BỘ) gọi tool qua bridge
                         ▼
                    mcp_server.py  (FastMCP, stdio)  ← MCP server CHUẨN
                         │  tools_core.py: 13 tool đọc (ezdxf) + render/highlight
                         ▼
                    ODA File Converter (.dwg→.dxf, mọi phiên bản)
```
Vì sao tự bridge thay vì auto-MCP của SDK: `google-genai 2.10.0` deepcopy config chứa
`ClientSession` → lỗi. Bridge thủ công né lỗi + giữ vòng lặp chống bịa.

## Công cụ MCP (`mcp_server.py`)
`nap_ban_ve`, `tim_kiem`, `dem_so_luong`, `tra_cuu_so_luong`, `liet_ke_so_luong`,
`tong_so_luong`, `thong_ke_thep`, `thong_ke_thep_hinh`, `liet_ke_chu_theo_layer`,
`liet_ke_sheet`, `liet_ke_layer`, `liet_ke_block`, `thong_ke_doi_tuong`,
`thong_tin_kich_thuoc`, **`danh_dau_cau_kien`** (⭐ khoanh đỏ trên ảnh).

## Chạy local (Windows)
```
# 1) Đặt khoá Gemini: tạo file .env trong folder này (hoặc dùng .env của demo 1):
#      GEMINI_API_KEY=...
# 2) (Chỉ cần nếu test .dwg) đặt ODA_EXE trỏ ODAFileConverter.exe; hoặc test thẳng .dxf.
pip install -r requirements.txt
python app.py                # -> http://localhost:5050
```

## Cắm MCP server vào client khác (chứng minh "chuẩn MCP")
`mcp_server.py` là MCP server stdio chuẩn — cấu hình vào Gemini CLI / Claude Desktop:
```json
{ "mcpServers": { "doc-autocad": { "command": "python", "args": ["mcp_server.py"] } } }
```

## Deploy Render
Xem `Dockerfile` + `render.yaml`. Cần: (1) `vendor/ODAFileConverter.deb` (xem `vendor/README.txt`),
(2) đặt env `GEMINI_API_KEY` trên Render. Repo nên PRIVATE (license ODA).

## Câu hỏi demo gợi ý
"Có bao nhiêu bộ cửa D1?" · "Đánh dấu cửa D1 trên bản vẽ" · "Tổng số bộ cửa?" ·
"Khối lượng thép?" · "Liệt kê các sheet" · "Có bao nhiêu layer?"
