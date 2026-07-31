# Clean State Checklist — demo 2

Chạy TRƯỚC mỗi commit và cuối mỗi phiên (một phiên = một "transaction": commit sạch, không để dở/test đỏ/rác).

## Build / Import
- [ ] `python -c "import tools_core"` sạch (không lỗi import)
- [ ] `grep -c "@mcp.tool" mcp_server.py` = **34** (33 + `tim_chu_trong_ky_hieu` [2026-07-31, đọc chữ trong định nghĩa ký hiệu/khối ĐƯỢC CHÈN])
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
- [ ] `python tests/test_takeoff_chong_bia.py` = **272/272 PASS** (offline; nhóm A-Y + [Z0] R1 + [Z] P3 + P4 + [id84] 12 ca + [I3-U L1] 4 ca + **[I3-U L2] 10 ca** (quy đổi '3.6m'→mm code-only tag-only/degrade-safe + C1-lite standing invariant)) — *cần env READFILE_MAX_MB=300; check.sh tự set*
- [ ] `python tests/test_qa_data.py` = **129/129** (đọc — cần ../input_files/_dxf + ../demo_doc_autocad)
- [ ] `python tests/test_model_fallback.py` = **22/22 PASS** (robustness H + **[H.10] empty-response nudge**; offline mock)
- [ ] `python tests/test_size_guard.py` = **9/9** · `test_file_ttl.py` = **12/12** · `test_health.py` = **11/11** (robustness I/J/L, offline)
- [ ] `python tests/test_session.py` = **36/36 PASS** (robustness K + **[K.7] R11 IDOR** cross-session 404 + **[K.8] F-A** race evict né phiên bận + **[K.9] bounded lock** 3 route có trần chờ + body từ chối đủ 4 khoá chữ)
- [ ] **CHỊU TẢI (2026-07-30):** `test_admission` **63** [trần SỐ BẢN VẼ `MAX_BAN_VE`; A.13-A.17 = ca red-team-impl bắt] · `test_bridge_close` **28** [dọn tiến trình mồ côi + `call()` không treo sau close; B.6 qua đường truyền MCP THẬT] · `test_ty_le_do` **17** [DIMLFAC — bản vẽ tự khai hệ số tỉ lệ đo]
- [ ] `python tests/test_hoc_log.py` = **20/20** · `test_hoc_quy_uoc.py` = **2/2** (P2 log WORM + P3 INV-10 LLM-exclusion/INV-12 grep-guard)
- [ ] **GĐ1-2 kiểm thử (offline):** `test_visual_highlight` **19** [+U6C bi_cat] · `test_excel_content` **21** [+I2 Tien_luong] (mở lại .xlsx) · `test_misc_tools` **107** [+I5 bi_cat +recall A/B/C: _tok_bound/thong_tin_file/bang_con] · `test_vntext` 28 · `test_fuzz_input` 36 · `test_dwgconv` 10 · `test_mcp_stdio` 14 (spawn mcp_server thật) · `test_app_routes` **10** [+I9 prompt keys] · `test_bang_ve_net` **9** [I4a detector] · `test_prompt_taxonomy` **24** [I9 byte-lock sha256]
- [ ] `python tests/test_grounding_guard.py` = **47/47** (id135 grounding-guard + I1b m2/m3 + I4a exclude) · `python tests/test_cao_do_min_max.py` = **31/31** (id135 recall: đọc cao độ min/max + handle)
- [ ] **KHO KIẾN THỨC (L0-L6, 2026-07-27):** `test_dispatch_gate` **11** [L0 chặn tool host-only ở dispatch] · `test_kienthuc` **15** [L1+L2 validator digit-free + byte-lock KB_HASH + strip `_kb`] · `test_kb_graft` **18** [L4 gate bằng-chứng-dương; A6 khoá BỘ BA] · `test_kb_xacnhan` **44** [L5 confirm-only + 3 bản vá + 7 vá red-team] · `test_tra_ky_hieu` **13** [L3] · `test_garble_dia` **26** [L6 fold ỉ//g→Ø]
- [ ] **ĐỢT 2026-07-31 (5 suite mới/đổi):** `test_so_do_dim` **27** [nguồn số đo: hệ số ÂM · đường đo GÓC · code 42; N.6b hình-học-suy-biến + gõ đè -> KHÔNG cứu] · `test_neo_grounding` **34** [3 kênh bơm neo: mã hiệu / tên file / HANDLE + cụm-từ-chối không tắt guard] · `test_chu_in_kich_thuoc` **24** · `test_vung_chua_doc` **44** · `test_chu_trong_ky_hieu` **26** · `test_grounding_guard` 50→**56** [+`[F2]` hàng rào SỐ ĐẾM] · `test_kienthuc` 15→**30** [+K12 tra ngược nghĩa→ký hiệu, 6 ca khoá "đa nghĩa thì KHÔNG tra ngược"] · `test_ty_le_do` 17→**25**
- [ ] `bash harness/scripts/check.sh` = **HARNESS GATE: PASS** (**41 bước**: import+33tool · no-key · takeoff 272 · fallback 22 · size 9 · ttl 12 · **session 36** · **health 23** · hoc-log 22 · hoc-quy-uoc 2 · visual 19 [U6C] · excel 21 [I2] · misc 107 [I5+recall] · vntext 28 · fuzz 36 · dwgconv 10 · mcp-stdio 14 · **app-routes 12** [+I9 +/health mới] · **grounding-guard 50** [+I1b +I4a +M4 sạch số] · cao-do 31 · khao-sat-corpus 61 · ole-canh-bao 51 · **oleexcel 18** [U3] · **handle-guard 44** [I1] · **i3-bounds 24** [I3-B] · **bang-ve-net 9** [I4a] · **prompt-taxonomy 24** [I9 byte-lock] · **dispatch-gate 11** · **kienthuc 15** · **kb-graft 18** · **kb-xacnhan 44** · **tra-ky-hieu 13** · **garble-dia 26** · **admission 63** · **bridge-close 28** · **ty-le-do 17**)
- [ ] ⚠ **CỔNG XANH KHÔNG ĐỦ để tin bản vá đã chạy.** Bài học 2026-07-30: vá DIMLFAC đổi số thật trên 21,5% đường kích thước mà CẢ 6 suite đóng-băng-số (272/107/51/31/24/61) VẪN XANH — bộ kiểm cũ mù hoàn toàn với lớp lỗi đó. Với mọi bản vá đổi hành vi đọc: phải TỰ KIỂM NGƯỢC rằng nó thực sự chạy (so số trước/sau bằng script), rồi mới thêm suite khoá.
- [ ] ⚠⚠ **KHÔNG TIN "PASS" NẾU CỔNG CHẠY TRÊN CÂY ĐANG SỬA — VÀ PHẢI ĐỌC MÃ THOÁT THẬT.** Bài học 2026-07-31, ba lần trong một phiên: (a) cổng chạy nền trong lúc còn đang sửa file test → kết quả vô nghĩa, phải chạy lại trên cây đã ổn định; (b) một lần cổng **`exit 127`** (thư mục shell bị đặt lại) nên **KHÔNG HỀ CHẠY** — đọc mỗi dòng "PASS" của lần trước thì tưởng xong; (c) notification nền báo "exit code 0" là mã thoát của lệnh `echo` nối sau, KHÔNG phải của `check.sh`. ⇒ luôn ghi `EXIT_CODE_THAT=$?` NGAY sau `check.sh` vào chính file output, và `grep "HARNESS GATE"` trong FILE chứ đừng tin summary.
- [ ] ⚠ **ĐO TRƯỚC, CODE SAU — và coi chừng phép đo tautology.** Bài học 2026-07-31: lượt đo đầu của hàng rào số-đếm ra "0% lọt" chỉ vì tự loại số trùng neo lúc sinh dữ liệu (kết quả tất yếu của cách sinh, không đo gì). Và "tỉ lệ lọt" nói chung KHÔNG phải đại lượng ổn định — cùng một rổ neo, đổi bộ sinh số thì chạy 0,0%→13,6%. Phép đo dùng được để RA QUYẾT ĐỊNH là phép đo trên **câu trả lời THẬT chấm bằng NHÃN ĐỘC LẬP** (`ky_vong` của bộ 198 câu), không phải trên dữ liệu tự sinh.
- [ ] **E2E-AI (TỐN API, NGOÀI cổng):** `tests/run_battery.py` 198 câu + `tests/kichban_gd2.py` 12 lượt (đối chiếu engine-truth) — KPI ~0% bịa (đã đo ~1.1% bịa cứng 2026-07-13, đều edge-case)

## Tổng quát (chống overfit)
- [ ] Quy ước mới nhận diện → test trên **≥3 file khác domain** (9T cm / CT-A mm / hạ tầng)
- [ ] Mỗi quy ước/fix mới → thêm 1 ca vào `tests/test_takeoff_chong_bia.py` (đặc biệt ca ĐỐI KHÁNG "gặp lạ → không bịa")

## Repo / Bảo mật
- [ ] `git status` không có file lạ; `_uploads/` `_renders/` `.env` KHÔNG bị stage (đã .gitignore)
- [ ] `harness/feature_list.json` + `quality-document.md` + `session-handoff.md` cập nhật đúng hiện trạng

## Cloud
- [ ] Push `main` → Render rebuild OK
- [ ] `GET /version` live = commit VỪA push + `sect_cm_max:130` + `has_section_index:true` + `models:[2.5-flash,2.0-flash,1.5-flash]` + **`prompt_version:2026.07.27-kb-l3` + `prompt_hash:239e8b7ba707…`** [+_P_R18 kho kiến thức; hash cũ: e5e05d7d routing-l2, bea17c6e I9] + **`kb_version:kb-2026.07.26-dot-dau` + `kb_hash:e55ac112d1a3…`** [định danh KHO KIẾN THỨC — đổi kho phải chạy `harness/scripts/kb_refreeze.sh` rồi dán hash mới vào `tests/test_kienthuc.py`]
- [ ] `GET /health` live = `{ok:true, uptime_s, sessions, metrics}` (L — healthCheckPath Render + monitor ngoài; self-ping tự chạy khi có RENDER_EXTERNAL_URL)
