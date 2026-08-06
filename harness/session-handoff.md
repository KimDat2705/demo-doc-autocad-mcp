# Session Handoff — demo 2

> **⭐ THỨ TỰ ƯU TIÊN CÔNG VIỆC (user chốt 2026-07-25) — A → C → D → B:** làm cạn nhóm trên trước khi sang nhóm dưới. **A** = chức năng CHÍNH (đọc chính xác + trả lời đúng, KHÔNG ảo giác) · **C** = RAM/dung lượng upload file · **D** = khác (vận hành/AI-tự-học/kiểm-thử/UI/bảo-mật) · **B** = dự toán/khối-lượng/xuất-Excel **LÀM CUỐI** (user cân nhắc thu hẹp; dự toán CHI PHÍ đã ngoài phạm vi). Chi tiết phân nhóm 64 đầu mục: artifact "Rà soát đầu mục" + `wf_d5d37fa6-683`; luật ưu tiên cũng ghi ở `AGENTS.md`. Memory `[[project-uu-tien-nhom-cong-viec]]`.

> **⭐ PIVOT AI-TỰ-HỌC (user chốt 2026-07-26) — "DEV DẠY TRƯỚC, ĐỐI TÁC CHỈ XÁC NHẬN":** **BỎ kênh đối-tác-dạy-mở** (không phơi `hoc_quy_uoc` cho đối tác — rủi ro dạy-sai + prompt-injection cao nhất dự án) + **BỎ P5 auto-codify** (hoá cứng từ log học) + **BỎ F-B web-teaching**. THAY BẰNG: (1) **KHO KIẾN THỨC DEV-SOẠN** đa-domain (ký hiệu/quy ước/thuật ngữ VN-EN + ca dễ-nhầm CH/D/mũi-cọc≠đáy-đài…), mỗi mục kiểm-chứng-được (TCVN/quy-ước-phổ-biến/bản-vẽ-thật), fail-open (ngoài kho → "bí" + HỎI, không đoán); (2) khi "bí"/dễ-nhầm → tool HỎI với **phương án chuẩn bị sẵn**, đối tác **CHỈ BẤM XÁC NHẬN (confirm-only)**, không nhập tự do. GIỮ `hoi_de_hoc`/`doi_chieu_nghi_ngo` (đọc-thuần) + `_TEMPLATE_ENUM` dev-cấp; `hoc_quy_uoc` giữ làm công cụ DEV nội bộ. **Tháo nút thắt P5-chờ-≥3-firm.** Kho kiến thức = việc nhóm **A** (giúp đọc đúng). Memory `[[project-ai-tu-hoc-ke-hoach]]` (pivot ghi đầu file). **→ Nghiên cứu chi tiết ✅ XONG: thiết kế chốt + 7 lát L0-L7 ở `KE_HOACH_KHO_KIEN_THUC.md`** (GO_WITH_ADJUSTMENTS). User chốt: CÓ nút /xac-nhan (đủ L5) + GIAO dev chốt danh sách ký hiệu. **→ L0+L1+L2+L4 ✅ CODE XONG (⚠ CHƯA commit — user chốt commit/push/deploy MỘT THỂ sau):** L0 gate dispatch-side (vá lỗ an ninh model gọi tool host-only qua dispatch) + L1 `kienthuc.py` 24 entry digit-free byte-lock `e55ac112…` + kb_refreeze.sh + /version kb_hash + L2 `_strip_kb` chống-lọt-rổ (K9 số-lén-không-lọt / K10 số-file-vẫn-vào-rổ) + **L4 graft có GATE bằng-chứng-dương** (3 điểm cắm: phan_loai/doi_chieu/cao_do; cap 1 câu/lượt; chống-lặp `kb_hoi`; `kb_da_phat` nền L5; test `test_kb_graft.py` 18/18 [30]; **red-team-impl corpus thật: file móng cặp ĐC/DC → HỎI đúng · thuần-cột 0/9 · ca fire duy nhất là D1 section+door = mâu thuẫn thật id84**). Gate bắt 2 regress (mock tools=[] + chuỗi khoá call-site cũ) → vá test đúng ý định. **→ L5 ✅ CODE XONG** (`Drawing.xac_nhan_ky_hieu` fail-closed 3 lớp + tool #31 host-only 2 hàng rào + bridge trả `kb_cau_hoi` + endpoint POST `/xac-nhan` + nút bấm PAGE; test `test_kb_xacnhan.py` 19/19 → check.sh [31]). **→ L3 ✅ XONG + ĐO A/B LIVE GO** (tool #32 `tra_ky_hieu` + `_P_R18`; PROMPT_VERSION `2026.07.27-kb-l3` FROZEN `239e8b7b…`; A/B 30 câu: trap 5/5 GIỮ cả 2 vế · routing 6/6 · giá trị R18 = trình bày nêu nguyên văn câu hỏi + đủ phương án khớp nút; test 13/13 [32]; gate [32/32] PASS). (User chốt: DÙNG key đã đưa, KHÔNG đổi key.) **⛔ L7 (xác nhận ĐỔI SỐ) = KHÔNG LÀM — chốt có SỐ 2026-07-27** (`wf_92eee202-d98`: 62 file/493 mục/357 mã → **0 ca kích hoạt**; ví dụ trụ cột `'DẦM D1'≠'CỬA D1'` trong docstring SAI so với code vì `'cửa'` ∉ `_MA_TYPE_WORDS`; gộp **giữ-1-vứt-1 không cộng** → bấm sai làm tổng **đi XUỐNG** 7% BOQ và bảng sai **trông sạch hơn**). **Đừng mở lại trừ khi có corpus MỚI đạt ngưỡng ≥1% tổng mục VÀ ≥3 file của ≥2 đơn vị.** → **VÁ 3 BUG L5 + 7 vá red-team ✅ LIVE `c9e2171`** (undo trung thực · cổng khoá BỘ BA theo mã · nút '↩ Hoàn tác' + bảng `#xnbox` + tool #33 `danh_sach_xac_nhan` host-only; red-team bắt 2 CAO do CHÍNH bản vá đầu: lệch-khoá strip/truncate + route tạo phiên đuổi LRU). Test kb-xacnhan **19→44**, gate **[33/33]**.
**CỤM L0-L5+L3 ✅ LIVE `998950f` (verify /version+kb_hash+/health). → L6 garble-Ø ✅ LIVE `fccc635`** (fold ỉ//g→Ø có gông trước unaccent; đo 53 file: +666 token, 0 phản-khớp, 0 đổi số; test 26/26 [33]; gate [33/33]). **KHO KIẾN THỨC L0-L6 XONG TRỌN.** CÒN: **L7 HOÃN** (xác nhận đổi-số — gated red-team 2 tầng riêng, KHÔNG tự khởi động) · họ-slash decode đầy đủ DEFER (1 file/firm).

> **🕒 CẬP NHẬT 2026-07-26 — NHÓM C (nâng dung lượng upload / RAM) = HOÃN TỚI CUỐI DỰ ÁN (user chốt):** nâng RAM = **tốn tiền Render (tiền túi)** → chờ dự án XONG + sếp ưng → kêu gọi tài trợ rồi mới nâng. **Chỉ API key Gemini được sếp cho dùng FREE;** mọi chi phí/nâng cấp trả-phí khác = tiền mình → **TRÁNH tới cuối**. **Demo hiện tại chỉ test file NHỎ/VỪA (≤45MB, trong bản Free).** ⚠ ĐỪNG tự khởi động lại nhóm C (kể cả phần "vá code chịu tải") khi user chưa yêu cầu — chuyển sang nhóm D. **Nghiên cứu nhóm C đã LÀM (dùng lại khi quay lại ở cuối):** đo RSS thật (84 file) ⇒ worst-case container = **316 + 11.28×dxf_mb** (web 68 + subproc 68 là 2 RSS riêng Render cộng cả) ⇒ `READFILE_MAX_MB=`**120** (KHÔNG phải 200 như HELD; 130 vẫn phá lằn 0.85) + `MAX_SESSIONS=`**1** → mở khoá **13/14** file bị chặn (chỉ file 202MB vẫn chặn trên 2GB). **⛔ CHỐT QUAN TRỌNG: `MAX_SESSIONS=1` HIỆN CHỈ LÀ CAP "MỀM"** — 3 lỗ code cho 2 doc ezdxf cùng nằm RAM (→ ~2640MB OOM dù cap=1): (a) phiên BẬN không bị đuổi `app.py:107-108` + lock non-blocking `app.py:72` [vốn CỐ Ý cho fix F-A]; (b) `MCPBridge.close()` fire-and-forget KHÔNG chờ subprocess chết `mcp_bridge.py:148-150`; (c) `nap_ban_ve` dựng doc mới TRƯỚC khi bỏ doc cũ `mcp_server.py:33-34`. ⇒ **config đúng thôi CHƯA đủ an toàn, phải VÁ CODE (đồng bộ close + chặn cứng khi bận + `del` doc cũ trước readfile) TRƯỚC khi bật gói trả phí.** **HELD `f025ad7` HIỆN BUGGY** (READFILE=200 → lọt file 202MB = 2324MB OOM; QUÊN hạ MAX_SESSIONS vẫn=4; lý do "5.8x" là tracemalloc không phải RSS). Số đo là Windows PeakWorkingSet — **PHẢI đo lại cgroup RSS trên Render/Linux trước khi chốt** (Linux thường cao hơn 10-30%). Workflow `wf_4e2405d0-971`. Chi tiết + hướng thay thế FREE (local-parse + upload index) ở `[[project-chiu-tai-va-chi-phi]]`.

> **🔁 2026-07-17 — THỬ MỞ PUBLIC RỒI HOÀN TÁC (repo GIỮ PRIVATE):** user đổi ý giữa chừng. Đã **khôi phục main về `130afae`** từ mirror backup + force-push → demo NGUYÊN TRẠNG (verify: `/version`=130afae, `/health` ok, **upload .dwg thật lên cloud CHẠY LẠI** — ODA convert ok, 102 layer/1555 text khớp local). **Mọi hash cũ trong tài liệu này CÒN HIỆU LỰC** (c0b85af/97ffc60/7188c3c/130afae…).
> **⚠ VÌ SAO REPO PHẢI PRIVATE:** `vendor/ODAFileConverter.deb` (53.6MB) là phần mềm **ĐỘC QUYỀN của Open Design Alliance**, phải commit để Render build Docker → **public = phân phối lại binary bên thứ ba**. Đây là ràng buộc LICENSE, không phải tuỳ chọn.
> **Muốn public thật sau này — ĐỪNG LÀM LẠI TỪ ĐẦU:** nhánh local **`public-ready`** đã có sẵn trọn gói (history sạch không .deb qua `git filter-repo` · Dockerfile tải ODA tuỳ chọn qua `ODA_DEB_URL` · thông báo .dxf-only thân thiện · .gitignore chặn .deb). Đánh đổi: cloud chỉ đọc .dxf tới khi đặt `ODA_DEB_URL`. Mirror backup: `D:/Dat-Antigravity/_backup_repo_truoc_khi_public_20260717/repo-mirror.git`.


## 🛡 2026-08-06 — RÀ TẦNG 3 (hàng rào chống bịa): TRẠNG THÁI THẬT + 2 đầu mục mới (`feature_list` 90 → **91**)
> **⛔ ĐÍNH CHÍNH TRÍ NHỚ CŨ — 3 "kênh lọt" ĐÃ VÁ XONG, đừng nêu lại như việc còn treo.** `neo-grounding-sach` **LIVE `5548fe1`+`5756b37`** bịt cả ba: (1) mã-hiệu gạch nối sinh neo ÂM (`DẦM D2-10`→−10; **68/76 file** có ≥1 neo âm; 24/76 neo âm rơi ĐÚNG dải cao độ = cấp phép bịa id135) · (2) **TÊN FILE** (cùng nội dung byte, đổi tên thành `MC coc -13.7 va 7500.dxf` → 2 câu bịa chuyển từ CHẶN sang LỌT) · (3) **HANDLE hex** (kết quả 3 handle + chữ KHÔNG SỐ vẫn sinh rổ `[1,2,9,38,13876]`). Cộng `lat4a-prose-0-chu-so-cao-do`. **Hiệu quả đo: lớp id135 lọt `0,0%`.** Chạy lại 2026-08-06: **6 suite hàng rào 471 ca, 0 FAIL** (grounding 57 · neo 34 · neo-rỗng 29 · handle 44 · i3 24 · takeoff 283).
>
> ### ⭐ THƯỚC ĐO — "tỉ lệ lọt" KHÔNG DÙNG ĐƯỢC, đây là chỗ dễ sai nhất
> 5 probe đo **CÙNG đại lượng** trên **CÙNG hàng rào** ra `0% / 23,8% / 32,2% / 37,9% / 52-77,5%`; giữ nguyên rổ neo **chỉ đổi BỘ SINH** số bịa → `0,0% → 13,6%` (probe khác `1,9% → 79,2%`). ⇒ **"tỉ lệ lọt" là thuộc tính của BỘ SINH, không phải của hàng rào. ĐỪNG trích con số nền nào, kể cả 15,0% hay 36-49% ở tài liệu cũ.**
> **BA thước THẬT thay thế:** ① **giết oan (FP)** trên 198 câu THẬT chấm bằng nhãn độc lập `ky_vong` — hiện **0** (guard gốc 0/198; guard số đếm 0/72) · ② **lọt theo LỚP tấn công đã biết** — id135 **0,0%** · ③ **vùng mù** (mỗi REFUSE phải phân loại được) — legacy **117/179** chưa phân loại, PA-0 đã bật seam vĩnh viễn ⇒ lượt sau = 0.
> **VÌ SAO FP LÀ RÀNG BUỘC QUYẾT ĐỊNH, không phải tỉ lệ lọt:** siết chặt hơn thì GIẾT CHÍNH CHỨC NĂNG — `ALL` giết **82% câu có PHÉP CỘNG** (việc chính của bóc tách), per-claim **96,7-100% câu nó giết là câu ĐÚNG**, bỏ ×1000 giết oan **36,5%→85,4%**. `ANY-GROUNDED` là luật DUY NHẤT có **0% chặn oan trên cả 7 dạng**.
>
> ### 🎯 "BAO GIỜ ĐỦ DÙNG" — tiêu chí thay cho "% hoàn hảo"
> ① **giết oan = 0** trên bộ câu thật (ràng buộc **CỨNG**) · ② **mỗi lớp tấn công đã biết → lọt 0%** (cộng dồn) · ③ **không tìm ra lớp mới** sau K vòng → tạm cạn, mở lại khi có corpus/model mới.
> Nguyên tắc: **hàng rào không cần hoàn hảo, nó cần KHÔNG BAO GIỜ SAI ÂM THẦM.** Số không neo được thì bị chặn, mà chặn thì người dùng THẤY.
>
> ### 📌 NGUYÊN TẮC BẤT DI (rút từ 2 kết luận NGƯỢC nhau cùng ngày)
> **SIẾT PHẠM VI thì được · ĐỔI LUẬT PHÁN QUYẾT thì không.** `guard-so-dem` **GO** (siết *cái gì được coi là khẳng định*: bắt đúng 1 — model nói '120 lần' trong khi tool trả 5 — **giết oan 0/72**) vs `per-claim` **NO_GO** (đổi luật phán quyết).
>
> ### 📊 TRẠNG THÁI HARNESS cho tầng 3 — **15 đầu mục**
> **9 done** (`anti-bia` · `i1-guard-validate-handle` · `guard-so-dem` · `neo-grounding-sach` · `a2-rổ-neo-rỗng` · `a3-neo-theo-trích-dẫn` · `lo-cum-tu-choi-tat-guard` · `lat4a-prose` · `pa0-seam-đo`) · **1 partial** (`i3-bounds-check`) · **5 NO_GO CÓ SỐ** (per-claim · câu-tổng-hợp-bị-giết · gợi-ý-trong-tool · bộ-dò-tự-cộng-số · cờ-số-máy-tính). **Nhóm NO_GO là TÀI SẢN** — chặn 5 hướng nghe rất hợp lý nhưng đã chứng minh làm hỏng.
>
> ### ➕ HAI CHỖ THIẾU → ĐÃ LẬP (user chốt 2026-08-06)
> 1. **`ra-kenh-bom-ro-neo-loop`** (mục mới, `planned`) — đầu mục **THƯỜNG TRỰC** tìm kênh bơm rổ neo thứ 4, 5… bằng loop-until-dry. Đây là **đòn bẩy DUY NHẤT** với điểm yếu ANY (rổ `{220}` + *"Dầm rộng 220 mm, cao 9999 mm, dài 12345 mm"* → **LỌT**), vì đổi luật đã NO_GO.
> 2. **Đo lại hàng rào = GỘP vào GĐ2 bước 2.6** của `KE_HOACH_NANG_CAP_MODEL.md` (user chốt gộp) — cùng 198 câu, một lượt chạy cho CẢ so-sánh-model LẪN phân-loại-hàng-rào; chạy riêng = đốt quota 2 lần. ⚠ Đọc kết quả phải tách *guard đổi hành vi* vs *model đổi văn phong* bằng cột `answer_truoc_guard`.

## 📏 2026-08-06 — ĐO RESIDUAL TOÀN CORPUS → hàng đợi công việc CÓ SỐ → `KET_QUA_DO_RESIDUAL_TOAN_CORPUS.md`
> **Phiên HỎI-ĐÁP, KHÔNG sửa code chạy.** Sản phẩm: `KET_QUA_DO_RESIDUAL_TOAN_CORPUS.md` + script `tests/do_residual_corpus.py` + dữ liệu thô `_khao_sat/residual_toan_corpus.json` (gitignored — **số liệu đã chép vào .md để không mất**) + 2 đầu mục `feature_list` (88 → **90**).
> **Phép đo ĐẮT: 14 phút.** Đừng chạy lại nếu chỉ cần số — đọc file .md.
>
> ### KẾT QUẢ — 86/86 file, 0 lỗi
> **956.114 đoạn chữ · residual 907.993 = 95,0%.** Phân rã: chữ+số-không-đơn-vị **42,2%** · số trần **25,0%** · chữ thuần **23,9%** · **CÓ ĐƠN VỊ (hàng đợi ưu tiên) 32.475 = 3,6%**.
> ⚠ **KHÔNG đọc "95%" thành "hỏng 95%".** 3 nhóm hạ tầng chiếm **751k/956k = 78,6%** tổng chữ với residual 96–99,9% nhưng "có đơn vị" chỉ 0,5–1,3% (chữ của chúng là tên mốc trắc địa/số hiệu cọc). Nhà dân dụng residual **62–70%**. ⇒ **hạ tầng cần thước đo RIÊNG**, gộp chung làm mọi tỉ lệ mất nghĩa.
>
> ### ⭐ XẾP HẠNG LOẠI DỮ LIỆU BỊ BỎ SÓT (= danh sách công cụ nên xây)
> **#1 đường kính thép `Ø10a150`/`2Ø14+2Ø14`/`4Ø10` — 17.908 = 55,1%** (cách biệt lớn) · #2 tiết diện `AxB` 4.688 = 14,4% · #3 gán nhãn `s=`/`L=`/`h=` 4.519 = 13,9% · #4 **có-đơn-vị-chưa-khớp-mẫu 3.601 = 11,1% (đáng soi, có thể lộ loại chưa biết)** · #5 độ dài 1.061 · #6 khối lượng 447 · #7 diện tích 193.
>
> ### ✅ ĐÃ XÁC MINH — 17.908 chuỗi Ø KHÔNG trùng bảng thống kê thép
> `2. Ket Cau_NHA 9T.dxf`: `thong_ke_thep` đọc **279.679,6 kg** từ **THUỘC TÍNH BLOCK** trong khi **3.850** chuỗi Ø trong **TEXT** là residual **100%**. Kiểm chéo `2. KET CAU MONG-…`: **183/183 residual**. **Hai tập TÁCH RỜI ⇒ con số là thật, không thổi phồng.**
>
> ### ⚠ BA CÁI BẪY ĐÃ TRẢ GIÁ TRONG PHIÊN — ĐỪNG DẪM LẠI
> 1. **`Drawing.texts` KHÔNG có trường chiều cao chữ** (khoá chỉ `handle/layer/text/vn/x/y`). Lần đo đầu ra *"81,2% số cô độc"* — **SAI HOÀN TOÀN** vì thang `H` mặc định về `1.0` = 1 đơn vị bản vẽ. Phải chuẩn hoá bằng **trung vị khoảng cách láng giềng gần nhất giữa các đoạn chữ trong CHÍNH file đó** → số thật: **96,1% số trần CÓ chữ ở gần** (63,7% sát bên).
> 2. **Cổng `READFILE_MAX_MB=45` chặn 14/86 file** — và đó chính là các bản **kết cấu LỚN NHẤT** (nhà 9T 114MB, thống kê thép 68MB). Bỏ ra thì kết quả lệch nặng về file nhỏ (72 file cho 212k chữ; đủ 86 file cho **956k** — tức 78% chữ nằm ở phần bị chặn). **Đo local PHẢI đặt `READFILE_MAX_MB=400`** — cổng 45MB là giới hạn RAM CLOUD, không phải logic; đọc local MIỄN PHÍ.
> 3. **residual ĐẾM THIẾU phần đã đọc bằng đường khác**: `4. Thong ke thep SUA.dxf` trông rỗng (27 đối tượng, 17 đoạn chữ, `thong_ke_thep`=0kg) nhưng có **8 `OLE2FRAME`**, bảng đầu **254 hàng × 32 cột** *"BẢNG TÍNH CHI TIẾT KHỐI LƯỢNG CỐT THÉP"* — tool #27 `doc_bang_nhung` **ĐỌC ĐƯỢC**. Đừng kết luận "file không đọc được" chỉ vì residual im lặng.
>
> ### ❌ HAI GIẢ THUYẾT VỀ "SỐ TRẦN" ĐÃ CHẾT (mẫu 8 file/1.114 số)
> **Tên layer cho biết nghĩa** — chỉ **~7%** trên layer mang nghĩa (`Caodo`/`CD_Dinh`/`CD_Day`), **76,8%** trên layer chung chung (`7`,`6text`,`Text`,`Chu`,`0`). **Lấy nhãn gần nhất là ra nghĩa** — cặp thật hỏng: `12 ← "MẶT CẮT 12-12"`, `9 ← "MẶT BẰNG"`, `14 ← "MẶT CẮT 14-14"`. ⇒ một phần đáng kể "số trần" **không phải dữ liệu** (số hiệu mặt cắt / bong bóng trục) — tỉ lệ số-trần đang **thổi phồng** vấn đề.
>
> ### ⚠ NHÓM "CÓ ĐƠN VỊ" MẠNH NHƯNG KHÔNG TINH KHIẾT — KHÔNG tự động đổ vào dự toán
> Đọc tay bắt nhầm: `V=1:100`/`H=1:500` = **TỶ LỆ bản vẽ** · `cút thép hàn DN100x45°` = **DN100 × GÓC 45°** không phải tiết diện · `cho 1m3 nước, nước dùng để ngâm…` = **ghi chú bảo dưỡng bê tông**. Phải qua **sổ số chưa gán** để NGƯỜI duyệt.
>
> ### 🎯 HƯỚNG GIẢI + YÊU CẦU USER (chốt trong phiên)
> 4 tầng theo "cần bao nhiêu kiến thức xây dựng": **A** loại-trừ (không cần chút nào) · **B** trích-theo-CẤU-TRÚC — *không hỏi "số này nghĩa là gì" mà hỏi "số này nằm ở đâu, cạnh nhãn nào" rồi **chép nhãn NGUYÊN VĂN**; hệ thống KHÔNG BAO GIỜ HIỂU, chỉ trích và trích dẫn* (tiền lệ tool #36 đạt 861/861) · **C** người-biết-nghề (TCVN › thầy › đối tác; **hỏi CÂU ĐÓNG kèm ảnh khoanh vùng**, không hỏi mở) · **D** sổ-số-chưa-gán.
> **User chốt:** *"tất cả số liệu phải đọc đúng, bất kỳ số nào cũng có thể liên quan dự toán"* → phân định đã thống nhất: **"không bỏ qua" ≠ "đọc được hết"; nguy hiểm là bỏ sót ÂM THẦM** ⇒ sản phẩm bắt buộc là **sổ số chưa gán** (đếm được, giảm dần được).

## 🔴 2026-08-06 — API KEY BỊ KHOÁ (billing) · KẾ HOẠCH NÂNG CẤP MODEL → `KE_HOACH_NANG_CAP_MODEL.md`
> **Phiên HỎI-ĐÁP, KHÔNG code** (user chốt). Sản phẩm: `KE_HOACH_NANG_CAP_MODEL.md` + mục `nang-cap-model-3-6-flash` trong `feature_list.json` (87 → **88**).
>
> ### ⛔ SỰ CỐ ĐANG DIỄN RA — demo KHÔNG trả lời được
> Mọi lệnh gọi Gemini trả **403 PERMISSION_DENIED · `Lightning dunning decision is deny for project: projects/883414745254`** (hệ thống **cưỡng chế thanh toán** của Google — chặn cấp PROJECT). **Nguyên nhân: chưa gia hạn thanh toán** (sếp xác nhận 2026-08-06).
> **Xác minh 2 đường độc lập:** (a) gọi thẳng từ máy local bằng key `.env`; (b) **E2E thật lên Render** — upload OK (`so_layer:4`, `tong_doi_tuong:35`) rồi `/ask` trả chữ đỏ 403, `/health.metrics` = `{asks:0, errors:1, uploads:1}`. **Cùng một mã project** ở cả hai ⇒ không phải lỗi sandbox/mạng. Thử `2.5-flash / 3.6-flash / 3.5-flash / 2.0-flash / 1.5-flash` — **cả 5 đều 403** ⇒ **đổi model KHÔNG cứu được**.
> **Phân tầng hỏng:** tầng đọc (36 tool, ezdxf) **VẪN CHẠY TỐT**; chỉ tầng model chết. Demo sẽ nạp file + hiện tóm tắt bình thường rồi **gãy ở câu hỏi đầu tiên** — kiểu hỏng dễ mất mặt nhất.
>
> ### 🐛 BUG THẬT phát hiện khi rà (độc lập với billing)
> `_FALLBACK_DEFAULT = "gemini-2.0-flash,gemini-1.5-flash"` (`mcp_bridge.py:55`) — **`gemini-2.0-flash` đã bị Google TẮT HẲN**. Model chết trả **404**, mà `_is_overloaded()` chỉ nhận `{429,500,502,503,504}` ⇒ **KHÔNG fail-forward, ném lỗi luôn**. Chuỗi dự phòng đã mục 1 nấc mà không ai biết.
>
> ### ⏳ HẠN CỨNG
> `gemini-2.5-flash` **bị khai tử 16/10/2026** (~10 tuần). Google chỉ định bản thay: **`gemini-3.6-flash`**.
>
> ### ✅ CHỐT MODEL (chi tiết + nguồn ở `KE_HOACH_NANG_CAP_MODEL.md`)
> Chính **`gemini-3.6-flash`** (GA, không preview · mạnh nhất dòng Flash về **gọi công cụ** · rẻ hơn 3.5-flash ở đầu ra $7,50 vs $9,00 · ít token ra ~17% ⇒ đỡ áp lực `MAX_TURNS=14`).
> ⛔ **KHÔNG chọn 3.1 Pro** dù user cho phép "dùng model thông minh nhất": còn `-preview`; **nút thắt dự án là ghép nhãn↔giá trị ở TẦNG ĐỌC, không phải suy luận** (`[[project-nut-that-recall-ghep-nhan-gia-tri]]`) — Pro không đọc được ô bảng mà tool không trả về; tiền lệ *"Pro preview cạn quota ~25 req"* (`mcp_bridge.py:34`).
> Chuỗi mới: **`3.6-flash → 3.5-flash → 3.5-flash-lite`** (CÙNG thế hệ 3.x). **Đề xuất cũ `3.6 → 3.5-lite → 2.5-flash` đã RÚT LẠI** vì trộn thế hệ làm vỡ **chữ ký suy luận**.
>
> ### ⚠ VÁ CODE BẮT BUỘC (không chỉnh env được)
> Gemini 3 đính **thought signature** vào mỗi `function_call`, **bắt buộc gửi lại nguyên vẹn**, và **từ chối chữ ký của model khác**. `_gen_fallback` (`:76-95`) đổi model **giữa chừng request** trong khi `contents` đã mang chữ ký model cũ ⇒ **400**. Phải **chạy lại request TỪ ĐẦU** khi đổi model. *(Tin tốt: code append **nguyên đối tượng** `cand.content` ở `:1187/:1239/:1247` ⇒ trong CÙNG model chữ ký được giữ đúng.)*
>
> ### 🎯 3 RỦI RO PHẢI ĐO — KHÔNG ĐƯỢC GIẢ ĐỊNH
> **R1 `temperature=0` xung đột** (`:1150`,`:1269`): Gemini 3 khuyến nghị giữ **1.0**, dưới 1.0 *"may lead to looping or degraded performance"* — mà `temperature=0` là lựa chọn **chống bịa cốt lõi**. Phải A/B **riêng biến này**, không đổi cùng lúc với model.
> **R2 `max_output_tokens=8192` là ngân sách CHUNG** cho thinking + câu trả lời (`python-genai#2062`), `thinking_level` mặc định `high` ⇒ nguy cơ **empty-response** (`[[feedback-e2e-test-kpi]]` — đã từng dính).
> **R3** `FunctionResponse` có thể cần trường `id` (`:1193`,`:1230`) — tài liệu chính không xác nhận, **phải thử thật**.
> **Chi phí:** ×5 đầu vào ($1,50 vs $0,30), ×3 đầu ra ($7,50 vs $2,50), **cộng token suy nghĩ tính vào đầu ra** ⇒ thực tế có thể hơn ×3. Chưa đo thật.
>
> ### 📋 THỨ TỰ — **GĐ1 làm được NGAY (offline), GĐ2 CHẶN tới khi có API**
> **GĐ1 (không cần API):** gỡ `2.0-flash` chết · vá `_gen_fallback` chạy-lại-từ-đầu · thêm 404 vào fail-forward · đưa `thinking_level`/`max_output_tokens`/`temperature` ra env · nâng `google-genai` 2.10.0 → mới nhất · mở rộng `tests/test_model_fallback.py`. Cổng: `check.sh` xanh + `test_takeoff_chong_bia.py` 76/76 (**xoá `__pycache__` trước**).
> **GĐ2 (CẦN API):** khói 5 request → **xác minh R1/R2/R3 bằng ca nhỏ TRƯỚC** → A/B 198 câu × `{2.5-flash, 3.6-flash}`.
> ⚠ **BẮT BUỘC chống 429 + checkpoint theo dòng**: `tests/battery_results_pro25.jsonl` **hỏng 127/198 dòng** vì cạn quota giữa chừng và suýt cho kết luận ngược *"Flash giỏi hơn Pro"*.
> **Ngưỡng GO:** `3.6-flash` **không thua** ở trục **bẫy ảo giác** và **không tụt recall**. Thắng tốc độ/tiền mà thua bẫy = **NO_GO**.
> ⚠ **Kỷ luật đo:** đọc tay ≥10 ca trước khi tin số tổng hợp. *Trong chính phiên này phép đo cho **3 kết quả sai liên tiếp** (12,6% trùng khớp · 98/198 "không neo" · "Flash giỏi hơn Pro") — cả 3 đều trông hợp lý* (`[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`).

## 📐 2026-08-06 (nối 3) — **ĐẶC TẢ TOOL #37 CHỐT SAU RED-TEAM** → `DAC_TA_TOOL37.md` · ⛔ CHƯA CODE, chờ user quyết 4 mục
> **wf_689d5254**: tác giả dựng PROTOTYPE chạy được (`D:\Dat-Antigravity\_lat4\proto_khung\`) → 3 góc red-team tấn công code thật (2/3 BÁC ĐƯỢC) → chốt. **Toàn văn đặc tả + 11 bản vá V-A..V-K + thứ tự B0-B7 + 10 tiêu chí nghiệm thu đặt trước: `DAC_TA_TOOL37.md` (gốc repo).** Chi tiết cũng ở mục `muc4-lat-ghep-cuaso-ngansach` của feature_list.
> Tóm tắt: tool MỚI **#37 `doc_bang_ke_khung`** additive (#36 nguyên TỪNG BYTE; van nhường = lát riêng); phân tầng a/b/c + từ chối đúng loại; mỏ neo (rotation, align_point); Decimal nguyên; gate `da_chung_minh` (so_pt≥2 + xen_ke ⇒ F5 còn **9/23 claim, 336/462 ô = 72,7%** — số 81,8% cũ là định nghĩa lỏng); **garble-normalizer 2 phía cho `nhan_chua` = ĐIỀU KIỆN GO**. Red-team bắt nổi bật: **5.359 dải rơi KHÔNG VẾT** toàn corpus (V-C, tiêu chí = 0) · khoá dải round-tuyệt-đối câm trên 01-TD lệch 0.002 (V-D) · khung đọc nhầm **LƯỚI TRỤC NHÀ** thành bảng (V-H) · khung lồng không dedup (V-I). Rổ neo khai đủ 3 chiều: mốc-mm 52→55 · mốc-MÉT 70→85 (+21%) · corpus-wide ~2,5× · phiên đa-lượt ~2× — nguồn nở là Ô THẬT + **×1000 CÓ SẴN của `_is_grounded` (ngoài lát)**; kỷ luật rổ của #37 tự nó đứng vững (0 tham số/prose/đếm/handle lọt).
> **✅ USER ĐÃ CHỐT CẢ 4 (2026-08-06, theo đề xuất — ĐỪNG HỎI LẠI):** ① **LIVE #37 rồi vá ×1000 NGAY SAU** (lát grounding-có-đơn-vị ở mcp_bridge xếp kế tiếp, không hoãn LIVE) · ② trần **giữ 60 mặc định / 200 trần cứng** · ③ V-H lưới trục = **TỪ CHỐI ĐÍCH DANH** (không chỉ gắn cờ) · ④ ưu tiên ngân sách = **trên-xuống + mục lục V-J**. → Thi công B0-B3 đang chạy (`wf_9cfa893f`): đóng băng trọng tài → vá proto 4 cụm (V-C/D/E → V-F/G → V-A/B → V-H/I/J/K, mỗi cụm một lần đo đủ + sweep plateau, thay đổi ngoài kỳ vọng = DỪNG) → red-team vòng 1 trên proto đã vá. B4-B7 (tích hợp + test + cổng + red-team 2) làm SAU khi review B0-B3.

## 🧭 2026-08-06 (nối 2) — VÒNG 2 **NO_GO cả HỌ nối-dài** · VÒNG 3 **thước đọc tay + khung nét** · SỐ TRANH CHẤP đang phân xử
> **Cây SẠCH tại `0a3dfaa` — 0 dòng code sản phẩm bị đụng qua CẢ 3 vòng nghiên cứu.** Chi tiết đầy đủ + mọi con số: mục `muc4-lat-ghep-cuaso-ngansach` trong `feature_list.json` (đã cập nhật trọn). Workflow: vòng 2 `wf_da337a88` · vòng 3 `wf_c635c3e9`.
> **⭐ USER ĐẶT CHUẨN MỚI (2026-08-06, áp cho MỌI việc đọc-số về sau):** *"độ chính xác gần như tuyệt đối — số SAI = lỗi, số THIẾU = lỗi, không 9-bỏ-làm-10"* vì số chảy vào DỰ TOÁN. ⇒ phương án 'NÍN' (chỉ ngừng nói sai) của vòng 2 KHÔNG ĐẠT; mục tiêu là ĐỌC ĐÚNG hoặc TỪ CHỐI RÕ.
> **VÒNG 2 — NO_GO:** cả HỌ luật "nối dài ≤ K×bước" chết (F5: max(đi-tiếp)=5,46 > min(dừng)=0,76 chồng lấn tuyệt đối; K=1,25 làm F5 GIẢM 79,8%→75,4%); lợi ích trên 4 file đích = thuộc tính BỐ CỤC, không phải của luật. 🔴 **Lỗ ×1000 CÓ SẴN trong HEAD** (không do thiết kế nào mở): 1 lượt `nhan_chua='Khoảng cách'` trên C2 → 13/33 mốc mm + **6 câu bịa LỌT** — đòn bẩy ở `_is_grounded`/ANY-GROUNDED, KHÔNG ở tool #36.
> **VÒNG 3 — nền mới:** thước đọc tay **391 hàng/4.283 ô/5 file** (`_lat4/su_that_nen_doc_tay.json`) · khung nét làm biên XÁC NHẬN · **dãy handle KHÔNG phải chữ ký hàng** (3/5 file vẽ theo CỘT) · **C1/C2 là trắc NGANG** — tool đang âm thầm đọc loại bảng sai tên · **biên đúng chưa đủ**: 37% hàng đổi min/max vì ký hiệu vẽ đè (cao chữ 0.15 vs 0.20) · 💡 hướng mới: **số học tự-chứng-minh làm cơ chế đọc** (tách mức y + đẳng thức cộng dồn; O-B chéo).
> **✅ PHÂN XỬ XONG (wf_4ff11f74) — AGENT ĐÚNG NGUYÊN VĂN, số của tôi là ARTIFACT:** 3 bộ trích độc lập trùng 100% per-bảng ⇒ **23/23 khớp đẳng thức (74/74 phương trình, nguyên-cent KHÔNG dung sai) · O-B 97/97 ô · F5 462/462 ô hàng-số tự chứng minh, mục #24 = stub → TỪ CHỐI RÕ**. Nguyên nhân cơ học (tự kiểm tay ở mức entity): chữ cộng dồn viết DỌC có mỏ neo thật `align_point` (1 mức +0.617) nhưng `insert` tụt theo ĐỘ DÀI chuỗi (−0.743/−1.131/−1.520) — dải ±1.0 của tôi chặt cụt 65/171 ô = **lần thứ 10 bộ trích hỏng, hướng BI QUAN, đã xác nhận**. 📌 Bài học mới: TEXT căn lề (halign≠0) thì toạ độ NGHĨA là **`align_point`, không phải `insert`**; tín-hiệu-tách nên dùng cặp (rotation, align_point). Oracle 'không giảm' trên dãy trộn = SAI TẦNG (bắt oan 7/23) — vứt. ⚠ Không overclaim: 1 file/1 nguồn/1 quy ước; phải lặp trên trắc dọc nguồn độc lập. ⏳ TIẾP: đặc tả lát code (khung nét + (rotation, align_point) + đẳng thức nguyên-cent + từ chối rõ; phát hiện bảng thay G4/G7/G10 cho lớp có-khung) → red-team 2 tầng → code. Offline trọn; A/B Gemini chờ billing.

## 🔬 2026-08-06 — TOOL #36 CÓ **HAI** CƠ CHẾ CẮT · thước đo bị cong · lát ghép ĐANG LÀM
> *(cùng phiên với khối ghi "2026-08-05" ngay dưới — tôi ghi lệch ngày, nội dung không đổi.)*
> **HEAD `d4a7c33` · cây SẠCH · suite #36 `35 PASS / 0 FAIL`.** Bản vá dở đã **HOÀN TÁC khỏi cây**, lưu ở `D:\Dat-Antigravity\_lat4\lat4c_WIP.patch`. `feature_list` **86 → 87** (mục mới `muc4-lat-ghep-cuaso-ngansach`). Nghiên cứu: `wf_7d902824-ad4` (2 thiết kế + 3 góc phản biện + chốt), rồi TỰ ĐO THÊM.
>
> ### ① PHÁT HIỆN NỀN — có **HAI** cơ chế cắt, không phải một
> Ngoài trần `_BTD_CAP_TONG=60` (bỏ nguyên cả block) còn **cửa sổ ngang `xmax = 40.0*p`** (`tools_core.py:2418`) **cắt NGANG GIỮA một hàng**.
> **Bằng chứng đọc thẳng `entitydb`** (không qua `self.texts`), file `GD2/10. Cat doc cong D600.dxf`, hàng của nhãn `41E99`: dãy handle **liên tục** `41E9C→41EC2`, bước `x` đúng **2.000 không đứt**, `'1.940'` bên trong cửa sổ và `'1.840'` bên ngoài; cửa sổ kết thúc giữa `x=743.308` và `x=745.308`. ⇒ **min THẬT của hàng là `1.840`, tool đọc ra `1.940`.**
>
> ### ② HỆ QUẢ NẶNG NHẤT — **THƯỚC ĐO BỊ CONG**
> "Sự thật nền" mà mọi bản vá ngân sách dùng để tự chấm điểm lấy bằng cách nâng `_BTD_CAP_TONG` lên rất cao — **nhưng cửa sổ vẫn còn nguyên** ⇒ sự thật nền **thừa hưởng vết cắt**. Đo lại: **10/22 nhãn có sự-thật-nền SAI**, 9 trong số đó thuộc nhóm 13 nhãn từng coi là "vốn đúng". **1 trong 9 nhãn mà cả hai thiết kế chứng nhận "đã sửa đúng" được chấm đậu bằng một con số SAI.**
>
> ### ③ ⛔ HAI THIẾT KẾ NGÂN SÁCH ĐỀU NO_GO (3/3 góc phản biện `bac_bo=true`)
> Cả PA-A (tổng-hợp-theo-nhãn) lẫn PA-B (chia-suất) **mở giấy phép bịa thang milimét** qua hàng `'Khoảng cách (m)'` (0..5 m ×1000 rơi đúng dải 700/1200/2000/5000 mm dễ bịa nhất): A **+17** mốc mới, B **+79**. PA-A còn **giết câu đúng** (6/7 câu trung thực lật sang REFUSE) và trả **0 ô + 0 cảnh báo** ở 6/20 tổ hợp `gioi_han` thấp; PA-B **nhân bề mặt SAI-TỰ-TIN** (nhãn `'Cao trình tự nhiên'` → **31 ô `nho_nhat` mâu thuẫn, đúng 2/31**). Cả hai làm `gioi_han` **chết**.
>
> ### ④ ⛔ **KHÔNG GỘP min/max QUA BLOCK** — bằng chứng từ chính bản vẽ
> A1 có 2 TEXT tiêu đề `'TRẮC DỌC cống D600 (bên phải tuyến)'` và `'(bên trái tuyến)'`; A2 có 3 tiêu đề = **hai cống + một `'TRẮC DỌC KÊNH THỦY NÔNG HOÀN TRẢ'`**. Gộp ra dải `[1.740..1.900]` mà **không cống nào có**. Phép thử an toàn của PA-A ("cặp block rời hẳn") **mù theo cấu trúc** vì hai cống chồng lấn khoảng giá trị. ⇒ hướng đúng là **ĐỊNH DANH BLOCK** (trả tiêu đề + tên mặt cắt layer `tenmatcat`, lệch y ổn định +6.87) — chữ đó **có sẵn trong file mà tool đang giấu**; phải để trong `_vitri` vì `'D600'`/`'C117'` chứa chữ số.
>
> ### ⑤ 🔬 TỰ ĐO SAU KHI CODE THỬ — **vá cửa sổ MỘT MÌNH LÀM TỆ ĐI**
> Nối dài làm hàng dài gấp đôi (15→30 ô) nên trần 60 chỉ đủ **nửa số hàng**: A1 **4→2** (mất luôn nhãn `'đáy cống thiết kế'`), C1 4→2, C2 4→2, A2 4→3; `cat_bot_do_gioi_han` nổ ở file trước đây không nổ. Ghép thêm **chia suất theo hàng** cứu được A1+A2 (4→4) **nhưng C1/C2 vẫn 5→3** vì đói ngân sách còn ở **tầng BLOCK** (block 2→1).
> ⇒ **KẾT LUẬN CÓ SỐ: cửa sổ + ngân sách phải vá CHUNG MỘT LÁT.** Kế hoạch *"ship lát 4-C riêng và TRƯỚC"* của vòng thiết kế **bị chính phép đo này bác**.
>
> ### ⑥ MẶT TỐT đã đo được của vá cửa sổ (lý do vẫn đáng làm)
> Các cặp **`min == max` biến mất** — một hàng cao độ trắc dọc báo `('1.840','1.840')` hay `('3.220','3.220')` gần như chắc chắn là hàng **cụt**; sau vá thành `('1.740','1.840')`, `('3.120','3.220')`. A2 **cả 3 hàng** đều thoát; C2 `tim đường` `(3.200,3.200)→(3.100,3.200)`, `đầu cọc` `(3.000,3.130)→(2.780,3.130)`.
>
> ### ⑦ QUÉT ĐỘ NHẠY — đọc cho đúng
> `_BTD_NOIDAI_SAI` ∈ {0.15, 0.25, 0.35, 0.50, 1.00} cho kết quả **y hệt nhau ở cả 5 mức**. Đọc đúng: dữ liệu **BIMODAL** (khoảng trống hoặc ≈bước, hoặc ≫bước — ranh giới sang bảng kế bên đo được **23,0** so với bước **2,0**), nên ngưỡng gần như không có vai trò. **Không được đọc thành "tôi chọn ngưỡng khéo".**
>
> ### ⑧ CÒN PHẢI GIẢI
> **(a)** `N2`/`R2` ĐỎ vì định nghĩa "neo hợp lệ" chỉ gồm `h['gia_tri']` mà min/max nay lấy từ hàng đầy đủ — phản biện đã đo **code ĐANG CHẠY cũng vi phạm ở 8/20 cấu hình, gồm 3 cấu hình mặc định** ⇒ định nghĩa test hẹp **CÓ SẴN**, phải xử lý tử tế, **không sửa test cho xanh**. **(b)** Corpus **nhúc nhích**: 5 file kích hoạt thay vì 4 — file mới `4. Thoat nuoc mua::2. TD.dxf` (**"TD" nhiều khả năng là trắc dọc ⇒ có thể là RECALL TĂNG THẬT**), **chưa kiểm tay** nên chưa tính là điểm cộng. **(c)** `_BTD_CAP_HANG=30` chưa từng cắn (hàng dài nhất 19 ô) nhưng sau nối dài hàng lên **39 ô** nên **sẽ** cắn; và code cũ `break` **TRƯỚC** `sort(key=x)` nên khi cắn thì 30 ô giữ lại là **tập con TUỲ Ý theo x** rồi min/max tính trên đó — lỗi tiềm ẩn phải vá cùng dòng.
>
> ### ⑨ SỐ BỊ BÁC TRONG VÒNG NÀY — đừng trích lại
> *"C1 min thật là 1.10"* (góc 3) **không sống sót**: đến từ bộ trích **bỏ cửa sổ hoàn toàn** nên vợt sang bảng bên cạnh. Dưới phép nối-dài-đúng-bước thì C1 `'Cao trình tự nhiên'` = `[1.77..4.25]` **không đổi**. Đây là **lần thứ 9** dự án suýt kết luận ngược vì bộ trích hỏng — lần này theo hướng **BI QUAN**.
>
> ### ⏳ VIỆC TIẾP
> Chạy vòng thiết kế cho **LÁT GHÉP** với ràng buộc mới: **mọi con số chi phí của PA-A/PA-B phải TÍNH LẠI** vì hàng đã dài ra.

## 🏁 CHỐT SỔ PHIÊN 2026-08-05 — **ĐỌC KHỐI NÀY TRƯỚC**
> **Việc được giao:** *"nghiên cứu chi tiết và triển khai Lát 4"*. **Kết quả: lát 4 tách đôi — 4a VÁ XONG, 4b NO_GO có số.**
> **CỔNG `[49/49]` PASS exit 0 · 36 MCP tool · `test_cao_do_min_max` 31 → 52 ca · diff từng suite: DUY NHẤT bước [20/49] đổi số, 33/33 suite còn lại giữ NGUYÊN TỪNG CON SỐ** (takeoff 283 khớp baseline — suite duy nhất trong bước 1-15 có gọi `thong_tin_tang`). `feature_list.json` **85 → 86** (72 done · 1 partial · 13 deferred). **KHÔNG bump `PROMPT_VERSION`** (đo `sha256(SYSTEM_PROMPT)`=`239e8b7b…` KHỚP FROZEN). ⏳ **CHƯA COMMIT** — chờ user chốt.
> Nghiên cứu `wf_f5e1a3dd-ace` (5 probe + tổng hợp). Script đo **ngoài repo**: `D:\Dat-Antigravity\_lat4\` (`lat4a_ab.py` trước/sau · `audit_prose.py` sàng tĩnh · `verify_claims.py`/`verify2.py` tự kiểm chứng · `p1_corpus.jsonl` + `p1_control.jsonl` dữ liệu thô).
>
> ### ✅ LÁT 4a — bịt rò rổ neo qua PROSE (lỗi CÓ SẴN, không do lát 4 đẻ ra)
> `cao_do_min_max`/`thong_tin_tang` không ở tuple loại-trừ + `_strip_neo` không lọc chuỗi tự do ⇒ **mọi chữ số trong `ghi_chu`/`ly_do` thành NEO grounding**; ở nhánh 0-marker `_guard_text` là hàng rào **duy nhất** còn hoạt động.
>
> | chuỗi cũ | bơm vào rổ | câu bịa được bảo lãnh |
> |---|---|---|
> | `"kèm 2-3 số thập phân"` | 2.0 · 3.0 | *dài 3 m* · *dày 2 m* · *sâu 3000 mm* |
> | `"(vd 'CH - 2.700')"` + `"(vd 'cốt - 14.260')"` | 2.7 · **14.26** | *Cao độ đáy cống là 14,26 m* ← chữ ký id135 |
> | `"(±0.000, +3.600...)"` | 0.0 · **3.6** | *Chiều cao tầng điển hình là 3,6 m* · *3600 mm* |
> | `"(vd 'cột C1 cao 3.6m')"` | 1.0 · 3.6 | — |
> | `"⚠ Có %d marker…"` | số ĐẾM | — |
>
> **Vá bằng cách giữ NGUYÊN nghĩa**: viết số **bằng chữ** (`"hai đến ba chữ số thập phân"`) hoặc **placeholder** (`n.nnn`, `<số>`). Rổ neo: 0-marker `[0.0,2.0,3.0]`→`[0.0]` · `thong_tin_tang` 0 mốc `[0.0,3.6]`→**RỖNG** · **6 câu bịa lật LỌT→CHẶN**.
> ⚠ **`thong_tin_tang` nguy hơn ca 14.26** (3.6 = chiều cao tầng điển hình = số model dễ bịa nhất). Đây là chỗ **nới phạm vi** so với 2 lỗi báo cáo ban đầu — lý do bằng số, đã báo user.
> **Đối chứng đủ 4 loại:** nhánh G3 vốn sạch ⇒ **0 số đổi** · `77,77` CHẶN 2 phía · số đọc thật `-1.85/10.8/-9.12/3.3` và `'2.700'` có thật **vẫn lọt** · `_prose_digits` phân biệt prose vs dữ liệu. **Tự kiểm ngược: gỡ vá ⇒ đúng 15 ca đỏ**, đối chứng vẫn xanh.
>
> ### ⛔ LÁT 4b (routing-nudge) — NO_GO, ĐỪNG MỞ LẠI KHI CHƯA CÓ DÂN SỐ MỚI
> **(a) Trần tuyệt đối = 2 bản vẽ.** 123 file nạp được, bảng chéo: **A=2** (nudge hữu ích) · **B=52** (trỏ vào chỗ trống) · **C=2** (nudge không bao giờ bắn vì `cao_do_min_max` thành công) · D=67. Bắn 54 trúng 2 = **3,7%**; ngưỡng tiền lệ `≥3` **bất khả thi về số học**.
> **(b) Đích đến trả số SAI ở lệnh gọi mặc định:** `doc_bang_trac_doc()` → `1.800` (handle 42E96); `nhan_chua='đáy cống'` lộ **2 block**, min thật `1.740` (handle 4291B) — ngân sách `_BTD_CAP_TONG=60` bị block đầu tiêu hết. **Tool KHÔNG im lặng** (lộ bằng 4 đường: `khong_day_du` · `_bi_cat` · `canh_bao` · ghi_chu *"TUYỆT ĐỐI không kết luận nhỏ nhất/lớn nhất của TOÀN bảng"*), **nhưng hàng rào QUAY NGƯỢC**: `1,800 m` **LỌT**, `1,740 m` **CHẶN** ⇒ nudge **thành công** có thể làm hệ **tệ đi**.
> **(c)** Cả 2 file thắng nằm ngoài mọi corpus đã cấu hình (battery 3 file cố định, 0 câu trắc dọc).
> **Nếu sau này làm:** 0 chữ số bắt buộc (`'tool #36'` bơm 36.0 → E2E cho câu bịa *"…là 36 m."* đi trọn vẹn; dùng TÊN `doc_bang_trac_doc`) · cấm cụm ∈ `_REFUSAL_MARKERS` (`_guard_text` **thoát sớm, bỏ kiểm cả bài**) · cấm khẳng định bản vẽ CÓ dữ liệu (E2). Chi phí nudge-**có-đo** rẻ: median **1,39 ms** (0,172% thời gian nạp).
>
> ### 🔥 VIỆC CHỜ — phiên sau
> ① **Vá cắt ngân sách XUYÊN BLOCK của #36** (đề xuất thay cho 4b): offline, 0 API, là **điều kiện cần** cho mọi nudge sau. Đo trước/sau trên 4 file kích hoạt — cả 4 đều chạm trần nên vá có thể làm im lặng cả 4. · ② Lỗ **số ĐẾM** (`so_marker`, `so_bang`…) — lát riêng, vá sẽ dịch số nhiều suite · ③ **5 hàm** bộ sàng tĩnh nêu còn prose mang chữ số (`liet_ke_so_luong` chứa **đúng chuỗi `"vd 'D1'"` mà `b236b7e` đã gỡ ở `tra_cuu_so_luong`**, `hoc_quy_uoc`, `phan_loai_tin_hieu`, `_resolve_lo_cua`, `_gan_cc`) — **phải chạy thật để xác minh**, quét tĩnh có thể báo oan · ④ echo `tu_khoa` ở `tim_kiem` (A/B riêng) · ⑤ PA-2/PA-3 đọc bảng tổng quát (cần lát-0 riêng) · ⑥ nhóm C vẫn hoãn.
> **Điểm mù chưa đo:** 16/92 file corpus (17,4%) chưa bao giờ quét vì trần 45MB — soi tên thì không file nào mang chữ ký `Cat doc`/`CN duong`, nhưng **thấp không phải là đã đo**.
>
> ### 📌 BÀI HỌC
> **(a) Đi đo tính năng A lại tìm ra lỗi của tính năng B — và lỗi đó đáng giá hơn.** Lát 4 ra NO_GO, nhưng đường đi tới NO_GO lộ 5 chuỗi rò neo đang chạy LIVE.
> **(b) Bộ đo agent hỏng, bắt được nhờ số quá đẹp:** `NFD` không gỡ được `Đ/đ` (U+0110/0111 **không có canonical decomposition**) ⇒ báo *"0/76 file có nhãn trắc dọc"*. `[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`
> **(c) Không nhận nguyên xi kết luận agent:** phần **số** của agent đúng (1.800 vs 1.740), phần **mức nghiêm trọng** sai (bảo tool im lặng, thực tế lộ 4 đường) — phân biệt được hai cái đó đổi hẳn khuyến nghị.

## 🏁 CHỐT SỔ PHIÊN 2026-08-02 — **ĐỌC KHỐI NÀY TRƯỚC**
> **HEAD `0c1d710` == origin · tree SẠCH · LIVE `0c1d710` verify đủ 4 mục** (prompt `239e8b7b…` KHÔNG đổi · kb `e55ac112…` KHÔNG đổi · `/health` ok `ram_mb` 136,0 · trang chủ HTTP 200).
> **CỔNG `[49/49]` PASS · 36 MCP tool · tổng ca 1.627 → 1.680 · 48 → 49 bước · 0 regress ở MỌI lát.** `feature_list.json` **79 → 85 mục** (71 done · 1 partial · 13 deferred).
> ⚠ **pytest VẪN crash** (`ValueError: I/O operation on closed file` → `no tests ran`) — đã kiểm lại cuối phiên, KHÔNG phải nhớ. Cổng là `check.sh`. **KHÔNG có `specs/specs.json`** → `feature_list.json`. (Hai điều này lặp mỗi phiên, checklist dòng 8 đã ghi.)
> **7 commit** push+deploy+verify: `0cb25e6` vá audit · `dabcaac` docs F1 · `7030aa6` PA-0 · `6b7c2b9` VNI tầng 2 · `b366161` docs · `755d053` lát 0 · `0c1d710` lát 1 tool #36.
>
> ### 5 VIỆC LÀM ĐƯỢC
> | việc | kết quả ĐO ĐƯỢC |
> |---|---|
> | **Vá `dwgconv` audit=1** | cứu **10/147 file** khỏi "không đọc được", hỏng thêm **0**; trong đó có `chinhcaodo.dwg` của TB6 (988 chữ, **200 marker cao độ**) — bug **chỉ người dùng gặp**, dev không đi qua đường đó |
> | **VNI vớt tầng 2** | vớt **78/79 chuỗi**, 0 vớt-sai, **0 phá `TOÀ/HOÀ`**, 0 lệch số |
> | **PA-0 (rổ neo rỗng)** | chốt **DƯỚI NGƯỠNG** (1 hiện tượng < 3) ⇒ 0 đổi hành vi; đóng vùng mù đo lường + tripwire |
> | **Mục 4 lát 0** | 4/142 file kích hoạt đều đúng, **0 file kiến trúc/kết cấu**, 0 nhãn rác, 0 số âm |
> | **Mục 4 lát 1 — tool #36** | đọc được `'cao độ đáy cống'` → `1.800…1.900` kèm handle, thứ mà `cao_do_min_max` trả 0 kết quả |
>
> ### ⛔ 3 HƯỚNG ĐÓNG BẰNG SỐ TRONG PHIÊN — ĐỪNG MỞ LẠI
> **F1 bộ đối tác** (thiết kế sâu nhất −4,10m; 2 file đạt −5m là **hố khoan địa chất**, khác hệ) · **`Ø` vào `_SIG`** (126/152 ứng viên là ký hiệu đường kính thật ⇒ hại/lợi 4:1) · **gate "thẳng hàng"** cho detector bảng (rác 1,000 vs bảng thật 0,806, không ngưỡng nào tách).
>
> ### 📌 BÀI HỌC MANG SANG PHIÊN SAU
> **(a) TEST TỰ VIẾT KHÔNG THAY THẾ ĐƯỢC RED-TEAM** — 23 ca PASS hết mà **5 lỗi CAO** lọt, **3 do chính bản vá đẻ ra**; thẩm định ghi thẳng *"23 ca test hiện có KHÔNG bắt được một phát hiện nào"*. `[[feedback-red-team-khong-thay-the-duoc]]`
> **(b) `.pyc` CŨ CHO CỔNG KẾT QUẢ SAI** — vá 1 ký tự (cùng size) + khôi phục cùng giây ⇒ nạp bytecode bản đã gỡ vá; **chiều ngược = CỔNG XANH OAN**. Luôn xoá `__pycache__` trước cổng. `[[feedback-stale-pycache-lam-cong-sai]]`
> **(c) DANH SÁCH KHOÁ CỨNG LÀ BỀ MẶT DỄ QUÊN** — `_KHOA_HANDLE` hỏng đúng 2 lần, cả hai im lặng; nay lọc theo hình dạng tên.
> **(d) Bộ đo hỏng 6 lần trong phiên, tự bắt hết** — nổi bật: cache dùng basename **gộp 20 file trùng tên** khiến cả một vòng sweep chạy trên dữ liệu lai (bắt vì D600 = 1112 = 496+616).
>
> ### 🔥 VIỆC CHỜ — phiên sau
> ① **Lát 4 routing-nudge**: `cao_do_min_max` nhánh 0-marker → trỏ tool #36. Không đụng SYSTEM_PROMPT (chỉ `ghi_chu`) nhưng **BẮT BUỘC A/B** per-case + giữ từ chối trên 17 bẫy · ② echo `tu_khoa` ở `tim_kiem` (lỗi có sẵn, A/B riêng) · ③ trần công việc O(block×chữ) cho #36 (sort+bisect, giữ nguyên ngưỡng ⇒ số không đổi) · ④ **PA-2/PA-3** đọc bảng tổng quát cho id37 — **phải có lát-0 riêng**, gate PA-1 KHÔNG dùng lại được · ⑤ mục 3 `Ü` (có cách an toàn, lợi ích 49 chuỗi/2 file, **chưa đáng** — chỉ làm nếu user muốn dọn danh sách) · ⑥ **nhóm C vẫn hoãn**.
> **Chờ file ngoài:** F1 — cao độ **ĐÁY THIẾT KẾ** ≤ −5m (móng cọc / tầng hầm / trạm bơm; **hố khoan địa chất KHÔNG dùng được**) · F2 bảng bóc khối lượng làm tay.

## 🏁 CHỐT SỔ 2026-08-02 (nối 2) — (lát trước cùng ngày)
> **HEAD `6b7c2b9`** (VNI vớt tầng 2) ← `7030aa6` (PA-0) ← `dabcaac` (docs F1+audit) ← `0cb25e6` (vá audit). check.sh **[48/48] PASS · tổng ca 1.630 → 1.633 → 1.645** (PA-0 +3, VNI +12) · 35 MCP tool · 0 regress — mỗi lát diff từng suite: **DUY NHẤT** suite của lát đó đổi. `feature_list.json` **80 → 82 mục** (70 done · 1 partial · 11 deferred).
>
> ### ✅ MỤC 1 (VNI 9,8%) — XONG: vớt tầng 2 bằng BẰNG-CHỨNG ÂM TIẾT (`wf_666cedfd`, GO/GO_WA×2)
> Nhánh `elif` thứ ba `_vni_recovery` + bộ kiểm âm tiết `_la_am_tiet` (~160 dòng, thuần luật, nội tuyến `vntext.py`). Token **G** (thô vô-nghĩa → giải hợp lệ) / **A** (cả hai hợp lệ — đi kèm, KHÔNG tự kích) / **XẤU** (chặn cả chuỗi). **Bắn ⟺ ≥1 G và 0 XẤU** ⇒ `TOÀ NHÀ HOÀ` toàn-A không bao giờ bắn.
> **Số:** quần thể đo lại = **79 chuỗi/181 lượt/9 file** · vớt **78/79 (98,7%), 0 vớt-sai** (đọc tay 100%) · phá-chữ-đúng **0** (584 chuỗi bảo vệ byte-identical) · **0 lệch số, 0 mẫu Ø hỏng** · sweep old-vs-new trên cây thật ra khớp **từng con số** · hiệu năng to_unicode **+9,3%**. `test_vni` 43→**55**; tự kiểm ngược: vô hiệu recovery → **đúng 8 ca mới đỏ**.
> **Giới hạn khoá bằng test:** `E3b` cặp=1 (`QUY CAÙCH` chịu sót — hạ ngưỡng phải **ĐO LẠI**, số "phá 316" cũ đo trên gate không-có-tầng-âm-tiết) · `E3d` `T.CHIEÀU` (dấu chấm nội bộ, 1 lượt) · `E3e` residual chuỗi TRỘN Việt-đúng+VNI (0 ca corpus, đồng nhất nhánh cứng hiện hành) · **lớp Ì/Í oan (~71 chuỗi) = LÁT RIÊNG, đừng trộn**.
>
> ### ✅ MỤC 2 (rổ neo rỗng) — CHỐT DƯỚI NGƯỠNG, chỉ làm PA-0 đo-only (`wf_06b6cf5e`, 3 verify GO_WA)
> **832 lượt battery → 179 REFUSE → oan thật 1 hiện tượng (id69) < ngưỡng ≥3 ⇒ KHÔNG đổi hành vi.** id139 refuse GẦN ĐÚNG (ky_vong đòi "phải nói rõ không có"). **⛔ PA-2 (A3-kho-ký-hiệu) = NO_GO CẤU TRÚC — đừng đề xuất lại:** kho cấm chữ số toàn chuỗi mà guard chỉ giết câu có số ⇒ tập cứu RỖNG; bản ngây thơ dính lỗ ECHO tự-cấp-phép câu bịa id135 (đã đo). PA-1 delta gần rỗng (hằng LIVE đã có lời mời hỏi lại). **Vùng mù thật = 117/179 hàng REFUSE legacy thiếu trường.**
> **PA-0 đã LIVE trong `7030aa6`:** 2 seam battery LUÔN BẬT · `answer_truoc_guard` + per-call `{tool,args,rong,co_so}` chỉ ở seam · K4 đóng băng ĐẲNG THỨC tuple loại-trừ == 4 tên (thêm tool #36 PHẢI đỏ) · K5/K5b cấm rò vào `mcp_bridge.py`. **TRIPWIRE:** run mới đủ trường ra ≥3 hiện tượng mới mở lại; công cụ KHÔNG được là PA-2.
> **⏳ CHỜ USER QUYẾT:** entry kho KHÔNG-số `Ø/phi = ký hiệu đường kính thép tròn` → id69 miss→hit (đã đo 3 mắt xích: `_KB_PREFIX_RE` bắt `Ø` từ `Ø10` · khoá sập `ø` · kho hiện 0 entry). Giá: đổi `kb_hash` (re-freeze + verify).
>
> ### 📌 VIỆC NHỎ GHI SỔ (chưa làm)
> ① Convert lại **3 file cache `_khao_sat/_dxf` hỏng** `DXFStructureError` (di sản audit=0; gồm `chinhcaodo.dxf` — file mà bản vá audit hôm nay cứu). ② Bài học `.pyc` cũ làm cổng sai — memory `[[feedback-stale-pycache-lam-cong-sai]]`, LUẬT: sau mọi vòng gỡ-vá-rồi-khôi-phục phải xoá `__pycache__` trước khi chạy cổng.
>
> ### ✅ MỤC 4 — LÁT 1 XONG: **tool #36 `doc_bang_trac_doc` LIVE** (red-team 5 lỗi CAO đã vá)
> **Chiều cao chữ:** chọn đọc lại `self.doc.modelspace()` lúc gọi tool (đo **13ms/8.442 chữ** = 0,12% thời gian nạp) thay vì thêm trường vào `_extract` ⇒ **0 suite bị ảnh hưởng**.
> **🔴 RED-TEAM (`wf_cd35e271`, 4 góc + thẩm định): 11 phát hiện xác minh, 5 CAO — và vòng thẩm định ghi rõ "23 ca test tự viết KHÔNG bắt được phát hiện nào".**
> **3 lỗi do CHÍNH bản vá đẻ ra:** ① `loc_nhan` ngoài `_vitri` ⇒ tham số **model tự chọn** vào rổ neo — `nhan_chua='-600'` bơm **−600** (không tồn tại trong file) và **lật 2 câu bịa cao-độ-âm từ CHẶN sang LỌT** (đối chứng `'600'` không bơm ⇒ phân biệt được) · ② cap 60 `break` **CÂM** ⇒ giấu chính giá trị `1.740` mà docstring nêu làm lý do tồn tại; GD2 giấu **94,5%** giá trị, 0 cảnh báo · ③ min/max tính trên tập **ĐÃ CẮT** ⇒ `gioi_han=12` báo 2.930 thay vì **2.710**, không cảnh báo, số sai nằm TRONG rổ neo nên guard không bắt = **SAI-TỰ-TIN (I3-U L1)**.
> **2 lỗi CÓ SẴN:** ④ `handle_khong_khop` ngoài danh sách cứng `_KHOA_HANDLE`, giá trị là **chuỗi tuỳ ý do model cấp** — truyền `'-13.7'` ⇒ **câu id135 từ CHẶN sang LỌT** · ⑤ echo `tu_khoa` ở `tim_kiem` — **CHƯA VÁ, cần A/B**.
> **✅ Đã vá 4 CAO + 3 TRUNG**, đáng chú ý: **`_strip_handle` đổi từ DANH SÁCH CỨNG sang lọc theo TÊN KHOÁ** (`handle_*`/`*_handle`/`*handles`) — danh sách cứng đã hỏng đúng 2 lần, cả hai IM LẶNG. **Tự kiểm ngược:** chỉ thêm 1 khoá bị loại (`anchor_handle`, đúng là handle); rổ neo 5 tool chính **không đổi một số nào** (11/11 · 20/20 · 30/30 · 19/19 · 7/7).
> **Sau vá:** min/max **bất biến 2.710** mọi `gioi_han`; rổ mỗi lượt ⊆ giá trị đọc được của **chính lượt đó** (⚠ không so chéo giữa các lượt — lượt không-lọc bị cap che nên so chéo báo động giả); `nhan_chua='đáy cống'` **lấy lại `1.740`**.
> **Test 23 → 35 ca** (11 ca `[R]` khoá từng lỗ + đối chứng R7b). **Gate `[49/49]` PASS · 36 MCP tool · 1.645 → 1.680 ca · diff: DUY NHẤT suite #36 đổi.**
> **⏳ Còn ghi sổ:** echo `tu_khoa` (A/B) · O(block×chữ) chưa có trần (đề xuất sort+bisect, giữ nguyên ngưỡng) · handle trong CHUỖI `ghi_chu` của `tinh_dai_luong` (sửa = dịch số nhiều suite) · lát 4 routing-nudge.
>
> ### ✅ MỤC 4 — LÁT 0 (CỔNG DETECTOR) XONG · gate chốt bằng số
> Script đo ở `D:\Dat-Antigravity\_lat0\` (ngoài repo, **0 dòng code sản phẩm bị chạm**).
> **KẾT QUẢ trên 142 file: 4 file kích hoạt, TẤT CẢ là trắc dọc đường THẬT; 0 file kiến trúc/kết cấu/hạ tầng (rachmop IM)** ⇒ tiêu chí FAIL của lát 0 **ĐẠT**. Đọc tay toàn bộ nhãn (104 lượt): **9 nhãn duy nhất, 0 nhãn rác**. **520 giá trị, 0 SỐ ÂM** ⇒ 0 nguy cơ id135.
> **⛔ `G8` (thẳng hàng) = NO_GO CÓ SỐ — GỠ khỏi gate:** SAI HƯỚNG — rác thẳng hàng **hoàn hảo 1,000** (bảng mẫu tô `ansi31`/`ar-conc`) còn bảng trắc dọc thật chỉ **0,806** (hàng "khoảng cách" ghi GIỮA hai cọc); quét ngưỡng 0,50–0,90 **không có ngưỡng nào tách được**.
> **✅ Hai gate thay thế, tham số chốt bằng số:** **G10 mật độ** median giá trị/hàng **≥ 12** (đích min 15/median 18 · nhiễu median 2 ⇒ biên tách 8→15; **≥18 mất 2/5 block đích, KHÔNG được nâng**) · **G9 cùng-bậc-độ-lớn ở MỨC HÀNG** (max/min ≤ 10) loại ghi chú giả dạng bảng (`[4,5,1,150,200,8150]`) mà giữ trắc dọc.
> **📌 3 lỗi bộ đo tự bắt:** G8 cài theo giả định "cột cách đều" (trắc dọc cách theo địa hình) → detector chết ở chỗ phải sống · **cache dùng basename → gộp 20 file TRÙNG TÊN**, sweep chạy trên dữ liệu LAI (bắt vì D600 = 1112 = 496+616) · 4 cặp còn lại là **bản sao cùng file ở 2 thư mục** → nhân đôi mật độ, có thể cho nhóm phải-im LỌT OAN; dedup bỏ 21.786 bản ghi.
> **⏳ LÁT 1 (code tool #36) đủ điều kiện vào việc.** ⚠ Việc CHƯA giải: `self.texts` **không có chiều cao chữ** mà G7/QX đều cần — lát 0 đọc thẳng từ entity DXF; lát 1 phải quyết lấy `h` ở đâu trong sản phẩm (thêm trường vào `_extract` = chạm hàm nóng, hay đọc lại lúc gọi tool).
>
> ### 🔥 MỤC 4 — NGHIÊN CỨU NỀN (`wf_f79497a7`, GO_WA ×3), KẾ HOẠCH 5 LÁT
> **PA-1 = tool #36 `doc_bang_trac_doc`** (additive 100%, không sửa `cao_do_min_max`/`_extract`). Số nền: bảng trắc dọc cấu trúc hàng RÕ RỆT — **861/861 phép gán đọc tay đúng** (828/828 D600 + id37 3/3 + KC 30/30), prototype **1.062 cặp / 0 sai**, plateau eps 0.35-0.60×p; 2 check FAIL THẬT lộ mâu thuẫn NGUỒN (Km 249.40 vs 259.40) ⇒ đo không tautology. **Rổ neo: CÓ VÀO** (verbatim+handle; chiều ngược giết câu đúng 2/2 file) — 10/10 đòn bịa id135 vẫn REFUSE nhờ khớp-CÓ-DẤU.
> **⛔ LÁT 0 LÀ CỔNG SỐNG CÒN, làm TRƯỚC MỌI CODE:** detector lỏng đã đo ra thảm hoạ — KT **67 block/938 số FP**, rachmop 1 block sai nhãn **bơm 4 NEO ÂM verbatim**. Lát 0 = sweep gate G7/G8 toàn corpus 92 file + đọc tay render KT/KC/P9/rachmop; FAIL = kích hoạt trên KT/KC/P9. **Điều chỉnh bắt buộc đã ghi đủ trong `feature_list` mục `doc-bang-theo-vi-tri-pa1-ke-hoach`** (6+ gate cấu trúc không-keyword · strip metadata `_vitri` vào `_strip_neo` TRƯỚC khi code · cap ≤60 XUYÊN block + `nhan_chua=` · per-call không index bền · QX cục bộ ≤2× chiều cao chữ · nghiệm thu 3 đòn bịa/file). Journal đầy đủ: `wf_f79497a7-57b`. Lát 4 (routing-nudge) TÁCH RIÊNG, phải A/B.
> **Việc nhỏ đã xong thêm:** cache `chinhcaodo.dxf` convert lại qua dwgconv đã vá (0,23MB cụt → 8,12MB, 988 chuỗi/200 marker khớp số A/B) — corpus cache **92/92 file thật đọc được**; 2 file "hỏng" còn lại ở `_uploads` chỉ là stub 50 byte của test cũ. · Mục 3 (`Ø/Ü`) hoãn có cơ sở · Nhóm C không đụng · Chờ user quyết: entry kho `Ø/phi` (id69).

## 🏁 CHỐT SỔ 2026-08-02 (nối) — (lát trước cùng ngày)
> **commit `0cb25e6` · ⏳ CHƯA PUSH** (lệnh push bị bộ phân loại quyền của Claude Code chặn — user tự chạy `git push origin main`, rồi verify LIVE). tree chỉ còn docs. **check.sh `[48/48] PASS` · 35 MCP tool · 0 regress · tổng ca 1.627 → 1.630.** Diff từng suite: **DUY NHẤT** `dwgconv` 10→13, mọi suite khác giữ nguyên **từng con số**. `feature_list.json` **79 → 80** (68 done · 1 partial · 11 deferred).
>
> ### ⛔ F1 = **KHÔNG ĐẠT** — đừng dùng bộ này chốt id135
> Đối tác gửi 57 file .dwg (2 đơn vị tư vấn Hải Dương, 27/07/2026). Phần **thiết kế** sâu nhất **−4,10 m** (Bể PCCC) · −3,95 (Trạm XLNT) ⇒ **vẫn dưới −5m** (TB6 = −2,49m).
> Hai file đạt ngưỡng là **KHOAN ĐỊA CHẤT**: `MC KDC Truc Khe` **−54,30m**, `Tru KDC Truc Khe` **−30,00m** — đọc tay quanh chính handle sâu nhất thấy `'Độ sâu hố khoan - m'` · `'(Depth of borehole)'` · `'(Layer depth)'` · `SPT16` ⇒ **độ sâu KHẢO SÁT, KHÁC HỆ**, đúng loại từng làm `cao_do_min_max` KT trôi −2.1 → −94.44. **Dùng nó tuyên bố "đậu" = lặp lại đúng lỗi đã phải rollback 2026-07-24.**
> **→ Khi đi xin file lần sau PHẢI nói rõ: cần cao độ ĐÁY THIẾT KẾ (đáy cống/đài cọc/bể ngầm) ≤ −5m; HỐ KHOAN ĐỊA CHẤT KHÔNG DÙNG ĐƯỢC.** (Bản `YEU_CAU_FILE_HA_TANG_gui_doi_tac.txt` hiện **chưa** loại trừ điều này — nên sửa trước khi gửi lại.)
> 📌 **Bộ trích của tôi hỏng lần thứ 8:** quét thô đọc `'29.5-29.95'` (khoảng độ sâu mẫu) thành −29,95 ⇒ báo oan "engine bỏ sót". **Engine ĐÚNG.**
>
> ### ✅ VÁ: `dwgconv.py:97` audit `"0"` → `"1"` — bug NGƯỜI DÙNG gặp mà DEV không thấy
> `.dwg` lỗi cấu trúc + audit=0 ⇒ ODA **vẫn sinh** `.dxf` nhưng **CỤT** (thiếu `ENDSEC`) ⇒ `outs` không rỗng ⇒ hàm **trả về file hỏng KHÔNG BÁO GÌ**.
> ⚠ So sánh đầu **không sạch** (đổi recurse + audit cùng lúc) — **đã cô lập biến** rồi mới kết luận.
> **A/B 148 file** (92 corpus + 56 mới), chỉ đổi audit: **cứu 10/147 = 6,8%** · **hỏng thêm 0** · 121/123 file **số y hệt** · 2 file lệch **duy nhất `tong_doi_tuong`** (cao độ/chữ/dim/thép/marker **giữ nguyên**, kể cả −54,30) · 14 file cả hai lỗi = **trần 45MB của chính dự án**.
> **Giá:** +0,47s/file (+27,5% tổng); file 36,33MB: 24,3s → 30,4s (timeout 600s); dxf **cùng kích thước** ⇒ không phình file lành.
> 📌 **Vì sao chưa từng lộ:** 10 file được cứu có **`chinhcaodo.dwg` của TB6** (988 chữ, **200 marker cao độ**) — corpus **không có bản `.dxf`**, dev luôn dùng `.dxf` sẵn nên **không đi qua `dwgconv.py`**; chỉ **upload .dwg** mới đi.
> **Test `[G]`** khoá cờ audit (10→13). Tự kiểm ngược: hạ về `"0"` → **đúng ca đó đỏ**, hai ca kia xanh.
>
> ### 📌 BÀI HỌC MỚI — `.pyc` CŨ CHO CỔNG KẾT QUẢ SAI
> Cổng lần đầu sau vá báo **FAIL**, chạy tay cũng FAIL ⇒ trông y hệt bug thật. Thực ra vá **1 ký tự** nên file **cùng size**, khôi phục **cùng giây** (`.pyc` …**343** vs `.py` …**423**) ⇒ Python nạp bytecode **bản đã gỡ vá**. Xoá `__pycache__` → PASS.
> ⚠ **Chiều ngược lại cho CỔNG XANH OAN mà không có gì báo.** ⇒ **LUẬT: sau mọi vòng gỡ-vá-rồi-khôi-phục, xoá `__pycache__` TRƯỚC khi chạy cổng.** `[[feedback-stale-pycache-lam-cong-sai]]`
>
> ### ⏳ VIỆC CHỜ
> ① **push + deploy + verify** bản `0cb25e6` (user chạy) · ② `dwgconv.py:104` vẫn **trả file cụt im lặng** nếu ODA sinh `.dxf` hỏng — audit=1 làm nó **không xảy ra trên 147/147**, nhưng cơ chế còn nguyên, **cần đo riêng** · ③ **F1 vẫn chờ file** đúng loại · ④ 56 file đối tác **chưa nhận vào corpus** (user chốt để sau); dữ liệu đo giữ tại `D:\Dat-Antigravity\_f1_check\` (6,06 GB) · ⑤ **ca thật cho R3**: `Cat doc cong D600` có 24–36 lần "cao độ", 8 lần "đáy cống", nhưng `cao_do_min_max` = **0 marker** vì bảng trắc dọc ghi cao độ **KHÔNG DẤU**.

## 🏁 CHỐT SỔ CUỐI PHIÊN 2026-08-01→08-02 — (phiên trước)
> **HEAD `7544bdf` == origin · tree SẠCH · check.sh `[48/48] PASS` · 35 MCP tool · 0 regress · tổng ca 1.467 → 1.627 (+160) · check.sh 42 → 48 bước.**
> **LIVE `45acd2f`** verify (lần thứ 7 trong phiên): prompt `2026.07.27-kb-l3` hash `239e8b7b…` **KHÔNG đổi** · kb `e55ac112…` **KHÔNG đổi** (không lát nào chạm SYSTEM_PROMPT/kho kiến thức ⇒ **không cần A/B**) · `/health` ok · `ram_mb` 135,5 · trang chủ HTTP 200 đủ 4 chuỗi.
> `feature_list.json` **69 → 79 mục** (66 done · **1 partial** · 12 deferred). **13 commit** push+deploy+verify từng cái.
> ⚠ **pytest VẪN không chạy được** (`ValueError: I/O operation on closed file` → `no tests ran`) — cổng là `check.sh`. **KHÔNG có `specs/specs.json`** → dùng `feature_list.json`. (Đã kiểm lại cuối phiên này, không phải nhớ.)
>
> ### 5 VIỆC VÁ LIVE (đều nhóm A)
> | việc | commit | hiệu quả ĐO ĐƯỢC |
> |---|---|---|
> | **A3 mã-định-dạng** | `af0c879` | bớt **11.597 hit ảo**; kênh lớn nhất là `%%C` (hỏi "cột C1" trả về mọi ghi chú thép Ø10/12/16). Cứu 437 ký hiệu thép: `(D1)(D2)(D3)` trước đây **sập thành `(D)`** |
> | **Tool #35 `doc_chu_trang_in`** | `349e82a` | mở đường đọc chữ TRANG IN; kho thật **18 file / 2.180 lượt / 621 chuỗi** |
> | **A2 rổ-neo-rỗng** | `a61472d` | thôi khẳng định SAI SỰ THẬT về bản vẽ (0,18% lượt) |
> | **A3 trích-dẫn** | `e57ee22` | lấy lại câu ĐÚNG bị guard xoá oan (20/621 = 3,2% chuỗi) |
> | **BẢNG MÃ VNI** | `45acd2f` | **cứu 852 chuỗi/15 file**; E2E: *"phòng"* **0→33**, tổng 12 từ khoá **11→194** trên file gốc của vấn đề |
>
> ### ⛔ 7 HƯỚNG ĐÓNG BẰNG SỐ — ĐỪNG MỞ LẠI (mỗi cái có khối riêng bên dưới)
> `Φ` (tiền đề SAI: `_norm('Φ10')==_norm('Ø10')` sẵn) · `Ø/Ü` vào `_SIG` · cờ trang in khớp-từ-khoá · "câu tổng-hợp bị giết" (thực ra **model phá luật `_P_R2`**) · A2 phương-án-rộng (**làm vỡ `test_grounding_guard:137`**) · A2 phương-án-nhắc-lại (giả định 0 phép đo) · cờ "số do máy tự tính" (1 hiện tượng < ngưỡng 3).
> **📌 Ít nhất 3 trong 7 hướng đó, nếu code thẳng, sẽ MỞ LẠI đúng lớp lỗi id135.**
>
> ### 🔥 BƯỚC TIẾP — ứng viên, **CHƯA chốt** (user chọn)
> ① **Lấy lại 9,8% chuỗi VNI bỏ sót** (93/945: `THEÙP SAØN` · `BEÂ TOÂNG LOÙT` · `CHI TIEÁT DAÀM`) — cần cách phân biệt `TOÀ/HOÀ` an toàn (có thể cần từ điển âm tiết). Ca `E3` của `test_vni` đang khoá hành vi hiện tại.
> ② **`Ø/Ü` vào `_SIG`** — *hoãn có cơ sở*, **LÀM ĐƯỢC** nhưng đo ra chỉ 132 chuỗi = 0,0103% corpus, nội dung **không phải khối lượng**; nếu làm phải tách **`Ü` riêng, `Ø` riêng**.
> ③ **Rổ neo rỗng ⇒ nói sai sự thật** — A2 mới hạ "nói dối" xuống "trung thực"; danh sách loại-trừ vừa đi **3→4 tool** nên bề mặt RỘNG THÊM.
> ④ Nhóm C (RAM/upload) vẫn **HOÃN tới cuối dự án** (tốn tiền túi).
> **Chờ file ngoài:** F1 bản vẽ hạ tầng sâu ≥−5m từ đơn vị KHÁC · F2 bảng bóc khối lượng làm tay của kỹ sư.
>
> ### 📌 BÀI HỌC MANG SANG PHIÊN SAU — SỔ SAI SÓT CỦA CHÍNH TÔI (tự bắt hết)
> **7 bộ trích/bộ kiểm hỏng** (2 tautology · 1 ca test không phân biệt được · 1 cắt cụt 400 chuỗi/file · **1 sai ĐƠN VỊ + 1 sai MẪU SỐ đã kịp vào tới CODE**) · **7 lần assert sai mà code ĐÚNG** (khuôn lặp: giả định một câu kích guard trong khi `do_luong` rỗng nên guard **thoát sớm**) · **3 giả thuyết sai** · **1 tác dụng phụ do chính bản vá**.
> 🔴 **Lần nguy hiểm nhất (VNI): bản đo báo "hỏng thêm 1101" khiến tôi suýt VỨT MỘT BẢN VÁ ĐÚNG.** ⇒ **"Số quá XẤU" cũng là dấu hiệu bộ trích hỏng, không chỉ "số quá đẹp".**
> **Công cụ bắt được TẤT CẢ, dùng lại mỗi lần:** ***"phép đo này CÓ THỂ ra kết quả KHÁC được không?"*** và ***"tử số/mẫu số có đo CÙNG MỘT THỨ chưa?"***

## 🏁 CHỐT SỔ CUỐI PHIÊN 2026-08-01 (phiên trước) — ĐỌC KHỐI NÀY TRƯỚC
> **HEAD `b236b7e` == origin · tree SẠCH · check.sh [42/42] PASS · 34 MCP tool · 0 regress.**
> **LIVE `b236b7ee`** verify: prompt `2026.07.27-kb-l3` / `239e8b7b…` **KHÔNG đổi** · kb `e55ac112…` **KHÔNG đổi** ·
> `/health` ok · `ram_mb` 135,5 · trang chủ HTTP 200 đủ 4 chuỗi frontend. **11 commit** push+deploy+verify.
> ⚠ **pytest VẪN không chạy được** — cổng là `check.sh`. **KHÔNG có `specs/specs.json`** → `feature_list.json` (**69 mục**: 62 done · 6 deferred · 1 partial).
> Suite đổi số: takeoff 272→**283** · vntext 28→**53** · garble 26→**27** · **MỚI battery-runner 52**. Khác GIỮ NGUYÊN.
>
> **PHIÊN NÀY:** 1.06 dụng cụ đo · 1.03 nắn phông (**cứu 8.913 chuỗi, 0 hỏng thêm**) · 1.04 đơn vị · **Q2 baseline M3 = 13,0%** · soi id193 · **3 NO_GO có số**. Chi tiết: `claude-progress.md` entry đầu.
>
> **⛔ ĐỪNG LÀM LẠI (đã bác BẰNG SỐ trong phiên này):** bộ dò tổng-tập-con · vá bỏ sót bằng gợi-ý-trong-kết-quả-tool (2 vòng A/B) · thêm `tool_numbers` vào dict trả về `tra_loi_ai` (`app.py:625` `jsonify(r)` bơm số nội bộ ra trình duyệt — dùng **seam bọc `_guard_text` phía test**) · phủ quyết cả chuỗi khi thấy ký tự Unicode Việt (27 chuỗi hỏng thêm) · nhét `Ä/Å/Û/Φ` vào bảng `_TCVN3`.
>
> **BƯỚC TIẾP — ứng viên, CHƯA chốt (user chọn):**
> ① **GHÉP NHÃN↔GIÁ TRỊ THEO VỊ TRÍ** (đọc bảng hàng/cột) — đây là nút thắt THẬT của recall, đã chứng minh bằng số; repo có tiền lệ `_gan_dim_cau_kien`. Việc LỚN, phải đo trước.
> ② Luật **"câu có TỔNG + số không truy được nguồn"** — hình dạng đúng (2 bắt / 0 báo oan trên 25 câu) nhưng bằng chứng dương chỉ là **MỘT hiện tượng quan sát 2 lần**; cần mở rộng 198 câu × ≥2 lượt, và hành động phải là **GẮN CỜ, không thay câu trả lời**.
> ③ ~~Họ mã lạ `Ä/Å/Û/Φ` (768 chuỗi) — cần dựng bảng mã riêng + đo lại.~~ → **ĐÃ TRUY RA 2026-08-01: đây CHÍNH LÀ vế VNI của mục 1.03, không phải việc riêng.** Xem khối "1.02 & 1.03 CHƯA XONG" ngay dưới. Số "768" cũng sai — cận dưới là **1.422**.
> ④ Nhóm C (RAM/upload) vẫn HOÃN tới cuối dự án (tốn tiền túi).
> **Dữ liệu để dùng lại:** `tests/battery_runs/run02|03|04` (Q2, 198 câu ×3) · `run09` (33 câu có rổ neo) · `run10-15` (probe recall, có `tool_goi`). **Gitignored, chỉ có trên máy dev.**
>
> **📌 BÀI HỌC MANG SANG PHIÊN SAU:** ba lần trong phiên này **bộ trích của chính tôi hỏng** và cả ba suýt cho kết luận NGƯỢC (regex vớ `"304"` trong `"INOX 304"` → "0 gắn cờ"; bộ dò từ-khoá đếm *"không tìm thấy lỗi font"* thành từ chối → thổi bỏ-sót 2%→13%; tổng-tập-con mù với tổng cộng SAI). **Số "0%" và số "quá đẹp" là dấu hiệu bộ trích hỏng, không phải tin mừng** — chạy nó lên ca đã biết đáp án trước khi tin.

## ✅ BẢNG MÃ VNI-Windows — VIỆC NHÓM A LỚN NHẤT ĐÃ XONG (2026-08-02) · gate **[48/48]** · `wf_5543e990-f82`
> Đóng vế còn thiếu của mục 1.03 (tiêu đề BA VẾ, trước đây mới làm 2). Vế VNI có **0 dòng code**; nắn đúng **0/415 = 0,0%**; gõ *"phòng"* → **0 kết quả** trên file có **34 đoạn `PHOØNG HOÏC 1…18`**, trong khi CÙNG file *"phòng"* (phần TCVN3) = **51** ⇒ engine KHÔNG hỏng, **thiếu bảng mã**.
>
> ### CẤU TRÚC — vì sao KHÔNG nhét được vào `_TCVN3`
> `_TCVN3` là bảng **1:1 thay ký tự**. VNI là **[NGUYÊN ÂM] + [KÝ TỰ DẤU ĐỨNG SAU]**: `PHOØNG` = P,H,O,**Ø**,N,G → `PHÒNG` · `GIAÙO` = G,I,A,**Ù**,O → `GIÁO`. Cộng **5 CHỮ ĐÚC SẴN** đứng một mình (`Ñ Ô Ö Æ Ò`) — đó là lý do `NGHÆ`→`NGHỈ` **không theo khuôn** nguyên-âm+dấu. ⇒ thuật toán khác hẳn `_decode_tcvn3`.
> **Bảng: 15 mục dấu + 5 chữ đúc sẵn, MỖI mục có BẰNG CHỨNG CHÉO-FILE** (số cặp kiểm chứng ghi kèm trong code). **⛔ 2 ô bị LOẠI có chủ đích:** `Ì`(0xCC), `Í`(0xCD) — nghe rất hợp lý để thêm "cho đối xứng họ trăng" nhưng **0 bằng chứng**, và thêm vào sẽ **bắn vào chữ Việt ĐÚNG**: `KÍCH` 76 · `KÍNH` 33 · `TRÌNH` 27 · `BÌNH` 19. Các ô khác cũng đã xét và loại vì 0 hoặc NGƯỢC bằng chứng: `Þ` · `Ó` · `Ú` · `≥` · `·` (là dấu đầu dòng; **724 chuỗi TCVN3** dùng nó với nghĩa `ã`) · `Ư`.
>
> ### 🔴 PHẢN BIỆN BÁC ĐƯỢC CỔNG TỐT NHẤT BẰNG CA PHẢN CHỨNG THẬT
> Biến thể mà 4 nhóm đo hội tụ về — trông đã chặt — vẫn **PHÁ CHỮ VIỆT ĐÚNG**: `TOÀ NHÀ HOÀ BÌNH` → **`TỒ NHÀ HỒ BÌNH`** (vì `O`+`À` trong VNI đúng là `Ồ`, nhưng `TOÀ`/`HOÀ` là tiếng Việt viết đúng sẵn).
> **Cách chặn: điều kiện BẰNG CHỨNG CỨNG** — chuỗi phải có ≥1 ký tự **KHÔNG THỂ là chữ Việt hợp lệ** (`Û Ï Å Ä Ë Ñ Ö Æ`). Tập này **SUY RA chứ không chọn tay**, và **cố ý TRỪ `Ø`** vì `Ø` là ký hiệu **đường kính thép** (chính `vntext.py` đã ghi *"thêm vào là phá dữ liệu quan trọng nhất"*; đo: giữ `Ø` thì `TOÀ NHÀ HOÀ Ø20` → `TỒ NHÀ HỒ Ø20`).
> ⇒ Loại **cả một LỚP phá theo CẤU TRÚC**, không chỉ vá vài ca đã biết: vùng rủi ro **85 lượt → 0**.
>
> ### CỔNG: 3 PHỦ QUYẾT + 2 ĐIỀU KIỆN DƯƠNG — mỗi vế có SỐ hậu quả nếu ai đổi
> veto Unicode-đúng · veto ký-tự-CHỈ-thuộc-TCVN3 · **bằng chứng cứng** · **ngưỡng ≥2 cặp** (hạ xuống 1 **phá 316 lượt**: `CHñ NHIÖM THIÕT KÕ`→`CHĐ NHIƯM THĨT KÕ`) · ký tự ĐƠN không tính vào ngưỡng (tính vào **phá 3.237 lượt**).
> **⛔ TUYỆT ĐỐI KHÔNG dùng TÊN PHÔNG làm cổng:** 11 file khai `vn_vni.shx`/`VNI-Helve-Condense.TTF` nhưng **ruột TCVN3** và đang nắn ĐÚNG ⇒ dùng tên phông = **phá 107.764 chuỗi đang chạy tốt**; và còn **BỎ SÓT** — 3/16 file được cứu **KHÔNG hề khai** phông VNI.
>
> ### BA PHÁT HIỆN VỀ THỨ TỰ ÁP
> · **NFC phải chạy TRƯỚC khi dò** (bản cũ để ở CUỐI): corpus có chuỗi lưu dạng NFD ⇒ dò trên chuỗi thô làm `BẢNG THỐNG KÊ CỐT THÉP` → `BẢNG THỚNG KÊ CỚT THÉP`; hỏng thêm **0 → 19 lượt**.
> · **VNI phải TRƯỚC TCVN3, và là `elif`**: **350/415** chuỗi VNI mang ≥1 ký tự `_SIG` nên **đang đi nhầm nhánh TCVN3** và ra rác. Đặt sau ⇒ bản vá **vô hiệu trên ~84% ca**. (Tự đo xác nhận ở quy mô lớn hơn: **773/852** chuỗi đổi cũng khớp `_looks_tcvn3`, và nhánh đó cho `MAẬT CAẪT II-II` thay vì `MẶT CẮT II-II`.)
> · Hai nhánh **không va nhau THEO CẤU TRÚC**: `_looks_vni` phủ quyết mọi ký tự chỉ-thuộc-TCVN3.
>
> ### TỰ KIỂM NGƯỢC — 910.574 chuỗi / 98 file, MỘT lượt đọc tính cả trước lẫn sau
> | ngưỡng CỨNG | kết quả |
> |---|---|
> | chuỗi **thiếu bằng chứng cứng** trong tập bị đổi | **0/852** ✅ (bảo đảm CẤU TRÚC: `truoc` chắc chắn là garble) |
> | ca **"sau tệ hơn"** | **0** ✅ |
> | **delta SỐ** (`cao_do`·`thep_kg`·`thephinh_kg`·`n_sheet`·`n_qty`·`n_text`·`n_dim`) | **lệch 0**, 15/15 file ✅ |
> | gate | **[48/48] PASS · 0 suite cũ đổi số** dù bản vá chạm `to_unicode` |
> **Cứu 852 chuỗi riêng biệt / 15 file.** Ví dụ: `MAẬT CAẪT II-II`→`MẶT CẮT II-II` · `PHOỈNG HOẼP`→`PHÒNG HỌP` · `TRỆỄỈNG TRUNG HOẼC`→`TRƯỜNG TRUNG HỌC` · `SOÁ 17, DỆỄNG VAẤN AN…`→`SỐ 17, DƯƠNG VĂN AN…`
>
> ### ⚠ GIÁ PHẢI TRẢ, ĐO ĐƯỢC VÀ ĐÃ KHOÁ BẰNG CA TEST
> Điều kiện bằng-chứng-cứng làm **bỏ sót 93/945 = 9,8%** chuỗi VNI mà **mọi ký tự dấu đều trùng chữ Việt hợp lệ**: `PHOØNG AÊN` · `THEÙP SAØN` · `BEÂ TOÂNG LOÙT` · `CHI TIEÁT DAÀM` · `THIEÁT KEÁ`.
> Đây là **ĐÁNH ĐỔI CÓ Ý THỨC — đúng-đắn đổi lấy recall.** Khoá bằng ca `E3`: ai muốn "vớt thêm" phải sửa **có ý thức** và **đo lại lớp `TOÀ/HOÀ`**.
>
> ### 📌 LẦN THỨ 7 BỘ PHÂN LOẠI CỦA TÔI HỎNG — VÀ LẦN NÀY SUÝT CHO KẾT LUẬN **NGƯỢC HẲN**
> Bản đo đầu báo **"HỎNG THÊM = 1101"** và **"2190 chuỗi bị chạm ở file bẫy"** — nghe như phải **huỷ bản vá ngay**. Nhưng chính ví dụ nó gắn cờ là `'CHI TIEÁT MUẾI COẼC'`→`'CHI TIẾT MŨI CỌC'`, tức **CỨU ĐÚNG**. Hai lỗi ĐỊNH NGHĨA:
> · gọi *"file bẫy"* = mọi file khai phông VNI — nhưng file bẫy THẬT là **khai VNI mà RUỘT TCVN3**; file khai VNI *và* ruột VNI chính là **mục tiêu hợp lệ**;
> · định nghĩa *"sạch"* = không có ký tự lạ — nhưng **VNI DÙNG LẠI chính chữ Việt hợp lệ làm DẤU** (`GIAÙO` = A+Ù+O, cả ba hợp lệ) ⇒ **mọi bản cứu bị tính thành hỏng**.
> **Nếu tin con số đầu tiên, tôi đã vứt một bản vá ĐÚNG.** ⇒ Bài học mở rộng: *"số quá xấu"* cũng là dấu hiệu bộ trích hỏng, không chỉ *"số quá đẹp"*.
> ### ✅ E2E QUA ĐƯỜNG SẢN PHẨM — LIVE `45acd2f`, đo trên ĐÚNG file đã dùng để chứng minh lỗi
> `TKTC-THPT NHI CHIEU-KHOI LOP HOC_15112023_F.dxf`, 12 từ khoá người dùng thật sẽ gõ:
> | từ khoá | trước | sau | | từ khoá | trước | sau |
> |---|---|---|---|---|---|---|
> | **phòng** | **0** | **33** | | trần | 0 | 25 |
> | phòng học | 0 | 25 | | mặt cắt | 0 | 16 |
> | tường | 4 | 43 | | chi tiết | 0 | 14 |
> | mặt bằng | 0 | 13 | | thép | 0 | 12 |
> | giáo viên | 0 | 3 | | kết cấu | 0 | 2 |
> **TỔNG 11 → 194.** **0 từ khoá đi xuống.** ⚠ Đây là MỘT file (file gốc của vấn đề) — đừng trích như số toàn corpus; số toàn corpus là **852 chuỗi/15 file**.
> **TEST** `tests/test_vni.py` **43 ca** (A giải-mã · B chống-tái-phát · C không-được-đụng · D source-guard 8 ca khoá từng quyết định kèm số hậu quả · E đối-chứng + giới-hạn). check.sh 47→**48**, tổng ca 1.584→**1.627**.
> **⇒ MỤC 1.03 NAY TRỌN CẢ BA VẾ** (TCVN3 ✅ · Ø `%%C` ✅ · VNI ✅; `Φ` = NO_GO có số). `feature_list` `vntext` **partial → done** BẰNG SỐ, không bằng nhãn.

## ✅ A3 — NEO-THEO-TRÍCH-DẪN: lấy lại câu ĐÚNG mà hàng rào xoá oan (2026-08-02) · gate **[47/47]** · `wf_c748163d-28b`
> ### 🔴 GIẢ THUYẾT CỦA TÔI ("bị giết là vô hại") **SAI** — nhưng sai theo hướng có lợi
> Đọc tay **20/20** chuỗi thực sự bị giết (đo bằng CHÍNH `Drawing._trang_in_kho`):
> | loại | số |
> |---|---|
> | kích thước **THẬT** (`B=1.5m - L=394,5m` · `S= 1740.4m2` · `d315-HDPE-l421m-I=0.33%` · `Thảm đá dày 30cm` · `Tim đường đá mi B=1.5m`) | **7** |
> | **danh tính công trình** — số ĐẾM thật (`3 TẦNG 12 PHÒNG` · `NHÀ LỚP HỌC 3 TẦNG 21 PHÒNG` · `Nhà mái bằng 1 tầng, 2 tầng` = chuỗi bị giết NHIỀU NHẤT, 10 lượt) | **6** |
> | rác (mã cọc `CỌC 4.1-30` · `HỐ GA 6.3-23` · `loại 1,2` · `Tel: 0220.3855952` · `+1.63`) | **7** |
> | **lưới toạ độ `581000` · số tờ `-7/10` · tỉ lệ `TL 1:150` · mã hiệu `Đ-0.01`** | **0** |
> **Lý do 0:** chúng cho `do_luong=[]` ⇒ `_guard_text` **THOÁT SỚM** ⇒ **không bao giờ** vào tập bị giết. Tập bị giết **tự lọc về đúng phần có nghĩa**: 13/20 là dữ liệu thật.
>
> ### ⛔ HAI SỐ TÔI GHI VÀO CODE ĐỀU SAI — ĐÃ SỬA Ở 3 CHỖ (`mcp_bridge` · `tools_core` · `test_trang_in`)
> · **"60,8% (975/1.604) chuỗi trang in CÓ chữ số"** — **SAI ĐƠN VỊ**: đo *"CÓ CHỮ SỐ"*, không đo *"BỊ GIẾT"*. Đúng: **20/621 = 3,2%** chuỗi riêng biệt · **34/2.180 = 1,6%** theo lượt.
> · **"2.721 chuỗi / 24 file"** — **SAI MẪU SỐ**: bộ quét riêng của tôi chui vào **ATTRIB của INSERT**, `_trang_in_kho()` thì KHÔNG (`Ket Sat 3T12P`: quét **313** vs kho thật **3**). Kho THẬT = **18 file / 2.180 lượt / 621 chuỗi riêng biệt**. (Tôi **tự đo lại** bằng chính hàm sản phẩm, ra khớp chính xác — đây là lần thứ **6** trong phiên một phép đo của tôi lệch, và là lần đầu số sai đã kịp vào code.)
> · "5/8" từ probe là mẫu nhỏ, câu tự soạn. Số đúng đơn vị: **3/1699 = 0,18% lượt**.
>
> ### BẢN VÁ `_a3_trich_trang_in` (`mcp_bridge.py:~940`), cắm ở **CẢ HAI** call-site, **TRƯỚC** A2
> Giữ câu khi **MỌI** số đo-lường của nó nằm **TRỌN** trong đoạn trích **NGUYÊN VĂN ≥`_A3_K`=12 ký tự** khớp một chuỗi `doc_chu_trang_in` đã trả **trong CHÍNH lượt này** ⇒ trả lại câu + gắn cờ `CO_TRANG_IN`. **KHÔNG** bơm số vào `tool_numbers`. **FAIL-CLOSED** (mọi lỗi → giữ lời từ chối). 5 vế cổng: 4 vế đầu **đúng cổng A2** (không mở rộng phạm vi), vế 5 lọc theo **NHÓM** `doc_chu_trang_in` — cố ý lọc theo nhóm chứ KHÔNG dựa vào *"tình cờ `tra_ky_hieu` không phát handle"*.
> **BA QUYẾT ĐỊNH, mỗi cái vì bản ngây thơ ĐÃ ĐO RA HỎNG:**
> · **`all` chứ KHÔNG `any`** — bản ANY để lọt **10-12/12 ca ĂN THEO** (trích đúng 1 chuỗi rồi chở thêm số bịa; ANY-GROUNDED bảo lãnh cả câu). → ca `G1`
> · **gộp vùng RIÊNG TỪNG CHUỖI** — gộp chung thì khâu đuôi `'…trải mái m=3'` với đầu `'1.5m - L=394,5m'` **ĐẺ RA số MỚI 31.5 không có ở đâu cả**. → ca `G2`
> · **số A3 KHÔNG vào rổ neo** — khác biệt CƠ CHẾ: không để lại "giấy phép" cho lượt SAU trong cùng phiên.
> **K=12 là ĐO, không phải hằng số hiển nhiên:** K=8→5/5 · **K=12→5/5** · K=16→**3/5** · K=20→3/5.
> **⛔ KHÔNG bỏ tool #35 khỏi tuple loại-trừ** — đo lại: MỘT lượt `doc_chu_trang_in(15)` trên `rachmop` bơm 10 số vào rổ neo, **trong đó `-7.0`** (sinh thuần từ SỐ TỜ) = đúng nguyên liệu id135.
>
> ### ⚠ CHỖ NGUY HIỂM NHẤT CỦA BẢN VÁ — LOGIC NHÂN BẢN TRONG ĐƯỜNG CHỐNG-BỊA
> `_a3_do_luong_vitri` là **bản nhân bản GIỮ-VỊ-TRÍ** của `_answer_numbers`. Ai sửa `_MAHIEU_RES` / `_I1B_*` / `_DEM_NUM_RE` mà quên ⇒ **hai bản trôi lệch ÂM THẦM**. Khoá bằng ca bất biến `M1`; **tự đo trên 2.042 chuỗi/câu → 0 lệch**, trong đó **326** câu CÓ số đo-lường (⇒ phép đo **không tautology**).
> ### 📌 RỦI RO TỒN DƯ, KHÔNG CHẶN HẾT ĐƯỢC
> Model trích **ĐÚNG** nhưng **GÁN SAI NGHĨA**: `'Tel: 0220.3855952'` → *"chiều dài tuyến 220,38 m"*. **4/17** số cấp phép được thuộc loại này. Cờ `CO_TRANG_IN` + `ghi_chu` tool là thứ **duy nhất** giảm nhẹ. **Phải nêu khi báo cáo.**
> ### 📌 NÓI THẲNG VỀ ĐÁNH ĐỔI
> Quy mô **0,18% lượt**, và **KHÔNG phải lỗi an toàn** (A2 đã hạ "nói dối" → "trung thực"). Đổi lại là một cơ chế **khá nặng** trong đường chống-bịa. Thiết kế tự đánh giá **"ĐÁNG LÀM nhưng ƯU TIÊN THẤP"**. Nếu xếp lại ưu tiên thì **bảng mã VNI** (1.422 chuỗi đọc sai hoàn toàn) đáng làm trước nhiều.
> **TEST** `tests/test_a3_trich_trang_in.py` **21 ca** (D phân-biệt-được · G chống-hồi-quy · M bất-biến · S source-guard), check.sh 46→**47**. **Tự kiểm ngược:** gỡ A3 → D1/D2/D3 **ĐỎ**, G5 (id135) **XANH cả hai phía**. Gate: **0 suite cũ đổi số**, tổng ca 1.563→1.584.
> **📌 Lần thứ 7 assert của tôi sai mà code đúng:** ca `G6` dùng *"5 cống hộp"* — `"cống"` KHÔNG nằm trong `_DEM_TU` nên `do_luong=[]`, câu **chưa bao giờ bị chặn**. Đổi sang *"5 bộ cửa"* + thêm `G6b` khoá luôn hành vi đó. **Cùng khuôn lỗi với `G3` của suite A2** — tôi liên tục giả định một câu kích guard trong khi nó không kích.

## ⛔ CỜ "SỐ DO MÁY TỰ TÍNH" = **NO_GO** (không đạt ngưỡng ĐẶT TRƯỚC) + ✅ KIỂM LẠI XẾP LỚP TOOL #35 = **GIỮ** — 2026-08-01 `wf_d32aae4a-708`
> ### ⛔ VIỆC 1 — cờ "số do máy tự tính": **NO_GO**, thiết kế đã siết và ĐÓNG BĂNG (lấy ra dùng khi có corpus mới)
> | ngưỡng ĐẶT TRƯỚC khi chạy | đo được | |
> |---|---|---|
> | ≥3 **hiện tượng ĐỘC LẬP** (đếm theo bảng/bản vẽ, KHÔNG theo lượt) | **1** — đúng bảng "THỐNG KÊ KHỐI LƯỢNG INOX 304" 9 dòng, 1 file, qua 2 câu id32+id193, 4 lần bắn | ❌ |
> | báo oan **≤20%** | **0%** — nhưng **con số này BỊ QUẦN THỂ ÉP** | ⚠ KHÔNG kết luận được |
> **Đã cố mở rộng 3 trục, vẫn = 1 hiện tượng:** mẫu nở **33 → 195 câu có rổ neo THẬT** (replay offline chuỗi `tool_goi`, tự kiểm **131/134 dòng khớp chính xác** `ro_neo_n` đã ghi) · quét thêm **637 câu** run01-04 bằng rổ siêu-tập → 11 ca → đọc tay 11/11 → **0 hiện tượng mới** (9 ca *"89 bộ cửa"* là **báo oan của phép đo**: `tong_so_luong(loc='cua')` trả thẳng `{"tong":89}`; 1 ca id105 *"80 vị trí"* là **TRẦN CẮT** `highlight(gioi_han=80)` chứ không phải phép cộng) · quét trục KHÁC (bỏ hẳn từ khoá "tổng") trên **832 câu** → 10 nhóm → **1** tự-cộng, 9 artifact.
> **✅ ĐÃ KIỂM CHỐNG-TAUTOLOGY:** cơ hội sinh hiện tượng #2 **CÓ TỒN TẠI** (file ketcau có 4 ô *"TỔNG KHỐI LƯỢNG (kG)"* rời rạc 9.15/14.4/353.7/379.9 + 9 câu battery có chữ "tổng" trên ketcau, 5 trên hatang). **Model đơn giản là KHÔNG tự cộng ở đó** ⇒ "1 < 3" là kết quả THẬT, không phải artifact corpus.
> **Vì sao "báo oan 0%" KHÔNG dùng được:** trong 162 lượt có `tool_goi`, chỉ **20 lượt** gọi tool bị-loại-khỏi-rổ-neo, và chỉ **1/20** có câu-tổng kèm số đo-lường ⇒ quần thể có cơ hội bắn oan ≈ **1**.
> **🔴 DỰNG ĐƯỢC 4 CHẾ ĐỘ BÁO OAN, TÁI HIỆN TRÊN CHÍNH BẢN VÁ:**
> · **X1 kết tội SAI ĐỐI TƯỢNG** — *"Tổng khối lượng thép tròn là **564.8 kg**, trong đó Ø6 dài 49.9 m **dày 5 mm**"*, rổ neo **CÓ** 564.8 ⇒ cờ bắn vào `5.0`. **Số tổng có neo đầy đủ.**
> · **X4 NHÃN CỘT ≠ máy cộng** — *"tổng chiều dài 49.9 m"* là ô bảng **đọc verbatim**. Dạng này chiếm **45,7%** miền sống.
> · **X3b kênh CẤU TRÚC** — *"Bảng nhúng có dòng TỔNG CỘNG ghi 1384.83 kg"*: số **CÓ THẬT in trên bản vẽ**, nhưng tool OLE bị **cố ý** loại khỏi rổ neo nên **không bao giờ neo được**.
> · **X5b** — `_TONG_RE` vớ *"tổng **thể**/tổng **hợp**"*: *"kích thước tổng thể mặt bằng là 45.6 m"*.
> **Độ phơi trên 790 bản ghi:** miền sống = 232 câu-tổng có số đo-lường; **116 = 50,0%** có ≥2 số đo-lường (cửa vào X1); **106 = 45,7%** dạng X4. **Gần MỘT NỬA miền sống là chỗ chữ cờ sai bản chất ngay cả khi grounding chạy đúng.**
> **📌 CHI TIẾT ĐÁNG SỢ NHẤT:** 4 ca bắn thật **thoát báo-oan CHỈ VÌ model tình cờ XUỐNG DÒNG** tách *"dày 5mm:"* ra khỏi câu tổng — **đổi một dấu xuống dòng là thành báo oan**.
> **THIẾT KẾ ĐÃ SIẾT, ĐÓNG BĂNG (nếu mở khoá thì CHỈ dùng bản này, KHÔNG dùng bản sơ bộ):** loại "tổng thể/hợp/quan/mặt bằng/bình đồ" · loại **nhãn cột** (`tổng chiều dài|số thanh|số lượng|…`) · chỉ xét **SỐ ĐẦU TIÊN SAU** mệnh đề tổng · loại lượt có gọi tool OLE/bảng-vẽ-nét · loại số kiểu VN `1.384,83` · tách câu **KHÔNG theo `|`** (mất dòng bảng markdown) · cắm ở **CẢ HAI** call-site (đường "hết lượt tool" là chỗ rủi ro tự-cộng cao nhất và **dễ quên nhất**) · chữ cờ **trung tính về nguyên nhân** (KHÔNG quy kết "AI tự cộng" — X3b chứng minh cờ bắn được cả số ĐÚNG in trên bản vẽ) · **GẮN CỜ, TUYỆT ĐỐI KHÔNG CHẶN**.
> **ĐIỀU KIỆN MỞ LẠI:** có **≥3 hiện tượng tự-cộng ĐỘC LẬP** (≥3 bảng/bản vẽ khác nhau). Nếu corpus mới vẫn ra 0 hiện tượng mới ⇒ kết luận đổi thành *"hành vi tự cộng CHỈ xuất hiện ở bảng thống kê nhiều dòng cùng đơn vị"* ⇒ khi đó **bỏ hẳn cờ**, thay bằng **cảnh báo TĨNH gắn theo TOOL đọc bảng**.
>
> ### ✅ VIỆC 2 — `doc_chu_trang_in` trong `_TOOL_DIEN_GIAI`: **GIỮ NGUYÊN**
> **Căn cứ CƠ CHẾ (mạnh nhất, không phụ thuộc tỉ lệ dạng câu hỏi):** vế đầu A2 là `guarded == REFUSE_MESSAGE`, mà `_guard_text` **thoát sớm** ở `if not do_luong`. Câu **khẳng định vắng mặt hầu như không mang số** ⇒ A2 **gần như không có cửa** làm tệ đi. Đo trên **văn phong THẬT** (832 câu → 471 dedupe → 40 câu vắng-mặt-thuần): A2 đổi **5/40 = 12,5%**.
> **Soi 5 ca đó:** **cả 5** mang số từ khuôn OLE do **chính `_P_R8c_OLE` ép ra** — mà R8c lại **CẤM** nói *"bản vẽ KHÔNG có bảng"* khi có `canh_bao_nhung`. ⇒ Trong đúng 5 ca A2 kích, **`REFUSE_MESSAGE` VI PHẠM luật của chính dự án**, còn A2 thì không.
> **Xác minh TRỰC TIẾP (bắt nguyên văn TRƯỚC guard):** **5/5** model **trích nguyên văn payload kèm handle THẬT** (`[257B0B]`, `[25827A]`, `[25728D]`), **0/5 bịa**. Không có A2, 5 câu ĐÚNG-CÓ-HANDLE đó thành *"Không có thông tin này trong bản vẽ."* = **nói dối ngay trên thứ máy vừa đọc được**.
> **Rủi ro nêu trong đề bài KHÔNG hiện thực hoá:** quần thể đáng lo nhất (tool trả RỖNG, 111/198 câu) đo LIVE: **4/4 model gọi MỘT MÌNH** `doc_chu_trang_in` (thoả vế 4 của A2) nhưng viết vắng mặt **SẠCH SỐ** ⇒ `do_luong=[]` ⇒ **0/4 A2 kích**. Và **4/8** câu probe dạng "hỏi tồn tại" **VẪN route vào tool này** ⇒ kết luận KHÔNG dựa vào giả định "tool ít bị route vào dạng tồn tại".
> **Mệnh đề bị phản biện BÁC (không lật kết luận):** `file_summary` do **HOST bơm thẳng** vào `system_instruction` (*"8024 đối tượng, 141 layer"* — cả hai từ đều trong `_DEM_TU`) **KHÔNG bao giờ vào rổ neo** ⇒ **2/198 câu** battery có thể sinh câu vắng-mặt ĐÚNG mà A2 hạ xuống "chưa tra được". Phát biểu đúng: **"dương trong 5/5 quan sát, kèm MỘT kênh nhỏ đo được có thể âm"**, KHÔNG phải "luôn dương".
> **⛔⛔ RÀNG BUỘC SỐNG CÒN — AN TOÀN DO MỘT *TÌNH CỜ* GIỮ, KHÔNG DO THIẾT KẾ:** `doc_chu_trang_in` là tool **hiếm hoi KHÔNG gọi `_gan_canh_bao_nhung`** (tự kiểm: **14 chỗ khác** trong `tools_core.py` CÓ gọi). Ai gắn `canh_bao_nhung` vào nó — **nghe rất hợp lý** theo tinh thần R8c *"máy không đọc được ≠ không có"* — thì **mọi** câu vắng-mặt trên file OLE tự mang *"N đối tượng nhúng"* ⇒ `do_luong` ≠ rỗng ⇒ REFUSE ⇒ A2 kích, và lớp lỗi *"A2 làm câu ĐÚNG tệ đi"* chuyển từ **0 ca** sang **PHỔ BIẾN**. **Đã ghi cạnh code + KHOÁ bằng 3 ca test `[K]`** (K2 là đối chứng chống-tautology).
>
> ### ⚠ VẤN ĐỀ TO HƠN LỘ RA — **KHÔNG phải lỗi A2**, ghi sổ, CHƯA VÁ
> Tool #35 nằm trong tuple loại-trừ rổ neo ⇒ **MỌI trích dẫn có chữ số từ nó đều bị `_guard_text` từ chối**, mà **60,8% (975/1.604) chuỗi trang in CÓ chữ số** (tự đo độc lập; agent đo 68% trên mẫu con — cùng bậc). Probe: guard **xoá 5/8 câu trả lời ĐÚNG** của tool #35. Trên `rachmop`, `'Hoàn trả đường dân sinh - B=1.5m - L=394,5m'` đọc **ĐÚNG** nhưng **KHÔNG BAO GIỜ tới người dùng**.
> ⇒ **A2 chỉ hạ "nói dối" xuống "vô dụng"; nó KHÔNG lấy lại câu trả lời.** Hạng mục RIÊNG, cần đo riêng. **Cách rẻ nhất lấy nốt dữ liệu (~10 lượt API):** 5 câu LIVE dạng "hỏi tồn tại" trên **một file OLE có `canh_bao_nhung`** (quần thể duy nhất chưa chạm) — đây là ca duy nhất còn có thể lật kết luận việc 2.
> **⛔ ĐỪNG LÀM VỘI:** đề xuất *"thông điệp thứ ba"* (thay `KHONG_TRA_DUOC` bằng *"đọc được ở khung tên nhưng số ở đó không dùng làm số liệu"*) nghe hợp lý nhưng **CHƯA ĐO** — đúng loại vá-nghe-hợp-lý dự án đã nhiều lần đo ra NO_GO. Phải A/B riêng, và phải kiểm cả `tra_ky_hieu` vì đổi nhánh này chạm **cả hai** tool trong `_TOOL_DIEN_GIAI`.
> **CÒN THIẾU, nói thẳng:** `doc_chu_trang_in` vẫn **0/162 lượt trong mọi log lịch sử**; toàn bộ bằng chứng đến từ **17 câu probe LIVE trên 2 file**, 1 model, 1 lượt/câu, temperature=0 ⇒ đủ để **GIỮ** (giữ = giữ hiện trạng, lệch về an toàn), **KHÔNG đủ** để trích "6/6 gọi một mình" hay "5/8 A2 kích" như hằng số toàn hệ. Quét corpus là **SÀN** (21/98 file bị bỏ, gồm chính `rachmop`; `gioi_han=40` là trần cứng).

## ✅ A2 — RỔ NEO RỖNG *VÌ CHÍNH SÁCH* KHÔNG ĐƯỢC KHẲNG ĐỊNH "BẢN VẼ KHÔNG CÓ" (2026-08-01) · gate **[46/46]**
> **Lỗi:** model **CHỈ** gọi tool trong tuple loại-trừ rổ neo ⇒ `tool_numbers` RỖNG ⇒ `_guard_text` trả *"Không có thông tin này trong bản vẽ."* = **KHẲNG ĐỊNH VỀ BẢN VẼ**, và nó **SAI** khi bản vẽ có dữ liệu. Đo **3/1699 = 0,18%**; id69 gọi `tra_ky_hieu` → từ chối, trong khi `ky_vong` = *"Thép tròn, 4817 thanh / 25752.6 kg"*; **cùng câu** lượt gọi `thong_ke_thep` thì **trả lời ĐÚNG** ⇒ nguyên nhân là **ROUTING**.
>
> **⛔ HAI PHƯƠNG ÁN HIỂN NHIÊN ĐỀU NO_GO — ĐỪNG LÀM LẠI:**
> · **(A) điều kiện rộng "rổ neo rỗng + `da_goi`"**: bắn trúng **đúng lớp lỗi id135** (`tim_kiem` chạy THẬT trả `{}` rồi model bịa `-10m` — ở đó REFUSE là câu **ĐÚNG**) ⇒ **làm vỡ `test_grounding_guard:137`**, cổng 232→231 PASS/1 FAIL · bắn trúng câu hỏi **TỒN TẠI** (id139, `ky_vong` đòi nguyên văn *"PHẢI NÓI RÕ KHÔNG CÓ"*, `loi_san='ảo giác'`) · **ghi đè lời từ chối TRUNG THỰC do chính model viết** (REFUSE_MESSAGE nằm trong SYSTEM_PROMPT + cả 2 câu nhắc đều dạy model nói đúng chuỗi đó). **Lý do cấu trúc:** `REFUSE_MESSAGE` **gánh HAI vai** — **≥22/36 lượt** REFUSE toàn corpus nằm trên id mà `ky_vong` **ĐÒI** khẳng định-vắng-mặt ⇒ một thông điệp không phục vụ được cả hai quần thể.
> · **(B) ép model gọi lại tool có số**: giả định cốt lõi (*"model đổi routing sau lời nhắc"*) có **0 phép đo** · số lợi ích "3/3 id có lượt đúng nhờ routing khác" là **TAUTOLOGY** (≈10 lượt/id ⇒ "tồn tại ≥1 lượt đúng" gần như chắc chắn theo cấu tạo mẫu; nó đo **biến thiên routing**, không đo **hiệu lực câu nhắc**) · **bằng chứng ngược:** câu **ĐỊNH TÍNH** đúng của id69 **đã đi qua hàng rào sẵn** khi không kèm số ⇒ bệnh là *"một con số tình cờ"*, không phải *"thiếu số liệu"* ⇒ (B) **ép model NHÉT SỐ vào câu vốn định tính** = đúng lớp rủi ro đã NO_GO ở `_VCD_CAU_NUDGE` · chi phí **+2 lượt gọi/ca** (không phải +1) · **không cắm được vào call-site thứ hai** vì `cfg_final` **không truyền `tools=`**.
>
> **✅ (A2) — BIẾN THỂ HẸP, ĐÃ LÀM.** Phát hiện then chốt: **tuple loại-trừ chứa HAI LỚP NGỮ NGHĨA NGƯỢC NHAU**.
> | lớp | tool | rổ neo rỗng vì | câu đúng |
> |---|---|---|---|
> | **DIỄN GIẢI** | `tra_ky_hieu`, `doc_chu_trang_in` | **CHÍNH SÁCH** (payload là giải nghĩa/tiêu đề, không phải nguồn số) | *"chưa tra được"* |
> | **PHÁT HIỆN TỒN TẠI** | `doc_bang_nhung`, `phat_hien_bang_ve_net` | đầu ra HỢP LỆ **chính là** "có/không có bảng" | **khẳng định vắng mặt** ⇒ giữ REFUSE |
> Hàm `_a2_khong_tra_duoc` (`mcp_bridge.py:890`), cắm ở **CẢ HAI** call-site. **4 vế**, mỗi vế chặn một rủi ro đo được: `guarded == REFUSE_MESSAGE` · **`text_goc != REFUSE_MESSAGE`** (chặn ghi đè lời từ chối trung thực — vế `guarded` một mình KHÔNG phân biệt được vì `_guard_text(REFUSE, set())` trả lại chính nó) · `not tool_numbers` · **`ten_tool <= _TOOL_DIEN_GIAI`** (vế chặn id135 + câu hỏi tồn tại; tập RỖNG cũng không kích vì đòi `ten_tool` truthy).
> `ten_tool_da_goi` ghi **mọi** `fc.name` **kể cả tool bị L0 chặn** — **lệch về phía AN TOÀN**: tên lạ sẽ không ⊆ `_TOOL_DIEN_GIAI` ⇒ bản vá không kích.
> **`_apply_i1` (`:641`) đã vá tường minh** thành `in (REFUSE_MESSAGE, KHONG_TRA_DUOC)`. Đo được hôm nay nó **vô hại** (không khớp `_REFUSAL_MARKERS` nên chạy tiếp, nhưng `_handle_tokens` rỗng ⇒ `n_call=0`) — **vẫn vá, KHÔNG dựa vào may**. ⛔ **KHÔNG thêm "chưa tra được" vào `_REFUSAL_MARKERS`**: đó là bộ lọc **ngôn ngữ tự nhiên** áp lên câu do MODEL viết, thêm cụm phổ biến sẽ miễn kiểm-handle cho một tập câu chưa đo được kích thước.
> **Hình dạng thông điệp đã ĐO trước khi viết:** 0 chữ số · `_answer_numbers` → `([], [])` · **ĐIỂM BẤT ĐỘNG** (`_guard_text(msg, set()) == msg`, không tự huỷ ở vòng sau) · không khẳng định gì về bản vẽ.
> **TEST** `tests/test_neo_rong_tu_choi.py` **23 ca**, check.sh 45→**46**. **Tự kiểm ngược:** gỡ bản vá thì **D1/D2/D3 ĐỎ**, còn **G1 (id135) XANH cả hai phía** ⇒ suite **phân biệt được**, không phải cổng-xanh-vô-nghĩa.
> ⚠ **Helper `run_e2e` của `test_grounding_guard.py:44` HARD-CODE tool `"tim_kiem"`** — đó là lý do **6 file test hiện có đều MÙ** với lớp lỗi này. Suite mới dùng helper **có tham số tên tool** + bridge trả kết quả **theo từng tool**.
> **📌 GIÁ TRỊ THẬT, NÓI THẲNG:** bản vá **KHÔNG lấy lại câu trả lời đúng nào** (0/5 lượt kích). Nó chỉ đổi một **khẳng định SAI về bản vẽ** thành câu **trung thực**. Đừng trích nó như một cải thiện recall.
> **⛔ ĐÍNH CHÍNH đề bài tôi giao (đã đo):** call-site là **`:992`/`:1012`** (không phải `:994`/`:1008`) · **6** file test tham chiếu `REFUSE_MESSAGE` (không phải 5) · điều kiện kích cần **3 vế**, không phải 2 (phải thêm "câu thô có ≥1 số ĐO-LƯỜNG": `_guard_text("Thép Ø10 là thép tròn.", set())` **GIỮ NGUYÊN** vì `do_luong` rỗng) · trong 3 ca "từ-chối-oan" thì **chỉ id69 là oan thật**, id139 KHÔNG oan, id103 guard **không hề chạm**.
> **CÒN LẠI:** `doc_chu_trang_in` có **0/162 lượt gọi** trong mọi log ⇒ xếp nó vào `_TOOL_DIEN_GIAI` là **suy luận ngữ nghĩa, chưa đo** — món phải kiểm ở lượt battery đầy đủ kế tiếp.

## ✅ E2(b) TOOL #35 `doc_chu_trang_in` + ⛔ NO_GO "câu tổng-hợp bị giết" — 2026-08-01 · gate **[45/45]** · 35 tool
> **① QUÉT ĐỦ CORPUS LẦN ĐẦU (95/98 file — trước đây luôn thiếu file to nhất) — LẬT NGƯỢC CẢ HAI GIẢ ĐỊNH:**
> · chuỗi chỉ-ở-trang-in **851/893 → 2.721** (3×), ở **24/95 file** — "cận dưới" là đúng.
> · nhưng chuỗi **MANG GIÁ TRỊ ĐO** chỉ **10/2.721**, và **9/10 nằm trong `rachmop.dxf`** (id135, đã có trong battery). **Ngoài rachmop, TOÀN corpus còn ĐÚNG 1 chuỗi:** `d315-HDPE-l421m-I=0.33%`.
> · 🔴 **File 202MB tên `XR-CAP NUOC …-trangin-chiHoa.dxf` — thứ HAI vòng nghiên cứu trước đều DỪNG LẠI ĐỂ CHỜ — đo ra `chỉ-trang-in = 0`. Điều kiện tiên quyết cũ đuổi theo một CHỖ TRỐNG.**
> · file đóng góp nhiều nhất (`XR-KHAO SAT TKCS`, 1.517 chuỗi = 56%) có **46,3% là LƯỚI TOẠ ĐỘ** (`581000`, `581200`…) ⇒ trần mặc định phải THẤP.
> **📌 BỘ TRÍCH CỦA TÔI LẠI CẮT CỤT (lần 4 trong phiên):** lưu tối đa 400 chuỗi/file nên bảng phân loại đầu chạy trên 1.604/2.721; **toàn bộ 1.117 chuỗi mất đều thuộc ĐÚNG một file**. Đã quét lại riêng file đó bỏ trần.
>
> **② TOOL #35 `doc_chu_trang_in` — LÀM XONG.** E2E file thật: hỏi `"lưu vực"` → **15 kết quả**, cùng từ khoá `tim_kiem` → **0**. Chỉ trả chuỗi **KHÔNG có ở modelspace** (tránh đếm trùng + tránh bơm neo cửa hai) · kho dựng **LƯỜI**, **KHÔNG nạp vào `self.texts`** (nạp vào là đổi mọi index/rổ neo toàn hệ — đúng thứ đã BÁC khi làm chữ-trong-khối) · trần 40, mặc định 15 · chặn khớp **mù dấu** · fail-open.
> **⛔ ĐIỀU KIỆN SỐNG CÒN ĐÃ CÀI CÙNG LÁT:** tool nằm trong tuple loại-trừ rổ neo `mcp_bridge.py:958`. **KHÔNG phải phòng xa — đo LIVE:** nếu không loại, tool bơm **DÃY ÂM LIỀN `-1,0 … -10,0`** vào rổ neo, sinh **THUẦN từ SỐ TỜ** (`… LƯU VỰC TB.6 -7/10`), cộng lưới toạ độ `581000+` và tỉ lệ `1:150`. Dãy âm đó bảo lãnh **cao độ âm TRÒN bịa** (−2,0m / −5,0m) = **đúng lớp lỗi id135**.
> **NÓI THẲNG VỀ GIÁ TRỊ:** tool này **KHÔNG giúp bóc khối lượng** (1 chuỗi mang giá trị đo trên toàn corpus ngoài file đã phủ). Nó trả lời *"bản vẽ này là gì / gồm những tờ nào / tên công trình"*. Làm vì nó đóng một **thất bại im lặng** thật.
> **TEST** `tests/test_trang_in.py` **20 ca**, check.sh 44→**45**. Ca `T3b` **chứng minh việc loại-trừ là CẦN THIẾT** chứ không chỉ khẳng định nó tồn tại.
>
> **③ ⛔ NO_GO — "câu tổng-hợp ĐÚNG bị hàng rào giết" (`wf_028146eb-439`): GIẢ THUYẾT CỦA TÔI SAI.**
> Tôi từng ghi *"câu tổng cộng đúng viết bằng `Ø` đang bị hàng rào giết"*. **Ba đối chứng bác thẳng:**
> | thử | kết quả | ý nghĩa |
> |---|---|---|
> | `"…Ø6, Ø8, Ø10 là 24331.67 kg."` | CHẶN | ca tôi nêu |
> | `"…là 24331.67 kg."` (**không có Ø nào**) | **CHẶN Y HỆT** | ⇒ **strip mã-hiệu KHÔNG phải nguyên nhân** |
> | `"…Φ6, Φ8, Φ10 là 99999.99 kg."` (**bịa thuần**) | **ĐI QUA** | ⇒ nhánh `Φ` là **LỖ**, không phải hành vi đúng |
> ⇒ Tôi đã **lấy một LỖ HỔNG làm chuẩn mực** rồi kết luận hành vi đúng là sai. Vá theo hướng đó = **nhân bản lỗ sang `Ø`**.
> **BẢN CHẤT THẬT — model PHÁ LUẬT `_P_R2` (cấm tự cộng), hàng rào chạy ĐÚNG.** Bằng chứng dứt điểm: id193 trên **CÙNG một bản vẽ** cho **6 giá trị khác nhau** qua các lượt (`1344.33` · `3545.9` · `1384.83` · `161.21` · `80,52` · `76.9`) ⇒ tối thiểu **5/6 SAI**; và `tool_goi` cho thấy model **đã gọi đúng** `thong_ke_thep_hinh`, mà tool đó **ĐÃ trả sẵn `tong_khoi_luong_kg`** (`tools_core.py:2532`) kèm ghi chú *"KHÔNG tự cộng bảng con"*.
> **CHI PHÍ NẾU VÁ:** cứu **0 câu**, đổi lấy **8,3%** câu được cấp neo miễn phí + **17,8% bịa lọt thêm** (tích chéo 20 câu bịa × 137 rổ neo thật; mẫu hiện thực nhất 64-67%). Soi "người bảo lãnh" trong mô phỏng: chữ số hex của **HANDLE** `[126EA6]`→6.0 · tiết diện `40x80x2mm`→2.0 · mác `M200`→200.0. **Mảnh vụn vô nghĩa đi bảo lãnh cho khẳng định khối lượng**; không có cách chỉnh để chỉ cứu bên phải.
> **Vế 1 (strip quá tay) đo ra BẰNG 0:** `Ø<số>` xuất hiện 144/1699 câu (8,5%) nhưng `Φ/φ/Ф/⌀`+số xuất hiện **0/1699** — kênh Φ là lý thuyết, **chưa từng sống**. **Vế 2 NGƯỢC CHIỀU:** hàng rào đang **THẢ** chứ không giết — **9/157 = 5,7%** câu PASS mang số đo-lường **không truy được nguồn**, gồm đúng `1344.33` và `1384.83` của id193.
>
> ### 🔴 LỖI THẬT ĐO ĐƯỢC — VÀ **BẢN VÁ CỦA CHÍNH TÔI VỪA NỚI BỀ MẶT CỦA NÓ**
> Khi model **CHỈ** gọi một tool nằm trong **tuple loại-trừ rổ neo** thì `tool_numbers` **RỖNG** ⇒ mọi khẳng định có số bị chặn ⇒ trả *"Không có thông tin này trong bản vẽ."* — **một câu SAI SỰ THẬT**. Đo: **3/1699 lượt** là từ-chối-oan thật, ca id69 (`tra_ky_hieu`, `ro_neo_n=0`) trong khi `ky_vong` = *"Thép tròn, 4817 thanh / 25752.6 kg"*; cùng câu đó lượt gọi `thong_ke_thep` (`ro_neo_n=4`) thì **trả lời ĐÚNG**.
> ⚠ **Danh sách loại-trừ vừa đi từ 3 → 4 tool vì tôi thêm `doc_chu_trang_in`.** Việc loại trừ vẫn ĐÚNG và BẮT BUỘC (không loại thì dãy âm −1..−10 vào rổ neo), nhưng **không miễn phí** — ghi rõ ở đây để phiên sau không tự vấp.
> **HƯỚNG SỬA (lát riêng, chưa làm):** KHÔNG nới rổ neo, mà **đổi nhánh xử lý** — rổ neo rỗng **VÀ** đã gọi ≥1 tool ⇒ ép gọi lại tool có số (cơ chế nhắc-lại đã có ở `mcp_bridge.py:971-978`, tối đa 1 lần/câu), hoặc trả thông điệp trung thực *"chưa tra được từ công cụ có số liệu"*. **Rủi ro:** thông điệp mới **TUYỆT ĐỐI không được chứa số nào** (nới cửa = tái sinh id135) · sẽ làm nhiều suite đóng-băng-số đổi ⇒ **phải tự kiểm ngược bằng số TRƯỚC**, liệt kê từng ca đổi kèm lý do, rồi mới sửa suite.
> **⛔ ĐÍNH CHÍNH MỘT KHUYẾN NGHỊ ĐANG LƯU HÀNH TRONG DỰ ÁN:** `answer_goc` **KHÔNG phải** văn bản TRƯỚC hàng rào — `mcp_bridge.py:994` và `:1008` đều gán `_goc = _guard_text(text, tool_numbers)`, tức **ĐẦU RA** của guard. Ghi `answer_goc` vào log để phân tích hàng rào là **vô ích**. Chỗ đúng: seam `_bat_ro_neo` ở `tests/run_battery.py:93` **đã bọc `_guard_text` và đang nhận `text` nguyên bản**.
> **CÒN CHƯA BIẾT:** **26/36** ca REFUSE **không phân loại được** (không có rổ neo trong bản ghi) — đó mới là kích thước thật của vùng chưa biết, **không phải 0**. Có bằng chứng suy đoán trước đây **sai 50%**: id105/id189 từng bị quy oan cho hàng rào, thực ra `do_luong` rỗng ⇒ guard **thoát sớm** ở `:859` ⇒ model **tự** từ chối.

## ⛔ BA NO_GO CÓ SỐ — C1 (Φ) · B1 (Ø/Ü vào `_SIG`) · E2 (cờ trang in khớp-từ-khoá) — 2026-08-01 `wf_3e934400-206`
> **Cả 3 phản biện đều `bac_bo=true`, và agent thiết kế TỰ CHẠY LẠI 4 phép đo quyết định — cả 4 đứng về phía phản biện.** Đây là kết quả TỐT: 3 hướng sai đã đóng bằng số, 0 dòng code sản phẩm bị chạm.
>
> ### ⛔ C1 — `Φ` → `Ø`: **NO_GO. Tiền đề của cả mục là SAI.**
> **Đo trên code thật:** `_norm('Φ10') == _norm('Ø10') == 'ø10'` (do `unaccent()` có `.lower()` + `_DIAM_RE` `tools_core.py:46-51`) ⇒ **TÌM KIẾM ĐÃ KHỚP Φ RỒI**. Mọi lập luận "vá để tăng recall" là **SAI**. Rổ neo cũng bất biến với Φ↔Ø (cả hai nằm trong dải `À-ỹ` của lookbehind `_NUM_IN_STR_RE`, `mcp_bridge.py:670`) ⇒ "vá để sinh neo mới" cũng SAI.
> **Nếu vẫn vá (thêm Φφ vào `_MAHIEU_RES[4]`) thì đó là per-claim thu nhỏ:** `_MAHIEU_RES` chạy trên **CÂU TRẢ LỜI** (`mcp_bridge.py:825`), nên strip Φ đồng thời **xoá số đường kính khỏi rổ neo của câu trả lời** ⇒ mọi câu **tổng-hợp/cộng-dồn** (đầu ra lõi của phần mềm bóc khối lượng) mất chỗ bám. Đo: *"Tổng khối lượng thép Φ6, Φ8, Φ10 là 24331.67 kg"* → **PASS → BLOCK**. **Giết 17/26 câu ĐÚNG** (8/11 · 5/8 · 4/7 trên 3 file mang Φ), đổi lấy việc đóng **1/6 cách diễn đạt** — mà mẫu bị đóng lại chính là mẫu **Gemini ít dùng nhất** (nó viết tiếng Việt: *"đường kính 8 mm"*, *"phi 8"*, cả hai vẫn lọt 100%). Trùng đúng chốt cũ `[[project-any-grounded-giu-nguyen]]`.
> **📌 Phép đo "giết oan 0/48" của panel đo là TAUTOLOGY:** rổ neo dựng TỪ 48 chuỗi rồi lấy chính 48 chuỗi đó làm câu đúng; `tat_ca ⊆ NEO` là bao hàm cấu trúc.
> **Sự cố THẬT: 0** — 0 ký tự Φ trong 22 file log trả lời; 3 file mang Φ **chưa từng chạy battery**; 164/200 ca là mô phỏng.
> **⛔ ĐÍNH CHÍNH 2 SỐ/NHẬN ĐỊNH CỦA CHÍNH TÔI:** Φ là **65 lượt** (không phải 130) · tôi từng viết *"chú thích `vntext.py` xếp Φ vào họ mã khác là SAI"* — **câu đó mới sai**, `vntext.py:188-189` đã ghi đúng cả nhận định lẫn con số 65 từ trước.
> **Ghi sổ để không đo lại — 2 lỗ hổng phụ có thật nhưng 0 ca corpus, KHÔNG vá:** `_CI_SO` (`tools_core.py:257`) thiếu Φφ · khoá `'ØΦ10'` của `_acc_thep` (`tools_core.py:126`+`:1143` dùng chuỗi RAW — lưu ý vá `to_unicode` **KHÔNG** chữa được cái này).
> **Điều kiện DUY NHẤT để mở lại:** (i) đo giết-oan bằng câu **số DẪN XUẤT** chứ không phải chuỗi nguồn, (ii) chứng minh lợi ích còn lại sau khi trừ 5 mẫu câu bypass, (iii) có **≥1 ca Φ trong log trả lời THẬT**. Hiện cả 3 đều không có.
>
> ### ⛔ B1 — thêm `Ø/ø`, `Ü/ü` vào `_SIG`: **NO_GO ở lát này**
> **Số của panel đo bị thổi ~1,8-2,0× do ĐẾM ĐÔI:** bộ quét duyệt `modelspace + layouts + doc.blocks` mà `doc.blocks` **chứa luôn** `*Model_Space`/`*Paper_Space`. Bằng chứng cơ học trong chính dữ liệu của họ: 10.681 bản ghi → **5.861 cặp (file,handle) duy nhất**; 4.767 handle có ở cả 'model' lẫn 'block'. Số ĐÚNG: lợi ích **132 chuỗi / 13 file = 0,0103% corpus** (không phải 257); chiều hỏng nếu thêm Ø thô: **448 chuỗi** (không phải 913).
> **Hàng rào bảo vệ đường kính là MÃ CHẾT:** `bao_ve_O` kích **0/5.797** chuỗi và **không thể** khác 0 — chính panel đo tự ghi *"chuỗi có CẢ HAI loại Ø = 0"*. Bằng chứng duy nhất cho nó là chuỗi oracle **viết tay** `'cèt thÐp Ø16'` **không có trong corpus**. Tautology nằm đúng trên dữ liệu quan trọng nhất của dự án.
> **Hàng rào đó thua đúng MỘT DẤU CÁCH:** `'chØ dÉn: Ø 20'` → `'chỉ dẫn: ỉ 20'` · `'èng Ø300 vµ Ø 400'` → **bảo vệ một nửa, giết một nửa, TRONG CÙNG MỘT CHUỖI, im lặng**. Corpus chưa có ca đường kính viết cách ⇒ đó là *"chưa có ca"*, không phải *"an toàn"*.
> **🔴 Lớp hỏng THỨ HAI mà CẢ HAI panel bỏ sót (agent thiết kế tự tìm):** Ü phá **tên hãng thiết bị nước ngoài** — `'Bơm Grundfos Müller CR-32'` → `'Bơm Grundfos Mỹller CR-32'` · `'Zürich 25'` → `'Zỹrich 25'`. Umlaut là chuyện **bình thường trong bản vẽ M&E** (Müller, Wilo, Zürich, Bühler). Corpus hiện 0 ca ⇒ đúng bài học `[[feedback-tranh-overfit-quy-uoc-ban-ve]]`: **0 ca corpus KHÔNG chứng minh không thể có**.
> ⇒ 132 chuỗi (nội dung là *"nghĩa trang"*, *"quỹ tín dụng"*, tên phố — **không phải khối lượng**) đổi lấy việc chạm `to_unicode` = hàm NÓNG NHẤT repo + 36 suite đóng-băng-số. **Để CUỐI hoặc không làm.** Nếu làm thì tách **Ü riêng, Ø riêng**.
>
> ### ⛔ E2 — cờ "chưa với tới" khớp-từ-khoá cho trang in: **NO_GO**. Thay bằng 2 lát khác.
> **Panel đo ĐO SAI CHỖ:** họ đo tại `tim_kiem`/`dem_so_luong`, nhưng cờ còn bắn ở **nhánh ÂM của `tra_cuu_so_luong`** — đo lại: **103 cặp = 1,170% / 13 file** so với 13 cặp = 0,148% / 6 file. **7,9× số cặp, 2,2× số file**; **90 ca vô hình** với cổng của panel đo.
> **Lợi ích đo SAI ĐẠI LƯỢNG:** trong 893 chuỗi chỉ-có-ở-trang-in, số chuỗi **mang GIÁ TRỊ ĐO** (số + đơn vị) là **7/893 = 0,78%**, và **6/7 nằm trong `rachmop.dxf`** — file id135 đã biết, đã trong battery. **Trừ rachmop ra còn 1 chuỗi trên TOÀN corpus.** Trong 27 ca cờ bắn, **1/27** khớp chuỗi mang giá trị đo.
> **Nudge hiện tại khẳng định SAI:** `_VCD_CAU_NUDGE` (`tools_core.py:340-343`) ghi nguyên văn *"và cụm từ đang tìm CÓ ở đó"*. Dùng câu đó cho khớp `Ø6 ↔ d6` (do `_norm` ánh xạ `d→ø`) là **ép bịa CÓ CHỮ KÝ**. Sai-từ đo được: `'sơn'` ↔ `'pgđ. hồ chí **sơn**'` (TÊN NGƯỜI) · `'van'` ↔ `'đường phạm **văn** đồng'` — **đúng lớp lỗi đã dùng để NO_GO khối mồ côi**.
> **Rổ neo bị bơm 163 số** từ trang in: số tờ `'... TB.6 -1/10'` → `[-1.0, 6.0, 10.0]` = **neo ÂM**, lưới toạ độ `581000`, tỉ lệ `1:150`. (Đính chính mức nguy hiểm: `_is_grounded` có dung sai 1% nên `-1.0` **không** bảo lãnh `-1.34`; rủi ro thật là bảo lãnh **cao độ âm TRÒN bịa** `-2,0m`/`-5,0m` — mà tròn lại là dạng bịa tự nhiên nhất.)
> **THAY BẰNG 2 LÁT RIÊNG:** **(a)** câu cảnh báo **TĨNH theo FILE**, không theo từ khoá, **tuyệt đối không có mệnh đề "cụm từ đang tìm CÓ ở đó"** · **(b)** **tool đọc trang in độc lập** (số hiệu sau #34), trả `handle + text + tên layout`. **Điều kiện BẮT BUỘC của (b):** thêm tên tool vào tuple loại-trừ `mcp_bridge.py:958` cạnh `("doc_bang_nhung","phat_hien_bang_ve_net","tra_ky_hieu")` **trong CÙNG commit** để số trang in không vào rổ neo; và `ghi_chu` cố định phải nói rõ *"đây là chữ trên bản in (tiêu đề/khung tên), KHÔNG phải nội dung bảng"* — vì đo được `03.TB6-CT HO GA` có **tiêu đề** bảng ở trang in mà **thân bảng không tồn tại ở đâu cả** ⇒ model rất dễ "đọc tiếp" bằng cách bịa.
> **⚠ ĐIỀU KIỆN TIÊN QUYẾT — CHƯA AI QUÉT 22/93 FILE TO NHẤT**, gồm đúng file tên `XR-CAP NUOC ...-trangin-chiHoa.dxf` (202MB) và `rachmop`, `00.So do vi tri`, `01/02.TB6`, `Ket Sat 3T9P`. **Mọi tỉ lệ ở trên là CẬN DƯỚI.** Phải quét nốt trước khi làm (a)/(b).
>
> ### 🆕 PHÁT HIỆN MỚI KHI TỰ KIỂM NGƯỢC CA TEST C1 — BẤT ĐỐI XỨNG `Ø` vs `Φ` CÓ SẴN (chưa vá, chưa đo)
> Khi kiểm xem suite C1 có **thật sự đỏ** dưới bản vá bị bác, tôi đo được điều không ai nêu: **câu tổng-hợp ĐÚNG viết bằng `Ø` thì HÔM NAY ĐÃ BỊ HÀNG RÀO GIẾT.**
> | câu | rổ neo `{6, 8, 10, 14.57, 65.66}` (KHÔNG chứa tổng — vì tool không trả tổng) |
> |---|---|
> | `Tổng khối lượng thép **Φ**6, Φ8, Φ10 là 24331.67 kg.` | **đi qua** |
> | `Tổng khối lượng thép **Ø**6, Ø8, Ø10 là 24331.67 kg.` | **BỊ CHẶN** |
> Nguyên nhân: `Ø` vốn nằm trong `_MAHIEU_RES[4]` (`[A-Za-zØøĐđ]+[-.]?\d+…`), nên `Ø6/Ø8/Ø10` bị strip khỏi câu trả lời ⇒ số duy nhất còn lại là `24331.67` mà nó **không có trong rổ neo** ⇒ ANY-GROUNDED không có gì bảo lãnh ⇒ chặn.
> ⇒ **Lỗi "giết câu tổng-hợp đúng" KHÔNG do bản vá Φ đẻ ra — nó ĐÃ TỒN TẠI cho `Ø`, tức cho ĐÚNG cách viết phổ biến nhất.** Bản vá bị bác chỉ **mở rộng** thiệt hại sẵn có sang `Φ`. Điều này **củng cố** NO_GO, đồng thời mở một đầu mục MỚI.
> **ĐẦU MỤC MỚI (chưa vá, chưa đo, đừng tự khởi động):** *"câu tổng-hợp ĐÚNG bị hàng rào giết vì MỌI số thành phần đều bị strip như mã-hiệu"*. Phải đo tỉ lệ trên bộ 198 câu trước — có thể đây là một phần của **M2 (trả-lời-vs-từ-chối 8,7%)** trong baseline Q2. Hành vi hiện tại **đã được KHOÁ** bằng ca `P2c` để nếu ai sửa thì phải sửa CÓ Ý THỨC kèm phép đo riêng.
>
> ### THỨ TỰ CHỐT
> **1.** C1 + E2-NO_GO: ghi sổ + test khoá bất biến (**0 dòng code sản phẩm**) → **2.** quét nốt 22 file to → **3.** E2(a) câu cảnh báo tĩnh (lát nhỏ, không đụng rổ neo) → **4.** E2(b) tool đọc trang in (**ưu tiên cao nhất trong nhóm có-viết-code**, thuộc nhóm A) → **5.** B1 cuối cùng hoặc không làm.
> **⛔ KHÔNG ĐƯỢC GỘP** B1 vào E2(b): B1 đổi *nội dung chuỗi*, E2(b) đổi *phạm vi chuỗi được trả về* — gộp thì delta rổ neo không tách được nguồn.

## ✅ A3 **LIVE `af0c879`** — MÃ ĐỊNH DẠNG KHÔNG CÒN LÀM MỒI KHỚP ẢO (2026-08-01) · gate **[43/43]**
> **Verify LIVE:** `/version` = `af0c8795` · prompt `2026.07.27-kb-l3` hash `239e8b7b…` **KHÔNG đổi** · kb `e55ac112…` **KHÔNG đổi** (bản vá không chạm SYSTEM_PROMPT/kho kiến thức nên không cần A/B) · `/health` ok · `ram_mb` 135,5 · trang chủ HTTP 200 đủ 4 chuỗi frontend.
> **Bug:** `search_texts` ghép nhánh **THÔ** (chưa gỡ mã) vào rổ so khớp — `hay = _norm(vn) + " \x01 " + _norm(text)`. Tên phông / mã màu / mã AutoCAD thành **chữ để khớp**. Dự án **đã biết từ đợt trước** (chú thích `tools_core.py:301-303`: *"lỗi CÓ SẴN của search_texts"*, đo được `'C1'` → 41 hit ảo) nhưng chưa ai quay lại vá.
> **Kênh mồi lớn nhất KHÔNG phải tên phông mà là `%%C`:** `%%C10/%%C12/%%C16` → `_norm` → `%%c10…` **chứa `c1`** ⇒ hỏi cột **"C1"** trả về **mọi ghi chú thép Ø10/Ø12/Ø16**. Một mình nó = **9.147/11.597** hit ảo bị loại.
>
> **VÁ 3 CHỖ, MỘT LÁT (ship lẻ = ship lỗi — đo: chỉ vá thô mất 2/9 ca đúng; chỉ vá `vn` còn 4/7 ca ảo):**
> · **P1** `vntext._mtext_codes` — tách 3 họ mã: **TOGGLE gỡ TRƯỚC** (`\L\O\K` đang bị regex tham số ăn tới dấu `;` kế tiếp và **nuốt chữ thật**), **GIỮ nội dung `\S`** (phân số/chỉ số là DỮ LIỆU), thêm tham số `sep` + hàm public `ma_ve_trang()`. Chữ ký `to_unicode` **không đổi**.
> · **P2** `tools_core.search_texts:2004` — nhánh thô qua `_tho_khop` (gỡ mã → **KHOẢNG TRẮNG**, đổi `%%`), **fail-open** (lỗi → chuỗi gốc, KHÔNG rỗng), **cổng rẻ** (99,6% chuỗi không trả tiền regex). **GIỮ nhánh thô** — có hit đúng chỉ nó tìm ra.
> · **P3** `tools_core._build_qty_index:1825` — **BỎ** nhánh thô. Đây là đường **DUY NHẤT** nhánh thô sinh **SỐ** ra kết quả tool: `'{\f.VnAvantH|b1|i1|…;Tæng céng}'` → `_QTY_RE` hút chữ số của `|b1|` → **đẻ ra "Tổng cộng = 1"**.
>
> **⚠ HAI CHỖ GỠ MÃ THEO HAI CÁCH NGƯỢC NHAU — ĐỪNG "SỬA CHO ĐỒNG BỘ":**
> · nhánh **THÔ** = **khoảng trắng**. Gỡ thành rỗng thì **DÁN CHỮ và ĐẺ RA CHỮ KHÔNG CÓ THẬT**: `'{\f..;WC C}Hç{\f..; T}HÊ{\f..;P N}HÊ{\f..;T LÀ }2700'` → `…cthepn…` = **mọc chữ "thép"** giữa ghi chú hoàn thiện kiến trúc, khớp luôn `thép` / `thống kê thép`.
> · **`to_unicode`** = **GIỮ RỖNG**. Khoảng trắng ở đây **CHẺ SỐ THẬT**: `mác 200#`→`mác 2 0 0#` · `1760`→`176 0` · `0.95`→`0.9`+`5` (dải cao độ) · `F14`→`F 14`.
>
> **TỰ KIỂM NGƯỢC — 95 file / 2.652.196 chuỗi (cổng xanh không đủ, và lần này cổng ĐÚNG LÀ mù: 0/35 lời gọi `search_texts` trong 3 suite cũ phụ thuộc nhánh thô):**
> | đại lượng | kết quả | ngưỡng |
> |---|---|---|
> | `vn` đổi | **437** (0,0165% corpus) | — |
> | đổi **ngoài** 2 họ dự kiến | **0** | =0 ✅ |
> | `vn` **ngắn đi** (mất dữ liệu) | **0/437** | =0 ✅ |
> | `cao_do`·`thep_kg`·`thephinh_kg`·`n_sheet`·`n_qty`·`n_text` | **lệch 0**, 15/15 file | delta=0 ✅ |
> | hit từ khoá **chữ thuần** | 6.680→6.661 = **−0,3%**, toàn bộ mức giảm là `nha de xe` (chính bug) | ✅ |
> | hit từ khoá **có chữ số** | 36.706→25.109 = **−31,6%** (`C1` −9.147 · `C2` −1.799 · `A1` −471 · `T1` −91) | kênh ảo ✅ |
> | regex gỡ mã có khớp chữ thật? | 4.989 lượt, **10/10 chữ cái đều là mã MTEXT chuẩn, 0 lượt khớp chữ lạ** | ✅ |
> | entity `TEXT` (không phải MTEXT) chứa `\` | 3, **0 cái bị đổi** | ✅ |
>
> **LỢI ÍCH PHỤ — CỨU DỮ LIỆU:** cả 437 ca đều **dài ra**, đều là ký hiệu thép lấy lại chỉ số dưới: `(D)`→`(D1)/(D2)/(D3)` (trước đây **3 mã khác nhau SẬP THÀNH MỘT**) · `L ³ 3Dd`→`Lneo1 ³ 3Dd1` · `H < 40D`→`Hcv < 40D`. Nguồn của `D1 +15`, `D2 +15`.
> **RỦI RO ĐÃ ĐÓNG:** 313/437 chuỗi **sinh thêm chữ số** ⇒ nguy cơ neo giả / cao độ giả. Đã đo: **6 đại lượng số lệch 0**. (253/437 nằm trong định nghĩa khối, không vào `self.texts`; 184 chạm đường sản phẩm.)
>
> **TEST:** `tests/test_ma_dinh_dang.py` **35 ca / 6 nhóm**, check.sh **42→43 bước**. Chạy **TRƯỚC** khi vá đã ĐỎ đúng chỗ (A1 `nhà để xe`=1 hit ảo; B3-B8 chứng minh `to_unicode` **đang xoá dữ liệu thật**). 40 suite cũ **giữ nguyên từng con số**, tổng ca 1.467→1.502.
>
> **📌 HAI LẦN BỘ KIỂM CỦA CHÍNH TÔI HỎNG TRONG LÁT NÀY (cùng họ bài học 2026-07-31):**
> ① bộ phân loại "mất oan" định nghĩa mất-oan = *token có trong `vn`* — nhưng token có trong `vn` thì haystack MỚI (vốn chứa `vn`) vẫn khớp ⇒ hit không thể biến mất ⇒ **luôn trả 0 bất kể bản vá an toàn hay không**. Số "0 mất oan" đầu tiên là **TAUTOLOGY**.
> ② bộ kiểm "đoạn bị xoá có phải mã không" cũng gần tautology (`_mtext_codes` chỉ xoá được đúng cái regex nó khớp) **và** quá chặt — `difflib` cắt span tuỳ tiện nên `{\H0.7x;\S^` bị gắn cờ oan.
> ⇒ Câu hỏi **có giá trị** là: ***regex gỡ mã có bao giờ khớp vào chữ người đọc thấy không?*** — trả lời được bằng số thật: **0/4.989**.
> ③ Ngoài ra 2 ca test tự viết bị hỏng, tự bắt: A7 đậu vì chuỗi **thiếu token** chứ không nhờ bản vá; E2 so `None == None` = **xanh vĩnh viễn**.
>
> **⛔ TÁCH KHỎI LÁT NÀY, CÓ LÝ DO SỐ (đừng gộp):** `tools_core.py:1764` `_tok_ban_ve` (nhánh thô bơm +2.328…2.694 token giả/77 file, **155 token có dạng handle** → nới cảnh báo handle-bịa; **chiều "vá xong có nổ oan không" CHƯA AI ĐO** ⇒ NO_GO) · `:1283` `%%U` nhận diện sheet (nhánh thô ở đây là **BẮT BUỘC**; có lỗi thật **1.162 chuỗi `%%u` chữ thường lọt** do `startswith` phân biệt hoa-thường, nhưng sửa là đổi **danh sách sheet mọi file** → lát riêng) · `:1122/1126` ATTRIB bảng thép (20 ô/26.755, đổi **KHOÁ bảng thép**) · `vntext._looks_tcvn3` misfire chuỗi trộn phông (**gốc rễ** khiến nhánh thô còn phải sống; đụng `vn` toàn corpus → lát riêng).
> **CHƯA CHỨNG MINH:** chưa đo xuôi dòng qua Gemini, chưa chạy `battery.json`, chưa A/B. Chỉ được nói *"bớt N hit ảo, giữ nguyên mọi số"* — **KHÔNG** được nói *"cải thiện chất lượng trả lời"*.

## ⛔ 1.02 & 1.03 **CHƯA XONG** — HAI NHÃN "done" LÀ SAI, ĐÃ SỬA (2026-08-01, `wf_4efbe809-21b`)
> **Bối cảnh:** user hỏi *"1.02 và 1.03 đã đều xong rồi đúng không?"*. Tôi trả lời "1.03 ✅ xong" — **SAI**. Cho chạy 4 phép đo + 4 phản biện đối kháng (**0/4 phép đo bị bác**, nhưng phản biện sửa số ở 4 chỗ). Kết quả: **cả hai đều chưa xong.** `feature_list.json` đã sửa: `vntext` **done → partial**, thêm mục mới `doc-chu-trang-in-paperspace`, cập nhật `doc-chu-trong-khoi` (70 mục: 61 done · 2 partial · 7 deferred).
>
> **📌 VÌ SAO LỌT — DẠNG MỚI CỦA "CỔNG XANH KHÔNG ĐỦ", NGUY HIỂM HƠN CÁC LẦN TRƯỚC:** hai lần trước là *bản vá chạy mà cổng mù*. Lần này là **một PHẦN VIỆC CHƯA BAO GIỜ BẮT ĐẦU mà cổng vẫn xanh**. Mục 1.03 có tiêu đề **ba vế** — *"nắn phông cũ (**VNI**, phần TCVN3 còn sót, ký hiệu Ø vỡ)"* — được đánh dấu done+LIVE khi mới làm 2 vế. `test_vntext` **53 PASS nhưng 0/53 ca chạm VNI**, nên cổng **không thể đỏ**. ⇒ **LUẬT MỚI: đầu mục có tiêu đề nhiều vế (dấu phẩy / "và" / ngoặc liệt kê) thì phải tách từng vế và đòi MỘT CON SỐ cho MỖI vế trước khi đánh dấu xong; và hỏi "suite hiện có bao nhiêu ca chạm vế này?" — nếu 0 thì cổng xanh không nói gì về vế đó.** Tương tự, đầu mục bị **THAY bằng cách làm khác** (1.02 → tool riêng thay kho chữ chung) phải hỏi lại **phần nào của mục tiêu GỐC vẫn chưa đạt**.
>
> ### 1.03 — 3 vế, mới làm 2
> | vế | trạng thái | số |
> |---|---|---|
> | **VNI** | ❌ **0 dòng code** | `grep VNI` = 2 hit **đều là chú thích** (`vntext.py:138`, `tools_core.py:1948`); bảng mã trong `to_unicode` **chỉ 1** (`_TCVN3`); nắn đúng **0/1.422 = 0,0%**; **0/53 ca test** chạm VNI |
> | TCVN3 còn sót | ✅ phần lớn, **còn 3 chỗ rò** | đúng **107.764/132.203 = 81,5%** (trước vá 70,9%), **+16.571 cứu / −0 hỏng** |
> | ký hiệu Ø vỡ | ✅ `%%C` · `Φ` = **NO_GO có số, không phải việc còn thiếu** | `%%C`: **0 mất / 1.754 lượt** · `Φ` U+03A6 **65 lượt/3 file** (KHÔNG phải 130) — xem khối C1 bên dưới |
>
> **Hệ quả thật (chạy engine thật, 3 đơn vị vẽ):** gõ **"phòng" → 0 kết quả** trên file kiến trúc có **34 đoạn ghi `PHOØNG HOÏC 1…18`** · **"giáo dục" → 0** dù bản vẽ ghi `PHOØNG GIAÙO DUÏC VAØ ÑAØO TAÏO HUYEÄN GIA LOÄC` · **cùng file đó "phòng" (phần TCVN3) = 51** ⇒ **engine KHÔNG hỏng, thiếu bảng mã**. 9 từ khoá có đáp án biết trước đều 0: PHOØNG 0/109 · THEÙP 0/112 · HOÏC 0/91 · MAËT BAÈNG 0/40.
> **🔴 NẶNG HƠN BỎ SÓT — KHỚP SAI TỰ TIN (= việc A3):** `tim_kiem('nhà để xe')` = **3 kết quả**, khớp vào `NHAØ XE GIAÙO VIEÂN` trong khi bản vẽ **KHÔNG có chữ "để"**; token `de` đến từ **mã phông `\fVNI-Helve-Condense`** lọt vào nhánh raw của rổ tìm kiếm. **BÁC TRỰC TIẾP** chú thích `tools_core.py:1948` (*"chữ garble sẽ KHÔNG khớp được → chiều an toàn"*): file VNI **vừa bỏ sót VỪA BỊA**.
> **Còn rò ở vế TCVN3:** `Ø/ø` **278 lượt/19 file** (`p.nghØ gv` = "p.nghỉ gv") vì `Ø` **cố ý bị loại khỏi `_SIG`** — cả thước đo của dự án lẫn của agent đo đều mù với ca này · `Ü/ü` **66 lượt/3 file** (`nghÜa trang`) · **DIMENSION/TOLERANCE 31 lượt/4 file**, thuộc vùng **7.583 chuỗi CHƯA TỪNG được soi** (mọi phép đo trước chỉ quét TEXT/MTEXT/ATTRIB/ATTDEF, trong khi sản phẩm CÓ đọc — `tools_core.py:1128`).
> **`Φ`** nằm đúng dòng `- Trọng lượng thép có đường kính Φ10 = 4385.64 kg`. ⛔ **ĐÍNH CHÍNH 2026-08-01: hai điều tôi ghi ở đây ban đầu đều SAI** — (a) số đúng là **65 lượt**, không phải 130; (b) tôi viết *"chú thích `vntext.py` xếp Φ vào họ mã khác là SAI"* — **chính câu đó mới sai**: `vntext.py:188-189` ngay bên dưới đã ghi đúng nguyên văn *"Φ gần như chắc là người vẽ gõ 'phi' Hy Lạp thay cho Ø — nhưng 65 lượt, và sửa nó là đổi KÝ HIỆU ĐƯỜNG KÍNH nên phải đo riêng"*. Chú thích cũ đã đúng cả nhận định lẫn con số. Xem khối **C1 NO_GO** bên dưới.
>
> ### 1.02 — 2 vế, một nửa xong, một mù hoàn toàn
> · **Khối ĐƯỢC CHÈN** ✅ **9.105** chuỗi (4.732 vô hình với `tim_kiem`)/70 file — nhưng qua **tool riêng #34**, ***không phải kho chữ chung*** (`self.texts` vẫn chỉ gom modelspace, `tools_core.py:1100→1263`).
> · **Khối MỒ CÔI** ❌ 5.738 chuỗi/30 file — ⚠ **50,5% con số đó là MỘT file toàn mã escape `%%199`**, không phải nội dung thật ⇒ trừ ra còn **~1.900–2.500**. **Đừng lấy 5.738 làm cớ**, phải đo chất lượng nội dung trước.
> · **Chữ TRANG IN** ❌ **MÙ HOÀN TOÀN, không tool nào đọc** — **851** chuỗi riêng biệt (685 vô hình)/24 file; bộ trích thô độc lập 100/100 file đếm **3.252 đối tượng**/25 file. Đang bị nuốt: `MẶT BẰNG TỔNG THỂ TUYẾN CỐNG DỊCH VỤ LƯU VỰC TB.6 -10/10` · `DANH MỤC BẢN VẼ PHẦN KẾT CẤU ĐƠN NGUYÊN 1: 3 TẦNG 12 PHÒNG` — tức **tiêu đề bản vẽ / danh mục / khung tên**.
> **🔴 THẤT BẠI IM LẶNG (phát hiện mới của phản biện):** với **khối mồ côi và chữ trang in**, `co_o_vung_chua_doc = **None**` ⇒ máy trả 0 kết quả mà **KHÔNG bật cả cờ cảnh báo** (chỉ khối ĐƯỢC CHÈN mới bật). Xác nhận corpus thật (`00.So do vi tri.dxf`): 3 chuỗi chỉ-có-ở-trang-in đều `tim_kiem=0, dem_so_luong=0, #34=False`, **không cờ**. Đúng thứ dự án đã chốt là không chấp nhận được.
>
> ### ⛔ BỐN SỐ CŨ CỦA CHÍNH DỰ ÁN BỊ PHẢN BIỆN SỬA
> · *"768 chuỗi `Ä/Å/Û/Φ`"* → khối lượng VNI thật chỉ có **cận dưới 1.422**, cận trên ~14.381 — **chưa ai đo chính xác**.
> · *"21/92 file khai phông VNI (22,8%)"* → **thổi phồng**; file thật sự **chứa chữ mã VNI** chỉ **10/91 (11%)**. `03.CTN ngoai nha.dxf` khai `VNI-Helve-Condense.TTF` nhưng ruột là TCVN3 và **đang nắn ĐÚNG**.
> · *"907/907 = 100% còn dấu hiệu VNI"* → **TAUTOLOGY** (bộ dò chọn theo `[AEIOUY]+[ÙÚÛ]`, mà 0xD9–0xDB không có trong `_TCVN3` nên **về cấu trúc không thể ra khác 100%**). Ruột vẫn đúng qua đường không-vòng-tròn: 0/1.422.
> · *"0 chuỗi hỏng thêm"* (commit `aaea3ec`) → **không chính xác tuyệt đối**: **944 chuỗi VNI** bị đem giải mã TCVN3 (`CÖÛA SOÅ`→`CỆÛA SOÅ`). Tổng hoà **vô hại** (chỉ **8,6% xa đáp án hơn**, 46 chuỗi GẦN hơn, độ giống TB 0,7065→0,7055 = phẳng) — *"đổi" ≠ "tệ hơn"* — nhưng **cơ chế CÓ THẬT**.
> · Mẫu 1.02 khai *"đã phủ 88/88 file"* → trên đĩa có **100 file .dxf**; đo nốt 12 file thiếu: tổng mù **5.145 → 5.745 (+11,7%)**. Khe hở này chỉ làm số mù **TĂNG** nên không lật kết luận.
>
> ### KHÔNG ĐO ĐƯỢC (nói thẳng, không lấp)
> khối lượng VNI thật (chỉ có cận dưới/cận trên) · **tỉ lệ model THỰC SỰ gọi tool #34** — điều 5 ép gọi **đã bị GỠ** khỏi `SYSTEM_PROMPT` (`mcp_bridge.py:298-308`) vì A/B lợi ích ≈ 0, nên phép đo chỉ nói **khả năng đọc của code**, không nói mức dùng thật · ATTDEF trong khối mồ côi (`_vcd_bong` cố ý bỏ, `tools_core.py:1891`) · `chinhcaodo.dxf` **code sản phẩm không mở được** (`DXFStructureError: missing ENDSEC`) mà file này CÓ `VNI-Helve` trong byte thô · **92 file `.dwg` gốc chưa convert** ở `input_files/` · DIMENSION/LEADER trên trang in · ⚠ **mẫu số tổng chuỗi lệch giữa các lần đo** (1.141.092 vs 285.413 vs 2.285.049 tuỳ phạm vi/bộ trích) ⇒ **mọi so sánh % "trước/sau 1.03" giữa HAI LẦN ĐO KHÁC NHAU là KHÔNG hợp lệ**; chỉ so được tỉ lệ nội bộ cùng một lần đo.
>
> ### VIỆC CÒN LẠI — thứ tự rẻ-mà-đau trước
> ⚠ **DANH SÁCH NÀY ĐÃ LẠC HẬU sau khi đo (2026-08-01):** A3 ✅ LIVE · **C1, B1, E2 đều NO_GO có số** — xem khối "BA NO_GO" ngay dưới. Việc CÒN LẠI thực sự chỉ là **E2(a) câu cảnh báo tĩnh** + **E2(b) tool đọc trang in** (đều cần quét nốt 22 file to trước), rồi D1+B2, E1, A1+A2.
> ~~**1. A3** → **2. E2**~~ bật cờ `co_o_vung_chua_doc` cho khối mồ côi + trang in *(NHỎ, 43/87 file — hết im lặng)* → **3. C1** `Φ`→`Ø` *(1 dòng, 130 lượt)* → **4. B1** `Ø/Ü` TCVN3 còn rò *(NHỎ–TRUNG; `Ø` vừa là đường kính vừa là dấu huyền ⇒ phải phân biệt bằng ngữ cảnh, Ø-trước-chữ-số = đường kính)* → **5. D1+B2** thêm ca VNI vào `test_vntext` + mở phạm vi đo sang DIMENSION *(đóng cổng đo)* → **6. E1** đọc trang in *(TRUNG BÌNH — cần quyết: kho chung hay tool riêng thứ hai)* → **7. A1+A2** dựng bảng mã VNI *(**LỚN, rủi ro cao nhất**)* → **8. E3/F1** cần đo thêm hoặc cần user quyết.
> **⚠ RÀNG BUỘC SỐNG CÒN CHO A1 (VNI):** nhận diện **PHẢI** dùng **dấu hiệu CẤU TRÚC** (dấu đặt **SAU** nguyên âm: **73,6%** ở phông VNI vs **9,3%** ở TCVN3), **TUYỆT ĐỐI KHÔNG dùng TÊN PHÔNG** — **11 file** tên `vn_vni.shx` nhưng **ruột là TCVN3 và đang nắn ĐÚNG**; đụng vào sẽ **phá 107.764 chuỗi đang chạy tốt**.

## ⛔ VÁ BỎ SÓT BẰNG "GỢI Ý TRONG KẾT QUẢ TOOL" = **KHÔNG ĐẠT, ĐÃ GỠ — ĐỪNG LÀM LẠI Y HỆT** (2026-08-01)
> **Tiêu chí chốt TRƯỚC khi chạy:** thắng = **≥3/11** câu bỏ sót lấy lại được **VÀ ≤2/17** câu bẫy bị phá.
> **Đã thử 2 vòng, A/B trên đúng 28 câu (`run13` trước vs `run14`/`run15` sau):**
> · vòng 1 — gắn gợi ý *"hãy gọi `tim_kiem` với từ khoá NGẮN"* vào kết quả RỖNG của `tra_cuu_so_luong` / `thong_ke_thep` / `boc_tach_kich_thuoc` → **lấy lại 1/11 · phá bẫy 0/17**
> · vòng 2 — thêm gợi ý *"rút ngắn từ khoá"* vào chính `tim_kiem` khi 0 kết quả → **lấy lại 1/11 · phá bẫy 0/17**
> ⇒ **KHÔNG ĐẠT ngưỡng đã chốt. GỠ cả hai** (giữ code sạch, không để lại rác chưa chứng minh).
>
> **📌 LÝ DO THẤT BẠI — ĐỌC TRƯỚC KHI THỬ HƯỚNG KHÁC. MODEL ĐÃ NGHE LỜI:**
> `id136` thêm `tim_kiem('taluy')` · `id130` thêm `tim_kiem('O10')` · `id37` leo lên **4 lệnh** có cả `tim_kiem('lavabo')` — **đúng từ khoá đã tự xác minh là tìm ra 2 kết quả**. Nó tìm ĐÚNG rồi **vẫn** trả "không có".
> Vì chuỗi `lavabo trẻ em` CÓ tồn tại nhưng **KHÔNG chứa chiều cao**; số `400/450mm` nằm ở **Ô KHÁC của bảng**. Máy tìm được **NHÃN** mà không nối được sang **GIÁ TRỊ**.
> ⇒ **Nút thắt thật = GHÉP HAI MẨU CHỮ RỜI NHAU THEO VỊ TRÍ (đọc bảng theo hàng/cột)**, KHÔNG phải "không chịu tìm". **Mọi bản vá kiểu nhắc-nhở/prompt đều sẽ vô hiệu ở lớp này** — đừng tốn thêm lượt A/B cho hướng đó.
> ⇒ Và phải nói rõ: **nhiều câu "không có" ở đây là TRUNG THỰC** — máy thấy nhãn, không thấy số, nên không đoán. Đó là hàng rào chống bịa chạy ĐÚNG, không phải lỗi. Con số "8% bỏ sót" vì thế **một phần là GIỚI HẠN NĂNG LỰC (đọc bảng theo vị trí), không phải bug**.
> **GIỮ LẠI 1 thay đổi duy nhất:** bỏ chuỗi `(vd 'D1')` khỏi prose `tra_cuu_so_luong` — nó bơm `1.0` vào rổ neo. Thuộc "làm sạch rổ neo" = đòn bẩy DUY NHẤT đã chứng minh có tác dụng.
> **NẾU QUAY LẠI:** hướng còn lại là **ghép nhãn↔giá trị theo toạ độ** (đã có tiền lệ `_gan_dim_cau_kien` trong repo). Đó là việc LỚN, phải đo trước như mọi lần.

## 🎯 BỎ SÓT (recall) — ĐÃ TRUY RA NGUYÊN NHÂN BẰNG LỆNH GỌI TOOL THẬT (2026-08-01)
> **SEAM MỚI `--ghi-tool`** (bọc `br.call` phía test, **0 dòng code sản phẩm**) — lần đầu nhìn được model đã gọi tool NÀO với THAM SỐ GÌ. Dữ liệu: `run10|11|12` (26 câu chập chờn ×3) + `run13` (28 câu từ-chối-ổn-định).
>
> **⛔ HAI CON SỐ CŨ CỦA CHÍNH TÔI LÀ ẢO — ĐÍNH CHÍNH:**
> · *"13% bỏ sót chứng minh được"* → **SAI**. Bộ dò từ-khoá của tôi đếm nhầm khác-CÁCH-NÓI thành khác-NỘI-DUNG. Ví dụ id144: một lượt *"đọc được chữ 'Cọc'… không có lỗi font"*, lượt kia *"**không tìm thấy** thông tin cho thấy chữ 'Cọc' bị lỗi font"* — **cùng kết luận**, bị đếm là lệch. Đo lại 26 câu chập chờn ×2 lượt mới: **69% gọi tool Y HỆT · 73% ra CÙNG tập số** ⇒ lệch nội dung thật chỉ ~4-5 câu ≈ **2%**.
> · *"~43% bất ổn do ROUTING"* (suy từ biến thiên `n_evidence`) → **SAI**. Nhìn lệnh gọi THẬT: trên 6 câu lệch, **5/6 gọi tool y hệt cùng tham số** mà một lượt trả lời một lượt từ chối. Routing chỉ 1/6.
>
> **VẤN ĐỀ THẬT LÀ BỎ SÓT *ỔN ĐỊNH* — mọi phép so-lượt đều MÙ với nó.** 28/197 câu cả 3 lượt đều từ chối; đọc `ky_vong` thì **~17 câu từ chối là ĐÚNG** (câu bẫy `bay_ao_giac`/`bay_lac_de`), còn **~11 câu là bỏ sót THẬT**. Tự kiểm 5 ca trên bản vẽ — **dữ liệu CÓ và tìm ra dễ**: `Thép Ø10 L=6cm` (2 kq, đúng nguyên văn ky_vong) · `lavabo trẻ em` (2) · `nilon lót chống mất nước` (6) · `Sơn phản quang màu trắng` (3) · `phòng học` (16). ⇒ quy mô ≈ **11/197 ổn định + ~4 chập chờn ≈ 8%**.
>
> **NGUYÊN NHÂN — 2 NHÁNH, đọc thẳng từ `tool_goi`:**
> **(A) 6/11 — chọn tool CHUYÊN DỤNG, tool trả rỗng, rồi KẾT LUẬN "không có" mà KHÔNG BAO GIỜ thử tìm theo chữ:**
> `id30` chỉ `tra_cuu_so_luong('phòng học')` (mà chữ "phòng học" có 16 lần) · `id37` chỉ `boc_tach_kich_thuoc('lavabo trẻ em')` · `id94` chỉ `tra_cuu_so_luong('Lanh to LT-1200B')` · `id130` chỉ `thong_ke_thep(duong_kinh='O10')` (đáp án là CHỮ "Thép Ø10 L=6cm") · `id131` chỉ `tra_cuu_so_luong` ×2 · `id179` **0 lệnh gọi nào**.
> **(B) 5/11 — CÓ tìm theo chữ nhưng dùng CẢ CỤM CÂU HỎI thay vì từ khoá đặc trưng:**
> `id136` tìm `'He so mai taluy (m)'` → 0; bản vẽ ghi `m = 2.0` · `id142` tìm `'biển báo sơn màu'` → 0; bản vẽ ghi `Sơn phản quang màu trắng` (tìm `'phản quang'` ra 3) · id81/id58/id187 tương tự.
>
> **THIẾT KẾ ĐỀ XUẤT (chưa cài):** nhánh (A) vá ở **TẦNG TOOL, không phải prompt** — khi tool chuyên dụng trả **0 kết quả**, chính kết quả tool kèm thêm trường gợi ý *"chưa thử tìm theo chữ; hãy gọi `tim_kiem` với từ khoá NGẮN"*. Model đọc nó **đúng lúc cần**, mạnh hơn hẳn một luật prompt toàn cục (lịch sử `_P_R5`: nudge prompt đo A/B ra 4/8 vs 5/8 = trong nhiễu). Nhánh (B) khó hơn, cần hướng dẫn tách từ khoá — **để sau**, đo (A) trước.
> ⚠ Chạm `tools_core.py` = code sản phẩm ⇒ theo nếp dự án phải red-team + A/B trước khi ship. **CHƯA CÀI GÌ.**

## 🟡 (b2) LUẬT "CÂU CÓ *TỔNG* + SỐ KHÔNG TRUY ĐƯỢC NGUỒN" — **HỨA HẸN, CHƯA ĐỦ BẰNG CHỨNG ĐỂ CÀI**
> **Đo bằng dữ liệu THẬT có rổ neo, lần đầu.** Chạy 33 câu (những câu từng sinh khẳng định "tổng") = **223 giây**, 33/33, 0 hỏng → `tests/battery_runs/run09.jsonl`.
> **CÁCH LẤY RỔ NEO — 0 DÒNG CODE SẢN PHẨM:** bọc `mcp_bridge._guard_text` **từ phía test** (`run_battery.py --ghi-ro-neo`); nó nhận đúng `tool_numbers` ở `mcp_bridge.py:986` và `:1006`.
> ⛔ **ĐỪNG thêm `tool_numbers` vào dict trả về của `tra_loi_ai`** — `app.py:625` làm `return jsonify(r)`, tức **bơm toàn bộ số nội bộ của tool ra trình duyệt** ở mọi câu hỏi. (Đây là đề xuất SAI của chính tôi, đã tự bác.)
>
> **📌 PHÉP ĐO ĐẦU TIÊN LÀ PHÉP ĐO HỎNG — GHI LẠI ĐỂ KHÔNG LẶP:** regex `tổng…{0,40}(\d…)` cho **0 gắn cờ**, tưởng "sạch tuyệt đối". Thực ra nó vớ phải **"304" trong "INOX 304"** trước khi tới `1344.33`. Bộ trích hỏng → luật không bao giờ kích. Phải đổi sang **quét theo CÂU** (câu chứa "tổng" → mọi số đo-lường trong câu đó).
>
> **KẾT QUẢ (sau khi sửa bộ trích):**
> · 27/33 câu có mệnh đề "tổng" · **gắn cờ 2** (7% câu-có-tổng · 6% toàn bộ) · **0 báo động giả trên 25 câu còn lại** (tổng do tool trả đều truy được nguồn — vd id38 `564.8` và `3545.9` đều grounded).
> · **Cả 2 ca gắn cờ đều THẬT và đều CỘNG SAI:** cùng 9 mục inox (tổng đúng **1384,83**), model phát **1384,33** (id32, lệch 0,5) và **1344,33** (id193, lệch 40,5).
> · **Độ bỏ sót:** toàn corpus chỉ **5/33** câu có số đo-lường không-truy-nguồn; 2 ca là tổng bịa (bắt), 3 ca còn lại là số nguyên nhỏ (5.0, 5.0, 10.0) trong câu KHÔNG khẳng định tổng → bỏ qua **có chủ ý** (chính là loại dễ báo oan).
> · **Bắt được đúng thứ B1 mù**: tổng cộng SAI.
>
> **⚠ ĐỪNG ĐỌC "2/2 = 100%" LÀ ĐÃ CHỨNG MINH:** id32 và id193 **cùng rơi vào MỘT bảng inox 9 dòng** ⇒ đây là **MỘT hiện tượng quan sát 2 lần, không phải 2 bằng chứng độc lập**. Thêm nữa: mẫu 33 câu được CHỌN vì trước đó từng sinh "tổng" (mẫu đã làm giàu), 1 lượt, 1 bản code, 3 bản vẽ.
> **NẾU LÀM TIẾP:** (1) mở rộng mẫu ra cả 198 câu + ≥2 lượt để có ca độc lập; (2) **hành động phải là GẮN CỜ/CẢNH BÁO, KHÔNG phải thay câu trả lời** — lịch sử per-claim đã NO_GO vì giết câu đúng; (3) red-team 2 tầng trước khi chạm `_guard_text`. **CHƯA CÀI GÌ VÀO SẢN PHẨM.**

## ⛔ (b) BỘ DÒ "TỰ CỘNG SỐ" KIỂU TỔNG-TẬP-CON = **NO_GO CÓ SỐ — ĐỪNG LÀM LẠI**
> Đo offline trên **595 câu trả lời THẬT** (3 lượt × 198, `run02|03|04`), **0 đồng API**. Luật chốt TRƯỚC khi nhìn số: *tồn tại số T và tập con ≥3 số KHÁC trong CHÍNH câu đó với |sum(S) − T| ≤ max(0,01; 0,1%·T)*.
> · chạy trên `tat_ca`: gắn cờ **25/595 = 4,2%** · chạy trên `do_luong` (sạch handle): **13/595**.
> · **CHẤM TAY TOÀN BỘ: gần như KHÔNG ca nào là "model tự cộng" thật.** Rác điển hình: `8 = 1+2+5` (**4 lần**, là "8 loại lan can" vs số bộ từng loại) · `6 = 1+2+3` (2 lần) · `34 = 9+10+15` · `53 = 2+6+45` · `1000 = 2+30+43+307+618` (1000 là số đối tượng TEXT) · **`51841 = 2+10+51842`** — đó là **HANDLE**, không phải số đo.
>
> **🔴 HỎNG Ở TẦNG CẤU TRÚC, KHÔNG PHẢI Ở NGƯỠNG — thử ngay trên ca đã đẻ ra ý tưởng (id193):**
> | lượt | số model phát | bộ dò |
> |---|---|---|
> | run02 | **1344,33 — SAI 40,5 kg** (ca GÂY HẠI) | **TRƯỢT, không gắn cờ gì** |
> | run03 | 3545,9 (dẫn nhầm, không tự cộng) | không có gì để bắt |
> | run04 | 1384,83 (tự cộng, ĐÚNG số học) | bắt được — **kèm 1 báo động giả** (357,95) |
> ⇒ **Bộ dò chỉ bắt được tổng CỘNG ĐÚNG, và mù với tổng CỘNG SAI** — vì tổng sai thì theo định nghĩa nó *không* bằng tổng tập con nào. Mà **tổng cộng sai mới là cái gây hại**. Siết ngưỡng/đổi kích thước tập con KHÔNG chữa được điều này.
> ⇒ Cộng thêm: với 5-15 số/câu, trùng-hợp tổng-tập-con của số nguyên nhỏ là **gần như chắc chắn xảy ra**.
>
> **HƯỚNG THAY THẾ (chưa đo được, cần 1 thứ rẻ):** luật **"số đứng sau cụm TỔNG mà KHÔNG có trong rổ neo"**. Cụm `tổng…<số>` xuất hiện **57/595 = 9,6%** câu — cỡ mẫu vừa phải. Thử tay trên id193: `1344,33` không có trong rổ → **BẮT ĐÚNG** · `1384,83` không có trong rổ → bắt (vẫn là vi phạm `_P_R2` dù cộng đúng) · `3545,9` **CÓ** trong rổ (tool trả) → **KHÔNG bắt, đúng**. Hình dạng hứa hẹn hơn hẳn.
> ⚠ **NÚT THẮT:** rổ neo (`tool_numbers`) **KHÔNG được lưu** trong bản ghi lượt chạy, nên KHÔNG đo được offline. Muốn đo cần `tra_loi_ai` phơi `tool_numbers` ra (chạm **code sản phẩm** `mcp_bridge.py`) rồi chạy lại battery — sau đó đo **miễn phí** trên dữ liệu mới. **CHƯA LÀM, chờ user quyết.**

## 🔍 id193 ĐÃ SOI XONG (2026-07-31) — **2 lỗi TÁCH BIỆT, cái nặng hơn thì phép đo ổn định KHÔNG THẤY**
> Câu hỏi: *"Tổng khối lượng inox lan can cầu thang là bao nhiêu kg?"* (`doc_thieu`, `loi_san = "doc thieu"`).
>
> **LỖI A — TRƯỢT RECALL, ỔN ĐỊNH 3/3 LƯỢT (nặng hơn, và VÔ HÌNH với M1/M2/M3).**
> Đáp án nằm nguyên vẹn ở handle **`60E44`**: *"ghi chú: (tính trên 1 cầu thang) - khối lượng inox lan can (inox 304): + tay vịn inox d60 dày 2mm: 27,8m = 80,52 kg. + tay vịn inox d40: 20m = 37,84 kg. + tay đỡ inox 20x20x1.5mm: 38 cái = 3,18 kg. + inox hộp 30x30x2mm: 49,3 kg. + inox hộp 25x25x1.5mm: 165,82 kg."*
> **Cả 3 lượt có Y HỆT 10 handle, KHÔNG lượt nào chứa `60E44`** ⇒ model chưa bao giờ lấy được nó, không phải "thấy rồi bỏ qua".
> **Truy được model đã hỏi gì:** truy vấn `"TỔNG KHỐI LƯỢNG"` → trả đúng **10/10 handle** model dùng, và **KHÔNG** chứa `60E44`. Trong khi MỌI truy vấn bám CHỦ ĐỀ câu hỏi đều tìm ra, ở hạng rất cao:
> | truy vấn | số kq | hạng của `60E44` |
> |---|---|---|
> | `lan can cầu thang` | 2 | **1** |
> | `lan can` | 24 | **1** |
> | `khối lượng inox` | 10 | **2** |
> | `inox 304` | 11 | **2** |
> | `inox` | 59 | 9 |
> | `TỔNG KHỐI LƯỢNG` | 10 | **không có** |
> ⇒ **TOOL KHÔNG HỀ CÓ LỖI** (đã bác giả thuyết bug tool bằng số). Lỗi là model **truy vấn theo HÌNH DẠNG ĐÁP ÁN nó muốn ("tổng khối lượng") thay vì theo CHỦ ĐỀ CÂU HỎI ("inox lan can cầu thang")** — rồi rơi đúng vào một bảng tổng KHÔNG liên quan. Đây chính là cái bẫy `doc_thieu` đã gài, và hệ sập 3/3.
>
> **LỖI B — TỰ CỘNG SỐ, vi phạm luật có sẵn (đây mới là phần M3 bắt được).**
> `_P_R2` ghi rõ **"KHÔNG tự cộng/trừ/tính"**. Trên CÙNG 10 mục đó: lượt 2 TUÂN THỦ (*"Hệ thống không tự cộng…"*) nhưng dẫn nhầm **3545,9** = TỔNG THÉP HÌNH; lượt 3 tự cộng ra **1384,83** (đúng số học); lượt 1 tự cộng ra **1344,33** — **SAI 40,5 kg**. Tự kiểm: tổng đúng của 9 mục = 1384,83. ⇒ **model phá luật ở 2/3 lượt, và khi phá thì sai 1/2 số lần.** Hàng rào ANY-GROUNDED không chặn được vì 9 số thành phần đều truy được nguồn — đúng điểm yếu đã ghi sổ, và **đòn bẩy đúng ở đây là chặn việc TỰ CỘNG, không phải đổi luật phán quyết**.
>
> **📌 BÀI HỌC PHƯƠNG PHÁP:** Q2 gắn cờ id193 vì lỗi B. Lỗi A **nặng hơn** nhưng M1/M2/M3 **không thể thấy** vì nó SAI GIỐNG NHAU cả 3 lượt — đúng cảnh báo in sẵn trong `do_on_dinh.py`: *"đây là ĐỘ ỔN ĐỊNH, KHÔNG phải ĐỘ ĐÚNG; ba lượt cùng sai giống nhau vẫn cho 0% mâu thuẫn"*. ⇒ **Không được dùng M3 làm thước đo chất lượng.** Muốn bắt lớp A phải chấm theo `ky_vong` (việc riêng, chưa làm).
> **CHƯA VÁ GÌ.** Hai hướng, đều cần đo trước: (a) lỗi A — prompt-nudge "truy vấn theo chủ đề câu hỏi trước, đừng tìm thẳng từ 'tổng'", phải A/B có mục tiêu; (b) lỗi B — bộ dò tất định "một số trong câu trả lời = tổng các số khác trong CHÍNH câu đó mà không có trong rổ neo" → cần đo tỉ lệ báo động giả trên 594 câu trước.

## 📊 Q2 XONG — BASELINE ĐỘ ỔN ĐỊNH N=3 (2026-07-31) · **M3 = 13,0%**
> **Tiêu chí ĐỊNH TRƯỚC ở `harness/Q2_TIEU_CHI_TRUOC_KHI_CHAY.md`, commit `aae3109` — TRƯỚC khi có bất kỳ số nào.** Đọc file đó trước khi trích số ở đây.
> **Dữ liệu thô:** `tests/battery_runs/run02|03|04.jsonl` (**gitignored**, chỉ có trên máy dev) · sidecar `_meta/`. `run01` bị LOẠI (code_hash `bdffe2ea`, trước 1.03/1.04 — cổng chống-trộn của 1.06 **tự từ chối** `--tiep`, đúng vai trò).
>
> **3 CỔNG HỢP LỆ — ĐẠT HẾT:** 198/198 câu cả 3 lượt · hỏng hạ tầng **0,0% / 0,0% / 0,5%** (1 câu id127, trần 5%) · 4 hash giống nhau (`prompt 239e8b7b` · `kb e55ac112` · `code 319de40e` · `battery 5f29111a`). Thời gian: 1232s / 1317s / 1532s.
>
> | chỉ số | giá trị |
> |---|---|
> | **M1 — mâu thuẫn SỐ** | **4,3%** |
> | **M2 — trả lời vs từ chối** | **8,7%** |
> | **M3 = M1+M2 (quyết định)** | **13,0%** → dải **10–25%** |
> | bao hàm (chẩn đoán) | 10,4% · cặp tệ nhất 5,1% |
> | macro-average 12 nhóm | 7,3% |
>
> **ĐỌC ĐÚNG CON SỐ:** **M2 gấp ĐÔI M1.** Bất ổn chủ đạo KHÔNG phải "hai lượt cho số đá nhau" mà là **"lúc trả lời được, lúc bảo không có"** — tức hàng rào chống bịa đang giữ vững, cái chập chờn là **RECALL**. Tỉ lệ từ chối 3 lượt sát nhau (31,5 / 34,5 / 33,0%) nên M1 thấp KHÔNG phải do một lượt từ chối nhiều hơn (đã kiểm đúng cảnh báo trong công cụ).
> **Theo nhóm:** ổn định tuyệt đối `thep` 0%/0% · `so_luong` 0%/3,5% · `ky_thuat_vs_thuc_te` 0%/6,1%. Tệ nhất `bay_lac_de` 28,6% mâu thuẫn · `doc_thieu` 26,3%/21,1% · `font_loi` 11,1%/22,2%.
>
> **TRUY NGUYÊN NHÂN (bắt buộc theo luật đã đăng ký cho dải 10-25%) — tách được 2 nhóm GẦN BẰNG NHAU, đo bằng biến thiên `n_evidence`:**
> · câu **BẤT ỔN** (46): biến thiên n_evidence trung bình **5,1**, chỉ 57% có biến thiên = 0
> · câu **ỔN ĐỊNH** (151): biến thiên trung bình **0,8**, **93%** có biến thiên = 0
> ⇒ **~20/46 (43%) = ROUTING** — Gemini gọi tool/từ khoá khác nhau nên gom được bộ bằng chứng khác nhau. Ví dụ sống: **id21** lượt 1 tìm ĐÚNG *"xà gồ thép hộp 40x80x2mm: 672m — 2472.64 kg"* (khớp `ky_vong`) trong khi lượt 2+3 trả *"không có thông tin"*; **id82** lượt 1+3 ra CB300-V/260MPa (n_ev=19) còn lượt 2 nói không có (n_ev=**3**).
> ⇒ **~26/46 (57%) = SINH VĂN BẢN** — CÙNG bộ bằng chứng, khác câu trả lời (id26/id27/id28/id35/id55…). Không phải routing.
> ⚠ **KHÔNG tìm thấy bug TOOL nào** trong nhóm này — nói thẳng thay vì bịa ra việc vá cho khớp luật.
> 🔴 **CA ĐÁNG LO NHẤT — id193** (`doc_thieu`, bất đồng 3/3 cặp): 3 lượt cho **3 tổng khác nhau** cho cùng câu hỏi khối lượng inox: **1344,33 kg / 3545,9 kg / 1384,83 kg**, cùng `n_ev=10`. Con số **3545,9** chính là TỔNG THÉP HÌNH — đúng thứ **rule 8b CẤM gộp** (xem lịch sử bug id38/id22). Đây là ứng viên vá số 1, nhưng phải ĐO trước khi sửa.
>
> **BƯỚC TIẾP ĐỀ NGHỊ:** (a) id193 — soi vì sao model gộp inox vào tổng thép hình; (b) nhóm ROUTING: thử prompt-nudge có phạm vi + đo A/B (đúng khuôn `[[feedback-do-thay-doi-prompt-ab]]`); (c) nhóm SINH VĂN BẢN: gần như không vá được bằng prompt — cân nhắc chấp nhận & khai báo. **Chưa làm gì trong số này.**

## ✅ E2E LIVE `7022aad` — 1.03 + 1.04 XÁC MINH TRÊN MÁY THẬT (2026-07-31)
> **LIVE verify:** `/version.commit` = `7022aad6…` = HEAD = origin · `prompt_hash` `239e8b7b…` **KHÔNG đổi** · `kb_hash` `e55ac112…` **KHÔNG đổi** (đợt này không chạm SYSTEM_PROMPT/kho kiến thức → không cần A/B) · `/health` ok · `ram_mb` 135,4 lúc rảnh.
> **CÁCH LÀM ĐÚNG: dựng ĐÁP ÁN CHUẨN tại local TRƯỚC, rồi mới hỏi LIVE** — "câu trả lời trông ổn" không chứng minh gì.
> **File test:** `01-TD tuyen ong ap luc.dxf` (12,8MB) — chọn vì nó bật ĐỒNG THỜI cả 1.03 lẫn 1.04. Upload OK: `so_kich_thuoc` **175** khớp local · `tong_doi_tuong` 19.442 · RAM 135 → **291,6MB** (đúng ngân sách 1 bản vẽ) · `errors 0` · `tu_choi 0`.
>
> **1.04 — ĐẬU.** Máy trả: *"khai báo đơn vị là **mét (m)**… nếu đơn vị khai báo là mét là đúng thì các số kích thước này **có thể bị sai thang đo**"* — khớp `don_vi_khai_bao="m"` + `don_vi_khai_bao_khac_mm=True`, không gắn `kho_tin` (đúng: khai báo hợp lý).
> ⚠ **NÓI SÒNG PHẲNG:** mã 6 (`m`) VỐN đã có trong bảng cũ nên phần "nhận ra đơn vị" KHÔNG mới; cái mới là **câu cảnh báo sai-thang-đo**. **Nhánh inch/feet/mile của 1.04 file này KHÔNG chạm tới** — vẫn chỉ có bằng chứng local (9+1+1 file).
>
> **1.03 — ĐẬU, và đậu ở chiều MẠNH HƠN hiển thị: máy trước đây KHÔNG TÌM RA những chuỗi này.**
> | tìm | local trước | local sau | **LIVE thật** |
> |---|---|---|---|
> | "mặt bích" | 3 | 6 | **6** |
> | "ống HDPE" | 3 | 6 | **6** |
> | "cống hiện có" | 4 | 7 | **7** |
>
> Chuỗi LIVE trả về đúng là các chuỗi từng vô hình, kèm handle: `MẶT BÍCH RỖNG THÉP DN200 [24DF7D]` · `DN250 [24DF86]` · `DN100 [24E01E]` · `DÙNG CHO ỐNG HDPE [24DF75]` · `chi tiết qua cống dn500 hiện có [204836]` · `cống hiện có dn1250-btct [21AA48]`. **Quét 0 mẩu garble sót** (`MÆT BÝCH RçNG THÐP èNG DïNG hiÖn`) trong cả 3 câu trả lời.

## 📏 1.04 XONG — ĐƠN VỊ inch/feet: ĐỐI CHIẾU + LỘ MÂU THUẪN (2026-07-31, nối phiên)
> **Làm ĐÚNG như cảnh báo cũ: KHÔNG thêm bảng tra, KHÔNG tự quy đổi.** Đo `$INSUNITS` + phân bố số đo thật trên 86 file (1 file lỗi đọc):
> **mm 40 · m 24 · không khai 10 · inch 9 · feet 1 · mile 1.**
> **Khai báo sai theo CẢ HAI CHIỀU — đây là lý do không được tự sửa:**
> · 9 file khai **inch** + 1 **feet** + 1 **mile** thực chất vẽ mm — bằng chứng: giá trị hay gặp NHẤT của chúng là `110, 220, 100, 200, 300, 1200, 3000, 3300, 3600, 4200` = **đúng bộ số mm kinh điển**; một file khai **mile**, trung vị 1700 → 2.736 km.
> · NHƯNG ~9 file khai **m** thì ĐÚNG là mét thật (bản vẽ tuyến hạ tầng, trung vị 13,5–29,6 m) → với chúng, các trường `_mm` máy đang báo **lệch 1000×**. Trong đó có `01-TD tuyen ong ap luc` (trung vị 27,4) — chính file id135.
> · `$MEASUREMENT` **VÔ DỤNG** làm tín hiệu: 28/38 file khai mm cũng để `MEASUREMENT=0` (English).
> **CÁCH LÀM:** `_INSUNITS_TEN` nhận **đủ 17 mã** (trước chỉ 4/5/6, nên inch/feet/mile bị báo là *"bản vẽ KHÔNG khai $INSUNITS"* = **máy nói sai**) + `_doi_chieu_don_vi()` trả 2 cờ **BOOL, prose SẠCH SỐ**:
> · `don_vi_khai_bao_khac_mm` — khai khác mm trong khi mọi trường đều mang hậu tố `_mm`.
> · `khai_bao_don_vi_kho_tin` — quy trung vị theo ĐÚNG đơn vị khai báo ra độ lớn phi lý ⇒ **chính khai báo mới sai, ĐỪNG nhân/chia theo nó**.
> Dải hợp lý `[0,005; 60] m` hiệu chuẩn từ corpus (nhóm mm: trung vị 0,014–5,6 m; nhóm mét-thật: 13,5–29,6 m).
> **ĐO TỈ LỆ GẮN CỜ trên 85 file: im lặng 50 (59%) · mâu thuẫn 26 (31%) · khó tin 9 (11%)** — dưới trần nhiễu 45%.
> **Test:** `test_takeoff_chong_bia` 272→**283** (W.10a-k). **KHÔNG đụng số máy báo** (chỉ thêm trường cờ).
> **CÒN TỒN:** chưa phân biệt được file khai `inch` là "sai hoàn toàn" hay "thật" — cần tín hiệu độ-tròn của số đo, chưa đo. Hiện xếp vào `mâu thuẫn` (nói có xung đột) chứ KHÔNG dám gọi là khó tin.

## 🔤 1.03 XONG — NẮN PHÔNG CŨ (2026-07-31, nối phiên) · check.sh **[42/42]**
> **⛔ ĐÍNH CHÍNH SỐ CŨ CỦA CHÍNH TÀI LIỆU NÀY:** "545 chuỗi/21 file" là **SAI** (không có script đo kèm). Đo lại toàn corpus `_khao_sat/_dxf` **86 file / 285.413 chuỗi**: thực tế **9.680 chuỗi / 73 file** còn garble — lệch ~18×.
> **KẾT QUẢ (tự kiểm ngược TRƯỚC/SAU trên cả 86 file):** cứu **8.913** chuỗi · **HỎNG THÊM 0** · đổi-mà-cả-hai-sạch 285 · **số máy báo KHÔNG dịch** (cao độ KT −2.1/10.8 · KC −1.85/10.8 · HT **−14.26**/2.5 y nguyên; text count y nguyên) ⇒ lợi ích recall THUẦN.
> **3 lỗi độc lập đã vá trong `vntext.py`:**
> 1. **Dò quá HẸP** — `_SIG` cũ chỉ phủ ô TCVN3 hiện ra KÝ HIỆU Latin-1 (0xA1-0xBE); chuỗi mà mọi ô đều nằm 0xC6-0xFE thì không bị phát hiện (`diÖn tÝch`, `THÐP`, `cèt thÐp`). Thêm 22 chữ Latin không-phải-chữ-Việt làm dấu hiệu tầng 2. **Cố ý loại trừ** `Ø`(0xD8) `×`(0xD7) `÷`(0xF7) + mọi chữ Việt hợp lệ (É Ý é í ô…) — đo corpus: 0 lượt ký tự sót nào trùng 2 nhóm này.
> 2. **⚠ TỰ NUỐT Ø (lỗi đang SỐNG)** — `_autocad_codes` chạy TRƯỚC nên `%%C`→`Ø`(U+00D8), rồi bộ giải mã TCVN3 ăn luôn vì 0xD8 = ô `ỉ`. **Chuỗi `'thép ỉ10 neo xà gồ'` — bằng chứng chủ lực của lát L6 — là DO MÁY MÌNH TẠO RA**: raw thật `'thÐp %%C10 neo xµ gå'`. Đảo thứ tự → **152 ca Ø-bị-nuốt về 0**. (L6 fold `ỉ→Ø` GIỮ NGUYÊN: nó ở tầng `_norm` cho tìm-kiếm.)
> 3. **`Ð` hai nghĩa** — ô TCVN3 `é` (`THÐP`→`THÉP`) vs chữ `Đ` viết nhái (`Ðang XD`→`Đang XD`, `Khu ÐT`→`Khu ĐT`). Phân biệt bằng VỊ TRÍ: `Đ` thật trong TCVN3 là 0xA7 (`§`) nên `Ð` **không dính sau chữ cái** chắc chắn là `Đ`.
> + Gộp **NFC** cho Unicode tổ-hợp-dấu (266 lượt).
>
> **📌 BẪY ĐÃ MẮC RỒI MỚI THOÁT — ĐỪNG LẶP:** thêm chốt *"chuỗi đã có ký tự Unicode Việt thì bỏ qua cả chuỗi"* nghe rất hợp lý nhưng **làm 27 chuỗi HỎNG THÊM**: bản vẽ đổi **PHÔNG GIỮA CHỪNG** (`{\f.VnTimeH…®…\fArial…Ư…}`) nên một chuỗi có thể NỬA TCVN3 NỬA Unicode thật (`'Cäc tiÕp ®Þa MẠ KẼM'`). Dấu hiệu SIG tự nó đã đủ chặt.
> **CÒN TỒN (cố ý, có số):** **768 chuỗi** vẫn hỏng, mang `Ä`(0xC4) `Å`(0xC5) `Û`(0xDB) `Φ` `†` `„` `‚` `Š` — **KHÔNG nằm trong bảng `_TCVN3`** ⇒ **HỌ MÃ KHÁC** (nhiều khả năng VNI-Windows). Muốn xử phải dựng bảng mã riêng + đo lại, **ĐỪNG nhét vào `_TCVN3`** (là đoán). `Φ` (65 lượt) gần như chắc là gõ 'phi' Hy Lạp thay `Ø` nhưng sửa nó = đổi KÝ HIỆU ĐƯỜNG KÍNH → phải đo riêng. `bé`↔`bộ` là nhập nhằng THẬT ở mức byte, không dấu hiệu nào gỡ được.
> **Test:** `test_vntext` 28→**53** (thêm khối E/F/G/H/I/K) · `test_garble_dia` 26→**27** (G5 đổi kỳ vọng + G5b, có ghi rõ lý do đính chính).

## 🔧 1.06 XONG — DỤNG CỤ ĐO BỘ 198 CÂU (2026-07-31, nối phiên) · check.sh **[42/42]**
> **HỢP ĐỒNG CHỐT — đừng sáng tác lại:**
> · Dữ liệu lượt: `tests/battery_runs/run<NN>.jsonl` (**gitignored**) · định danh: `battery_runs/_meta/run<NN>.meta.json` (ghi 1 lần, mode `"x"`).
> · **APPEND-ONLY tuyệt đối.** Không có đường nào rewrite/xoá/`os.replace` lên file kết quả. `tests/battery_results.jsonl` (24/07) **không còn bị script đụng tới**.
> · **"Hợp lệ" nhận biết bằng CẤU TRÚC:** `"answer_goc" in r`. `tra_loi_ai` chỉ đính khoá này ở 2 đường trả lời THẬT (`mcp_bridge.py:988`, `:1008`); cả 4 đường hỏng (`:913` quá tải · `:918` rỗng · `:984` rỗng-sau-nhắc · `:1012` hết lượt tool) đều KHÔNG có. **Đừng quay lại khớp chuỗi tiếng Việt** — câu chữ trôi, cấu trúc thì không.
> · Mã thoát: `0` đủ · `2` đã tồn tại/sidecar mồ côi · `3` jsonl hỏng giữa file · `4` chuỗi model chưa tắt · `5` lệch định danh · `8` còn khuyết câu · `9` thiếu bản vẽ.
> · `run_battery.py` **ép `GEMINI_FALLBACK_MODELS=""` trước `import mcp_bridge`** (MODELS chốt lúc import). Mở lại: `BATTERY_CHUOI_MODEL=1`. Lý do: 429 lặng lẽ nhảy 2.0-flash → không biết đang chấm model nào.
> · Đo ổn định: `python tests/do_on_dinh.py` — in **BA số** (mâu thuẫn số · trả-lời-vs-từ-chối · tổng), trung bình trên C(N,2) cặp, **không có ngưỡng đạt/không-đạt**.
>
> **SỐ ĐO TRƯỚC-KHI-CODE (2 cặp lượt lịch sử thật):** so nguyên văn **3,5%/0,0%** = chỉ số CHẾT · `_answer_numbers` trả LIST nên so `==` cho 43,4% còn `set()` cho 53,0% (**chênh 10 điểm thuần do lỗi so sánh**) · **29,3%** cặp câu không có số ở CẢ HAI lượt = giống nhau TẦM THƯỜNG, đã loại khỏi mẫu · độ phân giải đạt (cùng model/khác code 33,6% vs khác model 11,5%).
>
> **📌 BÀI HỌC TỐN TIỀN THẬT:** `ap.parse_args([] if argv is None else argv)` ⇒ chạy từ DÒNG LỆNH thì mọi tham số bị vứt IM LẶNG ⇒ `--chay-thu` vô tác dụng ⇒ **chạy thật, tiêu API 42 câu**. **49 ca test tự viết đều XANH** vì ca nào cũng truyền argv tường minh. Idiom đúng: `parse_args(argv)` (đã có sẵn đúng ở `tests/khao_sat_corpus.py:486`). Ca khoá `[R.11]` đi đúng đường `sys.argv`. ⇒ **seam làm test dễ viết đồng thời làm test MÙ với entry point thật.**
>
> **Tiện thể vá 1 rủi ro MẤT DỮ LIỆU có thật:** `prep_verify.py` xoá `*.json` theo `argv[2]`; `""` hoặc `"."` quét trúng **`tests/battery.json`** (bộ 198 câu, gitignored = BẢN DUY NHẤT) + `kichban_ketqua.json` + `rerun_ids.json`. Đã chặn (chỉ xoá `chunk_*.json`, bắt buộc thư mục con trực tiếp của `tests/`).
> ⚠ `prep_verify.py` vẫn CHẾT vì thiếu `_renders/profile_*.json` → chạy `python tests/dump_profile.py` trước. Có `tests/battery_runs/run01.jsonl` = **42 câu thật** (lượt 1 dở dang từ sự cố trên, định danh khớp bản hiện tại) — chạy tiếp `--tiep --luot 1` hoặc xoá.
> **CỐ Ý KHÔNG LÀM:** khoá theo pid · trộn thứ tự câu · thư mục nhóm theo code_hash · file "kết sổ" riêng · bộ tách số thứ hai (dùng chính bộ của hàng rào chống bịa).

## 🏁 CHỐT SỔ CUỐI PHIÊN 2026-07-31 — ĐỌC 12 DÒNG NÀY TRƯỚC
> **HEAD `8156d47` == origin · tree SẠCH · check.sh [41/41] PASS · 34 MCP tool · 0 regress.**
> **LIVE `8156d47`** verify: prompt `2026.07.27-kb-l3` / `239e8b7b…` (thêm rồi GỠ `_P_R5` → byte-identical
> bản cũ) · kb `e55ac112…` KHÔNG đổi · `/health` ok · `ram_mb` 135. **9 commit** push+deploy+verify.
> ⚠ **pytest KHÔNG chạy được** (`I/O operation on closed file` → `no tests ran`) — cổng = `check.sh`.
> **KHÔNG có `specs/specs.json`** → `feature_list.json` (**64 mục**: 59 done · 4 deferred · 1 partial).
>
> **PHIÊN NÀY:** vá **nền đọc số đo** (3 lỗi độc lập) · làm đủ **4 việc đợt vùng-mù** · bịt **4 lỗ hàng rào
> chống bịa** · **1.05** nối cụm-từ-Việt với ký-hiệu · chốt **NO_GO có số cho per-claim**. Chi tiết đầy đủ:
> `claude-progress.md` entry đầu.
>
> **BƯỚC TIẾP (nhóm A, đúng thứ tự):** ① **1.06 sửa `tests/run_battery.py`** (~15', đang GHI ĐÈ kết quả lượt
> trước — chặn Q2/Q3/Q4) → ② **1.03 nắn phông VNI** (545 chuỗi/21 file) → ③ **1.04 đơn vị inch/feet
> ⚠ KHÔNG phải thêm bảng tra** (12/76 file khai đơn vị MÂU THUẪN với chính số đo — thêm ngây thơ = biến câu
> nhẹ thành câu SAI TỰ TIN; việc đúng là **cross-check + LỘ mâu thuẫn**) → ④ Q2/Q3/Q4.
>
> **⛔ ĐỪNG MỞ LẠI (đã bác BẰNG SỐ trong phiên này):** per-claim / ALL-GROUNDED · bỏ luật ×1000 · per-câu ·
> thêm vế ngoại lệ vào `_P_R5` · đọc chữ-trong-khối vào kho chữ chung · khối mồ côi + trang in · đọc bảng
> DIMSTYLE thay `e.override()` · `_tok_bound` trần cho rổ bóng · vá bug parser dấu nghìn (đang bị ÷1000 che).

## 🕘 TRẠNG THÁI GIỮA PHIÊN 2026-07-31
> **HEAD `4c42a35` · tree SẠCH · check.sh [41/41] PASS · 34 MCP tool · 0 regress.**
> **✅ ĐÃ PUSH + DEPLOY + VERIFY LIVE `0613591`** (user chốt push 2026-07-31): `/version` commit khớp ·
> prompt_version **`2026.07.31-vung-chua-doc`** hash **`56177a5b…`** (đổi CÓ CHỦ ĐÍCH, xem việc 4) ·
> kb_hash `e55ac112…` KHÔNG đổi (không chạm kho kiến thức) · `/health` ok, `ram_mb` **135,3** (không phình).
> **VERIFY END-TO-END TRÊN MÁY THẬT** (upload `01-TD tuyen ong ap luc.dxf` 13MB qua web, hỏi qua Gemini):
> `so_kich_thuoc` = **175** (khớp đo local; `counts.DIMENSION` vẫn **241** = thống kê KHÔNG hụt) ·
> trả lời **"lớn nhất 212.1 mm, nhỏ nhất 0.7 mm"** — đúng số AutoCAD tự lưu, thay cho **35.970 mm**
> (vốn là GÓC 359,7°) và 0,3 trước đây · **câu cảnh báo việc 1 bật đúng**, câu TRẤN AN SAI đã biến mất.
> ℹ Quan sát (KHÔNG phải regress, là hợp đồng M9 sẵn có): model nêu cả `don_vi_khai_bao = mét` bên cạnh
> trường `_mm` — đúng thiết kế "lộ giả định đơn vị", nhưng đọc hơi nghịch. Cân nhắc làm rõ ở lát sau.
>
> **PHIÊN NÀY LÀM 4 VIỆC USER GIAO + 1 VIỆC PHÁT SINH (nền đo).** Chuỗi: `5548fe1` (2 lỗ guard) →
> `138d104` (nền đo 3 lỗi + việc 1/2/3) → `f621b6e` (`_P_R5` + A/B) → `4c42a35` (vá 3 lỗi red-team).
>
> **⭐ PHÁT HIỆN LỚN NHẤT — NỀN ĐỌC SỐ ĐO SAI Ở 3 TẦNG ĐỘC LẬP,** lộ ra khi rà lại trước khi làm việc 1
> (việc 1 chính là "so chữ in với số máy đo", nên số máy sai thì việc 1 vô nghĩa):
> 1. **Hệ số tỉ lệ ÂM bị áp** (do chính `6de1aaa` sinh ra): 1.882 đường/4 file thành âm → bị các cổng lọc
>    dương của dự án vứt IM LẶNG, `so_duong_kich_thuoc` vẫn đếm đủ. Nặng nhất 71,9% một file.
> 2. **Đường đo GÓC coi là mm** (lỗi CÓ TRƯỚC DIMLFAC): `01-TD` báo **35.970 mm cho góc 359,7°** đồng thời
>    in câu TRẤN AN rằng số khớp bản vẽ.
> 3. **Không ai đọc group code 42** (`actual_measurement` — số đo AutoCAD TỰ LƯU, có mặt 94,9%). Phép thử
>    không thiên vị 54.735 đường: code42 đúng RIÊNG 2.936 ca / engine đúng RIÊNG **0** ca. Dim dài-XIÊN
>    engine chỉ đúng **37,2%**. → **USER CHỐT dùng code42 làm nguồn chính.**
> ⚠ **code42 CHỈ đáng tin khi HÌNH HỌC CÒN ĐỠ NÓ** — xem "bài học" bên dưới.
>
> **KẾT QUẢ ĐO CỦA TỪNG VIỆC (công bố theo yêu cầu của chính thiết kế):**
> - **Việc 1** (chữ in ghi đè): luật bắt 1.098 đường/26 file; cờ "lan rộng" bật **19/66 = 29%** file — dưới
>   trần 45% nên GIỮ ngưỡng. Con số `837 dim/15 file` trong thiết kế cũ **KHÔNG tái lập được**.
> - **Việc 2** (cờ vùng chưa đọc): nhiễu **15,3% → 0,0%** sau khi siết vế "chèn ≥2 lần" chỉ áp cho truy vấn
>   MANG MÃ (ngưỡng thiết kế 10%); 4/4 ca dương vẫn bật; chi phí dựng rổ ≤0,11s.
> - **Việc 3** (tool #34 `tim_chu_trong_ky_hieu`): cổng cứng ngân sách rổ neo **6,0 vs `tim_kiem` 19,0** →
>   ĐẠT, nên KHÔNG đưa vào tuple loại-trừ. E2E lấy lại `l=1100`[38E9C/38EA5] · `L=1600, SL:67`[3053A] ·
>   `DN-01, L=15000, SL:02`[1C2F1E] — chuỗi trước đây KHÔNG tool nào chạm tới.
> - **Việc 4** (`_P_R5`): ⚠ **A/B LIVE KHÔNG CHỨNG MINH ĐƯỢC TÁC DỤNG.** Prompt CŨ 4/8, MỚI 5/8 — chênh
>   đúng 1 ca. **Recall thắng là nhờ việc 2+3, không phải `_P_R5`.** Không gây hại (4/4 bẫy vẫn từ chối
>   đúng, 0 từ-chối-oan). ĐỪNG tính nó vào lợi ích.
>
> **📌 BÀI HỌC ĐẮT NHẤT — RED-TEAM IMPLEMENTATION BẮT ĐƯỢC LỖI BỊA SỐ DO CHÍNH BẢN VÁ SINH RA:**
> bản vá code42 đầu "cứu" MỌI đường đo-ra-0. Nhưng hình học suy biến ⇒ code42 **chắc chắn là số CŨ**.
> Đo 607 đường được cứu: **529 chữ in RỖNG → cứu ĐÚNG** · **66 gõ đè SỐ KHÁC → BỊA** (bản vẽ in `10000`
> mà máy phát 2136,3) · 11 gõ đè ký hiệu. **Tệ HƠN lỗi gốc**: lỗi gốc chỉ làm rơi giá trị, cứu sai thì
> phát số tự tin VÀ số đó thành NEO grounding. **Cả 3 suite mới tự viết đều XANH** — điểm mù: ca test
> dựng đúng nhánh cứu nhưng CỐ Ý không gõ đè chữ. → luật đúng: hình học >0 dùng code42; hình học =0 chỉ
> cứu khi KHÔNG có chữ gõ đè.
>
> **✅ ĐỢT 2 CÙNG NGÀY — user chốt "nghiên cứu kỹ rồi mới quyết":**
> - **GỠ vế ngoại lệ `_P_R5`** (prompt về BYTE-IDENTICAL `239e8b7b`). Đề xuất "giữ" của phiên trước **BỊ
>   BÁC bằng số**: lợi ích ~0 (A/B 4/8 vs 5/8, Fisher p=1,000) · hại đo được: trong ca cờ bật chỉ **5%**
>   tool trả dữ liệu thật, **95%** câu trả lời ĐÚNG vẫn là "không có" mà vế đó lại CẤM nói → **cỗ máy ép
>   bịa**. GIỮ phần CODE (cờ + tool) vì dữ liệu mất là thật.
> - **Sửa NGUYÊN NHÂN GỐC báo động giả: đòi khớp ĐÚNG DẤU** (`_vcd_dau_khop`). `_norm` bỏ dấu nên
>   'cửa'→'của', **'mác'→'mạc tiến trình' (TÊN NGƯỜI KÝ)**, 'cột'→'cốt thép', 'trần'→'THỊ TRẤN'.
>   Kết quả: ca bật cờ **20→5** · khớp mù dấu **15→0** · tỉ lệ mang dữ liệu thật **5%→20%**.
> - **GỠ thoát-sớm theo cụm TỪ CHỐI trong `_guard_text`** (giữ ở `_apply_i1`). Dòng đó là MÃ CHẾT với câu
>   từ chối thuần (`if not do_luong` đã lo trọn — 0/102 câu đổi kể cả rổ neo RỖNG), nên tác dụng duy nhất
>   là miễn trừ đúng phần nguy hiểm. Với rổ neo THẬT: **0/793 câu đổi**.
> - **VÁ HANDLE BƠM NEO ẢO — kênh RỘNG NHẤT.** `'13876A'` → neo `13876.0`; kết quả chỉ gồm 3 handle +
>   chữ KHÔNG CÓ SỐ vẫn sinh rổ `[1,2,9,38,13876]`. MỌI tool trả handle đều dính. `_strip_handle` gộp vào
>   `_strip_neo`; I1 KHÔNG ảnh hưởng (`_collect_handles` chạy trên result thô).
> - Test: neo_grounding 21→**34**, vung_chua_doc 37→**44**. Gate **41/41**.
>
> **⚠ ĐÍNH CHÍNH SỐ CŨ CỦA CHÍNH TÀI LIỆU NÀY: "45% câu trả lời ở trạng thái không-hàng-rào" là SAI.**
> Đo lại trên 822 câu thật: **21,2%** (mẫu chính 198 câu) / **14,5-17,5%** (mẫu gộp), và phần lớn VÔ HẠI
> (từ chối thuần, không có số để bảo vệ). Nhóm nguy hiểm thật (trộn từ-chối + khẳng định số) = **2,1%**.
>
> **⛔⛔ ANY-GROUNDED = GIỮ NGUYÊN. ĐỔI SANG PER-CLAIM = NO_GO CÓ SỐ (2026-07-31). ĐỪNG MỞ LẠI.**
> Đã nghiên cứu trọn vẹn theo yêu cầu user ("nếu làm sai có thể đánh đổi cả dự án"): workflow 8 agent
> (`wf_8a663cde-735`, 7/8 xong) + 3 phép đo độc lập của chính người viết. **KẾT LUẬN: KHÔNG đụng vào
> `_guard_text` / `_answer_numbers` / `_is_grounded`.**
>
> **⚠ TRƯỚC HẾT — "TỈ LỆ LỌT" KHÔNG PHẢI ĐẠI LƯỢNG DÙNG ĐƯỢC ĐỂ RA QUYẾT ĐỊNH.** 5 probe đo CÙNG một
> đại lượng ra **0% / 23,8% / 32,2% / 37,9% / 52-77,5%**; người viết đo ra 15,0%. Tự kiểm: trên **CÙNG
> MỘT rổ neo**, chỉ đổi BỘ SINH số bịa thì tỉ lệ chạy **0,0% → 13,6%** (probe khác đo 1,9% → 79,2%).
> ⇒ Mọi con số "nền" đều là ARTIFACT của bộ test. **ĐỪNG trích con số nào làm căn cứ**, kể cả 15,0%
> hay 36-49% từng ghi ở tài liệu cũ.
>
> **THỨ CÓ GIÁ TRỊ QUYẾT ĐỊNH = đo trên CÂU TRẢ LỜI THẬT, chấm bằng NHÃN ĐỘC LẬP (`ky_vong` bộ 198 câu):**
> · độ chính xác của per-claim = **0/25** (probe 3) và **1/30 = 3,3%** (probe 6) ⇒ **96,7-100% câu nó giết
>   là câu ĐÚNG** · giết oan **9,9-33,1%** câu đã xác minh đúng · mỗi lần giết mất **~587 ký tự thân bài**,
>   thay bằng 36 ký tự từ chối.
> · đo riêng của người viết (7 dạng câu đúng): **ALL giết 82% câu có PHÉP CỘNG** (= việc CHÍNH của phần mềm
>   bóc tách) và 31% câu có số ĐẾM. **ANY là luật DUY NHẤT có 0% chặn oan trên cả 7 dạng.**
> · **BỎ luật ×1000 cũng NO_GO**: 2 đường đo độc lập — 36,5% giết oan (85,4% với câu đổi m→mm) / 82%-80%
>   với dạng "chỉ dùng đơn vị đã quy đổi".
> · **PER-CÂU không cải thiện gì** (15,0% y hệt ANY) vì câu bịa thường gói trong MỘT câu.
>
> **ĐÒN BẨY ĐÚNG LÀ LÀM SẠCH RỔ NEO — VÀ ĐÃ LÀM XONG.** Bằng chứng: lớp lỗi **id135 (bịa cao độ ÂM)** nay
> có tỉ lệ lọt **0,0%**. Truy được nguyên nhân: trước bản vá hôm nay, **24/76 file có neo âm nằm đúng dải
> cao độ, sinh THUẦN từ mã hiệu** (`DẦM D2-10` → −10). Gỡ 3 kênh neo bẩn = lấy đi chính những chiếc neo
> cấp phép cho lớp lỗi đó. Mỗi neo bẩn gỡ đi làm vùng phủ (mỗi neo nở 3 bậc đơn vị) co lại **mà KHÔNG mất
> một câu đúng nào** — khác hẳn việc đổi luật phán quyết.
>
> **HIỂU ĐÚNG VỀ ANY-GROUNDED:** nó CÓ điểm yếu thật (1 số truy được ⇒ bảo lãnh cả bài; demo:
> rổ `{220}` + "Dầm rộng 220 mm, cao 9999 mm, dài 12345 mm" → LỌT). Nhưng đó là **đánh đổi CÓ CHỦ Ý** ghi
> sẵn trong chú thích gốc ("chỉ từ chối khi câu bịa THUẦN"), và mọi phương án thay thế đều **tệ hơn về
> tổng thể**. Điểm yếu đó phải xử bằng **thu hẹp rổ neo**, KHÔNG phải bằng đổi luật.
>
> **✅ ĐỢT 3 — HÀNG RÀO CHO SỐ ĐẾM (nhóm A, LÀM XONG 2026-07-31).** Bề mặt đang MỞ HOÀN TOÀN ở **31%**
> câu trả lời: `do_luong` chỉ gồm số có ĐƠN VỊ / THẬP PHÂN nên câu chỉ khẳng định SỐ ĐẾM thoát sớm ở
> `if not do_luong: return text`. Rổ neo RỖNG: *"Tổng số cọc là 156 cọc."* LỌT · *"Bản vẽ có 9999 cột."*
> LỌT, trong khi *"Chiều dài dầm 30 m"* CHẶN. Với phần mềm bóc khối lượng thì "bao nhiêu cấu kiện" quan
> trọng NGANG "dài bao nhiêu mét".
> **ĐO TRƯỚC, CODE SAU** — 198 câu thật, rổ neo dựng lại từ engine, chấm bằng nhãn độc lập `ky_vong`:
> 106/198 = 54% câu có khẳng định đếm · **62/198 = 31% chỉ có số đếm** · trong 72 câu bản vá chạm tới:
> chặn thêm **1**, **giết oan 0**, bắt đúng **1** (id123: model nói "120 lần" trong khi `dem_so_luong('MC')`
> trả **5**). ⇒ chính xác 1/1, từ-chối-oan 0/72. **Profile NGƯỢC HẲN per-claim** — đó là lý do mục này GO
> còn per-claim NO_GO, dù cùng là "siết hàng rào": ở đây siết cái được coi là KHẲNG ĐỊNH, không đổi luật
> phán quyết. 71/72 câu vẫn lọt vì model VỐN đã đọc số đếm từ tool.
> **2 quyết định KHÔNG-LÀM có số:** biến thể KHÔNG DẤU (`156 coc`) vẫn lọt — đo được bắt thêm **0/198**
> (model luôn trả lời có dấu) · tên LOẠI DXF (`2355 DIMENSION`) không tính — chỉ **1/198** ca và đó là
> BÁO ĐỘNG GIẢ (`01 TEXT` = tên layer). Cả hai lần **kỳ vọng trong test SAI, không phải code sai**.
> Cổng bắt 4 ca đỏ khoá hợp đồng cũ ("số nguyên trơn miễn") — cả 4 là khẳng định PHÂN LOẠI, mọi ca HÀNH VI
> E2E vẫn xanh. `test_grounding_guard` 50→**56** (+khối `[F2]` khoá cả hai chiều).
> ⏳ Rủi ro tồn dư: danh sách danh từ đếm dựa trên 198 câu của 3 bản vẽ; corpus mới có thể có danh từ chưa
> phủ — chiều hỏng là IM LẶNG (bỏ sót), không phải báo oan.
>
> **GHI SỔ, KHÔNG SỬA:** có bug parser thật ở dấu ngăn cách nghìn kiểu VN (`62.900` bị tách thành 62,9),
> nhưng đo được luật ÷1000 đang **che hoàn toàn** (8/8 ca không đổi kết quả). Vá một bug đang bị vô hiệu
> hoá = thêm rủi ro, đổi lại 0. Chỉ mở lại NẾU sau này có ai đổi luật ÷1000.
> 2. **Regex neo mới ĐỔI neo âm lấy neo dương** (`D2-10` nay cho `10` thay vì `−10`). Không thuần tuý là
>    thu hẹp. Vá đối xứng (chạy `_MAHIEU_RES` cả phía rổ neo) thì `Ø22` mất neo 22 → nguy cơ từ-chối-oan.
> 3. **Việc 1 im lặng với chữ in là SỐ THUẦN khác số máy** — đúng, nhưng lớp đó bắn **91,2%** ứng viên nên
>    đưa vào cờ luôn-bật sẽ thành nhiễu. Đường đúng = tool tra theo yêu cầu (lát 2 thiết kế, chưa làm).
>
> **⛔ ĐỪNG LÀM LẠI:** đọc bảng DIMSTYLE thay override (docstring cũ SAI — `e.override()` VỐN gộp bảng, và
> nhánh đó ĐÚNG, code42 xác nhận) · dùng `_tok_bound` trần cho rổ bóng (khớp mảnh vụn `1/100` + substring).

## 🕘 TRẠNG THÁI CHỐT PHIÊN 2026-07-30 (trước) — ĐỌC MỤC NÀY TRƯỚC
> **HEAD `6de1aaa` · tree SẠCH · check.sh [36/36] PASS · 33 tool · 0 regress.**
> **⚠ 2 commit CHƯA PUSH (cố ý): `6de1aaa` (code DIMLFAC) + `f0ae46c` (docs). LIVE hiện là `fb8a597`** (mã nguồn y hệt `371d950`, chỉ khác tài liệu). Đẩy: `git push origin main` → Render tự deploy ~60s → verify `/version` + `/health`. `6de1aaa` là commit **ĐỔI SỐ máy báo** nên verify kỹ hơn thường lệ.
> **Đo LIVE cuối phiên (`fb8a597`):** `ram_mb` **135,5MB** · `ban_ve` 0/1 · `metrics.tu_choi` **0** (chưa ai bị chặn oan) · **`keepalive` ok=99 / lỗi=0** — 99 cú tự-gọi giữ-thức liên tiếp KHÔNG lỗi lần nào, xác nhận bản vá bom-3 chạy đúng trên máy thật.
>
> **PHIÊN NÀY (2 phần):** (A) vá **3 bom hẹn giờ chịu tải** — 2 lát đã LIVE `eba4d67` + `371d950`; (B) quay lại **nhóm A**: rà soát lại toàn nhóm + vá **hệ số tỉ lệ đo (DIMLFAC)**. Chi tiết đầy đủ: `claude-progress.md` 2 entry đầu.
>
> **USER CHỐT (2026-07-30):** giữ `READFILE_MAX_MB=45` · **ĐỌC hệ số tỉ lệ đo** dù ĐỔI SỐ · **CÓ sửa `_P_R5`** kèm đo A/B · triển khai theo 2 đợt (nhẹ trước, nặng sau).
>
> **BƯỚC TIẾP — làm đúng thứ tự này:**
> 1. **Xong nốt đợt đang dở** (3/4 việc còn lại): bộ phân loại "ghi đè THẬT" trên đường kích thước · cờ "chưa với tới vùng này" (4 tool, khớp **CHỈ trên `to_unicode`** — khớp raw cho **41 hit ẢO**) · tool `tim_chu_trong_ky_hieu` (chỉ khối ĐƯỢC CHÈN). Thiết kế chốt + số liệu: `scratchpad/chot_vungmu.md`, workflow `wf_0cdb83d4-bca`.
> 2. **`_P_R5` + đo A/B** (lát riêng, cuối cùng — bump PROMPT_VERSION + re-freeze hash).
> 3. **Nhóm A còn 22 việc** — artifact: https://claude.ai/code/artifact/2aac664c-26fd-4ada-9ece-641ab6e596e5
> 4. Chạy lại bảng điểm 198 câu 3-5 lượt — **sửa `tests/run_battery.py` trước** (đang ghi đè kết quả lượt trước nên không đo được độ ổn định).
>
> **⛔ ĐỪNG LÀM LẠI (đã bác bằng số trong phiên này):**
> - **"Đọc chữ trong khối vào kho chữ chung"** — 71,6% là nhãn DIMENSION đã đọc rồi · 55,7% khối là khối CHẾT (một khối chết ghi *"156 cọc"* trong khi bản vẽ sống ghi *"131 CỌC"*) · mã cấu kiện chỉ 0,8% · lợi ích +3,0% mà 19/71 file lợi ích BẰNG KHÔNG · toạ độ hệ nội bộ → khoanh đỏ sai chỗ · **`cao_do` KT −2.1 → −94.44** · **id135 `rachmop` −14.26 → −16.14 mà cổng vẫn XANH**.
> - **Khối mồ côi + chữ trang in đưa vào kho chữ chung** — nguồn không tin được thì KHÔNG trả.
> - Hạ `MAX_SESSIONS` · tăng `--threads` · lazy-import `google.genai` bằng `find_spec` (xem entry chịu tải).
>
> **⚠ HAI ĐÍNH CHÍNH TÀI LIỆU CŨ:** (1) ghi chú *"chữ trong khối không phải bug — đã tự bác bỏ"* là **SAI** (2.068 chuỗi vô hình / 30-40 file) — nhưng cách vá hiển nhiên cũng SAI, xem ⛔ trên. (2) **Bảng điểm 198 câu (24/07) LẠC HẬU** so với code — **đừng trích "39 câu hỏng"** cho ai.
>
> **📌 LỖ HỔNG ĐÃ BIẾT, CHƯA VÁ:** hàng rào chống bịa **chỉ soi số ĐO LƯỜNG**; **số ĐẾM không có hàng rào nào** (đo với rổ neo RỖNG: *"Tổng số cọc là 156 cọc."* → LỌT · *"Bản vẽ có 9999 cột."* → LỌT). Vá được nhưng dịch số cả 36 suite → lát RIÊNG.
>
> **📌 BÀI HỌC PHIÊN NÀY (đã ghi vào clean-state-checklist):** **cổng xanh KHÔNG đủ để tin bản vá đã chạy.** Vá DIMLFAC đổi số thật trên 21,5% đường kích thước mà cả 6 suite đóng-băng-số vẫn xanh. Với mọi vá đổi hành vi đọc: TỰ KIỂM NGƯỢC (so số trước/sau) rồi mới thêm suite khoá.

## 🕘 TRẠNG THÁI CHỐT PHIÊN 2026-07-30 (giữa phiên — chịu tải)
> **HEAD `371d950` == origin · tree SẠCH · check.sh [35/35] PASS · 33 MCP tool · 0 regress.**
> **LIVE `371d950`:** prompt `2026.07.27-kb-l3` (`239e8b7b…`) + kb `kb-2026.07.26-dot-dau` (`e55ac112…`) **KHÔNG ĐỔI** (đợt này không chạm SYSTEM_PROMPT/kho kiến thức → không cần đo A/B) · `/health` ok · **`ram_mb` = 135.3MB** (lần đầu đo được RAM Linux thật).
>
> **PHIÊN NÀY LÀM GÌ:** vá **3 "bom hẹn giờ" chịu tải** (RAM/thread/keep-alive) qua 2 lát: `eba4d67` (nhẹ) + `371d950` (nặng). Quy trình: nghiên cứu 11 agent (`wf_40e7e334-100`, bản chốt `scratchpad/wf_chot.md`) → code → gate → **red-team-IMPLEMENTATION 5 agent engine thật** (`wf_a2699eb1-622`) → vá → gate. Chi tiết đầy đủ ở `claude-progress.md` mục 2026-07-30.
> **ĐO THẬT BÁC 3 mục dự kiến (ĐỪNG làm lại):** hạ `MAX_SESSIONS` (tiết kiệm **0MB** — trần RAM là `MAX_BAN_VE`, số bản vẽ trong RAM = số request đồng thời) · tăng `--threads` 4→8 (**nhân đôi** bom RAM) · lazy-import `google.genai` bằng `find_spec` (**find_spec NÓI DỐI** + NÉM khi thiếu namespace cha = deploy fail).
> **RED-TEAM-IMPL BẮT 2 LỖI MỨC CHẶN** (1 do CHÍNH bản vá): (a) **bấm 2 lần** phá được trần bản vẽ (cờ đang-nạp là 1 ô vô hướng → request thứ hai xoá cờ của request anh em) — 42 ca test tự-viết MÙ vì đều tuần tự 1 luồng; (b) **nạp lỗi vẫn hiện "✅ Đã nạp"** (`MCPBridge.call` bỏ `res.isError` → `res.get('loi')` là mã chết) — kèm lỗ chống-bịa: model tự bơm được số vào rổ neo qua thông điệp lỗi pydantic. Cả hai đã vá + có test khoá.
>
> **VIỆC CHỜ / BƯỚC TIẾP:**
> 1. **⚠ Đọc `ram_mb` ở `/health` sau khi nạp 1 bản vẽ thật** rồi mới chốt `READFILE_MAX_MB`. Ngân sách còn ~377MB; ngoại suy cho thấy **trần an toàn thật THẤP HƠN 45MB nhiều**, và cổng theo MB **về nguyên tắc không bound được RAM** (RAM đi theo SỐ ĐỐI TƯỢNG). User chốt 2026-07-30 tạm **GIỮ 45**.
> 2. **Monitor NGOÀI** (UptimeRobot / cron-job.org 5' trỏ `/health`) — code KHÔNG giải được: self-ping chỉ GIỮ THỨC, không ĐÁNH THỨC. **User tự lập tài khoản.**
> 3. **Nhóm C (nâng RAM)** = vẫn HOÃN tới cuối dự án (tốn tiền). **Nửa MIỄN PHÍ đã LÀM XONG trong phiên này.**
> 4. **Nhóm A còn:** 13 ca recall hạ-tầng (chặn RAM) · id135 deep (chờ file độc lập sâu ≥-5m) · Pattern D/E (hoãn).
> 5. **Nhóm D ứng viên:** I8 panel phân tầng tin cậy (UI — giá-trị-demo cao nhất) · Truth-engine · phục hồi subprocess chết.
> 6. **ĐỪNG làm lại:** L7 · họ-slash · pagination · dem_theo_block · I3-U ngưỡng-sàn · U6 iterdxf · I9 Option B · **+3 mục bị bác ở trên**.

## 🕘 TRẠNG THÁI CHỐT PHIÊN 2026-07-27 (phiên trước)
> **HEAD `91eaba6` == origin · working tree SẠCH · check.sh [33/33] PASS · 33 MCP tool · 0 regress.**
> **LIVE `c9e2171`:** prompt `2026.07.27-kb-l3` (`239e8b7b…`) · kb `kb-2026.07.26-dot-dau` (`e55ac112…`) · `/health` ok.
> ⚠ **pytest KHÔNG chạy được** (crash `I/O operation on closed file` → `no tests ran`) — cổng = `bash harness/scripts/check.sh`. **KHÔNG có `specs/`** → `feature_list.json` (46 mục: 44 done/1 deferred/1 partial).
>
> **PHIÊN NÀY LÀM GÌ:** hoàn tất **KHO KIẾN THỨC DEV-SOẠN L0→L6 trọn bộ** (pivot "DEV dạy trước, đối tác CHỈ xác nhận"): L0 gate dispatch (vá lỗ an ninh) · L1 `kienthuc.py` 24 ký hiệu byte-lock · L2 chống-lọt-rổ `_strip_kb` · L3 `tra_ky_hieu`+`_P_R18` (A/B LIVE GO) · L4 graft gate bằng-chứng-dương · L5 confirm-only + nút bấm · L6 fold garble Ø (+666 token, 0 phản-khớp, 0 đổi số). **L7 (đổi số) ĐÓNG có-số.** **Vá 3 bug L5 + 7 vá red-team.** Chuỗi: `998950f` → `fccc635` → `c9e2171` → `91eaba6`.
>
> **VIỆC CHỜ / BƯỚC TIẾP:**
> 1. **⚠ 3 bom hẹn giờ vá FREE, CHƯA làm** — quan trọng nhất: **hạ `MAX_SESSIONS` 4→1-2** (đo thật: RAM 7.5×/file, **2 phiên file lớn = OOM** trên gói free 512MB mà cấu hình đang cho 4). Kèm: hết thread ở `n==--threads(4)`, keep-alive hỏng thầm. → `[[ref-canh-bao-health-check-render]]`.
> 2. **Nhóm C (nâng RAM)** = HOÃN tới cuối dự án (tốn tiền). Config đúng đã nghiên cứu sẵn.
> 3. **Nhóm A còn:** 13 ca recall hạ-tầng (chặn RAM) · id135 deep (chờ file độc lập sâu ≥-5m) · Pattern D/E (hoãn).
> 4. **Nhóm D ứng viên:** **I8 panel phân tầng tin cậy** (UI — giá-trị-demo cao nhất) · Truth-engine · phục hồi subprocess chết.
> 5. **ĐỪNG làm lại:** L7 · họ-slash decode đầy đủ · pagination · dem_theo_block · I3-U ngưỡng-sàn · U6 iterdxf · I9 Option B.

## Trạng thái hiện tại (2026-07-26 — I3-U Lớp 2 code-only unit-tag LIVE `9d90b25` [⏳ prompt-half CHỜ user lần sau] · I9 tách SYSTEM_PROMPT có version/hash LIVE `de69324` · I5 micro-fix recall LIVE `8f00510` · I4a `6ff81cc` · I2 `86776b9` · U6(C) `a242027` · I3-U Lớp 1 `21926c9` · I1 `de1ef47` · I3-B `82951db` · I1b `b2a0ea5` · **I3-U ngưỡng-sàn NO_GO (data thật 34-41% FP)** · U6 iterdxf HOÃN · ⏳ id135-E2E VẪN chờ file hạ tầng ĐỘC LẬP sâu)
> Mỗi tuyên bố "xong" kèm BẰNG CHỨNG (commit + số test) truy được. Nhật ký chi tiết hơn: `GHI_CHU_HOAN_THIEN.md`. Kế hoạch nâng cấp: `PHUONG_AN_NANG_CAP_DU_AN.md` (U1-U6).
> **Code LIVE = `d244865`** (LIVE bundle: routing prompt `_P_R7b` [Gemini BẮT BUỘC gọi tim_kiem trước khi từ chối] + I3-U L2 prompt-half [code sở hữu unit-math] — **đo LIVE A/B GO**: recall refused 19→15, anti-bịa traps GIỮ, prompt-half OK; prompt_hash→`e5e05d7d` version `2026.07.26-routing-l2`. NỀN: Recall offline A/B/C `_tok_bound` D2-x + `thong_tin_file` tool#30 + `bang_con` subtotal (vá 7 ca recall tool-bug); I3-U L2 code-only; robust cho MỌI MCP-client; I9 `de69324` tách SYSTEM_PROMPT (nay 24 mảnh) — verify /version prompt_hash=`e5e05d7d…` + prompt_version=`2026.07.26-routing-l2` + /health ok 2026-07-26; chuỗi phiên: U3 `fd48b19` → I1 `de1ef47` → I3-B `82951db` → I1b `b2a0ea5` → I3-U-L1 `21926c9` → U6C `a242027` → I2 `86776b9` → I4a `6ff81cc` → I9 `de69324` → I3-U-L2 `9d90b25` → recall-A/B/C `81b0a52` → **routing+prompt-half `d244865`**). check.sh **[27/27] PASS · 30 tool** · takeoff 272 · qa 129 · **grounding-guard 47** · misc-tools 107 · cao_do 31 · session 25 · khảo-sát-corpus 61 · ole-cảnh-báo 51 · oleexcel 18 [U3] · handle-guard 44 [I1] · i3-bounds 24 [I3-B] · visual-highlight 19 [U6C] · excel-content 21 [I2] · bang-ve-net 9 [I4a] · **prompt-taxonomy 24 [I9]** · app-routes 8→10 (+I9). Kế hoạch kiểm thử: `KE_HOACH_KIEM_THU_TONG_THE.md`.
> **⚠ GHI-BÙ (baseline + soạn tối 2026-07-23, commit `0cee9b6` sáng 2026-07-24):** entry U3 dưới đây ghi bù cho phiên đêm 2026-07-22 (chat `279bf2f9`) — phiên đó CODE+PUSH+LIVE xong U3 rồi máy crash trước khi cập nhật ledger. Code an toàn; đây chỉ là bổ sung giấy tờ. Transcript `279bf2f9.jsonl` còn nguyên (resume được).
> **⚠ GIT:** local có nhánh **HELD `held-ram-config` (`f025ad7`, render.yaml nâng RAM)** + `public-ready` (`a69502b`, mở public sẵn) + `backup-truoc-rebase-20260717` — ĐỀU local, CỐ Ý chưa push (`main` sạch + push hết). Chi tiết ở [[project-repo-private-vi-oda]] + [[project-chiu-tai-va-chi-phi]].
> **✅ ẨN DANH SẠCH:** 0 tên địa danh/người thật trong file tracked (bí danh CT-A…CT-K; "9T"/"MN" là mô tả generic giữ có chủ đích). Quy trình: `harness/QUY_TRINH_AN_DANH_DU_LIEU_MAU.md`.
> **✅ I3-U Lớp 2 prompt-half ĐÃ XONG [2026-07-26, `d244865`]:** đã đổi SYSTEM_PROMPT (code sở hữu unit-math) + đo LIVE A/B GO (Gemini truyền '3.6m'/'360cm' verbatim, code quy đổi đúng; ca Gemini vẫn ×1000 vẫn đúng nhờ code backstop). Gộp cùng routing fix R7b. **⚠ CHƯA cập nhật `tests/kichban_gd2.py`** (vẫn assert bs=3600 ở engine-truth — engine-truth vẫn ĐÚNG vì code quy đổi '3.6m'→3600; chỉ là chưa đổi để exercise path mới, KHÔNG cấp thiết). id135 deep vẫn chờ file hạ tầng sâu ĐỘC LẬP.

- **✅ LIVE BUNDLE — ROUTING PROMPT (R7b) + I3-U L2 PROMPT-HALF — đo LIVE A/B GO — LIVE `d244865` [2026-07-26]:** Đòn bẩy recall LỚN NHẤT từ nghiên cứu (48/60 recall-miss = Gemini ROUTING, không gọi tim_kiem). Đổi 2 fragment SYSTEM_PROMPT (nền I9): **`_P_R7b` routing** (tool chuyên dùng rỗng cho câu VẬT LIỆU/GHI CHÚ/THÔNG SỐ → BẮT BUỘC gọi `tim_kiem` theo từ-khoá TRƯỚC khi kết luận 'không có'; hỏi tên/phiên bản file → `thong_tin_file`; GIỮ chống bịa: trích nguyên văn+handle, KHÔNG suy diễn luật 8, số truy được về tool) + **`_P_R10` prompt-half** (đối tác cấp số → truyền NGUYÊN giá-trị+đơn-vị '3.6m', code quy đổi mm). hash `bea17c6e`→`e5e05d7d`, PROMPT_VERSION `2026.07.26-routing-l2`, re-freeze test (emit 23→24, VN 15→16). **ĐO LIVE A/B (key user, harness `live_measure.py`) 43 routing + 26 trap + prompt-half:** RECALL refused 19→15 (~5 gain ĐÚNG có handle: mica 7 màu/phụ kiện cửa DW/độ dốc i=/**D2-4 SL=5 [Pattern A qua Gemini]**/đánh dấu bể PCCC; 0 bịa; 1 loss variance); **ANTI-BỊA: MỌI trap suy-diễn/lạc-đề VẪN từ chối đúng** (chiều dài công trình id151/khoảng cách id153/toạ độ id154/hướng id155/giá dự toán id150), 0 lật sang bịa, vài trap NEW an toàn hơn → routing nudge KHÔNG phá chống bịa; **PROMPT-HALF: Gemini truyền '3.6m'/'360cm' verbatim → code quy đổi → 4.704 m³ đúng** (ca vẫn ×1000 vẫn đúng nhờ backstop). ⇒ **GO**. ⚠ Caveat trung thực: 1 A/B run + Gemini variance — hướng rõ + an toàn, KHÔNG overclaim. check.sh [27/27], takeoff 272, 0 regress. ✅ commit+push+deploy+verify LIVE `d244865`. **⏳ CÒN:** 13 hatang chặn RAM 45MB (→ nhóm C); Pattern D/E recall biên (rủi ro, hoãn); đo lặp A/B firm-up nếu cần.
- **✅ RECALL OFFLINE A/B/C — vá 7/9 ca recall-miss (tool bug THẬT) — LIVE `81b0a52` [2026-07-26]:** **Nghiên cứu root-cause TRIỆT ĐỂ 60 ca recall-miss qua workflow `wf_0d021c50-125` (probe engine THẬT offline):** **48/60 = GEMINI ROUTING** (tool CÓ data, `tim_kiem` trả đúng, nhưng Gemini TỪ CHỐI thay vì gọi) → vá PROMPT/tool-desc (LIVE, đòn bẩy lớn nhất); **9/60 = tool bug THẬT** → 3 fix code offline; 3-4 = từ chối ĐÚNG (không bug); **13 hatang = chặn RAM 45MB** (file rachmop 81.6MB — hạ tầng nhóm C, KHÔNG phải logic). ⇒ điểm yếu recall ~92% SỬA ĐƯỢC, KHÔNG phải corpus-blocked như kết luận vội trước. **(A) `_tok_bound`** (tools_core.py): chuẩn hoá ĐỐI XỨNG token+label — strip gạch CHỮ→SỐ (C-1==C1), GIỮ gạch SỐ-SỐ ('D2-4') → 'D2-4' khớp 'd2-4' (recall id73/93/103 + cả LỚP mã D<số>-<số>); 'D2' (họ) VẪN khớp 'D2-n' qua ranh giới; chặn C-4≠C-40/D2-2≠D2-2A/D2-4≠D2-40. **⚠ GATE BẮT 1 REGRESS:** thử strip-all token phá 'D2' khớp họ (tong_so_luong 40→0) → sửa thành đối xứng (bài học: red-team boundary tôi thiếu ca 'họ'). **(B) `thong_tin_file`** (MCP tool #30 + Drawing.thong_tin_file): read-only wrap tom_tat() (tên/phiên bản DXF/số layer) → vá id39/107 (hỏi metadata lúc đang hỏi). **(C) `bang_con`** (thong_ke_thep_hinh): subtotal RIÊNG từng bảng (ô 'TỔNG KHỐI LƯỢNG (kG): N' layer KCS_THONGKE + ghép tiêu đề bảng GẦN NHẤT theo toạ độ) → vá id22/32 (cầu thang 2163.02, inox304 161.21); số ĐỌC nguyên văn + handle, KHÔNG tự cộng, tong_khoi_luong_kg vẫn tổng toàn file. Red-team-impl engine THẬT (A/B/C đều xác minh trên KT/KC). Test +13 → **misc-tools 94→107**; **30 tool**; check.sh [27/27], takeoff 272, 0 regress. ✅ commit+push+deploy+verify LIVE `81b0a52`. **⏳ CÒN (task riêng, LIVE):** ~35 ca ROUTING-MISS → vá SYSTEM_PROMPT/tool-desc (BẮT BUỘC gọi `tim_kiem` theo từ-khoá vật liệu TRƯỚC khi kết luận 'không có', clusters R1-R5) + I3-U L2 prompt-half; cần đo LIVE A/B. 13 hatang → nâng RAM (nhóm C).
- **✅ I3-U LỚP 2 (CODE-ONLY) — QUY ĐỔI ĐƠN VỊ ĐỘ DÀI tất định trong `tinh_dai_luong` — LIVE `9d90b25` [2026-07-26]:** Helper `_quy_doi_don_vi_dai` quy CHUỖI có TAG đơn-vị-độ-dài (`'3.6m'`/`'360cm'`/`'36dm'`/`'3600mm'`/`'3,6m'`) → mm (`re.fullmatch` neo đầu-cuối). **CODE tính, KHÔNG để LLM/đối tác nhân ×1000.** Cắm vào vòng dispatch `tinh_dai_luong` **CHỈ khi `dv=='mm'` VÀ input là CHUỖI khớp tag** → vá đường **TỪ-CHỐI-OAN** (trước: `'3.6m'` qua `_nd` giữ raw string → cổng 'xau' đá vào `so_lieu_khong_hop_le`). LỘ giả định qua field `quy_doi_don_vi` (thất-bại-phải-lộ). **Robust cho MỌI MCP-client:** client trực tiếp (Claude Desktop/Cursor) KHÔNG có luật ×1000 của SYSTEM_PROMPT → `'3.6m'` tới thẳng tool bị từ-chối-oan; nay tool tự hiểu. **Chọn qua workflow probe 5 ứng viên nhóm A (`wf_fc8788d7-dd2`): CẢ 5 HOAN** (guard đã cực rộng tay, từ-chối-oan thật ≈0/198; lớp resolver bão hoà chống-bịa; detector-bỏ-sót báo động 90% mọi file; U2/U3-OCR blocked) = **safe-cheap-A gần CẠN**; C4 code-only là giao điểm duy nhất (chạm recall/từ-chối-oan × doable-now × không-blocked × rủi-ro-thấp). **AN TOÀN (red-team-impl chạy engine THẬT 54/54):** degrade-safe — số/`'3600'`/bare-`3.6`/`kg`/`m²`/`'-3.6m'`/`'0m'`/`'3.6 m2'` giữ hành vi cũ (0 regression); CHỈ tag tường minh + CHỈ `dv=='mm'` (gate dv; `_rs_bs_only` dùng chung bộ/kg/m² KHÔNG đụng); KHÔNG đoán đơn vị số-trần (chống bịa đơn vị); KHÔNG động SYSTEM_PROMPT/grounding-guard → **luồng Gemini KHÔNG đổi hành vi (không cần đo LIVE để ship)**; I3-U L1 vẫn hoạt động; note KHÔNG tạo anchor grounding mới. Test +10 (I3-U L2 + C1-lite standing invariant) → **takeoff 262→272**; check.sh [27/27] PASS, 0 regress. ✅ commit+push+deploy+verify LIVE `9d90b25`. **⏳ PHẦN CÒN LẠI (user CHỐT làm LẦN GIAO VIỆC SAU + đo LIVE — NHẮC user):** đổi SYSTEM_PROMPT để CODE sở hữu unit-math (Gemini truyền 'giá-trị+đơn-vị verbatim', ngưng ×1000) + update `tests/kichban_gd2.py` = mở khoá giá trị thật.
- **✅ I9 — TÁCH SYSTEM_PROMPT (luật bất-biến / quy-ước-VN) CÓ VERSION + HASH — LIVE `de69324` [2026-07-25]:** SYSTEM_PROMPT TRƯỚC là 1 tuple string 124 dòng (rule 1-17 trộn lẫn, rule 15 chống-thao-túng kẹt giữa 14 và 16, rule 9 cuối, **2 nhãn "8c" trùng**). Nay tách thành **23 mảnh có TÊN** gộp `_INVARIANT`(7: phân-biệt/1/2/5/6/15/9) / `_VN_CONVENTION`(15) / `_HEADER`(1) + `_EMIT_ORDER` **GIỮ NGUYÊN byte order** → `SYSTEM_PROMPT="".join(_EMIT_ORDER)` **byte-identical** (sha256 `bea17c6e…a70e18` KHÔNG đổi). Thêm `PROMPT_VERSION`+`PROMPT_HASH` lộ ở `/version` (trước /version KHÔNG có định danh prompt). **Chọn hướng qua workflow 9-agent** (3 design A+/B/C + 5 red-team lăng kính CHẠY ENGINE THẬT + synth): **5/5 lăng kính chọn A+**. **B (đảo thứ tự thật) BÁC** vì (i) prompt = lõi chống-bịa, đổi text cần đo LIVE mà LIVE **KHÔNG chứng minh nổi** non-regression — đo THẬT 2 run temp=0 trùng **0/173** câu trả lời + lệch **44% handle-set**, nhóm an toàn **0/23** tái lập → noise floor > effect size (bỏ chặn tiền/API cũng vô ích: nút thắt là ĐỘ PHÂN GIẢI ĐO); (ii) "tách thật" phần lớn **ẢO** — 34/39 mệnh đề chống-bịa (⛔) lồng trong thân rule VN, đảo header không dời được. **C-external BÁC** (prompt ra file phá offline-import mà check.sh + 2 test prompt phụ thuộc). **AN TOÀN:** fragment sinh bằng **SLICE chuỗi đóng băng** (KHÔNG gõ tay → chống hỏng ★/⛔/space); 2 nhãn "8c" → tách tên `_P_R8c_OLE`/`_P_R8c_INOX` (khử trùng ở SOURCE, GIỮ nhãn byte-identical); docstring **TRUNG THỰC** ('tách' = nhãn/index, KHÔNG phải tách rời điều khoản); consumer (585/678 + 2 substring test) không đụng vì byte-identical. **Byte-lock test** `test_prompt_taxonomy.py` **24 ca** (sha256 đóng băng + lắp ráp + phân hoạch + anchor regression) → wired check.sh **[26→27]**; `test_app_routes` +2 (prompt_version/prompt_hash). **check.sh [27/27]** · takeoff 262/misc 94/grounding 47/qa 129 **KHÔNG đổi = 0 regress**. Hash `bea17c6e` GIỮ NGUYÊN local Windows-CRLF + Render Linux-LF (fragment dùng escape `\n`, không newline vật lý → **EOL-independent**). ✅ commit+push+deploy+verify LIVE `de69324` (workflow `wf_f1111f89-fa0`). **⏳ Option B (reorder sạch + dọn nhãn 8c) HOÃN** = 1 dòng sửa `_EMIT_ORDER` rồi ĐO LIVE A/B với baseline đóng băng — CHỈ làm khi muốn thử giả thuyết primacy, KHÔNG phải kết luận sẵn (red-team cho thấy upside trong noise).
- **✅ I3-U LỚP 1 — VÁ 2 BUG SAI-TỰ-TIN trong `tinh_dai_luong` — LIVE `21926c9` [2026-07-25]:** phần LÀM-NGAY tách ra từ I3-U (bug đơn-vị-1000×), corpus-independent, không ngưỡng, additive. **(1b)** kết quả tính LÀM TRÒN VỀ 0.0 dù mọi input dương (vd `chieu_cao=3.6` gõ MÉT thay mm) TRƯỚC trả `co_ket_qua=True + 0.0 m³ + ghi_chu "đọc trực tiếp từ file (đáng tin)"` = lệch 1000× đóng nhãn đáng tin (repro SỐNG). Nay `kq<=0` → `co_ket_qua=False` + cờ BOOL `nghi_ngo_don_vi` + prose SẠCH SỐ "kiểm lại đơn vị (mét/mm)"; mirror guard `net<=0` nhánh trừ lỗ. **(1a)** input ĐỐI TÁC CẤP (số trần, `nguon=nguoi_dung_cung_cap`) bị dán "Mọi input đọc trực tiếp từ file (đáng tin)" = khẳng định SAI provenance; nay tách nhánh theo `co_dung_cap`: VẪN giữ "đáng tin" theo số đối tác nhập (R1 pos-control còn xanh) NHƯNG bỏ khẳng định sai "đọc từ file" + nhắc đối chiếu đơn vị. **Red-team-trước-code:** kiểm 12 công thức + độ làm tròn → 0 cấu kiện thật round về 0.0 (không FP). **Red-team-impl (repro engine thật):** bug chặn ✓ · ca đúng 3600→0.174 giữ ✓ · 0.05 m³ hợp lệ KHÔNG bị chặn ✓ · biên 0.0 chặn ✓. **Prose sạch số + cờ bool → KHÔNG lọt `_collect_numbers`** (không tái sinh -22.75). Test khoá +4 → **takeoff 258→262**; gate **[25/25]** · qa 129 · 0 regress. ✅ commit+push+deploy+verify LIVE `21926c9`.
  - **⛔ I3-U NGƯỠNG-SÀN = NO_GO có SỐ CỨNG [2026-07-25]:** firm-gate ĐÃ MỞ (đếm **8 đơn vị thiết kế** phân biệt trong corpus — trùng fax/block/nhân sự) nhưng khi CÓ data để calibrate thì data BÁC thiết kế: đo THẬT **86 file / 77.083 dim** → FP dưới sàn: toàn corpus <50mm=**7.67%**, chỉ-mm-khai=**4.64%**, **file GỐC-MÉT (hạ tầng) <30mm=34.9% / <50mm=37.3% / <100mm=41.0%**. Corpus DỊ CHỦNG đơn vị (40 mm/25 mét/9 inch…), nhãn đơn vị KHÔNG đáng tin → không tách sạch. ⇒ **Mọi ngưỡng sàn mm cố định = 34-41% FP trên bản vẽ mét-native. I3-U dạng ngưỡng-sàn KHÔNG khả thi kể cả khi đủ firm.** Lưu memory `[[project-i3-bounds-check-nogo]]`.
  - **⏳ CÒN (đã có kế hoạch, CHƯA code):** **Lớp 2** (unit-tag D+C: `_nd` nhận `'3.6m'/'3600'`, quy đổi tất định, thiếu đơn vị → HỎI) — cần user quyết có động prompt Gemini không (degrade-safe: số trần → giữ hành vi cũ). **Lớp 3** (Thiết kế A cross-check nội bộ scale-invariant) — HOÃN tới đo tỷ-lệ-bắn trên 86 file trước-code. Lớp 1 bắt ca round-về-0; KHÔNG phải guard tổng quát (gõ 250 thay 2500 ra số >0 vẫn lọt — việc của L2/L3).
- **✅ I5 (THU GỌN sau nghiên cứu) — `tim_kiem`/`liet_ke_chu_theo_layer` LỘ cờ `bi_cat` + nudge — LIVE `8f00510` [2026-07-25]:** **Nghiên cứu (probe chạy THẬT trên corpus) PIVOT scope: phần lớn I5 KHÔNG đáng làm** — (1) **pagination offset/cursor = ROI THẤP:** đo thật, từ khoá ngữ-nghĩa (tên cấu kiện) max ~123 hits (san=123/cong=107/thep=95/cot=76) **KHÔNG BAO GIỜ chạm trần 200**; query >200 đều là nhiễu substring; `so_ket_qua` luôn phơi tổng thật → cursor chỉ thêm bề-mặt-API, ~0 recall → **BỎ**. (2) **`dem_theo_block` = PHẦN LỚN THỪA:** value-probe cho thấy 2/3 file mọi block ngữ-nghĩa đã trong top-25 của `liet_ke_block`; file thứ 3 block ngoài top-25 chủ yếu annotation (Tieude/_ArchTick), lại đúng bẫy "số-chèn ≠ số-cấu-kiện" → **DEFER** (chống-overclaim). **CHỈ CÒN khe recall ĐO ĐƯỢC:** default `gioi_han=40 < 76-123` → kết quả ngữ-nghĩa bị cắt âm thầm. **Vá:** thêm cờ BOOL `bi_cat` (len(hits)>len(ket)) + nudge ghi_chu "gọi lại với gioi_han cao hơn" cho `tim_kiem` VÀ `liet_ke_chu_theo_layer`. Prose SẠCH SỐ (số ở field so_ket_qua/hien_thi; nudge không chữ số → không lọt grounding dù `tim_kiem` KHÔNG bị loại khỏi tool_numbers). ADDITIVE: giữ default 40 (không phình token), giữ hành vi gioi_han âm→hien_thi=0 (test_takeoff:148). Red-team-impl chạy engine thật (tim_kiem('1') default 40 → bi_cat=True+nudge; gioi_han=200 lấy hết; từ hiếm → False; gioi_han=-5 → hien_thi=0). Test khoá +8 (`test_misc_tools` kiem_tim_kiem_bicat KT/KC) → **misc-tools 84→94**; gate [26/26], qa 129, 0 regress. ✅ LIVE `8f00510`. **Bài học: nghiên cứu-trước-code SAVE việc build 2 feature ROI thấp (pagination + dem_theo_block).**
- **✅ I4a — DETECTOR BẢNG VẼ-BẰNG-NÉT (LINE grid + TEXT) + CẢNH BÁO — LIVE `6ff81cc` [2026-07-25]:** vá lỗ hổng **RECALL "miss âm thầm"** (điểm yếu THẬT của demo). **Đo corpus thật (probe hình học 65 file):** ~29% file có bảng schedule vẽ-bằng-nét mà engine đọc 0 block thép; **~8 bản vẽ KẾT CẤU có bảng thống kê THÉP vẽ-bằng-nét → `thong_ke_thep` trả `thep_kg=0` + `co_bang_thong_ke=False` = BỎ SÓT TOÀN BỘ ÂM THẦM** (thép kết cấu = đại lượng giá-trị-nhất). Gần 50/50 với quy ước block-ATTRIB (đọc được) → KHÔNG edge-case. Theo tiền lệ **U3/bug-C**: chốt **I4a = DETECT + CẢNH BÁO an toàn** (KHÔNG đọc nội dung — reader I4b rủi ro overfit để SAU). **Cơ chế:** MCP tool #29 `phat_hien_bang_ve_net` (lazy-scan modelspace, CAP=`RENDER_MAX_ENTITIES` chống OOM); tín hiệu HÌNH HỌC cổng-VÀ LOCAL **miễn nhiễm garble/đơn-vị**: ≥4 vạch-hàng ĐỒNG-ĐIỂM (lượng-tử THÍCH NGHI theo đơn-vị, KHÔNG mm tuyệt đối) + ≥2 cột (TRẦN 15 loại LƯỚI-TRỤC cột nhà cols=48) + ≥3 chữ trong bbox. Trả **bool + so_vung + prose SẠCH SỐ**, FAIL-OPEN try/except. **KHÔNG lọt grounding:** `mcp_bridge` LOẠI tên tool khỏi `tool_numbers` (dạng tuple, cơ chế U3). SYSTEM_PROMPT **rule 8d** (`thong_ke_thep`=0 trên KẾT CẤU → gọi tool; `co_bang_ve_net=true` → ĐỐI CHIẾU TAY, cấm nói 'bản vẽ không có bảng'). **Red-team-impl (chạy engine THẬT đa-domain):** DƯƠNG 6/6 (thép HIEP CAT/KC nha cong an/KET CAU THAN/Ninh Hai + kiến-trúc có bảng cửa/toạ-độ/thiết-bị THẬT); ÂM 2/2 (mặt-cắt 08.MAT CAT MUONG, bảng ở OLE 4.Thong ke thep SUA); lưới-trục cols=48 bị loại đúng. Test khoá tổng hợp (DXF synthetic) **9/9** [`test_bang_ve_net.py`] (dương/âm/fail-open/grounding-exclude/prose-sạch-số) → check.sh [25/25]→**[26/26]** · grounding 46→47 · **28→29 tool** · qa 129 · 0 regress. ✅ commit+push+deploy+verify LIVE `6ff81cc`. **RECALL-FIRST: chỉ LỘ cờ mềm, KHÔNG tự đọc/cộng số.** **⏳ I4b (đọc NỘI DUNG bảng → tổng kg) HOÃN** (overfit cao theo style bảng — cần corpus đa-firm + red-team nặng, giống gate P5).
- **✅ I2 — SHEET EXCEL 'Tien_luong' (BOQ PHẲNG chuẩn dự toán VN) — LIVE `86776b9` [2026-07-25]:** vá điểm yếu P1 "đầu-ra VN". Excel TRƯỚC chỉ 1 sheet tổng hợp 8 cột + các khối metadata (khó cắm vào phần mềm dự toán). Nay THÊM sheet phẳng copy-ready: [STT | Mã hiệu(TRỐNG) | Tên công tác | Đơn vị | Khối lượng | Diễn giải(=nguồn) | Ghi chú], nhóm theo `loai` + subtotal. QS dán thẳng vào G8/F1/Dự toán GXD (tự áp mã định mức + giá). **AN TOÀN (red-team-trước-code + red-team-impl chạy xuat_excel thật + mở lại .xlsx):** TÁI DÙNG cùng object `th` (không gọi lại tong_hop, không tính lại số → **2 sheet KHÔNG thể lệch** — verify subtotal Tien_luong khớp TUYỆT ĐỐI TỔNG PHỤ bảng chính); `create_sheet` KHÔNG index (nối cuối) + KHÔNG đổi `wb.active` → sheet chính vẫn active → test_excel_content (đọc wb.active) không đổi; subtotal LẤY TRỰC TIẾP `th['tong_phu']` (không tự cộng → không double-count, tôn trọng `_khong_cong`); **LOẠI `quy_uoc_chua_xac_nhan` (bất biến P4** — chỉ dùng `th['bang']`; verify số học 12.5 ĐANG DẠY KHÔNG lọt Tien_luong); **return dict KHÔNG đổi** → số nội dung Excel nằm trong FILE, không vào `_collect_numbers`/grounding. **Phạm vi (user chốt 2026-07-09): CHỈ khối lượng, KHÔNG cột đơn giá/thành tiền** (README nhắc QS tự áp mã+giá). Row thiếu số (Tiết diện gia_tri chuỗi) → ô Khối lượng TRỐNG + ghi chú "cần thêm số", KHÔNG chế số. Test khoá +4 (khối [C]) → **excel-content 17→21**; gate [25/25], qa 129, 0 regress. ✅ commit+push+deploy+verify LIVE `86776b9`. **⏳ v2 (chưa, HOÃN):** cột Diễn-giải công-thức-sống (cần mở tong_hop mang toán hạng — đụng tầng tổng hợp, rủi ro 'bịa tái sinh'); mã hiệu định mức tự động (cần DB định mức); đơn giá/thành tiền (ngoài phạm vi tới khi user mở lại).
- **✅ U6(C) — HẠ TRẦN ENTITY RENDER 20000→6000 (env `RENDER_MAX_ENTITIES`) — LIVE `a242027` [2026-07-25]:** đòn bẩy (C) chống ĐỈNH RAM render mà GIỮ 100% chức năng. **Đo thật (matplotlib ~26KB/entity):** render 1 cửa-sổ dày 20000 entity ~ **+500-600MB** RAM (khảo sát cũ CHỈ đo parse, BỎ SÓT spike render này); cửa-sổ highlight THẬT chỉ vẽ **≤1067 entity** → trần 6000 KHÔNG cắt ca thường (dư 5.6×), chỉ chặn cửa-sổ DÀY bệnh lý (worst-case ~500MB→~180MB, **~3×**). **AN TOÀN (verify code + engine thật):** ô KHOANH ĐỎ vẽ ĐỘC LẬP (`ax.add_patch`) → hạ trần KHÔNG mất marker, chỉ giảm nét NỀN. **THẤT-BẠI-PHẢI-LỘ:** `highlight` trả thêm cờ BOOL `anh_bi_cat` + prose SẠCH SỐ ("vùng quá dày, vị trí khoanh đỏ vẫn đúng") → không lọt `_collect_numbers`. Env-tunable (lên gói RAM mạnh nâng lại). Red-team-impl (repro engine thật): default 6000; highlight thường 964 không đổi + `anh_bi_cat=False`; cửa-sổ 7467→cắt 6000; PNG+ô đỏ còn; override 2000 chạy (+43MB). Test khoá +4 → **visual-highlight 15→19**; gate [25/25], qa 129, 0 regress. ✅ commit+push+deploy+verify LIVE `a242027`. **⏳ CÒN đòn bẩy (ii):** nâng RAM Standard 2GB (config HELD `f025ad7` + hạ MAX_SESSIONS 4→2) — chờ user bật billing Render.
- **📌 U6 iterdxf-streaming — HOÃN DỨT KHOÁT [2026-07-25]:** iterdxf **PHÁ 5 chức năng** (I1 `entitydb.get`, render RenderContext+quét lần 2, U3 OLE paperspace, layers, INSUNITS) → rớt gate [11]+[24] VÀ **không cứu OOM** (render vẫn readfile lại). Hệ số nạp 7-8x bất biến với ràng buộc load-once-random-access. Trần thật = hằng `READFILE_MAX_MB=45`. Đã thay bằng U6(C) [trên] + (ii) nâng RAM. Lưu memory `[[project-chiu-tai-va-chi-phi]]`.
- **✅ I1b — VÁ LỖ THẬT GROUNDING-GUARD (m2/m3) — LIVE `b2a0ea5` [2026-07-24]:** guard chống bịa TRƯỚC **MÙ với diện-tích/thể-tích BỊA dạng 'X m2'/'X m3'** (Gemini viết SỐ thay mũ ²/³) vì `_MAHIEU_RES[4]` ăn nhầm 'm2' như mã-hiệu → `do_luong` rỗng → guard không khai hoả. Vá (`_answer_numbers`): chuẩn hoá `m2→m², m3→m³` (chỉ khi liền sau SỐ) TRƯỚC strip; KHÔNG đụng nhãn trục 'M2', VẪN strip 'AxB mm'. **Repro engine thật** (giả thuyết FN5-handle-che SAI). **LIVE battery bắt bug bản-vá-đầu** (trích raw → nuke 'Cột 220x220 mm' id77) → sửa lại. Đo LIVE 2 lần: từ-chối **4→1 (giảm)**, id77 hết nuke. Test grounding **34→46**. **⏳ CÒN:** tầng-2 handle calibrate (I1 tầng-2 đang im).
- **⏳ id135-E2E — VẪN CHỜ file hạ tầng ĐỘC LẬP (KHÔNG done) [2026-07-24]:** ⚠ tôi lỡ OVERCLAIM 'ĐẬU' rồi ROLLBACK. Sự thật (không bịa): battery LIVE trên `rachmop.dxf` (HT/CT-K, mốc -14.26) → Gemini trả ĐÚNG '-14.26m [1F601D]' (bug gốc bịa '-10m'). NHƯNG `rachmop` CHÍNH là file mà bug id135 phát hiện ra từ đó + câu battery được THIẾT KẾ quanh nó (ky_vong ghi cứng -14.26) → 'đậu' = **không tái phạm CA ĐÃ BIẾT, KHÔNG chứng minh tổng quát hoá**. id135-E2E THẬT (chống overfit) VẪN cần bản vẽ hạ tầng ĐỘC LẬP (nguồn khác) → đang xin đối tác. Fix chạy đúng trên ca đã biết = tín hiệu tốt, KHÔNG phải hoàn tất. **CẬP NHẬT TB6 [2026-07-24]:** đối tác gửi bộ hạ tầng ĐỘC LẬP THẬT (thoát/cấp nước TB6, `input_files/03.TB6/`, 26 file). E2E LIVE 2 file → tool + Gemini đọc ĐÚNG cao độ sâu nhất (-1.34m/-2.49m) + KHÔNG bị số-mồi đánh lừa ('cút -11,25 độ'=góc ống, 'block-25.3'=nhãn). = **GENERALIZATION + chống-mồi VALIDATED trên file ĐỘC LẬP** (rachmop không cho được). NHƯNG TB6 NÔNG (-2.49m, không -14m) → **deep-independent CÒN chờ** (yêu cầu gửi đối tác đã cập nhật nhấn ĐỘ SÂU: `input_files/YEU_CAU_FILE_HA_TANG_gui_doi_tac.txt`). **VẪN chưa mark id135 done.**
- **✅ I1 — GUARD VALIDATE HANDLE — LIVE `de1ef47` [2026-07-24]:** guard chống bịa TRƯỚC chỉ kiểm SỐ; nay đối chiếu **handle** model trích dẫn với handle tool ĐÃ phát / có trong entitydb. **ADDITIVE THUẦN** (chỉ nối cảnh báo cuối câu, KHÔNG sửa/từ chối). 3 tầng: tool-phát→IM · trong-file→IM · không-đâu-có→⚠ (mã hiệu/câu hỏi→ℹ mềm). Cấu phần: `_collect_handles`+`_handle_tokens`(FORM A/B/C+echo)+`_kiem_handle`/`_apply_i1` (mcp_bridge) · MCP tool #28 `kiem_tra_handle` (host-only, CHỈ ĐỌC, entitydb.get, KHÔNG phán quyết) · `app.py` lưu **answer_goc** sạch vào history. **Chọn qua workflow 15-agent** (design red-team FP=0/854 câu thật, TP=2/854 — model chép hụt handle `449C4`→`44C4`) → GO_WITH_ADJ. **Red-team IMPLEMENTATION** (tự-repro file 26MB) vá F1 (kích thước trong ngoặc bị ⚠ nhầm → tách dãy số) + F2 (câu từ chối tự nhiên → bỏ qua). Test `test_handle_guard.py` **44/44**; check.sh **[23/23]→[24/24]** · grounding 34 KHÔNG đổi · 0 regress. **BẤT BIẾN:** không ngưỡng độ dài/tần suất (chống -22.75), không trường phán quyết (chống thap_nhat_dang_tin), fail-open. ✅ commit+push+deploy+verify LIVE `de1ef47`. **⏳ CHƯA (sau):** I1b (FN5 `_guard_text`) + đo LIVE battery 198 câu để calibrate hiển thị tầng-2.
- **✅ I3-B — BOUNDS-CHECK ĐƯỜNG KÍNH THÉP — LIVE `82951db` (verify /version+/health 2026-07-24) [thiết kế lại sau NO_GO]:** phần SỐNG SÓT của I3, tách riêng. Bound Ø thép TRÒN trên ô DK bảng thống kê (`_dk_bat_kha`: `_to_num` BARE, ≤0 hoặc >60mm; KHÔNG bóc Ø/d chống '2Ø16'→216; KHÔNG siết cận dưới → lưới hàn D3/D4/D5 hợp lệ). LỘ `nghi_ngo` (BOOL) + prose KHÔNG số; cờ trong `_acc_thep` KHÔNG đụng kg/so_thanh/dai_m → `tong_kg` bất biến; surface `thong_ke_thep` nhánh TỔNG (`co_nghi_ngo_duong_kinh`) + HỎI-1-CỠ. **KHÔNG-LỌT-GROUNDING (verify engine thật):** biên 60 + bất-khả 1600 ∉ `_collect_numbers` (1600 CHỈ ở KEY 'Ø1600'; cờ bool bị bỏ) — đóng đúng kênh đã giết plan cũ. Red-team 4/4 lăng kính GO_WITH_ADJ. Test `test_i3_bounds.py` 24/24; check.sh [24/24]→[25/25]; misc/takeoff/qa 0 regress. FP đã biết (soft): PT/Dywidag Ø65/75; bảng phi-thép reuse cột TL+DK>60 (hiếm).
- **⏳ I3-U — BUG ĐƠN-VỊ-1000× = HOÃN tới corpus ≥3 firm [2026-07-24, user chốt]:** bug thật `tinh_dai_luong(chieu_cao=3.6 gõ MÉT)` → 0.005 m³ vẫn 'đáng tin'. Red-team 4/4 GO_WITH_ADJ, **cơ chế AN TOÀN đã verify** (early-return TRƯỚC compute → số sai KHÔNG phát; `_MM_FLOOR` code-only KHÔNG lọt grounding). NHƯNG ngưỡng sàn (dưới MỌI mm hợp lệ) + tiền đề 'mọi mm nguyên' rút **n=1 file** = OVERFIT → FP sàn/lớp mỏng 30-49mm + dim lẻ (grid-split 4237.5, imperial 101.6) → cần đa-firm calibrate (đúng gate P5). **Hướng ĐÃ VET (code khi có corpus):** neo `dv=='mm'`+`nguon` (không theo đại-lượng); early-return+HỎI (không tự quy đổi); CỬA-THOÁT xác-nhận-đơn-vị per-input (tránh recall dead-end); prose 'mét HOẶC cm'; CẤM trần-trên-theo-đại-lượng (tái sinh -22.75); chỉ bắt hướng XUỐNG. Memory `[[project-i3-bounds-check-nogo]]`.

- **✅ U3 — ĐỌC BẢNG EXCEL NHÚNG (OLE) — LIVE [2026-07-22 đêm, `fd48b19`; ghi-bù 2026-07-23 sau crash]:** bảng thống kê nằm trong OLE2Frame (Excel nhúng) TRƯỚC đây engine đọc 0 (bug C GĐ4, chỉ cảnh báo) → nay **đọc THẬT** qua binary. Module `oleexcel.py`: `ezdxf OLE2Frame.binary_data()` → magic **CFBF offset≠0** → `olefile` → `xlrd`(vá decode khoan dung .xls VN)/`openpyxl`. Deps mới: **olefile, xlrd**. Probe corpus: **~89% OLE đọc được binary** (KHÔNG OCR); "Thong ke thep SUA" + THPT 67 bảng → đọc hết. **AN TOÀN chống bịa (red-team 6 hướng / 26 finding / 8 CHẶN):** MCP tool #27 `doc_bang_nhung` chỉ trả **HÀNG bảng + nguồn `ole:<handle>:<sheet>`**, máy **KHÔNG tự chọn ô TỔNG / tự cộng**; **số ô OLE KHÔNG vào rổ grounding** (`mcp_bridge` loại `doc_bang_nhung` — nếu vào sẽ flooding sập guard chống bịa); giàu hoá `ole_nhung` 1-nguồn (fake test cũ không vỡ); trần RAM 150k ô. Commit `1cc84ad` (module+probe+test) + `fd48b19` (wiring LIVE, verify /version+/health). Test `test_oleexcel.py` **18/18** + ole-cảnh-báo 51 → check.sh **[22/22]→[23/23]** · **0-OLE không đổi · 0 regress**. Fixture THEP_OLE ở `tests/corpus_local` (gitignored). **⏳ v2 CHƯA:** OCR fallback tầng 2 cho **~11% OLE dạng ẢNH** (StaticDib/PBrush/EMF); diễn giải bảng thép → tổng kg (overfit — CHẶN tới ≥3 firm/P5). Design lưu `[[project-doi-sanh-kien-truc]]`.

- **✅ AUDIT GĐ4 (34-agent) + VÁ BÓ F1/F2/F3/F4 — LIVE [2026-07-22, `fd7019d`]:** user yêu cầu rà tester chuyên nghiệp TRƯỚC khi đi tiếp. Workflow 34-agent (6 mảng → skeptic-verify → synth): **0 bug nghiêm trọng** (git toàn vẹn sau rebase/filter-repo/restore, id135 an toàn, số verify giữ nguyên), tìm 2 gap thật trong CHÍNH bản vá phiên trước → vá hết:
  - **F1** (`c…`→ nay): cảnh báo OLE cắm đủ 3 tuyến số-lượng/kích-thước (`tra_cuu_so_luong`/`liet_ke_so_luong`/`thong_tin_kich_thuoc`) CHỈ khi kết quả RỖNG (gate-on-empty chống nhiễu).
  - **F4** (RED-TEAM trước code, workflow 4-agent → GO_WITH_ADJUSTMENTS): parser cao độ — bác blacklist-nhãn (vỡ garble) + Design-B (drop id135). CHỐT: `_CD_INL` khôi phục `\s*`; `+`/`±` mọi gap + `-` dính liền → min/max; **`-` DẤU CÁCH ('WORD - n.nnn', đồng dạng FP `CH-2.700` VÀ id135 `cốt-14.260`) → `canh_bao`** (LỘ, không bịa min, miễn nhiễm garble). Thu lại mốc thật dạng cách `+7.69/+8.5`. Verify engine thật: số verify GIỮ NGUYÊN.
  - **F2/F3** (hardening THẤP): F2 quét OLE cả paperspace (helper `_ole_ngoai_modelspace`, corpus 0 paperspace-OLE nên không đổi số); F3 bọc nhánh `co_trong_bang=False`. **CÒN LATENT: OLE trong định-nghĩa-BLOCK** → xem **U3**.
  - **D6 tự rút lại claim RAM:** "45MB×11.3=577MB→OOM" SAI (11.3x ở file 26.5MB = ngoại suy sai); rủi ro thật ở `MAX_SESSIONS=4` → xem **U6**.
  - Test: cao_do 27→31 · OLE 25→44 · gate [22/22] · qa 129 · 0 regress. Deploy+verify LIVE `/version`=fd7019d + `/health` ok.

- **🔥 GĐ4 ĐÃ CHẠY — CORPUS VỀ ĐỦ, TÌM ĐƯỢC 3 BUG THẬT (2026-07-17, ⚠ CHƯA VÁ, CHƯA COMMIT):** corpus đối tác **ĐÃ VỀ** `input_files\` (8 công trình mới + 2 cũ = **66 file / 10 nhóm**, 62 dwg mới/168MB, không nén). Khảo sát bằng `tests/khao_sat_corpus.py` (1 lỗi: ĐIỆN CT-E ODA không convert nổi). **NÚT THẮT ≥3 FIRM ĐÃ MỞ.** Bộ môn mới: điện · cấp-thoát-nước · hạ-tầng/rãnh · phá-dỡ · TMB · bảng-thống-kê-thép riêng.
  - **TIN TỐT (không overfit hệ thống):** bộ đọc số lượng ăn **9/10 nhóm** (qty tổng 1617). `qty=0` chủ yếu ở điện/nước/TMB/phá-dỡ = vô hại.
  - **❌ "BUG A" (cao độ -22.75 lệch 21m) — ĐÃ TỰ BÁC BỎ. TOOL ĐANG TRẢ ĐÚNG. KHÔNG ĐƯỢC VÁ.** Cáo buộc ban đầu (SAI): `Ket cau Truong mam non Ket Sat` trả `cao_do_thap_nhat_m=-22.75` trong khi "đáy móng thật -1.85" ⇒ tưởng text rác cô lập. **RED-TEAM + TỰ KIỂM CHỨNG BÁC BỎ bằng 4 chứng cứ hội tụ:** (1) file ghi rõ `'GIẢI PHÁP KẾT CẤU MÓNG: MÓNG CỌC BÊ TÔNG CỐT THÉP'` + `'TCVN 10304:2014 MÓNG CỌC'` + `'SỐ LƯỢNG CỌC ĐẠI TRÀ: 157'`; (2) có nhãn `'ĐẦU CỌC'` cách marker 412 đơn vị; (3) sơ đồ cọc vẽ tỷ lệ 1:1 — chênh cao độ 22.0m ↔ chênh toạ độ Y 21921 → **tỷ lệ 0.996** (rác không thể nằm đúng hình học tới 0.4%); (4) `-22.750` xuất hiện **2 lần** (tôi đã báo nhầm "1 lần"). ⇒ **`-22.75` = MŨI CỌC; `-1.85` = ĐÁY ĐÀI — hai đại lượng KHÁC nhau, cả hai đều THẬT.** Cọc 250×250, [P]=25T, dài 21.6m ở CT-C (Hải Dương, nền yếu ĐBSH) = bình thường. **BÀI HỌC: tôi suy đoán theo cảm tính miền ("mầm non 3 tầng không thể sâu 22m") mà KHÔNG đọc ghi chú kết cấu — đúng loại lỗi mà ethos dự án cấm.**
  - **🐞 RỦI RO THẬT (thay cho bug A) — HỢP ĐỒNG NGỮ NGHĨA lệch:** `mcp_bridge.py:208` quảng cáo tool là "CAO ĐỘ THẤP/SÂU NHẤT (**đáy móng**, đỉnh mái...)" NHƯNG tool tính **min của MỌI marker**. Trên bản vẽ móng cọc, hai thứ lệch **21m**. Đối tác hỏi "đáy móng sâu bao nhiêu" → nhận -22.75 (mũi cọc). **Vá = sửa MÔ TẢ, KHÔNG sửa số:** bỏ chữ "đáy móng" khỏi rule 8; `ghi_chu` nêu "thấp nhất XUẤT HIỆN trên bản vẽ — trên bản vẽ móng cọc thường là MŨI CỌC, KHÔNG mặc định là đáy đài".
  - **⛔ `thap_nhat_dang_tin` — NO_GO (red-team chặn, có bằng chứng chạy thật):** tiêm mốc id135 `-14.26` vào phân bố cao độ THẬT của **7/7 file kết cấu** → `_nghi()` gắn cờ CẢ 7, và `thap_nhat_dang_tin` trả số **nông hơn 11.26–13.23m** = ĐÚNG con số sai của id135, lại đóng nhãn "đáng tin" ⇒ **TÁI SINH id135**. Trường này là *phán quyết* đội lốt *dữ liệu*. BỎ HẲN, không có biến thể an toàn.
  - **✅ 3 BUG RED-TEAM — ĐÃ VÁ HẾT [gate 22/22, cao_do 12→27, ⚠ chưa push]:** (a) **G3 fallback**: bỏ `or found`; pool rỗng → `co_cao_do=False` + thép vẫn LỘ ở `canh_bao` + ghi_chu nêu lý do (hết tự mâu thuẫn). (b) **`_nghi()`**: `med` nay tính trên gap GIỮA CÁC MỐC KHÁC (loại chính điểm đang xét) → outlier hết TỰ THỔI ngưỡng; thêm `_median` THẬT (chẵn → trung bình 2 giá trị giữa) thay median-TRÊN. Kết quả: 2 giá trị `0/-22.75` → **nghi=True** (trước False); `0/-0.05/-22.75` → cờ (trước thr=68.1 thoát); bớt 1 marker vô can KHÔNG lật cờ; 1 giá trị duy nhất → không cờ. (c) **`_CD_INL`**: bỏ `\s*` giữa dấu và số → `'CH - 2.700'` (CHIỀU CAO, 9T KT) hết bị đọc thành cao độ -2.7. **Lọc theo HÌNH THỨC KÝ HIỆU (dấu phải dính liền), KHÔNG theo tần suất/cô lập → id135 an toàn** (test khoá: inline `-2.700` và `-14.26` dính liền VẪN đọc được). **Verify corpus thật: mọi số đã verify GIỮ NGUYÊN** (CT-A KC -1.85/FEF03 · KT -2.1/A51A7 · 9T KC -3.0 · CT-C mũi cọc -22.75 vẫn trả, nghi=True); CHỈ 9T KT đổi **-2.7→-1.6** (đúng chủ đích, marker 689→688). Test `[F1][F2][F3]` 12 ca.
  - **~~🐞 3 BUG THẬT do red-team tìm ra (độc lập, CHƯA vá)~~ [ĐÃ VÁ — xem trên]:** (a) **G3 fallback `pool = ... or found`** (`tools_core:1467`): khi MỌI marker ở layer thép → giá trị thép quay lại làm đáp án với `nghi_ngo=false` VÀ đồng thời nằm trong `canh_bao` ghi "đã loại khỏi min/max" ⇒ **output tự mâu thuẫn** (repro: min=-44.1 layer KCS_SOTHEP). Vá: bỏ fallback, pool rỗng → `co_cao_do=False`. (b) **`_nghi()` toán sai:** với **2 giá trị duy nhất KHÔNG BAO GIỜ cờ được** (thr=max(3·med,5) ≥ 3g > g — chứng minh + repro: `0/-22.75` → nghi=False); median-TRÊN chọn gap lớn (`0/-0.05/-22.75` → thr=68.1 → thoát); **outlier tự thổi `med` để tự thoát** (bớt 1 marker vô can là LẬT cờ). **7/38 file corpus có ≤3 giá trị.** (c) **`_CD_INL` đọc gạch-nối thành dấu-trừ:** `'CH - 2.700'` (= CHIỀU CAO 2.7m) bị đọc thành cao độ **-2.7** (9T KT, layer 'Net Text') ⇒ FP parser.
  - **❌ BUG B (text trong BLOCK không đọc) — ĐÃ TỰ BÁC BỎ, KHÔNG PHẢI BUG.** Giả thuyết ban đầu: `tools_core:832` chỉ duyệt `doc.modelspace()` + INSERT chỉ đọc `e.attribs` → text trong block definition vô hình ⇒ tưởng là lỗ recall (dẫn chứng `4. Thong ke thep SUA` đọc 17/1095). **KIỂM CHỨNG BÁC BỎ:** text trong block chủ yếu là **KHUNG TÊN** — file thép: 272 text được-chèn đều là `'công trình:'`/`'đơn vị tư vấn thiết kế:'`/`'ks. [tên đã ẩn]'` + 743 text ở block thư viện KHÔNG dùng; CT-A (corpus CŨ, 129 test QA xanh) cũng bị heuristic gắn cờ nhưng mẫu là `'tên bản vẽ :'`/`'chủ đầu tư :'` (block `khungten30-10`). ⇒ Bỏ qua text block gần như là **TÍNH NĂNG** (lọc nhiễu khung tên), không phải lỗ. **Bài học: heuristic "blk_txt > 2× đọc-được" OVER-FLAG — nó gắn cờ cả file corpus cũ đang đọc ĐÚNG.** Nội dung thật của file thép nằm ở OLE (bug C), KHÔNG ở block. (⚠ Chưa soi hết: mới lấy mẫu 6 text/file; nếu sau này nghi block chứa nhãn thật (tag cửa/mốc) thì phải soi lại có hệ thống.)
  - **🐞 BUG C — OLE2FRAME (bảng Excel NHÚNG) đọc ra số 0, không LỘ. PHỔ BIẾN: 19/65 file.** `4. Thong ke thep SUA.dwg` có **8 OLE2FRAME** = bảng thống kê thép nhúng Excel → ezdxf không đọc được blob OLE → `thep_kg=0` trên file tên "Thống kê thép" (đây MỚI là gốc của việc file 67.9MB chỉ ra 27 entity/17 text, KHÔNG phải bug B). Nặng nhất: `THPT CT-E_KET CAU` có **67** khung OLE; còn `00.So do vi tri` 2 · `TKTC-THPT MBTT` 4 · CT-D KC 4 · CT-A KT 2… Nguy cơ anti-bịa: nếu AI nói "thép = 0 kg" là SAI-TỰ-TIN; phải LỘ "bản vẽ có N bảng/đối tượng nhúng OLE không đọc được → số có thể THIẾU". (Thất bại phải lộ.) **Đây là đầu mục đáng làm nhất: phổ biến, rủi ro thấp (chỉ THÊM cảnh báo, không đổi số).**
  - **Ứng viên id135-E2E:** chưa có file hạ tầng mốc sâu thật; sâu nhất đáng tin = -3.0 (9T KC). File -22.75 là RÁC, KHÔNG dùng làm ca id135.

- **📌 ĐỌC TRƯỚC (2026-07-16 nối) — [ĐÃ CŨ: corpus nay ĐÃ VỀ, xem mục trên]:** **Corpus đối tác VẪN CHƯA CÓ TRÊN MÁY.** Đối tác gửi 7 thư mục qua Zalo nhưng đó là ảnh chụp ĐIỆN THOẠI — quét kỹ toàn C:/D: (kể cả `Zalo Received Files`, `D:\Zalo Data\...\ZaloDownloads`, mọi `.dwg/.dxf` sau 2026-07-10) = **0 file**. Cần user chép vào `input_files\`: Trụ sở làm việc 3/2024 (21,1MB) · C1 CT-D (112,9MB) · CA CT-F (76,2MB) · MN CT-C (74,1MB) · THPT hieu_F (70,4MB) · CA CT-G (2,6MB) · C1 CT-J (137,9MB). **≥3 công trình từ ≥3 firm là đủ mở khoá.** ODA **có sẵn** (`D:\Downloads\ODAFileConverter.exe`), D: còn 372GB → sẵn sàng nhận.

- **✅ CÔNG CỤ KHẢO SÁT CORPUS `tests/khao_sat_corpus.py` [2026-07-16 nối, ⚠ CHƯA COMMIT]:** file về là chạy được ngay: `python tests/khao_sat_corpus.py` (tuỳ chọn `--root/--gioi-han/--timeout`). Quét đệ quy → convert .dwg→.dxf qua ODA (CACHE) → đo RAM/kích thước → đếm layer/text/block/dim/sheet + **qty THEO NGUỒN** (bảng-thống-kê vs inline vs spatial = tín hiệu OVERFIT trên firm mới) → `cao_do_min_max` (tìm ứng viên id135) → `so_residual` (gap recall) → báo cáo bảng + `_khao_sat/bao_cao.json`. **Mỗi file 1 SUBPROCESS** (đỉnh RSS monotonic nên nạp chung sẽ sai số đo; + file lớn/hỏng không giết phiên: timeout + fail-soft, lỗi LỘ). Read-only với `--root`. Test **61 ca** (`test_khao_sat_corpus.py`, DXF tổng hợp — KHÔNG cần corpus thật) → check.sh **[20/20]→[21/21]** · takeoff 258 · qa 129 · 0 regress. Tự bắt+vá 3 bug khi chạy thật: đo-RAM im lặng hỏng (thiếu ctypes argtypes → handle 64-bit bị cắt) · **tracemalloc thổi RSS 2.1x** (công cụ đo làm hỏng số đo → mặc định TẮT) · hệ-số-rác ở file nhỏ (`MIN_MB_HE_SO=5`). (+ `.gitignore` `_khao_sat/` không ăn vì comment cuối dòng → 276MB suýt vào repo.)

- **⚠ ĐÍNH CHÍNH HỆ SỐ RAM — ẢNH HƯỞNG QUYẾT ĐỊNH TIỀN [2026-07-16 nối]:** memory + `render.yaml` HELD ghi **5.8x** nhưng đó là số **tracemalloc (Python-heap)**; Render chặn theo **RSS**. Mô hình đúng (đo thật 4 file): **RSS ≈ 68MB baseline + 6.9–8.1x × DXF** (9T KC 114.4MB→934MB = 8.1x). ⇒ ngưỡng 5.8x **hụt 25-40%**: 2GB + biên 0.7 → an toàn ~**170MB**, KHÔNG phải **200MB** như commit HELD `969822a`. Thêm: **`MAX_SESSIONS=4`** × 1 Drawing/subprocess ⇒ RAM tệ nhất ≈ **4×**(68+k×size). **CHƯA đối chiếu Linux** (đo trên Windows) → chạy lại script trên Render TRƯỚC khi chốt gói. → **Xem lại `READFILE_MAX_MB` 200→~170 + cân nhắc MAX_SESSIONS trước khi push HELD.** Memory [[project-chiu-tai-va-chi-phi]] đã cập nhật.

- **📌 CHỐT SỔ 2026-07-16 — ĐỌC TRƯỚC:** Phiên này = **4 fix đọc-số LIVE** (id84 `c0b85af` 142→59 · id135-guard `3ca5102` chống bịa · dầm `95f4282` 40→20 · cao_do_min_max `97ffc60` #26) + **quyết định chiến lược**. **NÚT THẮT CHÍNH = corpus ≥3 firm** (chặn GĐ4/P5/id135-E2E + lộ lỗi biên) → user đang xin đối tác 3–5 bản vẽ. **CHỊU TẢI FILE LỚN:** ràng buộc RAM cloud (đo thật DXF/RAM ~5.8x; Free 512MB chỉ đọc ≤45MB); **config nâng RAM sẵn `079c91c` (plan standard 2GB, đọc 200MB) CHƯA PUSH — chờ user bật billing Render** (nâng RAM = phí Render, KHÁC API key; đọc file LOCAL vẫn free ~vài trăm MB). Chi tiết memory [[project-chiu-tai-va-chi-phi]]. **F-B** (kênh học P3 vào web) vẫn chờ user quyết. ⚠ Git: local có 1 commit `079c91c` (render.yaml nâng RAM) GIỮ chưa push có chủ đích.

- **✅ THÊM TOOL `cao_do_min_max` — RECALL id135 (đọc cao độ thấp/cao nhất đúng) [2026-07-13 phiên nối 8, ⚠ CHƯA commit]:** hoàn thiện id135 (guard chặn bịa + tool đọc ĐÚNG). Thiết kế đã vet ở phiên trước (workflow design+red-team). MCP tool #26 (`cao_do_min_max`, `mcp_server.py` + method `tools_core.py`). Đọc RAW marker cao độ (regex `_CD_STD`/`_CD_INL`: dấu +/-/± + 1-3 số nguyên + **2-3 thập phân** [id135 -14.26=2, CT-A -1.850=3]), lấy min/max — **KHÔNG lọc tần suất ≥4/cluster** như `thong_tin_tang` (đó chính là lý do id135 miss mốc sâu thưa). RIÊNG tool (thong_tin_tang giữ cho chiều-cao-tầng). **Precision guards:** G1 bắt buộc dấu; G3 loại marker layer THÉP (`thep|sothep|rebar`, semantic) khỏi min/max nhưng LỘ ở `canh_bao`; G4/G5 flag `nghi_ngo` cho extreme cô lập/inline (chỉ FLAG, không âm thầm loại). Trả kèm handle + nguyên_văn (grounded → guard id135 giữ answer). SYSTEM_PROMPT rule 8: 'cao độ thấp/sâu/cao nhất' → cao_do_min_max, trích thap_nhat/cao_nhat (ĐỪNG lấy canh_bao). **Verify engine THẬT:** CT-A KC min=**-1.85**(FEF03)/max=**+10.8**(11FA7D); KT -2.1/+10.8; 9T KC min=**-3.0** (loại -44.1 thép)/max=+33.7; demo cửa co_cao_do=false. Test `test_cao_do_min_max.py` **12 ca** (real+handle + synthetic G1/G3/G4-5 + id135 -14.26 + guard) → check.sh **[19/19]→[20/20]** · takeoff 258 · qa 129 · 0 regress. **⚠ GIỚI HẠN overfit:** chỉ 2 firm (CT-A+9T), CHƯA có file hạ tầng/cầu-đường (ly trình K0+500 có thể FP) → cần ≥3 firm (P5/GĐ4). **✅ COMMIT `97ffc60` + push + deploy + verify LIVE** (`/version`=97ffc60 khớp + `/health` ok).

- **✅ VÁ DẦM DOUBLE-COUNT — over-count ~2× tổng dầm (residual id84) [2026-07-13 phiên nối 7, ✅ LIVE `95f4282`]:** phát hiện qua workflow re-hunt battery (khi nghiên cứu chọn đầu mục tiếp) — **outrank cao_do_min_max** (over-count là sai-tự-tin nguy hiểm hơn recall-miss). **Repro engine THẬT** (CT-A KC): `tong_so_luong('DM')`=**40** (đúng 20), DR/D2=40 (đúng 30), DC=34 (đúng 16). Gốc: callout inline **'DẦM DR-6 (SL=02)'** + nhãn spatial trần **'DR-6'** = CÙNG 1 dầm nhưng `_ma_key` BẢO THỦ (id84, giữ cả nhãn) không strip 'DẦM' → 2 key khác → KHÔNG dedup → cộng đôi. (Đài cọc id84 hết trùng vì nhãn 2 bên đều trần; dầm có tiền tố 'DẦM' trên inline nên lọt.) **Vá CẤU TRÚC — dedup CÓ-LOẠI** (`tools_core.py` `_ma_type`/`_ma_code`/`_types_of`/`_ma_group_key`): tách tiền-tố-LOẠI dẫn đầu (dầm/đài/cột…) khỏi MÃ; bare-code GỘP với type-code khi mã có loại DUY NHẤT ('DR-6' theo 'DẦM DR-6'), NHƯNG mã có ≥2 loại ('DẦM D1'+'CỬA D1') hoặc 0 loại → bare RIÊNG (GIỮ id84: 'DẦM D1'≠'CỬA D1', đài 'ĐC-3' 2 bản trần vẫn gộp). Áp cả 3 dedup site (tra_so_luong/tong_so_luong/tong_hop_khoi_luong). **Bonus:** KHÔI PHỤC id84 DC=16 + cảnh báo SL-lệch DCN (6 vs 8) mà key bảo thủ đã mất. **Kết quả:** DM/DR/D2/DC = 20/30/30/16 · ĐC vẫn 59 · door D1 giữ ([E] 84.24 ổn định). Test **[id84]+6 ca dầm** → takeoff **258** · check.sh **[19/19]** · qa 129 · excel-content 17 · misc-tools 84 · 0 regress.

- **✅ VÁ id135 — REFUSE-GUARD chống bịa SỐ ĐO-LƯỜNG không nguồn (grounding), AN TOÀN recall [2026-07-13 phiên nối 6, ✅ LIVE `3ca5102`]:** chọn thiết kế qua workflow (design + false-positive-hunt trên battery THẬT + red-team). **KHÔNG dùng `n_evidence=0` thô** (probe: 60/198 câu ĐÚNG có n_ev=0 vì tool trả số tổng-hợp KHÔNG gắn handle — đếm đối tượng/bảng thép/min-max dim/mốc cao độ → guard thô = SẬP recall 30%). Tín hiệu ĐÚNG = **GROUNDING**: số ĐO-LƯỜNG trong câu trả lời có truy được về số nào tool ĐÃ trả trong RAW result không. **2 lớp** (`mcp_bridge.py`): (L2) `_guard_text` — gom `tool_numbers` từ mọi RAW result (`_collect_numbers`), trích số ĐO-LƯỜNG của answer (`_answer_numbers`: MIỄN số đếm trơn + mã-hiệu B20/M14/1÷200/AxB), CHỈ từ chối (thay bằng "Không có thông tin này trong bản vẽ.") khi MỌI số (đo-lường lẫn đếm) đều KHÔNG grounded (dung sai đơn vị ×1000/÷1000 + làm tròn 1%, khớp CÓ DẤU); (L1) luật SYSTEM_PROMPT cao độ/chiều sâu: chỉ nêu số nếu tool trả, không thì nói "không đọc được có căn cứ". **Vet red-team (đã chạy `_answer_numbers` trên cả 198 câu battery) → FP=0** (0 câu đúng bị từ chối nhầm); bắt đúng id135 "-10m" (−10 vắng khỏi mọi result). **⚠ GIỚI HẠN E2E:** KHÔNG chạy được câu id135 THẬT (file hạ tầng không có trong corpus + cần API) → xác minh bằng **mock-E2E qua tra_loi_ai + unit + phân tích battery**, KHÔNG phải E2E-thật. Rủi ro deploy thấp vì thứ được verify chính là AN-TOÀN-RECALL (câu đúng được bảo vệ). Test `test_grounding_guard.py` **32 ca** (8 unit + mock BAN/GIỮ) → check.sh **[18/18]→[19/19]** · takeoff 252 · qa 129 · 0 regress.

- **✅ VÁ FINDING id84 — đài cọc ĐC gộp nhầm dầm + đếm trùng (142→59) [2026-07-13 phiên nối, ⚠ CHƯA commit]:** chọn qua workflow đa-agent (research repro offline + decision matrix + vet overfit) — id84 là đầu mục DUY NHẤT vừa unblocked vừa repro được engine thật (id135 BLOCKED: thiếu file hạ tầng trong corpus; F-B cần user quyết; GĐ4/P5 chặn corpus). **Repro:** `tong_so_luong(loc='ĐC')` trên `2. KetCau CT-A.dxf` = **142** (đúng 59). **4 root-cause** (`tools_core.py`): RC1 `unaccent` gộp đ→d nên 'ĐC'(đài) ≡ 'DC'(dầm) ở khớp mã (query 'ĐC'/'DC' GIỐNG HỆT); RC2 `_tok_bound` token chữ = substring ('dc'⊂'dcn'); RC3 dedup theo `(label_norm,so_luong)` không gộp inline vs spatial → 'ĐC-3' 2 lần; RC4 `tong_so_luong` `cs[-1]` nhặt nhầm annotation 'sl-25'. **Vá CẤU TRÚC:** (a) khớp qty trên field mới `label_ma`=`_norm_ma(nhãn)` (GIỮ đ/d: 'ĐC'→'djc' ≠ 'DC'→'dc') → đài cọc KHÔNG hút dầm; (b) `_ma_key` BẢO THỦ (bỏ annotation SL/L=/ngoặc rồi so NHÃN) — gộp inline/spatial cùng nhãn ('ĐC-3 (SL-25)'='ĐC-3') NHƯNG KHÔNG over-merge 2 loại cùng mã trần ('DẦM D1'≠'CỬA D1'); (c) xung đột SL 2 nguồn (DCN inline=6 vs spatial=8) → chọn inline + LỘ `canh_bao`+⚠ ở output, KHÔNG cộng dồn (THẤT BẠI PHẢI LỘ). Dedup `_ma_key` áp cả `tong_so_luong`/`tong_hop_khoi_luong` (Excel hết 'ĐC-3' 2 dòng). **Vet overfit (adversarial) bắt 3 lỗi TRƯỚC code** (TYPE_WORDS chưa qua _norm_ma → đổi sang key bảo thủ; fail-loud chưa ra output → đã wire; over-merge door/beam → phát hiện qua regress [E] tự vá). **Kết quả:** ĐC=**59**/6 mã · DC(dầm)=chỉ dầm · door/beam D1 GIỮ NGUYÊN (test [E] ổn định 84.24). Test **[id84] 12 ca** → takeoff **252/252** · check.sh **[18/18]** · qa 129 · 0 regress. **✅ COMMIT `c0b85af` + push + deploy + verify LIVE** (`/version`=c0b85af khớp + `/health` ok).

- **✅ KIỂM THỬ GĐ3 (E2E-AI, Gemini 2.5-flash thật) + vá bug empty-response — LIVE [2026-07-13 phiên nối, commit `7e9335e`]:** smoke `kichban_gd2` 10/10 vs engine-truth (0 bịa). **Full battery 198 câu:** DAT+PHAN 132 (67%) · SAI 49 (đa số "đọc thiếu"=recall miss, AN TOÀN) · RỖNG 17 · judge-panel (12 agent Claude, khác nhà-model) chấm. **Bug tìm+vá:** 17 câu (8.6%) trả "AI không đưa ra nội dung" vì Gemini trả part 'thought' RỖNG lượt đầu → `tra_loi_ai` bỏ cuộc ngay; vá NHẮC-1-lần (mcp_bridge.py ~409) → 8/8 câu cứng đầu hồi phục, test `[H.10]`. **KPI bịa THỰC (tự xác minh, không tin judge): ~1.1% bịa CỨNG** (không phải 3.9% judge thô — id17 '100m' thực có ở bảng thép = false-positive; ước-lượng-có-cờ ≠ bịa). Demo RẤT chắc anti-bịa (nghiêng từ chối).
- **⏳ FINDING:** ~~**id84** — đài cọc 142 vs 59~~ ✅ VÁ LIVE `c0b85af`. **id135** — cao độ sâu nhất "-10m" (đúng ~-14.26): ✅ **REFUSE-GUARD (grounding) ĐÃ VÁ** [phiên nối 6, xem entry trên] — chặn bịa số đo-lường không nguồn, an toàn recall (FP=0). **id135 ĐÃ HOÀN THIỆN 2 lớp:** (guard chặn bịa `3ca5102`) + (recall-tool `cao_do_min_max` phiên nối 8 — đọc ĐÚNG cao độ min/max kèm handle, đã verify -14.26 shape). **CÒN:** E2E-thật id135 trên file hạ tầng thật (thiếu corpus + cần API) — chờ đối tác cấp file để chốt. **Design tension:** tính-năng ước-1-tầng ("GIẢ ĐỊNH") kích trên câu-bẫy "chiều cao công trình/cao độ tầng" — nên TỪ CHỐI hẳn thay ước. **Recall gaps:** nhiều câu "đọc thiếu" (từ chối dù có info) — an toàn nhưng giảm hữu dụng.
- **✅ KIỂM THỬ GĐ0-2 (offline) + vá R11(IDOR)+F-A(race) — LIVE [commit `5b13ba0`]:** (giữ nguyên; chi tiết ở entry cũ).

- **✅ KIỂM THỬ GĐ0-2 (offline, 0 phí) + vá 2 bug hạ tầng — LIVE [2026-07-13 phiên nối, commit `5b13ba0`]:** đóng vai TESTER, rà toàn dự án qua workflow (bản-đồ-độ-phủ + benchmark-infra + corpus-mở + bề-mặt-E2E) → kế hoạch v2 (phản biện 4-góc bắt 2 lỗi CODE). **GĐ1-2:** +**212 ca / 8 file test mới** (visual-highlight 15 · excel-content 17 · misc-tools 84 · vntext 28 · fuzz 36 · dwgconv 10 · **MCP-stdio thật 14** [spawn mcp_server + JSON-RPC, wiring hoclog redact, số học không lọt tổng qua transport] · app-routes 8) → check.sh mở [10/10]→**[18/18]**. **Vá R11 (IDOR):** `s["artifacts"]`+`_artifact_owned` — `/file` `/image` cross-session → 404 (test `[K.7]`). **Vá F-A (race):** `_try_close_session` acquire-non-blocking né phiên đang bận — LRU/TTL không đóng subprocess GIỮA request (test `[K.8]`). **0 bug SẢN PHẨM** (lõi đọc-số cứng từ P1-P4; 2 bug đã vá ở tầng session/route). Fixtures VN chỉ 1-domain → overfit vẫn chưa test được (cần bản vẽ ≥3 firm).
- **⏳ CHỜ user:** **F-B** — `hoc_quy_uoc`/`thu_hoi` KHÔNG có route app.py + loại khỏi Gemini (R8) → kênh học P3 CHỈ dùng qua MCP-client, web-demo KHÔNG dạy được (quyết: nối UI web hay giữ MCP-only). **GĐ3 (E2E-AI full battery 198)** cần GEMINI_API_KEY riêng. **GĐ4** cần bản vẽ VN ≥3 firm (budget không mua được). Thu hồi dữ liệu test = GĐ5.
- **✅ P-1.1 + P3 + P4 — LIVE [commit `e9c4f80`]:** (giữ nguyên, không đụng khi kiểm thử).

- **✅ P4 RÀO TỔNG/EXCEL — LIVE [2026-07-13 phiên nối, commit `e9c4f80`]:** `tong_hop_khoi_luong`/`xuat_excel` (tools_core.py ~2156-2290): (1) **fail-closed guard** `learned_handles` = loại MỌI row có handle∈quy-ước-học (learned-anchor vốn residual → no-op bình thường, nhưng BIẾN bất biến "learned không vào tổng" thành RÀNG-BUỘC-CODE, chống future-bug/P5); (2) **cột `chua_chac`** per-row (TẠM TÍNH/suy đoán/thiếu SL/chưa rõ, quét cả hang_muc); (3) **`quy_uoc_chua_xac_nhan`** = list quy ước học (re-parse tươi) LỘ cho đối tác thấy 'đã dạy X' NHƯNG KHÔNG cộng vào tổng — khối riêng trong Excel (8 cột +'Chưa chắc'). Adversarial review 1-agent (tự-repro): AN TOÀN (không rò số học vào tổng, không crash/regression), vá 1 LOW (keyword 'suy đoán' chết → quét hang_muc). Test P4 4 ca → takeoff **240/240**, check.sh [10/10], qa 129/129. **✅ push+deploy+verify LIVE** (`/version` = `e9c4f80` khớp + `/health` ok). Số học nay có 3 lớp chặn: §2.6 backstop (P3) → fail-closed guard (P4) → không-đọc-hoc_phien (cấu trúc).
- **✅ P-1.1 (vá R1) + P3 MỞ KÊNH HỌC — LIVE [2026-07-13 phiên nối, commit `6933643`]:** CODE + test + red-team 2 vòng, **push+deploy+verify LIVE** (`/version` = `6933643` khớp + `/health` ok).
  - **P-1.1 (vá R1, lỗ E2 ĐANG TỒN TẠI):** `tinh_dai_luong` ([tools_core.py] ~1871-1920) — input `chua_chac` nguồn ≠ `gan_vi_tri` (E2 xác-nhận-handle) bị `ghi_chu` dán "đọc trực tiếp từ file (đáng tin)" mà `ghi_chu` là thứ Gemini thuật. Vá: `_gan_cc` gắn cờ MÁY-ĐỌC `resp['chua_chac']`/`can_doi_chieu` ở MỌI đường-ra (kể cả nhánh lỗi trình `gross`); nhánh ghi_chu chỉ nói 'đáng tin' khi KHÔNG có input chua_chac. Test `[Z0]` 3 ca (fix + positive-control + nhánh-lỗi).
  - **P3 (Lát 1-4):** `hoc_quy_uoc`/`thu_hoi_quy_uoc` (MCP tool #24-25) — đối tác dạy "đọc HANDLE THẬT này như <template> cho mã X". ENUM `_TEMPLATE_ENUM` {KG_PER_UNIT, KICH_THUOC_MM}, học CÁCH ĐỌC theo PHIÊN, **KHÔNG lưu số** (re-parse tươi). Cổng fail-closed: template∈ENUM · anchor∈residual · KHÔNG ô-thép · NGỮ CẢNH anchor chứa MỌI token mã · không chỉ-thị · token-nguyên-vẹn + biên. **§2.6 BACKSTOP** (tools_core `co_hoc`): input học → `co_ket_qua=False` + `uoc_luong_hoc`, **KHÔNG BAO GIỜ số chốt / KHÔNG vào tổng-Excel** (P3 giao TRƯỚC P4 nên tự chặn). LLM KHÔNG gọi tool ghi (`gemini_tools` loại; luật 17). `content_hash` (định danh theo bytes). Log WORM wiring.
  - **RED-TEAM THIẾT KẾ (119 agent):** 36→24 finding sống sót; phán quyết CONDITIONAL GO (Lát 0 backstop chặn-ship); doc `KET_QUA_REDTEAM_P3.md`.
  - **RED-TEAM IMPLEMENTATION (19 agent, tự-repro engine THẬT):** INV-A/B/C/D lõi KHÔNG phá được (số học không vào bàn giao/không mutate/cô lập/backstop vững). Vá 5 bug chất-lượng-cổng INV-E: **F1** regex token dính chữ ('B25'→25mm) + **F2** đơn vị cm/m (250cm→250mm 10×) + **F3** Đ↔D chéo-mã (unaccent gộp; thêm `_norm_ma` giữ đ/d) + **F4** đa-token any→all + **F5** copy `la_hoc` xuống da_co (backstop 2 lớp). Test `[Z13-16]`.
  - **Test:** takeoff **236/236** (nhóm `[Z]` 20 ca P3 + `[Z0]` 3 ca R1) · `test_hoc_quy_uoc.py` **2** (INV-10 LLM-exclusion + INV-12 grep-guard tokenize) · check.sh **[10/10] PASS** · qa **129/129**. **⚠ CHƯA push/deploy — chờ user chốt commit cả cụm.**

- **✅ CHỐT SỔ 2026-07-13:** clean-state **0 FAIL** — takeoff **214/214** (nhóm A-Y) · qa **129/129** · `check.sh` **PASS [9/9]** (23 tool · no-key · +hoc_log 20) · working tree TRACKED sạch, push hết. Phiên: **KHỞI ĐỘNG vòng AI TỰ HỌC** = Kế hoạch chi tiết (workflow 17-agent) + **P-1** (vá 6 lỗ E1-E6, LIVE `5ecaca1`) + **P0-P1** (classifier ①②③ đọc-thuần, LIVE `015161e`) + **P2** (log WORM, LIVE `b94da21`) — 6 commit code + docs, ĐỀU deploy+verify LIVE. Tất cả **ĐỌC-THUẦN (chưa học gì)**. Tiếp: **P3 mở kênh học (rủi ro CAO NHẤT)**. KHÔNG pytest (crash `I/O closed file`); KHÔNG specs/ (dùng feature_list.json).
- **✅ AI TỰ HỌC P2 — LOG WORM append-only (ĐỌC-THUẦN) [2026-07-13, commit `787b1e6`]:** cổng-4 nhật ký cho DEV rà "chỗ bí". `hoclog.py` CHỈ GHI (mode `'a'`, redact file_hash, best-effort, cap+xoay `.1`, tắt bằng `HOC_LOG=0`); wiring ở TOOL LAYER (`mcp_server` `hoi_de_hoc`/`doi_chieu_nghi_ngo`) → core `tools_core` giữ THUẦN. **BẤT BIẾN sống còn:** log KHÔNG hồi-tiếp inference (chống warm-start = đầu-độc chéo phiên) — khoá bằng **grep-guard** (đếm-`open()`==1 + GLOB mọi `*.py`). Adversarial review: 0 CONFIRMED cao/TB; vá 2 thap (rotation/cap + guard porous). Test `test_hoc_log.py` **20 ca** → check.sh **[9/9] PASS**, takeoff 214/214 không regression. **✅ push+deploy+verify LIVE** (HEAD `b94da21`). Tiếp: **P3 mở kênh học (rủi ro cao nhất)**.
- **✅ AI TỰ HỌC P0-P1 (ĐỌC-THUẦN) [2026-07-12(d), commit `6608edf`]:** phần read-only của vòng học (KHÔNG học/KHÔNG mutate). **P0:** `used_handles` (gom handle 8 index + text cao độ) + `_residual_texts()` (phép bù) + `hoc_phien=[]`. **P1:** `phan_loai_tin_hieu(ma)`→① (residual cấu-trúc gần mã: HỎI-ĐỂ-HỌC, phơi nguyên văn+handle, KHÔNG bịa) /② ; `doi_chieu_nghi_ngo(ma)`→③ (đa tiết diện/đơn vị/cửa chưa chắc, không tự chọn bên). 2 MCP tool `hoi_de_hoc`/`doi_chieu_nghi_ngo` (23 tool) + luật 16 SYSTEM_PROMPT. **Red-team đa-fixture bắt CLASSIFIER NGẬP NHIỄU 99%** (ký hiệu thép/mác chuẩn coi 'mã lạ'; 9T KC D3=96 ứng viên) → VÁ `_la_notation_chuan` + branch-order + dedupe → **9T KC 336→2** (còn nhãn lạ THẬT 'THÉP CHỜ V-1'). Test **[Y] 11 ca** → takeoff **214/214**. **✅ push+deploy+verify LIVE** (HEAD `015161e`, `/version`+`/health` ok). Tiếp: P2 (log WORM) → P3 (mở kênh học, rủi ro cao) → P4/P5.

- **✅ CHỐT SỔ 2026-07-12:** clean-state **0 FAIL** — takeoff **191/191** · qa **129/129** · `check.sh` **PASS [8/8]** (21 tool · no-key · +5 test robustness) · working tree TRACKED sạch, push hết, HEAD `301ccdd` LIVE (`/version`+`/health`). Phiên: Củng cố **A–G** + Residual G + Robustness **H–L** + Audit an toàn đa-agent (**8 commit** đều deploy LIVE). (Dùng SCRIPT runner, KHÔNG pytest.) feature_list: 28 done / dự toán chi phí deferred / AI tự học planned.
- **✅ AUDIT AN TOÀN ĐA-AGENT + VÁ 9 LỖ [2026-07-12]:** workflow 27-agent (7 audit song song mọi nhóm tool → 19 skeptic-verify → 10 confirmed) + TỰ tái hiện toàn bộ. Vá 9 lỗ chống-bịa/crash/mislabel (`tools_core.py`): **H1** `_to_num_vn` số VN '.'=nghìn (nhãn '1.130 m2' 9T KT: 1.13→**1130**, lệch 1000×); **H2** tong_phu KHÔNG gộp m³ ghi sẵn dị-loại (thêm 'Khối lượng (ghi sẵn)' vào `_khong_cong` — đúng lớp bug G); **M3** coerce JSON non-dict (chống crash); **M4** `tra_cuu_so_luong` không gán TỔNG(131) cho mã lẻ (cờ `is_total`); **M5** `tong_so_luong` tong=None khi không lọc; **M6** `liet_ke_so_luong` lọc trượt LỘ so_muc=0; **M7** `liet_ke_chu_theo_layer` khớp CHÍNH XÁC layer; **M8** 'ván khuôn móng'→fail-closed None; **M9** `thong_tin_kich_thuoc` lộ đơn vị chưa-chắc ($INSUNITS). Bề mặt an toàn xác nhận vững. Test **[W] 14 ca** → takeoff **191/191** + qa 129/129 + check.sh [8/8]. ⚠ CHƯA commit.
- **✅ ROBUSTNESS L — KEEP-ALIVE + GIÁM SÁT [2026-07-11(g)]:** `app.py` `/health` JSON NHẸ (no API/no bản vẽ: `{ok,uptime_s,sessions,use_ai,model,metrics}`) cho Render `healthCheckPath` + monitor ngoài; `_METRICS` (uploads/asks/errors) tăng ở upload/ask. Self-ping `_keepalive_ping()` GET `RENDER_EXTERNAL_URL/health` (traffic ngoài → Render không ngủ), nuốt lỗi; `_keepalive_loop` mỗi `KEEPALIVE_MIN`(10'); `_start_keepalive()` CHỈ chạy khi có URL (production; local/test KHÔNG kích). `render.yaml healthCheckPath` → `/health`. Test `test_health.py` **11/11** + `check.sh` [8/8]. Deploy: self-ping tự chạy (RENDER_EXTERNAL_URL), tắt bằng `KEEPALIVE_MIN=0`. ⚠ CHƯA commit.
- **✅ ROBUSTNESS K — TÁCH STATE THEO SESSION [2026-07-11(f)]:** hết cảnh "người B upload xoá bản vẽ+lịch sử người A". `app.py` (chỉ file này): `SESSIONS` dict theo cookie `sid` — mỗi phiên có bridge (1 MCP subprocess/1 Drawing) + summary + history + lock RIÊNG. `get_session()` sweep TTL + enforce CAP (`MAX_SESSIONS`=4, đầy→đóng LRU) ; `SESSION_TTL_MIN`=30 đóng phiên nhàn rỗi (giải phóng subprocess); bridge tạo LƯỜI ở /upload. `@app.after_request` set cookie. `_make_bridge()` tách để test mock. Không đụng mcp_server/tools/anti-bịa. Test `test_session.py` **17/17** (Flask test_client + FakeBridge, không subprocess/không API) + `check.sh` [7/7]. Deploy: chỉnh `MAX_SESSIONS` theo RAM. ⚠ CHƯA commit.
- **✅ ROBUSTNESS J — DỌN FILE TTL [2026-07-11(e)]:** `fileutil.py` mới — `cleanup_old_files(dirs, ttl_min, keep=None)` (nhẹ, import chéo web+subprocess không kéo ezdxf; xoá file mtime>TTL, chỉ FILE không đệ quy, keep giữ file vừa tạo, ttl<=0=tắt, nuốt lỗi I/O). `FILE_TTL_MIN` env (60') ở app.py + tools_core. Dọn OPPORTUNISTIC: mỗi upload dọn `_uploads`+`_renders`; sau mỗi render_region/xuat_excel dọn `_renders` (keep file mới). File active của phiên đều mtime-mới → không bị dọn; query/render dùng RAM (self.doc) → xoá đĩa không vỡ phiên. Test `test_file_ttl.py` **12/12** + `check.sh` [6/6]. ⚠ CHƯA commit.
- **✅ ROBUSTNESS I — CHẶN FILE LỚN SỚM [2026-07-11(d)]:** `tools_core.Drawing.__init__` kiểm `raw_mb > READFILE_MAX_MB` **TRƯỚC** `convert_dwg_to_dxf` (DWG lớn → DXF chắc ≥ DWG → loại NGAY, khỏi ODA ~600s) + giữ check sau-convert cho DWG nén phình. `app.py` thêm hằng `READFILE_MAX_MB` (khớp env), upload check `getsize` **sau save, trước MCP** → **413** + `os.remove` (dọn file, bắc cầu J). Không đổi ngưỡng → không false-reject file hợp lệ. Test `test_size_guard.py` **9/9** (offline: chặn trước parse, DXF hợp lệ vẫn chặn, dưới ngưỡng nạp được, app 413+dọn file qua Flask test_client) + `check.sh` [5/5]. ⚠ CHƯA commit.
- **✅ ROBUSTNESS H — MODEL FALLBACK 429/503 [2026-07-11(c)]:** `mcp_bridge.py` chuỗi `MODELS`=[gemini-2.5→2.0→1.5-flash] (env `GEMINI_FALLBACK_MODELS`, rỗng→hành vi cũ 1 model). `_is_overloaded` (429/5xx + chuỗi quota/unavailable) + `_gen_fallback(client,contents,cfg,state)` nhảy model kế khi 429/503 SAU SDK-retry (fail-forward, `state['i']` giữ model đang dùng qua các lượt trong 1 request). Cắm cả 2 chỗ gọi generate_content; hết chuỗi ở vòng tool → trả LỘ "AI đang quá tải, thử lại sau" (không crash/bịa); lỗi khác (safety/400/404) → ném ngay. `app.py /version` thêm `models`. Test `test_model_fallback.py` **20/20** (offline MOCK, không tốn API) + `check.sh` [4/4] PASS + takeoff 177/qa 129 không regression. ⚠ CHƯA commit — chờ user.
- **✅ RESIDUAL G [2026-07-11(b)]:** **#1 đọc SL BẢNG THỐNG KÊ theo cột TỔNG** — `_build_schedule_qty_index` (`tools_core.py`) ghép mã↔số theo hàng(y-band)+cột('TỔNG'), gated fail-silent (≥5 cặp duy nhất, |Δy| chặt, mã sát trái cột tổng; block không sạch→bỏ). Merge vào `qty_index` (nguồn 'bảng thống kê (cột TỔNG)'+handle). 9T KT: liet_ke_so_luong 6→28 mục (d2=9,d3=20,d10=18,d4=11,sk2=16…). Validate ÂM KC/KT CT-A+CT-K=0 bịa (port giữ nguyên). **#2 cờ suy_doan_don_vi cạnh <40 → BY-DESIGN, no-fix** (mm-interp <4cm phi thực → không nhập nhằng; nới cờ sẽ ngập false-alarm). Test **[V] 10 ca** → **177/177** + qa **129/129** + check.sh PASS. ⚠ CHƯA commit — chờ user.
- **✅ TASK G — TEST ĐỐI KHÁNG ĐA-DOMAIN + VÁ 3 BUG [2026-07-11]:** workflow probe 6-agent (KC/KT 9T + CT-K + gap-check + overfit-hunter) chạy engine thật → TỰ KIỂM CHỨNG (repro độc lập) 3 bug tầng tổng hợp/đọc: **(A cao, LIVE)** `tong_phu` gộp thép tròn+hình thành 1 số kg (KC 67759.7, KT 4110.7) — vi phạm rule 8b (mcp_bridge:164), mâu thuẫn code-vs-policy; **(C)** gộp 'Số lượng' dị loại → 835/191 vô nghĩa; **(B latent)** `_rs_dien_tich_ghi_san` regex thô đọc mật độ '16 cọc/1m2'=diện tích 1 (parity gap; live-scan 0/4 file). VÁ `tools_core.py`: tách loai thép tròn/hình + 'Số lượng'∈`_khong_cong` + resolver dùng `_STATED_M2_RE` (lookbehind). Test **[R][S][T][U] + I.5/I.6** (9T KC F ước 10 tầng=21.12 + C999 vàng; 9T KT 193k obj recall 16 nhãn đủ handle). Hoist 9T KC nạp 1 lần (trước 2 lần). **takeoff 167/167 (was 149) · qa 129/129 · check.sh PASS.** ⚠ CHƯA commit — chờ user.
- **✅ CHỐT SỔ 2026-07-10:** clean-state PASS — takeoff **149/149** · data **129/129** · `check.sh` PASS · 21 MCP tool · no-key · working tree TRACKED sạch, push hết, HEAD `a775825` LIVE (verify `/version`). Củng cố **A–F XONG**; còn G + robustness H–L. (Dùng SCRIPT runner, KHÔNG pytest.)
- **✅ TASK F — ƯỚC CHIỀU CAO CỘT theo cao độ [2026-07-10]:** `_rs_chieu_cao_cot` ước = `typical_floor_h`×1000mm khi đối tác không cấp (cờ `gia_dinh_cao_tang` + nguon `suy_tu_cao_do` + `chua_chac`); `_la_cot` (nhãn thắng prefix) chặn không-cột. **MÓNG resolver RIÊNG `_rs_chieu_cao_mong`** (luôn hỏi — hàng rào tất định ở tầng `_FORMULAS`). ghi_chu tách 'GIẢ ĐỊNH 1 tầng' khỏi 'GÁN VỊ TRÍ'. Không levels → hỏi (không bịa). ⚠ ĐỔI HÀNH VI: cập nhật test B (C1 chưa cấp cao → nay tính được) + P.3 (D↔F). Kiểm chứng đối kháng 29 probe = **0 lỗ** (F1-F7). Test **[Q] 14 ca** (149/149). ⚠ CHƯA commit — chờ user.

- **✅ TASK D — ỨNG VIÊN GỢI Ý cho input thiếu (1-click) [2026-07-10]:** `tinh_dai_luong` gắn `ung_vien` vào từng `inputs_thieu[i]` (additive). `_ung_vien_kg_moi_bo` (quét 'X kg', loại 'TỔNG', cờ per-unit `_KG_PU_RE` bền garble bộ→bé; GT inox 8.62 [67FFC]) + `_ung_vien_dim` (dim gần mã, đòi mã, loại 0.0, 'thap'+khoảng cách). Dispatch theo RESOLVER (không theo 'ten'): `chieu_cao` cột (`_rs_chieu_cao_cot`=cao độ) KHÔNG gợi vs tường (`_rs_bs_only`) gợi được; so_mat KHÔNG gợi. CHỐNG BỊA: ứng viên KHÔNG tự cắm (không vào vals/da_co, co_ket_qua giữ False), chỉ `inputs_bo_sung` mới tính; kg KHÔNG khẳng định thuộc mã. Kiểm chứng đối kháng 27 probe = **0 lỗ**. Test **[P] 14 ca** (134/134). ⚠ CHƯA commit — chờ user.

- **✅ TASK C — LIỆT KÊ DIỆN TÍCH GHI SẴN [2026-07-10]:** MCP tool `liet_ke_dien_tich_ghi_san` (#21) + `_build_stated_areas`/`self.stated_area` (mirror `stated_vol`). Đọc mọi nhãn 'X m²' NGUYÊN VĂN + handle + layer + cờ `co_tu_khoa_dien_tich`. CHỐNG BỊA/MISLABEL: KHÔNG khẳng định 'diện tích sàn', KHÔNG suy hình học (0 nhãn → gợi ý đối tác CẤP), KHÔNG cộng gộp (`tong_hop` loại 'Diện tích (ghi sẵn)' ∈ `_khong_cong`). Lọc mật độ + đuôi thập phân (regex `(?<![/.,\d])` + normalize `'/\s+'→'/'`). PROBE file thật trước (nhãn hỗn tạp → chốt không phân loại). Kiểm chứng đối kháng 2 vòng (vá bịa-đuôi-thập-phân + density-space; DROP-class còn lại đã ghi chú giới hạn). Test **[O] 15 ca** (`test_takeoff_chong_bia.py` **120/120**). ⚠ CHƯA commit — chờ user.
- **✅ TASK B — TRỪ LỖ cửa/cửa sổ (xây tường & trát) [2026-07-10]:** `xay_tuong`/`dien_tich_trat` nhận `lo_cua` (list) trong `inputs_bo_sung` — mỗi lỗ `{ma,sl}` (tra `door_size_index` confident, có handle) HOẶC `{rong,cao,sl}` (mm). net = gross − Σ(R×C×SL)×(be_day|so_mat). SL do ĐỐI TÁC khai (mirror inox — KHÔNG tự đoán cửa nào thuộc tường nào). Backward-compat: không `lo_cua` → số cũ y hệt. Kiểm chứng đối kháng 2 vòng (loop-until-dry): vòng 1 bắt 4 bug thật → vá (over-count cộng dồn per-code; net<=0 SAU làm tròn; block `sl`≠`so_luong`; trần SL 100000); vòng 2 DRY. Code: `_resolve_lo_cua`/`_sl_hop_le`/`tinh_dai_luong` (`tools_core.py`) + docstring `mcp_server.py` + SYSTEM_PROMPT `mcp_bridge.py`. Test **[N] 27 ca** (`test_takeoff_chong_bia.py` 103/103). ⚠ CHƯA commit — chờ user duyệt.
- **QUYẾT ĐỊNH CHIẾN LƯỢC:** đối tác test 2 demo → ưng demo 2. Rà soát: khác biệt tốc độ do MODEL (demo 1 pro vs demo 2 flash), không phải kiến trúc; "thất bại" demo 2 (inox/diện tích sàn) là giới hạn CHUNG/chống-bịa. → **Chốt demo 2 là sản phẩm chính, DỪNG demo 1.** Nguyên tắc "2 demo cân bằng" NGHỈ.
- **VÁ PARITY cm/mm + đọc bảng cột nhà 9T** (`_build_section_index` ghép tọa độ + ngưỡng 130 + cờ mơ hồ): 9T C-3 = 80×80cm → **23.04 m³ KHỚP demo 1**; CT-A mm 4.704 m³ không đổi. Commit `2a90a36`.
- **Endpoint `/version`** (RENDER_GIT_COMMIT + sect_cm_max + has_section_index) — verify deploy qua HTTP. Commit `e870074`.
- **Tính năng INOX = SL(đọc) × kg/bộ(đối tác cấp)** (feedback đối tác): inox S1 = 16×8.62 = **137.92 kg**. Commit `c034312`.
- **Kiểm chứng ĐỐI KHÁNG (workflow đa-agent) → hardening:** bắt lỗ `inf`/tràn số (16×1e308)/`bool` lọt cổng ra "Infinity kg" → vá `_nd` từ chối bool/inf/nan + cổng `math.isfinite` + kiểm KẾT QUẢ hữu hạn. Commit `c034312`.
- **Vá 3 lỗ BỊA SỐ** (workflow roadmap chạy code phát hiện): mã toàn chữ "GHOSTINOX"; "thể tích sàn" mã trống tự vơ diện tích; "thể tích inox" lệch đại lượng. Commit `4c597f3`.
- **Củng cố A + E:** tổng phụ theo (loại,đơn vị) trong tổng hợp+Excel; gợi ý m³ ghi sẵn (đào đất thiếu số → nêu "ĐÀO MÓNG 860 M3" [handle]). Commit `dd8d971`.
- **Tài liệu chiến lược:** ROADMAP_DEMO2 (hoãn dự toán chi phí, `fe4972c`), KE_HOACH_TONG_QUAT_HOA (độ phủ vs độ an toàn, KPI 0% bịa, `dd8d971`), NGHIEN_CUU_AI_TU_HOC (tự học an toàn, `2f51a8b`).
- **TÍCH HỢP HARNESS:** tạo `harness/` (12 file) — project-overview, tech-stack, feature_list.json (27 đầu mục), AGENTS.md, rubric, quality-document, clean-state-checklist, session-handoff, **claude-progress.md** (nhật ký phiên), README, benchmark_questions, scripts/check.sh. `check.sh` = **HARNESS GATE: PASS** (import + 20 tool + no-key + 76/76). Commit `de61ac5` (+ chốt sổ phiên cuối).
- **Test (chốt sổ 2026-07-09):** `test_takeoff_chong_bia.py` **76/76** (nhóm A-M) + đọc **129/129** + `check.sh` PASS. Deploy live + `/version` verify mỗi commit. Working tree sạch.
- **⚠ Lưu ý cấu trúc:** demo 2 KHÔNG có `specs/specs.json` (theo quy ước Harness đã ghi ở `AGENTS.md`) — `feature_list.json` thay cho specs/. Rà trạng thái tính năng ở `feature_list.json`, KHÔNG tìm specs/.

## Còn lại / Bước tiếp (xem `PHUONG_AN_NANG_CAP_DU_AN.md` U1-U6 + `feature_list.json` + `ROADMAP_DEMO2.md`)
- **📌 3 MỤC "CÒN LẠI" NAY GỘP VÀO `PHUONG_AN_NANG_CAP_DU_AN.md` (khỏi kê trùng):**
  - **OLE lồng trong định-nghĩa-BLOCK** (F2 latent — ezdxf không mở INSERT; chưa quét vì rủi ro đếm nhầm khung-tên) → **U3** (đọc bảng OLE nhúng, 3 tầng: binary OLE2FRAME → OCR → HITL).
  - **Chịu tải RAM / OOM** (ngưỡng 45MB Free lỏng ở file đặc + `MAX_SESSIONS=4` × Drawing; đo lại Linux khi bật billing; HELD `held-ram-config` chờ) → **U6** (iterdxf streaming + lọc layer rác — nền gỡ quyết định RAM HELD).
  - **P5 codify quy ước học** (đủ điều kiện ≥3 firm nay đã có corpus; feature AI-tự-học đã P-1→P4 LIVE, P5 là bước cuối) → **U1** (quy ước động + popup xác nhận web, gộp P3 LIVE + F-B). ⚠ P5/U1 vẫn cần red-team mạnh trước khi mở (rủi ro cao nhất vòng học).
  - Thứ tự đề xuất trong phương án: **U3-probe (19 file OLE, ~30' offline) → I-items nền chống-bịa → U6**. id135 E2E-thật vẫn chờ file hạ tầng mốc sâu (U5 corpus).
- **Củng cố treo:** ~~B (trừ lỗ cửa)~~ ✓ · ~~C (liệt kê diện tích ghi sẵn)~~ ✓ · ~~D (ứng viên kg/bộ 1-click)~~ ✓ · ~~E (gợi ý m³ ghi sẵn)~~ ✓ · ~~F (ước cao cột theo cao độ)~~ ✓ · ~~G (test đối kháng đa-domain)~~ ✓ [2026-07-11, +vá 3 bug tong_phu/diện tích] — **A–G XONG**; còn robustness H/I/J/K/L.
- **Residual G:** ~~recall SL 9T KT~~ ✓ [2026-07-11(b): đọc bảng thống kê cột TỔNG, gated fail-silent, test [V]] · ~~cờ suy_doan_don_vi cạnh <40~~ ✓ (nghiên cứu → BY-DESIGN, no-fix) — **XONG**. Còn: window S-code |Δy| lỏng hơn → nên đối chiếu thêm bản vẽ KHÁC layout trước khi tin tuyệt đối; (concurrency thuộc robustness K).
- **Robustness H–L HOÀN TẤT:** ~~H (model fallback)~~ ✓ [(c) 20/20] · ~~I (chặn file lớn sớm)~~ ✓ [(d) 9/9] · ~~J (dọn file TTL)~~ ✓ [(e) 12/12] · ~~K (tách session)~~ ✓ [(f) 17/17] · ~~L (keep-alive+giám sát)~~ ✓ [(g): /health + self-ping RENDER_EXTERNAL_URL + metrics, test 11/11].
- **Đề xuất trước khi giao rộng:** ~~audit an toàn đa-agent trên MỌI tool~~ ✓ [2026-07-12, vá 9 lỗ, test [W]]; còn: xin 3-5 bản vẽ đơn vị thiết kế khác layout (củng cố đọc bảng thống kê + VN-thousands đa-file) + dựng KPI "tỷ lệ bịa".
- **✅ P-1 TRIỂN KHAI — vá 6 lỗ tồn tại E1-E6 [2026-07-12(c)]:** nền cho AI tự học (tính năng tự học sẽ khuếch đại lỗ nếu không vá). **E1** neo+lọc-bán-kính `_KG_UV_R` (note xa mã → LỘ 'thap'+khoảng cách, không im lặng); **E2** `_xac_nhan_ung_vien_theo_handle` giữ provenance (chua_chac/handle/can_doi_chieu; handle bịa→từ chối; không khớp→fall-through đọc file); **E3** `_rs_so_luong` đối chiếu file→`nghi_ngo` khi lệch (số dùng đối tác); **E4** SYSTEM_PROMPT rule 15 + `_co_chi_thi_dang_ngo` (advisory, thu hẹp chống false-positive); **E5** runner đếm SKIP+CANH BAO; **E6** upload uuid_basename + cookie Secure gate-env. Workflow spec + **red-team đối kháng diff** (4 CONFIRMED đã vá; XÁC NHẬN không rò P4 + backward-compat). Test **[X] 12 ca** → takeoff **203/203** + qa 129/129 + check.sh [8/8]. Commit `73990de`(code)+`5ecaca1`(doc), **push+deploy+verify LIVE** (HEAD `5ecaca1`, `/version` commit khớp + `/health` ok). Tiếp: P0→P1 (đọc-thuần) làm được; P5 chặn tới khi có corpus ≥3 firm.
- **AI tự học — KẾ HOẠCH CHI TIẾT xong [2026-07-12(b), planning KHÔNG code]:** `KE_HOACH_AI_TU_HOC_CHI_TIET.md` (bản kỹ thuật của NGHIEN_CUU_AI_TU_HOC.md). Workflow 17-agent (design-panel + red-team) → kiến trúc **eng-minimal + grafts safety-first**, neo code thật. **Đã TỰ tái hiện 6 lỗ ĐANG TỒN TẠI** (E1 `_ung_vien_kg_moi_bo` quét cả file 1168-1191; E2 xác-nhận-ứng-viên qua `_nd` mất provenance 512/1442; E3 `_rs_*` short-circuit bs đè số-đọc 1258; E4 SYSTEM_PROMPT 0 dòng chống-injection; E5 test silent-skip + 0 fixture commit; E6 basename đè file). Lộ trình **P-1 (vá E1-E6, giá trị độc lập) → P0..P5**. **Mở P5 (codify) CHẶN** tới khi có corpus ≥3 firm. Trạng thái vẫn `planned`, CHƯA code. ⚠ CHƯA commit doc — chờ user.

## Quyết định đã chốt (chống lật lại)
- **Demo 2 = sản phẩm chính, DỪNG demo 1.** "2 demo cân bằng" nghỉ.
- **Phạm vi = ĐỌC + tính KHỐI LƯỢNG.** DỰ TOÁN CHI PHÍ (thành tiền) = HOÃN chờ đối tác chốt yêu cầu.
- **KHÔNG training/fine-tune** — tool-use. **KHÔNG** hardcode key. Ưu tiên **độ AN TOÀN > độ phủ** (KPI ~0% bịa).
- **AI tự học** (nếu làm): học CÁCH ĐỌC (verify được), KHÔNG học SỰ THẬT; hóa-cứng thì người duyệt.

## File quan trọng
- Code: `app.py`, `mcp_bridge.py`, `mcp_server.py`, `tools_core.py`, `dwgconv.py`, `vntext.py`
- Test: `tests/test_takeoff_chong_bia.py`, `tests/test_qa_data.py`
- Tài liệu: `GHI_CHU_HOAN_THIEN.md`, `ROADMAP_DEMO2.md`, `KE_HOACH_TONG_QUAT_HOA.md`, `NGHIEN_CUU_AI_TU_HOC.md`, `harness/`
- Cloud: https://doc-autocad-mcp-demo.onrender.com · repo private `KimDat2705/demo-doc-autocad-mcp`
