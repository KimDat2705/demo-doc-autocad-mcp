# QUY TRÌNH ĐO A/B — 20 cách phép đo tự hỏng, và cách chặn từng cái

> **Dùng khi nào:** trước MỌI phép đo so hai nhánh (đổi prompt · đổi model · bật/tắt một cơ chế ·
> đổi cách dựng request). Đọc file này TRƯỚC khi viết dòng script đo đầu tiên.
>
> **Quan hệ với các file khác:** `Q2_TIEU_CHI_TRUOC_KHI_CHAY.md` là bản *pre-registration* cho một
> lượt đo ổn định cụ thể (N=3, đóng băng cấu hình). File này ở tầng trên: nó liệt kê **các cách một
> phép đo A/B tự hỏng** bất kể pre-registration viết hay tới đâu. `clean-state-checklist.md` giữ
> các bài học ở tầng *commit*; đây là tầng *phép đo*.
>
> **Nguồn:** panel phản biện 2026-08-07 (`wf_28a75b80-60f`), sinh ra khi chuẩn bị A/B cho lát
> context-caching. Lát đó về sau **NO_GO** vì phép đo bác chính tiền đề của nó — nhưng danh sách
> dưới đây thì dùng lại được cho mọi lát sau.
>
> **⚠ TÌNH TRẠNG KIỂM CHỨNG:** danh sách do agent soạn từ đọc code. Tôi đã **tự kiểm 5 mệnh đề chịu
> lực nhất** (đánh dấu ✅ trong bài). Các mệnh đề còn lại **CHƯA tự kiểm** — dùng như *giả thuyết cần
> soi*, đừng trích như sự thật đã chứng minh.

---

## 0. BA CÂU HỎI BẮT BUỘC TRƯỚC KHI CHẠY ĐỒNG NÀO

1. **Nền nhiễu là bao nhiêu?** Nếu chưa biết khoảng cách A₁–A₂ (hai lượt CÙNG nhánh) thì mọi con số
   A–B đều vô nghĩa. `temperature` đã chết trên Gemini 3 ⇒ model **không tất định**, nền nhiễu lớn.
2. **Quần thể thật sự bị ảnh hưởng có bao nhiêu câu?** Nếu là 8/198 thì đo trên 198 sẽ ra "không đổi
   gì" một cách **tất yếu**, còn đo riêng 8 câu thì n quá nhỏ để nói gì.
3. **Dụng cụ có đo được đúng đại lượng cần không?** Muốn nói về TIỀN mà chỉ có `thoi_gian_s` thì
   đang nói về một đại lượng khác.

Không trả lời được cả ba → **chưa được chạy**.

---

## 1. NHÓM CHẾT-PHÉP-ĐO (kết quả vô nghĩa, nhưng vẫn đọc được thành kết luận)

### 1.1 Không có nhánh đối chứng A-vs-A
Chạy A một lượt, B một lượt rồi đếm "B lệch A ở 23 câu" **không tách được** phần do đổi prompt khỏi
phần do model tản. `tests/do_on_dinh.py` đã đo: hai lượt CÙNG model cách nhau 3 tuần chỉ giống nguyên
văn **3,5%**. Nền nhiễu lớn hơn mọi hiệu ứng mà lát đang xét có thể tạo ra.

- **Dấu hiệu sớm:** bảng kết quả chỉ có 2 cột (A, B), không có A₂/B₂.
- **Chặn:** ≥2 lượt MỖI nhánh; **công bố khoảng cách A₁–A₂ TRƯỚC** khi công bố A–B; chỉ được nói
  "B khác A" khi delta liên-nhánh **vượt hẳn** delta nội-nhánh. Chạy **xen kẽ A,B,A,B** (không phải
  A,A,B,B) để hấp thụ trôi theo thời gian/quota.

