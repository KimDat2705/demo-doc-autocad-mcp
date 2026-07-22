# PHƯƠNG ÁN NÂNG CẤP DỰ ÁN — bản HỢP NHẤT (đã khử trùng lặp) · 2026-07-22

> Gộp **góp ý các thầy (V1–V4)** + **nghiên cứu đối sánh 41 nguồn (P1–P3)** thành MỘT danh sách duy nhất.
> Nguyên tắc: **mỗi vấn đề = 1 mục = 1 hướng tối ưu duy nhất** — không để "1 vấn đề 2 giải pháp" gây xung đột khi code.
> Chỗ thầy và tôi trùng vấn đề nhưng khác giải pháp → đã nghiên cứu chọn 1 hướng, ghi rõ **CHỌN gì / BỎ gì / vì sao**.
> Nguồn chi tiết: `NGHIEN_CUU_DOI_SANH_KIEN_TRUC.md`. Đã kiểm chứng trên code thật.

---

## PHẦN A — BẢNG ĐỐI CHIẾU & KHỬ TRÙNG LẶP

| Vấn đề chung | Ý của THẦY | Ý nghiên cứu của TÔI | Quan hệ | → Gộp thành |
|---|---|---|---|---|
| Quy ước layer mỗi firm một kiểu | V1a từ điển động · V1b popup xác nhận | P3 kênh học (LIVE) · P1.6 F-B web UI | **Trùng** | **U1** |
| Đọc đúng số theo bối cảnh không gian | V1c "train LLM ngữ cảnh" | P2 zone phân vùng (code tất định) | **Xung đột PP** | **U2** |
| Bảng Excel nhúng OLE (19/65 file) | V2 OCR ảnh | P1.1 đọc binary OLE2FRAME | **Xung đột PP** | **U3** |
| SME đối chiếu — test theo hạng mục | V3a chia test móng/cửa | P1.7 gói SME theo hạng mục | **Trùng** | **U4** |
| Đối chiếu bóc tay + đủ bản vẽ | V3b sưu tầm bóc tay | P3 corpus đa firm (giaxaydung.vn) | **Bổ trợ** | **U5** |
| File lớn quá tải RAM | V4 lọc layer rác trước | P2 iterdxf streaming | **Bổ trợ** | **U6** |

**2 phương pháp của thầy bị BỎ (ghi lại để không ai vô tình tái dùng lúc code):**
- **V1c "train/huấn luyện LLM phân tích ngữ cảnh"** → BỎ. Dự án đã chốt **KHÔNG train model**; và LLM đọc số có rủi ro bịa
  (bằng chứng Enginuity: VLM đọc nội dung bản vẽ F1 chỉ 0.03–0.18). Giữ **mục tiêu** ngữ cảnh không gian nhưng làm bằng
  **luật code tất định** (U2) — kết quả tương đương, kiểm chứng được từng bước.
- **V2 "OCR làm đường chính"** → HẠ xuống **fallback tầng 2**. OCR sai ký tự (8↔B, 0↔O) = "sai-tự-tin", tối kỵ với KPI ~0% bịa.
  Đường chính đọc **binary** cho số chính xác tuyệt đối (U3).

**Kết luận thẩm định:** cả **4/4 vấn đề thầy nêu đều ĐÚNG** bài toán thật (2 vấn đề trùng khít số liệu đã đo). Chỉ điều chỉnh
**phương pháp** ở 2 chỗ (V1c, V2) sang hướng kỹ thuật bền hơn cùng mục tiêu — không phải thầy sai đề.

---

## PHẦN B — DANH SÁCH MỤC HỢP NHẤT (mỗi mục 1 hướng duy nhất)

### Nhóm 1 — mục CHUNG (thầy + tôi cùng nêu)

**U1 · Quy ước động + popup xác nhận trên web** — *gộp V1a+V1b + P1.6 + P3(LIVE)*
Lõi "từ điển động" ĐÃ CHẠY LIVE (`hoc_quy_uoc`/`thu_hoi_quy_uoc`, tools_core.py 1075–1131: học theo phiên, fail-closed,
không lưu số). **Không code lại lõi**; chỉ còn thiếu **UI popup web** (đối tác dạy "CH = cửa đi hay cao độ?" → chọn 1-click).
*Ví dụ 'CH' của thầy là bug CÓ THẬT đã vá (`'CH - 2.700'`→ đọc nhầm cao độ −2.7).* **CẦN USER CHỐT** (quyết định F-B treo).

**U2 · Ngữ cảnh không gian = chỉ mục ZONE tất định** — *gộp V1c(bỏ train) + P2-zone*
Gom các tín hiệu không gian đang nằm rải (band toạ độ, section/door/qty index, layer thép, hướng dim) thành **chỉ mục thứ 9
tường minh**: mỗi TEXT → {khung tên / bảng / ghi chú / khu vẽ} + nhãn tin cậy, dựa trên paperspace-vs-modelspace + bounding box
+ tên layer. Đây là chỗ giải "'2.700' trong block chữ nhật = thông thuỷ, không phải cao độ" — bằng **hình học + layer, không train LLM**.

