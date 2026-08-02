# Clean State Checklist — demo 2

Chạy TRƯỚC mỗi commit và cuối mỗi phiên (một phiên = một "transaction": commit sạch, không để dở/test đỏ/rác).

## Build / Import
- [ ] `python -c "import tools_core"` sạch (không lỗi import)
- [ ] `grep -c "@mcp.tool" mcp_server.py` = **35** (34 + `doc_chu_trang_in` [2026-08-01, đọc chữ trên TRANG IN/paperspace; NẰM TRONG tuple loại-trừ rổ neo])
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
- [ ] `python tests/test_takeoff_chong_bia.py` = **283/283 PASS** (offline; nhóm A-Y + [Z0] R1 + [Z] P3 + P4 + [id84] 12 ca + [I3-U L1] 4 ca + **[I3-U L2] 10 ca** (quy đổi '3.6m'→mm code-only tag-only/degrade-safe + C1-lite standing invariant)) — *cần env READFILE_MAX_MB=300; check.sh tự set*
- [ ] `python tests/test_qa_data.py` = **129/129** (đọc — cần ../input_files/_dxf + ../demo_doc_autocad)
- [ ] `python tests/test_model_fallback.py` = **22/22 PASS** (robustness H + **[H.10] empty-response nudge**; offline mock)
- [ ] `python tests/test_size_guard.py` = **9/9** · `test_file_ttl.py` = **12/12** · `test_health.py` = **11/11** (robustness I/J/L, offline)
- [ ] `python tests/test_session.py` = **36/36 PASS** (robustness K + **[K.7] R11 IDOR** cross-session 404 + **[K.8] F-A** race evict né phiên bận + **[K.9] bounded lock** 3 route có trần chờ + body từ chối đủ 4 khoá chữ)
- [ ] **CHỊU TẢI (2026-07-30):** `test_admission` **63** [trần SỐ BẢN VẼ `MAX_BAN_VE`; A.13-A.17 = ca red-team-impl bắt] · `test_bridge_close` **28** [dọn tiến trình mồ côi + `call()` không treo sau close; B.6 qua đường truyền MCP THẬT] · `test_ty_le_do` **17** [DIMLFAC — bản vẽ tự khai hệ số tỉ lệ đo]
- [ ] `python tests/test_hoc_log.py` = **20/20** · `test_hoc_quy_uoc.py` = **2/2** (P2 log WORM + P3 INV-10 LLM-exclusion/INV-12 grep-guard)
- [ ] **GĐ1-2 kiểm thử (offline):** `test_visual_highlight` **19** [+U6C bi_cat] · `test_excel_content` **21** [+I2 Tien_luong] (mở lại .xlsx) · `test_misc_tools` **107** [+I5 bi_cat +recall A/B/C: _tok_bound/thong_tin_file/bang_con] · `test_vntext` **53** · `test_fuzz_input` 36 · `test_dwgconv` 10 · `test_mcp_stdio` 14 (spawn mcp_server thật) · `test_app_routes` **10** [+I9 prompt keys] · `test_bang_ve_net` **9** [I4a detector] · `test_prompt_taxonomy` **24** [I9 byte-lock sha256]
- [ ] `python tests/test_grounding_guard.py` = **57/57** (id135 grounding-guard + I1b m2/m3 + I4a exclude) · `python tests/test_cao_do_min_max.py` = **31/31** (id135 recall: đọc cao độ min/max + handle)
- [ ] **KHO KIẾN THỨC (L0-L6, 2026-07-27):** `test_dispatch_gate` **11** [L0 chặn tool host-only ở dispatch] · `test_kienthuc` **15** [L1+L2 validator digit-free + byte-lock KB_HASH + strip `_kb`] · `test_kb_graft` **18** [L4 gate bằng-chứng-dương; A6 khoá BỘ BA] · `test_kb_xacnhan` **44** [L5 confirm-only + 3 bản vá + 7 vá red-team] · `test_tra_ky_hieu` **13** [L3] · `test_garble_dia` **26** [L6 fold ỉ//g→Ø]
- [ ] **ĐỢT 2026-07-31 (5 suite mới/đổi):** `test_so_do_dim` **27** [nguồn số đo: hệ số ÂM · đường đo GÓC · code 42; N.6b hình-học-suy-biến + gõ đè -> KHÔNG cứu] · `test_neo_grounding` **34** [3 kênh bơm neo: mã hiệu / tên file / HANDLE + cụm-từ-chối không tắt guard] · `test_chu_in_kich_thuoc` **24** · `test_vung_chua_doc` **44** · `test_chu_trong_ky_hieu` **26** · `test_grounding_guard` 50→**57** [+`[F2]` hàng rào SỐ ĐẾM] · `test_kienthuc` 15→**30** [+K12 tra ngược nghĩa→ký hiệu, 6 ca khoá "đa nghĩa thì KHÔNG tra ngược"] · `test_ty_le_do` 17→**25**
- [ ] **ĐỢT 2026-08-01 (1 suite mới + 4 suite đổi số):** `test_battery_runner` **52** [1.06 — dụng cụ đo bộ 198 câu: không ghi đè · chạy tiếp · chặn trộn phiên bản · R.11 tham số dòng lệnh phải có tác dụng] · `test_takeoff_chong_bia` 272→**283** [+W.10a-k đối chiếu `$INSUNITS` với độ lớn số đo] · `test_vntext` 28→**53** [+E/F/G/H/I/K: dấu hiệu TCVN3 tầng 2 · thứ tự giải-mã-trước/đổi-mã-sau · `Ð` hai nghĩa · chuỗi TRỘN · NFC] · `test_garble_dia` 26→**27** [G5 đổi kỳ vọng + G5b: `'thép ỉ10'` vốn do CHÍNH `to_unicode` tạo ra]
- [ ] `bash harness/scripts/check.sh` = **HARNESS GATE: PASS** (**48 bước · 35 MCP tool · tổng 1.627 ca**). ⚠ ĐỪNG nhớ số từng suite trong đầu — mốc ĐÚNG lấy từ chính output `check.sh`; checklist hay lạc hậu hơn code. Suite thêm/đổi số ở phiên 2026-08-01→08-02: **MỚI** `test_ma_dinh_dang` 35 · `test_c1_phi_no_go` 15 · `test_trang_in` 20 · `test_neo_rong_tu_choi` 26 · `test_a3_trich_trang_in` 21 · `test_vni` 43. **ĐỔI**: `test_vntext` giữ 53 (VNI tách suite riêng).
- [ ] ⚠ **CỔNG XANH KHÔNG ĐỦ để tin bản vá đã chạy.** Bài học 2026-07-30: vá DIMLFAC đổi số thật trên 21,5% đường kích thước mà CẢ 6 suite đóng-băng-số (272/107/51/31/24/61) VẪN XANH — bộ kiểm cũ mù hoàn toàn với lớp lỗi đó. Với mọi bản vá đổi hành vi đọc: phải TỰ KIỂM NGƯỢC rằng nó thực sự chạy (so số trước/sau bằng script), rồi mới thêm suite khoá.
- [ ] ⚠⚠ **KHÔNG TIN "PASS" NẾU CỔNG CHẠY TRÊN CÂY ĐANG SỬA — VÀ PHẢI ĐỌC MÃ THOÁT THẬT.** Bài học 2026-07-31, ba lần trong một phiên: (a) cổng chạy nền trong lúc còn đang sửa file test → kết quả vô nghĩa, phải chạy lại trên cây đã ổn định; (b) một lần cổng **`exit 127`** (thư mục shell bị đặt lại) nên **KHÔNG HỀ CHẠY** — đọc mỗi dòng "PASS" của lần trước thì tưởng xong; (c) notification nền báo "exit code 0" là mã thoát của lệnh `echo` nối sau, KHÔNG phải của `check.sh`. ⇒ luôn ghi `EXIT_CODE_THAT=$?` NGAY sau `check.sh` vào chính file output, và `grep "HARNESS GATE"` trong FILE chứ đừng tin summary.
- [ ] ⚠ **ĐO TRƯỚC, CODE SAU — và coi chừng phép đo tautology.** Bài học 2026-07-31: lượt đo đầu của hàng rào số-đếm ra "0% lọt" chỉ vì tự loại số trùng neo lúc sinh dữ liệu (kết quả tất yếu của cách sinh, không đo gì). Và "tỉ lệ lọt" nói chung KHÔNG phải đại lượng ổn định — cùng một rổ neo, đổi bộ sinh số thì chạy 0,0%→13,6%. Phép đo dùng được để RA QUYẾT ĐỊNH là phép đo trên **câu trả lời THẬT chấm bằng NHÃN ĐỘC LẬP** (`ky_vong` của bộ 198 câu), không phải trên dữ liệu tự sinh.
- [ ] ⚠⚠⚠ **KIỂM CHÍNH BỘ TRÍCH TRƯỚC KHI TIN CON SỐ NÓ ĐƯA RA.** Bài học 2026-08-01, **ba lần trong một phiên**, cả ba đều suýt cho kết luận NGƯỢC: (a) regex `tổng…{0,40}(\d)` ra **"0 gắn cờ"** nghe như "luật hoàn hảo" — thực ra nó vớ phải **"304" trong "INOX 304"** nên luật KHÔNG BAO GIỜ kích; (b) bộ dò từ-khoá đếm *"**không tìm thấy** thông tin cho thấy chữ 'Cọc' bị lỗi font"* (= một KHẲNG ĐỊNH DƯƠNG) thành "từ chối" → thổi "bỏ sót" từ ~2% lên **13%**; (c) luật tổng-tập-con bắt được tổng cộng ĐÚNG nhưng **mù với tổng cộng SAI** — đúng thứ gây hại. ⇒ Trước khi tin bất kỳ tỉ lệ nào: chạy bộ trích lên **ca đã biết đáp án** và xem nó có bắt đúng ca đó không. Số "0%" và số "quá đẹp" đều là dấu hiệu bộ trích hỏng, không phải tin mừng.
- [ ] ⚠⚠⚠⚠ **"SỐ QUÁ XẤU" CŨNG LÀ DẤU HIỆU BỘ TRÍCH HỎNG, KHÔNG CHỈ "SỐ QUÁ ĐẸP".** Bài học 2026-08-02 (bảng mã VNI), suýt VỨT MỘT BẢN VÁ ĐÚNG: bản đo đầu báo **"HỎNG THÊM = 1101"** + **"2190 chuỗi chạm file bẫy"** — nghe như phải huỷ ngay — nhưng chính ví dụ nó gắn cờ là `'CHI TIEÁT MUẾI COẼC'`→`'CHI TIẾT MŨI CỌC'`, tức **CỨU ĐÚNG**. Hai lỗi **ĐỊNH NGHĨA**: (a) gọi *"file bẫy"* = mọi file khai phông VNI — nhưng file bẫy THẬT là **khai VNI mà RUỘT TCVN3**; (b) định nghĩa *"sạch"* = không có ký tự lạ — nhưng **VNI DÙNG LẠI chính chữ Việt hợp lệ làm DẤU** (`GIAÙO` = A+Ù+O) nên **mọi bản CỨU bị tính thành HỎNG**. ⇒ Khi một tỉ lệ ra **quá xấu**, hỏi ĐÚNG câu như khi nó quá đẹp: *"tử số và mẫu số có đo CÙNG MỘT THỨ chưa?"* và *"phép đo này CÓ THỂ ra kết quả KHÁC được không?"*
- [ ] ⚠ **ĐẦU MỤC CÓ TIÊU ĐỀ NHIỀU VẾ → ĐÒI MỘT CON SỐ CHO MỖI VẾ trước khi đánh dấu xong.** Bài học 2026-08-01: mục 1.03 có tiêu đề BA VẾ (*"nắn phông cũ: **VNI**, TCVN3 còn sót, Ø vỡ"*) bị đánh dấu `done` khi mới làm 2 — vế VNI có **0 dòng code**, và `test_vntext` **53 PASS nhưng 0/53 ca chạm VNI** ⇒ **cổng KHÔNG THỂ đỏ dù vế đó chưa bắt đầu**. Luôn hỏi thêm: *"suite hiện có bao nhiêu ca chạm vế này?"* — nếu **0** thì cổng xanh **không nói gì** về vế đó.
- [ ] ⚠ **BẢN VÁ CŨNG CÓ THỂ NỚI RỘNG MỘT LỖI KHÁC — TỰ KHAI, ĐỪNG ĐỂ PHIÊN SAU VẤP.** Bài học 2026-08-01: thêm `doc_chu_trang_in` vào tuple loại-trừ rổ neo là ĐÚNG và BẮT BUỘC (không loại thì dãy âm `-1..-10` từ SỐ TỜ vào rổ neo = tái sinh id135), nhưng nó làm danh sách đi **3 → 4 tool**, tức **nới bề mặt** của lỗi *"rổ neo rỗng ⇒ máy trả 'không có thông tin' SAI SỰ THẬT"*.
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