### 1.2 Quần thể nhạy cảm quá nhỏ — pha loãng, hoặc n quá bé
Hai đầu đều cho kết luận vô căn cứ: gộp vào 198 câu thì hiệu ứng ở 4,5% mẫu bị 95,5% còn lại nuốt;
tách riêng 8 câu thì một câu đổi ý = 12,5 điểm phần trăm.

- **Chặn:** khai báo TRƯỚC **hai tầng** — (a) *tầng nhạy cảm* = danh sách id cố định, lặp nhiều lượt
  trên đúng tầng này; (b) *tầng hồi quy* = 198 câu, **chỉ** dùng bắt sập diện rộng, **không** dùng
  kết luận về tầng nhạy cảm.

### 1.3 Chọn nhánh bằng biến môi trường → cổng chống-trộn-phiên-bản mù
Nếu bật nhánh B bằng env để giữ `code_hash` bằng nhau thì `dinh_danh()` ghi ra hai bản ghi **giống
hệt nhau**; cổng "chạy tiếp mà định danh đã đổi" không phát hiện được, và một file lượt có thể chứa
**trộn** hai nhánh.

- **Dấu hiệu sớm:** hai meta có `prompt_hash8`/`code_hash8`/`model` y hệt, chỉ khác `ghi_chu` gõ tay.
  Hoặc `do_on_dinh` chạy trơn tru trên cả A lẫn B — **đúng lúc nó PHẢI dừng**.
- **Chặn:** dùng env thì phải thêm env vào `dinh_danh()` **và** `KHOA_CHAN_TRON` trước khi chạy;
  không thì tách hẳn hai commit/worktree. **Tuyệt đối không `--tiep` xuyên nhánh.**

### 1.4 ✅ Tham số sinh đọc từ env nhưng KHÔNG nằm trong định danh lượt
**Đã tự kiểm:** `dinh_danh()` ghi `prompt_version`, `prompt_hash`, `kb_version`, `kb_hash`,
`code_hash`, `battery_sha`, `model`, `models_cau_hinh`, `fallback_bi_tat`, `max_turns`, `commit`,
`python` — **KHÔNG** ghi `GEMINI_TEMPERATURE` / `GEMINI_MAX_OUTPUT_TOKENS` / `GEMINI_THINKING_LEVEL`.
Một shell còn sót `export` từ probe hôm trước là đủ để hai nhánh chạy khác cấu hình sinh mà **không
để lại dấu vết nào**.

- **Dấu hiệu sớm:** *không có dấu hiệu trong dữ liệu — đó chính là vấn đề.* Gián tiếp: thời gian/token
  của một nhánh lệch hệ thống mà nội dung câu trả lời không giải thích được.
- **Chặn:** thêm 3 biến đó (+ `GEMINI_MAX_TURNS`, `READFILE_MAX_MB`, `I1_KIEM_HANDLE`) vào
  `dinh_danh()` TRƯỚC khi chạy; chạy hai nhánh từ **shell mới**, không kế thừa.

### 1.5 ✅ Đo chi phí/cache bằng `thoi_gian_s` vì không nơi nào ghi `usage_metadata`
**Đã tự kiểm:** `mcp_bridge.py` không đọc/ghi `usage_metadata`; `run_battery` chỉ ghi `thoi_gian_s`.
Thời gian bị chi phối bởi số lượt gọi tool, kích thước bản vẽ, mạng và tải phía Google — **không**
bởi token vào được cache.

- **Dấu hiệu sớm:** báo cáo xuất hiện câu *"B nhanh hơn N% ⇒ tiết kiệm token"*.
- **Chặn:** thêm seam phía test ghi `resp.usage_metadata` vào bản ghi (theo khuôn `_bat_ro_neo`),
  **KHÔNG** đưa vào dict trả về của `tra_loi_ai` (`app.py` `jsonify` sẽ bơm ra trình duyệt).
  **Không có số token thì không phát biểu gì về chi phí.**

