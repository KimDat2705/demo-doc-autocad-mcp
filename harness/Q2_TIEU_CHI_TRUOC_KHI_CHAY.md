# Q2 — TIÊU CHÍ ĐỊNH TRƯỚC KHI CHẠY (pre-registration)

> **Commit file này TRƯỚC khi chạy lượt nào.** Mốc thời gian trong git là thứ duy nhất chứng minh
> các ngưỡng dưới đây được chốt *trước* khi nhìn thấy kết quả, chứ không phải chế ra sau cho vừa số.
> Dự án đã có tiền lệ đau: "tỉ lệ lọt" từng được trích ở 5 giá trị khác nhau (0% → 77,5%) vì mỗi lần
> lại chọn cách đo hợp với kết luận mong muốn.

## 0. Q2 LÀ GÌ / KHÔNG LÀ GÌ

**LÀ:** chạy lại bộ 198 câu **N = 3 lượt** trên CÙNG một bản code, rồi đo **ĐỘ ỔN ĐỊNH** —
chạy lại có ra như cũ không.

**KHÔNG LÀ:** đo độ ĐÚNG. Ba lượt cùng sai giống hệt nhau vẫn cho 0% mâu thuẫn. Việc chấm
đúng/sai (dùng `ky_vong` / `loi_san` / `tieu_chi_dat`) là **việc RIÊNG, sau Q2**, cần judge panel
và tốn thêm API — không gộp vào đây.

**Cũng KHÔNG phải** dịp để công bố lại "bảng điểm 198 câu". Bảng cũ (24/07) lạc hậu và đã bị cấm
trích; Q2 chỉ sinh ra **dữ liệu thô có đóng dấu phiên bản** để lần chấm sau dùng được.

## 1. CẤU HÌNH ĐÓNG BĂNG (không đổi giữa chừng)

| mục | giá trị |
|---|---|
| N | **3 lượt** (`run02`, `run03`, `run04` — `run01` đã bị loại, xem §5) |
| model | `gemini-2.5-flash`, **chuỗi dự phòng TẮT** (`run_battery` tự ép `GEMINI_FALLBACK_MODELS=""`) |
| thứ tự câu | **CỐ ĐỊNH**, y hệt nhau cả 3 lượt (không dùng `--tron-thu-tu`) |
| bản vẽ | KT / KC / HT của `corpus_local`, thứ tự `kientruc → ketcau → hatang` |
| nơi chạy | **LOCAL**, KHÔNG chạy trên LIVE production |
| công cụ đo | `tests/do_on_dinh.py`, không sửa sau khi có kết quả |

Định danh phải giống nhau cả 3 lượt: `prompt_hash` `239e8b7b…` · `kb_hash` `e55ac112…` ·
`code_hash` `319de40e…` · `battery_sha` `5f29111a…`.

## 2. CỔNG HỢP LỆ CỦA PHÉP ĐO (vi phạm ⇒ VÔ HIỆU, cấm trích số)

- **G1** — mỗi lượt phải đủ **198/198** câu có bản ghi (`run_battery` thoát mã 0).
- **G2** — mỗi lượt ≤ **5%** câu hỏng hạ tầng (429/rỗng/malformed). `do_on_dinh` tự chặn.
  *Căn cứ:* 2 lượt lịch sử đều **0,0%** hỏng, nên 5% đã là rất rộng tay.
- **G3** — cả 3 lượt cùng 4 hash ở §1. `do_on_dinh` tự chặn (kiểm theo TỪNG DÒNG).

Nếu một lượt vi phạm G1/G2 → chạy `--tiep` cho hết rồi mới đo. Nếu vi phạm G3 → **vứt lượt đó**,
chạy lại lượt mới; **tuyệt đối không** "đo tạm rồi ghi chú".

## 3. CHỈ SỐ CHÍNH (chốt trước, không đổi định nghĩa sau khi thấy số)