**U3 · Đọc bảng OLE nhúng — 3 tầng ưu tiên cứng** — *gộp V2 + P1.1* *(chi tiết cây quyết định ở Phần C)*
Tầng 1 **BINARY** (chính) → Tầng 2 **OCR** (fallback, chỉ khi binary không có data) → Tầng 3 **CẢNH BÁO** (như hiện nay).
**Bắt buộc probe 19 file OLE thật trước khi code.**

**U4 · Gói SME test theo hạng mục** — *gộp V3a + P1.7*
Chia test theo hạng mục (móng / cửa / thép…) trên corpus hiện có; xuất Excel kèm handle + ảnh khoanh đỏ để người chấm tra
ngược từng số; **công bố sai số theo TỪNG hạng mục** (không gộp chung); lệch → thành test case mới. Là bước Go-to-market GĐ4/P5.

**U5 · Đối chiếu bóc tay + thu thập corpus đa firm** — *gộp V3b + P3-corpus*
(1) U4 cấp hạ tầng chấm; (2) nguồn đối chiếu = **bảng bóc TAY** của kỹ sư QS; (3) kênh thu thập = **nhận lời thầy test thật** +
diễn đàn **giaxaydung.vn** xin bản vẽ ≥3 firm + dataset **FloorPlanCAD**. Gỡ đúng nút thắt số 1 (thiếu bản vẽ đa firm + người chấm).

**U6 · Giảm RAM: iterdxf streaming + lọc layer rác** — *gộp V4 + P2-iterdxf*
GIỮ ý thầy về **danh sách lọc** (blacklist HATCH mặt cắt / trang trí / cây / xe; chỉ lấy TEXT/MTEXT/INSERT/ATTRIB/DIMENSION/LINE).
SỬA cách làm: phải lọc **trong lúc đọc STREAM** bằng `iterdxf` (từng entity) — vì `ezdxf.readfile()` nạp cả file trước nên
"load-xong-mới-lọc" **không giảm** đỉnh RAM. Kích hoạt khi `size×7 > RAM budget`; stream chỉ thấy modelspace → tự khai giới hạn.
**Ảnh hưởng trực tiếp quyết định nâng RAM Render đang HELD** (có thể không cần lên gói đắt).

### Nhóm 2 — mục ĐỘC LẬP (chỉ nghiên cứu của tôi; thầy không nêu → không trùng, không xung đột)

| ID | Việc | Ưu tiên |
|---|---|---|
| **I1** | **Guard validate HANDLE** theo tập-đã-cấp (vá lỗ model chép/bịa handle — guard hiện chỉ check SỐ) | P1 · S |
| **I2** | **Excel chuẩn dự toán VN**: sheet `Tien_luong` phẳng 6 cột + cột Diễn giải công thức + công thức Excel sống + **không ôm đơn giá** + README định vị | P1 · S–M |
| **I3** | **Bounds-check vật lý + ratio ngành** (thép Ø6–51, tầng 1.8–12m; kg thép/m³ BT…) → nghi_ngo/canh_bao, không sửa số | P1 · S |
| **I4** | **Ghép bảng VẼ-TRỰC-TIẾP trong CAD** (LINE+TEXT): lưới từ đường kẻ (pdfplumber-lines) + suy cột rãnh-x (Camelot). ⚠ **KHÁC U3**: U3 là bảng Excel NHÚNG (OLE); I4 là bảng được VẼ bằng nét trong bản vẽ — 2 loại bảng khác nhau, cả hai đều cần | P1 · M |
| **I5** | Tool #27 query phân trang + #28 `dem_theo_block` (recall) | P2 · M |
| **I6** | Detector "vùng có mực chưa phủ" → cảnh báo vùng nghi bỏ sót | P2 · M |
| **I7** | Guard cờ "câu không cần nguồn" (giảm từ-chối-oan) | P2 · S |
| **I8** | UI panel màu trạng thái 8 chỉ mục sau upload + màu per-field + audit trail | P2 · S–M |
| **I9** | Tách SYSTEM_PROMPT = luật-bất-biến / quy-ước-VN có version | P2 · S |

### Nhóm 3 — roadmap xa (cần điều kiện)
Kênh **vision** (luật CHỐT: VLM chỉ ĐỊNH VỊ, cấm đọc số) + SoM audit đo trước · **router câu hỏi mẫu** →
chuỗi tool tất định · **guard claim phi-số** (triplet RefChecker) · **pin-to-accept HITL** (dùng chung cho cả nhánh OCR ở U3) ·
đẩy parse về local + upload chỉ mục JSON · LibreDWG plan B converter cho nhánh public.

---

## PHẦN C — 2 XUNG ĐỘT PHƯƠNG PHÁP ĐÃ GIẢI DỨT ĐIỂM