### 1.6 Đo nhánh B "inline" nhưng cái sẽ ship là `cached_content` — hai đường mã khác nhau
Dùng `cached_content` thì **không được** truyền `system_instruction`/`tools`/`tool_config` (API trả
400 — đã xác minh bằng gọi thật). Nhánh B trong A/B vẫn truyền cả ba inline. Nặng nhất: đường
**ép-trả-lời-cuối** khi hết `MAX_TURNS` **cố ý không truyền `tools`** để buộc model tự trả lời — nếu
cache chứa `tools` thì không còn cách bỏ nó ở lượt đó nữa.

- **Chặn:** viết thẳng vào kết luận rằng A/B này **chỉ** trả lời "dời X có hỏng chất lượng không",
  **không** trả lời "bật cache có an toàn không". Ca bắt buộc của lát cache: câu chạy hết `MAX_TURNS`.

### 1.7 Chấm điểm bằng từ khoá từ chối
Dự án đã dính đúng lỗi này: heuristic "có cụm từ chối" chấm ra 7/10/11 ca; đọc tay 12 ca thì phần lớn
là **trả lời ĐÚNG**, số thật là 3/3/2. Đủ để lật dấu kết luận.

- **Chặn:** mọi ca mà hai nhánh khác nhau phải **ĐỌC TAY** (đọc toàn bộ tập lệch, không lấy mẫu — tập
  này nhỏ). Bộ dò tự động chỉ để **khoanh vùng**, và phải chạy thử trên ca đã biết đáp án trước khi tin.

### 1.8 Chạy nhầm cây / bytecode cũ / sửa cây trong lúc lượt đang chạy
Ba cơ chế đều có tiền lệ: `__pycache__` cũ (Python xác thực cache theo mtime+size, độ phân giải
**giây**) · tồn tại bản sao cây ở `.claude/worktrees/…` với cùng call-site · `dinh_danh()` chốt MỘT
LẦN lúc khởi động nên meta không phản ánh cây hiện tại.

- **Dấu hiệu sớm:** hai nhánh giống nhau **đến mức bất thường** — giống hơn cả nền A-vs-A — là dấu
  hiệu kinh điển của bytecode cũ.
- **Chặn:** xoá `__pycache__` trước MỖI lượt; in `mcp_bridge.__file__` tuyệt đối + `code_hash` vào
  chính file log ở đầu lượt; không sửa file nào trong lúc lượt đang chạy; `git status` sạch.

---

## 2. NHÓM LÀM-LỆCH (số ra sai chiều, thường sai theo hướng dễ chịu)

