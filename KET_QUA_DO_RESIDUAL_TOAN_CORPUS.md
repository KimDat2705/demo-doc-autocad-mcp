# KẾT QUẢ ĐO VÙNG CHƯA ĐỌC (residual) — TOÀN CORPUS

> **Đo 2026-08-06.** `86/86` file `.dxf` · **0 lỗi** · **14 phút** · offline, không tốn API.
> Script: `tests/do_residual_corpus.py` · Dữ liệu thô: `_khao_sat/residual_toan_corpus.json` (gitignored).
> Nhóm việc: **A**. Mục đích: biến câu hỏi mơ hồ *"đã đủ công cụ chưa?"* thành **hàng đợi công việc đếm được**.

---

## 0. ⚠ ĐỌC TRƯỚC KHI DIỄN GIẢI BẤT KỲ CON SỐ NÀO

**`residual` = đoạn chữ mà KHÔNG bộ nhận-diện nào hấp thụ** (handle không nằm trong `used_handles`) — nghĩa đen *"có chữ mà không hiểu"*.

**Nó KHÔNG có nghĩa "AI không nhìn thấy".** `tim_kiem` vẫn tìm ra mọi chuỗi đó (bộ chuẩn còn có sẵn câu *"đếm Ø16 xuất hiện bao nhiêu lần"*). Cái thiếu là bước:

> từ *"có chữ `Ø16` ở 17.908 chỗ"* → sang *"dầm D1 có 2Ø12 lớp trên, tổng X kg"*

**Phạm vi thước đo — chỉ đếm TEXT/MTEXT ở modelspace.** Nằm ngoài:
- **bảng OLE nhúng** → đọc bằng tool #27 `doc_bang_nhung`
- **thuộc tính block** (bảng thống kê thép) → `thong_ke_thep`, đã nằm trong `used_handles`
- **chữ trong định nghĩa block** → không có trong `self.texts` (xem `test_vung_chua_doc.py`)

⇒ residual vừa **nói quá** (gộp cả chữ ghi chú) vừa **nói thiếu** (bỏ qua phần đọc bằng đường khác).

---

## 1. SỐ TỔNG — và vì sao KHÔNG được đọc thành "hỏng 95%"

**956.114 đoạn chữ · residual 907.993 = 95,0%**

| Thành phần residual | Số lượng | % residual |
|---|---:|---:|
| Chữ + số, không đơn vị (mã hiệu, tiêu đề, tham chiếu) | 383.029 | 42,2% |
| Số trần | 226.864 | 25,0% |
| Chữ thuần, không số | 217.356 | 23,9% |
| ⭐ **Có đơn vị → hàng đợi ưu tiên** | **32.475** | **3,6%** |

### Con số 95% bị chi phối bởi 3 nhóm hạ tầng

| Nhóm | File | Đoạn chữ | residual | "có đơn vị" |
|---|---:|---:|---:|---:|
| 02.AP LUC TB4.1-TB6-TB1 | 9 | 369.101 | **99,8%** | 0,9% |
| 01.TUYEN CONG CHINH | 5 | 216.066 | **99,9%** | 0,5% |
| 03.TUYEN CONG DICH VU | 11 | 165.841 | 96,4% | 1,3% |
| BV MN KẺ SẶT | 23 | 58.051 | 70,5% | 6,9% |
| BV+DT nha 9 tang | 2 | 43.891 | **65,6%** | 19,0% |
| 1. BAN VE - C1 PHUNG VAN TRINH | 7 | 32.468 | 96,7% | 22,8% |
| Bản vẽ C1 Ninh Hải | 7 | 16.016 | 93,9% | 12,7% |
| HS TKTC THPT NhiChieu | 6 | 15.809 | 96,8% | 27,3% |
| Trụ sở CA xã Tân Phong | 4 | 11.371 | 94,6% | 12,0% |
| BV+DT MN Gia Loc | 2 | 11.006 | **62,3%** | 24,5% |
| 2. Công an An Lâm | 6 | 11.044 | 85,9% | 11,0% |
| Ban ve cong an Hiep Cat | 2 | 4.951 | 95,9% | 11,3% |

**751k/956k = 78,6% tổng chữ nằm ở 3 nhóm hạ tầng.** Chữ của chúng chủ yếu là tên mốc trắc địa, số hiệu cọc, nhãn tuyến — nên tỉ lệ "có đơn vị" chỉ 0,5–1,3%. Nhà dân dụng đọc tốt hơn hẳn (residual 62–70% ở 2 nhóm có bảng thống kê).

> ⚠ **Ba nhóm hạ tầng cần thước đo riêng.** Gộp chung làm mọi tỉ lệ mất nghĩa.

---

## 2. ⭐ XẾP HẠNG LOẠI DỮ LIỆU BỊ BỎ SÓT — danh sách công cụ nên xây

