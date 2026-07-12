# Claude Progress — demo 2 (nhật ký tiến độ theo phiên)

> Continuity Artifact (chuẩn Harness): lưu "đã làm gì / kết quả test / quyết định / đang chờ" để phiên sau không mất ngữ cảnh.
> Mới nhất ở TRÊN CÙNG. Bàn giao đầy đủ: `session-handoff.md`. Nhật ký chi tiết hơn nữa: `../GHI_CHU_HOAN_THIEN.md`.

---
## Session 2026-07-12 (c) — TRIỂN KHAI P-1: vá 6 lỗ tồn tại E1-E6 (nền cho AI tự học)
**Mục tiêu:** user chốt "commit tài liệu + bắt tay P-1". Commit doc kế hoạch (`e32d7ce`) rồi triển khai P-1 = vá 6 lỗ ĐANG TỒN TẠI (tính năng tự học sẽ khuếch đại nếu không vá).

**Đã làm (quy trình chuẩn: workflow spec → tự đọc code → implement tuần tự E4→E6→E5→E1→E3→E2, test sau mỗi bước → red-team đối kháng diff → vá finding → commit):**
- **Workflow 7-agent** ra spec sửa TỐI THIỂU + backward-compat + regression-watch + test đối kháng cho từng lỗ (đã chạy fixture thật). Thứ tự implement + helper dùng chung do agent tích hợp chốt.
- **Vá 6 lỗ** (`tools_core.py`/`mcp_bridge.py`/`app.py`/`render.yaml`/tests): **E1** neo+lọc-bán-kính `_KG_UV_R` (loại note ngữ cảnh khác); **E2** `_xac_nhan_ung_vien_theo_handle` giữ provenance (chua_chac/handle/can_doi_chieu, handle bịa→từ chối); **E3** `_rs_so_luong` đối chiếu file→`nghi_ngo` khi lệch (số dùng đối tác); **E4** SYSTEM_PROMPT rule 15 + `_co_chi_thi_dang_ngo` (advisory); **E5** runner đếm SKIP+CANH BAO; **E6** upload uuid_basename + cookie Secure gate-env.
- **Red-team đối kháng 4-agent trên diff** → 4 CONFIRMED đã vá: **E1 overfit** (note kg xa mã bị vứt IM LẶNG → nay LỘ note xa hạ 'thap'+khoảng cách, "thất bại phải lộ"); **E4 false-positive** ('coi như tường 220'/'bỏ qua lớp vữa' bị cờ oan → thu hẹp chỉ bắt 'bỏ qua LUẬT/quy ước'); **E2 ép-thiếu-oan** (so_luong_handle → fall-through đọc file); **E3 xau** (lộ nghi_ngo cả khi input khác không hợp lệ). Red-team XÁC NHẬN **KHÔNG rò P4** (tong_hop/Excel không tiêu thụ output tinh_dai_luong) + backward-compat.

**Kết quả test:** `test_takeoff_chong_bia.py` **203/203** (was 191; nhóm mới **[X] 12 ca** khoá E1-E4 + E2 fall-through + E1 far-fallback) · `test_qa_data.py` **129/129** · `check.sh` **[8/8] PASS**. Commit **`73990de`** (code) + **`5ecaca1`** (doc). **✅ PUSH + DEPLOY + VERIFY LIVE:** `/version` commit = `5ecaca1bf767...` khớp HEAD; `/health` ok (uptime mới, use_ai, metrics sạch).

**Bài học:** red-team trên DIFF THẬT (không chỉ design) bắt được overfit E1 mà test-với-fixture-đơn KHÔNG lộ (fixture Gia Lộc xanh chỉ vì note tình cờ gần mã) — đúng ethos chống-overfit + "thất bại phải lộ". Fix đúng KHÔNG phải siết chặt hơn mà là LỘ khi recall bị cắt. Backward-compat = chỉ thêm key khi kênh mới kích hoạt (input cũ byte-identical).

**Đang chờ:** (P-1 đã LIVE ✅) — bước tiếp P0→P1 (đọc-thuần: used_handles/residual/hỏi-để-học) an toàn tuyệt đối, làm được ngay. P5 (codify) vẫn CHẶN tới khi có corpus ≥3 firm.

---
## Session 2026-07-12 (b) — NGHIÊN CỨU + KẾ HOẠCH CHI TIẾT "AI tự học" (planning, KHÔNG code)
**Mục tiêu:** user giao "tiếp tục nghiên cứu + lên kế hoạch chi tiết đầu mục AI tự học" (đang ở mức planned). Deliverable = tài liệu kế hoạch kỹ thuật, KHÔNG đụng code sản phẩm.

**Đã làm:**
- **Baseline đầu phiên (xác nhận trước khi làm):** `check.sh` **HARNESS GATE PASS [8/8]** (takeoff **191/191** + robustness 20/9/12/17/11) · `test_qa_data.py` **129/129** · git sạch, HEAD `5e1961f`=origin/main (đã push). *(Lưu ý: user gõ `cd backend && pytest` — dự án KHÔNG có backend/ & KHÔNG pytest; chạy script + check.sh.)*
- **Workflow 17-agent** (Ground 4 đọc code thật → Design panel 3 lăng kính → Judge 3 chấm chéo → Red-team 7 hướng): điểm safety-first 23.5 / product 22 / **eng-minimal 25 THẮNG**. Tổng hợp = xương sống eng-minimal + **ghép bắt buộc** đảm bảo an toàn của safety-first (cổng ngữ-nghĩa hoá-code, mặc-định-chỉ-log, thu-hồi first-class, comparator ③ 5 nguồn, cap tin-cậy).
- **TỰ tái hiện 6 lỗ ĐANG TỒN TẠI trên code thật** (không tin mù red-team — đúng `feedback-bia-tai-sinh-tang-code`): **E1** `_ung_vien_kg_moi_bo` quét cả file khoang_cach=None (1168-1191); **E2** xác nhận ứng viên qua `_nd` mất provenance→Excel chắc chắn (_nd 512, _rs_bs_only 1442); **E3** `_rs_*` short-circuit bs TRƯỚC đọc file→đè số-đọc âm thầm (1258 trước 1259); **E4** SYSTEM_PROMPT 0 dòng chống prompt-injection (mà vn[:80] đã vào context Gemini); **E5** test silent-skip + 0 dwg/dxf commit→gate ≥3-file không ép được (test 47-52); **E6** app.py:169 basename→2 phiên đè file.
- **Viết `KE_HOACH_AI_TU_HOC_CHI_TIET.md`** (bản kỹ thuật của NGHIEN_CUU_AI_TU_HOC.md): kiến trúc neo code thật (3 primitive lõi used_handles/_residual_texts/dò-residual-gần-mã; 3 tín hiệu; data model 3 bản ghi; 6 tool; 4 cổng↔code); threat-model 7 red-team + biện pháp bắt buộc; lộ trình **P-1 (vá E1-E6) → P0..P5**; bất biến/non-goals/kill-criteria; **giới hạn nền tảng** (đối tác sở hữu file → cổng-1 không đủ, phòng thủ thật = chua_chac + ≥3 nguồn + người + không-vào-tổng). Cập nhật `feature_list.json` evidence (vẫn planned).

**Kết quả test:** KHÔNG đổi code sản phẩm → baseline giữ nguyên (191/129/[8/8]). Chỉ thêm 1 doc + sửa 1 dòng evidence.

**Bài học:** design-panel + red-team đối kháng lộ ra tính năng "tự học" KHUẾCH ĐẠI lỗ SẴN CÓ (provenance-laundering khi xác nhận ứng viên, injection qua vn[:80]) → kế hoạch phải có phase PRE-WORK vá lỗ tồn tại trước khi xây vòng học. Sự thật cứng: đối tác SỞ HỮU file nên "neo handle thật" (cổng-1) thoả mãn tầm thường — phải nói thẳng giới hạn.