| # | Cách hỏng | Chặn |
|---|---|---|
| 2.1 | **Dụng cụ đo TỪ CHỐI so hai nhánh, rồi bị "chữa" bằng cách tắt cổng.** `do_on_dinh.py` coi `code_hash8` là khoá định danh nên sẽ DỪNG — cái DỪNG đó **an toàn**; nguy hiểm là phản ứng sau đó (bỏ `code_hash` khỏi khoá, gộp tay hai file) làm mất hàng rào cho **mọi** phép đo về sau | Viết công cụ **so nhánh RIÊNG**, không đụng `do_on_dinh.py`. Chạy nó trên hai lượt CÙNG nhánh trước để xác nhận ra ~0 khác biệt |
| 2.2 | ✅ **`prompt_hash` không đổi dù `system_instruction` gửi đi đã đổi.** Đã tự kiểm: `PROMPT_HASH = sha256(SYSTEM_PROMPT)` — chỉ hash phần HẰNG, không hash chuỗi thật gửi lên. Hai nhánh cùng khoe `239e8b7b` ⇒ **hồ sơ lượt nói dối** | Thêm khoá `si_shape` = sha256 của **khuôn** `system_instruction` đã dựng (phần biến thay bằng placeholder); tối thiểu ép `--ghi-chu` theo mẫu cứng và kiểm nó tồn tại |
| 2.3 | ✅ **Harness chỉ đổi `file_summary` 3 lần/198 câu.** Đã tự kiểm: battery nạp bản vẽ **theo NHÓM** (`for f in ORDER: nap_ban_ve → for q in can[f]`) nên tiền tố bất biến suốt cả nhóm ⇒ lợi ích cache **về mặt cấu trúc không thể xuất hiện**. Đó là thuộc tính của THỨ TỰ HARNESS, không phải của hệ | Tách phép đo CHI PHÍ khỏi battery: kịch bản **xoay vòng bản vẽ** (nạp KT → 1 câu → nạp KC → 1 câu → …). Battery chỉ dùng cho vế CHẤT LƯỢNG |
| 2.4 | ✅ **`file_summary` của battery KHÁC của sản phẩm.** Đã tự kiểm: battery dùng **bí danh** (`FILES[f]`), `app.py` dùng **tên file thật**. Hệ quả ngược chiều: nhánh nào nhại bí danh bị chấm SAI dù ở sản phẩm hành vi y hệt lại ĐÚNG; và tên file thật có thể **chứa số** (ca `MC coc -13.7 va 7500.dxf` từng lật câu bịa từ CHẶN sang LỌT) mà bí danh sạch số không bao giờ chạm tới | Chấm riêng các câu tên-file, không gộp vào tổng. Thêm ca với tên file **có số đo** |
| 2.5 | ✅ **Battery luôn gọi `history=None`.** Đã tự kiểm: `hoi_fn(br, q, summary)` — không truyền history, trong khi sản phẩm có. Lớp lỗi "nội dung nhét vào history nhân lên qua các lượt" **không thể thấy được** ⇒ A/B xanh rồi vỡ ở sản phẩm | Chạy `tests/kichban_gd2.py` (12 lượt, CÓ history) cho cả hai nhánh, hoặc thêm 3-5 cặp câu nối tiếp |
| 2.6 | **Hai cách cài đặt B không tương đương — đo cái này, ship cái kia.** Nối chuỗi vào `q` làm phình tập token của `_kiem_handle` ⇒ hàng rào I1 **yếu đi im lặng** trong khi điểm chất lượng **đẹp lên** | Chốt bản cài đặt B **bằng văn bản** trước khi chạy. Thêm trục *"số cảnh báo I1 phát ra"* vào bảng so sánh |
| 2.7 | **So số thô `'8.024'` vs `'8024'`** — từng hạ oan 3.6-flash mất 11 ca, và bẫy này rơi đúng nhóm câu số lớn | Chuẩn hoá HAI CHIỀU (bỏ `.` `,` `_` khoảng trắng trong số) rồi mới so; chạy bộ chấm lên ca đã biết đáp án |
| 2.8 | **Nhãn "đúng" và nhãn "an toàn" ngược nhau** + `ky_vong` tautology: số trong `file_summary` do HOST bơm, **không bao giờ vào rổ neo**, nên câu nhại tóm tắt thì ĐÚNG NỘI DUNG mà KHÔNG CÓ NEO. Chấm theo `ky_vong` sẽ **thưởng cho hành vi nhại tóm tắt** | Khai báo trước rằng trục quyết định của nhóm này là **ĐƯỜNG ĐI** (có gọi tool không / số có neo không), dùng `tool_goi` + `ro_neo_n` sẵn có |
| 2.9 | **Tỉ lệ ổn định tự đẹp lên khi hệ trả lời ÍT đi** — nhánh làm tăng REFUSE sẽ trông như nhánh tốt hơn vì mẫu số co lại | Luôn công bố **cặp** (chỉ số ổn định, tỉ lệ câu không nêu số). **Cấm trích một mình chỉ số ổn định.** So mẫu số trước khi so tỉ lệ |
| 2.10 | **Survivorship do 429/503** — câu nặng dễ rơi hơn, rơi KHÔNG ngẫu nhiên; hai nhánh còn lại tập câu khác nhau về độ khó trước khi so | So **chỉ trên giao** của id hợp lệ ở TẤT CẢ lượt của CẢ HAI nhánh; công bố kích thước giao; chạy xen kẽ, `--nghi` giống nhau |
| 2.11 | **"Không thấy khác biệt" bị đọc thành "không có khác biệt"** — thiếu lực thống kê + gộp một điểm (B tốt lên ở nhóm này, tệ đi ở nhóm chống-bịa, triệt tiêu thành 0) | Bắt buộc bảng **theo nhóm**, tách riêng nhóm bẫy. Khi ra "không khác", phát biểu **kèm cận**: *"không phát hiện được chênh lệch lớn hơn X câu với N lượt/nhánh"* |
| 2.12 | **Hệ quả SAU đo: "chữa" hồi quy bằng cách bơm số tóm tắt vào rổ neo** — đó là mở **kênh bơm rổ neo thứ NĂM** (sau mã hiệu gạch nối / tên file / handle / prose `ghi_chu`) | Chốt trước: A/B này **không được kèm bất kỳ thay đổi nào lên rổ neo**. Có hồi quy REFUSE thì đó là **kết quả cần báo cáo**, không phải thứ để vá trong cùng lượt đo |

