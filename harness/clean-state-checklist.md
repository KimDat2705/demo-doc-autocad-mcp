# Clean State Checklist — demo 2

Chạy TRƯỚC mỗi commit và cuối mỗi phiên (một phiên = một "transaction": commit sạch, không để dở/test đỏ/rác).

## Build / Import
- [ ] `python -c "import tools_core"` sạch (không lỗi import)
- [ ] `grep -c "@mcp.tool" mcp_server.py` = **21** (số MCP tool hiện tại; +liet_ke_dien_tich_ghi_san task C)
- [ ] `requirements.txt` đủ (ezdxf, Flask, gunicorn, google-genai, mcp, matplotlib, pillow, openpyxl)

## Kiến trúc / Nguyên tắc
- [ ] **KHÔNG hardcode API key**: `grep -nE "AIza[0-9A-Za-z_-]{10,}" tools_core.py app.py mcp_bridge.py mcp_server.py` = rỗng
- [ ] Mỗi tool trả thêm `ghi_chu` khai báo bản chất con số (đếm chữ ≠ số cấu kiện; tạm tính ≠ chốt)
- [ ] Số "đọc verbatim" / "gán vị trí (chưa chắc)" / "suy đoán đơn vị (cảnh báo)" / "phải tính" — phân tầng rõ, không trộn
- [ ] MCP: `nap_ban_ve` chỉ host gọi (loại khỏi tool cho LLM); mọi tool khác `_need()` khi chưa nạp bản vẽ

## Runtime
- [ ] `python app.py` khởi động (http://localhost:5050); `/config` trả `use_ai`+model; `/version` trả commit+sect_cm_max
- [ ] Nạp được .dxf (≤ READFILE_MAX_MB) và .dwg (qua ODA); hết MAX_TURNS → ép trả lời (không bỏ cuộc)

## Chống bịa (CỐT LÕI)
- [ ] Mã KHÔNG tồn tại (kể cả toàn chữ "GHOSTINOX") + có `inputs_bo_sung` → `khong_tim_thay` (KHÔNG bịa số)
- [ ] Input phi số / âm / 0 / inf / nan / bool / tràn số → `so_lieu_khong_hop_le` (KHÔNG ra "Infinity kg")
- [ ] Đơn vị cm/mm suy đoán → gắn cờ `suy_doan_don_vi` + cảnh báo "lệch 100× nếu sai quy ước"
- [ ] Sàn mã trống → KHÔNG tự quét cả file vơ "diện tích Xm2" (báo thiếu)
- [ ] Mọi nội dung cụ thể kèm **handle** có thật trong file

## Dữ liệu / Hồi quy
- [ ] `python tests/test_takeoff_chong_bia.py` = **177/177 PASS** (offline, không tốn API; nhóm A-V, +N/O/P/Q = task B/C/D/F, +R/S/T/U + I.5/I.6 = task G đa-domain & vá tong_phu gộp thép/Số lượng + parity diện tích, +V = Residual G #1 đọc SL bảng thống kê theo cột TỔNG)
- [ ] `python tests/test_qa_data.py` = **129/129** (đọc — cần ../input_files/_dxf + ../demo_doc_autocad)
- [ ] `python tests/test_model_fallback.py` = **20/20 PASS** (robustness H — chuỗi model 429/503, offline mock, KHÔNG tốn API)
- [ ] `python tests/test_size_guard.py` = **9/9 PASS** (robustness I — chặn file lớn sớm trước convert/parse, offline)
- [ ] `python tests/test_file_ttl.py` = **12/12 PASS** (robustness J — dọn file _uploads/_renders cũ theo TTL, offline)
- [ ] `python tests/test_session.py` = **17/17 PASS** (robustness K — tách state theo phiên, Flask test_client + FakeBridge, offline)
- [ ] `python tests/test_health.py` = **11/11 PASS** (robustness L — /health + self-ping keep-alive + metrics, offline)
- [ ] `bash harness/scripts/check.sh` = **HARNESS GATE: PASS** (8 bước: import+tool · no-key · takeoff 177 · fallback 20 · size-guard 9 · file-ttl 12 · session 17 · health 11)

## Tổng quát (chống overfit)
- [ ] Quy ước mới nhận diện → test trên **≥3 file khác domain** (9T cm / Gia Lộc mm / hạ tầng)
- [ ] Mỗi quy ước/fix mới → thêm 1 ca vào `tests/test_takeoff_chong_bia.py` (đặc biệt ca ĐỐI KHÁNG "gặp lạ → không bịa")

## Repo / Bảo mật
- [ ] `git status` không có file lạ; `_uploads/` `_renders/` `.env` KHÔNG bị stage (đã .gitignore)
- [ ] `harness/feature_list.json` + `quality-document.md` + `session-handoff.md` cập nhật đúng hiện trạng

## Cloud
- [ ] Push `main` → Render rebuild OK
- [ ] `GET /version` live = commit VỪA push + `sect_cm_max:130` + `has_section_index:true` + `models:[2.5-flash,2.0-flash,1.5-flash]` (bản đã lên + chuỗi fallback H)
- [ ] `GET /health` live = `{ok:true, uptime_s, sessions, metrics}` (L — healthCheckPath Render + monitor ngoài; self-ping tự chạy khi có RENDER_EXTERNAL_URL)