| # | Loại | Số lần | % hàng đợi |
|---|---|---:|---:|
| **1** | ⭐ **Đường kính thép** (`Ø10a150`, `2Ø14+2Ø14`, `4Ø10`, `Ø6A200`) | **17.908** | **55,1%** |
| 2 | Tiết diện (`AxB`) | 4.688 | 14,4% |
| 3 | Gán nhãn (`s=` `L=` `h=`) | 4.519 | 13,9% |
| 4 | Có đơn vị, **chưa khớp mẫu nào** | 3.601 | 11,1% |
| 5 | Độ dài (`X m/mm/cm`) | 1.061 | 3,3% |
| 6 | Khối lượng (`X kg/tấn`) | 447 | 1,4% |
| 7 | Diện tích (`X m2`) | 193 | 0,6% |
| 8 | Bước/khoảng (`@X`) | 40 | 0,1% |
| 9 | Thể tích (`X m3`) | 14 | 0,0% |
| 10 | Phần trăm (`X%`) | 4 | 0,0% |

**Mục #4 (3.601) đáng soi tiếp** — có thể lộ ra loại dữ liệu chưa ai nghĩ tới.

---

## 3. HAI PHÉP KIỂM ĐÃ CHẠY

### ✅ 17.908 chuỗi `Ø` **KHÔNG** trùng bảng thống kê thép — con số là thật

Trên `2. Ket Cau_NHA 9T.dxf`:

| | |
|---|---|
| `thong_ke_thep` đọc từ bảng | **279.679,6 kg** |
| Chuỗi `Ø` trong TEXT | **3.850** |
| Trong đó là residual | **3.850 = 100%** |

**Hai tập hoàn toàn tách rời:** bảng thống kê đọc từ **thuộc tính block**; các dòng gọi thép trên hình là **TEXT**, chưa bộ trích nào chạm tới. Kiểm chéo trên `2. KET CAU MONG- TH PHUNG VAN TRINH.dxf`: 183 chuỗi `Ø`, **183 residual (100%)**.

### ⚠ residual ĐẾM THIẾU phần đã đọc được bằng đường khác

`4. Thong ke thep SUA.dxf` thoạt nhìn rỗng — 27 đối tượng, 17 đoạn chữ, `thong_ke_thep` trả 0 kg. Nhưng thực tế:

> **8 `OLE2FRAME`**, bảng đầu **254 hàng × 32 cột**, tiêu đề *"BẢNG TÍNH CHI TIẾT KHỐI LƯỢNG CỐT THÉP"* — tool #27 `doc_bang_nhung` **đọc được**.

⇒ Đừng kết luận "file này không đọc được" chỉ vì residual/`thong_ke_thep` im lặng.

---

## 4. ⚠ NHÓM "CÓ ĐƠN VỊ" LÀ TÍN HIỆU MẠNH NHƯNG **KHÔNG TINH KHIẾT**

Đọc tay mẫu — bắt **đúng**:
```
- nhà lớp học 2 tầng 10 phòng ( s=533,91m2 ).     ← diện tích thật
- inox hộp 30x30x1.0 : 652.8 m = 600 kg           ← khối lượng thật
DN315-L=17.4M                                      ← chiều dài ống thật
2Ø12 · Ø6A200 · 5Ø6 · Ø16a200                      ← thép thật
BỐ TRÍ KHOẢNG CÁCH @750                            ← bước thép thật
```

Bắt **nhầm** (đã biết, đừng ngạc nhiên lại):

| Chuỗi | Thực chất |
|---|---|
| `V=1:100`, `H=1:500` | **Tỷ lệ bản vẽ**, không phải số liệu |
| `cút thép hàn DN100x45°` | `100x45` là **DN100 × GÓC 45°**, không phải tiết diện |
| `cho 1m3 nước, nước dùng để ngâm phải sạch…` | Ghi chú bảo dưỡng bê tông, `1m3` là văn nói |

⇒ **TUYỆT ĐỐI không tự động đổ nhóm này vào dự toán.** Phải qua **sổ số chưa gán** để người duyệt.

---

## 5. TÍN HIỆU ĐÃ ĐO CHO "SỐ TRẦN" — hai giả thuyết dễ nhất ĐÃ CHẾT

Mẫu 8 file / 1.114 số trần:

| Giả thuyết | Kết quả | |
|---|---|---|
| Tên layer cho biết nghĩa | Chỉ **~7%** trên layer mang nghĩa (`Caodo`, `CD_Dinh`, `CD_Day`). **76,8%** trên layer chung chung (`7`, `6text`, `Text`, `Chu`, `0`) | ❌ chết |
| Số bị mồ côi, không ngữ cảnh | **96,1%** có chữ ở gần (63,7% sát bên) | ❌ sai — tin tốt |
| Lấy nhãn gần nhất là ra nghĩa | Cặp thật hỏng: `12 ← "MẶT CẮT 12-12"`, `9 ← "MẶT BẰNG"`, `14 ← "MẶT CẮT 14-14"` | ❌ chết |