---

## 3. BA BÀI HỌC TỪ CHÍNH PHIÊN 2026-08-07 (tôi tự dính, không phải lý thuyết)

**3.1 — Ra đề sai rồi chấm câu ĐÚNG thành SAI.** Hỏi *"liệt kê bảng thống kê thép"* trên file
**bảng cửa** (không hề có bảng thép), rồi chấm câu trả lời đúng (*"bản vẽ không có"*) thành *từ chối
oan* ⇒ báo "recall 1/2" = **số rác**.
→ **Đọc sự thật nền từ file (`ezdxf`) TRƯỚC khi ra đề.**

**3.2 — Đo "ổn định" bằng so CHUỖI NGUYÊN VĂN** ⇒ đếm khác-diễn-đạt thành khác-đáp-án ("3/4 câu
không ổn định"), trong khi tập SỐ giống hệt nhau.
→ **Chấm trên TẬP SỐ + PHÁN QUYẾT, không phải trên văn bản.**

**3.3 — ⭐ Phép đo CHẾT vì lỗi hạ tầng mà kết quả vẫn được viết vào sổ.** Lượt đo sạch chết vì
`WinError 10053` **trước khi chạy được lượt nào**, nhưng tôi vẫn ghi *"implicit trúng 75,2% ba lần rồi
rơi về 0% lần thứ tư"* vào sổ + memory + commit, rồi dựng cả một lập luận lên trên nó. Đo lại:
**0% · 75,2% ×5, ổn định, không rơi.**
→ Đây là lớp lỗi **khác** các bài học bộ-trích-hỏng: lỗi hạ tầng **giết phép đo mà không giết niềm tin
vào kết quả** — nguy hiểm hơn phép đo cho số sai, vì **không có con số xấu nào để mà nghi**.
→ **Quy tắc: phép đo chết = KHÔNG CÓ SỐ. Chạy lại. Không lấp bằng suy đoán.**
→ Script đo phải **có retry mạng** và **in rõ đã chạy đủ N lượt chưa** trước khi in kết luận.

---

## 4. MẪU ĐỐI CHỨNG ÂM (bắt buộc, rẻ, và đã cứu một kết luận trong phiên này)

Khi ba biến thể ra số **giống hệt nhau**, hoặc một tỉ lệ ra **0%** / **100%**, đừng mừng và cũng đừng
hoảng — hỏi: *"phép đo này CÓ THỂ ra kết quả khác được không?"* Rồi **chứng minh bằng cách phá**.

Ví dụ thật (đo implicit cache): 3 biến thể đều ra 75,0%, nghi "hằng số chết" ⇒ chạy đối chứng âm —
chèn chuỗi lạ vào **đầu** `system_instruction` → cached **0** · bỏ hết khai báo tool → **0** ·
`system_instruction` cụt → **0**. **Đạt 3/3** ⇒ thước đo có phản ứng thật ⇒ con số 75,0% dùng được.

**Không có đối chứng âm thì mọi con số "ổn định đẹp" đều có thể là hằng số chết.**
