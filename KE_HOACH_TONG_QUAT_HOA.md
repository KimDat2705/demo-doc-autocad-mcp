# 🧭 KẾ HOẠCH TỔNG QUÁT HÓA & CHỐNG ẢO GIÁC — "cải thiện sao cho có điểm dừng"

> Soạn 2026-07-09, trả lời câu hỏi chiến lược: *"Cứ mỗi câu hỏi lạ lại phải sửa một tý — khi giao cho đối tác,
> không biết họ hỏi gì / upload file thế nào, cải thiện bao nhiêu vẫn thiếu. Phương pháp cải thiện con AI này là gì?"*

## 1. Bản chất: chúng ta KHÔNG "training AI"
- Demo **không** dạy/huấn luyện model, **không** cần dataset ảnh/Excel.
- Kiến trúc = **AI DÙNG CÔNG CỤ** (function-calling / tool-use):
  - **Code Python (tất định)** đọc số THẬT từ file, kèm `handle` truy nguồn.
  - **Gemini** chỉ làm 3 việc: *hiểu câu hỏi → chọn gọi tool nào → diễn đạt kết quả*.
  - Con số "24 bộ cửa", "137,92 kg inox" do **CODE tính**, KHÔNG do model "nhớ".
- Ví von: AI như một **thư ký thông minh KHÔNG học thuộc gì** — hỏi con số thì nó **mở đúng ngăn tủ** (gọi tool) đọc
  số thật ra, kèm số hiệu trang (handle). "Bộ não đọc số" là code, không phải trí nhớ AI → nên **chạy file lạ được ngay**
  (không cần "học" file đó) và **không bịa** (số có nguồn).

## 2. Vậy "cải thiện AI" = cải thiện 3 TẦNG (không phải luyện model)
| Tầng | Là gì | Vì sao hay phải sửa |
|---|---|---|
| **① ĐỌC** (code đọc file) | Nhận diện quy ước bản vẽ: font, đơn vị (cm/mm), cách ghi SL, dạng bảng, chữ X-hoa… | Bản vẽ VN **KHÔNG có chuẩn chung** — mỗi đơn vị thiết kế vẽ khác → gặp quy ước mới = thêm code |
| **② PHÁN ĐOÁN** (system prompt / luật) | Khi nào TÍNH / khi nào TỪ CHỐI, chọn tool nào, luật chống bịa | LLM đôi khi ảo giác / lạc trọng tâm → thêm rào chắn |
| **③ CÔNG THỨC/TOOL** (khả năng) | Loại đại lượng tính được (inox, diện tích…) | Đối tác cần cái mới = thêm công thức |

→ Cái bạn thấy "setup từng tý" chủ yếu ở tầng ① (quy ước mới) và ② (rào mới).

## 3. Đính chính NỖI SỢ: tách ĐỘ PHỦ vs ĐỘ AN TOÀN
Nỗi lo "cải thiện bao nhiêu vẫn thiếu" **đúng một nửa** — phải tách 2 thứ RẤT khác nhau:

- **ĐỘ PHỦ (coverage):** đọc được bao nhiêu quy ước, tính được bao nhiêu loại câu.
  → **SẼ LUÔN CÓ LỖ HỔNG.** Không thể phủ 100% (bản vẽ không chuẩn + đối tác hỏi mở). **Chấp nhận điều này.**
- **ĐỘ AN TOÀN (safety):** khi gặp cái CHƯA phủ, hệ **CƯ XỬ** thế nào?
  - ✅ AN TOÀN: *"cái này tôi chưa đọc/tính được / còn thiếu số / chưa hỗ trợ"* → **thú nhận**.
  - 🔴 NGUY HIỂM: trả một con số **SAI mà tưởng đúng** → thảm họa cho thi công / dự toán.

> **CHÌA KHÓA:** Sản phẩm dùng được hay không **KHÔNG nằm ở độ phủ, mà ở độ AN TOÀN.**
> Nếu mỗi khi gặp cái lạ hệ đều **thú nhận (an toàn)** thay vì **bịa (nguy hiểm)**, thì **bạn KHÔNG cần đoán trước
> mọi câu hỏi / mọi file của đối tác** để giao được sản phẩm. Cái xấu nhất đối tác gặp = *"demo nói: cái này tôi
> chưa làm được, bạn cấp thêm X"* (chấp nhận được, trung thực) — CHỨ KHÔNG PHẢI *"dự toán sai"* (mất uy tín).

Đây chính là lý do cả buổi tập trung **bịt các lỗ BỊA SỐ** (mã giả GHOSTINOX, tự vơ diện tích sàn, inf/tràn số): đó là
bịt những chỗ mà **input lạ có thể ra số SAI thay vì thú nhận**. Đúng trọng tâm.

## 4. KẾ HOẠCH — 2 mũi

