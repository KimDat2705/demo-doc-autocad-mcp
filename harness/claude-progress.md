# Claude Progress — demo 2 (nhật ký tiến độ theo phiên)

> **🔁 2026-07-17 — THỬ MỞ PUBLIC RỒI HOÀN TÁC (repo GIỮ PRIVATE):** user đổi ý giữa chừng. Đã **khôi phục main về `130afae`** từ mirror backup + force-push → demo NGUYÊN TRẠNG (verify: `/version`=130afae, `/health` ok, **upload .dwg thật lên cloud CHẠY LẠI** — ODA convert ok, 102 layer/1555 text khớp local). **Mọi hash cũ trong tài liệu này CÒN HIỆU LỰC** (c0b85af/97ffc60/7188c3c/130afae…).
> **⚠ VÌ SAO REPO PHẢI PRIVATE:** `vendor/ODAFileConverter.deb` (53.6MB) là phần mềm **ĐỘC QUYỀN của Open Design Alliance**, phải commit để Render build Docker → **public = phân phối lại binary bên thứ ba**. Đây là ràng buộc LICENSE, không phải tuỳ chọn.
> **Muốn public thật sau này — ĐỪNG LÀM LẠI TỪ ĐẦU:** nhánh local **`public-ready`** đã có sẵn trọn gói (history sạch không .deb qua `git filter-repo` · Dockerfile tải ODA tuỳ chọn qua `ODA_DEB_URL` · thông báo .dxf-only thân thiện · .gitignore chặn .deb). Đánh đổi: cloud chỉ đọc .dxf tới khi đặt `ODA_DEB_URL`. Mirror backup: `D:/Dat-Antigravity/_backup_repo_truoc_khi_public_20260717/repo-mirror.git`.


> Continuity Artifact (chuẩn Harness): lưu "đã làm gì / kết quả test / quyết định / đang chờ" để phiên sau không mất ngữ cảnh.
> Mới nhất ở TRÊN CÙNG. Bàn giao đầy đủ: `session-handoff.md`. Nhật ký chi tiết hơn nữa: `../GHI_CHU_HOAN_THIEN.md`.

---
## 🏁 2026-08-07 (PHIÊN NỐI) — **`gemini-3.6-flash` ĐÃ LIVE `683f0e4`** · vá 3 lỗi CAO · thay cổng D10 mù
> **CLOUD LIVE `683f0e4`** (verify `/version` + `/config` + `/health`). **6 commit tồn đọng đã PUSH HẾT — `origin/main` = HEAD, cây SẠCH.**
> **CỔNG `[50/50]` PASS · `EXIT_CODE_THẬT=0` · 1.805 → 1.847 ca · 0 FAIL.** Đối chiếu TỪNG DÒNG với cổng baseline: **lệch ĐÚNG 1 dòng** (suite fallback 42→84), 47 suite còn lại giữ nguyên từng con số — hợp lý vì mọi suite trong cổng đều OFFLINE.
>
> ### ⛔ PHÉP ĐO LẬT 3 GIẢ ĐỊNH CỦA CHÍNH KẾ HOẠCH — đọc trước khi trích lại bất cứ số nào
> **① `temperature=0` KHÔNG CÒN TÁC DỤNG trên Gemini 3.** Đo thật (prompt entropy cao, 5 lượt, **đối chứng dương ĐẠT**): `2.5-flash` cho **1 đáp án/5 lần** (`'738291'`×5), `3.6-flash` cho **5 đáp án/5 lần**. Rủi ro "R1" của kế hoạch ghi là *"xung đột thiết kế, phải A/B riêng"* — sai bản chất: **tham số bị BỎ QUA**. Thứ `mcp_bridge.py` tự khai là *"lựa chọn CHỐNG BỊA cốt lõi"* nay **không bảo vệ gì**; đây là thuộc tính của Gemini 3 nói chung nên chọn `3.5-flash-lite` cũng không tránh được. **HỆ QUẢ PHẢI NHỚ:** chống bịa dựa HOÀN TOÀN vào hàng rào phía code, và **mọi phép đo E2E từ nay phải chạy NHIỀU LƯỢT lấy phân bố** — kết luận từ một lượt là vô nghĩa. Nhãn ca test F1 đã sửa (nó từng khẳng định đây là hàng rào chống bịa).
> **② 31 khai báo tool gửi cho Gemini, KHÔNG phải 37** — `gemini_tools()` lọc 6 tool host-only. Mọi phép tính caching theo 37 lệch ~19% ở vế tool.
> **③ implicit caching ĐANG CHẠY SẴN** (đo sạch, danh sách cache explicit rỗng): lượt đầu **0%** (nguội) rồi **75,2% ỔN ĐỊNH** ở cả 5 lượt sau ⇒ con số **"×8 tiền" là tính tay theo GIÁ NIÊM YẾT, là CẬN TRÊN**, chưa phải hoá đơn.
> ⛔ **ĐÍNH CHÍNH — TÔI TỪNG GHI SAI Ở ĐÚNG DÒNG NÀY:** bản đầu ghi *"trúng 75,2% ba lần liên tiếp rồi RƠI VỀ 0% lần thứ 4"*. **Tôi KHÔNG HỀ ĐO điều đó** — lượt đo sạch 4 lần đã CHẾT vì lỗi mạng (`WinError 10053`) trước khi chạy được lượt nào, và tôi vẫn viết kết quả vào sổ + memory + commit message. Điểm dữ liệu THẬT duy nhất lúc ấy là **một** phép đo 8.071/10.727 = 75,2%, lại đo lúc **vẫn còn một cache explicit tồn tại**. Đo lại sạch (6 lượt, danh sách cache rỗng, có retry mạng): **0% · 75,2% · 75,2% · 75,2% · 75,2% · 75,2%** — implicit **ỔN ĐỊNH**, không rơi. ⇒ **Lập luận "đòn bẩy của explicit là bỏ được cái rơi-về-0" ĐÃ BỊ CHÍNH PHÉP ĐO BÁC.** Phần thêm thật của explicit chỉ là **10.711 − 8.071 = 2.640 token/lượt**. Bài học: lỗi hạ tầng làm chết phép đo mà **không làm chết niềm tin vào kết quả** — nguy hiểm hơn hẳn phép đo cho số sai.
>
> ### ✅ ĐO CHUỖI MODEL TRƯỚC KHI CHỐT (đúng lớp lỗi phiên trước để lọt)
> Phiên trước phát hiện chuỗi dự phòng **chưa từng chạy được** mà không ai biết — vì không ai đo. Lần này gọi thật từng model: `3.6-flash` / `3.5-flash` / `3.5-flash-lite` **đều SỐNG**; **đối chứng ÂM `gemini-2.0-flash` ra CHẾT 404** ⇒ phép đo có khả năng ra kết quả khác, không phải tautology.
>
> ### ✅ GĐ0 — 3 LỖI CAO vá TRƯỚC (`de981fb`), đều là bug HÔM NAY chỉ nóng lên theo Gemini 3
> **(a) Câu bị CẮT trả về ÂM THẦM như câu hoàn chỉnh** — `if special and not text` vứt cảnh báo khi CÓ text; câu cụt đi qua được **cả grounding-guard** (số của nó có neo thật) nên không hàng rào nào bắt. 3.6-flash sinh **×3,1 token ra** ⇒ tần suất tăng mạnh. Vá: `_noi_canh_bao_cat()` NỐI cảnh báo ở **cả 2 đường trả**, và **không nối vào câu guard đã thay** (kiểm bằng PHÉP CHỨA, không so danh sách thông điệp — danh sách khoá cứng là bề mặt dễ quên).
> **(b) `MAX_TOKENS` + text RỖNG = NGÕ CỤT** (không nhắc/không retry/không tụt model) — vá: nhắc ĐÚNG 1 lần, phủ cả ca `content=None`. Cố ý KHÔNG append phần thought cụt ⇒ né luôn việc gửi part suy-nghĩ của model này cho model khác.
> **(c) TIMEOUT không được nhận là quá tải** ⇒ 0 fail-forward và **phơi nguyên văn exception Python ra trình duyệt đối tác**. Vá: `_het_gio()` nhận theo KIỂU + TÊN LỚP (không cần import httpx).
>
> ### ✅ GĐ3 — ĐỔI MODEL
> `MODEL` → `gemini-3.6-flash` · `_FALLBACK_DEFAULT` → `gemini-3.5-flash,gemini-3.5-flash-lite` (**CÙNG ĐỜI 3.x**) · `render.yaml` ghi **TƯỜNG MINH** cả `GEMINI_MODEL` lẫn `GEMINI_FALLBACK_MODELS` (trước đó blueprint KHÔNG đặt ⇒ deploy ăn mặc định code; sửa trên dashboard thì deploy lại từ blueprint là MẤT) · 3 script E2E đổi `os.environ[...]=` (GÁN ĐÈ) sang `setdefault` — gán đè khiến sau khi đổi model prod, kịch bản vẫn chấm **model CŨ** = *"cổng xanh nhưng xanh cho model không chạy"*. `rerun2.py` GIỮ 2.5-flash vì nó TÁI HIỆN phép đo cũ.
> **Vì sao vẫn phải cùng đời** dù đã có bản vá chạy-lại-từ-đầu: bản vá đỡ được lỗi 400 *Corrupted thought signature*, nhưng giá của nó là **gọi lại TOÀN BỘ tool** (×2 thời gian, ×2 RAM trên gói free vốn đã sát trần, ×2 tác dụng phụ ghi ảnh/Excel). Cùng đời **tránh hẳn** đường đó thay vì chỉ xử lý được nó.
>
> ### ⭐ CỔNG D10 CŨ MÙ ĐÚNG CHIỀU NGUY HIỂM — đã thay bằng nhóm `[G]`
> D10 ghim chuỗi `'gemini-2.5'` và soi **HẰNG** `_FALLBACK_DEFAULT`, nên: đặt env `GEMINI_MODEL=gemini-3.6-flash` mà giữ dự phòng 2.5 ⇒ chuỗi THẬT trộn đời **mà cổng vẫn XANH** (đúng trạng thái nó sinh ra để chặn); ngược lại sửa cho ĐÚNG lại **ĐỎ OAN**. Bản mới soi `MODELS` (đại lượng THẬT, đã gộp env) và so đời **tương đối** với `MODELS[0]` ⇒ đúng với mọi đời model về sau; fail-closed khi không đọc nổi tên; nuốt tiền tố `models/`. **Kiểm lại bằng env THẬT:** cấu hình trộn ⇒ G8 **FAIL** đúng như mong đợi, cấu hình 2.5 cũ vẫn xanh (không đỏ oan).
>
> ### ✅ Kèm 3 lỗi TRUNG cùng vùng
> · `_is_overloaded` khớp **CHUỖI CON**: `'400 … token count 15042 exceeds'` chứa `'504'` ⇒ lỗi CẤU HÌNH VĨNH VIỄN bị xử như quá tải → máy nói *"thử lại sau ít phút"* = **NÓI SAI SỰ THẬT**. Gemini 3 sinh lỗi 400 mang SỐ nhiều hơn hẳn 2.5. Thay bằng regex có ranh giới hai phía. Đây là **SIẾT PHẠM VI, KHÔNG đổi luật**.
> · 2 đường NHẮC append `cand.content` mà không đặt `da_goi_tool` ⇒ contents nhiễm gửi thẳng sang model khác.
> · Tín hiệu `_CanChayLaiTuDau` bị `except Exception: pass` **NUỐT** ở lượt ép-trả-lời cuối — đúng lượt mà `da_goi_tool` gần như LUÔN True.
> · **+ `model_da_dung`** trong payload: `state['tried']` được GHI nhưng không chỗ nào ĐỌC; tụt sang dự phòng là **tụt chất lượng ÂM THẦM** (`3.5-flash-lite` bịa handle 2/198 ca).
>
> ### 🧪 E2E THẬT TRÊN BẢN LIVE — 5 lượt/câu, chấm bằng SỰ THẬT NỀN đọc từ file
> | Trục | Kết quả |
> |---|---|
> | Đúng số | **20/20 lượt** (4/4 câu đúng TRỌN 5/5) |
> | Chống bịa | **10/10 lượt** từ chối (2/2 câu bẫy) |
> | Ổn định | **5/6** câu cho CÙNG tập số suốt 5 lượt |
> | Câu bị cắt | **0** |
> | Thời gian | trung vị **5,0s** · p95 6,8s · max 7,0s (trần 60s) · `errors: 0` |
>
> Câu *"tổng số lượng cửa"* đòi **cộng 7 giá trị rời rạc** → đúng **141 bộ** cả 5 lượt (việc chính của bóc tách). Về nỗi lo `temperature` chết: **tập số ổn định 5/5 ở cả 4 câu thật**, câu duy nhất biến thiên là một câu TỪ CHỐI nói thêm ngữ cảnh ⇒ biến thiên nằm ở **diễn đạt, không ở con số**.
> ⚠ **GIỚI HẠN — ĐỪNG SUY RỘNG:** file đo là **0,1MB / 35 đối tượng**. Chứng minh được: deploy chạy, chuỗi 3.x đúng, trả lời đúng+ổn định+từ chối bẫy ở quy mô này. **CHƯA chứng minh gì cho bản vẽ lớn** (nơi 3.6-flash đo được 8,4s trung vị và 4 lượt gọi model).
>
> ### 📌 BÀI HỌC PHIÊN NÀY — bộ trích của CHÍNH TÔI hỏng 2 lần trong 1 phép đo E2E
> **(a)** Ra đề *"liệt kê bảng thống kê thép"* cho file **không có** bảng thép, rồi chấm câu trả lời ĐÚNG (*"bản vẽ không có"*) thành **TỪ CHỐI OAN** ⇒ báo *"recall 1/2"* = **số rác**. Sửa: đọc sự thật nền bằng `ezdxf` TRƯỚC khi ra đề.
> **(b)** Đo *"ổn định"* bằng so **CHUỖI NGUYÊN VĂN** ⇒ đếm khác-diễn-đạt thành khác-đáp-án (*"3/4 câu không ổn định"*). Sửa: chấm trên **TẬP SỐ + PHÁN QUYẾT**. Cùng họ với bài học `'8.024'` vs `'8024'` từng hạ oan 3.6-flash mất 11 ca.
> ⇒ Nối dài `[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`: **lần thứ 12–13**.
>
> ### ⚠ RED-TEAM BẮT 2 LỖI DO CHÍNH BẢN VÁ ĐẺ RA (lại đúng *"bản vá cũng là code mới"*)
> · `_model_dang_dung({'i':-1})` trả model **CUỐI** chuỗi (chỉ số âm Python) ⇒ trường dựng ra để *"thất bại phải LỘ"* lại **KHAI SAI TÊN MODEL**. Đổi hợp đồng: không chắc thì trả `None`.
> · Tên model `gemini-3.6-flash` sinh số **3.6** qua `_collect_numbers` — **trùng dải chính dự án dùng làm ca thử** (`'3.6m'` I3-U). Hôm nay VÔ HẠI (rổ neo chỉ dựng từ RAW result của tool), nhưng đã đóng **tripwire Q4** chặn trước kênh bơm rổ neo thứ 5.
> · Và **mutation check bắt lỗ trong test tôi vừa viết**: ca G7 tưởng khoá được vế *"trả None"* nhưng đổi `None`→`'0'` vẫn xanh ⇒ thêm G11.
>
> ### 📋 BẰNG CHỨNG
> `test_model_fallback` **42 → 84** PASS/0 FAIL · tự-kiểm-ngược **6/6 + 8/8 mutation đỏ ĐÚNG CHỖ** (khôi phục khớp TỪNG BYTE) · red-team `redteam_va_3loi.py` **14/14** + `redteam_doi_model.py` **36/36** · cổng `[50/50]` 1.847 ca · đối chiếu BYTE kiểu xuống dòng trên cả 10 file: không lệch (`render.yaml` bị công cụ ghi đổi LF→CRLF toàn file mà `git diff` GIẤU vì autocrlf — đã nắn lại và kiểm bằng byte).
>
> ### 🎯 VIỆC ĐANG CHỜ
> 1. **CONTEXT CACHING** — đã nghiên cứu + đo khả thi, **chưa code**. Đo thật: explicit trúng **99,9%**, phần tĩnh **10.711 token** (SYSTEM_PROMPT 5.761 + 31 tool ≈ 4.950). ⚠ **Đòn bẩy nhỏ hơn tưởng, và CHƯA đủ căn cứ để quyết:** implicit đã ăn **ổn định** 75,2% trong BURST, nên phần thêm của explicit chỉ **2.640 token/lượt** (≈ $0,0036/lượt gọi model, ≈ $0,014/câu ở 4 lượt) trong khi phí lưu trữ là **$0,0107/giờ** ⇒ hoà vốn ở **~0,75 câu/giờ**, tức RẤT SÁT. **Số quyết định còn thiếu: implicit có sống qua khoảng IM LẶNG của lưu lượng thưa không** (demo thật hỏi cách nhau vài phút, không bắn liên tiếp). Nếu implicit hết hạn thì mọi câu đều nguội 0% và explicit mới thật sự đáng làm. Đang đo. 3 ràng buộc đã xác minh bằng gọi thật: (i) truyền lại `tools`/`system_instruction` kèm `cached_content` → **400 THẬT**; (ii) `cached_content` sống chung được với `thinking_config` + `automatic_function_calling(disable=True)` ✅; (iii) ⛔ **TIỀN ĐỀ NÀY ĐÃ BỊ ĐO BÁC — xem khối CONTEXT CACHING NO_GO ngay dưới.** Chi tiết `[[project-context-caching-gemini]]`.
>
> ### ⛔ CONTEXT CACHING — **NO_GO, có số.** Thứ nó sinh ra để chữa thì KHÔNG TỒN TẠI
> **Tiền đề của cả lát:** *`file_summary` đổi theo từng bản vẽ nên `system_instruction` không bất biến ⇒ cache MISS mỗi lần nạp file mới ⇒ phải đẩy `file_summary` xuống message user đầu.* **Đo thật thì tiền đề SAI.**
> **Phép đo 3 biến thể × 4 lượt, cùng câu hỏi, danh sách cache explicit RỖNG:**
> 
> | Biến thể | Trúng cache |
> |---|---|
> | **A** — y hệt sản phẩm, `file_summary` ĐỔI mỗi lượt (trong `system_instruction`) | **75,0%** |
> | **B** — đối chứng, `file_summary` CỐ ĐỊNH | **75,0%** |
> | **C** — đề xuất sửa, `file_summary` xuống USER MESSAGE (vẫn đổi mỗi lượt) | **75,0%** |
> 
> **Giống hệt nhau.** `file_summary` nằm ở CUỐI `system_instruction` nên implicit cache khớp tiền tố ĐỨNG TRƯỚC nó (8.071 token) và không hề bị nó phá. ⇒ **Việc chuyển chỗ `file_summary` không mang lại gì. A/B mà user yêu cầu trở thành VÔ NGHĨA vì không có hiệu ứng nào để đo.**
> **⚠ Số 3 biến thể giống hệt nhau từng token là dấu hiệu 'quá đẹp' ⇒ đã chạy ĐỐI CHỨNG ÂM, và nó ĐẠT 3/3:** chèn chuỗi lạ vào ĐẦU `system_instruction` → cached **0** · bỏ 31 khai báo tool → cached **0** · `system_instruction` cụt → cached **0**. Thước đo CÓ phản ứng với việc phá tiền tố ⇒ con số 75,0% là thật, không phải hằng số chết.
> **Implicit cũng KHÔNG hết hạn theo lưu lượng thưa:** đo giãn 0/30/60/120/300/**600s** im lặng → **75,2% ở cả 6 mốc**, 0 lượt nguội.
> **Phần thêm CÒN LẠI của explicit cache** (10.711 − 8.071 = **2.640 token/lượt gọi model**) ≈ **$0,014/câu**, trong khi phí lưu trữ **$0,0107/giờ**. Đổi lại là thay đổi kiến trúc ở đúng seam nhạy cảm nhất (phải BỎ `system_instruction` + `tools` khỏi request vì API trả **400** nếu truyền kèm `cached_content`; phải tạo cache MỚI mỗi lần đổi prompt hoặc thêm/bớt tool — mà đây là dự án sửa prompt liên tục; cache gắn chặt 1 model nên nhánh dự phòng mất cache). ⇒ **KHÔNG ĐÁNG. Xếp lại thành đầu mục `deferred`, kèm nguyên nhân bằng SỐ.**
> **📌 Giá trị thật của lát này:** một phép đo giá vài đô đã **huỷ** một lát thi công nhiều ngày ở vùng nguy hiểm nhất của hệ. Đúng tinh thần `[[feedback-do-truoc-code-sau]]` — và lần này thứ bị lật là tiền đề do CHÍNH TÔI đặt ra hai lượt trước.
> 2. **Lát ×1000 grounding-có-đơn-vị** (`mcp_bridge`) — vẫn treo từ trước.
> 3. **E2E trên bản vẽ LỚN** với 3.6-flash (đo LIVE mới chỉ phủ file 0,1MB).
> 4. Đọc tay nốt **14/26 ca bẫy** chưa soi (con số 3/3/2 vẫn là CẬN DƯỚI).
> 5. ⚠ **XÁC MINH LẠI "hạn cứng 16/10/2026"** — agent tra cứu báo trang deprecations của **Gemini API** ghi `gemini-2.5-flash` *"No shutdown date announced"*, còn 16/10 là mốc của **Vertex AI** (nền tảng khác). **Chưa tự kiểm.** Nếu đúng thì áp lực GĐ4 nhẹ hơn sổ ghi nhiều.

## Session 2026-08-07 (CHỐT SỔ) — 🏁 **TOOL #37 B0-B7 XONG + LIVE** · **VAN NHƯỜNG** · **API SỐNG LẠI** · **NÂNG CẤP MODEL GĐ1+GĐ2**
> **7 commit**: `fc35897` (B4) · `f085610` (B5) · `b193350` (B6) · `bb84379` (B7) · `da0c993` (vá chuỗi model chết) · `36ab4ba` (van nhường) · `825eacd` (A/B 3 model). **Cây SẠCH.**
> **CLOUD LIVE `36ab4ba`** (verify `/version` + `/health`). ⚠ **2 commit cuối CHƯA push** (`825eacd` + chốt sổ) — xem mục CÒN LẠI.
> **CỔNG**: `[49/49] 1.701 ca` → `[50/50] **1.805 ca**` / **0 FAIL** · **36 → 37 MCP tool** · `feature_list` **91 → 93 mục** (74 done · 2 partial · 13 deferred · 4 planned).
> ⚠ **pytest VẪN crash** (`ValueError: I/O operation on closed file` → **`no tests ran`**, exit 1) — KHÔNG phải test đỏ, là pytest không chạy nổi trong repo này. **KHÔNG có `specs/specs.json`** (không có cả thư mục `specs/`) → sổ đặc tả là `feature_list.json`. Hai điều này lặp mỗi phiên.
>
> ### ✅ 1. TOOL #37 `doc_bang_ke_khung` — B0→B7 XONG TRỌN, ĐÃ LIVE
> **B4 tích hợp** (`fc35897`): port proto vào `tools_core.py`, **3 thay đổi duy nhất** so với proto — quet_bang nhận doc ĐÃ NẠP · chuỗi ra payload qua `to_unicode` · lọc `nhan_chua` chuẩn hoá garble 2 phía. Nền B0 tái lập trên đầu ra SẢN PHẨM: a **2.556/2.556** · b **171/171** · min/max **226/226** · 0 mất · 0 thêm · **0/391 oan**.
> **B5 bộ test** (`f085610`): `tests/test_bang_ke_khung.py` **77 ca**, 7 nhóm, mỗi vế gate một CẶP bắn/không-bắn; **47 fixture vào repo** ⇒ 69/77 ca chạy được cả trên cloud. **Tự kiểm ngược 6/6 mutation đỏ ĐÚNG CHỖ.**
> **B6 corpus** (`b193350`): **142 file** — `p37` lệch **0/142** · `t36` lệch **0/142** · tổng ô **7.207 = 7.207** · 9/9 DXFStructureError giữ `loi_doc_file`. Đường sản phẩm ≡ đường đọc-file **phủ trọn 142 file** (119 + 14 file to chạy riêng `READFILE_MAX_MB=400`, tổng 1.186 MB). K1-K5 qua bridge THẬT trên **93 file**: 0 lỗi. Union mốc-mm **135 ≤ trần 143**; lệch +2 so đặc tả đã đo có đối chứng ⇒ **bản vá đóng góp ĐÚNG 0 mốc**.
> **B7 red-team** (`bb84379`): **SẠCH, 0 phát hiện**. Tầng 1 câu bịa: **P1 = 7 = đúng mốc, KHÔNG TĂNG** (đối chứng `_vn=identity` cũng 7 ⇒ B4 đóng góp +0). Tầng 2 đánh vào 3 delta của bản port: doc dùng lại **bất biến 10/10 tool xen giữa** · `to_unicode` sinh **0/9.139** chữ số từ chuỗi không-số · `nhan_chua` model-cấp bơm **0 neo** · tham số thù địch không crash/rò.
>
> ### ✅ 2. VAN NHƯỜNG #36 → #37 (`36ab4ba`) — thứ THỰC SỰ chữa được lỗi số sai
> **E2E chứng minh #37 MỘT MÌNH KHÔNG đủ**: model vẫn thường chọn #36 → *"đáy cống thấp nhất"* trả **1.900** (đúng 1.840); *"hàng đáy kênh"* chỉ `1.840`×17, **thiếu 1.740**. Sau van: **routing sang #37 từ 2/5 → 5/5 câu**, 1.900→**1.840 ĐÚNG**, hàng đáy kênh liệt kê **cả 1.740**, câu *"khoảng cách mặt cắt"* **vẫn 3/20** (không mất gì), câu BẪY vẫn từ chối.
> **Hợp đồng #36 đổi — KHAI BÁO TRƯỚC**: 4 ca D1·D2·D5·N1, **không ca nào bị nới lỏng** (giữ nguyên nội dung kiểm, chuyển sang chạy trên đường VAN-TẮT) + 7 ca mới V1-V5/N0/E1-van; suite #36 **35 → 42**. Hash `G-16a`/`G-16b` **tái đóng băng kèm lý do trong file**.
>
> ### ✅ 3. API GIA HẠN → phát hiện **BUG LIVE nặng hơn sổ ghi** (`da0c993`)
> Sổ ghi *"`gemini-2.0-flash` đã tắt"* (một nấc). **Đo thật: CẢ HAI nấc đều 404** (`no longer available` / `is not found`), mà `_is_overloaded` không nhận 404 ⇒ **chuỗi dự phòng CHƯA TỪNG chạy được**; một cú 429/503 là demo văng lỗi. Vá: chuỗi → `gemini-2.5-flash-lite` (cùng thế hệ) + `_model_chet()` tách riêng + câu báo lỗi đúng loại.
>
> ### ✅ 4. NÂNG CẤP MODEL — GĐ1 xong, GĐ2 xong, **GO cho `3.6-flash`** (`825eacd`)
> **GĐ1**: chạy-lại-từ-đầu khi đổi model (thought-signature) · env-hoá temp/max_out/thinking (mặc định GIỮ Y HỆT) · SDK 2.10.0 → **2.17.0** · test 22 → **42 ca**.
> **GĐ2**: R3 **không cần `id`** · R2 **không kích ở 8192** · R1 **giữ được `temperature=0`**. A/B **198 câu × 3 model = 594 lượt, 0 DÒNG RƠI** (nhờ `--nghi` chống 429 mới thêm — lần trước hỏng 127/198 dòng đúng vì thiếu).
> | Trục | `2.5-flash` | `3.6-flash` | `3.5-flash-lite` |
> |---|---|---|---|
> | Bẫy ảo giác (ĐỌC TAY) | 3 vi phạm | **3** | **2** |
> | Đúng số /172 | 147 | **164** | 155 |
> | Recall "không có" | 34,3% | 19,8% | **18,0%** |
> | Thời gian trung vị | 3,6s | 8,4s | **2,3s** |
> | Chi phí/câu | $0,0113 | **$0,0909 (×8,0)** | chưa có giá |
> **Mục 2.6 hàng rào: GIẾT OAN = 0/198 × 3 model (ràng buộc CỨNG) · VÙNG MÙ = 0** ⇒ xoá sạch **117/179** hàng REFUSE mù của dữ liệu cũ.
>
> ### 📌 BÀI HỌC PHIÊN NÀY — **bộ đo hỏng 8 LẦN, tự bắt hết**
> **(a) Đo-trước KHÔNG thay thế được đo-lại-sau-khi-vá.** Van nhường: đo-trước bảo V1≡V2; sau khi code mới lộ — van gỡ hàng ⇒ **giải phóng ngân sách** ⇒ block bị trần cắt **lại hiện ra**; 6 hàng sống sót **đều là hàng #37 ĐÃ TỪ CHỐI** ⇒ V1 tự tay đẩy hàng bị chê lên thành câu trả lời TỰ TIN. Đã chuyển V2.
> **(b) So số phải so CÙNG ĐẠI LƯỢNG.** B7 báo *"11 > 7 = TRƯỢT"* — hoá ra con số 7 đo trên **23 câu × 4 file**, tôi chạy 28 câu × 5 file. Cùng phạm vi thì **đúng 7**.
> **(c) Heuristic từ-khoá-từ-chối chấm ra NO_GO ngược.** 7/10/11 "không từ chối" ⇒ trông như cả hai model mới thua trục quyết định; **đọc tay 12 ca** thì phần lớn là **TRẢ LỜI ĐÚNG**.
> **(d) Dấu phân cách hàng nghìn làm hỏng trục đúng-số**: `8.024` vs `8024` **hạ oan 3.6 mất 11 ca**.
> **(e) `git diff` GIẤU được thay đổi thật** (ghi file đổi CRLF→LF, `core.autocrlf` chuẩn hoá hai phía) · **(f) so hash phải dùng CÙNG chế độ đọc** với ca test đang khoá nó (`rb` vs text) · **(g) khớp hàng theo CHỮ là bộ đo hỏng** khi file có 30 hàng trùng nhãn · **(h) test tự viết có thể CHẾT GIỮA CHỪNG** (`IndexError`) làm "4 ca đỏ" thành con số chưa đủ.

---
## Session 2026-08-07 — ✅ **B4 TÍCH HỢP TOOL #37** + ✅ **B5 BỘ TEST** (36 → 37 MCP tool · cổng `[49/49]` → **`[50/50]`** · **1.701 → 1.778 ca** · diff hàm #36 = 0 byte)
> **TRẠNG THÁI:** commit LOCAL, **CHƯA push, CHƯA LIVE** (đặc tả: chỉ sau **B7** sạch phát-hiện-CAO mới được bàn commit/LIVE — commit này chỉ để **giữ ngữ cảnh**, không phải mark done). `feature_list` **91 mục** (72 done · **2 partial** · 13 deferred · 4 planned); mục `muc4-lat-ghep-cuaso-ngansach` `deferred` → **`partial`**.
> ✅ **B5 XONG: cổng ĐÃ CANH #37** — `tests/test_bang_ke_khung.py` **77 ca / 0 FAIL**, bước `[50/50]` của `check.sh`. (Cảnh báo "cổng chưa canh #37" ở bản ghi trước ĐÃ HẾT HIỆU LỰC.)
>
> ### 🔒 BA BẤT BIẾN CỨNG CỦA B4 — ĐẠT
> hàm #36 hash `275f19e9…` **KHÔNG đổi (0 byte)** · `tests/test_bang_trac_doc.py` hash `8186f9c3…` không đổi · `SYSTEM_PROMPT` `239e8b7b…` khớp FROZEN · **`mcp_bridge.py` KHÔNG bị chạm** (tên tool không xuất hiện ở đâu trong bridge; model vẫn thấy tool vì declaration sinh **ĐỘNG** từ `list_tools` trừ `_TOOL_KHONG_CHO_LLM`) · #37 **không** nằm trong tuple loại-trừ rổ neo ⇒ payload đi vào rổ đúng như thiết kế.
>
> ### 🔧 BA THAY ĐỔI DUY NHẤT SO VỚI PROTO (logic hình học/đẳng thức KHÔNG đụng một ký tự — để còn diff được với bản đã đo)
> **(1) `quet_bang` nhận doc ĐÃ NẠP** thay vì `readfile` lại — mở lại là **nhân đôi doc trong RAM**, mà trần RAM dự án đi theo SỐ doc đang giữ (`MAX_BAN_VE`), không theo MB file. Giữ nhánh path để 3 nhánh từ chối cấp file của V-E còn kiểm được.
> **(2) chuỗi ĐI RA payload qua `to_unicode`** (khuôn #36 — nó phát `vn`, không phát raw). **ĐO TRƯỚC KHI ĐỔI:** `to_unicode` đổi **0/4.451 ô SỐ** và **0/40** nhãn hàng-từ-chối, nhưng đổi **369/576 nhãn** + **20/20 ô chữ** ⇒ nhãn TCVN3 (`§­êng biÓu diÔn cao ®é ®¸y cèng thiÕt kÕ`) mới đọc được, **số không xê dịch một ly**.
> **(3) lọc `nhan_chua` chuẩn hoá GARBLE 2 PHÍA** bằng `_norm(to_unicode(...))` — **ĐIỀU KIỆN GO** của đặc tả.
>
> ### 📊 SỐ ĐO B4
> **① Nền B0 tái lập trên ĐẦU RA SẢN PHẨM** (không phải trên proto): tầng a **2.556/2.556** ô khớp handle nền (P=R=1.0) · tầng b **171/171** · min/max **226/226** · **0** hàng nền mất · **0** hàng thêm · **0/391** hàng nền hạ oan; F5 **23** hàng b / **74** phương trình / xen_ke 23/23.
> **② DIFF proto ↔ sản phẩm trên 5 file = 0 LỆCH** (chữ ký cấu trúc: handle ô, tầng, cờ, biên bảng). Kèm **căn cứ CẤU TRÚC** chứ không chỉ 5 file: `tools_core` **không có một đường ghi nào** vào `doc` (`Drawing.__init__` 0 dòng ghi; quét cả file 0 hit `audit(` / `explode(` / `purge` / `.dxf.x =` / `header[`) ⇒ đọc trên doc đang nạp **tương đương** readfile mới.
> **③ ĐIỀU KIỆN GO, có 2 ĐỐI CHỨNG:** A2 `nhan_chua='đáy kênh'` → **1.740**, `'đáy cống'` → **1.840**; gọi mặc định gh60 **KHÔNG** chứa `1.740` (số đến từ đường LỌC, không có sẵn trong payload = chống tautology) và **TẮT normalizer → 0 hàng** (đúng là normalizer làm nên việc).
> **④ TIÊU CHÍ (2) 6/6** hàng #36-đang-đọc-đúng được #37 trả đúng y giá trị (`_lat4/v_hoiquy_kq.json`).
> **⑤ K1-K5 qua `mcp_bridge` THẬT, 5/5 file sạch**; trần rổ neo **KHỚP CHÍNH XÁC** đặc tả: **160 neo** (đặc tả 160) · mốc-mm **cộng-theo-file 55** (đặc tả 55, trần 60) · mốc-mét **80 = 85 − 5** đúng như đính chính mục 5 (bỏ mốc 0.0, mỗi file 1), trần 90.
> **⑥ CỔNG `[49/49]` PASS `EXIT_CODE_THẬT=0`, 1.701 ca / 0 FAIL** — **diff cổng trước↔sau port ĐÚNG MỘT DÒNG**: `MCP tools khai bao: 36` → `37`. **47/47 suite giữ nguyên TỪNG CON SỐ.**
>
> ### ⚠ HAI LẦN BỘ ĐO / THAO TÁC CỦA CHÍNH TÔI HỎNG (tự bắt, ghi để phiên sau đỡ dẫm)
> **(a) Lần thứ 11 bộ trích hỏng.** Vòng đầu tiêu chí (2) báo **3/6 ĐỎ**. Chẩn đoán: **C1 có 30 hàng TRÙNG Y HỆT nhãn** *'Cao trình tự nhiên (m)'* nên nhánh khớp-theo-CHỮ của tôi vớt nhầm bảng khác; còn 2 ca *'không thấy hàng'* thì hàng nằm **ĐÚNG** ở `muc_luc_hang_chua_tra` vì chạm ngân sách (V-J chạy đúng thiết kế). Đo lại theo **đường caller thật** (`nhan_chua` + khớp theo **HANDLE**) → 6/6. 📌 Trên file nhiều bảng, **khớp theo chữ là bộ đo hỏng**; phải khớp handle.
> **(b) `git diff` GIẤU một thay đổi thật.** Script port ghi lại `tools_core.py` bằng `newline='\n'` ⇒ đổi **CRLF → LF toàn file** (4.367 CRLF → 0), mà `git diff` vẫn hiện **thuần chèn** vì `core.autocrlf=true` chuẩn hoá hai phía. Bắt được bằng cách **đếm byte `\r\n` so với bản backup**, không phải bằng diff. Đã trả lại CRLF (5.534) rồi kiểm lại hash #36 + import. 📌 Đúng khuôn `[[feedback-cong-xanh-khong-du]]`: diff sạch KHÔNG chứng minh file không đổi.
>
> ### ✅ B5 — BỘ TEST `tests/test_bang_ke_khung.py`: **77 ca / 0 FAIL**, thành bước `[50/50]` của cổng
> **Cổng: `[50/50]` PASS `EXIT_CODE_THẬT=0` · 1.701 → 1.778 ca · 0 FAIL.** Bỏ phần đánh-số-lại thì diff cổng B4→B5 **đúng 2 dòng** (bước mới) — **49 bước cũ giữ nguyên TỪNG CON SỐ**.
> **NGUỒN KỲ VỌNG không phải hành vi hiện tại** (chống tautology): bảng kỳ vọng từng fixture ĐÃ ĐÓNG BĂNG + reviewer người duyệt ở B1/B3 (`_lat4/b3fix_fixtures_final.txt`, `b1_ket_qua.jsonl`) · sự-thật-nền đọc tay 391 hàng · mốc hồi quy #36 (`v_hoiquy_kq.json`). Chạy tool sản phẩm trên **47/47 fixture** khớp bảng đóng băng; khác biệt DUY NHẤT là `'%%C10A150'` → `'Ø10A150'` = đúng delta (2) của bản port.
> **7 nhóm:** [D] 11 đọc-đúng-ô/mỏ-neo/V-K/V-G · [G] 26 từng vế từ chối, **mỗi vế MỘT CẶP bắn + không-bắn** · [N] 7 rổ neo (prose 18 chuỗi 0 chữ số, đóng kín, G-12 **hai chiều**) · [B] 7 ngân sách (min/max bất biến + đối chứng số ô PHẢI đổi; mục lục V-J; `gioi_han` dị dạng) · [E] 6 từ chối đúng loại · [R] 4 khoá additive (hash hàm #36 + test #36 + SYSTEM_PROMPT + #37 không bị giấu khỏi LLM) · [T] 8 file thật.
> **FIXTURE VÀO REPO** `tests/fixtures_khung/` (47 file, ~1MB, tổng hợp — đã kiểm 0 định danh khách hàng; chuỗi `TRINH` khớp là *lý trình*) ⇒ **69/77 ca LUÔN CHẠY kể cả trên cloud**; chỉ 8 ca [T] cần corpus ngoài repo, thiếu thì SKIP.
> **⭐ TỰ KIỂM NGƯỢC 6/6 MUTATION ĐỎ ĐÚNG CHỖ** (cổng xanh không chứng minh gì nếu test không đỏ được): gỡ garble-normalizer → T1/T2/T7 · gỡ gate V-A → G-05/G-07/T5b · gỡ `_vn` → T1/T2/T7 · để số đếm ra ngoài `_vitri` → N1/G-12a · bỏ mục lục V-J → G-18 · bỏ vết `khung_nho` → D2. `tools_core.py` khôi phục **nguyên byte** sau mỗi lần (hash `6ab80476` trước = sau).
> **🔒 KHOÁ MỘT QUYẾT ĐỊNH NO_GO:** ca `G-NOGO` khoá việc **vế RATIO của V-H đã BỎ** (bảng CAO và bảng THẤP phải đọc GIỐNG HỆT) — ai định thêm lại `NGƯỠNG_CAO` sẽ thấy ca đỏ và phải đọc `b1c4_censu_ketluan.md` trước (hàng THẬT ratio 2.64-46.0 **đan xen** chế tạo 3.63-506 ⇒ không tồn tại ngưỡng).
>
> ### ✅ B6 — CORPUS 142 FILE + KỶ LUẬT TOÀN BỘ: **ĐẠT, 0 LỖI**
> **⚠ Với B4 thì DANH SÁCH KỲ VỌNG LÀ RỖNG** — khác các cụm B1 trước (chúng có danh sách file được-phép-đổi). B4 không đụng một ký tự logic ⇒ **mọi khác biệt `p37` đều là LỖI**. Đây là mức chặt nhất có thể yêu cầu.
> **① DIFF CORPUS (quét 19,6 phút, `READFILE_MAX_MB` giữ MẶC ĐỊNH 45 = đúng cổng baseline dùng):** `p37` lệch **0/142 file** · `t36` (#36 hàng xóm) lệch **0/142** · trạng thái khớp từng nhóm `{co_bang 93 · khung_khong_bang 33 · khong_khung 7 · loi_doc_file 9}` · **9/9** DXFStructureError giữ `loi_doc_file` · **tổng ô đọc được toàn corpus 7.207 = 7.207**.
> **② ĐƯỜNG SẢN PHẨM ≡ ĐƯỜNG ĐỌC-FILE, PHỦ TRỌN 142 FILE.** Lượt đầu: 119 KHỚP · 14 bị cổng 45MB chặn · 9 file DXF hỏng. **Không bỏ im 14 file bị chặn** — chúng chính là các bản KẾT CẤU LỚN NHẤT (bỏ ra là mẫu đo lệch hẳn về file nhỏ) ⇒ chạy lại riêng với `READFILE_MAX_MB=400`: **14/14 KHỚP**, tổng **1.186 MB**, file to nhất **212 MB**, 14,1 phút.
> **③ K1-K5 qua `mcp_bridge` THẬT trên 93 FILE KÍCH HOẠT: 0 lỗi** (đặc tả đòi ≥30 — vượt xa; danh sách file lấy TỪ kết quả quét, không tự chọn tay). Σ neo cộng-theo-file **543**.
> **④ UNION MỐC-MM CORPUS-WIDE = 135**, trần khai **≤143**. ⚠ Lệch **+2** so con số **133** trong đặc tả ⇒ **KHÔNG để số đó không giải thích**: đo có đối chứng (đọc file MỘT lần, dựng payload HAI lần: `_vn=to_unicode` vs `_vn=identity`) ⇒ **bản vá giải-mã-phông đóng góp ĐÚNG 0 mốc** (135 cả hai chiều, **0/93 file khác biệt**). ⇒ chênh +2 **có từ TRƯỚC B4**, không do lát này đẻ ra, và nằm trong trần.
> **📌 Lần thứ 3 CRLF làm hỏng bộ đo trong phiên:** kiểm hash hàm #36 bằng one-liner đọc `'rb'` cho `083d5921` (lệch!) trong khi đọc chế độ TEXT — đúng như ca G-16b của suite — cho `275f19e9` KHỚP. Cả file `tools_core.py` hash không đổi (`6ab80476`) nên biết ngay là artifact. 📌 **Đọc file để so hash thì phải dùng CÙNG chế độ đọc với ca test đang khoá nó.**
>
> ### ✅ B7 — RED-TEAM VÒNG 2 SAU TÍCH HỢP: **SẠCH, 0 PHÁT HIỆN CẦN XỬ LÝ**
> **CỔNG CHỐT SỔ (đo lại cuối phiên, không phải nhớ): `[50/50]` PASS `EXIT_CODE_THẬT=0` · 1.778 ca · 0 FAIL · GIỐNG HỆT TỪNG DÒNG lần chạy B5.**
> **① TẦNG 1 — bộ câu bịa qua `_guard_text` THẬT. ⚠ VÒNG ĐẦU TÔI BÁO SAI 'TRƯỢT 11>7' vì so HAI ĐẠI LƯỢNG KHÁC NHAU:** bộ đo sinh ra con số 7 (`x3_cau_bia.py`) chạy **23 câu × 4 file (A1,A2,C1,C2), KHÔNG có F5**; tôi chạy 28 câu × 5 file. Phân xử bằng số: **P1 (23 câu × 4 file) = ĐÚNG 7** ✅ · P2 (thêm F5) = 9 · P3 (thêm 5 câu mới) = 11. **ĐỐI CHỨNG QUYẾT ĐỊNH:** P1 với `_vn=identity` (gỡ delta 2) cũng = **7** ⇒ **B4 đóng góp +0**. ⇒ tiêu chí (9) **ĐẠT: cùng phạm vi thì số KHÔNG TĂNG**.
> **② TẦNG 2 — đánh vào ĐÚNG 3 DELTA mà B4 đẻ ra** (bề mặt MỚI, proto chưa từng phải chịu — đây mới là chỗ đáng đánh):
> · **A1 doc DÙNG LẠI**: gọi **10 tool khác XEN GIỮA** (`doc_bang_trac_doc`, `cao_do_min_max`, `doc_chu_trang_in`, `phat_hien_bang_ve_net`, `doc_bang_nhung`, `thong_ke_thep`, `thong_tin_tang`, `tim_kiem`…) rồi gọi lại #37 → **BẤT BIẾN 10/10**; gọi #37 hai lần liên tiếp → bất biến. *(Đây là rủi ro riêng của B4: nếu tool khác làm biến đổi `doc` thì #37 đọc sai IM LẶNG.)*
> · **A2 `to_unicode` có sinh CHỮ SỐ từ chuỗi KHÔNG-SỐ?** (= kênh bơm neo MỚI) → **0/9.139** đoạn chữ trên 5 file đích.
> · **A3 `nhan_chua` do MODEL tự gõ** — thử `'-600'`, `'1.94'`, `'9999'`, `'-13.7'`, `'cống -600'`, `'30000'` → **0 neo bơm vào rổ**. Đây ĐÚNG lớp lỗi mà #36 từng dính (`loc_nhan` ngoài `_vitri` bơm −600) ⇒ #37 đóng kín vì `tham_so` nằm trong `_vitri`.
> · **A4 tham số thù địch** (20.000 ký tự · null byte · RTL override `‮` · chữ số toàn-rộng `９９９９` · path traversal · SQL-ish) → **không crash, không rò, ≤72 ms**, đều trả `loc_khong_khop`.
> **③ 🔴 SỐ MỚI CHƯA TỪNG ĐO — KHÔNG PHẢI LỖI NHƯNG PHẢI BIẾT:** trên **file KÍCH-HOẠT-MỚI** (#36 im hoàn toàn ⇒ mọi câu lọt đều do #37 mở): **31 lượt câu bịa lọt / 5 file** chạy được dưới cổng 45MB (4 file khác bị cổng chặn). **Đặc tả TRƯỚC ĐÂY chỉ định lượng cho 5 file đích, CHƯA HỀ đo nhóm này — mà corpus có 89 file thuộc nhóm đó.** Không phải hồi quy; đây là **cái giá của việc BẬT #37** mà user đã chốt chấp nhận (phương án (a): LIVE #37 rồi xếp lát grounding-có-đơn-vị NGAY SAU). Nhưng số thật **lớn hơn hình dung cũ** ⇒ **củng cố lý do làm lát ×1000 ngay, không để lâu**.
> **📌 BÀI HỌC:** *"11 > 7"* trông y như một hồi quy thật. Cứu được bằng đúng một câu hỏi: **con số 7 kia đo trên phạm vi nào?** ⇒ **so số thì phải so CÙNG ĐẠI LƯỢNG — bộ câu, danh sách file, mức gh phải trùng khớp**, nếu không thì "tăng/giảm" là vô nghĩa.
>
> ### ⏭ CÒN LẠI
> **B0-B7 XONG TRỌN.** Theo đặc tả, ĐÂY là lúc được phép bàn **commit/LIVE** (điều kiện "B7 sạch phát-hiện-CAO" đã đạt). **Chưa push — chờ user quyết.** **Ngay sau khi #37 LIVE:** lát **grounding-có-đơn-vị** (lỗ ×1000 ở `mcp_bridge`) — user đã chốt xếp NGAY SAU, và số ③ ở trên làm nó cấp thiết hơn.

---
## Session 2026-08-06→08-07 — 🏁 CHỐT SỔ: **lát 4a LIVE** · **3 vòng NO_GO có số** · **TOOL #37 proto B0-B3 HOÀN TẤT** · chuẩn mới của user
> **CHỐT SỔ:** HEAD **`7e24bc5`**, tree SẠCH. **CỔNG `[49/49]` PASS** (xem khối kết quả cuối entry). **8 commit**: `d4a7c33` (lát 4a — code) · `0a3dfaa` · `ef94b4a` · `d690e3d` · `51131f1` · `a68d23e` · `fd30737` · `7e24bc5` (7 commit docs/sổ). `feature_list.json` **85 → 91 mục** (72 done · 1 partial · 14 deferred · 4 planned — 4 planned và 1 số mục là của **phiên song song**, đã nhận nguyên trạng có ghi nguồn trong commit message).
> ⚠ pytest **VẪN crash** (`ValueError: I/O operation on closed file` → `no tests ran`) — kiểm lại cuối phiên, không phải nhớ. **KHÔNG có `specs/specs.json`** → `feature_list.json`. (Hai điều này lặp mỗi phiên; checklist dòng 8 đã ghi.)
>
> ### ⭐ CHUẨN MỚI CỦA USER (2026-08-06) — ÁP CHO MỌI VIỆC ĐỌC-SỐ VỀ SAU
> *"Đọc đúng và trả lời đúng còn ảnh hưởng tới chức năng chính tiếp theo là **DỰ TOÁN**. Chính xác gần như phải TUYỆT ĐỐI. Dù một sai sót nhỏ cũng ảnh hưởng toàn bộ dự án — **tuyệt đối không 9-bỏ-làm-10**."*
> ⇒ **số SAI = lỗi · số THIẾU = lỗi · đọc đúng hoặc TỪ CHỐI RÕ**. Phương án chỉ *giảm sai mà không đọc đúng* (kiểu "NÍN") = **cầm máu, KHÔNG phải lời giải**; phải trình user như LỰA CHỌN kèm giá, không tự quyết. Memory `[[feedback-chinh-xac-gan-tuyet-doi]]`.
>
> ### ✅ VIỆC DUY NHẤT VÀO CODE SẢN PHẨM: LÁT 4a (`d4a7c33`) — bịt kênh bơm rổ neo thứ 4
> `ghi_chu`/`ly_do` của tool **đi trọn vào rổ neo** (không ở tuple loại-trừ, `_strip_neo` không lọc chuỗi tự do). **5 chuỗi đã vá** ở `cao_do_min_max` + `thong_tin_tang`; nguy nhất: ví dụ `'cốt - 14.260'` bơm **14.26** (chữ ký id135) và `'(±0.000, +3.600…)'` bơm **3.6** (chiều cao tầng điển hình = số model dễ bịa nhất) — **6 câu bịa lật LỌT→CHẶN**. Vá bằng cách viết số **bằng chữ**/**placeholder**, giữ nguyên 100% thông tin. Test 31→**52**; tự kiểm ngược gỡ vá = **đúng 15 ca đỏ**; cổng `[49/49]`, **33/33 suite khác giữ nguyên TỪNG CON SỐ**.
>
> ### ⛔ BA VÒNG NO_GO CÓ SỐ (đừng mở lại — chi tiết ở `feature_list` mục `muc4-lat4-routing-nudge` + `muc4-lat-ghep-cuaso-ngansach`)
> **(1) Lát 4b routing-nudge**: trần tuyệt đối **2 bản vẽ** (bắn 54 file trúng 2 = 3,7%) ⇒ ngưỡng tiền lệ ≥3 **bất khả thi về số học**; và đích đến trả **số sai** ở lệnh gọi mặc định (`1.800` thay vì `1.740`), hàng rào **quay ngược** (bảo lãnh số sai, chặn số đúng).
> **(2) Cả HỌ luật "nối dài ≤ K×bước cột"**: F5 `max(đi-tiếp)=5,46 > min(dừng)=0,76` **chồng lấn tuyệt đối**; chấm bằng thước khung-nét độc lập thì nối dài K=1,25 làm F5 **ĐI XUỐNG** (79,8%→75,4%). Lợi ích trên 4 file đích là **thuộc tính BỐ CỤC**, không phải của luật.
> **(3) Gộp min/max qua block**: bản vẽ tự ghi `'cống bên trái/phải tuyến'`, `'KÊNH THUỶ NÔNG HOÀN TRẢ'` ⇒ gộp ra dải **không cống nào có**.
> 🔴 **PHÁT HIỆN NGOÀI PHẠM VI, QUAN TRỌNG NHẤT VỀ AN TOÀN:** lỗ **×1000 CÓ SẴN trong HEAD** — 1 lượt `doc_bang_trac_doc(nhan_chua='Khoảng cách')` trên C2 cấp **13/33 mốc mm** + **6 câu bịa LỌT**. Đòn bẩy ở `_is_grounded`/ANY-GROUNDED trong `mcp_bridge`, **KHÔNG ở tool #36**. User đã chốt: lát **grounding-có-đơn-vị** xếp **NGAY SAU** khi #37 LIVE.
>
> ### 🔬 NỀN ĐO MỚI — thước đọc tay + phân xử số tranh chấp
> **Thước sự-thật-nền ĐỌC TAY 391 hàng / 4.283 ô / 5 file** (`_lat4/su_that_nen_doc_tay.json`), biên bằng khung nét ngang+dọc, mỗi hàng 5-7 dấu hiệu quan sát được, **không luật ứng viên nào tham gia** — dựng vì cả 2 vòng trước đều bị chấm bằng thước do chính thuật toán sinh ra.
> **PHÂN XỬ số tranh chấp 23/23 vs 9/24** (3 bộ trích độc lập trùng 100% per-bảng): **agent ĐÚNG NGUYÊN VĂN** — 23/23 khớp đẳng thức (74/74 phương trình, Decimal nguyên-cent KHÔNG dung sai), O-B 97/97 ô. **Số 9/24 của tôi là ARTIFACT** = lần thứ **10** bộ trích hỏng: chữ cộng dồn viết DỌC có mỏ neo thật `align_point` nhưng `insert` **tụt theo ĐỘ DÀI chuỗi` ⇒ dải ±1.0 chặt cụt 65/171 ô. 📌 **BÀI HỌC KỸ THUẬT:** TEXT căn lề (`halign≠0`) thì toạ độ NGHĨA là **`align_point`, KHÔNG phải `insert`**.
>
> ### 🔨 TOOL #37 `doc_bang_ke_khung` — ĐẶC TẢ + PROTO B0-B3 HOÀN TẤT (**0 dòng code sản phẩm bị đụng**)
> Đặc tả chốt sau red-team: **`DAC_TA_TOOL37.md`** (gốc repo) — tool MỚI additive, #36 nguyên từng byte; phân tầng a-PHẲNG / b-ĐẲNG-THỨC (`da_chung_minh` BOOL, gate `so_pt≥2`+xen kẽ) / c-TỪ-CHỐI-ĐÍCH-DANH + 4 nhánh từ chối cấp file; mỏ neo `(rotation, align_point)`; Decimal nguyên; `gioi_han` sống. **User chốt 4 quyết định**: LIVE #37 rồi vá ×1000 ngay sau · trần 60/200 · V-H = từ chối đích danh · ưu tiên trên-xuống + mục lục.
> **B1 — 4 cụm + 5 guard sinh thêm giữa chừng, TẤT CẢ qua review người:** ① fail-closed: **80.224 dải rơi-không-vết → 0** (V-D nguyên văn **BỊ ĐO BÁC**, 49 hàng nền mất → ghép-dải-gần-bằng) · ② mỏ neo + V-F2a/b: soi entity 4 ca drift (**bản cũ neo SAI cả 4**), guard chữ-khổ-lớn **cứu hàng `2A` 9 giá trị thật** + giết hàng giả, **06.TB6 +18 hàng THẬT** (o_doc 125→407) · ③ gate chứng minh: F5 **23→9 claim** đúng từng số, 74/74 phương trình kiểm ĐỘC LẬP, corpus diff **0 mọi trục** · ④ lưới trục + V-H2 3 vế: **25/25 hàng chế-tạo bị chặn, oan 0/420** (vế RATIO **bỏ đúng luật knife-edge**).
> **B3 red-team → `đủ_điều_kiện_B4 = false`, bắt 4 CAO** mà **59/60 fixture tự viết vẫn pass** (đúng tiền lệ): bảng-vanish · nhánh câm khung nhỏ · mode-flip · ghép-x nuốt bảng kề. **Đã vá xong, gate xanh trọn**: vanish=0 · census **108 dải → 0** · mode-flip lộ · 2 bảng kề tách đúng · ma trận kỷ luật **75/75** · corpus diff **0 ngoài kỳ vọng**.
> **12 ngưỡng mới đều có plateau đo được, 0 knife-edge. 3 đề xuất sai bị CHÍNH PHÉP ĐO bác trước khi vào code** (V-D nguyên văn · vế RATIO · vế rot90-đứng-một-mình giết 193 hàng nền).
>
> ### 📌 BÀI HỌC PHIÊN NÀY
> **(a) Đi đo tính năng A lại tìm ra lỗi của tính năng B — và lỗi đó đáng giá hơn.** Lát 4 ra NO_GO, nhưng đường đi tới NO_GO lộ 5 chuỗi rò neo đang chạy LIVE + lỗ ×1000 có sẵn.
> **(b) `align_point` vs `insert`** — lần thứ 10 bộ trích hỏng, lần này theo hướng **BI QUAN**, suýt vứt một hướng ĐÚNG.
> **(c) Không nhận nguyên xi kết luận agent, kể cả khi nó đúng số:** ca `1.800/1.740` — phần **số** đúng, phần **mức nghiêm trọng** sai (bảo tool im lặng, thực tế lộ 4 đường); phân biệt được hai cái đó **đổi hẳn khuyến nghị**.
> **(d) Nhịp làm việc hiệu quả đã thành khuôn:** *máy đo → dừng đúng luật khi lệch kỳ vọng → người soi ENTITY → ghim*. 4/4 cụm không lọt thay đổi nào chưa qua mắt người. Scan corpus dài **mồ côi 5 lần** vì agent hết lượt — reviewer chạy lại ngoài workflow là thủ tục chuẩn, không phải sự cố.

---
## Session 2026-08-06 (nối) — 🔬 Tool #36 có **HAI** cơ chế cắt · **thước đo bị cong** · lát ghép ĐANG LÀM
> **HEAD `d4a7c33` · cây SẠCH · suite #36 `35 PASS / 0 FAIL`** (bản vá dở đã HOÀN TÁC, lưu `_lat4/lat4c_WIP.patch`). `feature_list` **86 → 87**. Chi tiết đầy đủ: khối 2026-08-06 ở `session-handoff.md`. Nghiên cứu `wf_7d902824-ad4`.
> **① Ngoài trần `_BTD_CAP_TONG=60` còn CỬA SỔ NGANG `40*p` cắt NGANG GIỮA MỘT HÀNG.** Đọc thẳng `entitydb`: dãy handle liên tục `41E9C→41EC2`, bước x đúng **2.000 không đứt**, `'1.940'` trong / `'1.840'` ngoài ⇒ min thật **1.840**, tool đọc **1.940**.
> **② Hệ quả: THƯỚC ĐO CONG.** "Sự thật nền" (nâng trần lên cao) vẫn thừa hưởng vết cắt cửa sổ ⇒ **10/22 nhãn có sự-thật-nền SAI**; **1 trong 9 nhãn "đã sửa" được chấm đậu bằng con số sai**.
> **③ ⛔ Hai thiết kế ngân sách đều NO_GO** (3/3 góc phản biện bác): cả hai **mở giấy phép bịa thang mm** qua hàng `'Khoảng cách (m)'` (A +17 mốc, B +79); PA-A **giết câu đúng** 6/7 và trả 0 ô + 0 cảnh báo ở 6/20 tổ hợp; PA-B nhân sai-tự-tin (31 ô `nho_nhat` mâu thuẫn, đúng 2/31).
> **④ ⛔ KHÔNG GỘP min/max qua block** — bản vẽ tự ghi `'cống bên trái/phải tuyến'` và `'KÊNH THỦY NÔNG HOÀN TRẢ'`; gộp ra dải **không cống nào có**. Hướng đúng: **định danh block** (chữ có sẵn, tool đang giấu).
> **⑤ 🔬 Tự đo sau khi code thử: vá cửa sổ MỘT MÌNH LÀM TỆ ĐI** — hàng dài gấp đôi ⇒ A1 **4→2 hàng** (mất `'đáy cống'`), C1/C2 4→2. Chia suất theo hàng cứu A1+A2 nhưng C1/C2 vẫn 5→3 vì đói ở **tầng BLOCK**. ⇒ **cửa sổ + ngân sách phải vá CHUNG MỘT LÁT**; kế hoạch "ship 4-C riêng trước" **bị chính phép đo bác**.
> **⑥ Mặt tốt đo được:** cặp `min == max` biến mất (dấu hiệu hàng cụt) — A2 cả 3 hàng thoát.
> **📌 Bài học:** quét độ nhạy ra **y hệt ở cả 5 mức ngưỡng** — đọc đúng là **dữ liệu BIMODAL**, KHÔNG phải "chọn ngưỡng khéo". Và *"C1 min thật 1.10"* của một góc phản biện **không sống sót** (bộ trích bỏ cửa sổ hoàn toàn nên vợt sang bảng kế bên) — **lần thứ 9** bộ trích suýt cho kết luận ngược, lần này theo hướng **bi quan**.

---
## Session 2026-08-05 — 🔎 Nghiên cứu **LÁT 4** → ✅ vá **LÁT 4a** (prose 0 chữ số) + ⛔ **lát 4b NO_GO có số**
> **CỔNG `[49/49]` PASS exit 0 · 36 MCP tool · `test_cao_do_min_max` 31 → 52 ca · diff từng suite: DUY NHẤT bước [20/49] đổi số, 33/33 suite còn lại giữ NGUYÊN TỪNG CON SỐ.** `feature_list.json` **85 → 86 mục** (72 done · 1 partial · 13 deferred). KHÔNG bump `PROMPT_VERSION` (đo `sha256(SYSTEM_PROMPT)` = `239e8b7b…` KHỚP FROZEN; ghi_chu của tool không phải chuỗi con của SYSTEM_PROMPT). Nghiên cứu: `wf_f5e1a3dd-ace` (5 probe độc lập + tổng hợp), script đo để **ngoài repo** ở `D:\Dat-Antigravity\_lat4\` — 0 dòng code sản phẩm bị chạm trong lúc đo.
>
> **① ✅ LÁT 4a — BỊT RÒ RỔ NEO QUA PROSE. Lỗi CÓ SẴN trong bản LIVE, phát hiện KHI đi đo lát 4, không phải do lát 4 đẻ ra.**
> **Cơ chế:** `cao_do_min_max`/`thong_tin_tang` KHÔNG ở tuple loại-trừ (`mcp_bridge.py:1226`), `_strip_neo` không lọc chuỗi tự do, `_collect_numbers` quét chữ số trong **mọi** chuỗi ⇒ mọi chữ số trong `ghi_chu`/`ly_do` thành **NEO grounding**. Ở nhánh 0-marker `_guard_text` là hàng rào **DUY NHẤT** còn hoạt động (đo có đối chứng: A2 không kích, A3 lọc nhóm khác) ⇒ một chữ số lạc vào đây = **mất trọn một lớp bảo vệ**.
> **5 chuỗi đã vá:** `'kèm 2-3 số thập phân'` (bơm 2.0/3.0) · hai ví dụ `'CH - 2.700'` + `'cốt - 14.260'` trong `ly_do` (bơm 2.7 và **14.26 = chữ ký id135**; `cb_am` nối vào `canh_bao` ở **cả nhánh THÀNH CÔNG** nên rò rộng hơn dự đoán) · `'Có %d marker…'` (số ĐẾM cũng thành neo) · `thong_tin_tang` `'(±0.000, +3.600...)'` (bơm 0.0/**3.6**) và `'cột C1 cao 3.6m'`.
> **Cách vá:** giữ NGUYÊN thông tin — viết số **bằng chữ** (`'hai đến ba chữ số thập phân'`) hoặc **placeholder** (`n.nnn`, `<số>`). Không cắt nghĩa câu nào.
> **Số trước/sau:** rổ nhánh 0-marker `[0.0, 2.0, 3.0]` → `[0.0]` · nhánh marker-ÂM-dạng-cách `[-2.7, 0, 1, 2, 2.7, 3, 14.26]` → `[-2.7, 0.0, 2.7]` · nhánh THÀNH CÔNG bỏ `2.7` và `14.26` · `thong_tin_tang` nhánh 0 mốc `[0.0, 3.6]` → **RỖNG**. Qua chính `_guard_text`, **6 câu bịa lật LỌT → CHẶN**: *'dài 3 m'* · *'dày 2 m'* · *'sâu 3000 mm'* · *'Cao độ đáy cống là 14,26 m'* · *'Chiều cao tầng điển hình là 3,6 m'* · *'Chiều cao tầng là 3600 mm'*.
> ⚠ **`thong_tin_tang` NGUY HƠN ca 14.26** — `3.6` là chiều cao tầng ĐIỂN HÌNH nên là con số model dễ bịa nhất, mà chính nhánh *"không đọc được gì"* đứng ra bảo lãnh nó. Ca này **nới phạm vi** so với 2 lỗi báo cáo ban đầu; lý do là bằng số, đã nói rõ với user.
> **Đối chứng (4 loại, đều giữ đúng hành vi 2 phía):** nhánh G3-fallback vốn sạch ⇒ **không đổi một số nào** · `'77,77 m'` CHẶN cả trước lẫn sau · số ĐỌC THẬT `-1.85/10.8/-9.12/3.3` và chuỗi `'2.700'` có thật trên bản vẽ **vẫn được bảo lãnh** (không giết câu đúng) · `_prose_digits` tự kiểm bắt được số cắm vào ghi_chu và bỏ qua trường DỮ LIỆU.
> **Tự kiểm ngược:** gỡ bản vá ⇒ **đúng 15 ca đỏ**, nhóm đối chứng + nhánh G3 vẫn xanh ⇒ suite phân biệt đúng chỗ.
> **⏳ CỐ Ý ngoài phạm vi:** trường ĐẾM `so_marker` vẫn bơm số (`'dày 2 m'` còn LỌT khi `so_marker=2`) = lỗ `[[ref-lo-hong-so-dem-khong-guard]]`, dự án đã chốt **lát riêng**. Bộ **sàng tĩnh** còn nêu 5 hàm khác có prose mang chữ số và không ở tuple loại-trừ: `liet_ke_so_luong` (**chính chuỗi `"vd 'D1'"` mà `b236b7e` đã gỡ ở `tra_cuu_so_luong`, sót lại ở đây**), `hoc_quy_uoc`, `phan_loai_tin_hieu`, `_resolve_lo_cua`, `_gan_cc` — **quét tĩnh, phải chạy thật để xác minh** trước khi vá.
>
> **② ⛔ LÁT 4b (routing-nudge) = NO_GO, có số. Không phải vì câu chữ khó viết.**
> **(a) Trần tuyệt đối = 2 bản vẽ.** Quét 123 file nạp được (76 corpus giao + 47 bộ `_f1_check`), bảng chéo `co_cao_do × co_bang`: **A** (0-marker ∧ #36 có kết quả = nudge hữu ích) = **2** · **B** (0-marker ∧ #36 rỗng = nudge trỏ vào chỗ trống) = **52** · **C** (có marker ∧ #36 có ⇒ nudge KHÔNG BAO GIỜ bắn) = 2 · D = 67. Nudge bắn 54 file, trúng 2 = **3,7%**. Ngưỡng tiền lệ `≥3/11` **bất khả thi về số học** vì tổng dân số trúng đích là 2.
> **(b) Đích đến trả SỐ SAI ở lệnh gọi mặc định** (tự chạy tool thật để kiểm, không nhận báo cáo của agent): `doc_bang_trac_doc()` trên file cờ đầu trả `nho_nhat='1.800'` handle `42E96`; gọi `nhan_chua='đáy cống'` lộ ra **2 block**, min thật `'1.740'` handle `4291B`. Ngân sách `_BTD_CAP_TONG=60` bị block đầu tiêu hết, block 2 bị bỏ, `_vitri.so_block` báo 1.
> **📌 ĐÍNH CHÍNH mô tả của agent:** tool **KHÔNG im lặng** — nó lộ bằng **4 đường** (`khong_day_du`, `_bi_cat` mức block, `canh_bao:['cat_bot_gia_tri_cua_hang',…]`, và ghi_chu ghi thẳng *"TUYỆT ĐỐI không kết luận nhỏ nhất/lớn nhất của TOÀN bảng… gọi lại với `nhan_chua` thu hẹp"*). Bản vá red-team lần trước **có tác dụng**. **Nhưng** hàng rào chống bịa **quay ngược**: *"…là 1,800 m."* **LỌT** (số SAI, có trong rổ) còn *"…là 1,740 m."* **CHẶN** (số ĐÚNG, không có trong rổ) ⇒ lớp bảo vệ duy nhất còn lại là model chịu đọc prose. ⇒ **nudge THÀNH CÔNG có thể làm hệ TỆ ĐI**, nudge thất bại thì vô ích.
> **(c)** Cả 2 file thắng nằm **ngoài mọi corpus đã cấu hình** (battery cố định 3 file KT/KC/rachmop, 0 file trắc dọc; `battery.json` 0 câu trắc dọc) ⇒ phải dựng driver riêng cho dân số 2 file.
> **Điểm ủng hộ đã ghi nhận công bằng (không đủ lật kết luận):** SYSTEM_PROMPT có `cao_do_min_max` nhưng **không hề có** `doc_bang_trac_doc` lẫn *"bảng trắc dọc"* ⇒ tool #36 hiện có **0 đường routing ở tầng prompt** · ghi_chu nhánh (1) không bị suite nào khoá · chi phí nudge-**có-đo** rẻ (detector trên đúng đường 0-marker: median **1,39 ms** = 0,172% thời gian nạp, xấu nhất 64 ms = 2,78%; RAM ≤1,56 MB) và **xoá sạch ô B**.
> **Ngôn từ nếu sau này làm:** bắt buộc **0 chữ số** — đo thật: `'tool #36'` bơm `36.0`, lật 2/5 câu bịa CHẶN→LỌT và E2E qua `tra_loi_ai` cho *"Cao độ đáy cống là 36 m."* đi trọn vẹn; gọi bằng TÊN `doc_bang_trac_doc` thì sạch. **Cấm** cụm `'không tìm thấy'`/`'không có thông tin'` (∈ `_REFUSAL_MARKERS` ⇒ `_guard_text` **thoát sớm, bỏ kiểm cả bài**) và **cấm** khẳng định bản vẽ CÓ dữ liệu (bài học E2). Tiền lệ ngôn từ ĐÚNG đã LIVE: nhánh rỗng của chính #36 (`tools_core.py:2300`) nudge ngược về `tim_kiem`/`cao_do_min_max`.
>
> **📌 BÀI HỌC PHIÊN NÀY**
> **(a) Đi đo một tính năng lại tìm ra lỗi của tính năng KHÁC — và lỗi đó đáng giá hơn.** Lát 4 đo xong ra NO_GO, nhưng đường đi tới NO_GO lộ ra 5 chuỗi rò neo đang chạy LIVE, trong đó `3.6` là số dễ bịa nhất của cả miền.
> **(b) Bộ đo của agent hỏng, tự bắt bằng số quá đẹp:** bộ dò nhãn trắc dọc dùng `NFD` để bỏ dấu, mà `Đ/đ` (U+0110/0111) **không có canonical decomposition** ⇒ mọi khoá *"cao độ"*/*"đường biểu diễn"* chết câm, báo *"0/76 file có nhãn"*. Đổi sang normalizer của chính sản phẩm ⇒ 13/76. Đúng khuôn `[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`.
> **(c) Không nhận nguyên xi kết luận của agent.** Agent mô tả ca `1.800/1.740` là *"sai tự tin, trình bày như sự thật sạch"*; chạy tool thật cho thấy nó lộ bằng 4 đường. Phần **đúng** là con số, phần **sai** là mức nghiêm trọng — và phân biệt được hai cái đó đổi hẳn khuyến nghị (từ *"tool hỏng"* sang *"hàng rào quay ngược"*).

---
## Session 2026-08-02 — 🏁 CHỐT SỔ PHIÊN: **F1 không đạt (có số)** · vá **audit ODA** · **VNI vớt tầng 2** · **PA-0** · **MỤC 4 lát 0 + lát 1 (tool #36)**
> **CHỐT SỔ:** HEAD **`0c1d710`** == origin, tree SẠCH. **LIVE verify `0c1d710`**: prompt `2026.07.27-kb-l3` hash `239e8b7b…` **KHÔNG đổi** · kb `e55ac112…` **KHÔNG đổi** (không lát nào chạm SYSTEM_PROMPT/kho ⇒ không cần A/B) · `/health` ok, `ram_mb` **136,0** · trang chủ HTTP 200.
> **CỔNG: `[49/49]` PASS · 36 MCP tool · tổng ca 1.627 → 1.680 (+53) · check.sh 48 → 49 bước · 0 regress ở MỌI lát** (mỗi lát diff từng suite chỉ đổi ĐÚNG suite của lát đó). `feature_list.json` **79 → 85 mục** (71 done · 1 partial · 13 deferred). ⚠ **pytest VẪN crash** (`ValueError: I/O operation on closed file` → `no tests ran`) — kiểm lại cuối phiên, không phải nhớ; cổng là `check.sh`. **KHÔNG có `specs/specs.json`** → dùng `feature_list.json`.
> **7 commit** push+deploy+verify: `0cb25e6` (vá audit) · `dabcaac` (docs F1) · `7030aa6` (PA-0) · `6b7c2b9` (VNI tầng 2) · `b366161` (docs) · `755d053` (lát 0) · `0c1d710` (lát 1 tool #36).
>
> **① ⛔ F1 KHÔNG ĐẠT — bác bằng số, KHÔNG phải bằng cảm tính.** Đối tác gửi 57 file (2 đơn vị tư vấn Hải Dương). Phần **thiết kế** sâu nhất **−4,10 m** (Bể PCCC) · −3,95 (Trạm XLNT) ⇒ vẫn dưới −5m. Hai file đạt ngưỡng là **KHOAN ĐỊA CHẤT** (−54,30 / −30,00) — đọc tay quanh chính handle sâu nhất thấy `'Độ sâu hố khoan - m'`, `'(Depth of borehole)'`, `SPT16` ⇒ **độ sâu KHẢO SÁT, khác hệ**, đúng loại từng làm `cao_do_min_max` trôi −2.1 → −94.44. Quét thô toàn bộ xác nhận không còn mốc ≤ −5m nào khác. **Corpus cũ cũng không có** (file −22,75 đã kiểm lại: outlier cô lập, cách giá trị âm kế tiếp **20,9 m**, engine tự gắn `nghi_ngo=True` ⇒ kết luận "rác" của dự án ĐÚNG). ⇒ F1 vẫn chờ file ngoài; đã soạn tin nhắn lần 2 **hỏi theo LOẠI CÔNG TRÌNH** (móng cọc/tầng hầm/trạm bơm) và **nói rõ hố khoan địa chất KHÔNG dùng được**.
>
> **② ✅ VÁ `dwgconv` audit=0 → audit=1 (`0cb25e6`) — bug NGƯỜI DÙNG gặp mà DEV không bao giờ thấy.** `.dwg` lỗi cấu trúc + audit=0 ⇒ ODA **vẫn sinh** `.dxf` nhưng **CỤT** ⇒ hàm trả về **file hỏng KHÔNG BÁO GÌ**. ⚠ So sánh đầu **không sạch** (đổi 2 biến) — đã **cô lập biến** rồi mới kết luận. A/B **148 file**: **cứu 10/147 (6,8%)** · **hỏng thêm 0** · 121/123 file **số y hệt** · 2 file lệch **duy nhất `tong_doi_tuong`** (cao độ/chữ/dim/thép **giữ nguyên**) · 14 file cả hai lỗi = **trần 45MB của chính dự án**. Giá: **+0,47s/file**; file 36,33MB 24,3s → 30,4s (timeout 600s). 📌 **Vì sao chưa từng lộ:** 10 file được cứu có **`chinhcaodo.dwg` của TB6** (988 chữ, **200 marker cao độ**) — corpus không có bản `.dxf` nên dev luôn dùng `.dxf` sẵn, **không đi qua `dwgconv.py`**. Cuối phiên đã convert lại file đó qua chính đường sản phẩm (0,23MB cụt → 8,12MB, số khớp A/B) ⇒ **cache corpus 92/92 file thật đọc được**.
>
> **③ ✅ MỤC 1 — VNI VỚT TẦNG 2 (`6b7c2b9`, `wf_666cedfd` GO/GO_WA×2).** Thay bằng-chứng-cứng KÝ TỰ bằng bằng-chứng **ÂM TIẾT** (token G/A/XẤU; bắn ⟺ ≥1 G ∧ 0 XẤU ⇒ lớp `TOÀ/HOÀ` toàn-A **không bao giờ bắn** — bảo vệ THEO CẤU TRÚC). Vớt **78/79 chuỗi (180/181 lượt), 0 vớt-sai** (đọc tay 100%), **0 phá-chữ-đúng** (584 chuỗi bảo vệ byte-identical), **0 lệch số**; sweep old-vs-new 97.406 chuỗi trên cây thật khớp **từng con số**; to_unicode +9,3%. `test_vni` 43→**55**; tự kiểm ngược: vô hiệu recovery → **đúng 8 ca mới đỏ**.
>
> **④ ✅ MỤC 2 — RỔ NEO RỖNG: chốt DƯỚI NGƯỠNG (`7030aa6`, `wf_06b6cf5e` 3 verify GO_WA).** 832 lượt → 179 REFUSE → **oan thật 1 hiện tượng (id69) < ngưỡng ≥3 ⇒ KHÔNG đổi hành vi**. ⛔ **PA-2 (A3-kho-ký-hiệu) = NO_GO CẤU TRÚC**: kho cấm chữ số toàn chuỗi mà guard chỉ giết câu CÓ số ⇒ **tập cứu RỖNG**; bản ngây thơ còn dính lỗ ECHO tự-cấp-phép câu bịa id135. **PA-0 (đo-only, 0 đổi hành vi)** đã LIVE: 2 seam battery LUÔN BẬT · `answer_truoc_guard` + per-call ở seam · **K4** đóng băng ĐẲNG THỨC tuple loại-trừ · **K5/K5b** cấm rò vào `mcp_bridge`. Vùng mù thật: **117/179 hàng REFUSE legacy** thiếu trường.
>
> **⑤ ✅ MỤC 4 — LÁT 0 (cổng detector).** Sweep **142 file**: **4 file kích hoạt, TẤT CẢ trắc dọc thật**; **0 file kiến trúc/kết cấu/hạ tầng** (rachmop IM); đọc tay 104 lượt nhãn = **9 nhãn duy nhất, 0 rác**; **520 giá trị, 0 SỐ ÂM**. ⛔ **`G8` (thẳng hàng) = NO_GO CÓ SỐ, SAI HƯỚNG**: rác thẳng hàng **hoàn hảo 1,000** (bảng mẫu tô AutoCAD `ansi31`/`ar-conc`) còn bảng trắc dọc THẬT chỉ **0,806** (hàng "khoảng cách" ghi GIỮA hai cọc) — quét 0,50–0,90 **không ngưỡng nào tách được**. ✅ Thay bằng **G10 mật độ ≥12** (đích min 15/median 18 vs nhiễu median 2; **≥18 mất 2/5 block đích**) + **G9 cùng-bậc ≤10× ở MỨC HÀNG** (loại ghi chú giả dạng bảng). **3 lỗi bộ đo tự bắt**: G8 giả định "cột cách đều" · **cache dùng basename → gộp 20 file TRÙNG TÊN**, cả một vòng sweep chạy trên dữ liệu LAI (bắt vì D600 = 1112 = 496+616) · 4 cặp còn lại là **bản sao cùng file ở 2 thư mục** → nhân đôi mật độ (dedup 21.786 bản ghi).
>
> **⑥ ✅ MỤC 4 — LÁT 1: TOOL #36 `doc_bang_trac_doc` LIVE (`0c1d710`).** Đóng nút thắt recall thật: bảng trắc dọc ghi cao độ **KHÔNG DẤU** nên `cao_do_min_max` mù; ở đây **nghĩa của số do NHÃN HÀNG định**. Chiều cao chữ: đọc lại `modelspace` lúc gọi tool (**13ms/8.442 chữ** = 0,12% thời gian nạp) thay vì chạm `_extract` ⇒ 0 suite ảnh hưởng.
> **🔴 RED-TEAM IMPL (`wf_cd35e271`): 11 phát hiện xác minh, 5 CAO — thẩm định ghi thẳng "23 ca test tự viết KHÔNG bắt được phát hiện nào".** **3 lỗi do CHÍNH bản vá đẻ ra:** `loc_nhan` ngoài `_vitri` ⇒ tham số **model tự chọn** vào rổ neo, `nhan_chua='-600'` bơm **−600** (không tồn tại trong file) và **lật 2 câu bịa cao-độ-âm từ CHẶN sang LỌT** (đối chứng `'600'` không bơm ⇒ phân biệt được) · cap 60 `break` **CÂM** giấu chính `1.740` mà docstring nêu làm lý do tồn tại, GD2 giấu **94,5%** giá trị 0 cảnh báo · min/max tính trên tập **ĐÃ CẮT** ⇒ `gioi_han=12` báo 2.930 thay vì **2.710**, không cảnh báo, số sai nằm TRONG rổ nên guard không bắt = **SAI-TỰ-TIN (I3-U L1)**. **2 lỗi CÓ SẴN:** `handle_khong_khop` ngoài danh sách cứng — **giá trị là chuỗi tuỳ ý do model cấp**, truyền `'-13.7'` ⇒ **câu id135 từ CHẶN sang LỌT**; echo `tu_khoa` ở `tim_kiem` (**chưa vá, cần A/B**).
> **Đã vá 4 CAO + 3 TRUNG**, đáng chú ý **`_strip_handle` đổi từ DANH SÁCH CỨNG sang lọc theo TÊN KHOÁ** (danh sách cứng hỏng đúng 2 lần, cả hai IM LẶNG). **Tự kiểm ngược:** chỉ thêm 1 khoá bị loại (`anchor_handle`, đúng là handle); rổ neo 5 tool chính **không đổi một số nào** (11/11·20/20·30/30·19/19·7/7). Sau vá: min/max **bất biến 2.710** mọi `gioi_han`; `nhan_chua='đáy cống'` **lấy lại `1.740`**. Test **35 ca** (11 ca `[R]` + đối chứng R7b).
>
> **⑦ ⛔ MỤC 3 (`Ø/Ü` vào `_SIG`) — ĐO LẠI, TÁCH THÀNH HAI KẾT LUẬN NGƯỢC NHAU.** Mô phỏng bản vá trên 141.130 lượt: **`Ø` = NO_GO chắc hơn cũ** — phân loại lại 152 ứng viên bằng chính bộ kiểm âm tiết: chỉ **26 chuỗi/9 file** là TCVN3 thật (toàn tên người/địa danh), còn **126 chuỗi/37 file là KÝ HIỆU ĐƯỜNG KÍNH** (`NHÓM Ø<=10(kg)`) ⇒ hại/lợi ≈ **4:1**; mô phỏng phá `'Cống tròn Ø1,50m'`→`'Cụng trũn ỉ1,50m'`. **`Ü`**: 49 chuỗi cứu, 0 phá trên corpus, nhưng ca phản chứng **5/5 phá** tên hãng (`Müller`→`Mỹller`). 🆕 **Điều đã đổi:** bộ kiểm âm tiết viết cùng ngày **giải được** bài toán tách (`nghÜa`→`nghĩa` = G, còn `Müller`/`Zürich` chặn 4/4) ⇒ B1-Ü chuyển từ *"không có cách an toàn"* sang **"có cách an toàn nhưng CHƯA ĐÁNG"** (49 chuỗi/2 file, nội dung tên riêng, **0 chuỗi mang khối lượng**).
>
> **📌 BÀI HỌC PHIÊN NÀY (đã ghi vào checklist + memory):**
> **(a) `.pyc` CŨ LÀM CỔNG CHO KẾT QUẢ SAI** — vá **một ký tự** nên file cùng size, khôi phục **cùng giây** ⇒ Python xác thực cache bằng (mtime, size) độ phân giải GIÂY nên nạp bytecode **bản đã gỡ vá**; cổng FAIL, chạy tay cũng FAIL ⇒ trông y hệt bug thật. **Chiều ngược lại = CỔNG XANH OAN.**
> **(b) TEST TỰ VIẾT KHÔNG THAY THẾ ĐƯỢC RED-TEAM** — 23 ca PASS hết mà 5 lỗi CAO lọt, 3 trong đó do chính bản vá đẻ ra.
> **(c) DANH SÁCH KHOÁ CỨNG LÀ BỀ MẶT DỄ QUÊN** — ưu tiên lọc theo hình dạng tên / allowlist-of-one-key.
> **(d) Bộ đo hỏng 6 lần trong phiên, tự bắt hết**: G8 giả định cột-cách-đều · cache gộp file trùng tên · script kiểm lấy nhầm file BD/CN · tiêu chí "rổ ⊆ rổ-không-lọc" sai (lượt không-lọc bị cap che) · bộ trích thô đọc `'29.5-29.95'` thành số âm · phép kiểm rò rỉ không phân biệt được nguồn số.
>
> **⏳ VIỆC CHỜ (phiên sau):** ① **lát 4 routing-nudge** (`cao_do_min_max` 0-marker → trỏ #36; **phải A/B**, không đụng SYSTEM_PROMPT) · ② echo `tu_khoa` ở `tim_kiem` (A/B riêng) · ③ trần công việc O(block×chữ) cho #36 (đề xuất sort+bisect, giữ nguyên ngưỡng) · ④ **PA-2/PA-3** đọc bảng tổng quát (id37) — **phải có lát-0 riêng**, không tái dùng gate PA-1 · ⑤ mục 3 `Ü` nếu user muốn dọn sạch danh sách · ⑥ nhóm C vẫn hoãn. **Chờ file ngoài:** F1 (cao độ ĐÁY THIẾT KẾ ≤ −5m) · F2 bảng bóc khối lượng làm tay.

---
## Session 2026-08-02 (nối 2) — ✅ MỤC 1 **VNI vớt tầng 2** (78/79, 0 phá) + ✅ MỤC 2 chốt **DƯỚI NGƯỠNG** (PA-0 đo-only)
> **CHỐT SỔ:** HEAD **`6b7c2b9`** ← `7030aa6` ← `dabcaac` ← `0cb25e6`. check.sh **[48/48] PASS**, tổng ca **1.630 → 1.633 → 1.645**, 35 tool, 0 regress; mỗi lát diff từng suite chỉ đổi ĐÚNG suite của lát. `feature_list` **80 → 82** (70 done). Quy trình: cả 2 mục đều nghiên cứu bằng workflow 7-agent (probe → design → 3 phản biện đối kháng chạy số trên corpus/battery THẬT) TRƯỚC khi viết dòng code nào.
> **① MỤC 1 — VNI vớt tầng 2 (`wf_666cedfd` → `6b7c2b9`):** thay bằng-chứng-cứng KÝ TỰ bằng bằng-chứng ÂM TIẾT (G/A/XẤU; bắn ⟺ ≥1 G ∧ 0 XẤU). Vớt **78/79 chuỗi (180/181 lượt), 0 vớt-sai, 0 phá `TOÀ/HOÀ`, 0 lệch số**; sweep 97.406 chuỗi trên cây thật khớp từng con số; to_unicode +9,3%. `test_vni` 43→55, tự kiểm ngược 8-đỏ-đúng-8. Giới hạn khoá test: E3b cặp=1 · E3d `T.CHIEÀU` · E3e residual trộn · **lớp Ì/Í = lát riêng**.
> **② MỤC 2 — rổ neo rỗng (`wf_06b6cf5e` → `7030aa6`):** 832 lượt → 179 REFUSE → **oan thật 1 hiện tượng (id69) < ngưỡng 3 ⇒ KHÔNG đổi hành vi**. ⛔ PA-2 = NO_GO CẤU TRÚC (kho cấm chữ số + lỗ echo). PA-0 đo-only: 2 seam luôn bật + `answer_truoc_guard` + per-call + K4 đẳng-thức-tuple + K5 cấm-rò. Vùng mù legacy 117/179 hàng. Tripwire ≥3. **Chờ user quyết:** entry kho `Ø/phi` (id69 miss→hit, đổi kb_hash).
> **③ Bài học mới:** `.pyc` cũ làm cổng cho kết quả SAI (vá 1 ký tự + khôi phục cùng giây) — chiều ngược = CỔNG XANH OAN; luật xoá `__pycache__` trước cổng, memory `[[feedback-stale-pycache-lam-cong-sai]]`. Corpus cache `_khao_sat/_dxf` có **3 file hỏng do audit=0** (gồm `chinhcaodo.dxf`) — cần convert lại, việc nhỏ ghi sổ.

---
## Session 2026-08-02 (nối) — 🧪 KIỂM **F1 KHÔNG ĐẠT** (có số) + 🐛 vá **ODA audit=0 sinh .dxf CỤT** (thất bại IM LẶNG)
> **CHỐT SỔ:** commit **`0cb25e6`** — ⏳ **CHƯA PUSH** (push bị bộ phân loại quyền chặn, user tự chạy). check.sh **[48/48] PASS · 35 MCP tool · 0 regress**; tổng ca **1.627 → 1.630** (+3); diff từng suite: **DUY NHẤT** dòng `dwgconv` 10→13 đổi, mọi suite khác giữ nguyên **từng con số**. `feature_list.json` **79 → 80 mục** (68 done · 1 partial · 11 deferred).
>
> **① ⛔ F1 KHÔNG ĐẠT — đối tác gửi bộ mới (57 file .dwg, 2 đơn vị tư vấn Hải Dương, 27/07/2026), đo xong bác bằng số.**
> Phần **THIẾT KẾ** sâu nhất chỉ **−4,10 m** (Bể PCCC) · **−3,95 m** (Trạm XLNT) · giao thông −2,0 · thoát nước −1,0 ⇒ vẫn **dưới ngưỡng −5m** (TB6 cũ là −2,49m, có tiến bộ nhưng chưa qua vạch).
> **Hai file DUY NHẤT đạt ngưỡng là KHOAN ĐỊA CHẤT, KHÔNG dùng được:** `MC KDC Truc Khe` −54,30m · `Tru KDC Truc Khe` −30,00m. Bằng chứng ngữ nghĩa đọc tay quanh chính handle sâu nhất: cạnh `-54.30` là `'Độ sâu hố khoan - m'`, `'(Depth of borehole)'`, `'(Layer depth)'`, `'Mẫu đá'`; cạnh `-30.00` là `SPT16`, `D16`, `29.5-29.95`. ⇒ **độ sâu KHẢO SÁT, khác hệ** — đúng loại đã làm `cao_do_min_max` KT trôi −2.1 → −94.44. Dùng nó tuyên bố "đậu" = lặp lại đúng lỗi đã phải **rollback 2026-07-24**.
> 📌 **BỘ TRÍCH CỦA TÔI HỎNG (lần thứ 8):** bản quét thô đọc `'29.5-29.95'` (khoảng độ sâu mẫu) thành số âm −29,95 ⇒ báo "engine bỏ sót". **Engine ĐÚNG, bộ trích SAI.** Lại đúng khuôn `[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`.
> **Phát hiện phụ (chưa làm):** `Cat doc cong D600` có **24–36 lần chữ "cao độ"**, **8 lần "đáy cống"**, 197–293 số thập phân trên layer `tracdoc` — nhưng `cao_do_min_max` trả **0 marker**, vì cao độ trong **bảng trắc dọc ghi KHÔNG DẤU** (`1.740`, `3.270`) mà engine chỉ nhận marker `+/−/±`. ⇒ **ca THẬT cho nút thắt ghép nhãn↔giá trị (R3)**, thay cho lý thuyết.
>
> **② ✅ VÁ `dwgconv.py:97` audit `"0"` → `"1"` — bug NGƯỜI DÙNG gặp mà DEV không bao giờ thấy.**
> Tham số 7 của ODAFileConverter là **audit**. Với `.dwg` lỗi cấu trúc, ODA **VẪN sinh ra** `.dxf` nhưng **CỤT** (thiếu `ENDSEC`) ⇒ `outs` không rỗng ⇒ `convert_dwg_to_dxf()` **trả về file hỏng MÀ KHÔNG BÁO GÌ**.
> ⚠ **So sánh đầu tiên của tôi KHÔNG SẠCH** (đổi `recurse` và `audit` cùng lúc) — đã **cô lập biến** rồi mới kết luận.
> **A/B TOÀN BỘ 148 file .dwg** (92 corpus + 56 bộ mới), cùng thư mục nguồn, cùng `recurse=0`, **chỉ đổi audit**: **CỨU 10/147 = 6,8%** · **HỎNG THÊM 0** · 123 file cả hai đọc được thì **121 file SỐ Y HỆT**; **2 file lệch DUY NHẤT `tong_doi_tuong`** (8531→8530, 10701→10672) trong khi `cao_do_thap`/`cao_do_cao`/`so_doan_chu`/`so_kich_thuoc`/`thep_tong_kg`/`so_marker_cd` **giữ nguyên từng con số** (kể cả −54,30) ⇒ audit chỉ bỏ **đối tượng HỎNG**, không mất dữ liệu có nghĩa · 14 file cả hai đều lỗi: **TẤT CẢ** do trần 45MB của chính dự án.
> **Giá phải trả, đo được:** +27,5% thời gian (252,7s → 322,2s cho 147 file = **+0,47s/file**); file 36,33MB (lớn nhất dưới trần) **24,3s → 30,4s**, còn xa `CONVERT_TIMEOUT=600s`; dxf đầu ra **CÙNG kích thước 202,4MB** ⇒ audit **không phình** file lành.
> 📌 **VÌ SAO CHƯA TỪNG LỘ RA:** trong 10 file được cứu có **`chinhcaodo.dwg` của BỘ TB6** — 988 đoạn chữ, 98 đường kích thước, **200 marker cao độ**. Corpus **không có bản `.dxf`** của nó, dev luôn làm việc trên `.dxf` có sẵn nên **không đi qua `dwgconv.py`**; chỉ **upload .dwg** mới đi đường đó — tức đúng đường của đối tác.
> **Test:** ca `[G]` khoá cờ audit (10 → 13 ca). **Tự kiểm ngược:** hạ về `"0"` thì **đúng ca AUDIT đỏ**, hai ca kia vẫn xanh ⇒ ca test **phân biệt đúng chỗ**.
>
> **③ 📌 BÀI HỌC QUY TRÌNH MỚI — `.pyc` CŨ LÀM CỔNG SAI (đã ghi memory).**
> Lần chạy cổng đầu **sau** vá báo **FAIL**, chạy tay cũng FAIL ⇒ trông y hệt bug thật. Thực ra: vá **một ký tự** (`'0'`/`'1'`) nên file **cùng size**, và `cp` khôi phục **trong cùng một giây** với lần compile trước (`.pyc` 19:49:20.**343** vs `.py` 19:49:20.**423**) ⇒ Python coi cache còn hợp lệ, **nạp bytecode của bản ĐÃ GỠ VÁ**. Xoá `__pycache__` → **[48/48] PASS**.
> ⚠ **Chiều ngược lại nguy hiểm hơn nhiều:** cache cũ là bản ĐÚNG trong khi `.py` đã hỏng ⇒ **CỔNG XANH OAN, không có gì báo.** ⇒ **LUẬT: sau bất kỳ vòng gỡ-vá-rồi-khôi-phục, PHẢI xoá `__pycache__` trước khi chạy cổng.** Memory `[[feedback-stale-pycache-lam-cong-sai]]`.
>
> **⏳ CÒN TỒN / VIỆC CHỜ:** `dwgconv.py:104` vẫn trả file cụt không báo gì nếu ODA sinh `.dxf` hỏng (với audit=1 **không xảy ra trên 147/147**, nhưng cơ chế thất-bại-im-lặng còn nguyên — **cần đo riêng**) · **F1 vẫn chờ file** hạ tầng có **cao độ ĐÁY THIẾT KẾ ≤ −5m** (phải nói rõ với đối tác: **hố khoan địa chất KHÔNG dùng được**) · bộ 56 file đối tác **CHƯA nhận vào corpus** (user chốt để sau) · dữ liệu đo để tại `D:\Dat-Antigravity\_f1_check\` (6,06 GB, user chốt giữ nguyên).

---
## Session 2026-08-01→08-02 — 🔎 NHÓM A: **5 việc VÁ LIVE** (A3 mã-định-dạng · tool #35 trang in · A2 · A3 trích-dẫn · **BẢNG MÃ VNI**) + **7 NO_GO có số** + sửa 2 nhãn "done" SAI
> **CHỐT SỔ:** HEAD **`45acd2f`** == origin, tree SẠCH. check.sh **[48/48] PASS · 35 MCP tool · 0 regress** — ở **MỌI lát**, các suite CŨ giữ nguyên **TỪNG CON SỐ**; tổng ca **1.467 → 1.627** (+160), check.sh **42 → 48 bước**, MCP tool **34 → 35**.
> **LIVE verify 7 lần** (`af0c879` → `639fa6c` → `349e82a` → `a61472d` → `363e980` → `e57ee22` → `45acd2f`), mỗi lần đủ 4 mục: prompt `2026.07.27-kb-l3` hash `239e8b7b…` **KHÔNG đổi** · kb `e55ac112…` **KHÔNG đổi** (không lát nào chạm SYSTEM_PROMPT/kho kiến thức nên không cần A/B) · `/health` ok, `ram_mb` 135,4 · trang chủ HTTP 200 đủ 4 chuỗi frontend.
> `feature_list.json` **69 → 79 mục** (66 done · 1 partial · 12 deferred). **13 commit:** `af0c879` (A3 mã-định-dạng) · `639fa6c` (3 NO_GO) · `349e82a` (tool #35 + NO_GO tổng-hợp) · `a61472d` (A2) · `363e980` (NO_GO cờ tự-cộng + giữ xếp lớp #35) · `e57ee22` (A3 trích-trang-in) · 5 commit docs.
> **CÂN ĐỐI PHIÊN — 5 việc VÁ THẬT vs 7 hướng ĐÓNG BẰNG SỐ.** Vá: **A3 mã-định-dạng** (bớt 11.597 hit ảo) · **tool #35** đọc chữ trang in · **A2** (thôi khẳng định sai về bản vẽ) · **A3 trích-dẫn** (lấy lại câu đúng bị xoá oan) · **BẢNG MÃ VNI** (cứu 852 chuỗi; *"phòng"* 0→33 trên file gốc của vấn đề). NO_GO có số: C1(Φ) · B1(Ø/Ü) · E2-cờ-trang-in · "câu tổng-hợp bị giết" · A2-phương-án-rộng · A2-phương-án-nhắc-lại · cờ "số do máy tự tính".
> **📌 Phần lớn giá trị nằm ở chỗ những thứ TRÔNG ĐÚNG đã bị bác BẰNG SỐ trước khi kịp gây hại** — ít nhất **3** trong số đó nếu code thẳng sẽ **mở lại đúng lớp lỗi id135** mà dự án tốn nhiều công mới bịt (rõ nhất: A2-phương-án-rộng làm **vỡ `test_grounding_guard:137`**, ca test đang khoá hành vi ĐÚNG).
> **📌 SỔ SAI SÓT CỦA CHÍNH TÔI TRONG PHIÊN (tự bắt hết):** **6** bộ trích/bộ kiểm hỏng — 2 tautology (luôn trả 0 bất kể đúng sai), 1 ca test không phân biệt được, 1 cắt cụt dữ liệu (400 chuỗi/file), **1 sai ĐƠN VỊ + 1 sai MẪU SỐ đã kịp vào tới CODE** · **7** lần assert sai mà code đúng (khuôn lặp: giả định một câu kích guard trong khi `do_luong` rỗng nên guard **thoát sớm**) · **3** giả thuyết sai · **1** tác dụng phụ do chính bản vá (tuple loại-trừ 3→4 tool). Công cụ bắt được tất cả: ***"phép đo này CÓ THỂ ra kết quả KHÁC được không?"***
>
> **① SỬA HAI NHÃN "done" SAI (`wf_4efbe809-21b` — 4 đo + 4 phản biện, 0 phép đo bị bác).** User hỏi *"1.02 và 1.03 xong rồi đúng không?"*; tôi trả lời "1.03 ✅ xong" — **SAI**. Mục 1.03 có tiêu đề **BA VẾ** (*"nắn phông cũ (**VNI**, TCVN3 còn sót, ký hiệu Ø vỡ)"*) mà mới làm 2: vế **VNI = 0 dòng code** (`grep VNI` ra 2 hit đều là chú thích), nắn đúng **0/1.422 = 0,0%**, và `test_vntext` **53 PASS nhưng 0/53 ca chạm VNI** ⇒ **cổng không thể đỏ dù vế đó chưa bắt đầu**. E2E: gõ *"phòng"* → **0 kết quả** trên file có 34 đoạn `PHOØNG HOÏC`; cùng file *"phòng"* (phần TCVN3) = 51 ⇒ engine đúng, thiếu bảng mã. **Nặng hơn bỏ sót — khớp SAI TỰ TIN:** `tim_kiem('nhà để xe')` = 3 khớp vào `NHAØ XE GIAÙO VIEÂN` dù bản vẽ **không có chữ "để"**. 1.02 cũng chỉ xong nửa (khối được chèn qua tool #34; **trang in mù hoàn toàn** 851 chuỗi/24 file, và `co_o_vung_chua_doc = None` ⇒ **thất bại IM LẶNG**). ⇒ `vntext` **done → partial**, thêm mục `doc-chu-trang-in-paperspace`. **4 số cũ của dự án bị phản biện sửa** (768 → cận dưới 1.422 · "21/92 file VNI" → 10/91 · "907/907=100%" là **tautology** · "0 chuỗi hỏng thêm" không tuyệt đối: 944 chuỗi VNI bị đem giải mã TCVN3).
>
> **② A3 ✅ LIVE `af0c879` — mã định dạng không còn làm mồi khớp ảo.** `search_texts` ghép nhánh **THÔ** chưa gỡ mã vào rổ so khớp ⇒ tên phông/mã màu/mã AutoCAD thành **chữ để khớp**. Dự án **đã biết từ đợt trước** (`tools_core.py:301-303`) mà chưa ai quay lại vá. **Kênh lớn nhất KHÔNG phải tên phông mà là `%%C`**: `%%C10` → `%%c10` chứa `c1` ⇒ hỏi cột **"C1"** trả về **mọi ghi chú thép Ø10/Ø12/Ø16** (9.147/11.597 hit ảo). Vá **3 chỗ một lát** (P1 `_mtext_codes` toggle-gỡ-trước + giữ `\S` + `ma_ve_trang` · P2 `_tho_khop` fail-open + cổng rẻ · P3 bỏ nhánh thô khỏi `_build_qty_index`). **Hai chỗ gỡ mã NGƯỢC NHAU**: nhánh thô = **khoảng trắng** (gỡ rỗng thì **đẻ ra chữ "thép" không có thật**), `to_unicode` = **giữ rỗng** (khoảng trắng **chẻ số thật**: `mác 200#`→`mác 2 0 0#`). **Tự kiểm ngược 95 file/2.652.196 chuỗi:** `vn` đổi 437 · đổi ngoài 2 họ **0** · `vn` ngắn đi **0** · **6 đại lượng số lệch 0** (15/15 file) · hit chữ-thuần **−0,3%** (toàn bộ là ca bug) · hit có-chữ-số **−31,6%** · regex gỡ mã: 4.989 lượt, **10/10 chữ cái đều là mã MTEXT chuẩn, 0 lượt khớp chữ lạ**. **Lợi ích phụ:** 437 ca đều CỨU dữ liệu — `(D)` → `(D1)/(D2)/(D3)` (trước đây **3 mã sập thành 1**).
>
> **③ BA NO_GO CÓ SỐ `639fa6c` (`wf_3e934400-206` — 3/3 phản biện `bac_bo=true`, agent thiết kế tự chạy lại 4 phép đo, cả 4 đứng về phía phản biện):** · **C1 (Φ→Ø): TIỀN ĐỀ SAI** — `_norm('Φ10') == _norm('Ø10')` ⇒ **tìm kiếm đã khớp Φ rồi**; nếu vẫn vá thì là per-claim thu nhỏ, **giết 17/26 câu đúng** đổi lấy đóng 1/6 cách diễn đạt mà Gemini **ít dùng nhất**; sự cố thật **0**. · **B1 (Ø/Ü vào `_SIG`):** số panel thổi **1,8-2,0× do đếm đôi**; hàng rào bảo vệ đường kính là **MÃ CHẾT** (0/5.797, không thể khác 0) và **thua đúng một dấu cách**; lớp hỏng thứ 2 cả hai panel bỏ sót: `Müller`→`Mỹller`. · **E2 (cờ trang in):** panel **đo sai chỗ 7,9×**; lợi ích thật **7/893 chuỗi mang giá trị đo, 6/7 ở rachmop** ⇒ trừ ra còn **1 chuỗi toàn corpus**; nudge khẳng định *"cụm từ đang tìm CÓ ở đó"* mà khớp vào **TÊN NGƯỜI** `'pgđ. hồ chí sơn'` = **ép bịa có chữ ký**. Thay bằng **E2(a)** cảnh báo tĩnh + **E2(b)** tool đọc trang in (bắt buộc loại khỏi rổ neo cùng commit).
>
> **④ 🆕 PHÁT HIỆN MỚI KHI TỰ KIỂM NGƯỢC CA TEST:** câu tổng-hợp **ĐÚNG** viết bằng **`Ø`** — cách viết phổ biến nhất — **HÔM NAY ĐÃ BỊ HÀNG RÀO GIẾT** (`Ø` vốn trong `_MAHIEU_RES[4]` nên `Ø6/Ø8/Ø10` bị strip ⇒ chỉ còn số tổng mà tổng không có trong rổ neo ⇒ chặn). Lỗi này **KHÔNG do bản vá Φ đẻ ra, nó có sẵn**. Nghi là một phần của **M2 = 8,7%** trong baseline Q2. Đã **KHOÁ** hành vi bằng ca `P2c`; **chưa vá, chưa đo** — đầu mục mới.
>
> **📌 BÀI HỌC PHIÊN NÀY — HAI CÁI, ĐỀU ĐẮT:**
> **(a) Dạng MỚI của "cổng xanh không đủ":** hai lần trước là *bản vá chạy mà cổng mù*; lần này là **một PHẦN VIỆC CHƯA BAO GIỜ BẮT ĐẦU mà cổng vẫn xanh**. ⇒ **LUẬT: đầu mục có tiêu đề NHIỀU VẾ thì phải tách từng vế và đòi MỘT CON SỐ cho MỖI vế trước khi đánh dấu xong; và hỏi "suite hiện có bao nhiêu ca chạm vế này?" — nếu 0 thì cổng xanh không nói gì về vế đó.**
> **(b) BA lần bộ kiểm của chính tôi hỏng, đều tự bắt:** ① bộ phân loại "mất oan" định nghĩa mất-oan = *token có trong `vn`* ⇒ **luôn trả 0 do CẤU TRÚC** ② bộ kiểm "đoạn bị xoá có phải mã không" cũng gần tautology ③ ca test C1 bản nháp đầu **không phân biệt được** vì để số tổng vào rổ neo (mô phỏng bản vá bị bác mà vẫn xanh). ⇒ **Câu hỏi phải tự hỏi trước khi tin bất kỳ số nào: "phép đo này CÓ THỂ ra kết quả KHÁC được không?"** Nếu không thì nó vô nghĩa. Cộng 2 ca test tự viết hỏng khác: A7 đậu vì chuỗi **thiếu token**, E2 so `None == None`.
> **⑤ QUÉT ĐỦ CORPUS + E2(b) TOOL #35 — LIVE `349e82a`, gate [45/45], 35 MCP tool.**
> **Quét 95/98 file lần đầu (trước luôn thiếu file to nhất) — LẬT NGƯỢC CẢ HAI GIẢ ĐỊNH:** chuỗi chỉ-ở-trang-in **851/893 → 2.721** (3×, 24/95 file) NHƯNG chuỗi **mang giá trị đo** chỉ **10/2.721**, **9/10 trong `rachmop.dxf`** (đã có trong battery) ⇒ **ngoài rachmop toàn corpus còn ĐÚNG 1 chuỗi** (`d315-HDPE-l421m-I=0.33%`). 🔴 **File 202MB tên `…-trangin-chiHoa.dxf` — thứ HAI vòng nghiên cứu trước đều DỪNG LẠI ĐỂ CHỜ — đo ra `0` chuỗi. Điều kiện tiên quyết cũ đuổi theo CHỖ TRỐNG suốt hai vòng.** File đóng góp nhiều nhất (1.517 chuỗi = 56%) có **46,3% là lưới toạ độ**.
> **Tool #35 `doc_chu_trang_in`:** chỉ trả chuỗi KHÔNG có ở modelspace · kho dựng LƯỜI, **KHÔNG nạp `self.texts`** · chặn khớp mù dấu · fail-open · trần 40/mặc định 15. E2E: hỏi `"lưu vực"` → **15 kết quả**, `tim_kiem` → **0**. **⛔ Loại khỏi rổ neo CÙNG LÁT — đo LIVE, không phải phòng xa:** không loại thì tool bơm **dãy âm liền −1,0…−10,0** sinh THUẦN từ **SỐ TỜ** (`… TB.6 -7/10`) ⇒ bảo lãnh **cao độ âm TRÒN bịa** = lớp lỗi id135. **Nói thẳng: tool KHÔNG giúp bóc khối lượng**, nó trả lời *"bản vẽ này là gì"*. Test 20 ca (T3b **chứng minh** loại-trừ là cần thiết).
>
> **⑥ ⛔ NO_GO "câu tổng-hợp ĐÚNG bị hàng rào giết" — GIẢ THUYẾT CỦA TÔI SAI (`wf_028146eb-439`).**
> Ba đối chứng bác thẳng: câu **không có `Ø` nào** cũng **CHẶN Y HỆT** ⇒ strip KHÔNG phải nguyên nhân · câu **bịa thuần** viết `Φ` thì **ĐI QUA** ⇒ nhánh `Φ` là **LỖ**. ⇒ **Tôi đã lấy MỘT LỖ HỔNG làm chuẩn mực rồi kết luận hành vi đúng là sai; vá theo hướng đó = NHÂN BẢN LỖ.** Bản chất thật: **model phá luật `_P_R2` (cấm tự cộng)**, hàng rào chạy ĐÚNG — id193 trên **cùng bản vẽ cho 6 giá trị khác nhau** (1344.33/3545.9/1384.83/161.21/80,52/76.9) ⇒ ≥5/6 SAI, trong khi tool **đã trả sẵn tổng**. Vá thì **cứu 0 câu**, đổi lấy **8,3% neo miễn phí + 17,8% bịa lọt thêm**; "người bảo lãnh" là **chữ số hex của HANDLE**, tiết diện `40x80x2mm`, mác `M200`.
> **🔴 LỖI THẬT — VÀ BẢN VÁ CỦA CHÍNH TÔI VỪA NỚI BỀ MẶT CỦA NÓ:** model **chỉ** gọi tool trong tuple loại-trừ ⇒ rổ neo RỖNG ⇒ trả *"Không có thông tin này trong bản vẽ"* = **SAI SỰ THẬT** (id69: bản vẽ CÓ 4.817 thanh Ø10; cùng câu, lượt gọi `thong_ke_thep` thì trả lời ĐÚNG ⇒ **ROUTING**). Danh sách vừa đi **3 → 4 tool** vì tôi thêm `doc_chu_trang_in`. Loại trừ vẫn ĐÚNG và BẮT BUỘC nhưng **KHÔNG MIỄN PHÍ** — đã ghi sổ kèm hướng sửa (đổi NHÁNH XỬ LÝ, **không nới rổ neo**).
> **⛔ ĐÍNH CHÍNH khuyến nghị đang lưu hành:** `answer_goc` **KHÔNG** phải văn bản trước hàng rào (`mcp_bridge.py:994`/`:1008` đều gán `_goc = _guard_text(...)` = ĐẦU RA) ⇒ ghi nó vào log để phân tích hàng rào là **vô ích**. **CHƯA BIẾT:** 26/36 ca REFUSE không phân loại được — đó mới là kích thước vùng chưa biết, **không phải 0**; suy đoán trước **sai 50%** (id105/id189 bị quy oan, thực ra guard **thoát sớm**).
>
> **⑦ ✅ A2 — RỔ NEO RỖNG *VÌ CHÍNH SÁCH* KHÔNG ĐƯỢC KHẲNG ĐỊNH "BẢN VẼ KHÔNG CÓ" — LIVE `a61472d`, gate [46/46].**
> **HAI PHƯƠNG ÁN HIỂN NHIÊN CỦA CHÍNH TÔI ĐỀU NO_GO:** **(A)** điều kiện rộng *"rổ neo rỗng + đã gọi tool"* **bắn trúng ĐÚNG lớp lỗi id135** (`tim_kiem` chạy THẬT trả `{}` rồi model bịa `-10m` — ở đó REFUSE là câu **ĐÚNG**) ⇒ **làm vỡ `test_grounding_guard:137`**; còn bắn trúng câu hỏi TỒN TẠI (id139) và **ghi đè lời từ chối trung thực do chính model viết**. Lý do cấu trúc: **`REFUSE_MESSAGE` gánh HAI vai** — **≥22/36 lượt** REFUSE toàn corpus nằm trên id mà `ky_vong` **ĐÒI** khẳng định-vắng-mặt. **(B)** ép model gọi lại tool có số: giả định cốt lõi có **0 phép đo**; số lợi ích "3/3 id" là **TAUTOLOGY** (~10 lượt/id ⇒ "tồn tại ≥1 lượt đúng" gần như chắc chắn theo cấu tạo mẫu); **bằng chứng ngược:** câu ĐỊNH TÍNH đúng của id69 **đã đi qua hàng rào sẵn** ⇒ bệnh là *"một con số tình cờ"*, nên (B) sẽ **ép model nhét số vào câu vốn định tính**.
> **✅ (A2) hẹp — phát hiện then chốt: tuple loại-trừ chứa HAI LỚP NGỮ NGHĨA NGƯỢC NHAU.** DIỄN GIẢI (`tra_ky_hieu`, `doc_chu_trang_in`) rỗng **do chính sách** ⇒ *"chưa tra được"*; PHÁT HIỆN TỒN TẠI (`doc_bang_nhung`, `phat_hien_bang_ve_net`) thì **khẳng định vắng mặt MỚI là đáp án** ⇒ giữ REFUSE. Hàm `_a2_khong_tra_duoc` cắm ở **cả hai** call-site, **4 vế** mỗi vế chặn một rủi ro đo được; `_apply_i1` vá tường minh. Thông điệp **đo trước khi viết**: 0 chữ số · `_answer_numbers → ([],[])` · **điểm bất động**. Test **23 ca**; **tự kiểm ngược: gỡ vá thì D1/D2/D3 ĐỎ, G1(id135) XANH cả hai phía** ⇒ suite phân biệt được.
> ⚠ **Helper `run_e2e` (`test_grounding_guard:44`) HARD-CODE tool `"tim_kiem"`** — đó là lý do **6 file test hiện có đều MÙ** với lớp lỗi này.
> **📌 GIÁ TRỊ THẬT:** **KHÔNG lấy lại câu trả lời đúng nào** (0/5 lượt kích). Chỉ đổi một **khẳng định SAI về bản vẽ** thành câu **trung thực**, tần suất **0,18%**. **Đừng trích như cải thiện recall.**
>
> **⑧ ⛔ CỜ "SỐ DO MÁY TỰ TÍNH" = NO_GO + ✅ KIỂM LẠI XẾP LỚP TOOL #35 = GIỮ (`363e980`).**
> **Cờ tự-cộng NO_GO — không đạt ngưỡng ĐẶT TRƯỚC:** cần **≥3 hiện tượng ĐỘC LẬP**, đo được **1** (đúng bảng inox 9 dòng, 1 file). Mở rộng 3 trục (33→**195 câu có rổ neo thật** · **637 câu** rổ siêu-tập · **832 câu** trục khác) → **0 hiện tượng mới**. **Đã kiểm chống-tautology:** cơ hội sinh hiện tượng #2 **CÓ tồn tại** (ketcau có 4 ô "TỔNG KHỐI LƯỢNG" rời rạc) — model **đơn giản là không tự cộng ở đó**. "Báo oan 0%" **bị quần thể ép** (chỉ 1/20 lượt có cơ hội bắn oan); dựng được **4 chế độ báo oan tái hiện trên chính bản vá**, và **4 ca bắn thật thoát báo-oan CHỈ VÌ model tình cờ XUỐNG DÒNG**. Thiết kế đã siết + đóng băng.
> **Xếp lớp tool #35: GIỮ** — lập luận CƠ CHẾ: guard **thoát sớm** khi câu không có số đo, mà câu vắng-mặt hầu như không mang số ⇒ A2 gần như **không có cửa** làm tệ đi (đo văn phong thật: đổi 5/40 = 12,5%; cả 5 ca đó `REFUSE_MESSAGE` **vi phạm chính `_P_R8c`**). **⛔ RÀNG BUỘC SỐNG CÒN:** an toàn do **MỘT TÌNH CỜ** giữ — tool #35 **không gọi `_gan_canh_bao_nhung`** (14 chỗ khác CÓ gọi); ai gắn vào là lớp lỗi "A2 làm câu ĐÚNG tệ đi" nhảy từ **0 ca** sang **phổ biến**. Đã ghi cạnh code + **khoá 3 ca test** (có đối chứng chống-tautology).
>
> **⑨ ✅ A3 — NEO-THEO-TRÍCH-DẪN, LIVE `e57ee22`, gate [47/47], 0 suite cũ đổi số, +21 ca (1.563→1.584).**
> **Giả thuyết của tôi ("bị giết là vô hại") SAI — nhưng sai theo hướng CÓ LỢI.** Đọc tay **20/20** chuỗi bị giết: **7 kích thước THẬT** · **6 danh tính công trình** · 7 rác · **0 lưới toạ độ, 0 số tờ, 0 tỉ lệ, 0 mã hiệu** (chúng cho `do_luong=[]` ⇒ guard **thoát sớm** ⇒ không bao giờ vào tập bị giết) ⇒ **tập bị giết TỰ LỌC về đúng phần có nghĩa**, 13/20 là dữ liệu thật.
> **⛔ HAI SỐ TÔI ĐÃ GHI VÀO CODE ĐỀU SAI — lần đầu trong phiên số sai kịp vào tới CODE:** *"60,8% chuỗi có chữ số"* **sai ĐƠN VỊ** (đo "có chữ số", không đo "bị giết"; đúng **20/621 = 3,2%**) · *"2.721 chuỗi/24 file"* **sai MẪU SỐ** (bộ quét riêng chui vào **ATTRIB của INSERT**; kho thật **18 file/2.180 lượt/621 chuỗi**; `Ket Sat 3T12P`: quét **313** vs thật **3**). Đã sửa 3 chỗ; **tự đo lại bằng chính hàm sản phẩm**, ra khớp.
> **Bản vá:** giữ câu khi **MỌI** số nằm **trọn** trong đoạn trích **nguyên văn ≥12 ký tự** khớp chuỗi tool đã trả trong **chính lượt đó**, kèm cờ, **không** bơm rổ neo, **fail-closed**, cắm **cả hai** call-site **trước** A2. **Ba quyết định đều vì bản ngây thơ ĐÃ ĐO RA HỎNG:** `all` chứ không `any` (ANY lọt **10-12/12 ca ăn theo**) · gộp vùng **riêng từng chuỗi** (gộp chung thì **khâu vá** đuôi-A với đầu-B **đẻ ra số 31.5 không có ở đâu cả**) · số A3 **không vào rổ neo**. K=12 là **đo** (K=16 tụt còn 3/5).
> **⚠ MÓN NỢ KỸ THUẬT THẬT:** `_a3_do_luong_vitri` là **bản NHÂN BẢN** của bộ trích số **nằm trong đường chống-bịa** — ai sửa `_MAHIEU_RES`/`_DEM_NUM_RE` mà quên thì **hai bản trôi lệch ÂM THẦM**. Khoá bằng ca bất biến, tự đo **2.042 chuỗi/câu → 0 lệch** (326 câu có số đo ⇒ không tautology).
> **📌 RỦI RO TỒN DƯ + ĐÁNH ĐỔI, nói thẳng:** model trích **ĐÚNG** nhưng **gán SAI NGHĨA** (`Tel: 0220.3855952` → *"chiều dài tuyến 220,38 m"*), **4/17** số cấp phép thuộc loại này. Quy mô chỉ **0,18% lượt** và **KHÔNG phải lỗi an toàn** ⇒ thiết kế tự đánh giá *"đáng làm nhưng ƯU TIÊN THẤP"*. **Bảng mã VNI đáng làm trước nhiều.**
>
> **⑩ ✅ BẢNG MÃ VNI-Windows — VIỆC NHÓM A LỚN NHẤT ĐÃ XONG. LIVE `45acd2f`, gate [48/48], 0 suite cũ đổi số.**
> Đóng **vế cuối** của mục 1.03 — chính mục mà đầu phiên phát hiện **bị đánh dấu "done" khi mới làm 2/3**. Trước vá: nắn đúng **0/415 = 0,0%**, gõ *"phòng"* ra **0 kết quả** trên file có 34 đoạn `PHOØNG HOÏC`.
> **CẤU TRÚC khác hẳn TCVN3** (bảng 1:1): VNI = **[nguyên âm] + [ký tự dấu đứng sau]** + **5 chữ đúc sẵn** (`Ñ Ô Ö Æ Ò`) — giải thích được vì sao `NGHÆ`→`NGHỈ` không theo khuôn. Bảng **15 mục dấu + 5 chữ**, mỗi mục có **bằng chứng chéo-file**; **2 ô bị LOẠI có chủ đích** (`Ì` `Í`: 0 bằng chứng, thêm vào sẽ bắn vào `KÍCH` 76 · `KÍNH` 33 · `TRÌNH` 27 · `BÌNH` 19).
> **🔴 Phản biện BÁC được cổng tốt nhất bằng ca phản chứng THẬT:** biến thể 4 nhóm hội tụ vẫn phá chữ Việt đúng — `TOÀ NHÀ HOÀ BÌNH` → **`TỒ NHÀ HỒ BÌNH`**. Chặn bằng **BẰNG CHỨNG CỨNG** (≥1 ký tự không-thể-là-chữ-Việt), tập **suy ra chứ không chọn tay** và **cố ý trừ `Ø`** (ký hiệu đường kính thép) ⇒ loại **cả một LỚP phá theo CẤU TRÚC**, vùng rủi ro **85 → 0**.
> **⛔ Không dùng TÊN PHÔNG làm cổng:** 11 file khai VNI mà **ruột TCVN3** ⇒ dùng tên phông = **phá 107.764 chuỗi đang chạy tốt**; và còn **bỏ sót** (3/16 file được cứu không khai phông VNI).
> **Ba phát hiện thứ tự:** NFC phải chạy **trước khi dò** (để cuối → hỏng thêm 0→19) · **VNI trước TCVN3 và là `elif`** (350/415 chuỗi VNI đang đi **nhầm** nhánh TCVN3; đo xác nhận **773/852**) · hai nhánh không va nhau **theo cấu trúc**.
> **Tự kiểm ngược 910.574 chuỗi/98 file, MỘT lượt:** cứu **852 chuỗi/15 file** · **0** ca "sau tệ hơn" · **0/852** thiếu bằng chứng cứng · **delta SỐ lệch 0** trên 15/15 file. **E2E LIVE** trên đúng file gốc của vấn đề: *"phòng"* **0→33**, *"tường"* 4→43, tổng 12 từ khoá **11→194**, **0 từ khoá đi xuống**.
> **⚠ Giá phải trả, đã khoá bằng ca test:** bỏ sót **93/945 = 9,8%** chuỗi VNI mà mọi ký tự dấu đều trùng chữ Việt hợp lệ (`THEÙP SAØN`, `BEÂ TOÂNG LOÙT`) — **đánh đổi có ý thức**, đúng-đắn đổi lấy recall.
> **📌 LẦN THỨ 7 BỘ PHÂN LOẠI HỎNG — SUÝT CHO KẾT LUẬN NGƯỢC HẲN:** bản đo đầu báo *"hỏng thêm 1101"* + *"2190 chuỗi chạm file bẫy"*, nghe như phải **HUỶ bản vá** — nhưng ví dụ nó gắn cờ là `CHI TIEÁT MUẾI COẼC`→`CHI TIẾT MŨI CỌC`, tức **CỨU ĐÚNG**. Hai lỗi ĐỊNH NGHĨA: *"file bẫy"* phải là **khai VNI mà ruột TCVN3** (không phải mọi file khai VNI); và *"sạch"* **không định nghĩa được** bằng "không có ký tự lạ" vì **VNI dùng lại chính chữ Việt hợp lệ làm dấu** (`GIAÙO` = A+Ù+O). **Tin số đầu tiên là vứt một bản vá ĐÚNG.** ⇒ **"Số quá XẤU" cũng là dấu hiệu bộ trích hỏng, không chỉ "số quá đẹp".**
>
> ### 🏁 CHỐT SỔ CUỐI PHIÊN — RÀ SOÁT ĐỦ (2026-08-02)
> **Cổng:** `check.sh` **[48/48] PASS**, ghi `EXIT_CODE_THAT` vào chính file output và `grep "HARNESS GATE"` trong FILE (theo đúng kỷ luật checklist dòng 43 tự dặn — đã có tiền lệ `exit 127` khiến cổng **không hề chạy** mà vẫn tưởng xong).
> ⚠ **Kiểm lại cuối phiên, KHÔNG nhớ:** `pytest` **vẫn crash** (`ValueError: I/O operation on closed file` → `no tests ran`) · **KHÔNG có `specs/specs.json`** (dùng `feature_list.json`). Hai điều này lặp lại trong yêu cầu mỗi phiên — checklist dòng 8 đã ghi.
> **Đã cập nhật `clean-state-checklist.md`** (đang lạc hậu: ghi 34 tool/42 bước, thực tế **35 tool/48 bước**) + thêm 3 mục bài học mới.
> **Rà `feature_list.json` bắt được 1 mục LẠC HẬU:** `doc-chu-trang-in-paperspace` còn ghi *"hiện MÙ HOÀN TOÀN"* — **không còn đúng** từ khi tool #35 lên LIVE ⇒ đã sửa `deferred → done` kèm trỏ sang 2 mục liên quan. Cuối cùng: **79 mục — 67 done · 1 partial · 11 deferred** (partial duy nhất còn lại là `i3-bounds-check`, đúng hiện trạng).
> **Memory:** thêm 2 mục dài hạn — `feedback-so-qua-xau-cung-la-bo-trich-hong` và `project-nhan-dien-phong-cu-vni-tcvn3`.
>
> **⏳ VIỆC ĐANG CHỜ (phiên sau, chưa mục nào được chốt):**
> ① **Lấy lại 9,8% chuỗi VNI bỏ sót** (93/945: `THEÙP SAØN` · `BEÂ TOÂNG LOÙT` · `CHI TIEÁT DAÀM`) — cần cách phân biệt `TOÀ/HOÀ` an toàn, nhiều khả năng phải có **từ điển âm tiết**; ca `E3` của `test_vni` đang khoá hành vi hiện tại.
> ② **`Ø/Ü` vào `_SIG`** — *hoãn có cơ sở*, **LÀM ĐƯỢC** nhưng chỉ 132 chuỗi = 0,0103% corpus và **không phải khối lượng**; nếu làm phải tách `Ü` riêng, `Ø` riêng.
> ③ **Rổ neo rỗng ⇒ nói sai sự thật** — danh sách loại-trừ vừa đi **3→4 tool** nên bề mặt rộng thêm.
> ④ **Nhóm C** (RAM/upload) — **HOÃN tới cuối dự án** (tốn tiền túi, user đã chốt).
> **Chờ file ngoài:** F1 bản vẽ hạ tầng sâu ≥−5m từ đơn vị KHÁC · F2 bảng bóc khối lượng làm tay của kỹ sư.
>
> **📌 BÀI HỌC BỔ SUNG:** bộ trích của tôi hỏng **lần thứ 4** trong phiên (cắt cụt 400 chuỗi/file ⇒ phân loại chạy trên 1.604/2.721, toàn bộ phần mất thuộc đúng 1 file). Cả 4 lần đều tự bắt bằng câu hỏi ***"phép đo này CÓ THỂ ra kết quả KHÁC được không?"***
> **⏳ VIỆC CHỜ:** ① **lỗi rổ-neo-rỗng trả "không có" SAI SỰ THẬT** (đã có hướng, cần tự-kiểm-ngược trước vì sẽ làm nhiều suite đổi) → ② gắn cờ "số do máy tự tính" (**GẮN CỜ, không chặn** — per-claim đã NO_GO) → ③ hoãn: B1 · A1+A2 (bảng mã VNI, việc LỚN nhất) · nhóm C.

---
## Session 2026-07-31→08-01 — 🔤 NHÓM A: 1.06 dụng cụ đo + 1.03 nắn phông (cứu 8.913 chuỗi) + 1.04 đơn vị + **Q2 baseline** + **3 NO_GO có số**
> **CHỐT SỔ:** HEAD **`b236b7e`** == origin, tree SẠCH. check.sh **[42/42] PASS · 34 MCP tool · 0 regress**.
> Suite đổi số: takeoff 272→**283** · vntext 28→**53** · garble-dia 26→**27** · **MỚI battery-runner 52**. Mọi suite khác GIỮ NGUYÊN.
> LIVE verify `/version` = `b236b7ee` · prompt **`2026.07.27-kb-l3`** hash `239e8b7b…` **KHÔNG đổi** · kb `e55ac112…` **KHÔNG đổi** · `/health` ok · `ram_mb` 135,5 · trang chủ HTTP 200 đủ 4 chuỗi frontend. **11 commit** push+deploy+verify.
> `feature_list.json` **64→69 mục** (62 done · 6 deferred · 1 partial). ⚠ pytest VẪN không chạy được · KHÔNG có `specs/specs.json`.
>
> **① 1.06 — DỤNG CỤ ĐO BỘ 198 CÂU (`68b5fcc`).** `run_battery.py` mở file bằng mode `"w"` ⇒ chạy một lần là **xoá sạch lượt trước** (và xoá luôn bản ghi lịch sử 24/07); docstring hứa "không mất tiến độ nếu gián đoạn" là **nói dối**. Viết lại: append-only tuyệt đối · mỗi lượt 1 file + sidecar meta ghi-một-lần · **mỗi dòng tự khai `prompt/kb/code/battery` hash** · `--tiep` chỉ hỏi câu thiếu và **TỪ CHỐI khi định danh đã đổi** · "hợp lệ" nhận biết bằng **CẤU TRÚC** (`"answer_goc" in r`, có ở 2 đường trả lời thật, KHÔNG có ở cả 4 đường hỏng) chứ không bằng chuỗi tiếng Việt · ép TẮT chuỗi model dự phòng. **MỚI** `do_on_dinh.py` (5 rổ, trung bình C(N,2) cặp, **không đặt ngưỡng đạt/không**). Tự kiểm ngược: gỡ bản vá → **7 ca ĐỎ**.
> 📌 **LỖI TỐN TIỀN DO CHÍNH BẢN VÁ:** `parse_args([] if argv is None else argv)` ⇒ chạy từ DÒNG LỆNH thì **mọi tham số bị vứt im lặng**, `--chay-thu` vô hiệu → chạy thật, **tiêu API 42 câu**. **49 ca test tự viết đều XANH** vì ca nào cũng truyền argv tường minh. Ca khoá `[R.11]` đi đúng đường `sys.argv`.
>
> **② 1.03 — NẮN PHÔNG CŨ (`aaea3ec`), 3 lỗi độc lập.** Ghi chú dự án nói "545 chuỗi/21 file" — **SAI ~18×**; đo lại 86 file/285.413 chuỗi: **9.680 chuỗi/73 file**. (a) **Dò quá HẸP** — `_SIG` cũ chỉ phủ ô TCVN3 hiện ra KÝ HIỆU Latin-1 nên chuỗi có mọi ô ở dải 0xC6-0xFE không bị phát hiện (`diÖn tÝch`, `THÐP`, `cèt thÐp`); thêm 22 chữ Latin không-phải-chữ-Việt, **cố ý loại `Ø` `×` `÷` + chữ Việt hợp lệ**. (b) **TỰ NUỐT Ø** — `_autocad_codes` chạy trước biến `%%C`→`Ø`(0xD8) rồi bộ giải mã ăn luôn vì 0xD8 = ô `ỉ`; **chuỗi `'thép ỉ10 neo xà gồ'` — bằng chứng chủ lực của lát L6 — là DO MÁY MÌNH TẠO RA** (raw thật `'thÐp %%C10 neo xµ gå'`). (c) **`Ð` hai nghĩa** (ô TCVN3 `é` vs chữ `Đ` viết nhái), tách theo VỊ TRÍ. + gộp NFC.
> **TỰ KIỂM NGƯỢC toàn corpus: cứu 8.913 · HỎNG THÊM 0 · Ø bị nuốt 152→0 · SỐ MÁY BÁO KHÔNG DỊCH** (cao độ KT −2.1/10.8 · KC −1.85/10.8 · HT **−14.26**/2.5). **E2E LIVE trên máy thật:** tìm "mặt bích" **3→6** · "ống HDPE" **3→6** · "cống hiện có" **4→7**, 0 mẩu garble sót.
> 📌 **BẪY ĐÃ MẮC RỒI MỚI THOÁT:** chốt *"chuỗi đã có ký tự Unicode Việt thì bỏ qua cả chuỗi"* nghe rất hợp lý nhưng làm **27 chuỗi HỎNG THÊM** — bản vẽ đổi **PHÔNG GIỮA CHỪNG** nên một chuỗi có thể nửa TCVN3 nửa Unicode.
> **CÒN TỒN:** 768 chuỗi mang `Ä Å Û Φ † „ ‚ Š` — **KHÔNG trong bảng `_TCVN3`** ⇒ họ mã KHÁC (có thể VNI-Windows); **đừng nhét vào `_TCVN3`**.
>
> **③ 1.04 — ĐƠN VỊ (`7022aad`).** Làm ĐÚNG cảnh báo cũ: **không thêm bảng tra, không tự quy đổi**. `$INSUNITS` 86 file: mm 40 · m 24 · không khai 10 · inch 9 · feet 1 · mile 1. **Khai báo sai theo CẢ HAI CHIỀU** — 9 inch + 1 feet + 1 mile thực chất vẽ mm (giá trị hay gặp nhất `110, 220, 100, 200, 300, 1200, 3000` = bộ số mm kinh điển; một file khai **mile**, trung vị 1700 → 2.736 km), NHƯNG ~9 file khai `m` thì ĐÚNG là mét (tuyến hạ tầng, trung vị 13,5-29,6 m — gồm `01-TD` chính là file id135, tức trường `_mm` đang lệch **1000×**). `$MEASUREMENT` **vô dụng** (28/38 file mm cũng để 0). Vá: `_INSUNITS_TEN` đủ 17 mã (trước inch/feet/mile bị báo là *"bản vẽ KHÔNG khai"* = **máy nói sai**) + 2 cờ BOOL prose sạch số. Tỉ lệ gắn cờ: im lặng 59% · mâu thuẫn 31% · khó tin 11%.
>
> **④ Q2 — BASELINE ĐỘ ỔN ĐỊNH N=3 (`aae3109` tiêu chí + `fcfaf6d` kết quả).** Tiêu chí đăng ký **TRƯỚC** khi chạy lượt nào (`harness/Q2_TIEU_CHI_TRUOC_KHI_CHAY.md`). 3 lượt 198/198, hỏng hạ tầng 0/0/0,5%. **M1 mâu thuẫn số 4,3% · M2 trả-lời-vs-từ-chối 8,7% · M3 = 13,0%** · macro-average 12 nhóm 7,3%. **M2 gấp ĐÔI M1** ⇒ hàng rào chống bịa đang giữ, cái chập chờn là **RECALL**. Nhóm `thep` 0%/0%.
>
> **⑤ id193 SOI XONG (`b7c8b93`) — 2 lỗi TÁCH BIỆT, cái nặng hơn thì M3 KHÔNG THẤY.** (A) đáp án nằm nguyên ở handle **`60E44`** (*"khối lượng inox lan can (inox 304): tay vịn d60 = 80,52 kg…"*), **cả 3 lượt Y HỆT 10 handle, không lượt nào có `60E44`**; truy được: model hỏi `"TỔNG KHỐI LƯỢNG"` (trả đúng 10/10 handle nó dùng) trong khi **mọi** truy vấn bám chủ đề đều ra hạng 1-2 (`lan can cầu thang` 2kq hạng 1 · `khối lượng inox` 10kq hạng 2). **Tool KHÔNG có lỗi.** (B) `_P_R2` cấm "tự cộng" nhưng model phá luật 2/3 lượt và **khi phá thì sai 1/2 số lần** (1344,33 và 1384,33 so với tổng đúng 1384,83).
>
> **⑥ BA NO_GO CÓ SỐ (`1e10d83`, `7923817`, `b236b7e`) — ĐỪNG LÀM LẠI:**
> · **Tổng-tập-con** bắt "model tự cộng": 25/595 gắn cờ mà gần như 0 ca thật (`8=1+2+5` bốn lần; `51841=2+10+51842` là **HANDLE**). Hỏng CẤU TRÚC: chỉ bắt tổng cộng ĐÚNG, **mù với tổng cộng SAI** — mà tổng sai mới gây hại.
> · **Thêm `tool_numbers` vào dict trả về `tra_loi_ai`** để đo: `app.py:625` làm `jsonify(r)` ⇒ **bơm toàn bộ số nội bộ của tool ra trình duyệt**. Thay bằng **seam bọc `_guard_text` phía test** (0 dòng code sản phẩm).
> · **Vá bỏ sót bằng GỢI Ý trong kết quả tool** (2 vòng A/B, tiêu chí chốt trước ≥3/11): **1/11 · phá bẫy 0/17** cả hai vòng → GỠ. **Model ĐÃ NGHE LỜI** (id37 gọi cả `tim_kiem('lavabo')` = từ khoá tìm ra 2 kết quả thật) nhưng chuỗi `lavabo trẻ em` **không chứa chiều cao** — số 400/450mm ở **Ô KHÁC của bảng**. ⇒ **Nút thắt thật = GHÉP NHÃN↔GIÁ TRỊ THEO VỊ TRÍ**, prompt/nhắc-nhở vô hiệu ở lớp này.
>
> **📌 BÀI HỌC LỚN NHẤT PHIÊN NÀY — BA LẦN BỘ TRÍCH CỦA CHÍNH TÔI HỎNG, CẢ BA SUÝT CHO KẾT LUẬN NGƯỢC:**
> (a) regex `tổng…{0,40}(\d)` ra **"0 gắn cờ"** nghe như luật hoàn hảo — thực ra vớ phải **"304" trong "INOX 304"** nên **luật không bao giờ kích**; (b) bộ dò từ-khoá đếm *"**không tìm thấy** thông tin cho thấy chữ 'Cọc' bị lỗi font"* (một KHẲNG ĐỊNH DƯƠNG) thành "từ chối" → thổi bỏ-sót từ ~2% lên **13%**; (c) luật tổng-tập-con mù với đúng ca gây hại. ⇒ **Số "0%" và số "quá đẹp" đều là dấu hiệu bộ trích hỏng, không phải tin mừng.** Đã ghi vào `clean-state-checklist.md`.
> **⏳ RỦI RO / VIỆC CHỜ:** xem `session-handoff.md` khối đầu.

---
## Session 2026-07-31 — 🧱 NHÓM A: vá NỀN ĐỌC SỐ ĐO (3 lỗi độc lập) + 4 việc đợt vùng-mù + 4 lỗ hàng rào chống bịa + **NO_GO có số cho per-claim**
> **CHỐT SỔ:** HEAD **`8156d47`** == origin, tree SẠCH. check.sh **[41/41] PASS · 34 MCP tool · 0 regress**
> (272/107/31/61/51/44/24/26/63/28/27/21 không đổi). LIVE verify `/version` = `8156d47` ·
> prompt_version **`2026.07.27-kb-l3`** hash **`239e8b7b…`** (thêm rồi GỠ vế `_P_R5` → về byte-identical) ·
> kb_hash `e55ac112…` KHÔNG đổi · `/health` ok, `ram_mb` 135. **9 commit** đã push+deploy+verify.
> ⚠ **pytest VẪN không chạy được** (`ValueError: I/O operation on closed file` → `no tests ran`) — cổng là
> `check.sh`. **KHÔNG có `specs/specs.json`** → dùng `feature_list.json` (nay **64 mục**: 59 done · 4 deferred · 1 partial).
>
> **① NỀN ĐỌC SỐ ĐO SAI Ở 3 TẦNG ĐỘC LẬP — lộ ra khi rà lại TRƯỚC khi làm việc 1** (việc 1 chính là "so chữ
> in với số máy đo", nên số máy sai thì việc 1 vô nghĩa). Commit `138d104`:
> 1. **Hệ số tỉ lệ ÂM bị áp** — lỗi do CHÍNH commit DIMLFAC `6de1aaa` sinh ra (may mà chưa push). 1.882
>    đường/4 file thành ÂM → bị các cổng lọc dương của dự án vứt **IM LẶNG**, trong khi `so_duong_kich_thuoc`
>    vẫn đếm đủ = "đếm đủ mà mất số". Nặng nhất **1.186/1.650 = 71,9%** một file.
> 2. **Đường đo GÓC coi là mm** (lỗi CÓ TRƯỚC DIMLFAC): `01-TD` báo **35.970 mm cho một GÓC 359,7°**, đồng
>    thời in câu **TRẤN AN** rằng số này khớp bản vẽ.
> 3. **Không ai đọc group code 42** (số đo AutoCAD TỰ LƯU, có mặt **94,9%**). Phép thử KHÔNG THIÊN VỊ trên
>    54.735 đường: code42 đúng RIÊNG **2.936** ca / engine đúng RIÊNG **0** ca; dim dài-XIÊN engine chỉ đúng
>    **37,2%**. **USER CHỐT** dùng code42 làm nguồn chính.
> **TỰ KIỂM NGƯỢC 73 file** (thứ duy nhất chứng minh bản vá chạy — mọi suite đóng-băng-số vẫn xanh suốt):
> 47 file đổi số · 0 sinh thêm số âm · 34 file được CỨU số đo. `01-TD`: `lon_nhat` **35.970,0 → 212,1** và
> `nho_nhat` 0,3 → 0,7 — khớp ĐÚNG số AutoCAD tự lưu ở cả hai đầu.
>
> **② 4 VIỆC CỦA ĐỢT VÙNG-MÙ (user giao) — làm đủ, mỗi việc công bố số:**
> - **Việc 1 — cờ chữ in ghi đè:** luật bắt 1.098 đường/26 file; cờ "lan rộng" bật **19/66 = 29%** file (dưới
>   trần 45% → giữ ngưỡng). Con số `837 dim/15 file` trong thiết kế cũ **KHÔNG tái lập được**.
> - **Việc 2 — cờ "chưa với tới vùng này"** (4 tool): nhiễu **15,3% → 0,0%**, giữ 4/4 ca dương.
> - **Việc 3 — tool #34 `tim_chu_trong_ky_hieu`:** cổng cứng ngân sách rổ neo **6,0 vs `tim_kiem` 19,0** → ĐẠT.
>   E2E lấy lại `l=1100`[38E9C/38EA5] · `L=1600, SL:67`[3053A] · `DN-01, L=15000, SL:02`[1C2F1E].
> - **Việc 4 — `_P_R5`: THÊM RỒI GỠ.** A/B LIVE: prompt CŨ **4/8** gọi tool mới, MỚI **5/8** — chênh 1 ca,
>   trong nhiễu (Fisher p=1,000). Đo tiếp thì thấy **HẠI**: trong ca cờ bật chỉ **5%** tool trả dữ liệu thật,
>   **95%** câu trả lời ĐÚNG vẫn là "không có" mà vế ngoại lệ lại **CẤM nói** → cỗ máy ép bịa. **GỠ**, prompt
>   về byte-identical. GIỮ phần CODE (cờ + tool) và **sửa nguyên nhân gốc**: đòi khớp ĐÚNG DẤU
>   (`cửa`≠`của`, **`mác`≠`mạc tiến trình`** = TÊN NGƯỜI KÝ) → ca bật cờ **20→5**, khớp mù dấu **15→0**.
>
> **③ 4 LỖ HÀNG RÀO CHỐNG BỊA (3 kênh neo + 1 lỗ phạm vi)** — `5548fe1` + `5756b37` + `5f21ae9`:
> - **Mã hiệu sinh neo ÂM**: `DẦM D2-10`→−10; **24/76 file** có neo âm nằm đúng dải cao độ sinh THUẦN từ mã
>   hiệu ⇒ tên dầm cấp phép bịa cao độ (đúng lớp id135). Bất đối xứng: phía câu trả lời đã strip, phía rổ neo thì không.
> - **TÊN FILE làm bằng chứng**: cùng byte, đổi tên → 2 câu bịa chuyển từ CHẶN sang LỌT. Kênh do NGƯỜI DÙNG
>   kiểm soát 100%, không cần đụng bản vẽ.
> - **HANDLE — kênh RỘNG NHẤT**: kết quả gồm 3 handle + chữ KHÔNG CÓ SỐ NÀO vẫn sinh rổ `[1,2,9,38,13876]`.
>   **MỌI tool trả handle đều dính.**
> - **Cụm TỪ CHỐI tắt guard TOÀN BÀI**: *"Không tìm thấy…, nhưng cao độ đáy đài cọc là −13,7 m."* LỌT dù rổ
>   neo không chứa −13,7. Dòng thoát-sớm là **MÃ CHẾT** với câu từ chối thuần → tác dụng duy nhất là miễn trừ
>   đúng phần nguy hiểm. Gỡ; với rổ neo THẬT **0/793 câu đổi**.
> - **HÀNG RÀO CHO SỐ ĐẾM**: **62/198 = 31%** câu trả lời CHỈ có số đếm → hàng rào bỏ qua hoàn toàn
>   (*"Tổng số cọc là 156 cọc."* LỌT). Vá: chặn thêm **1**, **giết oan 0**, bắt đúng **1**.
> **HIỆU QUẢ GỘP, đo được:** lớp lỗi **id135 (bịa cao độ ÂM) nay lọt 0,0%**.
>
> **④ 1.05 — nối CỤM TỪ tiếng Việt với KÝ HIỆU** (`8156d47`): hỏi `"đài cọc"` → trả **131** (ghi chú khác),
> **59 đài cọc thật biến mất**; file khác trả RỖNG + câu khẳng định SAI. ⚠ Cơ chế đ/d VẪN ĐÚNG (`ĐC`→59,
> `DC`→16) — **mô tả trong tài liệu cũ SAI**. Vá bằng kho ký hiệu, CHỈ **7/24 mục MỘT NGHĨA**; 15 mục đa
> nghĩa KHÔNG tra ngược. **KHÔNG GỘP** danh sách (chống mô hình cộng 131+59=190).
>
> **⑤ ⛔ NO_GO CÓ SỐ CHO PER-CLAIM — ĐỪNG MỞ LẠI** (`4c242b5`, workflow `wf_8a663cde-735`):
> "tỉ lệ lọt" **KHÔNG phải đại lượng dùng được** (5 probe ra 0%/23,8%/32,2%/37,9%/52-77,5%; cùng rổ neo đổi
> bộ sinh → 0,0%→13,6%). Đo bằng NHÃN ĐỘC LẬP: per-claim chính xác **0/25** và **1/30**, giết oan **9,9-33,1%**,
> ALL giết **82% câu có PHÉP CỘNG**. **ANY là luật DUY NHẤT 0% chặn oan trên cả 7 dạng.** Đòn bẩy đúng =
> **làm sạch rổ neo** (đã làm).
>
> **📌 BÀI HỌC ĐẮT NHẤT PHIÊN NÀY — RED-TEAM BẮT ĐƯỢC LỖI BỊA SỐ DO CHÍNH BẢN VÁ SINH RA.** Bản vá code42
> đầu "cứu" MỌI đường đo-ra-0. Nhưng hình học suy biến ⇒ code42 **chắc chắn là số CŨ**. Đo 607 đường được
> cứu: **529 chữ in RỖNG → cứu ĐÚNG** · **66 gõ đè SỐ KHÁC → BỊA** (bản vẽ in `10000`, máy phát `2136,3`) ·
> 11 gõ đè ký hiệu. **Tệ HƠN lỗi gốc**: lỗi gốc chỉ làm rơi giá trị, cứu sai thì phát số tự tin VÀ số đó
> thành NEO. **Cả 3 suite mới tự viết đều XANH** — điểm mù: ca test dựng đúng nhánh cứu nhưng CỐ Ý không gõ
> đè chữ.
>
> **VIỆC CHỜ (phiên sau) — nhóm A, theo thứ tự đề nghị:**
> 1. **1.06 sửa `tests/run_battery.py`** (~15 phút) — đang GHI ĐÈ kết quả lượt trước; là **điều kiện chặn** của Q2/Q3/Q4.
> 2. **1.03 nắn phông VNI + TCVN3 còn sót** — `grep VNI` = 0; còn 545 chuỗi/21 file; mở khoá 1 bộ hồ sơ 6 file.
> 3. **1.04 đơn vị inch/feet — ⚠ KHÔNG phải "thêm vào bảng tra".** Đo: 12/76 file khai đơn vị **MÂU THUẪN**
>    với chính số đo (`2. KetCau MN GiaLoc` khai INCH nhưng vẽ mm; `04. Cong` khai FEET, trung vị 220 → 67m).
>    Thêm ngây thơ = biến câu nhẹ "không khai đơn vị" thành câu SAI TỰ TIN. Việc đúng = **cross-check khai
>    báo với độ lớn số đo và LỘ mâu thuẫn**.
> 4. Q2 (chạy lại 198 câu 3-5 lượt, **tốn API**, phải định trước tiêu chí thắng/thua) · Q3 (4 câu bẫy) ·
>    Q4 (bật lớp cảnh báo 2 của handle-guard — khuyến nghị để im).
> 5. Chờ file: **F1** bản vẽ hạ tầng sâu ≥−5m từ đơn vị KHÁC · **F2** bảng bóc khối lượng làm tay của kỹ sư.
> 6. Hoãn có cơ sở: R1 lớp-3 đơn vị ×1000 (34,9-41% FP) · R2 Pattern D/E (**mất mô tả**) · R3 bộ nhận biết vùng.
> **⏳ RỦI RO TỒN DƯ:** rổ neo phình +6 ở ca đo 1.05 (số THẬT của bản vẽ nên phải là neo — chi phí thật của
> tăng recall) · danh sách danh từ đếm dựa trên 198 câu/3 bản vẽ, corpus mới có thể thiếu (chiều hỏng là IM
> LẶNG, không báo oan) · bug parser dấu nghìn VN (`62.900`) **đang bị luật ÷1000 che hoàn toàn** — ghi sổ, KHÔNG sửa.

---
## Session 2026-07-30 (nối) — 📐 NHÓM A: rà soát lại toàn nhóm + **vá HỆ SỐ TỈ LỆ ĐO (DIMLFAC)** — 21,5% đường kích thước đang bị đọc SAI
> **CHỐT SỔ:** HEAD **`6de1aaa`**, tree SẠCH. check.sh **[36/36] PASS · 33 tool · 0 regress** (272/107/50/31/63/28/44/24/26… KHÔNG đổi). ⚠ **`6de1aaa` CHƯA PUSH** — cố ý, xem "VIỆC CHỜ" #0. LIVE là `fb8a597` (mã nguồn y hệt `371d950`). Đo LIVE cuối phiên: `ram_mb` 135,5MB · `tu_choi` 0 · **`keepalive` ok=99 / lỗi=0** (99 cú giữ-thức liên tiếp không lỗi — bom 3 đã vá đúng trên máy thật).
> **USER CHỐT 3 điều:** (1) giữ `READFILE_MAX_MB=45`; (2) **ĐỌC hệ số tỉ lệ đo** dù nó ĐỔI SỐ máy báo; (3) **CÓ sửa `_P_R5`** (chỉ dẫn AI) kèm đo A/B.
>
> **① RÀ SOÁT LẠI TOÀN NHÓM A (workflow 7 agent `wf_70bc91b8-921`) — KẾT LUẬN NGƯỢC với ghi chú đầu phiên:**
> Quét 4 nguồn độc lập → **187 đầu mục thô** → đối chiếu code → **26 việc CÒN LẠI** · **13 mục tưởng còn nhưng ĐÃ XONG** (tài liệu chưa cập nhật) · **16 mục không thuộc A**. Phân tầng: **14 làm được NGAY (không vướng gì)** · 4 cần user quyết · 2 chờ file đối tác · 6 hoãn có cơ sở. **Artifact:** https://claude.ai/code/artifact/2aac664c-26fd-4ada-9ece-641ab6e596e5
> ⚠ **ĐÍNH CHÍNH ghi chú cũ:** `claude-progress.md`/`session-handoff.md` từng kết luận *"chữ trong khối KHÔNG phải bug — đã tự bác bỏ"*. **SAI.** Tự đo 40 file: **2.068 chuỗi riêng biệt** chỉ tồn tại trong khối/trang in, ở **30/40 file**, công cụ tìm kiếm KHÔNG bao giờ thấy và KHÔNG cảnh báo. (Nhưng xem ② — cách vá hiển nhiên lại SAI.)
> ⚠ **Bảng điểm 198 câu (`tests/battery_results.jsonl`, 24/07) LẠC HẬU** so với code (prompt đã qua 3 phiên bản). **ĐỪNG trích con số "39 câu hỏng"** cho ai.
>
> **② NGHIÊN CỨU TRƯỚC-CODE cho 3 việc đọc vùng mù (workflow 11 agent `wf_0cdb83d4-bca`, 4 red-team GO_WITH_ADJUSTMENTS) — BÁC BỎ 1 trong 3 việc đã duyệt:**
> - **V2 "đọc chữ trong khối vào kho chữ chung" = BỎ HẲN** (không bản rút gọn, không "để sau"). Số cứng: **71,6%** chữ-trong-khối là nhãn DIMENSION `*D` **máy ĐÃ đọc rồi** (nạp vào = đếm trùng + bơm lại số vào rổ neo) · **55,7%** khối có chữ là khối **CHƯA TỪNG được chèn** — khối chết ghi *"156 cọc"* trong khi bản vẽ sống ghi *"131 CỌC"* · chữ trong khối được-chèn: **mã cấu kiện chỉ 0,8%**, khung tên 37,8% · lợi ích thật **+3,0%**, **19/71 file lợi ích BẰNG KHÔNG**, top5 file chiếm 59% · hệ số phóng đại **8,61×** (1 bản trong định nghĩa = 8,61 lần hiện) · toạ độ khối là hệ NỘI BỘ (29%/56%/**97%** chữ nằm ngoài khung bản vẽ) → đầu độc mọi tuyến ghép-theo-vị-trí + khoanh đỏ SAI CHỖ · `cao_do_min_max` KT **−2.1 → −94.44** (cao độ khảo sát địa hình, khác hệ; lọc "chỉ khối được chèn" KHÔNG cứu) · **id135 `rachmop` đổi đáp án −14.26 → −16.14 mà 35/35 vẫn XANH** (trôi thầm).
> - **THAY BẰNG:** tool ĐỌC RIÊNG `tim_chu_trong_ky_hieu`, chỉ khối **ĐƯỢC CHÈN**, không nhập vào `self.texts`, KHÔNG trường đếm. Lý do bắt buộc phải có: chỉ gắn cờ "có vùng chưa đọc" mà KHÔNG cho đường đọc = vừa khẳng định *có*, vừa cấm nói *không có*, vừa không đưa dữ liệu = **công thức ép bịa**. Dữ liệu THẬT đang mất: `SL:67`, `L=1600`, `DN-01, L=15000, SL:02`, `l=1100`.
> - **Khối MỒ CÔI + TRANG IN: BỎ khỏi mọi tool/cờ** (nguồn không tin được thì KHÔNG trả, chứ không phải trả rồi chặn rổ neo).
> - V1 (cờ "chưa với tới") phải khớp **CHỈ trên `to_unicode`**: khớp raw tạo **bằng chứng ẢO** — file `04.Cong, tuong rao` + `C1` → **41 hit ảo** (mã màu `\|c163\|` của nhãn phong thuỷ).
> - **`_P_R5` PHẢI SỬA** (nằm trong `_INVARIANT`, ra lệnh *"tool trả 0 kết quả → nói thẳng không có"*) — không sửa thì cờ V1 nằm im vô dụng. Tách lát riêng + bump version + re-freeze hash + A/B.
>
> **③ ĐÃ LÀM & LIVE-READY: HỆ SỐ TỈ LỆ ĐO (DIMLFAC) — commit `6de1aaa`**
> Bản vẽ cho phép MỖI đường kích thước tự khai hệ số ("chi tiết vẽ thu nhỏ, nhân 0,25 mới ra số thật"). `get_measurement()` trả số HÌNH HỌC THÔ, **không áp hệ số** → số máy đọc KHÁC số IN. **Tự đo 40 file/15.608 đường: 3.352 đường (21,5%) có khai hệ số ≠ 1, dính 17/40 file.** Ca đối chiếu được với chữ in: khớp *"số đo × hệ số"* **19** / khớp số đo thô **0**. Trên `MB KET CAU 27.3.2022.dxf`: tổng 3.167.454,3 → **2.498.584,2**, **569 đường đổi số**.
> Đọc hệ số theo **TỪNG ĐƯỜNG** (`e.override()`), KHÔNG đọc bảng kiểu dáng (đo được **11 file** có bảng khai hệ số mà **0 đường** nào dùng → đọc bảng sẽ áp OAN). FAIL-OPEN: hệ số rác (0/NaN/±inf) hoặc `override()` ném → về hành vi CŨ, không nuốt dimension. LỘ bằng cờ **BOOL** `co_dim_ty_le_do` + prose **SẠCH SỐ**, **không thêm trường đếm** (mọi số trong kết quả tool đều nở rổ neo).
> ⚠ **BÀI HỌC ĐẮT NHẤT PHIÊN NÀY:** sau khi vá, **CẢ 6 suite đóng-băng-số vẫn XANH** — bộ kiểm **mù hoàn toàn**. Phải TỰ KIỂM NGƯỢC (so tổng số đo trước/sau) mới biết bản vá thực sự chạy, chứ không im lặng rơi về hành vi cũ. → suite mới `test_ty_le_do` **17 ca** (bản vẽ SYNTHETIC ezdxf, tất định): không-khai-hệ-số KHÔNG đổi số · có-khai nhân đúng (0,25/100/0,5/2,0) · hệ số RÁC giữ cũ · `override()` ném → fail-open không nuốt dimension · cờ BOOL + prose sạch số + KHÔNG trường đếm · rổ neo không nở. check.sh **35→36 bước**.
>
> **④ LỖ HỔNG PHÁT HIỆN DỌC ĐƯỜNG (chưa vá, ngoài phạm vi — GHI SỔ):** hàng rào chống bịa **CHỈ soi số ĐO LƯỜNG**, **số ĐẾM không có hàng rào nào**. Đo với rổ neo RỖNG: *"Tổng số cọc là 156 cọc."* → **LỌT** · *"Bản vẽ có 9999 cột."* → **LỌT**; cùng lượt *"Chiều dài dầm 30 m"* → CHẶN, *"Diện tích sàn 43 m2"* → CHẶN. Nguyên nhân: `_guard_text` thoát sớm ở `if not do_luong: return text`. Với phần mềm bóc khối lượng thì "bao nhiêu cấu kiện" quan trọng ngang "dài bao nhiêu mét". Vá được nhưng sẽ dịch số của cả 36 suite → phải là lát RIÊNG.
>
> **VIỆC CHỜ (phiên sau):**
> 0. **⚠ `6de1aaa` CHƯA PUSH.** Cố ý: đã hứa với user gộp cùng phần còn lại của đợt (cảnh báo ghi-đè + cờ + tool tra). Muốn đẩy ngay: `git push origin main` (Render tự deploy ~60s, rồi verify `/version` + `/health`). Nếu đẩy riêng thì nhớ: đây là commit **ĐỔI SỐ máy báo**, nên verify LIVE kỹ hơn thường lệ.
> 1. **Còn 3/4 việc của đợt này:** bộ phân loại "ghi đè THẬT" trên đường kích thước (luật `_dang_chu_in` đã thiết kế + đã vá 2 họ báo-động-giả; đo: luật chốt bật 837 dim/15 file, luật thô bật 859/17 và có **2 file bật 100% OAN**) · cờ "chưa với tới vùng này" (4 tool) · tool `tim_chu_trong_ky_hieu`.
> 2. **`_P_R5` + đo A/B** — user ĐÃ CHỐT LÀM. Lát riêng, cuối cùng.
> 3. **Nhóm A còn 22 việc khác** — xem artifact ở ① (14 việc không vướng gì: chữ trang in · nắn phông VNI/TCVN3 còn sót · nhận đơn vị inch/feet · "đài cọc" trả ra "dầm" · 7 việc nhỏ…).
> 4. Bảng điểm 198 câu: chạy lại 3-5 lượt (user đã chốt phương án b) — **làm SAU khi 3 việc còn lại của đợt lên**, và phải sửa `tests/run_battery.py` (ghi đè kết quả lượt trước) TRƯỚC.

---
## Session 2026-07-30 — 🧯 VÁ 3 "BOM HẸN GIỜ" CHỊU TẢI (2 lát LIVE `eba4d67` + `371d950`), gate 33→35/35, **lần đầu ĐO ĐƯỢC RAM Linux thật**
> **CHỐT SỔ:** HEAD `371d950` == origin, tree sạch. check.sh **[35/35] PASS · 33 tool · 0 regress** (272/107/50/31/44/24/26 không đổi). LIVE verify 2 lần: `/version` commit khớp + **prompt_hash/kb_hash KHÔNG đổi** (bản vá này TUYỆT ĐỐI không chạm SYSTEM_PROMPT/kho kiến thức → không cần đo A/B) + `/health` ok + **verify TRANG THẬT 6/6 chuỗi frontend**.
> **USER CHỐT:** giữ `READFILE_MAX_MB=45` (giữ điểm mạnh "đọc bản vẽ thật") · triển khai **2 đợt** (nhẹ trước, nặng sau).
> **BỐI CẢNH:** 3 bom lộ ra từ chẩn đoán cảnh báo health-check 2026-07-27 (`[[ref-canh-bao-health-check-render]]`). Quy trình: **workflow nghiên cứu 11 agent** (4 probe đo thật + 2 thiết kế + 4 red-team-trước-code + synth → `scratchpad/wf_chot.md`, `wf_40e7e334-100`) → code → gate → **red-team-IMPLEMENTATION 5 agent chạy ENGINE THẬT** (`wf_a2699eb1-622`) → vá → gate.
>
> **⛔ ĐO THẬT BÁC 3/8 MỤC DỰ KIẾN (không làm việc vô ích/có hại):**
> - **`MAX_SESSIONS` 4→2 = BỎ.** Ma trận cap-vs-thread **5/5 cấu hình**: số bản vẽ trong RAM = **số REQUEST ĐỒNG THỜI** (`--threads`), KHÔNG phụ thuộc cap (cap2/thread4 vẫn 4 bản vẽ). Hạ cap tiết kiệm **0MB** và còn MỞ 2 thread rảnh cho người mới → tự bỏ lớp che mà `threads==cap` đang cho. GIỮ 4 + comment cảnh báo.
> - **`--threads` 4→8 = BỎ.** Cùng 8 upload: threads=4 → đỉnh 4 bridge; threads=8 → **8 bridge (+~600MB)** = OOM chắc chắn. Sau khi có gate thì vô nghĩa (threads=4 + chặn cứng cho `/health` **0.002s** ở N=8, so với **4.658s** khi không chặn).
> - **lazy-import `google.genai` bằng `find_spec` = BỎ.** Tái hiện được **`find_spec` NÓI DỐI** (shadow `certifi` → find_spec True nhưng import FAIL → `/config` báo `use_ai:true` trong khi AI chết, đối tác chờ convert .dwg 600s xong mới biết) + `find_spec` **NÉM** ModuleNotFoundError khi thiếu namespace cha → viết nải là **sập `import app` = deploy fail 100%**. Lợi ích chỉ để dẹp 1 cảnh báo LÀNH TÍNH; và lazy genai một mình vẫn 7.84s dưới tải CPU (chưa dưới ngưỡng 5s).
> - **"close() chờ tiến trình con chết" = TIỀN ĐỀ SAI.** Đo thật: con chết **0.198s (rảnh) → 2.022s (đang parse)**, 8 vòng spawn+close chỉ **+2.3MB**, **0** mồ côi (mcp 1.27.0 tự terminate process tree). ⇒ thay bằng vá **lỗ THẬT**.
>
> **LÁT 1 — LIVE `eba4d67`:** `_evict_one_lru` ưu tiên đuổi **phiên RỖNG (965 byte)** trước phiên giữ bản vẽ (149-430MB) — trước đây 4 khách VÔ DANH đẩy được bản vẽ đối tác ra · keep-alive hết **HỎNG THẦM** (ping TRƯỚC rồi ngủ [bỏ 10' mù sau boot] · chu kỳ 10'→**5'** [đồng hồ ảo: 600s vs ngưỡng ngủ 900s = chịu **0** nhịp trượt] · bộ đếm ok/lỗi + log · lỗi → ngủ 30s · **tín hiệu thất bại lấy từ BỘ ĐẾM** vì `_keepalive_ping` LUÔN trả True → viết `if not _keepalive_ping()` là MÃ CHẾT vĩnh viễn) · `/health` + khối `keepalive` · **3 route bounded lock** `LOCK_WAIT_S=3` + `_tu_choi()` **đủ 4 khoá chữ** (thiếu `ly_do` là tái sinh 'undo nói dối' — nút ↩ Hoàn tác chỉ đọc khoá đó) + `metrics.tu_choi` (đo thật trước vá: khoá giữ 12s → POST /xac-nhan nằm **11.60s**, giữ chết 1/4 thread) · PAGE `jpost` KHÔNG BAO GIỜ ném + `upload()` try/catch (hết treo vĩnh viễn ở "⏳ Đang tải lên & nạp...") · M4 thông điệp lỗi tool SẠCH SỐ.
> **LÁT 2 — LIVE `371d950`:** **TRẦN SỐ BẢN VẼ `MAX_BAN_VE=1`** (đây mới là trần RAM) — gate đặt **SAU 3 cửa rẻ**, đếm LẠI TỪ SỰ THẬT, không pop phiên nạn nhân (giữ `artifacts`), fail-closed CÓ kế toán (`dang_dong`), `finally: _tra_suat` bao CẢ HÀM · **M1 dọn tiến trình MỒ CÔI** khi spawn quá hạn (`MCP_READY_S=60`; trước: RuntimeError xong con **sống mãi** ~98MB/lần bấm) · `call()` guard `_closed` (trước: treo tròn 600s) · **`nap_ban_ve` bỏ doc cũ TRƯỚC** (đỉnh **383.1→259.2MB, -123.9MB**) · **M2 `/health` phơi `ban_ve`/`dang_nap`/`dang_dong`/`max_ban_ve`/`ram_mb`** · NÓI THẬT 3 route theo `da_nhuong`/`nap_loi`/chưa-từng-nạp (phiên chưa nạp GIỮ NGUYÊN VĂN câu cũ = hợp đồng K.5).
>
> **🔴 RED-TEAM-IMPL BẮT 2 LỖI MỨC CHẶN (mỗi lỗi 3-4 lăng kính ĐỘC LẬP tái hiện) — 1 do CHÍNH BẢN VÁ sinh ra:**
> - **CHẶN-1 (bản vá tự đẻ): một cú BẤM HAI LẦN phá được trần bản vẽ.** Cờ 'đang nạp' là MỘT ô vô hướng/phiên → request /upload thứ HAI cùng phiên thua khoá → 503 → `finally` của NÓ **xoá cờ của request ANH EM đang parse** → `_dem_ban_ve()` tụt 0 → phiên KHÁC xin được suất → **2 bản vẽ cùng RAM = ĐÚNG cái OOM gate này tồn tại để chặn**. Đo: **4 người = 4 bản vẽ**; `/health` tự tố `ban_ve=2 max_ban_ve=1`. Nút "Tải lên & nạp" KHÔNG bị khoá nên đối tác bấm 2 lần là tái hiện. **42 ca test tự-viết MÙ hoàn toàn** (đều tuần tự 1 luồng). → Vá: `_giu_suat`/`_tra_suat` **ĐẾM request đang bay** (`nap_dem`) + khoá nút ở frontend.
> - **CHẶN-2 (lỗ có sẵn, lát 2 làm hoá HỒI QUY): nạp thất bại vẫn hiện "✅ Đã nạp".** `nap_ban_ve` KHÔNG trả `{'loi'}` khi lỗi — nó NÉM; `MCPBridge.call` **BỎ QUA `res.isError`** → rơi vào `{'ket_qua': 'Error executing tool ...'}` ⇒ điều kiện `res.get('loi')` và TOÀN BỘ máy "nói thật" của lát 2 là **MÃ CHẾT trên đường lỗi phổ biến nhất**: HTTP 200, `co_ban_ve=True` cho bản vẽ KHÔNG tồn tại, `summary='None (AutoCAD None), None đối tượng'` **bơm vào system prompt Gemini mọi câu sau đó**, và **1 người tải file hỏng lên là GIẾT bản vẽ đang dùng của người khác rồi chiếm suất với ZERO bản vẽ trong RAM**. → Vá GỐC 1 chỗ (`call()` đọc `isError` → `{'loi': <SẠCH SỐ>}`) + vành đai 2 ở `/upload` (**đòi DẤU HIỆU THÀNH CÔNG** `res.get('name')`, không đòi dấu hiệu thất bại) + không trả `ket_qua` ra trình duyệt (chứa đường dẫn máy chủ).
> - **Cùng 1 vá gốc đóng luôn lỗ CHỐNG-BỊA:** text lỗi thô chảy vào rổ neo grounding, mà **pydantic v2 nhét NGUYÊN giá trị tham số** (`input_value=<số>`) ⇒ model (hoặc chữ trong file lái model) **tự BƠM ĐƯỢC SỐ TUỲ Ý vào rổ** chỉ bằng cách gọi 1 tool sai kiểu → câu bịa mang số đó ĐI QUA guard. Chứng minh vá xong trên **đường truyền MCP THẬT** (B.6): `gioi_han='...987654'` → rổ RỖNG. **ĐÍNH CHÍNH M4 (lát 1): sanitizer M4 chỉ bọc `except` PHÍA HOST, KHÔNG với tới lỗi ném ở tiến trình con.**
> **+4 lỗi CAO/TB đã vá:** TOCTOU 3 route đọc (kiểm `bridge is None` TRƯỚC khoá, dùng SAU khoá → `AttributeError NoneType` ra đối tác; nay đọc LẠI vào biến cục bộ + kiểm lại, tách `_msg_khong_ban_ve`/`_msg_so_xn`) · `_try_close_session` KHÔNG BAO GIỜ pop phiên đang có request bay (trước: LRU pop phiên trong cửa sổ `_dong_cho_chac` → nạp vào dict MỒ CÔI, "✅ Đã nạp" mà câu sau là "Chưa nạp", 149-430MB **không ai đếm được nữa**) + vành đai 2 (`/upload` kiểm lại phiên còn trong SESSIONS → 409) · `_keepalive_loop` bọc try/except quanh THÂN (1 ngoại lệ = tính năng **tắt lặng lẽ** mà `/health` vẫn báo lành = **đúng khuôn 'hỏng thầm' chính nó đang đi vá**) · **`_env_int` + kẹp `LOCK_WAIT_S>=0`** — RỦI RO MỚI do chính lát 1-2 tạo ra: `render.yaml` vừa phơi 4 nút lên dashboard mà code đọc `int()` trần ⇒ **gõ sai 1 chữ = deploy FAIL 100%**; số ÂM = `acquire(timeout=-1)` chờ VÔ HẠN = **tắt âm thầm chính bản vá chống nghẽn** (đo: `abc`→3, `-5`→0) · 3 thông báo nói SAI nguyên nhân + cờ `da_nhuong` không được gỡ.
> **Red-team KHÔNG phá được:** deadlock (2 vòng ép tải **1077 request**) · rỉ suất qua đường 400/413/500 · giật bản vẽ liên-phiên · dọn mồ côi (0 sót, 3-5 vòng) · 14/14 tool báo lỗi tử tế sau khi nạp lỗi · `close()` đổi hợp đồng None→bool (grep toàn repo + 200 lần gọi) · `_ram_container_mb`.
>
> **📏 LẦN ĐẦU ĐO ĐƯỢC RAM LINUX THẬT (`/health.ram_mb`, cgroup `anon`):** **135.3MB** lúc rảnh, 0 bản vẽ. Đối chiếu: Windows đo web = 104.9MB ⇒ **Linux cao hơn ~29%**, khớp ghi chú cũ "Linux +10-30%". ⇒ Ngân sách còn cho 1 bản vẽ ≈ **377MB**. Ngoại suy theo tỉ lệ đó: bản vẽ 23.31MiB (Windows child 289.2MB) ≈ 373MB Linux → tổng ~508/512MB = **SÁT LẰN**; file 39.28MiB/145.807 đối tượng ≈ 555MB → **OOM một mình**. ⚠ Đây là NGOẠI SUY 1 tỉ lệ, chưa đo trực tiếp — nhưng đã đủ để nói: **trần an toàn thật THẤP HƠN 45MB nhiều**, và cổng đo theo MB không bound được RAM (RAM đi theo **SỐ ĐỐI TƯỢNG**: 38.54MiB/35.772 obj → 260.3MB vs 39.28MiB/145.807 obj → 398.7MB).
> **TEST:** MỚI `test_admission.py` **63 ca** (A.13-A.17 = ca red-team-impl bắt) + `test_bridge_close.py` **28 ca** (B.6 chạy qua đường truyền MCP THẬT với file rác THẬT). SỬA: test_session 25→**36** (bọc `MAX_BAN_VE=99` + comment trỏ sang test_admission; K.9 bounded-lock; `FakeBridge.close(cho_giay)`; phòng thủ dòng `br=` khỏi IndexError giết cả suite), test_health 11→**23** (L.6 hỏng-thầm-phải-LỘ + L.7 đồng hồ ảo), test_app_routes 10→**12**, test_grounding_guard 47→**50**. check.sh 33→**35** khối.
> **⏳ RỦI RO CÒN LẠI (ghi sổ, KHÔNG vá trong đợt này):** 1 file DÀY đối tượng vẫn đủ OOM MỘT MÌNH (user chốt giữ 45, sẽ chốt ngưỡng sau khi đọc `ram_mb` thật) · `--timeout 600` của gunicorn **KHÔNG giết** request dài dưới worker gthread (đọc source `gthread.py:203-205`) · self-ping chỉ GIỮ THỨC, **không ĐÁNH THỨC** → cần monitor NGOÀI (UptimeRobot/cron 5', user tự lập) · mọi số RAM còn lại là Windows WorkingSet · gunicorn không chạy trên Windows nên số concurrency là `waitress`/Semaphore mô phỏng (đã đối chiếu source `gthread.py:98`).

---
## Session 2026-07-26→27 — 🏁 CHỐT SỔ: KHO KIẾN THỨC DEV-SOẠN L0-L6 TRỌN BỘ LIVE + L7 đóng có-số + vá 3 bug L5
> **CHỐT SỔ CUỐI PHIÊN (2026-07-27):** HEAD **`91eaba6`** == origin, working tree **SẠCH (0 file)**. check.sh **HARNESS GATE PASS [33/33]** · **33 MCP tool** · takeoff **272** · qa 129 · grounding 47 · misc 107 · cao_do 31 · prompt-taxonomy 24 · **kho kiến thức: dispatch-gate 11 · kienthuc 15 · kb-graft 18 · kb-xacnhan 44 · tra-ky-hieu 13 · garble-dia 26** · **0 regress**. LIVE verify `/version`: commit `c9e2171` (docs `91eaba6` không đổi code) · prompt_version **`2026.07.27-kb-l3`** hash `239e8b7b…` · **kb_version `kb-2026.07.26-dot-dau` hash `e55ac112…`** · `/health` ok; **verify TRANG THẬT có nút 'Hoàn tác' + bảng `#xnbox`**.
> ⚠ **pytest KHÔNG dùng** (test đổi `sys.stdout` lúc import → crash `I/O operation on closed file`, `no tests ran`) — cổng là `check.sh`. **KHÔNG có `specs/specs.json`** → dùng `feature_list.json` (**46 mục**: 44 done · 1 deferred [dự toán chi phí] · 1 partial [I3]).
> **CHUỖI COMMIT PHIÊN:** `998950f` (kho L0-L5+L3) → `fccc635` (L6 garble-Ø) → `c9e2171` (vá 3 bug L5 + 7 vá red-team) → `91eaba6` (chốt sổ docs).
> **VIỆC ĐANG CHỜ (phiên sau):**
> - **Nhóm C (RAM/upload) — HOÃN tới CUỐI dự án** (user chốt: tốn tiền túi, chờ tài trợ). Nghiên cứu đã xong sẵn: `READFILE_MAX_MB=120` + `MAX_SESSIONS=1`, HELD `f025ad7` đang BUGGY. Xem `[[project-chiu-tai-va-chi-phi]]`.
> - **⚠ 3 BOM HẸN GIỜ đo được, vá FREE, CHƯA làm** (từ chẩn đoán cảnh báo Render): **RAM 7.5×/file → 2 phiên file lớn = OOM mà `MAX_SESSIONS=4` đang cho phép** (nên hạ 4→1-2, 1 dòng env) · hết thread ở `n==--threads(4)` · keep-alive hỏng thầm. Xem `[[ref-canh-bao-health-check-render]]`.
> - **L7 (xác nhận đổi số) = ĐÓNG** có số cứng (0 ca/62 file) — chỉ mở lại khi corpus MỚI đạt **≥1% tổng mục VÀ ≥3 file của ≥2 đơn vị**. Xem `[[project-l7-doi-so-khong-lam]]`.
> - **Nhóm A còn:** 13 ca recall hạ-tầng (chặn RAM → nhóm C) · Pattern D/E biên (hoãn) · **id135 deep** chờ bản vẽ hạ tầng ĐỘC LẬP sâu ≥-5m.
> - **Nhóm D ứng viên tiếp:** I8 panel phân tầng tin cậy (UI, giá-trị-demo cao) · Truth-engine 12 công thức × ≥3 mã · phục hồi subprocess chết.
> - Nghiên cứu-loại (ĐỪNG làm lại): họ-slash decode đầy đủ (1 file/1 firm) · L7 · pagination · dem_theo_block · I3-U ngưỡng-sàn · U6 iterdxf · I9 Option B.

---
## Session 2026-07-26 (nối 2) — ⭐ PIVOT AI-TỰ-HỌC: "DEV dạy trước, đối tác CHỈ XÁC NHẬN" (user chốt) + khởi động nghiên cứu KHO KIẾN THỨC DEV-SOẠN
> **Bối cảnh:** sau khi hoãn nhóm C, rà nhóm D → user hỏi sâu về AI-tự-học (P-1→P4 LIVE, chỉ còn P5 chặn + F-B treo). Tôi giải thích lý do kênh học bị rào (rủi ro prompt-injection dạy quy ước độc = cao nhất dự án; nguyên tắc "con người bấm, không để AI tự học") → **user đồng ý và PIVOT định hướng**:
> - **BỎ:** kênh đối-tác-dạy-mở (`hoc_quy_uoc` không phơi cho đối tác — giữ làm công cụ DEV nội bộ) · P5 auto-codify (hoá cứng từ log học) · F-B web-teaching (không làm).
> - **THAY BẰNG:** (1) **KHO KIẾN THỨC DEV-SOẠN** trong quá trình phát triển — ký hiệu/ngôn ngữ/quy ước/thuật ngữ ĐA-DOMAIN (kết cấu/kiến trúc/điện/nước/hạ tầng, VN/EN) + danh mục ca DỄ NHẦM (CH=cửa↔cao độ, D=dầm/đài/cửa, mũi cọc≠đáy đài…); mỗi mục KIỂM-CHỨNG-ĐƯỢC (truy về TCVN/quy ước phổ biến/bản vẽ thật); **fail-open** (ngoài kho → "bí" + HỎI, KHÔNG đoán). (2) Khi bí/dễ-nhầm → HỎI đối tác với **phương án chuẩn bị sẵn** → đối tác **CHỈ BẤM XÁC NHẬN (confirm-only)**, không nhập/dạy tự do.
> - **Soi code xác nhận hiện trạng giống ~70%:** `hoi_de_hoc`+`doi_chieu_nghi_ngo` (đọc-thuần, "không bịa nghĩa/không tự chọn bên") + `_TEMPLATE_ENUM` dev-cấp = ĐÚNG hướng sẵn, GIỮ; chỉ nhánh `hoc_quy_uoc` đối-tác-chủ-động-dạy + P5 là khác → đóng. **Lợi:** tháo nút thắt "P5 chờ ≥3 firm + red-team auto-codify"; kho kiến thức giúp đọc đúng = việc nhóm **A** (đúng ưu tiên); giảm báo-động-giả của classifier (chỉ hỏi ca kho BIẾT dễ nhầm).
> - **Ghi sổ:** memory `[[project-ai-tu-hoc-ke-hoach]]` (pivot đầu file) + MEMORY.md + banner session-handoff + AGENTS.md.
> **NGHIÊN CỨU KHO KIẾN THỨC ✅ XONG (workflow `wf_f83e8fa0-19f`, 10 agent: 3 probe + 2 design + 4 red-team + synth) — verdict GO_WITH_ADJUSTMENTS (4/4 red-team), thiết kế chốt ghi `KE_HOACH_KHO_KIEN_THUC.md`:**
> - **Bằng chứng probe thật:** 7 va-chạm cùng-token-khác-nghĩa có nguyên văn (ĐC↔DC tái hiện TRONG 1 FILE, handle 16AA1F/17F56D; D/Đ1/C1/CT/M/CH...); bão-hỏi đo được 50-80% câu thừa nếu không gate; kiến thức rải rác ~25+ chỗ tools_core chưa version.
> - **Thiết kế chốt (lai):** `kienthuc.py` kiểu I9 (KB_VERSION/HASH, degrade-safe) + entry digit-free 2-tầng-khoá (giữ đ/d) + **chống-lọt-grounding 3 tầng** (payload cấm số + strip key `_kb` allowlist-of-one + test B5 end-to-end) + **gate hỏi bằng-chứng-dương-nội-file + cap 1 câu/lượt** + confirm-only host-only (endpoint /xac-nhan, KHÔNG qua chat) + ASK/NEVER_AUTO 100% (không auto-resolve khi ship) + kb-refreeze 1 lệnh. 7 lát L0→L7 (L7 đổi-số HOÃN).
> - **⚠ PHÁT HIỆN AN NINH HIỆN HỮU (đã TỰ XÁC MINH code):** `_TOOL_KHONG_CHO_LLM` (mcp_bridge:173) chỉ lọc DECLARATION (:177); vòng dispatch (:700) `bridge.call(fc.name)` thi hành MỌI tên tool Gemini phát → Gemini/injection có thể gọi `hoc_quy_uoc`/`nap_ban_ve` host-only bằng cách phát đúng tên. **Vá = L0 gate dispatch-side (~3-5 dòng), độc lập kho, làm ngay được.**
> - **✅ USER ĐÃ CHỐT (AskUserQuestion):** (1) CÓ làm nút /xac-nhan trên web UI (đủ L5); (2) GIAO dev tự chốt danh sách ký hiệu đợt đầu theo tần-suất-đo-được. (Mặc định giữ: xác nhận per-phiên-file; L7 hoãn; giới thiệu tính năng đúng mức.)
>
> **TRIỂN KHAI L0+L1+L2 ✅ CODE XONG — check.sh [29/29] HARNESS GATE PASS (⚠ CHƯA commit — chờ user chốt):**
> - **L0 — gate dispatch-side (`mcp_bridge.py`):** `_ten_tool_cho_llm(bridge.tools)` + gate `fc.name not in _ten_llm` TRƯỚC `bridge.call` → tool host-only/tên-lạ bị từ chối bằng `_loi_tool_host_only()` (dict TƯƠI, SẠCH SỐ, KHÔNG chèn fc.name — tên do model phát có thể mang chữ số lọt rổ) + tự append FunctionResponse + continue (không qua nhánh evidence/gom-số). Vá lỗ AN NINH HIỆN HỮU (model/injection gọi được `hoc_quy_uoc` qua dispatch). Test `test_dispatch_gate.py` **11/11** (tập dispatch == tập declaration; source-guard thứ tự gate-trước-call). check.sh **[28]**.
> - **L1 — `kienthuc.py` (24 entry đợt đầu) + `KB_VERSION`/`KB_HASH` byte-lock `e55ac112…` + `harness/scripts/kb_refreeze.sh` + `/version` lộ kb_version/kb_hash:** entry digit-free 2-tầng-khoá (khoa_phan_biet giữ đ/d ≠ khoa_sap; trùng khoá-sập bắt buộc có cạnh confusable_with — validator kiểm), on_collision ASK 100%, confirm_template luôn có `khac_khong_chac`, data thuần không I/O không import dự án (degrade-safe). 24 entry = ca đã-trả-giá + va-chạm đo được (cặp ĐC↔DC; CH; họ D/Đ/C/T/S/V/K; B/M vật liệu; DK/TL/L/i hình-thức-tự-phân-biệt → KHÔNG hỏi; Km+; cút-góc; 'WORD - n.nnn'; mũi-cọc≠đáy-đài; WC/GM word-like cấm suppression). Test `test_kienthuc.py` (K1-K8): validator 0 vi phạm + **B5-lite THẬT `_collect_numbers`(payload mọi entry)==RỖNG** + tra cứu 2 tầng + fail-open + grep-guard data-thuần. check.sh **[29]**.
> - **L2 — chống-lọt-rổ tầng bridge (`_strip_kb`):** strip đệ quy key `_kb` (allowlist-of-one-key) trước `_collect_numbers` + thêm `tra_ky_hieu` vào tuple loại-toàn-phần. Test K9 (số LÉN trong `_kb` giả-lập-entry-lỗi KHÔNG lọt = tầng 2 cứu khi tầng 1 thủng) + K10 (số FILE ngoài `_kb` VẪN vào rổ — không từ-chối-oan) + K11 source-guard.
> - **GATE BẮT 2 REGRESS THẬT (đúng vai trò):** (a) [19] grounding-guard 43/47 — mock `_Bridge.tools=[]` phi thực tế bị L0 từ chối tool giả `tim_kiem` → vá MOCK (khai báo tool nó dùng) → 47/47; (b) [26] bang-ve-net 8/9 — test khoá chuỗi nguyên văn call-site cũ `_collect_numbers(result)` → cập nhật theo dạng mới `_collect_numbers(_strip_kb(result))` (ý định giữ nguyên, dạng mới khoá riêng ở K11a) → 9/9. ⚠ Bài học: notification nền báo "exit 0" nhưng GATE THẬT в file là FAIL — PHẢI đọc file output, đừng tin summary.
> - feature_list.json 39→41 (kb-l0-dispatch-gate, kb-l1-kienthuc-module).
>
> **NỐI (cùng phiên) — L4 GRAFT CÓ GATE ✅ CODE XONG + **check.sh [30/30] HARNESS GATE PASS chốt** (verify log thật: 0 FAIL, takeoff 272 · misc 107 · grounding 47 · cao_do 31 · kb-graft 18 · kienthuc 15 · dispatch 11) (user chốt "làm tiếp, commit/push/deploy MỘT THỂ sau"):**
> - **Cắm kho vào 3 điểm đọc** (`tools_core.py`): `phan_loai_tin_hieu` + `doi_chieu_nghi_ngo` (nguồn (d) "đa nghĩa ký hiệu (kho kiến thức)") + `cao_do_min_max` (móc cb_am `'WORD - n.nnn'` = đường kích hoạt thật ca CH-2.700). ADDITIVE + FAIL-OPEN tuyệt đối (mọi graft try/except→None; `_kienthuc=None` → hệ y hệt cũ — test khoá E1).
> - **GATE bằng-chứng-dương nội-file (chống bão-hỏi 50-80% đo được):** chỉ hỏi khi entry confusable VÀ (cả-2-dạng-raw cùng tồn tại qua cạnh confusable_with [lazy `_kb_quet_file` — tập khoá `_norm_ma` letter-run] HOẶC mã dính ≥2 LOẠI index section+door [`_kb_hit_types`]) VÀ engine chưa tự ghép 1 loại VÀ chưa hỏi trong phiên; **CAP 1 câu/lượt** + trạng thái `kb_hoi` chống lặp + `kb_da_phat` (nền L5 fail-closed) + legend-note. Câu hỏi nội-suy `{ky_hieu}` bằng token THẬT của file; toàn bộ payload dưới key `_kb` (L2 strip); nguyên văn+handle NGOÀI `_kb`.
> - **Test khoá `test_kb_graft.py` 18/18** (synthetic offline: cặp-bằng-chứng hỏi / đơn-độc im / engine-đã-ghép im / chống-lặp xuyên-tool / móc CH-2.700 / grounding-parity / degrade-safe / fail-open) → check.sh **[30]**. **RED-TEAM-IMPL CORPUS THẬT:** file kết cấu móng C1 cặp ĐC/DC thật (khoá djc+dc cùng file) → **HỎI đúng**; file kết cấu thuần-cột → **0/9 mã bị hỏi**; 2 file sanity khác → 1 ca fire duy nhất là mâu-thuẫn 2-index THẬT (`D1` vừa section vừa door cùng file = đúng bài học id84 DẦM D1≠CỬA D1, không phải hỏi oan). feature_list 41→42.
> - **Gate bắt regress thứ 3 (cùng lớp với 2 ca trước — mock/fake lệch hợp đồng mới):** [20] cao_do 30/31 — `_Fake` trong `test_cao_do_min_max.py` (docstring "chỉ đọc self.texts") thiếu method graft L4 → AttributeError. Vá FAKE trung thực hơn: mượn `tc.Drawing._kb_hoi_am_cach` THẬT + state `kb_hoi/kb_da_phat` (graft chạy y sản phẩm, không stub né) → 31/31. **Bài học gộp 3 ca: graft additive vẫn ĐỔI HỢP ĐỒNG ngầm của self/call-site — mock/fake/source-guard trong test PHẢI cập nhật theo, và gate là thứ bắt được.**
> - ~~⏳ L5~~ → **✅ XONG (xem entry dưới)**. **⏳ CÒN: L3** (tool `tra_ky_hieu` + mảnh prompt `_P_R18` → bump PROMPT_VERSION + **đo A/B LIVE**) · L6 garble-code · L7 HOÃN. **📌 USER CHỐT (2026-07-26): KHÔNG đổi API key Gemini — dùng key user đã đưa cho L3; ĐỪNG nhắc thu hồi nữa.** **⚠ TOÀN CỤM L0-L5 CHƯA COMMIT (user chốt: commit/push/deploy MỘT THỂ sau).**
>
> **NỐI (2026-07-27) — L7 NGHIÊN CỨU → **KHÔNG LÀM** (có SỐ) + VÁ 3 BUG THẬT trong L5 (+7 vá từ red-team), gate [33/33] PASS:**
> - **L7 (xác nhận ĐỔI SỐ) = KHÔNG NÊN LÀM.** Workflow `wf_92eee202-d98` (11 agent) ĐO THẬT: **62 file / 493 mục / 357 mã → 0 mã có ≥2 loại = 0 ca kích hoạt** (không phải hiếm — CHƯA TỪNG xảy ra). Lý do: nhãn VN thật mở đầu bằng 'MẶT CẮT'/'CHI TIẾT'/'CẤU TẠO' hoặc garble ('cột'→'cét') nên `_ma_type`=''. **Ví dụ trụ cột trong docstring `_ma_key` là SAI so với code**: `'cửa'` ∉ `_MA_TYPE_WORDS` (14 từ) → `_ma_code('CỬA D1')='cua d1'` ≠ `'d1'`, KHÔNG bao giờ va nhau (tôi tự chạy xác minh). **ĐÍNH CHÍNH cách hiểu:** gộp **KHÔNG CỘNG** mà **giữ 1 vứt 1** → bấm sai làm tổng đi **XUỐNG** (đo: 1 cú nuốt 14 dòng/51 SL = 7% BOQ), và bảng sai **TRÔNG SẠCH HƠN** bảng đúng = đúng khuôn `thap_nhat_dang_tin` đã NO_GO. **Trả lời user:** undo chữa "giá trị sai", KHÔNG chữa "không ai biết là sai"; cửa sổ undo ~30' vs phát hiện sau nhiều ngày; Excel đã gửi đi thì undo bán kính = 0.
> - **NHƯNG nghiên cứu lộ 3 BUG THẬT trong L5 đang LIVE (tôi tự tái hiện cả 3 trước khi vá):** (0) **undo NÓI DỐI** — `thu_hoi` luôn `ok=True` + "đã gỡ (nếu có)" nên trượt khoá đ/d vẫn in "✔ Đã gỡ" trong khi state còn nguyên; (1) **cổng fail-closed KHÔNG khoá theo mã** — `kb_da_phat` cặp `(entry,option)` → hỏi 1 mã **mở khoá xác nhận cho MỌI mã** (repro: `MA-KHAC-999` lọt); (2) **giao diện KHÔNG có nút Hoàn tác** (`xacNhanBtn` ghi đè cả khối, chưa từng gửi cờ `thu_hoi`) + bấm **'khác/không chắc' khoá câu hỏi tới hết phiên**.
> - **VÁ:** (0) pop CẢ `kb_xacnhan` LẪN `kb_hoi`, không gỡ được → `ok=False`+`khong_co_gi_de_go`, gỡ được → `loai_da_go` + câu chữ ĐÚNG từng ca; frontend kiểm `da_thu_hoi`. (1) `kb_da_phat` → **BỘ BA** `(entry,option,ma_key)`; kênh cao độ có hằng `_KB_KENH_CAO_DO='@cao_do'` riêng. (2) giữ khối nút + **'↩ Hoàn tác'** + **bảng `#xnbox` thường trực** (tool #33 `danh_sach_xac_nhan` HOST-ONLY + `GET /xac-nhan/danh-sach`) → 'khác/không chắc' **gỡ được, câu hỏi quay lại**.
> - **RED-TEAM IMPL (`wf_5a1e6c98-979`, 4 agent engine thật) — GO_WITH_ADJUSTMENTS, 0 CHẶN, bắt 3 CAO (2 do CHÍNH bản vá của tôi) + 4 TB/THẤP, ĐÃ VÁ HẾT:** **CAO-1 lệch khoá** (khoá dùng `ma` thô, nút echo `ma.strip()[:40]` → hệ **HỎI rồi TỪ CHỐI chính câu nó hỏi**, mã >40 hoặc có khoảng trắng → **kẹt chết cả phiên**) → chuẩn hoá MỘT LẦN ở biên; **CAO-2 route xác nhận TẠO phiên** → **4 GET vô danh đuổi phiên đang mở bản vẽ** qua LRU → `_phien_hien_co()` cho CẢ 2 route; **CAO-3 bảng thiếu/dư** → `taiDanhSach()` ở init + `showSum`; TB `hoanTacDs` nuốt lỗi; TB `doi_chieu_nghi_ngo` lật ngược "cần XÁC NHẬN" ngay sau khi xác nhận (bug L5 gốc); THẤP bảng phơi khoá `djc-1` / `thu_hoi:"false"` chuỗi truthy / GET chờ khoá vô hạn. **Red-team KHÔNG phá được:** xác nhận khống · va chạm khoá 2 chiều · undo 2 lần/trượt khoá · **tất định vòng undo (deepcopy state)** · AI chặn 2 tầng cả 2 tool mới · `_kb` không lọt grounding · fail-open · **XSS 5 payload** · **fuzz 40.000 chuỗi `_norm_ma`**.
> - Test `test_kb_xacnhan.py` **19→44 ca**; gate bắt **2 regress** (A6 khoá dạng cặp cũ; X6b ăn ké phiên do route tự tạo) → cập nhật theo dạng MỚI chặt hơn. check.sh **[33/33] PASS**, 33 tool, feature_list 46.
> - **✅ LIVE `c9e2171`** (verify ~30s: `/version` commit khớp + prompt/kb giữ nguyên + `/health` ok; **verify TRANG THẬT: 'Hoàn tác' ×2 · `thu_hoi:true` ×2 · `xnbox` ×3 · `taiDanhSach` ×6** — nút Hoàn tác + bảng thường trực đã có mặt trên demo, không chỉ trong repo).
> - **BÀI HỌC PHIÊN NÀY (đắt, nên nhớ):** vòng vá đầu (3 lỗi) tự nó **đẻ thêm 2 lỗi CAO** (CAO-1 lệch khoá, CAO-2 route tạo phiên) — **red-team-implementation bắt được cả hai**, gate KHÔNG bắt nổi vì cả hai đều "đúng theo test đã viết". ⇒ với thay đổi chạm **vòng đời state + route + giao diện**, test-của-chính-mình là chưa đủ; phải có vòng đối kháng chạy engine thật. Cũng lần thứ 4-5 trong phiên gate bắt được "hợp đồng ngầm đổi mà test cũ khoá dạng cũ" — dấu hiệu tốt, không phải phiền.
>
> **NỐI (2026-07-27) — L6 GARBLE ĐƯỜNG KÍNH ✅ LIVE `fccc635`** (gate **[33/33] PASS** 0 regress → commit+push+deploy+**verify LIVE ~60s**: /version=fccc635 + prompt/kb giữ nguyên + /health ok). **KHO KIẾN THỨC L0-L6 HOÀN TẤT TRỌN — chỉ còn L7 HOÃN (gated red-team 2 tầng riêng) + họ-slash DEFER.**
> - **Fold `_GARBLE_DIA_RE` trong `_garble_fold`** (tools_core:54-66): `'ỉ/Ỉ'` + `'/g|/G'` LIỀN SỐ + KHÔNG dính chữ trước → `'ø'`, chạy **TRƯỚC unaccent** (unaccent sập ỉ→i làm mất phân biệt thép hình I10/độ dốc i — không sửa được sau). Đúng thiết kế L6 từ red-team kho (RT2-4: alias garble CẤM vào kho — vá tầng CODE có gông + đo corpus).
> - **Bằng chứng ≥3 firm:** 'kim thu sét ỉ20'/'dây tiếp địa ỉ14' (điện) · **'Ỉ16X2400' mà CÙNG FILE ghi 'Ø16 DÀI 2,4m' cùng đối tượng** (firm khác — chứng cứ chéo) · 'ống thông hơi ỉ50' (cỡ uPVC) · '/g10' 67× cạnh a150 · 'MÓC CẨU /G8' · 'thép ỉ10 neo xà gồ' (KT CT-A).
> - **ĐO corpus:** quét 53 file → **98 'ỉ' + 568 '/g' mở khoá, 0 PHẢN-KHỚP**; Drawing-level trước/sau 4 file: **thep_kg/qty/cao_do/so_text BẤT BIẾN 100%**, recall tìm-Ø tăng đúng (KETCAU_CA Ø10 **11→78**; CAPDIEN 0→12; MONG Ø8 72→80; KT +1 XÁC MINH THẬT). **Họ-slash đầy đủ DEFER** (1 file/firm, mapping phức tạp, rủi ro 'kG//cm2'; subset '/G8' đã ăn theo).
>
> **🏁 CHỐT SỔ CỤM KHO KIẾN THỨC (2026-07-27): ✅ COMMIT `998950f` + PUSH + DEPLOY + VERIFY LIVE MỘT THỂ** (user chốt gộp): `/version` = commit `998950f` + prompt_version `2026.07.27-kb-l3` + prompt_hash `239e8b7b…`==FROZEN + **kb_version `kb-2026.07.26-dot-dau` + kb_hash `e55ac112…`==byte-lock** (kho lần đầu có định danh trên LIVE) + `/health` ok, deploy ~60s. Nội dung: **L0** (gate dispatch — vá an ninh) · **L1** (kienthuc.py 24 entry + kb_refreeze) · **L2** (_strip_kb) · **L4** (graft gate, red-team corpus thật) · **L5** (confirm-only + nút /xac-nhan) · **L3** (tra_ky_hieu #32 + _P_R18, **A/B LIVE GO**). Gate [27]→**[32/32] PASS**. Tool 30→**32**. feature_list 39→**44**. HEAD `998950f`==origin, tree sạch. **CÒN của kho: L6** (garble-code, nhỏ, tách riêng) · **L7 HOÃN** (đổi số — gated red-team 2 tầng).
>
> **NỐI (2026-07-27) — L3 (tool tra_ky_hieu + _P_R18) PHẦN OFFLINE ✅ XONG, check.sh [32/32] PASS; ⏳ ĐANG ĐO A/B LIVE:**
> - **Tool #32 `tra_ky_hieu`** (tools_core + mcp_server, PHƠI cho LLM — ngược với xac_nhan host-only): tra kho read-only; query người-gõ dùng KHOÁ SẬP kéo NHÓM dễ-nhầm ('DC' kéo cả ĐC qua cạnh) + cờ `khop_chinh_xac` giữ đ/d; FAIL-OPEN ngoài kho → "KHÔNG đoán"; injection qua tham số vô hại; kèm trạng thái đã-xác-nhận phiên; câu hỏi confirm CHỈ đi qua `_kb` CÓ GATE (không bão-hỏi); listing pop cau_hoi/phuong_an trần; **kết quả bị LOẠI TOÀN PHẦN khỏi rổ grounding** (tuple L2 đã chờ sẵn); WORM log ký-hiệu-MISS = nhiên liệu dev soạn entry mới.
> - **Mảnh prompt `_P_R18`** (chỉ luật TRÌNH BÀY + định tuyến): hỏi 'X là gì' → GỌI tra_ky_hieu; nêu ĐỦ nghĩa KHÔNG tự chọn; tier=xuất xứ cấm dùng để quyết nghĩa; ⛔ cấm dùng mô tả kho làm SỐ LIỆU; ngoài kho → nói thẳng, đừng đoán; có `_kb.cau_hoi` → nêu NGUYÊN VĂN + mời BẤM NÚT, ⛔ cấm tự xác nhận thay. Chèn TRƯỚC `_P_R9` (tiền lệ R7b; emit 24→25, VN 16→17); **PROMPT_VERSION `2026.07.27-kb-l3`**, re-freeze FROZEN `239e8b7b…` (taxonomy 24/24).
> - Test `test_tra_ky_hieu.py` **13/13** → check.sh **[32]**; full gate **[32/32] PASS** (verify log: 0 FAIL, 30 suite xanh).
> - **✅ ĐO A/B LIVE XONG — VERDICT GO** (30/30 câu, human-judge per-case đọc full answer theo `[[feedback-do-thay-doi-prompt-ab]]`): **routing 6/6 CẢ 2 VẾ** (tool-description tự lái đủ; R18 = đai an toàn — không chứng minh delta routing, không cần); **TRAP CHỐNG-BỊA 5/5 GIỮ cả 2 vế** (chiều-dài/khoảng-cách/toạ-độ/hướng/giá — 0 lật sang bịa); **recall giữ** (24 bộ D1 [67CDF] cả 2 vế); **kb_cau_hoi=1 nổi đúng** file cặp ĐC/DC (gate server-side, độc lập prompt); **GIÁ TRỊ THẬT của R18 = TRÌNH BÀY**: vế B nêu NGUYÊN VĂN câu hỏi + ĐỦ 4 phương án khớp nút bấm L5 (vế A chỉ hỏi chung chung không phương án) + nêu đủ nghĩa (B20: A tự chọn 1 nghĩa, B đủ 3) + caveat trung thực "từ kho kiến thức chung, không phải đọc từ bản vẽ này". 0 regression. Caveat: 1 run + Gemini variance (không overclaim). JSONL: scratchpad `ab_l3_results.jsonl`.
>
> **NỐI (cùng phiên) — L5 KÊNH XÁC NHẬN CONFIRM-ONLY ✅ CODE XONG + check.sh [31/31] HARNESS GATE PASS (verify log: 0 FAIL, xanh NGAY lần đầu — không regression; kb-suites 11/15/18/19):**
> - **Drawing.xac_nhan_ky_hieu** — FAIL-CLOSED 3 lớp: kb_id tồn tại + option ∈ ENUM dev-soạn + (entry,option) ∈ `kb_da_phat` ĐÃ PHÁT trong phiên (không xác nhận khống). State per (entry|mã): **da_xac_nhan** (nhãn "theo xác nhận trong phiên file này" — TUYỆT ĐỐI không đổi số) / **khac_khong_chac** (giữ bí, không nhãn, suppress re-ask) / **thu_hoi** (gỡ + CHO hỏi lại). Sống trên Drawing → đổi file reset. L4 helpers check `kb_xacnhan` TRƯỚC khi hỏi + phát kèm `ma` echo.
> - **MCP tool #31 `xac_nhan_ky_hieu` HOST-ONLY 2 hàng rào** (declaration-filter + L0 dispatch-gate — AI phát đúng tên cũng bị chặn, test X4) + WORM log xác nhận + log `kb_id` lúc PHÁT-HỎI (`hoi_de_hoc`).
> - **Đường đi câu hỏi → nút bấm:** bridge `_kb_hoi_tu_result` gom câu hỏi từ `_kb` (top-level + nested `nghi_ngo`, dedupe, bỏ note) → `tra_loi_ai` trả **`kb_cau_hoi`** ở mọi return thành công → `/ask` truyền thẳng → PAGE JS `kbHtml`/`xacNhanBtn` render nút (data-attribute + `esc` mở rộng escape dấu-nháy-kép chống chèn thuộc tính; caption "Chỉ bạn bấm được — AI không tự chọn") → **POST `/xac-nhan`** (session-lock, `bridge.call` thẳng, KHÔNG qua chat/Gemini; 400 khi chưa nạp).
> - Test 19/19: fail-closed ×3 + flow xác-nhận/thu-hồi/không-chắc + host-only 2 rào + collector + endpoint 400/pass-through + PAGE hook + source-guard kb_cau_hoi. feature_list 42→43.

---
## Session 2026-07-26 (nối) — NHÓM C: nghiên cứu chịu-tải RSS thật + adversarial-verify → user CHỐT HOÃN tới CUỐI dự án (tốn tiền)
> **KHÔNG code, KHÔNG đổi LIVE.** Baseline verify đầu phiên: check.sh **[27/27] PASS** (30 tool, takeoff 272, grounding 47…), HEAD `526edbf`==origin, tree sạch. (⚠ pytest vẫn crash 'I/O closed file' — user hỏi `cd backend && pytest` nhưng KHÔNG có backend/, gate = check.sh.)
> **User giao "nghiên cứu chi tiết + triển khai nhóm C (nâng RAM)".** Nghiên cứu ground bằng ĐO THẬT (84 file, RSS PeakWorkingSet trong `_khao_sat/bao_cao*.json`, 100 .dxf sẵn — khỏi ODA lại) + workflow adversarial-verify 5 agent `wf_4e2405d0-971`:
> - Mô hình ĐÚNG: container = **316 + 11.28×dxf** (web 68 + subproc 68 = 2 RSS RIÊNG Render cộng cả — tôi từng tính nhầm 1×). ⇒ `READFILE_MAX_MB=`**120** (không phải 200 HELD; 130 phá lằn 0.85), `MAX_SESSIONS=`**1** → mở khoá **13/14** file >45MB (chỉ file 202MB vẫn chặn). 14 file bị chặn: 13 file 46.6–114.4MB + 1 file 202MB.
> - **⛔ Phát hiện quan trọng: `MAX_SESSIONS=1` chỉ là cap "MỀM" — config đúng CHƯA đủ.** 3 lỗ code cho 2 doc ezdxf cùng RAM (~2640MB OOM): (a) phiên bận không bị đuổi `app.py:107-108`+lock non-blocking `:72` [cố ý cho F-A]; (b) `close()` fire-and-forget `mcp_bridge.py:148-150`; (c) `nap_ban_ve` giữ doc cũ `mcp_server.py:33-34`. Đã VERIFY code (b)(c) tay. ⇒ cần **vá code (đồng bộ close + chặn cứng khi bận + del doc cũ)** TRƯỚC gói trả phí — phần vá này FREE, cũng cứng bản Free.
> - HELD `f025ad7` BUGGY: 200→OOM file 202MB; quên hạ MAX_SESSIONS(=4); "5.8x" là tracemalloc. Windows≠Linux → phải đo lại cgroup RSS trên Render.
> **USER CHỐT (giữa phiên): nhóm C = HOÃN TỚI CUỐI DỰ ÁN** — nâng RAM tốn tiền túi, chờ dự án xong + sếp ưng → gọi tài trợ. Chỉ API key Gemini free; mọi chi phí khác = tiền mình → tránh. Demo dùng file ≤45MB. **KHÔNG chạm code/config LIVE lần này.** Đã note harness (session-handoff banner + AGENTS.md) + memory `[[project-chiu-tai-va-chi-phi]]`/`[[project-uu-tien-nhom-cong-viec]]`. **Bước tiếp: chuyển sang nhóm D** (nhóm A còn lại đa số bị chặn RAM/file/user).

---
## Session 2026-07-26 — NHÓM A recall: I3-U L2 `9d90b25` + rà soát toàn dự án (artifact) + ưu tiên A→C→D→B + recall root-cause + offline A/B/C `81b0a52` + routing+prompt-half LIVE `d244865` (đo LIVE A/B GO)
> **CHỐT SỔ CUỐI PHIÊN (2026-07-26):** HEAD `5d3d300` == origin, working tree SẠCH. check.sh **HARNESS GATE PASS [27/27]** · **30 tool** · takeoff **272** · qa 129 · grounding 47 · misc **107** · prompt-taxonomy 24 (hash `e5e05d7d`) · 0 regress. ⚠ pytest KHÔNG dùng (crash 'I/O closed file' — 'no tests ran'); gate = check.sh. Chuỗi commit phiên: `9d90b25`(I3-U L2)→`5603c06`(docs)→`81b0a52`(recall A/B/C)→`ca9aa90`(docs)→`d244865`(routing+prompt-half LIVE A/B)→`5d3d300`(docs). LIVE verify /version: commit d244865, prompt_hash `e5e05d7d`, prompt_version `2026.07.26-routing-l2`, /health ok. **VIỆC CHỜ:** nhóm A còn 13 ca hatang chặn RAM 45MB (→ nhóm C) · Pattern D/E recall biên (hoãn, rủi ro) · id135 deep chờ file · ⚠ **key Gemini user dán trong chat — nhắc THU HỒI**. Bước tiếp theo hợp lý = **nhóm C (nâng RAM)** (đúng ưu tiên + mở khoá 13 ca hatang).
> **CHỐT SỔ:** check.sh **[27/27] PASS** · takeoff **262→272** (+I3-U L2 +C1-lite) · qa 129 · grounding 47 · 0 regress. **I3-U L2 code-only LIVE `9d90b25`** (code) + `5603c06` (chốt sổ docs). Working tree sạch, main==origin.
> **BỐI CẢNH PHIÊN:** (1) user yêu cầu **tổng rà soát toàn dự án** → workflow 6-agent quét mọi doc (`wf_d5d37fa6-683`) → **artifact "Rà soát đầu mục"** phân 64 mục thành A(chức năng chính chống-ảo-giác)/B(dự toán-Excel)/C(RAM-upload)/D(khác). (2) user **CHỐT thứ tự ưu tiên A→C→D→B** → ghi `AGENTS.md` + banner `session-handoff.md` + memory `[[project-uu-tien-nhom-cong-viec]]`. (3) chọn đầu mục nhóm A tiếp theo.
> **CHỌN ĐẦU MỤC A qua workflow probe 5 ứng viên (`wf_fc8788d7-dd2`) — KẾT QUẢ QUAN TRỌNG: CẢ 5 HOAN.** Các đầu mục A "an-toàn + rẻ + giá-trị-cao" GẦN CẠN: C1 audit-resolver (lớp resolver bão hoà chống-bịa, ~0 suspect mới) · C2 I7-giảm-từ-chối-oan (guard đã cực rộng tay: từ-chối-oan thật ≈**1/198** và ca đó là recall-miss không phải guard-nuke → nới guard chỉ mở lại id135-bịa) · C3 I6-detector-bỏ-sót (residual **47-100%** mọi file → báo động 90% = alarm fatigue; bản scoped đã LIVE = `hoi_de_hoc`) · C5 U2/U3-OCR (blocked: U2 greenfield overfit cần ≥3 firm; U3-OCR sai-ký-tự = sai-tự-tin). **Điểm yếu THẬT của demo = 22 câu recall-miss (retrieval: tool không tìm ra) — không đầu mục safe nào chữa được** (cần corpus/file bị chặn).
> **LÀM: C4 = I3-U Lớp 2 CODE-ONLY** (winner 7.5đ — giao điểm duy nhất chạm-recall × doable-now × không-blocked × rủi-ro-thấp). Helper `_quy_doi_don_vi_dai` quy chuỗi tag `'3.6m'`→mm (fullmatch); cắm dispatch `tinh_dai_luong` CHỈ khi `dv=='mm'`+chuỗi-khớp → vá từ-chối-oan; degrade-safe (số/'3600'/bare-3.6/kg/m²/'-3.6m'/'0m'/'3.6 m2' giữ cũ = 0 regress); **robust cho MCP-client trực tiếp** (không có luật ×1000). KHÔNG động SYSTEM_PROMPT/grounding-guard → luồng Gemini không đổi → không cần đo LIVE. Red-team-impl engine thật 54/54; test +10 → takeoff 272. **Nói thẳng KHÔNG overclaim:** đây là tăng-cường VỪA PHẢI (Gemini path Gemini đã tự ×1000 nên ít kích hoạt) — giá trị lớn thật = phần prompt-half.
> **⏳ NHẮC USER (chốt làm LẦN SAU):** I3-U L2 phần còn lại = đổi SYSTEM_PROMPT để CODE sở hữu unit-math (Gemini truyền 'giá-trị+đơn-vị verbatim', ngưng ×1000) + update `tests/kichban_gd2.py` + ĐO LIVE. User chọn "làm nhưng nhắc ở lần giao việc tiếp theo".
> **NỐI (cùng phiên) — NGHIÊN CỨU RECALL TRIỆT ĐỂ + vá 7 ca offline ✅ LIVE `81b0a52` (code) + chốt-sổ:** user đẩy "giải quyết triệt để điểm yếu recall, không nửa vời". Root-cause 60 ca recall-miss qua workflow `wf_0d021c50-125` (probe engine THẬT offline): **48/60 = GEMINI ROUTING** (tool CÓ data, `tim_kiem` trả đúng, Gemini TỪ CHỐI thay vì gọi) → PROMPT/tool-desc (LIVE, đòn bẩy lớn nhất, CHƯA làm); **9/60 = tool bug THẬT** → vá 3 code; 3-4 từ chối ĐÚNG; **13 hatang = chặn RAM 45MB** (hạ tầng nhóm C). ⇒ recall ~92% SỬA ĐƯỢC (bác kết luận vội "corpus-blocked"). **3 fix offline:** (A) `_tok_bound` đối xứng token+label (giữ gạch số-số 'D2-4' khớp, GIỮ 'D2' khớp họ) — recall id73/93/103 + lớp mã; **GATE bắt 1 regress D2-họ (strip-all) → sửa đối xứng**; (B) `thong_tin_file` tool#30 metadata (id39/107); (C) `bang_con` subtotal riêng bảng thép hình/inox (id22/32: 2163.02/161.21, đọc nguyên văn+handle). Test +13 (misc 94→107), 30 tool, check.sh [27/27] takeoff 272, 0 regress. **⏳ CÒN:** ~35 routing-miss (vá prompt R1-R5 + I3-U L2 prompt-half, cần LIVE A/B) + 13 hatang (nâng RAM nhóm C).
> **NỐI (cùng phiên) — LIVE BUNDLE routing + prompt-half ✅ LIVE `d244865` (đo LIVE A/B GO):** đổi 2 fragment SYSTEM_PROMPT (nền I9): `_P_R7b` routing (Gemini BẮT BUỘC gọi tim_kiem trước khi từ chối, câu vật-liệu/ghi-chú/thông-số; +thong_tin_file cho tên file; giữ chống bịa) + `_P_R10` prompt-half (truyền '3.6m' verbatim, code quy đổi). hash bea17c6e→e5e05d7d, PROMPT_VERSION 2026.07.26-routing-l2, re-freeze test (emit 23→24). **ĐO LIVE A/B (key user)** 43 routing+26 trap+prompt-half: recall refused **19→15** (~5 gain đúng có handle, 0 bịa); **anti-bịa: MỌI trap suy-diễn/lạc-đề VẪN từ chối** (id151/153/154/155/150), 0 lật sang bịa, vài trap an-toàn-hơn → routing nudge KHÔNG phá chống bịa; prompt-half: Gemini truyền '3.6m'/'360cm' verbatim → code→4.704 m³ đúng (ca vẫn ×1000 vẫn đúng nhờ backstop). ⇒ GO (caveat: 1 A/B run + variance, không overclaim). check.sh [27/27] takeoff 272 0 regress. Bài học: điểm yếu recall = routing (Gemini), vá được bằng prompt nudge có scope + giữ chống-bịa, đo LIVE xác nhận. **CÒN nhóm A: 13 hatang RAM (nhóm C) + Pattern D/E biên (hoãn) + id135 deep chờ file.**

---
## Session 2026-07-25 (nối) — I9 TÁCH SYSTEM_PROMPT có version/hash ✅ LIVE `de69324` (byte-identical A+, chọn qua workflow 9-agent)
> **CHỐT SỔ:** check.sh **[27/27] PASS** · 29 tool · takeoff 262 · qa 129 · grounding 47 · **prompt-taxonomy 24 (MỚI, I9)** · app-routes 8→10 · 0 regress. **I9 LIVE `de69324`** (code) + `9ee8ac4` (chốt sổ docs). Verify LIVE: `/version` prompt_hash=`bea17c6eec564361f3c2fca21fb1cdd458078b3cda45be1d7f61827100a70e18` + prompt_version=`i9-2026.07.25` + commit=de69324 + `/health` ok. Working tree sạch, main==origin.
> **I9 = TÁCH SYSTEM_PROMPT (P2·S) — hướng A+ (byte-identical) chọn qua workflow 9-agent, 5/5 lăng kính đồng thuận:**
> - **Vấn đề:** SYSTEM_PROMPT là 1 tuple 124 dòng trộn luật-bất-biến (chống bịa/thao túng) với quy-ước-VN theo thứ tự cũ (rule 15 kẹt giữa 14-16, rule 9 cuối, **2 nhãn "8c" trùng**). Spec I9: "tách luật-bất-biến / quy-ước-VN có version".
> - **CRUX:** tách 2 khối SẠCH ⇒ phải ĐẢO thứ tự ⇒ đổi text prompt (lõi chống bịa) ⇒ cần đo LIVE. Workflow so 3 hướng: **A+** (mảnh có tên, giữ byte order → byte-identical), **B** (đảo thật + dọn 8c → cần LIVE), **C** (external-file / prompt-as-data).
> - **KẾT LUẬN có bằng chứng (agent chạy engine thật):** (1) **A+ byte-identical XÁC MINH** — slice-rejoin 23 mảnh == gốc, sha256 `bea17c6e…` (3 agent độc lập + tôi tự đo). (2) **B BÁC** — LIVE KHÔNG chứng minh nổi non-regression: đo THẬT 2 run temp=0 trùng **0/173** câu + lệch **44% handle-set**, nhóm an toàn (bay_ao_giac 14 + bay_lac_de 9) **0/23** tái lập → noise floor > effect size; **KHÔNG phải vấn đề tiền/API mà là độ-phân-giải-đo**. Thêm: "tách thật" phần lớn ẢO (34/39 mệnh đề ⛔ lồng trong thân rule VN). (3) **C-external BÁC** — phá offline-import (check.sh + 2 test prompt phụ thuộc). (4) **C-idea GỘP vào A+ miễn phí:** lộ prompt_hash ở /version (audit thật — /version trước KHÔNG có định danh prompt) + tách tên 2 mảnh 8c ở source.
> - **Đã làm (mcp_bridge.py):** 23 mảnh có TÊN → `_INVARIANT`(7)/`_VN_CONVENTION`(15)/`_HEADER`(1) + `_EMIT_ORDER` giữ byte order → `SYSTEM_PROMPT="".join(...)`; `PROMPT_VERSION="i9-2026.07.25"` + `PROMPT_HASH=sha256`. app.py /version +2 key. Fragment sinh bằng **SLICE chuỗi đóng băng** (không gõ tay). Docstring TRUNG THỰC: 'tách'=nhãn/index không phải tách rời điều khoản.
> - **Test:** `test_prompt_taxonomy.py` 24 ca (byte-lock sha256 đóng băng + lắp ráp + phân hoạch total+partition + anchor regression) wired check.sh [26→27]; test_app_routes +2. Byte-identity giữ takeoff 262/misc 94/grounding 47/qa 129/cao_do 31/ole 51 KHÔNG đổi.
> - **EOL:** hash GIỮ NGUYÊN local Windows-CRLF ↔ Render Linux-LF (fragment dùng escape `\n`, không newline vật lý). autocrlf=true chuẩn hoá repo.
> - **⏳ Option B HOÃN:** reorder sạch + dọn nhãn 8c = 1 dòng sửa `_EMIT_ORDER` rồi ĐO LIVE A/B với baseline đóng băng — CHỈ khi muốn thử primacy (red-team: upside trong noise, KHÔNG kết luận sẵn). Workflow `wf_f1111f89-fa0`.

---
## Session 2026-07-25 — I3-U L1 ✅ `21926c9` + U6(C) ✅ `a242027` + I2 BOQ ✅ `86776b9` + I4a bảng-vẽ-nét ✅ `6ff81cc` + **I5 micro-fix recall ✅ `8f00510`** + I3-U ngưỡng-sàn NO_GO + U6 iterdxf HOÃN
> **CHỐT SỔ 2026-07-25:** check.sh **[26/26] PASS** · takeoff 262 · visual 15→19 (U6C) · excel 17→21 (I2) · grounding 46→47 · bang-ve-net 9 (I4a) · **misc-tools 84→94 (I5)** · 29 tool · qa 129 · 0 regress. **5 fix LIVE:** I3-U L1 `21926c9` + U6(C) `a242027` + I2 `86776b9` + I4a `6ff81cc` + **I5 `8f00510`** (đều commit+push+deploy+verify /version+/health ok). Working tree sạch, main==origin. Đều qua red-team-trước-code + red-team-impl (repro engine thật). **Chuỗi:** U3 `fd48b19` → I1 `de1ef47` → I3-B `82951db` → I1b `b2a0ea5` → I3-U-L1 `21926c9` → U6C `a242027` → I2 `86776b9` → I4a `6ff81cc` → **I5 `8f00510`**.
> **I5 — THU GỌN sau nghiên cứu (bài học nghiên cứu-trước-code):** probe chạy THẬT PIVOT scope. **Pagination offset/cursor BỎ** (ROI thấp: từ-khoá ngữ-nghĩa max ~123 hits, không chạm trần 200; so_ket_qua luôn phơi tổng thật → cursor ~0 recall). **dem_theo_block DEFER** (value-probe: 2/3 file mọi block ngữ-nghĩa đã trong top-25 liet_ke_block; file thứ 3 block ngoài top-25 chủ yếu annotation + bẫy số-chèn≠số-cấu-kiện). CHỈ CÒN khe recall ĐO ĐƯỢC: default gioi_han=40 < 76-123 cắt kết quả âm thầm → thêm cờ BOOL `bi_cat` + nudge (tim_kiem + liet_ke_chu_theo_layer), prose sạch số (không lọt grounding), additive. Test khoá +8 → misc 84→94. **Nghiên cứu SAVE build 2 feature ROI thấp.**
> **I4a — detector BẢNG VẼ-BẰNG-NÉT (LINE grid + TEXT trong ô) + cảnh báo (nhóm 'làm ngay được', user chốt):** vá lỗ hổng RECALL 'miss âm thầm'. **Nghiên cứu qua workflow** (probe hình học chạy thật 65 file): ~29% file có bảng schedule vẽ-bằng-nét engine đọc 0 block thép; ~8 bản vẽ KẾT CẤU có bảng thống kê THÉP vẽ-bằng-nét → `thep_kg=0` + `co_bang_thong_ke=False` = bỏ sót TOÀN BỘ âm thầm; gần 50/50 với block-ATTRIB. Theo tiền lệ U3/bug-C → DETECT+CẢNH BÁO (I4a), reader (I4b) overfit để sau. **Cơ chế:** tool #29 `phat_hien_bang_ve_net` lazy-scan có CAP; tín hiệu hình học cổng-VÀ (≥4 vạch-hàng đồng-điểm + ≥2 cột trần-15 + ≥3 chữ trong bbox), lượng-tử THÍCH NGHI theo đơn-vị (miễn nhiễm garble/tỉ-lệ), prose sạch số, fail-open; LOẠI khỏi grounding (mcp_bridge tuple exclude) + SYSTEM_PROMPT rule 8d. Red-team-impl chạy engine thật: DƯƠNG 6/6 (thép + kiến-trúc có bảng cửa/toạ-độ thật), ÂM 2/2 (mặt-cắt/OLE), lưới-trục cols=48 loại đúng. Test khoá synthetic 9/9. **RECALL-FIRST: chỉ LỘ cờ, KHÔNG tự đọc/cộng số.** I4b (đọc nội dung→tổng kg) HOÃN (overfit, cần đa-firm).
> **I2 — sheet Excel 'Tien_luong' (BOQ phẳng chuẩn dự toán VN):** vá điểm yếu P1 "đầu-ra VN" (memory `[[project-doi-sanh-kien-truc]]`). Thêm sheet phẳng copy-ready [STT|Mã hiệu(trống)|Tên công tác|Đơn vị|Khối lượng|Diễn giải(=nguồn)|Ghi chú] nhóm theo `loai`+subtotal → cắm thẳng phần mềm dự toán VN. **Nghiên cứu chọn qua workflow** (4 probe: xác nhận khả thi bằng data có sẵn, không cần số mới; probe so-sánh-đầu-mục lỗi serialize nên KHÔNG overclaim 'tối ưu tuyệt đối' — chốt I2 là 'an toàn+giá trị+khả thi đã kiểm', caveat: I2 cải thiện TRÌNH BÀY không phải recall). **AN TOÀN:** tái dùng cùng `th` (2 sheet không lệch — verify subtotal khớp tuyệt đối tong_phu); create_sheet không index + không đổi active (test đọc wb.active không đổi); subtotal lấy trực tiếp tong_phu (không double-count); LOẠI quy_uoc_chua_xac_nhan (P4 — verify 12.5 đang-dạy không lọt); return dict không đổi (không vào grounding); CHỈ khối lượng KHÔNG đơn giá (phạm vi 2026-07-09). Test khoá +4 → excel-content 17→21.
> **U6(C) — hạ trần entity render 20000→6000 (env `RENDER_MAX_ENTITIES`):** đòn bẩy (C) từ nghiên cứu U6, GIỮ 100% chức năng. Đo thật matplotlib ~26KB/entity → cửa-sổ dày 20000 entity ~+500-600MB (khảo sát cũ CHỈ đo parse, bỏ sót spike render); highlight THẬT ≤1067 entity → trần 6000 KHÔNG cắt ca thường, chỉ chặn cửa-sổ dày (~500→~180MB, ~3×). Ô khoanh đỏ vẽ ĐỘC LẬP → hạ trần không mất marker. LỘ cờ bool `anh_bi_cat` + prose sạch số (không lọt grounding). Env-tunable. Red-team-impl repro engine thật (default 6000/highlight thường 964 không đổi/cửa-sổ 7467→cắt 6000/override 2000 chạy). Test khoá +4 visual 15→19. **⏳ đòn bẩy (ii) nâng RAM Standard 2GB (HELD f025ad7 + hạ MAX_SESSIONS 4→2) chờ user billing.**
> **BỐI CẢNH PHIÊN (user 2 lần delegate "nghiên cứu rồi triển khai cái hợp lý nhất"):** id135 deep vẫn chờ file đối tác sâu hơn (TB6 khảo sát nốt = -2.49m NÔNG). Nghiên cứu 2 đầu mục user hỏi: **I3-U** (thiết kế lại) + **U6** (có phá chức năng không). Cả 2 ra kết luận CÓ SỐ, rồi chọn triển khai phần LÀM-NGAY-AN-TOÀN nhất = I3-U Lớp 1.

**I3-U Lớp 1 — vá 2 bug SAI-TỰ-TIN trong `tinh_dai_luong` (corpus-independent, KHÔNG ngưỡng, additive):**
- **(1b) kết quả làm tròn về 0.0** dù mọi input dương (vd `chieu_cao=3.6` gõ MÉT thay mm) → TRƯỚC `co_ket_qua=True + 0.0 m³ + "đọc trực tiếp từ file (đáng tin)"` = lệch 1000× đóng nhãn đáng tin (**repro SỐNG**, tệ hơn ledger cũ ghi "0.005" — round ép về **0.0**). Nay `kq<=0` → `co_ket_qua=False` + cờ BOOL `nghi_ngo_don_vi` + prose SẠCH SỐ. Mirror guard `net<=0` (2437) nhánh trừ lỗ. Cổng chống-crash (2410) chỉ kiểm `isfinite` nên 0.0 lọt.
- **(1a) nhãn provenance sai:** `_nd()` đặt `chua_chac=False` cho input đối-tác-cấp → `not co_chua_chac` True → dán "Mọi input đọc trực tiếp từ file (đáng tin)" cho input KHÔNG đọc từ file. Nay `co_dung_cap=any(nguon=='nguoi_dung_cung_cap')` tách nhánh: VẪN "đáng tin" (R1 pos-control xanh) nhưng bỏ khẳng định sai "đọc từ file".
- **Red-team-trước-code:** kiểm 12 công thức `_FORMULAS` + độ làm tròn (prec 2/3) → cấu kiện thật (cột/dầm/móng/tường/sàn ≥ hàng trăm mm) cho KQ ≥0.01; chỉ kích thước phi thực (cột 5cm) mới round về 0.0 → 0 FP. **Red-team-impl (repro engine thật `BÌA TKTC.dxf`):** bug chặn + `nghi_ngo_don_vi=True` ✓ · 3600→0.174 giữ ✓ · sàn 0.05 m³ hợp lệ KHÔNG chặn ✓ · biên 0.0 chặn ✓. **BẤT BIẾN:** prose sạch số + cờ bool → `_collect_numbers` (mcp_bridge:498 bỏ bool) KHÔNG hút → không tái sinh -22.75.
- Test khoá +4 (`test_takeoff_chong_bia.py` khối I3-U) → 258→262. Gate [25/25], qa 129, 0 regress.

**⛔ I3-U NGƯỠNG-SÀN = NO_GO CÓ SỐ CỨNG (firm-gate đã mở nhưng data giết thiết kế):** workflow probe (dem-firm) đếm **8 đơn vị thiết kế** phân biệt (trùng fax `(0320)3.857.971`/block/nhân sự) → điều kiện "≥3 firm" của gate P5 THOẢ RÕ. NHƯNG probe phân-bố-mm (đo THẬT **86 file/77.083 dim** qua `ezdxf.get_measurement()`): FP dưới sàn toàn corpus <50mm=**7.67%**, chỉ-mm-khai=**4.64%**, **file GỐC-MÉT (hạ tầng) <30mm=34.9%/<50mm=37.3%/<100mm=41.0%** (Firm-hạ-tầng 63-66% dim <30mm). Corpus DỊ CHỦNG đơn vị (40 mm/25 mét/10 vô-đv/9 inch/1 ft/1 mi), nhãn KHÔNG đáng tin → không tách sạch nhóm mét. ⇒ **Ngưỡng sàn tuyệt đối CHẾT kể cả đủ firm.** Memory `[[project-i3-bounds-check-nogo]]` cập nhật. Lớp 2 (unit-tag) + Lớp 3 (cross-check A) đã có kế hoạch, CHƯA code.

**📌 U6 (giảm RAM) — trả lời user: iterdxf HOÃN DỨT KHOÁT (đo RAM thật):** iterdxf-streaming PHÁ 5 chức năng phụ thuộc `self.doc` random-access (I1 `entitydb.get`, render RenderContext+quét lần 2, U3 OLE paperspace, layers, INSUNITS) → rớt gate [11]+[24] VÀ không cứu OOM (render vẫn readfile lại). **Phát hiện đo được:** RENDER (matplotlib) mới phình RAM chính (+231MB/lần, khảo sát cũ chưa tính), không phải parse; trần thật = hằng `READFILE_MAX_MB=45`. **2 đòn bẩy GIỮ 100% chức năng:** (ii) push HELD Standard 2GB [cần billing] + hạ MAX_SESSIONS 4→2; (C) hạ render `hard_cap` 20000→~4-5k [làm NGAY, chỉ đổi độ phân giải]. Memory `[[project-chiu-tai-va-chi-phi]]` cập nhật.

**Đang chờ / bước tiếp:** **id135 deep** chờ file hạ tầng ĐỘC LẬP sâu ≥-5m (đối tác — TB6 nông -2.49m). **I3-U Lớp 2** (unit-tag) — cần user quyết prompt Gemini. **U6 (ii)** nâng RAM Standard 2GB (config HELD `f025ad7` + hạ MAX_SESSIONS 4→2) — chờ user bật billing Render. ~~U6(C)~~ ✅ `a242027` · ~~I2~~ ✅ `86776b9` · ~~I4a~~ ✅ `6ff81cc` · ~~I5~~ ✅ `8f00510` (thu gọn: pagination BỎ ROI-thấp, dem_theo_block DEFER thừa). Còn LÀM-NGAY-ĐƯỢC (không bị chặn): **I9** (tách SYSTEM_PROMPT có version — refactor, cần đo LIVE), **I2-v2** (Diễn-giải công-thức-sống — rủi ro tầng-tổng-hợp), **U2** (zone index, overfit + size L). **I4b** (đọc NỘI DUNG bảng vẽ-nét → tổng kg) + **dem_theo_block** HOÃN tới đa-firm (overfit/thừa). Recall sâu hơn (I6/I7) đụng lõi grounding + cần đo LIVE (API). ⚠ Đa số việc còn lại giờ hoặc CẦN USER QUYẾT (I3-U L2, U6 ii) hoặc CẦN ĐO LIVE/ĐA-FIRM (I9, I4b, I6/I7) — các "làm ngay được an toàn" giá-trị-cao đã cạn dần.

---
## Session 2026-07-24 — I1 (guard handle) ✅ LIVE + I3-B ✅ + I1b (vá guard m2/m3) ✅ + id135-E2E ⏳ (đã ROLLBACK overclaim)
> **CHỐT SỔ 2026-07-24:** check.sh **[25/25] PASS** (28 tool · takeoff 258 · qa 129 · **grounding 46** · handle-guard 44 · i3-bounds 24 · oleexcel 18 · 0 FAIL). **3 fix LIVE:** I1 guard-validate-handle `de1ef47` · I3-B bound-Ø-thép `82951db` · I1b vá-guard-m2/m3 `b2a0ea5`. Working tree sạch, **push hết (Code LIVE `b2a0ea5`, ledger HEAD = commit chốt sổ này)**. Đều qua red-team-trước-code + đo-LIVE. **I3-U HOÃN** tới corpus ≥3 firm (user chốt). **id135: ⚠ tôi OVERCLAIM 'E2E đậu' rồi ROLLBACK** (rachmop là file bug gốc, không độc lập) — sau đó đối tác gửi hạ tầng ĐỘC LẬP **TB6** (`input_files/03.TB6/`): E2E 2 file → generalization + chống-số-mồi VALIDATED, NHƯNG TB6 nông (-2.49m) → **deep-independent CÒN chờ** file đào sâu. **KHÔNG mark id135 done.** Bài học lưu memory [[feedback-khong-overclaim-milestone]]. KHÔNG pytest (dùng check.sh). KHÔNG specs/ (dùng feature_list.json = 28 tool + 33 feature).
> **BỔ SUNG (I1b — vá lỗ THẬT của grounding-guard):** user "làm I1b". Repro engine thật → **giả thuyết FN5-handle-che-chở SAI** (đọc dữ liệu thật ra gốc KHÁC): `_MAHIEU_RES[4]` (`[A-Za-z]+\d+`) **ĂN NHẦM đơn vị 'm2'/'m3'** (Gemini viết SỐ thay mũ ²/³) → `do_luong` rỗng → **guard MÙ với diện-tích/thể-tích BỊA dạng 'X m2'**. Vá: chuẩn hoá `m2→m², m3→m³` (chỉ khi liền sau SỐ) TRƯỚC strip. **LIVE battery bắt bug bản-vá-đầu** (trích từ text gốc → nuke 'Cột 220x220 mm' id77 = false-refusal) → sửa lại (chuẩn hoá thay vì trích-raw). **Đo LIVE 2 lần:** số câu TỪ CHỐI **4→1 (GIẢM, không tăng)**; id77 hết bị nuke; câu mới từ chối duy nhất là variance Gemini (không dính m2/m3). Test grounding **34→46** (+I1b +khoá regression id77). Bài học lặp lại: **test offline KHÔNG đủ cho lõi chống-bịa — phải đo LIVE.**
> **BỔ SUNG (id135 — ⚠ TÔI OVERCLAIM 'ĐẬU' RỒI ROLLBACK 2026-07-24):** battery LIVE (chạy để verify I1b) tình cờ hỏi id135 trên `rachmop.dxf` → Gemini trả ĐÚNG '-14.26m [1F601D]' (bug gốc bịa '-10m'). Tôi ĐÃ VỘI đánh dấu 'id135-E2E ĐẬU' + sửa ledger 'khỏi chờ đối tác' — **SAI = chạy trước ô tô**: `rachmop` CHÍNH là file bug id135 đến từ đó, câu battery thiết kế quanh nó (ky_vong=-14.26) → 'đậu' = không tái phạm CA ĐÃ BIẾT, KHÔNG chứng minh tổng quát hoá (có thể overfit). **id135-E2E THẬT VẪN CẦN bản vẽ hạ tầng ĐỘC LẬP (nguồn khác) — đang xin đối tác.** Đã rollback claim (không bịa dữ liệu — rachmop + -14.26 là thật; chỉ CLAIM 'done' là premature). **TIẾP (user chốt 'chạy TB6 + xin file sâu'):** đối tác gửi bộ hạ tầng ĐỘC LẬP THẬT (TB6 thoát/cấp nước, `input_files/03.TB6/` 26 file). Đọc thật cả 26 file → sâu nhất -2.49m (NÔNG, không -14m); 2 "mốc sâu" là SỐ MỒI (`cút -11,25 độ`=góc ống, `block-25.3`=nhãn) — tool bỏ qua ĐÚNG (áp đúng bài học -22.75: đọc text trước khi kết luận). E2E LIVE 2 file → tool+Gemini đọc ĐÚNG -1.34/-2.49m + không bị mồi = **generalization + chống-mồi VALIDATED trên file độc lập** (rachmop không cho). NHƯNG deep-independent (mốc -14m trên file độc lập) CÒN chờ file đào sâu. id135 = tốt hơn nhiều, VẪN chưa done.

> **BỔ SUNG (I3 thiết kế lại, sau khi plan cũ NO_GO):** workflow `wf_e507ad48` tách I3 làm 2. **✅ I3-B LIVE `82951db`** (verify /version+/health 2026-07-24): bound đường kính thép TRÒN trên ô DK bảng thống kê (`_dk_bat_kha` ≤0/>60mm, `_to_num` BARE) — LỘ nghi_ngo bool + prose KHÔNG số, cờ trong `_acc_thep` không đụng kg → tong_kg bất biến; surface ở `thong_ke_thep`. **KHÔNG-LỌT-GROUNDING verify thật:** biên 60 + bất-khả 1600 ∉ `_collect_numbers` (1600 chỉ ở KEY). Red-team 4/4 GO_WITH_ADJ. Test `test_i3_bounds.py` 24/24, gate **[25/25]**, misc/takeoff/qa KHÔNG đổi. **⏳ I3-U HOÃN tới ≥3 firm** (user chốt — chống overfit): red-team 4/4 GO_WITH_ADJ, cơ chế AN TOÀN (early-return trước compute → 0.005 KHÔNG phát; không lọt grounding), NHƯNG ngưỡng sàn + tiền đề 'mọi mm nguyên' rút n=1 file = overfit → FP sàn mỏng 30-49mm/dim lẻ; cần đa-firm calibrate. Hướng đã vet + memory `[[project-i3-bounds-check-nogo]]`.

> **CHỐT:** check.sh **[24/24] PASS** · **28 tool** · takeoff 258 · qa 129 · **handle-guard 44** · grounding 34 (KHÔNG đổi — I1 không đụng `_guard_text`) · 0 regress. **I1 XONG & LIVE `de1ef47`** (code commit `de1ef47`; verify /version=de1ef47 + /health ok 2026-07-24, rebuild 49s). **I3 NO_GO** (red-team 4/4 lăng kính bác) → giữ đầu mục, thiết kế lại. feature_list: +i1(done) +i3(planned) = 33 mục.

**User:** "làm I1 + I3 luôn". Theo quy trình dự án: probe → design → red-team-TRƯỚC-code → implement → red-team-implementation → gate.

**WORKFLOW 15-agent (probe 4 + design 2 + red-team 8 + synth 1) — bằng chứng chạy engine THẬT:**
- **I1 = GO_WITH_ADJUSTMENTS.** Tự đo trên **854 câu trả lời thật** (5 file battery) đối chiếu entitydb thật 3 file corpus (80k/99k/177k handle): **FP=0/854**, TP=2/854 (ca giá trị nhất: model chép `44C4` trong khi tool trả `449C4` — RỚT 1 chữ số). Cạm bẫy đo được: nhãn trục VN A-F trùng khít bảng hex; 7 mã (C1-C5,D2,D6) đồng thời là handle thật.
- **I3 = NO_GO (4/4 lăng kính, 16 finding CAO).** LỖI GỐC: gắn bound vào TÊN Ô `chieu_cao` (mm) — mà slot này mang **5 nghĩa vật lý** qua 8 công thức (cao cột ~3600 / cao tiết diện dầm / dày đế móng / cao tường / dày lớp đắp). Áp dải cao-cột cho tất cả → **FP 87.5%** (bê tông lót 100mm, đắp cát 200mm, móng đế 250mm bị cờ oan) = TÁI SINH vụ -22.75. Lan chuyền: hằng biên lọt rổ grounding qua chuỗi → câu bịa 'Móng sâu 100m' TRƯỚC chặn nay LỌT (5/6). 2/3 ví dụ đặc tả gốc sai sẵn ('Ø6-51' nổ vào mã dầm/cọc; 'kg thép/m³ BT' khác phạm vi). SỐNG SÓT: I3-B (Ø thép trên ô DK bảng — 0 FP/60 file) + gate provenance vững. BUG THẬT còn nguyên: `tinh_dai_luong(chieu_cao=3.6)` gõ mét → 0.005 m³ vẫn dán 'đáng tin' (lệch 1000×) — cần hướng khác.

**I1 — ĐÃ CODE (7 lát, ADDITIVE THUẦN):** `_collect_handles` (gom handle THẬT mọi khoá chứa 'handle' + `ole:h:`) + `_handle_tokens` (detector FORM A/B/C bám HÌNH THỨC + echo) + `_kiem_handle`/`_apply_i1` (3 tầng: tool-phát→IM / trong-file→IM / không-đâu-có→⚠, mã-hiệu/câu-hỏi→ℹ mềm) cắm 2 điểm return; MCP tool #28 `kiem_tra_handle` (CHỈ ĐỌC, host-only, entitydb.get + `_build_tok_ban_ve`, trả dữ kiện THÔ, KHÔNG phán quyết); `app.py` lưu **answer_goc** (sạch) vào history.

**RED-TEAM IMPLEMENTATION (tự-repro file 26MB) → GO_WITH_ADJUSTMENTS, vá 2:** **F1** kích thước `[900]`/`[2200]` (cửa 900x2200 số THẬT) bị ⚠ nhầm là handle → `_build_tok_ban_ve` tách dãy số ('900x2200'→+'900','2200') → ℹ mềm. **F2** câu từ chối tự nhiên bị nối ⚠ → `_apply_i1` bỏ qua `_REFUSAL_MARKERS`. Đã thử phá THẤT BẠI (I1 vững): perf ~0 (build 0.016s/26MB), fail-open thật (bridge raise/rác/None đều giữ text), 0 crash fuzz, `_collect_handles` không sót trên 16 tool thật, answer_goc luôn sạch.

**BẤT BIẾN khoá test (chống tái sinh 3 tiền lệ):** KHÔNG ngưỡng độ dài/tần suất (handle 2 & 7 ký tự xử như nhau — chống -22.75); KHÔNG trường phán quyết `dang_tin`/`la_bia` (chống thap_nhat_dang_tin); ADDITIVE THUẦN — thân câu byte-identical, KHÔNG bao giờ từ chối; FAIL-OPEN mọi lỗi. Test `test_handle_guard.py` **44/44**.

**Đang chờ / bước tiếp:** commit I1 (+push+deploy+verify LIVE). **I3 THIẾT KẾ LẠI** (user muốn giữ): khoá bound theo đại-lượng-vật-lý-THẬT do RESOLVER quyết (không theo ten_input) + luật 'chỉ cờ khi KHÔNG tồn tại cách đọc hợp lệ' + KHÔNG để biên lọt grounding + chỉ LỘ cờ. **I1b** (vá FN5 `_guard_text`) + đo LIVE calibrate tầng-2. U-series còn U1/U2/U4/U5/U6 + I2/I4-I9.

---
## Session 2026-07-22 (nối, đêm) — U3: ĐỌC BẢNG EXCEL NHÚNG (OLE) — ✅ LIVE `fd48b19` · ⚠ ghi-bù 2026-07-23→24
> **GHI-BÙ (baseline + soạn entry tối 2026-07-23; commit `0cee9b6` sáng 2026-07-24):** phiên đêm 2026-07-22 (chat `279bf2f9`, 14:44→23:22 giờ VN) làm xong U3 + **push + verify LIVE** RỒI máy CRASH khi đang chờ user → entry progress/handoff/feature_list chưa kịp ghi (bạn chưa ra lệnh "chốt sổ"). Nay ghi-bù: **code AN TOÀN** (committed+pushed+LIVE, transcript `279bf2f9.jsonl` còn nguyên, resume được), chỉ thiếu giấy tờ. **Baseline re-verify 2026-07-23:** `check.sh` **HARNESS GATE PASS** (27 tool · takeoff **258** · qa **129** · oleexcel **18** · cao_do 31 · ole-cảnh-báo 51 · grounding 34 · **0 FAIL**).

**Mục tiêu:** U3 (`PHUONG_AN_NANG_CAP_DU_AN.md`) — đọc BẢNG Excel NHÚNG (OLE2Frame). Bug C GĐ4: file "Thong ke thep SUA" bảng thép nằm trong 8 OLE → engine đọc 0 thanh, TRƯỚC chỉ LỘ cảnh báo "không đọc được"; U3 = đọc THẬT nội dung bảng.

**Đã làm (2 commit, LIVE, qua red-team 6 hướng / 26 finding / 8 CHẶN):**
- **`1cc84ad`** — module `oleexcel.py` + probe + `test_oleexcel.py` 18 ca (CHƯA cắm engine). Cơ chế: `ezdxf OLE2Frame.binary_data()` → magic **CFBF offset≠0** (header thừa) → `olefile` → `xlrd` (**vá decode KHOAN DUNG** — vài .xls VN chết utf-16 surrogate) / `openpyxl`. Deps mới: **olefile, xlrd**. Probe corpus: **~89% OLE đọc được BINARY** (KHÔNG OCR); "Thong ke thep SUA" + THPT 67 bảng → đọc hết.
- **`fd48b19`** — WIRING vào engine + verify LIVE (`/version`=fd48b19 + `/health` ok, 23:21). **Red-team đổi thiết kế an toàn hơn:** (a) **số ô OLE KHÔNG vào rổ grounding** — `mcp_bridge` LOẠI `doc_bang_nhung` khỏi rổ neo (nếu vào: số bịa nào cũng khớp → sập guard chống bịa); số OLE = hiển-thị-đối-chiếu, KHÔNG phải chứng cứ. (b) **giàu hoá `ole_nhung`** (1 nguồn quét) thay vì thêm field mới → fake test cũ không KeyError. (c) MCP tool #27 `doc_bang_nhung` chỉ trả **HÀNG bảng + nguồn `ole:<handle>:<sheet>`**, máy **KHÔNG tự chọn ô TỔNG / KHÔNG tự cộng** (chống overfit+bịa); `_canh_bao_nhung` tách đọc-được/ảnh; trần RAM **150k ô**.

**Kết quả test:** `test_oleexcel.py` **18/18** + ole-cảnh-báo 51; check.sh **[22/22]→[23/23] PASS** · takeoff 258 · qa 129 · **0-OLE không đổi · 0 regress**. Fixture THEP_OLE ở `tests/corpus_local` (gitignored). Checklist cập nhật 27 tool. Memory design lưu `[[project-doi-sanh-kien-truc]]`.

**⏳ CHƯA (v2):** OCR fallback tầng 2 cho **~11% OLE dạng ẢNH thật** (StaticDib/PBrush/EMF); **diễn giải bảng thép → tổng kg** (overfit — CHẶN tới khi có corpus ≥3 firm / P5).

**Đang chờ / bước tiếp:** U-series còn **U1**(P5 codify) · **U2**(zone index) · **U4**(gói SME test) · **U5**(đối chiếu bóc tay) · **U6**(RAM iterdxf stream) + nhóm **I1-I9**. **id135 E2E-thật** chờ file hạ tầng mốc sâu thật. **F-B** (P3 vào web) chờ user quyết. **HELD RAM** push khi bật billing Render.

---
## Session 2026-07-22 (CHỐT SỔ) — AUDIT phiên GĐ4 (34-agent) + vá bó F1/F2/F3/F4 — ✅ LIVE `fd7019d`
> **CHỐT SỔ:** check.sh **[22/22] PASS** · takeoff 258 · qa 129 · cao_do **31** · OLE **44** · working tree TRACKED sạch, push hết, **HEAD LIVE `fd7019d`** (`/version` khớp + `/health` ok). Ẩn danh SẠCH (0 tên địa danh/người; đã vá 1 rò tên-địa-danh→bí-danh `CT-A` do chính tôi lỡ viết ở entry F1). 3 mục "còn lại" (OLE-block/RAM/P5) trỏ sang **U3/U6/U1** trong `PHUONG_AN_NANG_CAP_DU_AN.md`. KHÔNG pytest. feature_list: 29 done / 1 deferred (không đổi — phiên chỉ audit+hardening). Commit code: `85d8a50` (F1+F4) · `fd7019d` (F2+F3).

**User yêu cầu:** rà soát tester chuyên nghiệp mọi thay đổi phiên GĐ4 TRƯỚC khi đi tiếp, rồi triển khai bó vá (red-team F4 trước khi code).

**AUDIT (workflow 34-agent: 6 mảng review → skeptic-verify từng finding → synth):** 23 CONFIRMED/1 xác-minh-dương · 4 BÁC BỎ · **0 bug lớp nghiêm trọng** (không đổi số/crash/mất code). Git toàn vẹn sau rebase+filter-repo+restore (5/5 CONFIRMED tốt: main có đủ fix, .deb tracked, Dockerfile private, public-ready sạch, origin==local). id135 an toàn. Tôi TỰ kiểm chứng lại 2 finding chính (không tin judge mù) → cả 2 CONFIRM.
- **F1 (TB) — cảnh báo OLE cắm THIẾU chỗ:** `tra_cuu_so_luong`/`liet_ke_so_luong`/`thong_tin_kich_thuoc` trả kết-quả-âm trên file 8-OLE mà KHÔNG mang `canh_bao_nhung` = đúng failure mode rule 8c định chống, tôi chỉ cắm ở tuyến thép.
- **F4 (tiền đề SAI) — `_CD_INL` bỏ `\s*`:** comment "cao độ luôn dính liền" bị corpus bác — có mốc THẬT dạng cách `'cốt + 7.690'`,`'+ 8.500'`,`'± 0.000'`,`'CÈT + 9.800'`; fix cũ bỏ hết (min/max chưa đổi nhưng cơ chế sai trục + latent id135-loss).
- **D6 — tôi tự rút lại claim RAM:** "45MB×11.3=577MB→OOM" SAI (11.3x đo ở file 26.5MB, không phải ≤45MB = ngoại suy sai). Rủi ro OOM thật ở cơ chế khác: bỏ quên `MAX_SESSIONS=4`.

**VÁ (gate [22/22] · takeoff 258 · qa 129 · cao_do 27→31 · ole 25→37 · 0 regress):**
- **F1:** `_gan_canh_bao_nhung` cắm vào 3 tuyến CHỈ KHI kết quả RỖNG (gate-on-empty chống nhiễu: file OLE-khung-tên vẫn tra thấy số → KHÔNG cảnh báo). Verify: CT-A KT 2-OLE tra thấy 38 mục → không cảnh báo.
- **F4 (RED-TEAM TRƯỚC KHI CODE, workflow 4-agent → GO_WITH_ADJUSTMENTS):** red-team BÁC thiết kế blacklist-nhãn của tôi (vỡ garble 2 chiều) VÀ Design-B chỉ-+/± (drop id135 `cốt - 14.260`). **Thiết kế CHỐT:** `_CD_INL` khôi phục `\s*` (nhóm gap) → `+`/`±` mọi gap + `-` dính liền → min/max; **`-` DẤU CÁCH ('WORD - n.nnn', đồng dạng FP `CH-2.700` VÀ id135 `cốt-14.260`, KHÔNG tách được hình thức, nhãn vỡ garble) → đẩy `canh_bao` (LỘ, không bịa min, miễn nhiễm garble)**. Verify engine thật: id135 dạng cách → canh_bao; FP CH → canh_bao (min giữ -1.6); thu lại `+7.69/+8.5/+9.8`; standalone/dính-liền vẫn min/max; **số verify GIỮ NGUYÊN** (KC -1.85, KT -2.1, 9T -1.6). + prompt rule 8: hỏi độ sâu mà canh_bao có marker-âm-cách → PHẢI nêu "cần đối chiếu tay".
- **Test (D5):** thêm ca motivating synthetic (bảng thép TRONG OLE → co_bang=False + cảnh báo, KHÔNG cần corpus) + test khoá id135 `cốt - 14.260` phải trong canh_bao (yêu cầu red-team).
- **F2/F3 hardening nhẹ [tiếp theo, gate 22/22 · ole 37→44]:** **F2** — helper `_ole_ngoai_modelspace` quét thêm OLE ở **paperspace** (layout in ấn), trước chỉ modelspace nên bảng nhúng ở layout bị bỏ sót; fail-soft từng layout; testable (fake doc). Corpus xác nhận **0 paperspace-OLE** (108 modelspace) → hardening thuần, số OLE không đổi (KT=2, KC=0). ⚠ CÒN LATENT: OLE lồng trong định-nghĩa-BLOCK (ezdxf không mở INSERT) — chưa quét vì rủi ro đếm nhầm khung-tên/thư-viện. **F3** — nhánh `thong_ke_thep` `co_trong_bang=False` (hỏi cỡ dk vắng) nay cũng bọc `_gan_canh_bao_nhung` (nhất quán, additive). Test [F2][F3] +7 ca.

---
## Session 2026-07-17 — GĐ4 ĐA-DOMAIN (corpus 8 firm VỀ): vá OLE + 3 bug red-team + BÁC BỎ 2 "bug" tự nghĩ ra — ✅ LIVE `7188c3c`
> **✅ COMMIT `7188c3c` + REBASE đảo thứ tự + PUSH + DEPLOY + VERIFY LIVE** (`/version`=7188c3c khớp + `/health` ok=true). HELD (render.yaml nâng RAM) đảo lên TRÊN, **hash mới `f025ad7`** (cũ `969822a`), vẫn CỐ Ý chưa push. Backup: `backup-truoc-rebase-20260717`. Commit fix KHÔNG chạm render.yaml → deploy giữ `plan: free`, không dính billing.
**Corpus ĐÃ VỀ** `input_files\` (8 công trình mới, 62 dwg/168MB, không nén) → **66 file / 10 nhóm**. Chạy `tests/khao_sat_corpus.py` (~45'/lượt; 1 file ODA không convert nổi: ĐIỆN CT-E). **NÚT THẮT ≥3 FIRM MỞ.**

**Kết quả GĐ4 (quan trọng nhất: LÕI KHÔNG OVERFIT):** bộ đọc số lượng ăn **9/10 nhóm** (qty 1617). `qty=0` chủ yếu điện/nước/TMB/phá-dỡ = vô hại. Bộ đọc bảng-TK chỉ ăn 2/10 nhóm.

**✅ VÁ BUG C — OLE2FRAME (bảng Excel nhúng) [gate 22/22]:** GĐ4 đo **19/65 file có OLE** (THPT KC có 67 khung!). Ca nặng `4. Thong ke thep SUA.dwg` (CT-D, DXF 67.9MB nhưng msp chỉ 27 entity): cả bảng thép nằm trong 8 OLE → engine đọc 0 và trả *"bản vẽ KHÔNG có bảng thống kê thép"* trên file TÊN LÀ "thống kê thép" ⇒ đối tác hiểu SAI. **Vá = CHỈ LỘ, KHÔNG đổi số:** `tools_core` gom `self.ole_nhung` (handle+layer) + `_canh_bao_nhung()`/`_gan_canh_bao_nhung()` (ADDITIVE) cắm vào `thong_ke_thep` (cả 3 nhánh) · `thong_ke_thep_hinh` · `tong_hop_khoi_luong` (nguồn Excel bàn giao) + SYSTEM_PROMPT **rule 8c** (cấm nói "bản vẽ không có"/"0 kg" khi có `canh_bao_nhung`). Verify engine thật: file 8-OLE lộ cảnh báo; CT-A KC (0 OLE) **số y nguyên 67370.7**, không cảnh báo oan. Test `test_ole_canh_bao.py` **25 ca** → check.sh **[21/21]→[22/22]** · takeoff 258 · qa 129 · 0 regress.

**❌ TỰ BÁC BỎ "BUG B" (text trong block không đọc):** tưởng lỗ recall (file thép đọc 17/1095 text). Kiểm chứng: text trong block là **KHUNG TÊN** (`'công trình:'`, `'ks. [tên đã ẩn]'`) + block thư viện không dùng ⇒ bỏ qua là **TÍNH NĂNG**. Dấu hiệu lẽ ra phải thấy sớm: heuristic của tôi gắn cờ cả **CT-A** — file mà 129 test QA xác thực đọc ĐÚNG. Nội dung thật của file thép nằm ở OLE (bug C), không ở block.

**❌ TỰ BÁC BỎ "BUG A" (cao độ -22.75 'lệch 21m') — TOOL ĐANG TRẢ ĐÚNG, SUÝT VÁ HỎNG:** tôi cáo buộc `-22.75` là text rác (vì "mầm non 3 tầng không thể sâu 22m"). **Red-team (1 agent, tự chạy engine) + tôi tự kiểm chứng BÁC BỎ:** file ghi `'GIẢI PHÁP KẾT CẤU MÓNG: MÓNG CỌC BTCT'` + `'TCVN 10304:2014'` + `'SỐ LƯỢNG CỌC ĐẠI TRÀ: 157'`, có nhãn `'ĐẦU CỌC'` cách 412 đv, sơ đồ cọc **tỷ lệ 1:1 khớp 0.996**, marker lặp **2 lần** (tôi báo nhầm "1 lần"). ⇒ **-22.75 = MŨI CỌC THẬT, -1.85 = ĐÁY ĐÀI** — 2 đại lượng khác nhau. **Rủi ro THẬT = hợp đồng ngữ nghĩa:** prompt hứa "đáy móng" mà tool trả min mọi marker → lệch 21m trên bản vẽ móng cọc. **Vá MÔ TẢ, không vá số** (rule 8 bỏ "đáy móng" + dặn HỎI LẠI; `ghi_chu` cảnh báo mũi-cọc≠đáy-đài). Test `[COC]` 3 ca khoá cả 2 chiều (không được lọc mốc sâu + phải cảnh báo) → cao_do 12→**15**.

**⛔ RED-TEAM CHẶN `thap_nhat_dang_tin` (thiết kế tôi định làm) — NO_GO có bằng chứng:** tiêm mốc id135 `-14.26` vào phân bố THẬT của **7/7 file kết cấu** → `_nghi()` cờ cả 7, `dang_tin` trả số **nông hơn 11.26–13.23m** = đúng con số sai id135, đóng nhãn "đáng tin" ⇒ **TÁI SINH id135**. Trường này là *phán quyết* đội lốt *dữ liệu*. BỎ HẲN.

**✅ VÁ 3 BUG RED-TEAM [gate 22/22 · cao_do 12→27 · takeoff 258 · qa 129 · 0 regress]:** (a) **G3 fallback** `pool = ... or found` → bỏ hẳn; mọi marker ở layer thép ⇒ `co_cao_do=False` + thép vẫn LỘ ở `canh_bao` (hết cảnh "-44.1 vừa là đáp án vừa bị ghi 'đã loại'"). (b) **`_nghi()` toán sai** → `med` nay tính trên gap GIỮA CÁC MỐC KHÁC (loại chính điểm xét) nên outlier hết tự thổi ngưỡng; thêm `_median` THẬT thay median-TRÊN. Repro trước/sau: `0/-22.75` False→**True**; `0/-0.05/-22.75` thoát→**cờ**; bớt 1 marker vô can hết LẬT cờ; 1 giá trị → không cờ. (c) **`_CD_INL`** bỏ `\s*` → `'CH - 2.700'` (CHIỀU CAO 2.7m, 9T KT, 1 lần, layer 'Net Text') hết thành cao độ -2.7. **An toàn id135:** lọc theo HÌNH THỨC KÝ HIỆU (dấu dính liền), KHÔNG theo tần suất/cô lập; test khoá inline `-2.700`/`-14.26` dính liền VẪN đọc được. **Verify corpus thật:** mọi số đã verify GIỮ NGUYÊN (CT-A KC -1.85/FEF03 · KT -2.1/A51A7 · 9T KC -3.0 · CT-C -22.75 vẫn trả + nghi=True); chỉ 9T KT -2.7→**-1.6** đúng chủ đích (marker 689→688). Test `[F1][F2][F3]` 12 ca.

**Bài học:** **2 lần tôi tự nghĩ ra bug từ suy đoán cảm tính rồi suýt vá hỏng** (block-text; -22.75 móng cọc). Cả 2 lần cứu bởi ĐỌC DỮ LIỆU THẬT + red-team. Dấu hiệu vàng: **khi phép đo bắt lỗi cả thứ ĐÃ BIẾT là đúng (CT-A/129 test) thì phép đo sai, không phải đối tượng.** Red-team-trước-code (quy ước dự án) lần này chặn được một fix sẽ tái sinh chính bug nó định vá.

---
## Session 2026-07-16 (nối) — CÔNG CỤ KHẢO SÁT CORPUS + ĐÍNH CHÍNH hệ số RAM (⚠ CHƯA COMMIT)
**Bối cảnh:** đối tác gửi 7 thư mục bản vẽ qua Zalo (ảnh chụp điện thoại). **TÌM KỸ TRÊN MÁY → KHÔNG CÓ FILE NÀO.**
Đã quét: `input_files/` (chỉ corpus CŨ 2 firm) · Downloads/Documents/Desktop · `Documents\Zalo Received Files` (chỉ file học 2025) · `D:\Zalo Data\...\ZaloDownloads\file` (chỉ cache/DB Zalo) · TOÀN ổ D: mọi `.dwg/.dxf` sửa sau 2026-07-10 = **0 file** · toàn D: file >5MB sau 2026-07-14 = chỉ DB Zalo · C: quét tên đặc trưng = 0 hit · chỉ có ổ C:/D:. ⇒ File còn ở ĐIỆN THOẠI, chưa chép về PC. Đã báo user danh sách cần chép vào `input_files\`.

**Đã làm (user chốt: dựng sẵn công cụ trong lúc chờ file):** `tests/khao_sat_corpus.py` — quét đệ quy corpus, convert `.dwg→.dxf` qua ODA (có CACHE, khỏi convert lại 600s), đo RAM/kích thước, đếm layer/text/block/dim/sheet + **qty THEO NGUỒN** (bảng-thống-kê vs inline vs spatial = tín hiệu overfit đa-firm), `cao_do_min_max` từng file (tìm ứng viên id135), `so_residual` (gap recall). Nhóm theo THƯ MỤC GỐC.
- **Thiết kế:** mỗi file 1 **SUBPROCESS** — (a) đỉnh RSS là monotonic, nạp nhiều file 1 tiến trình thì số đo per-file SAI; (b) file lớn/hỏng OOM/treo không giết cả phiên (timeout + fail-soft, lỗi LỘ + đếm).
- **Ethos:** thất-bại-phải-lộ (file lỗi/timeout/thiếu-ODA liệt kê riêng, in TRƯỚC) · không-bịa (nhóm = THƯ MỤC, KHÔNG suy ra "đơn vị thiết kế" — người xác nhận) · read-only với `--root` (dxf ghi ra `_khao_sat/`).

**3 BUG TỰ BẮT khi chạy thật (đều tái hiện trước khi vá):**
- **Đo RAM im lặng hỏng:** `_peak_rss_mb` trả None (báo `RAM=None`). Gốc: thiếu `argtypes/restype` → ctypes coi `GetCurrentProcess()` là int 32-bit, pseudo-handle `(HANDLE)-1` bị CẮT khi vào tham số HANDLE 64-bit → API trả 0. Vá + khoá test `[B]`.
- **Chính công cụ đo làm hỏng số đo:** bật `tracemalloc` thổi RSS **~2.1x** (ĐO: cùng file tắt=241MB/6.9x · bật=510MB/17.6x) → báo cáo sẽ khiến **mua thừa RAM ~2.5x**. Vá: tracemalloc MẶC ĐỊNH TẮT, thành cờ opt-in có cảnh báo. Khoá test `[D]`.
- **Hệ số rác ở file nhỏ:** DXF 0.02MB → in "75x" (baseline lấn át). Vá: `MIN_MB_HE_SO=5.0`, dưới ngưỡng KHÔNG ngoại suy mà NÓI THIẾU. Khoá test `[K2]`.
- **(+ .gitignore)** `_khao_sat/ # comment` KHÔNG ăn — .gitignore không có comment cuối dòng → 276MB DXF suýt vào repo. Vá: comment ra dòng riêng, verify `git check-ignore`.

**⚠ ĐÍNH CHÍNH LOAD-BEARING — hệ số RAM (ảnh hưởng quyết định TIỀN):** memory/render.yaml ghi **5.8x** nhưng đó là số **tracemalloc = Python-heap**; Render chặn theo **RSS**. Mô hình đúng (đo 4 file thật): **RSS ≈ 68MB baseline + 6.9–8.1x × DXF** (CT-A KT 25.2→241MB/6.9x · KC 23.3→256MB · 9T KT 112.2→902MB/7.4x · 9T KC 114.4→934MB/8.1x). ⇒ ngưỡng theo 5.8x **hụt 25-40%**: với 2GB biên 0.7 → an toàn ~**170MB**, KHÔNG phải 200MB như commit HELD `969822a`. **Thêm:** `MAX_SESSIONS=4` × 1 Drawing/subprocess ⇒ RAM tệ nhất ≈ 4×(68+k×size), không phải 1×. **CHƯA đối chiếu Linux** (đo trên Windows) → phải chạy lại trên Render trước khi chốt gói. Đã cập nhật memory [[project-chiu-tai-va-chi-phi]].

**Kết quả test:** `tests/test_khao_sat_corpus.py` **61 ca** (helper/nhóm · đo RAM thật · tracemalloc-tắt · baseline+delta · DXF hỏng LỘ lỗi · thiếu ODA LỘ lỗi · parent fail-soft subprocess thật · ngưỡng Render · tổng-hợp tách file lỗi · KHÔNG mutate corpus gốc · JSON · root sai exit 1 · chặn hệ-số-rác) — KHÔNG cần corpus thật (DXF tổng hợp). check.sh **[20/20]→[21/21] PASS** · takeoff **258** · qa **129** · **0 regress**. Chạy thật corpus cũ: 4 file/2 nhóm, số khớp giá trị đã verify (CT-A KC min=-1.85/FEF03 · KT -2.1/A51A7 · 9T KC -3.0 · 9T KT có BẢNG-TK).

**Đang chờ / bước tiếp:** **user chép 7 thư mục vào `input_files\`** → chạy `python tests/khao_sat_corpus.py` là ra hồ sơ ngay → mở GĐ4/P5/id135-E2E. **CHƯA COMMIT** (HEAD đang là commit HELD `969822a` — commit chồng lên rồi push sẽ đẩy luôn config RAM đang cố ý giữ; chờ user chốt cách tách). **Xem lại ngưỡng 200→~170** trong render.yaml HELD trước khi push.

---
## Session 2026-07-16 (CHỐT SỔ) — 4 FIX ĐỌC-SỐ LIVE + quyết định RAM/chi-phí + hướng corpus/remote
> ⚠ Đính chính ngày: các entry "(nối 5-8)" bên dưới THỰC TẾ làm **2026-07-16** (ghi nhầm 2026-07-13 theo header phiên trước). Commit git có timestamp thật.

**Đã làm (4 fix code + docs, TẤT CẢ deploy+verify LIVE):**
- **id84** `c0b85af` — đài cọc `tong_so_luong('ĐC')` 142→59 (unaccent gộp đ→d nên ĐC≡DC; vá label_ma=_norm_ma + dedup _ma_key). Chọn qua workflow (research repro + decision matrix + vet overfit).
- **id135 grounding-guard** `3ca5102` — chống bịa số đo-lường không nguồn (KHÔNG dùng n_evidence=0 vì 60/198 câu đúng có n_ev=0 → sập recall 30%; dùng grounding: số answer truy được về số RAW-result tool). Vet chạy 198 câu → FP=0. + luật SYSTEM_PROMPT.
- **dầm double-count** `95f4282` (residual id84) — 'DẦM DR-6'+'DR-6'=cùng 1 dầm nhưng không dedup → over-count 2x (DM 40→20); vá dedup CÓ-LOẠI _ma_type/_ma_code/_ma_group_key (giữ 'DẦM D1'≠'CỬA D1'). Phát hiện qua workflow re-hunt.
- **cao_do_min_max** `97ffc60` — MCP tool #26 (id135-recall): đọc RAW min/max cao độ KHÔNG lọc ≥4 như _build_levels. G1 dấu/G3 layer-thép/G4-5 nghi_ngo. CT-A KC -1.85/+10.8; 9T KC -3.0 (loại -44.1 thép).

**Kết quả test (CHỐT SỔ, 0 FAIL):** `check.sh` **HARNESS GATE PASS [20/20]** (26 MCP tool · takeoff **258** · qa 129 · grounding-guard 32 · cao_do 12 · fallback 22 · session 25 · +…) · working tree TRACKED sạch. **KHÔNG pytest** (crash I/O closed file — dùng script-runner + check.sh). feature_list: **29 done / 1 deferred** (+cao_do vào floor-levels).

**Quyết định dài hạn (đã lưu memory [[project-chiu-tai-va-chi-phi]]):**
- **Chịu tải file lớn = ràng buộc RAM cloud, KHÔNG phải logic.** ĐO THẬT: DXF/RAM ~5.8x → 512MB→45MB, 2GB→200MB. Render Free hiện chỉ đọc ≤45MB.
- **Chiến lược chống lỗ:** trả tiền nâng RAM ở **BƯỚC CUỐI** (sau khi chốt deal); dev/validate = đọc file **LOCAL free**. Render cost ≠ Gemini API key (2 hoá đơn riêng).
- **Config nâng RAM sẵn** `079c91c` (plan standard 2GB + READFILE 200 + UPLOAD 220) — **GIỮ CHƯA PUSH**, chờ user bật billing Render.
- **Remote-work (điện thoại):** độ tin từ quy trình kiểm được (git commit + test gate + LIVE verify) reviewable trên GitHub — không cần đọc lại chat.

**Đang chờ / bước tiếp:**
- **Corpus ≥3 firm (nút thắt chính):** user xin đối tác 3–5 bản vẽ (.dwg/.dxf, nhiều nguồn, có bảng thống kê) → mở khoá GĐ4/P5/id135-E2E + lộ nốt lỗi biên ẩn. Tôi soi từng file khi có.
- **Nâng RAM Render:** khi user bật billing → push `079c91c` + verify.
- **F-B** (nối kênh học P3 vào web) — user quyết web-UI vs MCP-only.
- **Dự toán chi phí** — HOÃN.

---
## Session 2026-07-13 (nối 8) — THÊM cao_do_min_max (recall id135) — ✅ LIVE `97ffc60`
**Mục tiêu:** user "làm tiếp cao_do_min_max". Thiết kế đã vet ở phiên nối 7 (workflow design cao_do + red-team, GO_WITH_ADJUSTMENTS).

**Đã làm (implement từ design đã vet):** MCP tool #26 `cao_do_min_max` (recall id135 — đọc ĐÚNG cao độ thấp/cao nhất, bù cho guard chỉ chặn bịa).
- `tools_core.py`: `_CD_STD`/`_CD_INL` (dấu +/-/± + 1-3 nguyên + **2-3 thập phân**) + `_cd_val` + method `Drawing.cao_do_min_max`. Đọc RAW marker, min/max — **KHÔNG lọc ≥4/cluster** (lý do id135 miss). RIÊNG khỏi thong_tin_tang (giữ cho chiều-cao-tầng).
- Precision: G1 bắt buộc dấu; G3 loại layer THÉP (`thep|sothep|rebar`) khỏi min/max → LỘ ở canh_bao; G4/G5 flag nghi_ngo (extreme cô lập/inline, chỉ FLAG). Trả handle+nguyên_văn (grounded → guard giữ).
- `mcp_server.py`: @mcp.tool. `mcp_bridge.py` SYSTEM_PROMPT rule 8: 'cao độ thấp/sâu/cao nhất' → cao_do_min_max, trích thap_nhat/cao_nhat, ĐỪNG lấy canh_bao (bù điểm yếu guard không phân biệt giá-trị-đã-loại trong raw).

**Verify engine THẬT:** CT-A KC min=**-1.85**(FEF03)/max=**+10.8**(11FA7D); KT -2.1(A51A7)/+10.8(40ABE); 9T KC min=**-3.0** (loại -44.1 thép qua G3)/max=+33.7 (18 canh_bao thép); demo cửa co_cao_do=false. id135 shape '-14.26' (2 thập phân) → đọc đúng.

**Kết quả test:** `test_cao_do_min_max.py` **12 ca** (4 real+handle · G1/G3/G4-5 synthetic · -14.26 · guard-interaction) → check.sh **[19/19]→[20/20]** (26 MCP tool) · takeoff 258 · qa 129 · MCP-stdio 14 · 0 regress. **⚠ GIỚI HẠN overfit:** 2 firm, chưa có file hạ tầng/cầu-đường (ly trình K0+500 có thể FP) → cần ≥3 firm. **✅ COMMIT `97ffc60` + push + deploy + verify LIVE** (`/version`=97ffc60 khớp + `/health` ok).

**Đang chờ / bước tiếp:** **id135 E2E-thật** (chờ file hạ tầng + API). **F-B** user quyết. **GĐ4/P5** chặn corpus ≥3 firm (giờ là nút thắt chính — nhiều finding chờ verify đa-firm).

---
## Session 2026-07-13 (nối 7) — VÁ DẦM DOUBLE-COUNT (over-count ~2×, residual id84) — ✅ LIVE `95f4282`
**Mục tiêu:** user "nghiên cứu đầu mục tối ưu rồi làm". Workflow (design cao_do_min_max + RE-HUNT battery in-corpus) → **đổi khuyến nghị**: re-hunt (2 agent, engine-verified) tìm bug OUTRANK cao_do.

**BUG (mới, DA REPRO engine thật, in-corpus):** `tong_so_luong('DM')` trên CT-A KC = **40** nhưng đúng **20** (mỗi dầm đếm 2 lần: 'DẦM DM-1 (SL=02)' + 'DM-1'); DR/D2=40 (đúng 30); DC=34 (đúng 16). **Over-count ~2×** = sai-tự-tin (đặt thừa vật tư), nguy hiểm hơn recall-miss của cao_do (đã có guard chống bịa) → outrank. **Là RESIDUAL id84:** `_ma_key` bảo thủ (giữ cả nhãn để 'DẦM D1'≠'CỬA D1') vô tình KHÔNG gộp 'DẦM DR-6' (inline, có tiền tố loại) với 'DR-6' (spatial trần) = cùng 1 dầm. Đài id84 hết trùng vì 2 bản đều trần; dầm lọt vì inline có 'DẦM'.

**Vá CẤU TRÚC — dedup CÓ-LOẠI** (`tools_core.py`): `_ma_type` (tiền-tố-loại dẫn đầu), `_ma_code` (mã sau khi bỏ loại), `_types_of` (mã→tập loại), `_ma_group_key` (mã,loại). Bare-code GỘP vào loại DUY NHẤT của mã ('DR-6'→'DẦM DR-6'); mã ≥2 loại ('DẦM D1'+'CỬA D1') hoặc 0 loại → bare RIÊNG. Áp cả 3 site dedup (tra_so_luong:1173, tong_so_luong:1252, tong_hop_khoi_luong:2241). Giữ `_ma_key` làm helper tokenize.

**Kết quả (0 FAIL):** DM/DR/D2/DC = 20/30/30/16 · **id84 ĐC vẫn 59/6** · door D1 giữ ([E] 84.24 ổn định) · 'DẦM D1'≠'CỬA D1' · **KHÔI PHỤC DC=16 + cảnh báo SL-lệch DCN 6-vs-8** (key bảo thủ đã mất). Test **[id84]+6 dầm** → takeoff **252→258** · check.sh **[19/19] PASS** (excel-content 17, misc-tools 84 không regress) · qa **129**. **✅ COMMIT `95f4282` + push + deploy + verify LIVE** (`/version`=95f4282 khớp + `/health` ok).

**Đang chờ / bước tiếp:** **cao_do_min_max** (recall id135, thiết kế đã vet đầy đủ ở workflow phiên này — regex marker 2-3 thập phân, guard layer-thép G3, RIÊNG khỏi thong_tin_tang; verify CT-A KC min=-1.85/max=+10.8) — làm TIẾP. **F-B** user quyết. **GĐ4/P5** chặn corpus ≥3 firm.

---
## Session 2026-07-13 (nối 6) — VÁ id135 REFUSE-GUARD (grounding, an toàn recall) — ✅ LIVE `3ca5102`
**Mục tiêu:** user "vá tiếp id135 với refuse-guard khi n_evidence=0", rồi delegate "nghiên cứu chi tiết + chọn phương án tối ưu".

**PHÁT HIỆN then chốt (probe battery THẬT trước khi thiết kế):** `n_evidence=0` KHÔNG phải tín hiệu bịa — **60/198 câu (30%) có n_ev=0 + có số + ĐÚNG** (id1 '8024 đối tượng', id2 '141 layer', id16 '15/58800mm', id17 '298.4 kg') vì tool trả số tổng-hợp (đếm/bảng thép/min-max/mốc cao độ) KHÔNG gắn handle per-item. Guard `n_evidence=0 → từ chối` thô sẽ **SẬP recall 30%** (recall là điểm yếu THẬT của demo). → hỏi user, user delegate.

**Thiết kế qua workflow (design + false-positive-hunt battery + effectiveness/test + synthesize + vet):**
- Tín hiệu ĐÚNG = **GROUNDING**: số ĐO-LƯỜNG trong answer có truy được về số nào tool ĐÃ trả trong RAW result không (KHÔNG phải theo handle/evidence). id135 '-10m': −10 vắng khỏi mọi result → bịa; id1 '8024': tool đếm trả 8024 → grounded.
- **2 lớp** (`mcp_bridge.py`): (L2) `_guard_text`: gom `tool_numbers` từ mọi RAW result (`_collect_numbers` walk dict/list + regex số trong chuỗi, siêu-tập để rộng tay); `_answer_numbers` trích số ĐO-LƯỜNG của answer (có đơn vị m/mm/kg/m2/% hoặc thập phân) — MIỄN số đếm trơn + mã-hiệu (B20/M14/Ø22/1÷200/AxB/handle); `_is_grounded` khớp ×1000/÷1000 + sai số 1%, CÓ DẤU; CHỈ từ chối khi MỌI số (đo-lường lẫn đếm) đều ungrounded (neo=tất-cả-số → chống nuke câu đúng có phần đếm grounded). (L1) luật SYSTEM_PROMPT cao độ/chiều sâu.
- Hook tại 2 return-có-text-model (dòng ~419, ~436); KHÔNG đụng return thông-báo-hệ-thống.

**Vet red-team (GO_WITH_ADJUSTMENTS) — đã CHẠY `_answer_numbers` trên cả 198 câu battery → FP=0** (0 câu đúng bị từ chối nhầm; mọi số đo-lường của 60 câu n_ev=0 đều truy được về nguồn tool THẬT). Đã tiếp thu 2 adjustment: (1) neo grounding dùng TẤT-CẢ-số (kể cả đếm grounded) chống nuke câu 'id91-shape'; (2) xác nhận chiều-cao-tầng derived grounded vì `thong_tin_tang` trả `typical_floor_h` trong result (concern #2 tự tan). L1 prompt là BẮT BUỘC (guard hẹp, chỉ bắt số âm/ngoài-dải như -10).

**⚠ GIỚI HẠN E2E (trung thực):** KHÔNG chạy được câu id135 THẬT — file hạ tầng KHÔNG có trong corpus + cần API. Xác minh bằng **mock-E2E qua `tra_loi_ai` (đúng code path) + unit + phân tích battery**, KHÔNG phải E2E-thật. Rủi ro deploy thấp vì thứ verify = AN-TOÀN-RECALL (câu đúng được bảo vệ, FP=0); worst-case guard vô hiệu → id135 không tệ hơn cũ.

**Kết quả test:** `test_grounding_guard.py` **32/32** (8 unit trích-số/grounding + mock BAN id135 + GIỮ đếm/thép/đổi-đơn-vị/any-grounded/từ-chối-sẵn). check.sh **[18/18]→[19/19] PASS** · takeoff **252** · qa **129** · 0 regress. **✅ COMMIT `3ca5102` + push + deploy + verify LIVE** (`/version`=3ca5102 khớp + `/health` ok).

**Đang chờ / bước tiếp:** **id135 RECALL** — thêm recall-tool `cao_do_min_max` (đọc TEXT cao độ min/max kèm handle) để trả ĐÚNG -14.26 (guard chỉ chặn bịa, không giúp đọc đúng) — làm khi có file hạ tầng verify. **F-B** user quyết. **GĐ4/P5** chặn corpus ≥3 firm.

---
## Session 2026-07-13 (nối 5) — VÁ FINDING id84 (đài cọc 142→59) — ✅ LIVE `c0b85af`
**Mục tiêu:** user "nghiên cứu đầu mục nào tiếp theo hợp lý/đúng logic nhất → triển khai". Chọn qua workflow đa-agent, KHÔNG tự ý làm đầu mục cần quyết-định-user hay corpus ngoài.

**Chọn đầu mục (workflow: research 3-agent song song → synthesize → vet overfit):**
- Xếp hạng: **id84 > id135 > F-B > GĐ4 > P5 > dự toán**. Chọn **id84** — DUY NHẤT vừa UNBLOCKED vừa REPRO được engine thật (file `2. KetCau CT-A.dxf` CÓ trong corpus). Loại: **id135** BLOCKED (file 'hạ tầng' -14.26 KHÔNG có trong `_dxf` → không verify → vi phạm 'phải có bằng chứng engine thật'); **F-B** cần user quyết (fork web-UI vs MCP-only); **GĐ4/P5** chặn corpus ≥3 firm; **dự toán** HOÃN. id84 là lỗi SAI-TỰ-TIN (lớp tệ nhất theo ethos anti-bịa>phủ).

**Đã làm (probe → design → implement → vá regress → test):**
- **REPRO offline:** `tong_so_luong(loc='ĐC')` = **142** (đúng 59); query 'ĐC' và 'DC' cho kết quả GIỐNG HỆT (bằng chứng đ/d fold). Danh sách gộp DẦM (DCN/DCTH/DCT) + đếm trùng inline/spatial (ĐC-3=25+25).
- **4 ROOT-CAUSE** (`tools_core.py`): RC1 `unaccent` gộp đ→d (:45) → 'ĐC'≡'DC' ở khớp; RC2 `_tok_bound` token chữ=substring (:574); RC3 dedup `(label_norm,so_luong)` không gộp inline vs spatial; RC4 `tong_so_luong` `cs[-1]` nhặt nhầm 'sl-25'.
- **VÁ CẤU TRÚC** (tận dụng tiền lệ `_norm_ma` F3, KHÔNG hardcode 'ĐC'/'DCN'): (a) field `label_ma`=`_norm_ma(nhãn)` + khớp qty trên đó ('ĐC'→'djc'≠'DC'→'dc'); (b) helper `_ma_key` BẢO THỦ (bỏ annotation → so NHÃN đầy đủ) gộp inline/spatial cùng nhãn NHƯNG KHÔNG over-merge 'DẦM D1'≠'CỬA D1'; (c) xung đột SL 2 nguồn → chọn inline + LỘ `canh_bao`+⚠ (wire ra tra_cuu/liet_ke/tong_so_luong), KHÔNG cộng dồn. Áp `_ma_key` cả `tong_hop_khoi_luong` (Excel hết 'ĐC-3' 2 dòng).
- **VET OVERFIT (adversarial, TRƯỚC code) bắt 3 lỗi:** ① TYPE_WORDS chưa qua _norm_ma ('đài'→'djai') → nếu dùng first-token key thì 'ĐÀI CỌC ĐC-1' cho ma_key='djai' gộp mọi đài → **đổi sang key BẢO THỦ (so nhãn) né hẳn**; ② fail-loud chỉ ở entry nội bộ → **wire ra output**; ③ claim 'mã không-đ 0 đổi' sai ở tầng dedup → **thêm positive-control**. Verdict GO_WITH_ADJUSTMENTS.
- **VÁ REGRESS [E]:** lần đầu dùng key strip-type-word → over-merge 'DẦM D1'(dầm)+'CỬA D1'(cửa) → test [E] (4 biến thể 'diện tích cửa D1' → 1 giá trị) VỠ (3.51 vs 84.24). Đổi sang `_ma_key` bảo thủ (chỉ bỏ annotation) → door/beam TÁCH lại → [E] ổn định 84.24. (Bài học: dedup đụng mọi consumer; type-word là DISCRIMINATOR khi mã trần trùng.)

**Kết quả test (0 FAIL):** `tong_so_luong('ĐC')` **142→59**/6 mã, chỉ đài cọc · DC(dầm) chỉ dầm · door/beam D1 giữ nguyên. Test **[id84] 12 ca** → `test_takeoff_chong_bia.py` **252/252** · `check.sh` **[18/18] PASS** (excel-content 17, misc-tools 84 không regress) · `test_qa_data.py` **129/129**. **✅ COMMIT `c0b85af` + push + deploy + verify LIVE** (`/version`=c0b85af khớp + `/health` ok).

**Đang chờ:** **id135** vá khi có file hạ tầng (refuse-guard + recall cao-độ-text). **F-B** user quyết (nối UI web cho kênh học P3 hay MCP-only). **GĐ4/P5** chặn corpus ≥3 firm. Dự toán chi phí HOÃN.

---
## Session 2026-07-13 (CHỐT SỔ) — P3+P4 AI tự học LIVE + KIỂM THỬ TỔNG THỂ GĐ0-3 (5 commit code, 3 bug vá, đều LIVE)
**Tóm tắt phiên (DÀI):** hoàn tất vòng AI tự học (P-1.1+P3+P4) rồi đóng vai TESTER rà toàn dự án (GĐ0-3). Chi tiết từng phần ở các entry (nối)/(nối 2/3/4) bên dưới.

**Đã làm (5 commit code + docs, TẤT CẢ deploy+verify LIVE):**
- **P-1.1 + P3 MỞ KÊNH HỌC** `6933643` — vá R1 (nhãn 'đáng tin' cho input chua_chac) + `hoc_quy_uoc`/`thu_hoi_quy_uoc` (học CÁCH ĐỌC theo phiên, §2.6 backstop số-học-không-thành-số-chốt, LLM chặn tool ghi R8). Red-team 2 tầng (thiết kế 119-agent + implementation 19-agent tự-repro, vá 5 bug cổng F1-F5).
- **P4 rào tổng/Excel** `e9c4f80` — learned_handles fail-closed + cột chua_chac + mục 'chưa xác nhận'.
- **KIỂM THỬ GĐ0-2** `5b13ba0` — +212 test offline (8 file: visual/excel/misc/vntext/fuzz/dwgconv/MCP-stdio-thật/routes) + vá **R11 (IDOR** cross-session /file//image) + **F-A (race** đóng subprocess giữa request). check.sh [10/10]→[18/18].
- **KIỂM THỬ GĐ3 (E2E-AI)** `7e9335e` — battery 198 câu + smoke 10/10 vs engine-truth; vá **bug empty-response** (Gemini trả 'thought' rỗng → tra_loi_ai bỏ cuộc; nhắc-1-lần). KPI ~1.1% bịa cứng (tự xác minh, không tin judge 3.9%).

**Kết quả test (clean-state CHỐT SỔ, 0 FAIL):** `check.sh` **HARNESS GATE PASS [18/18]** (25 tool · takeoff 240 · fallback 22 · session 25 · +8 file kiểm thử) · `test_qa_data.py` **129/129** · working tree TRACKED sạch, push hết, **HEAD `89ead72`** (code LIVE `7e9335e`). **KHÔNG pytest** (crash `I/O closed file`); **KHÔNG specs/** (dùng feature_list.json). feature_list: **29 done / 1 deferred** (ai-tu-hoc→done; dự toán chi phí HOÃN).

**3 BUG VÁ phiên này (đều LIVE):** R11 (bảo mật IDOR), F-A (concurrency race), empty-response (E2E robustness). **2 BUG ĐỌC-SỐ ghi-nhận-vá-sau:** id84 (gộp/đếm đài cọc 142 vs 59), id135 (min cao độ -10 vs -14.26).

**Quyết định dài hạn (đã lưu memory):** [[feedback-e2e-test-kpi]] (E2E bắt bug offline không lộ; judge KPI phải tự xác minh; điểm yếu demo=recall không phải bịa) · [[feedback-red-team-2-tang]] · [[project-ke-hoach-kiem-thu]] (kế hoạch 6-GĐ + finding). Vòng AI tự học: P-1..P4 XONG&LIVE; **P5 (codify) CHẶN tới khi có bản vẽ VN ≥3 firm**.

**Đang chờ / bước tiếp:** **GĐ4 đa-domain** (cần bản vẽ VN thật ≥3 firm — budget không mua được, xin đối tác; trùng gate P5) · **id84/id135** vá sau · **F-B** (nối UI web cho kênh học P3 hay giữ MCP-client-only) · dự toán chi phí HOÃN.

---
## Session 2026-07-13 (nối 4) — KIỂM THỬ GĐ3 (E2E-AI 198 câu) + vá bug empty-response
**Mục tiêu:** user chốt option 2 (gồm E2E-AI) + "chi phí API không quan trọng". Có key (`../demo_doc_autocad/.env`), USE_AI=True. Chạy GĐ3 LOCAL (không đụng LIVE đối tác).

**Đã làm:**
- **SMOKE (`kichban_gd2`, 12 lượt):** đối chiếu ENGINE-truth tự động → **10/10 khớp số**, 0 bịa. Anti-bịa mọi cờ (thiếu→hỏi/không-tồn-tại/đa-tiết-diện/chưa-chắc/số-lần≠số-bộ) đều lộ.
- **FULL BATTERY 198 câu** (Gemini 2.5-flash, fallback-tắt-đo-sạch, 18 phút, 0 exception): DAT 105 + PHAN 27 (67%) · SAI 49 · RỖNG 17. **Judge-panel 12 agent Claude** (khác nhà-model Gemini, chống đồng-loã) chấm vs ky_vong/tieu_chi_dat + factsheet `dump_profile`.
- **BUG EMPTY-RESPONSE (tìm+vá):** 17/198 (8.6%) trả "AI không đưa ra nội dung" @1s. Rerun fallback-BẬT: 9 hồi phục, 8 CỨNG ĐẦU (highlight + câu đơn giản). Root cause (đọc code): Gemini 2.5-flash trả part `thought` RỖNG (không text/không tool) lượt đầu → `tra_loi_ai` (mcp_bridge.py:409) bỏ cuộc NGAY. **Vá: NHẮC-1-lần** (cờ `da_nhac_rong`) trước khi bỏ cuộc → re-run 8/8 hồi phục (id54 'BỂ NƯỚC PCCC' thực CÓ [A1263]; id132 từ chối trung thực). Test `[H.10]` (mock fake-resp, 2 ca: nhắc-rồi-phục-hồi + rỗng-cả-2-lượt-mới-báo).
- **XÁC MINH KPI BỊA (không tin judge mù — [[feedback-bia-tai-sinh-tang-code]]):** judge thô báo 7 bịa/3.9%; tự đọc answer+factsheet → **chỉ ~1.1% bịa CỨNG**: id84 (đài cọc tổng 142 vs 59 + gộp nhầm dầm) + id135 (cao độ -10 vs -14.26). Còn lại: id17 false-positive (100m THỰC có ở bảng thép), ~4 ranh-giới (ước-lượng-có-cờ ≠ bịa). 49 SAI đa số "đọc thiếu" (recall miss, an toàn).

**Kết quả test:** check.sh **[18/18] PASS** (model_fallback 20→22 +H.10) · takeoff 240 · qa 129 · 0 FAIL. E2E: demo RẤT chắc anti-bịa (KPI ≈0% bịa gần đạt, ~1% bịa cứng edge-case). **✅ COMMIT `7e9335e` + push + deploy + verify LIVE** (`/version` khớp + `/health` ok).

**Bài học:** E2E THẬT bắt bug mà offline không lộ (empty-response chỉ hiện khi gọi Gemini thật dưới tải). Judge-panel hữu ích NHƯNG phải TỰ xác minh KPI (judge over-flag ước-lượng-có-cờ + false-positive do factsheet thiếu cột). Điểm yếu thực của demo = RECALL (đọc thiếu), không phải bịa — đúng ethos "thà thiếu hơn bịa".

**Đang chờ:** commit vá empty-response (rồi deploy LIVE). **FINDING vá sau:** id84 (gộp/đếm đài cọc), id135 (min cao độ), ước-lượng over-fire trên câu-bẫy. **GĐ4** đa-domain (cần bản vẽ VN ≥3 firm). **GĐ5** thu hồi ✅ (đã dọn _uploads/_renders test). **F-B** nối-UI-web-P3 hay MCP-only.

---
## Session 2026-07-13 (nối 3) — KIỂM THỬ TỔNG THỂ GĐ0-2: +212 test + vá R11(IDOR)+F-A(race)
**Mục tiêu:** user giao "đóng vai TESTER chuyên nghiệp, rà toàn dự án (A-Z, P1-P4), lên kế hoạch kiểm thử nhiều giai đoạn, thu hồi dữ liệu test, nghiên cứu nguồn bản vẽ mở". Budget API KHÔNG là ràng buộc. Chọn phương án tối ưu → GĐ0-2 (offline + vá code) trước.

**Đã làm:**
- **NGHIÊN CỨU (workflow 4-agent):** bản-đồ-độ-phủ (25 tool vs test) + benchmark-infra (battery 198 câu/kichban_gd2 truth-engine/gap_verify) + corpus-mở (8 nguồn license rõ: ezdxf MIT, Autodesk imperial, LibreDWG…) + bề-mặt-E2E (routes + cách thu hồi). → `KE_HOACH_KIEM_THU_TONG_THE.md`.
- **PHẢN BIỆN KẾ HOẠCH (workflow 4-góc):** 4/4 "cần sửa", 27 finding/10 CAO. TỰ xác minh 2 lỗi CODE: **F-A** (`_close_session` chỉ giữ `_SESS_LOCK` → LRU/TTL đóng subprocess GIỮA request) + **F-B** (grep `hoc_quy_uoc` app.py=0 → kênh học P3 KHÔNG tới web, chỉ MCP-client). Nâng plan lên v2 (E2E full battery, đo ổn định N-lặp, grader tất định mislabel+bịa-mềm, tách overfit 2 nhánh, budget-sửa-được vs không).
- **GĐ1-2 (offline, 0 phí):** workflow 6-agent viết+tự-verify test → +8 file, **212 ca**, 0 bug: visual-highlight 15 · excel-content 17 (mở lại .xlsx) · misc-tools 84 · vntext 28 · fuzz 36 · dwgconv 10 · **MCP-stdio thật 14** (spawn mcp_server + JSON-RPC + wiring hoclog + số học không lọt tổng qua transport) · app-routes 8. check.sh [10/10]→**[18/18]**.
- **VÁ R11 (IDOR):** `s["artifacts"]` + `_artifact_owned` → `/file` `/image` cross-session 404 + traversal 404. Test `[K.7]` (5 ca).
- **VÁ F-A (race):** `_try_close_session` acquire-non-blocking (bận→bỏ qua) + `_evict_one_lru` né phiên bận. Test `[K.8]` (3 ca).

**Kết quả test:** check.sh **[18/18] PASS** · takeoff 240 · qa 129 · session **25** (+K.7 R11 +K.8 F-A) · **0 FAIL**. 0 bug SẢN PHẨM (lõi đọc-số vững; 2 bug ở tầng session/route đã vá). **✅ COMMIT `5b13ba0` + push + deploy + verify LIVE** (`/version` khớp + `/health` ok).

**Bài học:** đóng-vai-tester + workflow phản biện KẾ HOẠCH (không chỉ code) bắt 2 bug hạ tầng mà 380+ test cũ (dùng FakeBridge tuần tự) KHÔNG lộ (race concurrency + IDOR). Test tầng transport THẬT (spawn subprocess) khác test method trực tiếp — phải có. 0-bug-sản-phẩm sau khi bịt gap = tín hiệu lõi cứng.

**Đang chờ:** commit GĐ0-2 (rồi push+deploy+verify LIVE). **GĐ3** E2E-AI full battery (cần GEMINI_API_KEY riêng) · **GĐ4** đa-domain (cần bản vẽ VN ≥3 firm) · **GĐ5** thu hồi dữ liệu test · **F-B** quyết nối-UI-web-cho-P3 hay MCP-only.

---
## Session 2026-07-13 (nối 2) — P4 RÀO TỔNG/EXCEL (learned không-vào-tổng + cột chưa-chắc) — ⚠ CHƯA COMMIT
**Mục tiêu:** user "làm tiếp P4" (sau P-1.1+P3 đã LIVE `6933643`).

**Đã làm (probe → design → implement → adversarial review → test):**
- **PROBE:** đọc `tong_hop_khoi_luong`+`xuat_excel` — xác nhận rows dựng HOÀN TOÀN từ 8 index, KHÔNG bao giờ đọc `hoc_phien` → số học structurally không vào tổng (INV-2 đã giữ). P4 = biến lời-hứa thành ràng-buộc-CODE + hiện mục học.
- **IMPLEMENT (`tools_core.py`):** (1) **fail-closed guard** `learned_handles={r['anchor_handle'] for r in _quy_tac_hieu_luc()}`; `rows=[r for r in rows if handle not in learned_handles]` (no-op bình thường vì learned-anchor residual, nhưng khoá bất biến bằng CODE chống future-bug/P5-codify hút anchor học vào index). (2) **cột `chua_chac`** per-row (keyword TẠM TÍNH/suy đoán/thiếu SL/chưa rõ, quét cả nguon+hang_muc). (3) **`quy_uoc_chua_xac_nhan`** = re-parse tươi các quy ước học, LỘ cho đối tác NHƯNG KHÔNG cộng tổng (song song can_bo_sung/gia_dinh). `xuat_excel`: cột 'Chưa chắc' (8 cột) + khối "QUY ƯỚC ĐỐI TÁC DẠY (CHƯA XÁC NHẬN)".
- **ADVERSARIAL REVIEW (1-agent, tự-repro chạy engine + mở lại .xlsx):** AN TOÀN — mục 1/2/4/5 vững (số học KHÔNG vào tong_phu/bang, filter no-op đúng, `_hoc_reparse` không crash, Excel 8-cột OK, 0 regression khi hoc_phien=[]). Vá 1 LOW: keyword 'suy đoán' CHẾT (nằm ở hang_muc '(đv suy đoán)' không ở nguon) → quét cả hang_muc.

**Kết quả test (0 FAIL):** `test_takeoff_chong_bia.py` **240/240** (+4 P4: fail-closed collision cưỡng bức, cột chua_chac, xuat_excel không crash, visibility fixture thật) · `test_qa_data.py` **129/129** · `check.sh` **[10/10] PASS**. Dọn rác repro agent (`scratchpad/`). **✅ COMMIT `e9c4f80` + push + deploy + verify LIVE** (`/version` commit khớp HEAD + `/health` ok).

**Bài học:** tầng tổng/Excel vốn đã an-toàn-cấu-trúc (không đọc hoc_phien) nhưng biến thành RÀNG-BUỘC-CODE + test khoá là đúng ethos "lời-hứa-thiết-kế → ràng-buộc-code"; adversarial review tự-repro (chạy + mở lại xlsx) bắt keyword-chết mà đọc-code-thường bỏ qua.

**Đang chờ:** (P4 đã LIVE ✅ `e9c4f80`) — **P5** (codify quy ước học lên `_build_*` toàn cục — **CHẶN tới khi có corpus ≥3 firm**; G6: red-team P3 mới 1-domain kết cấu VN → cần bản vẽ đa-domain chống overfit TRƯỚC khi mở template mới / codify). Dự toán chi phí HOÃN. **Vòng AI tự học: P-1→P0-P1→P2→P-1.1→P3→P4 XONG & LIVE; còn P5 (nghẽn corpus).**

---
## Session 2026-07-13 (nối) — P-1.1 vá R1 + **P3 MỞ KÊNH HỌC** (code + red-team 2 vòng) — ⚠ CHƯA COMMIT
**Mục tiêu:** user chốt "khởi động P3, chạy red-team đa-agent TRƯỚC". Rồi "chọn phương án tối ưu và làm" (giao tôi quyết sắp xếp). Rồi "chưa commit, tiếp P3 luôn, commit cả cụm sau".

**Đã làm (theo quy trình chuẩn: red-team thiết kế → chọn phương án → code từng lát → test → red-team implementation → vá → test):**
- **Baseline đầu phiên** xác nhận (KHÔNG pytest/KHÔNG backend — dùng check.sh): trước phiên takeoff 214, qa 129, gate [9/9].
- **RED-TEAM THIẾT KẾ P3 (workflow 119 agent):** 9 hướng tấn công thiết kế × 3 giám định mặc-định-refute → 36 finding → **24 sống sót** (5 CAO). Phán quyết **CONDITIONAL GO** — Lát 0 (backstop provenance §2.6 + nhãn trung thực R1) là điều kiện CHẶN-SHIP, KHÔNG lùi sang P4. Doc `KET_QUA_REDTEAM_P3.md`. TỰ xác minh R1/R2 trên code thật (co_gan_dim :1871 chỉ whitelist gan_vi_tri → E2 chua_chac bị dán 'đáng tin').
- **QUYẾT ĐỊNH sắp xếp (tôi chọn):** tách **P-1.1** = vá R1 (lỗ E2 ĐANG TỒN TẠI, độc lập P3) làm TRƯỚC như đơn vị riêng — đúng tiền lệ P-1 (vá lỗ trước khi xây bộ khuếch đại) + kỷ luật commit + bền trước rủi ro G6.
- **P-1.1 (vá R1):** `_gan_cc` gắn cờ MÁY-ĐỌC `resp['chua_chac']`/`can_doi_chieu` ở MỌI đường-ra; nhánh ghi_chu chỉ 'đáng tin' khi 0 input chua_chac. Adversarial review 1-agent trên diff: AN TOÀN + tìm 1 lỗ phụ (cờ vắng ở 5 nhánh lỗi) → vá luôn. Test `[Z0]` 3 ca.
- **P3 Lát 1-4:** primitives (used_handles+thép, `_text_by_handle`, `_quy_tac_hieu_luc`) → `hoc_quy_uoc`/`thu_hoi_quy_uoc` + ENUM parser token-nguyên-vẹn 7 cổng → wiring `_ung_vien_hoc` + **§2.6 backstop `co_hoc`** → tool-layer (2 MCP tool, loại khỏi gemini_tools, luật 17, content_hash). Test nhóm `[Z]` + file mới `test_hoc_quy_uoc.py`.
- **RED-TEAM IMPLEMENTATION (workflow 19 agent, tự-repro chạy engine THẬT):** **INV-A/B/C/D lõi KHÔNG phá được** (số học không vào ket_qua/tổng/Excel, không mutate, cô lập, backstop vững) — kết quả tích cực. Vá **5 bug chất-lượng-cổng INV-E** (đều tự-repro trước khi vá): **F1** `_HOC_NUM_TOK_RE` lookbehind `\d`→`\w` (mác 'B25'→25mm số vô chủ) · **F2** đơn vị cm/m ghi rõ (250cm→250mm lệch 10×) fail-closed · **F3** Đ↔D chéo-mã (unaccent gộp Đ→D) → `_norm_ma` giữ đ/d · **F4** đa-mã any→all · **F5** copy `la_hoc` xuống da_co (backstop 2 lớp). Dọn rác repro agent (`_repro_f1.py`…) khỏi repo.

**Kết quả test (clean cuối phiên, 0 FAIL):** `test_takeoff_chong_bia.py` **236/236** (nhóm A-Y + `[Z0]` R1 3 ca + `[Z]` P3 20 ca) · `test_qa_data.py` **129/129** · `check.sh` **[10/10] PASS** (25 tool · +hoc_quy_uoc 2). **✅ COMMIT `6933643` + push + deploy + verify LIVE** (`/version` commit khớp HEAD + `/health` ok=true, use_ai). Working tree TRACKED sạch.

**Bài học:** (1) red-team THIẾT KẾ bắt lỗ tồn tại (R1 khuếch đại) + backstop-phải-ở-P3-không-chờ-P4; red-team IMPLEMENTATION (tự chạy engine) bắt lỗ mà thiết kế không thấy — cổng token-nguyên-vẹn regex phải loại chữ-số DÍNH chữ cái (B25), unaccent gộp Đ→D là bẫy chéo-mã. (2) 2 tầng red-team (thiết kế trước code, implementation sau code) đều cần. (3) INV-A (số học không thành số bàn giao) giữ được nhờ backstop provenance là chốt an toàn thực sự — các lỗ INV-E chỉ hạ CHẤT LƯỢNG gợi ý, không rò số.

**Đang chờ / bước tiếp:** (P-1.1+P3 đã LIVE ✅ `6933643`) — **P4** (rào Excel learned_handles fail-closed — nay §2.6 đã chặn tối thiểu ở tinh_dai_luong, P4 củng cố tầng tổng) · **P5** (codify — CHẶN tới khi có corpus ≥3 firm; **G6: red-team P3 mới chạy 1-domain kết cấu VN, cần bản vẽ đa-domain chống overfit trước khi mở template mới / codify**). Dự toán chi phí vẫn HOÃN.

---
## Session 2026-07-13 (CHỐT SỔ) — Khởi động vòng AI TỰ HỌC: Kế hoạch + P-1 + P0-P1 + P2 (đều LIVE)
**Tóm tắt phiên (DÀI, nhiều commit, mỗi phase theo quy trình chuẩn: implement → adversarial review → vá finding → test giữ baseline → commit → push/deploy/verify LIVE):**
- **Baseline đầu phiên** xác nhận (lưu ý user gõ `pytest`/`backend/` generic — dự án KHÔNG có, dùng script+check.sh).
- **KẾ HOẠCH CHI TIẾT AI tự học** (`KE_HOACH_AI_TU_HOC_CHI_TIET.md`) — workflow 17-agent (design-panel 3 lăng kính + red-team 7 hướng) → kiến trúc eng-minimal + grafts safety-first; phát hiện + tự-tái-hiện **6 lỗ tồn tại E1-E6** phải vá trước; lộ trình P-1..P5. Commit `e32d7ce`.
- **P-1** vá 6 lỗ E1-E6 (`73990de`, LIVE `5ecaca1`): neo ứng viên/provenance-xác-nhận-theo-handle/comparator-đối-chiếu/chống-injection/loud-skip/uuid-upload. Red-team diff bắt+vá overfit E1 (note kg xa mã bị vứt im lặng). Test [X] 12 ca.
- **P0-P1** đọc-thuần (`6608edf`, LIVE `015161e`): `used_handles`/`_residual_texts` + `phan_loai_tin_hieu` ①②③ + tool `hoi_de_hoc`/`doi_chieu_nghi_ngo` (23 tool) + luật 16. Red-team ĐA-FIXTURE bắt classifier NGẬP NHIỄU 99% (thép/mác chuẩn coi 'mã lạ'; 9T KC 96 ứng viên/mã) → vá `_la_notation_chuan`+branch-order → 336→2. Test [Y] 11 ca.
- **P2** log WORM (`787b1e6`, LIVE `b94da21`): `hoclog.py` CHỈ GHI (redact/cap+xoay/best-effort) + wiring tool-layer giữ core thuần; **bất biến KHÔNG hồi-tiếp inference** khoá bằng grep-guard (đếm-open+glob). Adversarial review 1-agent: 0 CONFIRMED cao/TB, vá 2 thap. Test [P2] 20 ca → check.sh [9/9].

**Kết quả test (clean-state cuối phiên, ĐỀU 0 FAIL):** `test_takeoff_chong_bia.py` **214/214** (nhóm A-Y) · `test_qa_data.py` **129/129** · `check.sh` = **HARNESS GATE PASS [9/9]** (import+23 tool · no-key · takeoff 214 · fallback 20 · size-guard 9 · file-ttl 12 · session 17 · health 11 · hoc-log 20). Working tree TRACKED sạch, push hết, **HEAD `cd0d767`** (P2 code verify LIVE tại `b94da21`). **KHÔNG pytest** (crash `I/O operation on closed file`). feature_list: 28 done / 1 deferred (dự toán chi phí) / 1 planned (ai-tu-hoc — đang xây theo phase).

**Quyết định dài hạn (đã lưu memory):** vòng AI tự học xây INCREMENTAL, P-1→P0-P1→P2 đều ĐỌC-THUẦN (chưa học gì, an toàn tuyệt đối); **P3 = ranh giới MỞ KÊNH HỌC = rủi ro cao nhất**, cần red-team workflow đa-agent mạnh. Bài học lặp lại: **red-team trên DIFF THẬT + ĐA-FIXTURE bắt overfit/nhiễu mà test-1-fixture (kể cả có số kỳ vọng) bỏ sót** — đã cứu 2 lần trong phiên (E1 R=8000, classifier 99% noise).

**Đang chờ / bước tiếp:** **P3** (`self.hoc_phien` + `hoc_quy_uoc`: đối tác dạy cách đọc, áp-phiên, cờ chưa-xác-nhận, thu-hồi được) — làm KHI user chốt, chạy red-team mạnh trước. P4 (rào Excel không-vào-tổng) · P5 (codify quy ước toàn cục — **CHẶN tới khi có corpus ≥3 đơn vị thiết kế**, nút thắt cứng nhất). Dự toán chi phí vẫn HOÃN chờ đối tác.

---
## Session 2026-07-13 — AI TỰ HỌC P2: log WORM append-only (cổng-4, đọc-thuần)
**Mục tiêu:** user chốt "làm tiếp P2 log WORM" — ghi NHẬT KÝ các lần phơi "chỗ bí" (`hoi_de_hoc`/`doi_chieu_nghi_ngo`) cho DEV rà. Vẫn đọc-thuần, KHÔNG học/KHÔNG hồi-tiếp inference.

**Đã làm:**
- **`hoclog.py`** (module mới): logger **CHỈ GHI** (mode `'a'`), redact `file_hash` (KHÔNG lưu path thật) + `vn` cắt ngắn, best-effort nuốt lỗi (không chặn luồng), tắt bằng env `HOC_LOG=0`, cap `HOC_LOG_MAX_MB`(5) → xoay `.1` (bound đĩa).
- **Wiring ở TOOL LAYER** (`mcp_server.py`): `hoi_de_hoc`/`doi_chieu_nghi_ngo` gọi `hoclog.ghi` → **core `tools_core` giữ THUẦN** (test cũ không sinh log rác). `_hoc_log/` gitignored.
- **BẤT BIẾN sống còn** (log KHÔNG hồi-tiếp inference → chống warm-start `hoc_phien` = đầu-độc chéo phiên) khoá bằng **grep-guard test**.
- **Adversarial review (1 agent, tự tái hiện code thật):** KHÔNG CONFIRMED cao/TB về đúng-đắn/an-toàn (bất biến giữ, tool không thể vỡ vì log lỗi nhờ 2 lớp try/except, backward-compat sạch). Vá 2 thap: **rotation/cap** (CONFIRMED) + **grep-guard porous** → siết bằng đếm-`open()`==1 (chặn `open()` mặc-định-đọc + iterator-read) + GLOB mọi `*.py` (bền hơn danh sách cứng 4 module).

**Kết quả test:** `tests/test_hoc_log.py` **[P2.A-D] 20 ca** (schema/redact/off + grep-guard + wiring + rotation) → `check.sh` thêm bước **[9/9]** = **HARNESS GATE PASS**. takeoff **214/214** + qa **129/129** KHÔNG regression (P2 không đụng core/tool cũ). Commit **`787b1e6`**(code)+**`b94da21`**(doc). **✅ PUSH + DEPLOY + VERIFY LIVE:** `/version` commit = `b94da21d34657...` khớp HEAD; `/health` ok.

**Bài học:** với feature ĐỌC-THUẦN nhỏ (logger), review 1-agent gọn là proportionate; grep-guard là "hàng rào bất biến" — phải siết chống cả open()-mặc-định-đọc + module mới (glob), không chỉ blacklist chuỗi. Wiring ở TOOL LAYER giữ core thuần = test không nhiễm side-effect.

**Đang chờ:** (P2 đã LIVE ✅) — bước tiếp: **P3 — MỞ KÊNH HỌC** (`self.hoc_phien` + `hoc_quy_uoc`: đối tác dạy cách đọc, áp-phiên) = **rủi ro CAO NHẤT**, cần red-team mạnh (workflow đa-agent) trước khi làm. P4 (rào Excel) · P5 (codify, chặn tới khi có corpus ≥3 firm).

---
## Session 2026-07-12 (d) — AI TỰ HỌC P0→P1 (đọc-thuần: used_handles/residual + classifier ①②③)
**Mục tiêu:** user chốt "làm tiếp P0→P1 vòng AI tự học" — phần ĐỌC-THUẦN (read-only, KHÔNG học/KHÔNG mutate state): phát hiện & phơi "chỗ bí" cho đối tác, chưa học gì.

**Đã làm:**
- **PROBE** cấu trúc handle 8 index (kế hoạch cảnh báo levels thiếu handle → đúng: gom handle text cao độ qua `_ELEV_RE`).
- **P0:** `self.used_handles` = HỢP handle đã hấp thụ (qty+qty_handle/section/door/stated_vol/stated_area/dim/sheet + text cao độ); `_residual_texts()` = `self.texts − used` (phép bù); `self.hoc_phien=[]`. Verify residual=texts−used, 0 handle index lọt residual.
- **P1:** `phan_loai_tin_hieu(ma)` → ① (residual có DẤU HIỆU cấu trúc trong band quanh mã → HỎI-ĐỂ-HỌC, phơi nguyên văn+handle, KHÔNG bịa nghĩa) / ② (không). `doi_chieu_nghi_ngo(ma)` → ③ (đa tiết diện/đơn vị cm-mm/cửa chưa chắc, KHÔNG tự chọn bên). 2 MCP tool `hoi_de_hoc`/`doi_chieu_nghi_ngo` (23 tool) + luật 16 SYSTEM_PROMPT.
- **Red-team đối kháng 2-agent** (diff + fixture thật) bắt **lỗi CAO mà test 1-fixture bỏ sót:** classifier NGẬP NHIỄU 99% — ký hiệu thép chuẩn 'Ø10a100'→'a100', mác 'B20'/'CB240' bị coi 'mã lạ'. **9T KC: D3=96 ứng viên (334/336 là thép)** — đúng kịch bản memory cảnh báo. VÁ: `_la_notation_chuan` loại thép Ø/rải a·/mác b/cb; branch `_SECT_STD_RE` TRƯỚC (không nhầm '800x3000'='mã lạ x3000'); dedupe theo nhãn; `_ELEV_RE.match` thay `_ELEV_IN_RE.search` (không nuốt text hỗn hợp). → **9T KC 336→2** (còn 'THÉP CHỜ V-1' = nhãn lạ THẬT), CT-A 26→0 (② trung thực).

**Kết quả test:** takeoff **214/214** (nhóm mới **[Y] 11 ca**: P0 residual + classifier ①②③ + noise-filter fixture thật + data-independent tất định) · qa **129/129** · check.sh **[8/8]**. Commit **`6608edf`**(code)+**`015161e`**(doc). Read-only → 0 regression tool cũ. **✅ PUSH + DEPLOY + VERIFY LIVE:** `/version` commit = `015161e62fb870...` khớp HEAD; `/health` ok.

**Bài học:** red-team ĐA-FIXTURE bắt overfit mà test 1-file KHÔNG lộ (CT-A C1=1 ứng viên "sạch", nhưng 9T=96 ngập nhiễu). ① đúng phải HIẾM (chỉ nhãn thật bất thường) — notation chuẩn TCVN (thép/mác) KHÔNG phải "chỗ bí". Đây đúng ethos chống-overfit + memory `feedback-tranh-overfit`.

**Đang chờ:** (P0-P1 đã LIVE ✅) — bước tiếp **P2** (log WORM append-only, vẫn đọc-thuần) → **P3** (self.hoc_phien + hoc_quy_uoc — MỞ KÊNH HỌC, rủi ro cao nhất, cần red-team mạnh) → P4 (rào Excel) → P5 (codify, CHẶN tới khi có corpus ≥3 firm).

---
## Session 2026-07-12 (c) — TRIỂN KHAI P-1: vá 6 lỗ tồn tại E1-E6 (nền cho AI tự học)
**Mục tiêu:** user chốt "commit tài liệu + bắt tay P-1". Commit doc kế hoạch (`e32d7ce`) rồi triển khai P-1 = vá 6 lỗ ĐANG TỒN TẠI (tính năng tự học sẽ khuếch đại nếu không vá).

**Đã làm (quy trình chuẩn: workflow spec → tự đọc code → implement tuần tự E4→E6→E5→E1→E3→E2, test sau mỗi bước → red-team đối kháng diff → vá finding → commit):**
- **Workflow 7-agent** ra spec sửa TỐI THIỂU + backward-compat + regression-watch + test đối kháng cho từng lỗ (đã chạy fixture thật). Thứ tự implement + helper dùng chung do agent tích hợp chốt.
- **Vá 6 lỗ** (`tools_core.py`/`mcp_bridge.py`/`app.py`/`render.yaml`/tests): **E1** neo+lọc-bán-kính `_KG_UV_R` (loại note ngữ cảnh khác); **E2** `_xac_nhan_ung_vien_theo_handle` giữ provenance (chua_chac/handle/can_doi_chieu, handle bịa→từ chối); **E3** `_rs_so_luong` đối chiếu file→`nghi_ngo` khi lệch (số dùng đối tác); **E4** SYSTEM_PROMPT rule 15 + `_co_chi_thi_dang_ngo` (advisory); **E5** runner đếm SKIP+CANH BAO; **E6** upload uuid_basename + cookie Secure gate-env.
- **Red-team đối kháng 4-agent trên diff** → 4 CONFIRMED đã vá: **E1 overfit** (note kg xa mã bị vứt IM LẶNG → nay LỘ note xa hạ 'thap'+khoảng cách, "thất bại phải lộ"); **E4 false-positive** ('coi như tường 220'/'bỏ qua lớp vữa' bị cờ oan → thu hẹp chỉ bắt 'bỏ qua LUẬT/quy ước'); **E2 ép-thiếu-oan** (so_luong_handle → fall-through đọc file); **E3 xau** (lộ nghi_ngo cả khi input khác không hợp lệ). Red-team XÁC NHẬN **KHÔNG rò P4** (tong_hop/Excel không tiêu thụ output tinh_dai_luong) + backward-compat.

**Kết quả test:** `test_takeoff_chong_bia.py` **203/203** (was 191; nhóm mới **[X] 12 ca** khoá E1-E4 + E2 fall-through + E1 far-fallback) · `test_qa_data.py` **129/129** · `check.sh` **[8/8] PASS**. Commit **`73990de`** (code) + **`5ecaca1`** (doc). **✅ PUSH + DEPLOY + VERIFY LIVE:** `/version` commit = `5ecaca1bf767...` khớp HEAD; `/health` ok (uptime mới, use_ai, metrics sạch).

**Bài học:** red-team trên DIFF THẬT (không chỉ design) bắt được overfit E1 mà test-với-fixture-đơn KHÔNG lộ (fixture CT-A xanh chỉ vì note tình cờ gần mã) — đúng ethos chống-overfit + "thất bại phải lộ". Fix đúng KHÔNG phải siết chặt hơn mà là LỘ khi recall bị cắt. Backward-compat = chỉ thêm key khi kênh mới kích hoạt (input cũ byte-identical).

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
  - **#2 cờ suy_doan_don_vi cạnh <40 → KHÔNG phải bug (by-design), no-fix.** `_unit_ambiguous_sect` đòi `lo>=40` là ĐÚNG ngữ nghĩa: raw<40 → hiểu-mm = cạnh <4cm phi thực → chỉ cm khả dĩ → không nhập nhằng để cảnh báo. Tiết diện thật vùng đó (KT CT-A dầm 22×30, dm 22×50) đều resolve đúng cm, vô hại. Nới cờ sẽ ngập false-alarm. (Ghi chú vặt: mệnh đề `and hi <= 2000` dòng ~212 là dead-code, không đụng.)
  - **#1 recall SL 9T KT → BUG THẬT (đã vá).** `liet_ke_so_luong()` chỉ trả 6 mục (Hộp inline), **bỏ sót cả bảng thống kê cửa**: d2=9, d3=20, d10=18, d4=11, dkt=36… Nguyên nhân: `_QTY_RE` đòi từ-khoá+số trong CÙNG entity, nhưng bảng đặt tiêu đề cột 'TỔNG' và ô số ở entity RIÊNG. Ground-truth MẠNH (cột TỔNG của chính bản vẽ).
- **TRIỂN KHAI (hướng user chốt = đọc cột TỔNG, gated fail-silent):** `_build_schedule_qty_index(texts)` (`tools_core.py`) ghép mã↔số theo HÀNG (y-band) + CỘT (khớp header 'TỔNG'). Gate CHỐNG BỊA: ≥5 cặp DUY NHẤT/cột, |Δy| chặt, mã ký-hiệu sát bên TRÁI cột tổng; block không sạch → BỎ (thà thiếu hơn bịa). Merge vào `qty_index` (dedup label_norm, không đè inline/spatial). Nguồn 'bảng thống kê (cột TỔNG)' + handle đối chiếu.
- **VALIDATE ĐA-FILE (probe thật trước khi code):** dương KT 9T (bảng cửa @923022 → 22 mã, LOẠI 8 bảng thép lạc); ÂM KC/KT CT-A + CT-K → 0 mã bịa (giữ port-faithfulness `test_qa_data`).

**Kết quả test:** `test_takeoff_chong_bia.py` **177/177** (nhóm mới **[V]** 10 ca: 9T KT d2=9/d3=20/d10=18/d4=11/sk2=16 + end-to-end `tra_cuu_so_luong` + ÂM KC CT-A 0 bịa & giữ 94 mục) · `test_qa_data.py` **129/129** (port KHÔNG đổi) · `check.sh` PASS.

**Bài học:** #1 lộ đúng nhờ probe đa-domain; fix bảng-cột NHẠY LAYOUT → validate đa-file + gate fail-silent (thà under-recall hơn bịa) là bắt buộc theo ethos chống-overfit. #2 xác nhận "không phải mọi finding subagent là bug" — nghiên cứu trước, no-fix khi by-design.

**Đang chờ:** ⚠ CHƯA commit đợt residual — chờ user duyệt (rồi push/deploy/verify như đợt trước). Residual còn: window S-code |Δy| lỏng hơn (đã đọc nhưng nên đối chiếu thêm bản vẽ khác layout trước khi tin tuyệt đối); robustness H–L.

---
## Session 2026-07-11 — Task G: TEST ĐỐI KHÁNG ĐA-DOMAIN + vá 3 bug tầng tổng hợp/đọc
**Mục tiêu:** đầu việc G (ROADMAP) — mở rộng test đối kháng đa-domain (KC/KT 9T + hạ tầng) để khoá regression cho A–F. User giao tự chọn task → chốt G (đúng ưu tiên #1 an toàn/KPI ~0% bịa; H–L là ops, xếp sau "giao rộng").

**Đã làm:**
- **PROBE (workflow 6-agent, chạy engine THẬT offline):** 5 agent probe song song (KC 9T · KT 9T · CT-K · gap-check CT-A · overfit-hunter) → 1 agent tổng hợp. Phát hiện 3 vector nghi ngờ ở tầng TỔNG HỢP/ĐỌC-DIỆN-TÍCH (lõi chống-bịa/existence/cm-mm/lỗ-cửa vẫn vững).
- **TỰ KIỂM CHỨNG (repro độc lập — KHÔNG chỉ tin subagent):** chạy `tong_hop_khoi_luong()` + regex trên KT/KC CT-A thật, xác nhận:
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
- **PROBE file thật TRƯỚC (⚠ ROADMAP yêu cầu):** KT CT-A có ~17-20 nhãn m² HỖN TẠP (mái 634, sàn 591/545, sơn 117/44.5/38.1, tường 77.5, granit 52/30/22, trống 67/22.7/18/11 [garbled 'diÖn tÝch'], vách 3.3); KC có 'mật độ 16 cọc//1m2' NHIỄU + 'diện tích 7,04 m2' THẬT; KC 9T = 0 nhãn; hạ tầng 9 nhãn 'S=…m2'. → KẾT LUẬN: nhãn KHÔNG đều là 'sàn' → phải liệt kê verbatim, KHÔNG phân loại.
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
- **Vá parity cm/mm + đọc bảng cột nhà 9T** (`_build_section_index` ghép tọa độ + ngưỡng 130 + cờ mơ hồ): 9T C-3 = 80×80cm → 23.04 m³ (khớp demo 1); CT-A 4.704 m³ không đổi. `2a90a36`.
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
