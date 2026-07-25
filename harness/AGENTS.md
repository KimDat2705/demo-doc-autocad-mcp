# AGENTS.md — demo 2 (đọc & tính khối lượng bản vẽ AutoCAD qua MCP)

## Khởi động (đọc theo thứ tự)
1. File này — ranh giới & quy ước.
2. `harness/project-overview.md` — bức tranh tổng quát (Cold-Start 5 câu hỏi).
3. `GHI_CHU_HOAN_THIEN.md` — nhật ký bàn giao chi tiết (trạng thái + việc còn lại).
4. `harness/feature_list.json` — trạng thái từng tính năng + bằng chứng.
5. `harness/session-handoff.md` — phiên gần nhất làm gì / còn gì.
6. Chạy baseline (dưới) → tóm tắt.

## ⭐ THỨ TỰ ƯU TIÊN CÔNG VIỆC (user chốt 2026-07-25 — ÁP DỤNG MỌI PHIÊN)
Ưu tiên hoàn thành theo đúng thứ tự: **A → C → D → B**. Làm cạn nhóm trên trước khi sang nhóm dưới (trừ khi user chỉ định khác trong phiên).
1. **A — CHỨC NĂNG CHÍNH (trọng tâm):** AI ĐỌC CHÍNH XÁC dữ liệu bản vẽ AutoCAD + TRẢ LỜI ĐÚNG, **KHÔNG ảo giác**. Gồm: bộ đọc dữ liệu (số lượng/thép/cao độ/kích thước/diện tích/bảng OLE+bảng-vẽ-nét/layer-block-sheet), recall/tìm kiếm, CHỐNG BỊA (grounding-guard, anti-manipulation, bounds-check, provenance, validate-handle, thất-bại-phải-lộ), và điều kiện để đọc được (DWG→DXF convert, giải mã TCVN3).
2. **C — RAM / DUNG LƯỢNG UPLOAD FILE:** chịu tải file lớn (nâng RAM Render, hạ render cap, size-guard, file-TTL). Ràng buộc là RAM cloud, không phải logic.
3. **D — KHÁC:** vận hành/robustness, AI tự học (P-series), kiểm thử/corpus, UI, bảo mật/repo.
4. **B — DỰ TOÁN / TÍNH KHỐI LƯỢNG / XUẤT EXCEL (LÀM CUỐI):** takeoff `tinh_dai_luong`, tổng hợp, xuất Excel/BOQ. User đang **cân nhắc THU HẸP** nhóm này — KHÔNG mở rộng thêm (I4b/I2-v2/Catalog) trừ khi user yêu cầu; **dự toán CHI PHÍ (đơn giá/định mức/thành tiền) đã NGOÀI phạm vi** (chốt 2026-07-09). Các guard chống-bịa nằm trong takeoff thì thuộc nhóm A và luôn giữ.
> Bản rà soát phân nhóm đầy đủ 64 đầu mục: artifact "Rà soát đầu mục" + workflow `wf_d5d37fa6-683`. Xem thêm memory `[[project-uu-tien-nhom-cong-viec]]` + `[[project-roadmap-con-lai-2026-07-25]]`.

## Lệnh kiểm tra (từ thư mục `demo_mcp_autocad/`)
- **Baseline nhanh (đầu phiên):** `python tests/test_takeoff_chong_bia.py` (**76/76**, offline, không tốn API)
- **Cổng đầy đủ (cuối phiên):** `bash harness/scripts/check.sh` (import + đếm tool + no-key + 2 bộ test)
- **QA đọc dữ liệu:** `python tests/test_qa_data.py` (**129/129**, cần `../input_files/_dxf` + `../demo_doc_autocad`)
- (KHÔNG có `backend/` — code ở ngay `demo_mcp_autocad/`. KHÔNG có `specs/` — dùng `harness/feature_list.json`.)

