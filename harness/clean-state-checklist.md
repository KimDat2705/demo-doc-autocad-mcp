# Clean State Checklist — demo 2

Chạy TRƯỚC mỗi commit và cuối mỗi phiên (một phiên = một "transaction": commit sạch, không để dở/test đỏ/rác).

## Build / Import
- [ ] `python -c "import tools_core"` sạch (không lỗi import)
- [ ] `grep -c "@mcp.tool" mcp_server.py` = **28** (24 + `hoc_quy_uoc` + `thu_hoi_quy_uoc` [P3, LOẠI khỏi gemini_tools = R8] + `cao_do_min_max` [id135-recall] + `doc_bang_nhung` [U3, đọc bảng OLE nhúng] + `kiem_tra_handle` [I1, đối chiếu handle — LOẠI khỏi gemini_tools, host-only])
- [ ] ⚠ KHÔNG dùng `pytest` (test đổi `sys.stdout` lúc import → pytest crash `I/O operation on closed file`); chạy SCRIPT trực tiếp + `check.sh`. KHÔNG có `specs/specs.json` (dùng `feature_list.json`).
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
- [ ] `python tests/test_takeoff_chong_bia.py` = **258/258 PASS** (offline; nhóm A-Y + [Z0] R1 + [Z] P3 + P4 + **[id84] 12 ca** (đài cọc đ/d 142→59 + dầm double-count 40→20 + door/beam D1)) — *cần env READFILE_MAX_MB=300; check.sh tự set*
- [ ] `python tests/test_qa_data.py` = **129/129** (đọc — cần ../input_files/_dxf + ../demo_doc_autocad)
- [ ] `python tests/test_model_fallback.py` = **22/22 PASS** (robustness H + **[H.10] empty-response nudge**; offline mock)
- [ ] `python tests/test_size_guard.py` = **9/9** · `test_file_ttl.py` = **12/12** · `test_health.py` = **11/11** (robustness I/J/L, offline)
- [ ] `python tests/test_session.py` = **25/25 PASS** (robustness K + **[K.7] R11 IDOR** cross-session 404 + **[K.8] F-A** race evict né phiên bận)
- [ ] `python tests/test_hoc_log.py` = **20/20** · `test_hoc_quy_uoc.py` = **2/2** (P2 log WORM + P3 INV-10 LLM-exclusion/INV-12 grep-guard)
- [ ] **GĐ1-2 kiểm thử (offline):** `test_visual_highlight` 15 · `test_excel_content` 17 (mở lại .xlsx) · `test_misc_tools` 84 · `test_vntext` 28 · `test_fuzz_input` 36 · `test_dwgconv` 10 · `test_mcp_stdio` 14 (spawn mcp_server thật) · `test_app_routes` 8
- [ ] `python tests/test_grounding_guard.py` = **32/32** (id135 grounding-guard chống bịa số đo-lường) · `python tests/test_cao_do_min_max.py` = **12/12** (id135 recall: đọc cao độ min/max + handle)
- [ ] `bash harness/scripts/check.sh` = **HARNESS GATE: PASS** (**25 bước**: import+28tool · no-key · takeoff 258 · fallback 22 · size 9 · ttl 12 · session 25 · health 11 · hoc-log 20 · hoc-quy-uoc 2 · visual 15 · excel 17 · misc 84 · vntext 28 · fuzz 36 · dwgconv 10 · mcp-stdio 14 · app-routes 8 · grounding-guard 46 [+I1b m2/m3] · cao-do 31 · khao-sat-corpus 61 · ole-canh-bao 51 · **oleexcel 18** [U3] · **handle-guard 44** [I1] · **i3-bounds 24** [I3-B])
- [ ] **E2E-AI (TỐN API, NGOÀI cổng):** `tests/run_battery.py` 198 câu + `tests/kichban_gd2.py` 12 lượt (đối chiếu engine-truth) — KPI ~0% bịa (đã đo ~1.1% bịa cứng 2026-07-13, đều edge-case)

## Tổng quát (chống overfit)
- [ ] Quy ước mới nhận diện → test trên **≥3 file khác domain** (9T cm / CT-A mm / hạ tầng)
- [ ] Mỗi quy ước/fix mới → thêm 1 ca vào `tests/test_takeoff_chong_bia.py` (đặc biệt ca ĐỐI KHÁNG "gặp lạ → không bịa")

## Repo / Bảo mật
- [ ] `git status` không có file lạ; `_uploads/` `_renders/` `.env` KHÔNG bị stage (đã .gitignore)
- [ ] `harness/feature_list.json` + `quality-document.md` + `session-handoff.md` cập nhật đúng hiện trạng

## Cloud
- [ ] Push `main` → Render rebuild OK
- [ ] `GET /version` live = commit VỪA push + `sect_cm_max:130` + `has_section_index:true` + `models:[2.5-flash,2.0-flash,1.5-flash]` (bản đã lên + chuỗi fallback H)
- [ ] `GET /health` live = `{ok:true, uptime_s, sessions, metrics}` (L — healthCheckPath Render + monitor ngoài; self-ping tự chạy khi có RENDER_EXTERNAL_URL)