**Đang chờ:** ⚠ CHƯA commit (doc kế hoạch) — chờ user duyệt. Khi triển khai: bắt đầu P-1 (vá E1-E6, có giá trị độc lập). Mở P5 (codify) CHẶN tới khi có corpus ≥3 firm khác nhau (trùng "xin 3-5 bản vẽ đa-domain" đã treo).

---
## Session 2026-07-12 (CHỐT SỔ) — Củng cố G + Residual G + Robustness H–L + Audit an toàn
**Tóm tắt phiên:** phiên DÀI, **8 commit** đều theo quy trình chuẩn (probe → design → adversarial verify → test → docs → commit/push/deploy/verify `/version`(+`/health`) LIVE). Chi tiết từng đầu việc ở các entry bên dưới.

**Đã làm (8 commit, tất cả deploy LIVE):**
- **G** `7b06188` — test đối kháng ĐA-DOMAIN (9T KT/KC) + vá **3 bug tầng tổng hợp** (tong_phu gộp thép 67759.7/4110.7 · gộp Số lượng 835 · parity diện tích density).
- **Residual G** `d1c8b03` — đọc SL BẢNG THỐNG KÊ theo cột TỔNG (`_build_schedule_qty_index`, gated fail-silent); #2 cờ đơn vị <40 = by-design no-fix.
- **Robustness H–L:** `3f16531` model fallback 429/503 · `a890f9f` chặn file lớn sớm · `f472ee0` dọn file TTL · `7c721a8` tách state theo session · `fee67f9` keep-alive+giám sát (/health).
- **Audit an toàn đa-agent** `301ccdd` — workflow 27-agent → vá **9 lỗ** (H1 VN-thousands 1.130→1130 · H2 tong_phu gộp m³ ghi sẵn · M3-M9 crash/mislabel/tra-cứu). Bề mặt an toàn xác nhận vững.

**Kết quả test (clean-state cuối phiên, ĐỀU 0 FAIL):** `test_takeoff_chong_bia.py` **191/191** (nhóm A-W) · `test_qa_data.py` **129/129** · `harness/scripts/check.sh` = **HARNESS GATE: PASS [8/8]** (import+21 tool · no-key · takeoff 191 · fallback 20 · size-guard 9 · file-ttl 12 · session 17 · health 11). Working tree TRACKED sạch, push hết, HEAD `301ccdd` LIVE (`/version`+`/health`). **KHÔNG pytest** (test đổi sys.stdout lúc import → pytest crash; dùng SCRIPT runner + check.sh).

**Quyết định dài hạn (đã lưu memory):** audit đa-agent hiệu quả nhưng SYNTH/VERIFY có thể mâu thuẫn/thổi phồng → **phải TỰ tái hiện** finding trên file thật; kiểm code-vs-policy phải quét HẾT danh mục cùng lớp (audit tìm đúng bug SAME-CLASS mà `feedback-bia-tai-sinh-tang-code` cảnh báo).

**Trạng thái ROADMAP:** Củng cố **A–G** ✅ · Residual G ✅ · Robustness **H–L** ✅ · Audit an toàn đa-agent ✅. feature_list: 28 done / 1 deferred (dự toán chi phí) / 1 planned (AI tự học).

**Đang chờ / bước tiếp (trước giao rộng):** xin 3-5 bản vẽ đơn vị khác LAYOUT (củng cố đọc bảng thống kê + VN-thousands đa-file) + dựng KPI "tỷ lệ bịa". Dự toán chi phí = HOÃN chờ đối tác chốt. AI tự học = planned (research).

---
## Session 2026-07-12 — AUDIT AN TOÀN đa-agent (mọi tool) + vá 9 lỗ hổng
**Mục tiêu:** audit chống-bịa toàn diện MỌI tool (đề xuất trước giao rộng), rồi vá lỗ tìm được. (Sau robustness H–L, HEAD `fee67f9` live.)

**Đã làm:**
- **AUDIT (workflow 27-agent):** 7 agent audit song song theo nhóm tool (quantity/steel/listing/dimensions/takeoff×2/agg) chạy engine THẬT offline với input đối kháng → 19 finding nghi ngờ → 19 skeptic verify độc lập (mặc định refute) → **10 confirmed** (9 refute là an-toàn/đúng-thiết-kế). Rồi **TỰ tái hiện TẤT CẢ trên file thật** (không tin mù synth/verify — synth under-report + 1 finding verify refute mà synth lại promote → phải tự chạy).
- **9 LỖ THẬT đã vá (`tools_core.py`):**
  - **H1 VN-thousands:** `_to_num_vn` — '.' = phân cách NGHÌN. Nhãn thật 9T KT `'ký túc xá: 1.130 m2'` đọc **1.13 → nay 1130** (lệch 1000×). Dùng ở `_build_stated_areas`/`_build_stated_volumes`.
  - **H2 tong_phu gộp m³ ghi sẵn dị-loại** (đào 860+bê tông 500=1360): thêm "Khối lượng (ghi sẵn)" vào `_khong_cong` (đúng lớp bug G thép/Số lượng — [[feedback-bia-tai-sinh-tang-code]] đoán đúng).
  - **M3** `tinh_dai_luong` crash JSON non-dict (`[1,2]`/`5`...) → coerce {}. **M4** `tra_cuu_so_luong` gán 131 (TỔNG cọc) cho mã lẻ c-40 → cờ `is_total`, `tra_so_luong` bỏ qua khi truy vấn mã. **M5** `tong_so_luong` gộp 711 dị-loại → tong=None khi không lọc. **M6** `liet_ke_so_luong` lọc trượt âm thầm trả cả 94 → so_muc=0 LỘ. **M7** `liet_ke_chu_theo_layer` overmatch substring → khớp CHÍNH XÁC. **M8** "ván khuôn móng" → the_tich_be_tong_mong → fail-closed None. **M9** `thong_tin_kich_thuoc` hardcode mm → đọc $INSUNITS + ghi_chu chưa-chắc.
- **BỀ MẶT AN TOÀN xác nhận (audit chứng cả cái vững):** 177 test cũ · G tách thép · `_nd` inf/nan/bool · existence gate · `_resolve_lo_cua` trần/tràn · takeoff `math.isfinite`+>0. Lõi chống-bịa vững; 9 lỗ ở tầng ĐỌC/TỔNG-HỢP/TRA-CỨU phụ.

**Kết quả test:** `test_takeoff_chong_bia.py` **191/191** (nhóm mới **[W]** 14 ca khoá 9 fix + [M] cập nhật do m³-ghi-sẵn nay chỉ ở bảng) · `test_qa_data.py` **129/129** (port KHÔNG đổi — KEYWORDS không có mã cọc lẻ nên is_total-skip vô hại) · `check.sh` [8/8].

**Bài học:** audit đa-agent + skeptic-verify hiệu quả (10/19 sống sót) nhưng SYNTH/VERIFY có mâu thuẫn → phải TỰ tái hiện; audit tìm đúng bug SAME-CLASS mà [[feedback-bia-tai-sinh-tang-code]] cảnh báo (tong_phu còn 1 danh mục m³ chưa loại) — kiểm code-vs-policy phải quét HẾT danh mục cùng lớp.

**Đang chờ:** ⚠ CHƯA commit audit fixes — chờ user. Sau audit: xin 3-5 bản vẽ khác layout (củng cố đọc bảng thống kê + VN-thousands đa-file) + KPI tỷ lệ bịa; dự toán chi phí HOÃN.