Trung bình trên cả **C(3,2) = 3 cặp lượt** (bất biến theo N; **không** dùng "cặp tệ nhất" làm
chỉ số chính vì nó luôn xấu đi khi N tăng):

- **M1 = MÂU THUẪN SỐ** — hai lượt cùng nêu số nhưng tập số đá nhau.
- **M2 = TRẢ LỜI vs TỪ CHỐI** — lượt này ra số, lượt kia bảo "không có".
- **M3 = M1 + M2** — bất ổn mà người dùng THẤY. **Đây là chỉ số quyết định.**

Mẫu số đã **loại** rổ `khong_so_moi_luot` (cả hai lượt đều không nêu số) — nếu tính vào, con số
đẹp lên vô nghĩa vì câu không có số thì không thể lệch.

## 4. LUẬT HÀNH ĐỘNG THEO MỨC (chốt TRƯỚC khi chạy)

| M3 | kết luận | hành động bắt buộc |
|---|---|---|
| **≤ 10%** | ổn định đủ cho demo | ghi baseline vào handoff. KHÔNG mở việc vá mới. |
| **10% – 25%** | có bất ổn thật, chưa nguy cấp | lấy **TOP 12** câu bất ổn nhất, truy nguyên nhân từng câu (bug tool / routing Gemini / nhập nhằng thật của bản vẽ), mở việc vá cụ thể cho nhóm bug-tool. |
| **> 25%** | **RỦI RO DEMO** | báo user NGAY. Cùng một câu hỏi mà số đổi giữa các lần chạy là thứ đối tác sẽ thấy. Ưu tiên vá trước mọi việc nhóm A còn lại. |

*Vì sao mốc 25%:* đo được trên 2 lượt lịch sử **cùng model nhưng KHÁC code** cho 33,6% bất đồng
trên nhóm câu có khẳng định đo-lường. Đó là chặn trên *đã gồm cả trôi do đổi code*. Bất ổn thuần
do chạy lại mà chạm tới mức đó thì phải coi là nghiêm trọng.

**M1 và M2 phải đọc CÙNG NHAU với tỉ lệ từ chối từng lượt.** M1 GIẢM khi hệ trả lời ÍT đi —
một lượt từ chối nhiều hơn sẽ làm số đẹp lên một cách giả tạo. `do_on_dinh` in sẵn bảng đó.

## 5. NHỮNG THỨ ĐÃ BIẾT TRƯỚC, KHAI BÁO THẲNG

- **`run01` bị LOẠI.** 42 bản ghi sinh ra do sự cố tham số ngày 2026-07-31, ở `code_hash bdffe2ea`
  (trước 1.03/1.04). Cổng chống-trộn của 1.06 đã tự từ chối `--tiep` vào nó. Không dùng, không xoá.
- **Điểm mù đã khai báo:** đo tại **MỘT thứ tự câu hỏi cố định**. 198 câu chạy tuần tự trong cùng
  một phiên bridge nên trạng thái theo phiên (`kb_hoi`, `kb_da_phat`) truyền từ câu trước sang câu
  sau. Đổi thứ tự **chưa đo bao giờ** — Q2 KHÔNG kết luận gì về chiều đó.
- **Biến nhiễu không khử được:** khung giờ chạy (quota Gemini), tải máy chủ Google.
- Bộ tách số dùng chính bộ của hàng rào chống bịa, **kể cả hạn chế đã biết** (dấu ngăn nghìn kiểu
  VN). Hai lượt bị tách sai giống nhau nên phần lớn triệt tiêu, nhưng không phải hết.

## 6. LỆNH CHẠY

```bash
cd demo_mcp_autocad
python tests/run_battery.py --luot 2 --ghi-chu "Q2 luot 1/3"
python tests/run_battery.py --luot 3 --ghi-chu "Q2 luot 2/3"
python tests/run_battery.py --luot 4 --ghi-chu "Q2 luot 3/3"
python tests/do_on_dinh.py --luot 2,3,4
```
