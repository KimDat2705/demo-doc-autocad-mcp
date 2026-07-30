# Claude Progress — demo 2 (nhật ký tiến độ theo phiên)

> **🔁 2026-07-17 — THỬ MỞ PUBLIC RỒI HOÀN TÁC (repo GIỮ PRIVATE):** user đổi ý giữa chừng. Đã **khôi phục main về `130afae`** từ mirror backup + force-push → demo NGUYÊN TRẠNG (verify: `/version`=130afae, `/health` ok, **upload .dwg thật lên cloud CHẠY LẠI** — ODA convert ok, 102 layer/1555 text khớp local). **Mọi hash cũ trong tài liệu này CÒN HIỆU LỰC** (c0b85af/97ffc60/7188c3c/130afae…).
> **⚠ VÌ SAO REPO PHẢI PRIVATE:** `vendor/ODAFileConverter.deb` (53.6MB) là phần mềm **ĐỘC QUYỀN của Open Design Alliance**, phải commit để Render build Docker → **public = phân phối lại binary bên thứ ba**. Đây là ràng buộc LICENSE, không phải tuỳ chọn.
> **Muốn public thật sau này — ĐỪNG LÀM LẠI TỪ ĐẦU:** nhánh local **`public-ready`** đã có sẵn trọn gói (history sạch không .deb qua `git filter-repo` · Dockerfile tải ODA tuỳ chọn qua `ODA_DEB_URL` · thông báo .dxf-only thân thiện · .gitignore chặn .deb). Đánh đổi: cloud chỉ đọc .dxf tới khi đặt `ODA_DEB_URL`. Mirror backup: `D:/Dat-Antigravity/_backup_repo_truoc_khi_public_20260717/repo-mirror.git`.


> Continuity Artifact (chuẩn Harness): lưu "đã làm gì / kết quả test / quyết định / đang chờ" để phiên sau không mất ngữ cảnh.
> Mới nhất ở TRÊN CÙNG. Bàn giao đầy đủ: `session-handoff.md`. Nhật ký chi tiết hơn nữa: `../GHI_CHU_HOAN_THIEN.md`.

---
## Session 2026-07-30 (nối) — 📐 NHÓM A: rà soát lại toàn nhóm + **vá HỆ SỐ TỈ LỆ ĐO (DIMLFAC)** — 21,5% đường kích thước đang bị đọc SAI
> **CHỐT SỔ:** HEAD **`6de1aaa`**, tree SẠCH. check.sh **[36/36] PASS · 33 tool · 0 regress** (272/107/50/31/63/28/44/24/26… KHÔNG đổi). ⚠ **`6de1aaa` CHƯA PUSH** — cố ý, xem "VIỆC CHỜ" #0. LIVE vẫn là `371d950`.
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
