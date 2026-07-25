# 🗺️ BỨC TRANH TỔNG QUÁT — demo 2 (đọc & tính khối lượng bản vẽ qua MCP)

> Cập nhật 2026-07-09. Một trang để nắm TOÀN CẢNH: hệ thống là gì, tổ chức ra sao, chạy/kiểm thế nào, tiến độ tới đâu,
> đi hướng nào. (Theo "Cold-Start Test" của Harness Engineering: một phiên mới tinh phải trả lời được 5 câu này chỉ bằng đọc repo.)

## ① HỆ THỐNG LÀ GÌ?
Web app **đọc + tính toán bản vẽ AutoCAD (.dwg/.dxf) qua MCP**, trả lời câu hỏi kỹ sư + **bóc tách KHỐI LƯỢNG** (m²/m³/kg/bộ),
**không bịa số**. Kiến trúc **TOOL-USE** (KHÔNG training AI): code Python tất định đọc/tính số THẬT kèm handle truy nguồn;
Gemini chỉ hiểu câu hỏi + gọi tool + diễn đạt. **Phạm vi ĐÃ CHỐT (2026-07-09):** đọc dữ liệu trong file + tính công thức ra
**khối lượng**. Dự toán CHI PHÍ (thành tiền) = **HOÃN** chờ đối tác chốt. Demo 2 là **sản phẩm chính** (demo 1 đã dừng).

## ② TỔ CHỨC RA SAO? (kiến trúc 4 tầng MCP)
```
Trình duyệt ──HTTP──► app.py (Flask host, state global: BRIDGE/SUMMARY/CHAT_HISTORY)
                         │
                         ▼
                   mcp_bridge.py (1 phiên MCP BỀN trên asyncio nền; vòng lặp Gemini function-calling
                         │         14 lượt + SYSTEM_PROMPT 21 luật chống bịa)
                         │ stdio JSON-RPC
                         ▼
                   mcp_server.py (FastMCP 'doc-autocad', 20 @mcp.tool wrapper mỏng, giữ 1 DRAWING)
                         │
                         ▼
                   tools_core.py (lớp Drawing: ezdxf trong RAM + _FORMULAS takeoff + render/highlight)
```
File chính: xem `harness/AGENTS.md`. Công nghệ + LƯU TRỮ: xem `harness/tech-stack.md`. **Không có database** — state in-RAM + file `_uploads/`,`_renders/` (ephemeral).

## ③ CHẠY / KIỂM THẾ NÀO?
- Local (Windows): `python app.py` → http://localhost:5050
- Test tất định (không tốn API): `python tests/test_takeoff_chong_bia.py` (**76/76**) + `python tests/test_qa_data.py` (đọc **129/129**)
- Cổng chất lượng: `bash harness/scripts/check.sh`
- Deploy: commit → push `main` → Render tự build → verify `GET /version` (khớp commit + `sect_cm_max:130`)
- Live: https://doc-autocad-mcp-demo.onrender.com

## ④ XÁC MINH THẾ NÀO? (chống bịa = KPI cốt lõi)
- Mỗi số kèm **handle** truy nguồn; thiếu → **hỏi** (không bịa); suy đoán/gán → **gắn cờ "chưa chắc"**.
- Test tất định khoá: existence (mã giả → không tìm thấy), hardening (inf/nan/bool/tràn số → chặn), đơn vị cm/mm, inox, tổng phụ.
- Nhận-diện-quy-ước test **≥3 file khác domain** (9T / CT-A KT / CT-A KC / hạ tầng) — chống overfit.
- **KPI đúng: "tỷ lệ BỊA ≈ 0%"** (KHÔNG phải "trả lời 100%"). Xem `KE_HOACH_TONG_QUAT_HOA.md`.

## ⑤ TIẾN ĐỘ TỚI ĐÂU? (giai đoạn + đầu mục)
| Giai đoạn | Trạng thái |
|---|---|
| **GĐ1 — ĐỌC** (SL/thép/kích thước/tiết diện/layer/block/sheet + khoanh đỏ ảnh) | ✅ XONG |
| **GĐ2 — TÍNH/takeoff** (12 công thức + cm/mm + tổng hợp + Excel + tầng) | ✅ XONG |
| **Feedback đối tác** (inox = SL×kg/bộ) + hardening đối kháng | ✅ XONG |
| **CỦNG CỐ** — tổng phụ (A), gợi ý m³ ghi sẵn (E) | ✅ XONG |
| CỦNG CỐ còn treo — trừ lỗ cửa (B), diện tích ghi sẵn (C), kg/bộ 1-click (D), ước cao cột (F), test đa-domain (G) | ⏳ planned |
| ROBUSTNESS — model fallback (H), chặn file lớn sớm (I), dọn TTL (J), tách session (K), keep-alive (L) | ⏳ partial |
| **DỰ TOÁN CHI PHÍ** (thành tiền) | ⏸️ HOÃN — chờ đối tác chốt yêu cầu |
| **AI TỰ HỌC** (hỏi-để-học từ đối tác, an toàn) | 🔬 mới NGHIÊN CỨU |

Chi tiết từng đầu mục + bằng chứng: `harness/feature_list.json`. Hướng đi: `ROADMAP_DEMO2.md`.

## 📚 Bản đồ tài liệu
| File | Nội dung |
|---|---|
| `GHI_CHU_HOAN_THIEN.md` | Nhật ký bàn giao chi tiết (đọc TRƯỚC khi vào phiên) |
| `ROADMAP_DEMO2.md` | Hướng đi + ưu tiên (củng cố khối lượng; dự toán HOÃN) |
| `KE_HOACH_TONG_QUAT_HOA.md` | Phương pháp: độ PHỦ vs độ AN TOÀN, KPI 0% bịa |
| `NGHIEN_CUU_AI_TU_HOC.md` | Nghiên cứu "AI tự học" an toàn (chưa code) |
| `harness/` | Kỷ luật chất lượng: feature_list, rubric, checklist, handoff, check.sh |