---
## Session 2026-07-11 (g) — Robustness L: keep-alive + giám sát (CHỐT robustness H–L)
**Mục tiêu:** đầu việc L (robustness CUỐI) — Render free ngủ sau ~15' idle → cold-start; giữ thức + health check + quan sát cơ bản. (Sau K, HEAD `7c721a8` live.)

**Đã làm:**
- **PROBE:** `Dockerfile` chạy `gunicorn --workers 1 --threads 4` (→ giả định 1-worker của K ĐÚNG); `render.yaml` `plan: free` + `healthCheckPath: /` (nặng — trả cả HTML); chưa có keep-alive. Render tự set `RENDER_EXTERNAL_URL`.
- **TRIỂN KHAI (`app.py`):** `/health` — JSON NHẸ (no API/no bản vẽ): `{ok, uptime_s, sessions, use_ai, model, metrics}`. `_METRICS` (uploads/asks/errors) tăng ở upload/ask (giám sát cơ bản). Self-ping: `_keepalive_ping()` GET `<RENDER_EXTERNAL_URL|KEEPALIVE_URL>/health` (traffic NGOÀI thật → Render không ngủ), nuốt lỗi; `_keepalive_loop` mỗi `KEEPALIVE_MIN` (10') ; `_start_keepalive()` CHỈ chạy khi có URL (production) — local/test KHÔNG kích. `render.yaml` `healthCheckPath` → `/health`.
- **AN TOÀN:** self-ping guard theo URL (không chạy local/test/không cấu hình); nuốt mọi lỗi (không crash luồng nền); `/health` không tốn API/không đụng bản vẽ; `KEEPALIVE_MIN=0` tắt.

**Kết quả test:** `tests/test_health.py` **11/11** (offline: /health 200+shape, metrics tăng sau upload/ask, self-ping không chạy khi URL rỗng + ping đúng `<url>/health` + nuốt lỗi khi urlopen fail, _start_keepalive an toàn, healthCheckPath render.yaml) · `check.sh` **[8/8] PASS** · takeoff 177 + fallback 20 + size-guard 9 + file-ttl 12 + session 17 KHÔNG regression.

**★ CHỐT ROBUSTNESS H–L HOÀN TẤT:** H (model fallback) · I (chặn file lớn) · J (dọn file TTL) · K (tách session) · L (keep-alive+giám sát) — ĐỀU XONG, mỗi mục có test offline riêng trong cổng [8/8]. Cùng Củng cố A–G + Residual G.

**Bài học:** self-ping bằng `RENDER_EXTERNAL_URL` (traffic ngoài) là cách keep-alive hợp lệ trên Render free (khác self-ping nội bộ vô tác dụng); guard-theo-env cho phép tính năng production chạy an toàn mà test offline không kích; tách hàm 1-lần (`_keepalive_ping`) khỏi vòng lặp vô hạn để test tất định.

**Đang chờ:** ⚠ CHƯA commit L — chờ user duyệt. Sau H–L: đề xuất trước giao rộng = audit an toàn đa-agent MỌI tool + xin 3-5 bản vẽ khác layout (củng cố đọc bảng thống kê) + dựng KPI tỷ lệ bịa; dự toán chi phí vẫn HOÃN chờ đối tác.

---
## Session 2026-07-11 (f) — Robustness K: tách state theo session (hết cảnh 2 người đạp nhau)
**Mục tiêu:** đầu việc K (robustness NẶNG NHẤT) — hiện 1 `Drawing` global + 1 MCP subprocess + 1 SUMMARY/CHAT_HISTORY global → người B upload xoá bản vẽ + lịch sử của người A. Cô lập per-session. (Sau J, HEAD `f472ee0` live.)

**Đã làm:**
- **PROBE:** `app.py` giữ `BRIDGE`/`SUMMARY`/`CHAT_HISTORY` GLOBAL; `MCPBridge` = 1 subprocess = 1 Drawing (khởi tạo đắt, chờ tới 40s). `/upload` + `/ask` dùng chung state global.
- **THIẾT KẾ (cô lập ở TẦNG APP — KHÔNG đụng mcp_server/tools/anti-bịa):** mỗi phiên trình duyệt (cookie `sid`) có bridge (1 subprocess/1 Drawing) + summary + history + lock RIÊNG. Bound RAM: **CAP** `MAX_SESSIONS` (đầy → đóng phiên CŨ NHẤT/LRU, giải phóng subprocess) + **TTL** `SESSION_TTL_MIN` (đóng phiên nhàn rỗi). Bridge tạo LƯỜI ở /upload (phiên chưa upload → không tốn subprocess). Không đổi mcp_server (mỗi bridge vẫn 1 Drawing global — nhưng nay 1 subprocess/PHIÊN).
- **TRIỂN KHAI (`app.py` — chỉ file này):** `SESSIONS` dict + `_SESS_LOCK` (RLock) + `MAX_SESSIONS`(4)/`SESSION_TTL_MIN`(30, env). `_make_bridge()` (tách để test mock), `_close_session()`, `get_session()` (sweep TTL + enforce cap LRU + stash `g.sid`), `@app.after_request` set cookie `sid` (httponly+SameSite=Lax). `/upload` + `/ask` dùng `s["bridge"]/s["summary"]/s["history"]` với `with s["lock"]` (tuần tự hoá request cùng phiên; khác phiên = khác bridge → song song). Xoá `BRIDGE/SUMMARY/CHAT_HISTORY/get_bridge` cũ. `/ask` chưa nạp → báo LỘ "Chưa nạp bản vẽ cho phiên này".
- **AN TOÀN/CHỐNG BỊA:** không đụng lõi đọc/anti-bịa; CAP+TTL chặn nổ RAM/subprocess; per-session lock tránh 2 lượt đạp history/bridge; backward-compat: 1 trình duyệt = 1 phiên như cũ.

**Kết quả test:** `tests/test_session.py` **17/17** (offline, Flask test_client + FakeBridge mock + fake tra_loi_ai — KHÔNG spawn subprocess/KHÔNG tốn API: K.1 2 phiên cô lập + bridge khác nhau, K.2 history riêng, K.3 CAP đóng LRU, K.4 TTL đóng phiên nhàn rỗi, K.5 ask chưa nạp báo lộ, K.6 hằng số) · `check.sh` **[7/7] PASS** · takeoff 177 + fallback 20 + size-guard 9 + file-ttl 12 KHÔNG regression.

**Bài học:** cô lập ở TẦNG CAO NHẤT (app quản dict phiên → nhiều bridge) rẻ + an toàn hơn nhồi session_id vào mọi tool MCP (đụng anti-bịa core); tách `_make_bridge()` cho phép test cô lập/CAP/TTL tất định bằng FakeBridge không subprocess; CAP + TTL là bắt buộc khi mỗi phiên = 1 subprocess (chặn nổ RAM trên gói nhỏ).

**Đang chờ:** ⚠ CHƯA commit K — chờ user duyệt. Deploy nên chỉnh `MAX_SESSIONS` theo RAM gói Render. Còn robustness L (keep-alive + giám sát) — mục cuối.

---
## Session 2026-07-11 (e) — Robustness J: dọn file TTL (_uploads/_renders không phình)
**Mục tiêu:** đầu việc J (robustness) — `_uploads`/`_renders` tích tụ (DXF upload/convert, PNG render, Excel) → bound đĩa theo TTL. (Sau I, HEAD `a890f9f` live.)

**Đã làm:**
- **PROBE điểm tạo file:** `UPLOAD_DIR` (upload save + `convert_dwg_to_dxf`), `RENDER_DIR` (`hl_*.png` render_region dòng 1849, `th_*.xlsx` xuat_excel dòng 1798). Chưa có cleanup.
- **THIẾT KẾ:** util NHẸ (chỉ os/time) để import được ở CẢ web process (app.py) LẪN MCP subprocess (tools_core) không kéo ezdxf/matplotlib. Dọn OPPORTUNISTIC (không thread nền — tránh chồng K): (1) mỗi UPLOAD dọn cả `_uploads`+`_renders` (bound qua nhiều phiên); (2) sau mỗi RENDER/EXCEL dọn `_renders` (bound trong 1 phiên dài nhiều ảnh).
- **TRIỂN KHAI:** `fileutil.py` mới — `cleanup_old_files(dirs, ttl_min, keep=None)` xoá file mtime > TTL; `keep`=giữ file vừa tạo/đang dùng; ttl<=0=tắt; chỉ xoá FILE (không đệ quy thư mục con); nuốt lỗi I/O lẻ (đếm errors, không chặn luồng). `tools_core`: `FILE_TTL_MIN` env (60') + gọi sau savefig (render_region) & wb.save (xuat_excel) với keep=file mới. `app.py`: `FILE_TTL_MIN` (khớp env) + gọi `cleanup_old_files([UPLOAD_DIR,RENDER_DIR])` đầu mỗi upload.
- **AN TOÀN:** file đang-dùng của phiên đều MỚI (mtime gần) → không bị dọn; query/render dùng `self.doc` trong RAM (không đọc lại đĩa) → xoá file cũ trên đĩa không vỡ phiên; keep bảo vệ file vừa tạo; ttl<=0 tắt hoàn toàn (env).

**Kết quả test:** `tests/test_file_ttl.py` **12/12** (offline, dùng `os.utime` lão hoá — J.1 xoá cũ/giữ mới/keep/không đệ quy, J.2 ttl=0 tắt, J.3 dir vắng không crash, J.4 nhiều dir, J.5 hằng số int + app khớp tools_core) · `check.sh` **[6/6] PASS** · takeoff 177 + fallback 20 + size-guard 9 KHÔNG regression.

**Bài học:** cleanup opportunistic (theo sự kiện tạo file) đủ cho demo + KHÔNG cần thread nền (tránh vướng đa-worker của K); tách util NHẸ để dùng chéo process không kéo dep nặng; `keep=` + mtime-mới bảo vệ file active mà không cần biết "session hiện tại".

**Đang chờ:** ⚠ CHƯA commit J — chờ user duyệt. Còn robustness K (tách session — 1 DRAWING global) / L (keep-alive + giám sát).

---
## Session 2026-07-11 (d) — Robustness I: chặn file lớn SỚM (trước convert/parse)
**Mục tiêu:** đầu việc I (robustness) — từ chối file quá khổ TRƯỚC khi tốn ODA convert (~600s) + ezdxf parse (RAM). (Sau H, HEAD `3f16531` live.)

**Đã làm:**
- **PROBE:** đã có `MAX_CONTENT_LENGTH=150MB` (Flask 413 cho upload thô) + `too_large`. Nhưng `tools_core.Drawing.__init__` kiểm `READFILE_MAX_MB` (45MB) **SAU convert** → DWG lớn tốn ODA rồi mới loại; và file 45–150MB vẫn save+parse rồi mới báo lỗi (500) sâu trong tools_core.
- **THIẾT KẾ (phòng thủ nhiều tầng):** (1) `tools_core`: kiểm size **raw TRƯỚC convert** (DWG lớn → DXF chắc chắn ≥ DWG do phình 2-8x → loại NGAY, khỏi ODA) + giữ check **sau-convert** cho DWG nén phình. (2) `app.py`: kiểm size ngay **sau save, trước gọi MCP** → trả **413** sạch + **DỌN file** (chạm luôn J).
- **TRIỂN KHAI:** `tools_core.py __init__` tách `raw_mb > READFILE_MAX_MB` (trước `convert_dwg_to_dxf`) + nhánh DWG check lại sau convert. `app.py` thêm hằng `READFILE_MAX_MB` (khớp env), upload check `os.path.getsize(dest)` → 413 + `os.remove`. Lỗi DWG-nén-phình vẫn qua đường 500 cũ (không đoán được trước convert — đã ghi chú).
- **CHỐNG BỊA/an toàn:** không đổi ngưỡng (vẫn READFILE_MAX_MB), chỉ ÉP SỚM hơn → KHÔNG false-reject file hợp lệ dưới ngưỡng; DWG nén dưới ngưỡng vẫn cho qua (tools_core check sau convert).

**Kết quả test:** `tests/test_size_guard.py` **9/9** (offline, tất định, KHÔNG tốn API — I.1 file rác chặn TRƯỚC parse ezdxf, I.2 DXF hợp lệ >ngưỡng vẫn chặn, I.3 dưới ngưỡng nạp được, I.4 app /upload trả 413 + dọn file qua Flask test_client, I.5 hằng số int + app khớp tools_core) · `check.sh` **[5/5] PASS** · takeoff 177 + fallback 20 KHÔNG regression.

**Bài học:** chặn sớm = kiểm ở tầng CAO NHẤT có đủ thông tin (raw size biết ngay, DXF-sau-convert phải đợi convert) → phòng thủ 2 tầng thay vì 1 check sâu; dọn file khi từ chối (bắc cầu J). Flask `test_client` cho test upload tất định không cần server thật.

**Đang chờ:** ⚠ CHƯA commit I — chờ user duyệt (rồi push/deploy/verify). Còn robustness J (dọn file TTL) / K (tách session) / L (keep-alive).

---
## Session 2026-07-11 (c) — Robustness H: chuỗi model dự phòng khi 429/503
**Mục tiêu:** đầu việc H (ROADMAP robustness) — Gemini model chính 429 (cạn quota) / 503 (quá tải) kéo dài → tự nhảy model phụ, không crash/không bịa. (Sau Residual G, HEAD `d1c8b03` live.)

**Đã làm:**
- **PROBE:** `mcp_bridge.py` dùng 1 `MODEL` (env `GEMINI_MODEL`=gemini-2.5-flash); SDK đã có `HttpRetryOptions` retry HTTP 429/5xx ~3 lần/model (dòng 274). 2 chỗ gọi `generate_content` (vòng tool-use + câu cuối). Comment 35-37 xác nhận đúng vấn đề (3.5-flash hay 503, pro 429). `app.py ask()` đã try/except quanh `tra_loi_ai`.
- **THIẾT KẾ (phân tầng):** SDK retry lo blip TẠM (retry cùng model); H kích khi model VẪN cạn/quá tải SAU retry → NHẢY model kế trong chuỗi (fail-forward), KHÔNG lùi lại model đã hỏng trong cùng request.
- **TRIỂN KHAI (`mcp_bridge.py`):** `MODELS = [MODEL] + GEMINI_FALLBACK_MODELS` (env, mặc định `gemini-2.0-flash,gemini-1.5-flash`; rỗng → hành vi CŨ 1 model). `_is_overloaded(e)` (mã HTTP 429/500/502/503/504 hoặc chuỗi resource_exhausted/unavailable/quota/high demand; lỗi khác=False). `_gen_fallback(client,contents,cfg,state)` thử `MODELS[state['i']:]`, gặp 429/503→model kế, `state['i']` giữ model đang dùng qua các lượt. Cắm vào CẢ 2 chỗ gọi (chung `_mstate`). Quá tải HẾT chuỗi ở vòng tool → trả LỘ "AI đang quá tải, thử lại sau" (không crash). `app.py /version` thêm `models` (verify deploy). Lỗi KHÔNG quá-tải (safety/400/404) → ném ngay (fallback vô ích).
- **CHỐNG BỊA:** fallback CHỈ đổi model, KHÔNG chạm chốt chống-bịa (số vẫn do tool/handle); hết model → báo lỗi trung thực, KHÔNG bịa câu trả lời.

**Kết quả test:** `tests/test_model_fallback.py` **20/20** (offline, MOCK client, KHÔNG tốn API — H.1 nhận lỗi, H.2-4 nhảy model, H.5 hết chuỗi ném, H.6 lỗi khác ném ngay, H.7 state không dò lại, H.8 chuỗi 1-model = cũ) · `check.sh` **[4/4] PASS** (thêm bước fallback) · takeoff 177/177 + qa 129/129 KHÔNG regression (H không đụng tools_core). Import `app`/`mcp_bridge` sạch, MODELS=[2.5→2.0→1.5-flash].

**Bài học:** feature ops đụng API live vẫn test tất định được bằng MOCK client + tách logic thuần (`_is_overloaded`/`_gen_fallback`) khỏi SDK — không tốn API, khoá regression. Phân tầng retry (SDK=blip, app=đổi model) tránh chồng chéo.

**Đang chờ:** ⚠ CHƯA commit H — chờ user duyệt (rồi push/deploy/verify). Deploy nên đặt env `GEMINI_FALLBACK_MODELS` theo model account có quyền. Còn robustness I/J/K/L.

---
## Session 2026-07-11 (b) — Residual G: đọc SL bảng thống kê theo cột TỔNG (#1) + xác nhận #2 by-design
**Mục tiêu:** triển khai 2 Residual G (sau khi commit `7b06188` đã push+deploy+verify `/version` LIVE). Nghiên cứu bằng workflow trước, chỉ vá nếu là defect thật.

**Đã làm:**
- **NGHIÊN CỨU (workflow 2-agent, chạy code thật):**
  - **#2 cờ suy_doan_don_vi cạnh <40 → KHÔNG phải bug (by-design), no-fix.** `_unit_ambiguous_sect` đòi `lo>=40` là ĐÚNG ngữ nghĩa: raw<40 → hiểu-mm = cạnh <4cm phi thực → chỉ cm khả dĩ → không nhập nhằng để cảnh báo. Tiết diện thật vùng đó (KT GiaLộc dầm 22×30, dm 22×50) đều resolve đúng cm, vô hại. Nới cờ sẽ ngập false-alarm. (Ghi chú vặt: mệnh đề `and hi <= 2000` dòng ~212 là dead-code, không đụng.)
  - **#1 recall SL 9T KT → BUG THẬT (đã vá).** `liet_ke_so_luong()` chỉ trả 6 mục (Hộp inline), **bỏ sót cả bảng thống kê cửa**: d2=9, d3=20, d10=18, d4=11, dkt=36… Nguyên nhân: `_QTY_RE` đòi từ-khoá+số trong CÙNG entity, nhưng bảng đặt tiêu đề cột 'TỔNG' và ô số ở entity RIÊNG. Ground-truth MẠNH (cột TỔNG của chính bản vẽ).
- **TRIỂN KHAI (hướng user chốt = đọc cột TỔNG, gated fail-silent):** `_build_schedule_qty_index(texts)` (`tools_core.py`) ghép mã↔số theo HÀNG (y-band) + CỘT (khớp header 'TỔNG'). Gate CHỐNG BỊA: ≥5 cặp DUY NHẤT/cột, |Δy| chặt, mã ký-hiệu sát bên TRÁI cột tổng; block không sạch → BỎ (thà thiếu hơn bịa). Merge vào `qty_index` (dedup label_norm, không đè inline/spatial). Nguồn 'bảng thống kê (cột TỔNG)' + handle đối chiếu.
- **VALIDATE ĐA-FILE (probe thật trước khi code):** dương KT 9T (bảng cửa @923022 → 22 mã, LOẠI 8 bảng thép lạc); ÂM KC/KT Gia Lộc + rachmop → 0 mã bịa (giữ port-faithfulness `test_qa_data`).

**Kết quả test:** `test_takeoff_chong_bia.py` **177/177** (nhóm mới **[V]** 10 ca: 9T KT d2=9/d3=20/d10=18/d4=11/sk2=16 + end-to-end `tra_cuu_so_luong` + ÂM KC GiaLộc 0 bịa & giữ 94 mục) · `test_qa_data.py` **129/129** (port KHÔNG đổi) · `check.sh` PASS.

**Bài học:** #1 lộ đúng nhờ probe đa-domain; fix bảng-cột NHẠY LAYOUT → validate đa-file + gate fail-silent (thà under-recall hơn bịa) là bắt buộc theo ethos chống-overfit. #2 xác nhận "không phải mọi finding subagent là bug" — nghiên cứu trước, no-fix khi by-design.

**Đang chờ:** ⚠ CHƯA commit đợt residual — chờ user duyệt (rồi push/deploy/verify như đợt trước). Residual còn: window S-code |Δy| lỏng hơn (đã đọc nhưng nên đối chiếu thêm bản vẽ khác layout trước khi tin tuyệt đối); robustness H–L.

---
## Session 2026-07-11 — Task G: TEST ĐỐI KHÁNG ĐA-DOMAIN + vá 3 bug tầng tổng hợp/đọc
**Mục tiêu:** đầu việc G (ROADMAP) — mở rộng test đối kháng đa-domain (KC/KT 9T + hạ tầng) để khoá regression cho A–F. User giao tự chọn task → chốt G (đúng ưu tiên #1 an toàn/KPI ~0% bịa; H–L là ops, xếp sau "giao rộng").

**Đã làm:**
- **PROBE (workflow 6-agent, chạy engine THẬT offline):** 5 agent probe song song (KC 9T · KT 9T · rachmop · gap-check Gia Lộc · overfit-hunter) → 1 agent tổng hợp. Phát hiện 3 vector nghi ngờ ở tầng TỔNG HỢP/ĐỌC-DIỆN-TÍCH (lõi chống-bịa/existence/cm-mm/lỗ-cửa vẫn vững).
- **TỰ KIỂM CHỨNG (repro độc lập — KHÔNG chỉ tin subagent):** chạy `tong_hop_khoi_luong()` + regex trên KT/KC Gia Lộc thật, xác nhận:
  - **BUG A (cao, LIVE):** `tong_phu` GỘP thép tròn+thép hình thành 1 số kg — KC **67759.7**=67370.7+389.0, KT **4110.7**=564.8+3545.9. Trùng đúng con số rule 8b (mcp_bridge:164) CẤM; rule 11 lại bảo LLM "nêu tong_phu" → mâu thuẫn code-vs-policy, tái sinh lỗi bịa lịch sử ở tầng CODE.
  - **BUG C (thấp-TB, LIVE):** `tong_phu` gộp 'Số lượng' dị loại (cửa+dầm+cột+thép) → **835**/191 bộ/cái vô nghĩa + double-count dầm chia đoạn.
  - **BUG B (TB→latent):** `_rs_dien_tich_ghi_san` dùng regex thô đọc mật độ '16 cọc/1m2' thành diện tích=1 (BỊA sàn) — parity gap với `_build_stated_areas` (có lookbehind). Cơ chế THẬT nhưng **live-scan = 0/4 file** → tiềm ẩn, không thổi phồng.
- **VÁ (`tools_core.py`):** (A) tách `loai` thép tròn/hình ("Khối lượng thép tròn"/"...hình") để tong_phu KHÔNG nhóm chung → hiện 2 tổng RIÊNG (khớp rule 8b "nêu riêng"); (C) thêm "Số lượng" vào `_khong_cong`; (B) resolver dùng `_STATED_M2_RE` (lookbehind) + normalize `/\s+`→`/`, giữ case hợp lệ "634m2"=634.
- **TEST (khoá regression + đa-domain):** nhóm mới **[R]** (KC/KT không gộp thép) · **[S]** (parity density KHÔNG bịa=1, "634m2"=634) · **[T]** (không gộp Số lượng, SL vẫn trong bảng) · **[U]** (9T KIẾN TRÚC 193k obj: recall 16 nhãn diện tích đủ handle + mã cửa giả→vàng) · **I.5/I.6** (9T KC: F ước 10 tầng=**21.12** + C999→vàng + typical 3.3m). Hoist 9T KC nạp **1 lần** (trước nạp 2 lần, phí ~53s) → gate ~không đổi dù thêm 9T KT.

**Kết quả test (ĐỀU XANH):** `test_takeoff_chong_bia.py` **167/167** (was 149; +18 assertion, nhóm A-U) · `test_qa_data.py` **129/129** · `harness/scripts/check.sh` = **HARNESS GATE: PASS** (21 tool + no-key).

**Bài học:** bug bịa có thể tái sinh ở tầng CODE ngay cả khi guard tầng PROMPT đã có (rule 8b) — probe đa-domain + repro độc lập bắt được; đối kháng subagent phải TỰ chạy xác nhận (B bị subagent nói "live" nhưng thực ra latent). Overfit thường ở TẦNG TỔNG HỢP (gộp theo loại/đơn vị) chứ không chỉ ở đọc.

**Đang chờ / bước tiếp:** ⚠ CHƯA commit — chờ user duyệt (chưa push/deploy). Residual (vòng sau): recall SL 9T KT cần ground-truth độc lập; robustness H–L (429/503, file lớn, TTL, session, keep-alive); trước giao rộng: audit an toàn đa-agent + xin 3-5 bản vẽ đơn vị khác + KPI tỷ lệ bịa.

---
## Session 2026-07-10 (CHỐT SỔ) — Củng cố B/C/D/F + clean-state
**Tóm tắt phiên:** làm 4 đầu việc củng cố ROADMAP theo cùng quy trình (probe → design panel → triển khai → kiểm chứng đối kháng loop-until-dry → test → docs → commit/push/deploy/verify). Chi tiết từng task ở các entry (b)/(c)/(d) bên dưới.

**Đã làm (4 task, mỗi task commit riêng + live + verify `/version`):**
- **B — Trừ lỗ cửa/cửa sổ** (`lo_cua` cho xây/trát). Commit `7095614`. Adversarial: 4 bug thật → vá.
- **C — Liệt kê diện tích ghi sẵn** (`liet_ke_dien_tich_ghi_san`, tool #21). Commit `4113a8a`. Adversarial: bịa đuôi thập phân + density-space → vá.
- **D — Ứng viên gợi ý** (kg/bộ + số đo, `ung_vien` trong inputs_thieu, 1-click). Commit `4168708`. Adversarial: garble bộ→bé → vá.
- **F — Ước cao cột theo cao độ** (1 tầng, cờ giả định; móng resolver riêng). Commit `a775825`. Adversarial: 0 lỗ (tách móng ở tầng công thức).
- (E — gợi ý m³ ghi sẵn: ĐÃ XONG từ trước = `goi_y_ghi_san`; user chốt bỏ qua, làm F.)
- Chốt sổ: cập nhật số cũ trong `clean-state-checklist.md` (20→21 tool, 76→149 test); thêm `.gitignore` cho artifact test (kichban_*_ketqua, verify*_chunks); rà `feature_list.json` (A-F done, G planned, H-L partial); **KHÔNG có `specs/specs.json`** (demo 2 dùng feature_list.json thay specs/ — đúng AGENTS.md).

**Kết quả test (clean-state cuối phiên, ĐỀU XANH):** `test_takeoff_chong_bia.py` **149/149** (17 nhóm A-Q) · `test_qa_data.py` **129/129** · `harness/scripts/check.sh` = **HARNESS GATE: PASS** (import + 21 tool + no-key). Working tree TRACKED sạch, đã push hết, HEAD `a775825` LIVE. (Lưu ý: dùng SCRIPT runner, KHÔNG pytest — pytest crash do test đổi sys.stdout lúc import.)

**Quyết định dài hạn (đã lưu memory):** quy trình củng cố chuẩn (probe→design→adversarial verify) + gotcha TCVN garble (heuristic phải bền garble).

**Đang chờ / bước tiếp:** **G** (mở rộng test đối kháng đa-domain trên KC/KT/9T — khoá regression) + robustness **H** (model fallback 429/503), **I** (chặn file lớn sớm), **J** (dọn file TTL), **K** (tách session), **L** (keep-alive). Dự toán chi phí = HOÃN (chờ đối tác chốt). Trước khi giao rộng: audit an toàn đa-agent + xin 3-5 bản vẽ đơn vị khác + KPI tỷ lệ bịa.

---
## Session 2026-07-10 (d) — Task F: ƯỚC CHIỀU CAO CỘT theo cao độ
**Mục tiêu:** đầu việc F (ROADMAP) — ước "cột cao 1 tầng" ở luồng takeoff lẻ (trước luôn bắt nhập tay). (E đã xong từ trước = goi_y_ghi_san; user chốt bỏ qua E, làm F.)

**Đã làm:**
- **PROBE:** KC typical_floor_h=3.6m (n_tang 2); 9T 3.3m (n_tang 10). `_loai_tu_ban_ve`: C1/C4 loai=[] + mã c<digit>; DM-1={dam}; M1/D1 không phải cột.
- **Nghiên cứu (design panel 3 lens):** CHỐT tách MÓNG ở tầng CÔNG THỨC — `the_tich_be_tong_mong` đổi input chieu_cao sang resolver RIÊNG `_rs_chieu_cao_mong` (luôn hỏi) → móng KHÔNG BAO GIỜ ước, tất định, không phụ thuộc nhãn. `_la_cot` là phòng-thủ-chiều-sâu trong `_rs_chieu_cao_cot`.
- **Triển khai (`tools_core.py`):** `_la_cot(ma)` (nhãn thắng prefix) + `_rs_chieu_cao_cot` (thêm nhánh ước = typical_floor_h×1000mm, cờ gia_dinh_cao_tang/nguon suy_tu_cao_do/chua_chac) + `_rs_chieu_cao_mong`. Propagate `gia_dinh_cao_tang` vào da_co; ghi_chu TÁCH 'GIẢ ĐỊNH 1 tầng' khỏi 'GÁN VỊ TRÍ' (co_gan_dim = nguon=='gan_vi_tri'). Docstring `mcp_server` + SYSTEM_PROMPT.
- **CHỐNG BỊA (suy đoán CÓ CỜ, được phép):** ước LUÔN gắn cờ + nguồn + chua_chac + câu ghi_chu 'xác nhận nếu cột cao khác'; đối tác cấp → override sạch; KHÔNG levels → hỏi (không bịa mặc định); móng KHÔNG ước; `_la_cot`+sai_loai chặn không-cột.
- **⚠ ĐỔI HÀNH VI:** test cũ B 'C1 chưa cấp cao → thieu' NAY thành 'tính được (ước 1 tầng)' → cập nhật. Test D nhóm P.3 (chieu_cao cột không có ứng viên) đổi sang kiểm DISPATCH trực tiếp (vì F nay điền chieu_cao → không còn ở inputs_thieu).
- **KIỂM CHỨNG ĐỐI KHÁNG (3 lens/29 probe) = 0 lỗ hổng** (F1-F7). Móng không ước kể cả mã cột thật C-3; override sạch; đa-cờ 9T lộ đủ.

**Kết quả test:** `test_takeoff_chong_bia.py` **149/149** (nhóm mới **[Q]** 14 ca) · `test_qa_data.py` **129/129** · 21 MCP tool.

**Bài học:** tách hàng rào ở tầng CÔNG THỨC (resolver riêng cho móng) tất định hơn phân biệt trong 1 resolver dùng chung; đổi-hành-vi phải rà MỌI test gọi công thức đó (bắt được cả B lẫn P.3 interaction D↔F).

**Đang chờ:** commit F + push (C+D `4168708` đã live); còn G (test đối kháng đa-domain) + robustness H/I/J/K/L.

---
## Session 2026-07-10 (c) — Task D: ỨNG VIÊN GỢI Ý cho input thiếu (1-click)
**Mục tiêu:** đầu việc D (ROADMAP) — tự nêu ứng viên 'X kg/bộ' / số đo gần mã để đối tác 1-click xác nhận (feedback "AI hỏi nhiều").

**Đã làm:**
- **PROBE:** KT có ghi chú '[67FFC] khung inox 304 ... (1 bé):13.42m= 8.62 kg' = ứng viên kg/bộ VÀNG (khớp inox S1 task B). Cạnh đó '4,35kg' (không /bộ), nhiều 'TỔNG KHỐI LƯỢNG (kG): X' (tổng, nhiễu), 'xà gồ ... 2472.64kg' (tổng). Dim cột C1 có 'ngang=220' (tiết diện) lẫn nhiều '0.0' (nhiễu).
- **Nghiên cứu (design panel 3 lens):** chốt DISPATCH THEO RESOLVER (`rs_name`) không theo 'ten' — vì `chieu_cao` dùng cả `_rs_chieu_cao_cot` (cao độ, KHÔNG gợi: dim 220 là tiết diện không phải chiều cao) lẫn `_rs_bs_only` (tường, gợi được).
- **Triển khai (`tools_core.py`):** `_ung_vien_kg_moi_bo` (verbatim 'X kg', loại 'TỔNG', cờ per-unit `_KG_PU_RE`='(1 …)'/'kg/bộ', KHÔNG proximity) + `_ung_vien_dim` (dim gần mã, đòi code_toks, loại 0.0, LUÔN 'thap'+khoảng cách) + `_ung_vien_cho_input` (dispatch). Gắn `ung_vien` vào từng `inputs_thieu[i]` (chỉ khi non-empty → additive). Docstring `mcp_server` + SYSTEM_PROMPT luật ↳.
- **CHỐNG BỊA:** ứng viên KHÔNG vào vals/da_co, KHÔNG lật co_ket_qua/can_bo_sung; CHỈ `inputs_bo_sung` (đối tác xác nhận) mới tính (đường cũ 137.92 không đổi). kg KHÔNG khẳng định thuộc mã nào (chống bịa liên kết kg-mã, giữ luật task B).
- **KIỂM CHỨNG ĐỐI KHÁNG (1 vòng, 3 lens 27 probe) = 0 lỗ hổng** (D1-D7 giữ). Test [P] tự bắt bug garble 'bộ'->'bé' (perl-unit dùng bare '\bbo\b' → sai) → vá `_KG_PU_RE='(1 …)'` bền garble + không nhầm '02 bộ bản lề' (phụ kiện).

**Kết quả test:** `test_takeoff_chong_bia.py` **134/134** (nhóm mới **[P]** 14 ca) · `test_qa_data.py` **129/129** · 21 MCP tool (D KHÔNG thêm tool — ứng viên nằm trong response `tinh_dai_luong`).

**Bài học:** garble TCVN 'bộ'->'bé' lặp lại (như 'diÖn tÝch' ở C) → heuristic từ-khoá phải BỀN garble; dispatch theo RESOLVER (không theo tên input) tránh gợi sai cho cao-độ-cột.

**Đang chờ:** commit D + push (C `4113a8a` đã commit CHƯA push); còn F (ước cao cột theo cao độ), G (test đa-domain) + robustness H/I/J/K/L.

---
## Session 2026-07-10 (b) — Task C: LIỆT KÊ DIỆN TÍCH GHI SẴN
**Mục tiêu:** nghiên cứu chi tiết + triển khai đầu việc C (ROADMAP) — liệt kê nhãn 'X m²' ghi sẵn (verbatim + handle) để đối tác đối chiếu/cấp diện tích sàn.

**Đã làm:**
- **PROBE file thật TRƯỚC (⚠ ROADMAP yêu cầu):** KT Gia Lộc có ~17-20 nhãn m² HỖN TẠP (mái 634, sàn 591/545, sơn 117/44.5/38.1, tường 77.5, granit 52/30/22, trống 67/22.7/18/11 [garbled 'diÖn tÝch'], vách 3.3); KC có 'mật độ 16 cọc//1m2' NHIỄU + 'diện tích 7,04 m2' THẬT; KC 9T = 0 nhãn; hạ tầng 9 nhãn 'S=…m2'. → KẾT LUẬN: nhãn KHÔNG đều là 'sàn' → phải liệt kê verbatim, KHÔNG phân loại.
- **Nghiên cứu (design panel 3 lens: chống-bịa/UX/regex):** chốt hợp đồng mirror `stated_vol`.
- **Triển khai (`tools_core.py`):** `_build_stated_areas` + `self.stated_area` + `_STATED_M2_RE` + `_DT_KW_RE`; method `liet_ke_dien_tich_ghi_san` (trả {co_du_lieu, so_nhan, so_co_tu_khoa, danh_sach[{text,m2,handle,layer,co_tu_khoa_dien_tich}], goi_y khi 0, ghi_chu}, KHÔNG có field tổng). Tích hợp `tong_hop_khoi_luong` loại 'Diện tích (ghi sẵn)' + `_khong_cong` (KHÔNG cộng gộp mái+sơn+granit). MCP tool #21 + SYSTEM_PROMPT luật 14.
- **CHỐNG BỊA:** không khẳng định 'sàn', không suy hình học (0 nhãn → gợi ý đối tác CẤP), không cộng gộp; lọc mật độ + đuôi thập phân; mã DM2/mm2 tự loại; KHÔNG min (giữ 0.12m²).
- **KIỂM CHỨNG ĐỐI KHÁNG (loop-until-dry):** test [O] tự bắt **bug BỊA đuôi thập phân** ('117m2/44,5m2' → bịa 4.5/8.1) → vá regex `(?<![/.,\d])`. Vòng 1 (3 lens) bắt **density-space** ('16 cọc/ 1m2' → bịa 1.0) → vá normalize `'/\s+'→'/'`. Vòng 2 (2 lens) xác nhận MỌI vector BỊA đã kín; 3 ca còn lại là DROP-class (comma-no-space/slash-area/dedup) — an toàn (không bịa) + verbatim giữ đủ + không xuất hiện trên file thật → GHI CHÚ giới hạn (thất bại phải lộ), KHÔNG vá (fix mong manh).

**Kết quả test:** `test_takeoff_chong_bia.py` **120/120** (nhóm mới **[O]** 15 ca) · `test_qa_data.py` **129/129** · `check.sh` **PASS** (21 MCP tool).

**Bài học:** probe TRƯỚC khi thiết kế là quyết định (data thật cho thấy nhãn hỗn tạp → chốt "không phân loại"); test tự bắt bug bịa số thập phân trước cả adversarial → viết test-với-số-kỳ-vọng đáng giá.

**Đang chờ / bước tiếp:** commit + push (CHƯA — chờ user); D (ứng viên kg/bộ 1-click), F (ước cao cột), G (test đa-domain) + robustness H/I/J/K/L.

---
## Session 2026-07-10 — Task B: TRỪ LỖ cửa/cửa sổ (xây tường & trát)
**Mục tiêu:** nghiên cứu chi tiết + triển khai đầu việc B (ROADMAP) — trừ lỗ cửa/cửa sổ khi tính xây tường & trát.

**Đã làm:**
- **Nghiên cứu (workflow design panel 3 lens):** chống-bịa / hợp-đồng-UX / QS-xây-dựng → CHỐT hợp đồng: `lo_cua` (list) trong `inputs_bo_sung`, chỉ cho `xay_tuong` + `dien_tich_trat` (cờ `tru_lo`). Nguyên tắc mirror INOX: CODE cấp phần verify được (R×C), ĐỐI TÁC khai phần không tự-liên-kết (mã+SL lỗ) — hệ KHÔNG tự đoán cửa nào thuộc tường nào.
- **Triển khai (`tools_core.py`):** `_resolve_lo_cua` + `_sl_hop_le` + tích hợp trong `tinh_dai_luong`. Mỗi lỗ: `{ma,sl}` (tra `door_size_index` confident, có handle) HOẶC `{rong,cao,sl}` (mm, đối tác cấp; nhận cả `sl`/`so_luong`). net = gross − Σ(R×C×SL)×(be_day/1e9 | so_mat/1e6). KHÔNG cộng reveal/bệ cửa (lộ ghi chú). Cập nhật docstring `mcp_server.py` + SYSTEM_PROMPT `mcp_bridge.py` để Gemini biết dùng + trình bày gross→net.
- **Backward-compat tuyệt đối:** không `lo_cua`/`[]` → số CŨ y hệt, KHÔNG field mới → 76 test cũ không đổi.
- **KIỂM CHỨNG ĐỐI KHÁNG (loop-until-dry, workflow đa-agent):** Vòng 1 (4 lens) bắt **4 bug THẬT** (đã chạy xác nhận): (1) over-count lách bằng tách 1 mã thành nhiều entry (36 d2 > 18); (2) net làm tròn về 0.0 vẫn báo co_ket_qua=True; (3) `sl` vs `so_luong` mâu thuẫn bị bỏ im lặng; (4) sl khổng lồ → so_lo là int 300 chữ số. → VÁ cả 4 (cộng dồn per-code canonical; gate net<=0 SAU làm tròn; block khi sl≠so_luong; trần `_SL_LO_MAX=100000`). Vòng 2 (3 lens, 25+ ca) = **DRY, 0 lỗ hổng** — mọi biến thể hoa/thường/gạch/space/unicode/NaN/overflow đều BLOCK an toàn.

**Kết quả test:** `test_takeoff_chong_bia.py` **103/103** (nhóm mới **[N]** 27 ca trừ lỗ, gồm N.4 hardening 4 bug) · `test_qa_data.py` **129/129** (không regression) · `harness/scripts/check.sh` = **HARNESS GATE: PASS**.

**Quyết định thiết kế (đã cân nhắc):** (1) chuỗi số "900"→900 GIỮ (đồng nhất `_nd` toàn hệ, Gemini hay gửi số dạng chuỗi) — KHÔNG coi là lỗi kiểu; (2) mode kích-thước-trực-tiếp KHÔNG có trần `_door_qty_for` (dims+SL đối tác cấp, không verify được) — chỉ trần-mỗi-lỗ 100000 + gate net>0 + cờ `confident=False` minh bạch; (3) so sánh `==trần` được PHÉP (đối tác có thể có đúng N lỗ), `trần+1` chặn.

**Đang chờ / bước tiếp:** commit (CHƯA commit — chờ user duyệt); các củng cố treo còn lại C/D/F/G + robustness H/I/J/K/L (xem `feature_list.json` + `ROADMAP_DEMO2.md`).

---
## Session 2026-07-09 — Chốt demo 2 + củng cố + tích hợp Harness
**Mục tiêu:** phản hồi feedback đối tác (chọn demo 2, thêm tính năng inox) → củng cố → tích hợp bộ Harness cho demo 2.

**Đã làm:**
- **Quyết định chiến lược:** đối tác test 2 demo → ưng demo 2. Rà soát bằng chứng (tốc độ do MODEL flash-vs-pro, không phải kiến trúc; "thất bại" demo 2 là giới hạn CHUNG/chống-bịa). → **CHỐT demo 2 là sản phẩm chính, DỪNG demo 1.** "2 demo cân bằng" NGHỈ.
- **Vá parity cm/mm + đọc bảng cột nhà 9T** (`_build_section_index` ghép tọa độ + ngưỡng 130 + cờ mơ hồ): 9T C-3 = 80×80cm → 23.04 m³ (khớp demo 1); Gia Lộc 4.704 m³ không đổi. `2a90a36`.
- **Endpoint `/version`** verify deploy qua HTTP. `e870074`.
- **Tính năng INOX = SL(đọc)×kg/bộ(đối tác cấp)** (feedback): inox S1 = 16×8.62 = **137.92 kg**. `c034312`.
- **Kiểm chứng ĐỐI KHÁNG (workflow đa-agent):** bắt lỗ `inf`/tràn số/`bool` lọt cổng ra "Infinity kg" → hardening (`_nd` từ chối bool/inf/nan + `math.isfinite` + kiểm KẾT QUẢ hữu hạn). `c034312`.
- **Vá 3 lỗ BỊA SỐ** (workflow roadmap chạy code): mã toàn chữ "GHOSTINOX", "thể tích sàn" tự vơ diện tích, "thể tích inox" lệch đại lượng. `4c597f3`.
- **Củng cố A + E:** tổng phụ theo (loại,đơn vị) + gợi ý m³ ghi sẵn (đào đất thiếu → nêu "ĐÀO MÓNG 860 M3"). `dd8d971`.
- **Tài liệu chiến lược:** ROADMAP_DEMO2 (hoãn dự toán chi phí `fe4972c`), KE_HOACH_TONG_QUAT_HOA (độ phủ vs độ an toàn, KPI 0% bịa `dd8d971`), NGHIEN_CUU_AI_TU_HOC (tự học an toàn `2f51a8b`).
- **Tích hợp HARNESS:** tạo `harness/` 12 file (project-overview, tech-stack, feature_list.json 27 đầu mục, AGENTS, rubric, quality-document, clean-state-checklist, session-handoff, claude-progress, README, benchmark_questions, scripts/check.sh). `de61ac5`.

**Kết quả test:** `test_takeoff_chong_bia.py` **76/76 PASS** (nhóm A-M) · `test_qa_data.py` đọc **129/129 PASS** · `harness/scripts/check.sh` = **HARNESS GATE: PASS** (20 MCP tool + no-key). Deploy live, `/version` verify từng commit.

**Quyết định dài hạn:** (1) demo 2 = sản phẩm chính, bỏ demo 1; (2) phạm vi = ĐỌC + tính KHỐI LƯỢNG, dự toán chi phí HOÃN chờ đối tác chốt; (3) ưu tiên ĐỘ AN TOÀN > độ phủ (KPI ~0% bịa); (4) AI tự học (nếu làm) = học CÁCH ĐỌC không học SỰ THẬT, hóa-cứng thì người duyệt.

**Bài học:** TÔI từng đẩy "dự toán chi phí (thành tiền)" lên P0 dựa trên tầm nhìn gốc dự án — nhưng đối tác CHƯA yêu cầu và phạm vi vốn "chưa chốt" → sai ưu tiên, user bắt đúng. → Phân biệt "đối tác đã yêu cầu" vs "tôi suy từ tầm nhìn"; không tự nâng scope hoãn thành hướng chính.

**Đang chờ / bước tiếp:** củng cố treo B/C/D/F/G + robustness H/I/J/K/L (xem `feature_list.json` + `../ROADMAP_DEMO2.md`); trước khi giao rộng: audit an toàn đa-agent + xin 3-5 bản vẽ đơn vị thiết kế khác + dựng KPI "tỷ lệ bịa".