### U3 — Đọc OLE: cây quyết định DUY NHẤT (không chạy binary & OCR song song cho cùng 1 blob)
```
B0  Phát hiện OLE2FRAME (modelspace + paperspace) — ĐÃ CÓ, giữ. Mỗi OLE chạy độc lập, fail-soft.
B1  Nối bytes tag 310 → blob.        rỗng/thiếu (ODA strip / OLE LINKED) ──────────────► B5 (OCR)
B2  Kiểm magic:  D0CF11E0 (CFBF) → B3 │ PK.. (.xlsx) → openpyxl = EXACT │ WMF/EMF (chỉ ảnh) → B5 │ lạ → B6
B3  CFBF → olefile:  có 'Workbook'/'Book' → xlrd = EXACT │ 'Package'/.xlsx → openpyxl = EXACT │ chỉ ảnh → B5
B4  ✅ TẦNG 1 (CHÍNH): trả bảng, nguồn 'ole:<handle>:<sheet>:<R,C>'; mặc định cờ nghi_ngo tới khi qua bounds-check(I3);
        không auto vào tổng; handle qua guard(I1).
B5  ⚠ TẦNG 2 (OCR FALLBACK — chỉ tới đây khi B1/B2/B3 không có stream data): render ảnh → OCR → mọi số CỜ nghi_ngo BẮT BUỘC
        + detector ký tự nhập nhằng (8/B,0/O,1/l) → token nghi thì HẠ thành cảnh báo; qua grounding guard; KHÔNG vào tổng;
        đính ảnh khoanh để người xác nhận (pin-to-accept).
B6  🛑 TẦNG 3 (TERMINAL): cả 2 thất bại → giữ nguyên `_gan_canh_bao_nhung`: "có N đối tượng nhúng, máy KHÔNG đọc được"
        (≠ "bản vẽ không có"), không phát số.
```
**OCR thực sự cần cho 4 ca** (đều là ca binary không có data): OLE LINKED · dán-dạng-hình (chỉ WMF/EMF) · ODA cắt tag 310 ·
blob không CFB nhưng render được. **Probe 19 file quyết định OCR có phải nhánh chạy thường hay chỉ bảo hiểm hiếm dùng** — không đoán trước.

### U2/U1 — Ngữ cảnh & quy ước: kiến trúc 4 tầng MỘT CHIỀU (b → c → a, cấm back-edge)
```
extract tất định ──► (b) ZONE/tin-cậy   ──► residual+mơ hồ ──► (c) POPUP web  ──► user chọn ──► (a) KÊNH HỌC (rule/phiên)
   [nền chống bịa]     U2 · code tất định                       U1 · F-B (chốt)                   P3 LIVE · chua_chac
                                                                                                        │
                                              [dev quan sát WORM log ≥3 nguồn] ◄── codify thủ công ──────┘  (offline, không runtime)
```
**Luật ranh giới (để 3 cơ chế không đè nhau lúc code):**
- **(b) là nguồn DUY NHẤT** sinh nhãn tin cậy tự động (hình học+layer); không tự hỏi popup, không tự ghi học.
- **(c) popup CHỈ hỏi cái (b) KHÔNG chắc** (residual) — cấm hỏi lại cái đã phân loại chắc (tránh hỏi hiển nhiên); đầu ra chỉ 1 đích = ghi vào (a).
- **(a) là nơi DUY NHẤT** lưu quy ước user xác nhận, chỉ theo phiên, luôn `chua_chac`, không vào tổng/Excel. Thành vĩnh viễn CHỈ qua dev codify ≥3 nguồn.
- **Ưu tiên khi mâu thuẫn**: số engine đọc CHẮC (b) THẮNG quy ước phiên (a) — đã cưỡng chế trong code (`hoc_quy_uoc` từ chối anchor đã-đọc).
- **Tách đích ghi**: (b)→index tất định · (a)→`hoc_phien` · (c)→không sở hữu state (chỉ là view+relay). Không vùng nào ghi vào vùng khác.

---

## PHẦN D — THỨ TỰ THI CÔNG & VIỆC CẦN QUYẾT

**Thứ tự đề xuất** (mỗi việc: probe → design → red-team 2 tầng → gate 22/22 + không regress 850 test):
1. **U3-probe** (19 file OLE, ~30′ offline) — chốt ROI việc recall lớn nhất
2. **I1** (validate handle, S) · **I3** (bounds-check, S) — vá guard rẻ, độc lập
3. **U6** (iterdxf + lọc layer) — nền tảng + gỡ quyết định RAM HELD
4. **U2** (zone index) — nền cho popup + giải ngữ cảnh
5. **I2** (Excel VN) · **I4** (ghép bảng native)
6. **U4** (gói SME test) → **U5** (thu thập bóc tay + corpus)
7. *(chờ user chốt)* **U1** (F-B popup web UI)

**Cần user / thầy quyết:**
1. **U1 (F-B)** — đưa kênh học lên web UI popup? (thầy V1 nghiêng mạnh CÓ; lõi P3 đã LIVE, chỉ thêm route+UI). *← chặn U1.*
2. **U5** — thầy cấp thêm **bản bóc tay** đối chiếu nếu có; xác nhận thầy tham gia test hạng mục (U4).
3. **HELD RAM Render** — hoãn chốt gói tới sau U6.