### 🛡️ Mũi 1 (ƯU TIÊN): làm KÍN mạng an toàn — "gặp lạ thì thú nhận, tuyệt đối không bịa"
Đây là thứ cho phép **giao sản phẩm mà không cần biết trước mọi câu**.
1. **Kiểm thử đối kháng định kỳ** (như workflow hôm nay): ném câu/input lạ vào TỪNG tool, xác nhận thất bại luôn là
   "từ chối an toàn", không bao giờ ra số bịa → đưa vào bộ test thường trực.
2. **Rà soát mọi resolver tìm đường "bịa ngầm"** (các bug GHOSTINOX / tự-vơ-diện-tích là loại này): resolver nào khi
   input lạ/thiếu lại TRẢ SỐ thay vì `None`/từ chối? → audit hết.
3. **Luôn LỘ độ tin cậy**: đọc-thẳng (đáng tin) / gán-vị-trí (chưa chắc) / suy-đoán (cảnh báo). Không trình số "chưa chắc" như chắc chắn.
4. **ĐO bằng KPI ĐÚNG:** trên bộ câu khó, đo **"tỷ lệ trả lời SAI (bịa)"** → mục tiêu ≈ **0%**; "từ chối khi không chắc"
   là CHẤP NHẬN ĐƯỢC. → KPI là **"0% bịa"**, KHÔNG phải "100% trả lời".

### 📈 Mũi 2: mở rộng ĐỘ PHỦ CÓ HỆ THỐNG (thay vì vá phản ứng từng câu)
1. **Thu thập CORPUS đa dạng — đòn bẩy #1:** xin đối tác **nhiều bản vẽ của NHIỀU đơn vị thiết kế khác nhau** (không chỉ
   2-3 file). Mỗi đơn vị = một bộ quy ước. Rút quy ước từ corpus TRƯỚC khi đối tác gặp → chủ động thay vì phản ứng.
2. **Bộ câu hỏi CHUẨN lớn** (đã từng làm 198 câu): mở rộng + phân nhóm (đếm / kích thước / khối lượng / tính / tổng hợp /
   từ-chối-đúng), chạy định kỳ như "đề thi" cố định.
3. **Phân loại lỗi để tìm cái GENERALIZE:** mỗi lần fail, xếp vào (a) ảo giác, (b) lạc trọng tâm, (c) đọc thiếu (data có
   mà không lấy), (d) từ chối quá đà → sửa **NGUYÊN NHÂN HỆ THỐNG** của cả nhóm (1 luật prompt / 1 fix đọc phủ cả CLASS),
   KHÔNG sửa lẻ từng câu.
4. **Ghi LOG cái CHƯA đọc/hiểu được:** khi hệ bí, log lại mẫu không parse được → rà log → thêm quy ước. Biến "đối tác dùng"
   thành **vòng lặp cải thiện** (không im lặng bỏ sót).

## 5. Bottom line (thật lòng)
- Demo **sẽ không bao giờ** trả 100% câu lạ — đó là bình thường, đúng bản chất bài toán (bản vẽ không chuẩn + hỏi mở).
- Nó thành SẢN PHẨM DÙNG ĐƯỢC nhờ **3 điều**: (1) **không bao giờ đưa số SAI chắc nịch** → tin được cái nó nói;
  (2) độ phủ **tăng có hệ thống** (corpus + bộ câu hỏi), không chỉ vá phản ứng; (3) khi bí thì **bí một cách hữu ích** (nói cần gì).
- Sửa-từng-tý ở tầng ĐỌC là **một phần không tránh khỏi** (vì bản vẽ VN không chuẩn) — nhưng nên chuyển từ *"phản ứng theo
  câu đối tác"* → *"chủ động phủ bằng corpus đa dạng + đo độ an toàn"*.

## 6. Đề xuất bước đi NGAY (đề nghị làm trước khi giao rộng cho đối tác)
1. **Chạy 1 đợt AUDIT AN TOÀN toàn diện** (workflow đa-agent) trên MỌI tool → tìm hết đường "bịa ngầm" còn lại → bịt. *(Mũi 1, việc #1-2)*
2. Xin đối tác **3-5 bản vẽ của các đơn vị thiết kế KHÁC nhau** → rút quy ước + test đa-domain. *(Mũi 2, việc #1)*
3. Dựng lại **bộ câu hỏi chuẩn + KPI "tỷ lệ bịa"** → chạy, lấy số an toàn trước khi giao. *(cả 2 mũi)*

> Nguyên tắc này khớp với bài học đã ghi: *test ≥3 file khác domain trước khi tin; thất bại phải LỘ; phân tầng độ tin cậy*
> (xem `demo_mcp_autocad/GHI_CHU_HOAN_THIEN.md` mục "Chống bịa" + memory chống-overfit).