**Phát hiện kèm theo:** một phần đáng kể "số trần" **không phải dữ liệu** — chúng là số hiệu mặt cắt, số thứ tự bản vẽ, số bong bóng trục. Tức tỉ lệ số-trần đang **thổi phồng** vấn đề thật.

> 🐛 **BẪY ĐÃ TRẢ GIÁ:** lần đo đầu ra *"81,2% số cô độc"* — **SAI HOÀN TOÀN**. Bản ghi chữ (`Drawing.texts`) **KHÔNG có trường chiều cao chữ** (khoá chỉ gồm `handle/layer/text/vn/x/y`), nên thang `H` mặc định về `1.0` = 1 đơn vị bản vẽ. Phải chuẩn hoá bằng **trung vị khoảng cách láng giềng gần nhất giữa các đoạn chữ trong CHÍNH file đó**.

---

## 6. HƯỚNG GIẢI ĐÃ CHỐT — 4 tầng theo "cần bao nhiêu kiến thức xây dựng"

| Tầng | Nội dung | Cần kiến thức ngành? |
|---|---|---|
| **A — LOẠI TRỪ** | Cắt số không-phải-dữ-liệu bằng thuần cấu trúc: số trùng số trong tiêu đề gần đó (`12` ↔ `"MẶT CẮT 12-12"`); số trong bong bóng/vòng tròn; số lặp đều theo lưới (đánh số trục) | **Không chút nào** |
| **B — TRÍCH THEO CẤU TRÚC** ⭐ | Không hỏi *"số này nghĩa là gì"* mà hỏi *"số này nằm ở đâu, cạnh nhãn nào"* rồi **chép nhãn NGUYÊN VĂN**. Hệ thống **không bao giờ hiểu — chỉ trích và trích dẫn**. Tiền lệ: tool #36 (`mật độ ≥12 giá trị/hàng`, `cùng bậc` = dấu hiệu HÌNH HỌC) đạt **861/861 gán đúng** | Không |
| **C — NGƯỜI BIẾT NGHỀ** | TCVN/tài liệu ngành (dev đọc → `kienthuc.py`, trích nguồn) › thầy/chuyên gia › **đối tác** (quy ước riêng của chính họ) | Có — lấy từ **ngoài** |
| **D — SỔ SỐ CHƯA GÁN** | Mỗi file xuất thêm bảng `giá trị · handle · layer · nhãn gần nhất · đã phân loại?` | Không |

**Cách hỏi đối tác (tầng C) — CÂU ĐÓNG kèm ảnh khoanh vùng, KHÔNG hỏi mở:**
> *"Con số `2.21` khoanh đỏ nằm cạnh nhãn `II-246`. Nó là: (a) cao độ tự nhiên (b) cao độ thiết kế (c) khác — xin ghi rõ."*

Hỏi kiểu này thì **dev không cần biết xây dựng để hỏi**, và câu trả lời **kiểm chứng được**. Hỏi mở *"cái này là gì?"* thì không đánh giá nổi câu trả lời.

---

## 7. ⭐ VỀ YÊU CẦU "TẤT CẢ SỐ LIỆU PHẢI ĐỌC ĐÚNG" (user nêu 2026-08-06)

> **"Không bỏ qua" ≠ "đọc được hết".** Cái nguy hiểm không phải *bỏ sót*, mà là **bỏ sót ÂM THẦM**.

Hệ đọc được 100% là không tồn tại. Nhưng hệ **đọc được X% và tự khai ra phần còn lại là gì, nằm ở đâu** thì **không con số nào biến mất** — mọi số đều có mặt trong một trong hai danh sách.

⇒ Sản phẩm bắt buộc: **sổ số chưa gán** (tầng D) — **đếm được, giảm dần được**. Với dự toán, đây mới là bảo đảm thật, chứ không phải lời hứa *"đọc được hết"*.

---

## 8. VIỆC TIẾP THEO (theo thứ tự đáng làm)

1. **Đọc thép gọi tên trên hình** — 55,1% hàng đợi. Chuỗi có cấu trúc rõ (`số thanh + Ø + đường kính + a + khoảng cách`) nên **tách chuỗi là phần DỄ**; phần KHÓ là **gán vào đúng cấu kiện** — lại là bài toán ghép nhãn↔giá trị (`[[project-nut-that-recall-ghep-nhan-gia-tri]]`).
2. **Tầng A (loại trừ)** — đo xem cắt được bao nhiêu % số trần. Rẻ, offline, không cần kiến thức ngành.
3. **Soi nhóm "có đơn vị, chưa khớp mẫu"** (3.601) để tìm loại dữ liệu chưa biết.
4. **Thước đo riêng cho hạ tầng** — 3 nhóm chiếm 78,6% chữ nhưng đặc tính khác hẳn.
5. **Sổ số chưa gán** (tầng D).