## Bối cảnh — kiến trúc TOOL-USE (KHÔNG training/fine-tune)
Code Python tất định ĐỌC/TÍNH số thật từ file qua "công cụ" MCP; Gemini chỉ HIỂU câu hỏi + GỌI công cụ + DIỄN ĐẠT.
Số do CODE tính → **không bịa**. File mẫu để PHÁT HIỆN quy ước → viết CODE (không phải dữ liệu training).
**Demo 2 là sản phẩm chính (demo 1 đã dừng — 2026-07-09).** Phạm vi: đọc + tính **KHỐI LƯỢNG**; dự toán chi phí = HOÃN.

## File chính (kiến trúc 4 tầng MCP)
| File | Vai trò |
|---|---|
| `app.py` | Flask host (MCP host tự viết) + routes (/upload,/ask,/image,/file,/config,/version) + state global (BRIDGE/SUMMARY/CHAT_HISTORY) + UI (biến PAGE) |
| `mcp_bridge.py` | Cầu Gemini↔MCP: 1 phiên MCP bền (asyncio nền) + vòng lặp function-calling (MAX_TURNS=14) + SYSTEM_PROMPT (7 mảnh bất-biến chống bịa + 15 quy-ước-VN + header, tách mảnh có version/hash — I9) |
| `mcp_server.py` | FastMCP server (stdio), **20 @mcp.tool()** wrapper mỏng gọi `tools_core` |
| `tools_core.py` | Lớp `Drawing`: ezdxf trong RAM + trích xuất + `_FORMULAS` engine takeoff + render/highlight |
| `dwgconv.py` / `vntext.py` | Convert .dwg→.dxf (ODA) / giải mã TCVN3 |
| `tests/test_takeoff_chong_bia.py` | Cổng chống bịa takeoff (76/76, offline) |

## Ranh giới / Quy ước (chống bịa = BẤT DI)
- **Đọc verbatim** (số có sẵn) > **ghép vị trí / suy đoán** (cờ "chưa chắc") > **phải tính/takeoff** (cờ "số do hệ thống TÍNH"). KHÔNG trộn 3 tầng thành 1 con số khẳng định.
- Mỗi số kèm **handle** truy nguồn; mỗi tool trả `ghi_chu` khai báo bản chất con số.
- Thiếu dữ liệu → **HỎI** (`can_bo_sung`), không bịa. Mã không tồn tại → `khong_tim_thay` (kể cả có `inputs_bo_sung`).
- Input đối tác cấp: chỉ nhận SỐ DƯƠNG hữu hạn (chặn bool/inf/nan/tràn số/≤0 — `math.isfinite`).
- KHÔNG hardcode API key (env `GEMINI_API_KEY`).

## Definition of Done (1 tính năng "xong" khi)
1. `python -c "import tools_core"` sạch; `bash harness/scripts/check.sh` = PASS.
2. Trả lời ĐÚNG trên file thật + **kèm handle**; suy đoán/gán → gắn cờ.
3. Test trên **≥3 file khác domain** (chống overfit) — thêm ca vào `tests/test_takeoff_chong_bia.py`.
4. **Đối kháng:** ném input lạ/thiếu → phải "từ chối an toàn", KHÔNG ra số bịa (thêm ca như nhóm [K][L]).
5. Cập nhật `harness/feature_list.json` (status + evidence) + `session-handoff.md`.
6. `harness/clean-state-checklist.md` qua hết. Deploy → verify `/version` khớp commit.

## 4 nguyên tắc CHỐNG OVERFIT (bài học sự cố cửa D1 + cm/mm)
1. **Recall trước, faithfulness khi trình bày** — khớp khoan dung (fold font, đa quy ước), trình bày nguyên văn + handle.
2. **Test ≥3 file khác domain TRƯỚC khi tin** một cách nhận diện (9T cm / CT-A mm / hạ tầng).
3. **Phân tầng độ tin cậy, lộ ra** cho người đọc.
4. **Thất bại phải LỘ** — thử mọi biến thể rồi mới "không có"; ghép mơ hồ → "tạm khớp, cần đối chiếu".

## Session handoff
Đọc `harness/session-handoff.md` khi vào phiên; cập nhật cuối phiên (làm gì / còn gì / quyết định / file sửa / commit).
