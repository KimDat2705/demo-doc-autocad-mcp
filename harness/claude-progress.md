# Claude Progress — demo 2 (nhật ký tiến độ theo phiên)

> **🔁 2026-07-17 — THỬ MỞ PUBLIC RỒI HOÀN TÁC (repo GIỮ PRIVATE):** user đổi ý giữa chừng. Đã **khôi phục main về `130afae`** từ mirror backup + force-push → demo NGUYÊN TRẠNG (verify: `/version`=130afae, `/health` ok, **upload .dwg thật lên cloud CHẠY LẠI** — ODA convert ok, 102 layer/1555 text khớp local). **Mọi hash cũ trong tài liệu này CÒN HIỆU LỰC** (c0b85af/97ffc60/7188c3c/130afae…).
> **⚠ VÌ SAO REPO PHẢI PRIVATE:** `vendor/ODAFileConverter.deb` (53.6MB) là phần mềm **ĐỘC QUYỀN của Open Design Alliance**, phải commit để Render build Docker → **public = phân phối lại binary bên thứ ba**. Đây là ràng buộc LICENSE, không phải tuỳ chọn.
> **Muốn public thật sau này — ĐỪNG LÀM LẠI TỪ ĐẦU:** nhánh local **`public-ready`** đã có sẵn trọn gói (history sạch không .deb qua `git filter-repo` · Dockerfile tải ODA tuỳ chọn qua `ODA_DEB_URL` · thông báo .dxf-only thân thiện · .gitignore chặn .deb). Đánh đổi: cloud chỉ đọc .dxf tới khi đặt `ODA_DEB_URL`. Mirror backup: `D:/Dat-Antigravity/_backup_repo_truoc_khi_public_20260717/repo-mirror.git`.


> Continuity Artifact (chuẩn Harness): lưu "đã làm gì / kết quả test / quyết định / đang chờ" để phiên sau không mất ngữ cảnh.
> Mới nhất ở TRÊN CÙNG. Bàn giao đầy đủ: `session-handoff.md`. Nhật ký chi tiết hơn nữa: `../GHI_CHU_HOAN_THIEN.md`.

---
## Session 2026-07-22 — AUDIT phiên GĐ4 (34-agent) + vá bó F1/F4/test (đối kháng, tự-repro)
**User yêu cầu:** rà soát tester chuyên nghiệp mọi thay đổi phiên GĐ4 TRƯỚC khi đi tiếp, rồi triển khai bó vá (red-team F4 trước khi code).

**AUDIT (workflow 34-agent: 6 mảng review → skeptic-verify từng finding → synth):** 23 CONFIRMED/1 xác-minh-dương · 4 BÁC BỎ · **0 bug lớp nghiêm trọng** (không đổi số/crash/mất code). Git toàn vẹn sau rebase+filter-repo+restore (5/5 CONFIRMED tốt: main có đủ fix, .deb tracked, Dockerfile private, public-ready sạch, origin==local). id135 an toàn. Tôi TỰ kiểm chứng lại 2 finding chính (không tin judge mù) → cả 2 CONFIRM.
- **F1 (TB) — cảnh báo OLE cắm THIẾU chỗ:** `tra_cuu_so_luong`/`liet_ke_so_luong`/`thong_tin_kich_thuoc` trả kết-quả-âm trên file 8-OLE mà KHÔNG mang `canh_bao_nhung` = đúng failure mode rule 8c định chống, tôi chỉ cắm ở tuyến thép.
- **F4 (tiền đề SAI) — `_CD_INL` bỏ `\s*`:** comment "cao độ luôn dính liền" bị corpus bác — có mốc THẬT dạng cách `'cốt + 7.690'`,`'+ 8.500'`,`'± 0.000'`,`'CÈT + 9.800'`; fix cũ bỏ hết (min/max chưa đổi nhưng cơ chế sai trục + latent id135-loss).
- **D6 — tôi tự rút lại claim RAM:** "45MB×11.3=577MB→OOM" SAI (11.3x đo ở file 26.5MB, không phải ≤45MB = ngoại suy sai). Rủi ro OOM thật ở cơ chế khác: bỏ quên `MAX_SESSIONS=4`.

**VÁ (gate [22/22] · takeoff 258 · qa 129 · cao_do 27→31 · ole 25→37 · 0 regress):**
- **F1:** `_gan_canh_bao_nhung` cắm vào 3 tuyến CHỈ KHI kết quả RỖNG (gate-on-empty chống nhiễu: file OLE-khung-tên vẫn tra thấy số → KHÔNG cảnh báo). Verify: Gia Lộc KT 2-OLE tra thấy 38 mục → không cảnh báo.
- **F4 (RED-TEAM TRƯỚC KHI CODE, workflow 4-agent → GO_WITH_ADJUSTMENTS):** red-team BÁC thiết kế blacklist-nhãn của tôi (vỡ garble 2 chiều) VÀ Design-B chỉ-+/± (drop id135 `cốt - 14.260`). **Thiết kế CHỐT:** `_CD_INL` khôi phục `\s*` (nhóm gap) → `+`/`±` mọi gap + `-` dính liền → min/max; **`-` DẤU CÁCH ('WORD - n.nnn', đồng dạng FP `CH-2.700` VÀ id135 `cốt-14.260`, KHÔNG tách được hình thức, nhãn vỡ garble) → đẩy `canh_bao` (LỘ, không bịa min, miễn nhiễm garble)**. Verify engine thật: id135 dạng cách → canh_bao; FP CH → canh_bao (min giữ -1.6); thu lại `+7.69/+8.5/+9.8`; standalone/dính-liền vẫn min/max; **số verify GIỮ NGUYÊN** (KC -1.85, KT -2.1, 9T -1.6). + prompt rule 8: hỏi độ sâu mà canh_bao có marker-âm-cách → PHẢI nêu "cần đối chiếu tay".
- **Test (D5):** thêm ca motivating synthetic (bảng thép TRONG OLE → co_bang=False + cảnh báo, KHÔNG cần corpus) + test khoá id135 `cốt - 14.260` phải trong canh_bao (yêu cầu red-team).

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
