# 🧰 CÔNG NGHỆ SỬ DỤNG & LƯU TRỮ — demo 2

> Cập nhật 2026-07-09. Liệt kê mọi công nghệ + cách LƯU TRỮ dữ liệu (câu hỏi "database hay gì đó").

## 1. Ngăn xếp công nghệ (tech stack)
| Lớp | Công nghệ | Phiên bản | Vai trò |
|---|---|---|---|
| Ngôn ngữ | Python | 3.10 | Toàn bộ backend (Dockerfile python:3.10-slim) |
| Web host | **Flask** | 3.1.3 | Máy chủ web + "custom MCP host"; UI là HTML/JS nhúng trong biến `PAGE` (không dùng template engine) |
| WSGI | **gunicorn** | 23.0.0 | Chạy production: 1 worker · 4 threads · timeout 600s (1 worker vì giữ 1 phiên MCP + 1 bản vẽ/lượt) |
| Giao thức AI | **MCP** (FastMCP) | 1.27.0 | `mcp_server.py` = MCP server stdio; `mcp_bridge.py` = MCP client (ClientSession/stdio_client) |
| LLM | **google-genai** (Gemini) | 2.17.0 | Model mặc định **gemini-3.6-flash** (chốt 2026-08-07; đổi qua env `GEMINI_MODEL`), chuỗi dự phòng CÙNG ĐỜI `gemini-3.5-flash,gemini-3.5-flash-lite`; max_output_tokens=8192, auto-function-calling DISABLE, retry 429/5xx (3 lần), timeout 60s + fail-forward khi TIMEOUT. ⛔ `temperature=0` vẫn được truyền nhưng **Gemini 3 BỎ QUA** (đo thật: 2.5-flash 1 đáp án/5 lần, 3.6-flash 5/5) ⇒ KHÔNG còn là hàng rào chống bịa |
| Đọc CAD | **ezdxf** | 1.4.4 | Đọc .dxf + `addons.drawing` để render ảnh |
| Convert DWG | **ODA File Converter** | Qt6 (Linux .deb / .exe Windows) | .dwg→.dxf trên server (Linux qua `xvfb-run`); **KHÔNG cần AutoCAD** → deploy cloud được |
| Vẽ ảnh | **matplotlib** | 3.10.9 | Backend **Agg** (headless, `MPLBACKEND=Agg`) → PNG khoanh đỏ cấu kiện |
| Ảnh | pillow | 12.2.0 | Phụ trợ ảnh |
| Excel | **openpyxl** | 3.1.5 | Xuất bảng tổng hợp .xlsx |
| Đồng bộ | asyncio + threading | (chuẩn) | 1 vòng lặp asyncio ở luồng nền daemon giữ **1 phiên MCP BỀN** (không teardown mỗi request) |
| Đóng gói | **Docker** | — | xvfb/xauth + libGL/EGL/Qt6 + fonts-dejavu + ODAFileConverter.deb (từ `vendor/`) |
| Hạ tầng | **Render** (Blueprint) | plan free | `render.yaml` runtime docker; ngủ sau 15p, RAM 512MB |
| Giải mã chữ | vntext.py (tự viết) | — | Font cũ TCVN3 + mã AutoCAD/MTEXT → Unicode |

## 2. LƯU TRỮ DỮ LIỆU — **KHÔNG có database**
Hệ **KHÔNG dùng** SQLite/Postgres/MySQL/ORM/vector-DB nào. Lưu trữ hoàn toàn **trong RAM + file trên đĩa**:

### (a) Trạng thái trong RAM (mất khi restart)
| Nơi | Biến | Nội dung |
|---|---|---|
| `app.py` | `BRIDGE` | Phiên MCP bền (lười khởi tạo) |
| `app.py` | `SUMMARY` | Chuỗi tóm tắt bản vẽ đang nạp |
| `app.py` | `CHAT_HISTORY` | List `[{role,text}]`, giữ **6 lượt** (`MAX_HISTORY_TURNS`), clear khi nạp file mới |
| `mcp_server.py` | `DRAWING` | 1 bản vẽ đang mở (ghi đè khi nạp file mới) |

### (b) File trên đĩa (ephemeral trên Render free)
| Thư mục | Nội dung |
|---|---|
| `_uploads/` | File .dxf/.dwg đối tác upload + bản .dxf convert ra |
| `_renders/` | Ảnh PNG khoanh đỏ (`hl_<uuid>.png`), Excel (`th_<uuid>.xlsx`), `_serverlog.txt` |

Cả hai thư mục nằm trong `.gitignore`.

### (c) Hệ quả & hạn chế đã biết (→ roadmap)
- **KHÔNG persistence qua restart**: Render free đĩa ephemeral + ngủ sau 15 phút → mất hết state. Mỗi lần dùng là 1 phiên độc lập.
- **Đồng thời (concurrency):** chỉ 1 `DRAWING` chung + gunicorn 1 worker → 2 người dùng cùng lúc **đạp bản vẽ của nhau** (ROADMAP mục K — chưa tách session).
- **Không dọn file theo TTL** → đĩa free có thể đầy (ROADMAP mục J).
- **Nếu sau này cần lưu bền** (lịch sử dự toán, quy ước đã học, đơn giá...): mới cần cân nhắc thêm 1 lớp lưu trữ (file JSON có version, hoặc SQLite nhẹ). **Hiện chưa cần** vì phạm vi = xử lý-1-file-1-phiên.

## 3. Bảo mật / cấu hình
- API key qua env `GEMINI_API_KEY` (KHÔNG hardcode; grep 'AIza' trong source = rỗng). Trên Render đặt env tay (`sync:false`).
- `MAX_UPLOAD_MB=150`, `READFILE_MAX_MB=45` (chặn file quá lớn cho RAM free — file 9T 114MB cần nâng plan).
- Repo **private** (`github.com/KimDat2705/demo-doc-autocad-mcp`) vì đóng kèm ODAFileConverter.deb (license ODA).
