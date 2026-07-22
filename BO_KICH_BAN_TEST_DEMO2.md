# BỘ KỊCH BẢN TEST DEMO 2 (kèm đáp án) — file "1. Kien truc CT-A.dwg"

> **Cách dùng:** mở demo 2 → tải file `1. TKBVTC kien truc CT-A 091124.dwg` (file cửa đối tác hay dùng)
> → hỏi từng câu ở cột **Câu hỏi** → so câu trả lời của demo với cột **Đáp án chuẩn**.
> Đáp án chuẩn = số THẬT đọc từ chính file (mình đã kiểm chứng độc lập). Bạn không cần mở AutoCAD.

---

## ⭐ NHÓM 0 — ĐÚNG 2 CÂU ĐỐI TÁC TỪNG CHÊ (test đầu tiên!)

| # | Câu hỏi | Đáp án chuẩn | Ghi chú |
|---|---|---|---|
| 0.1 | **Số lượng cửa đi D1 là bao nhiêu?** | **24 bộ** | ✅ **ĐÃ FIX** — demo 2 trả "24 cho cửa d1 [67CDF]" (đã kiểm live). Demo 1 từng trả "không ghi sẵn" ❌ |
| 0.2 | **Tổng diện tích cửa D1?** | ⚠️ 1 bộ 1300×2700mm = 3,51m²; ×24 = **84,24 m²** | ❌ **Demo 2 TỪ CHỐI** ("chưa hỗ trợ tính diện tích"). Là **TÍNH TOÁN (takeoff) = giai đoạn 2** — xem mục ⚠️ CUỐI. |

---

## A — TỔNG QUÁT (dễ, để làm quen)

| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| A1 | Có bao nhiêu layer? | **141 layer** |
| A2 | File có bao nhiêu đối tượng? | **8024 đối tượng** |
| A3 | Có bao nhiêu đường kích thước? | **2355** |
| A4 | Thống kê các loại đối tượng | DIMENSION 2355 · LWPOLYLINE 1723 · INSERT 1438 · TEXT 1000 · LINE 618 · MLINE 307 · HATCH 288 · LEADER 169 · ARC 43 · CIRCLE 30 · MTEXT 25... |
| A5 | Liệt kê các sheet (bản vẽ con) | ~73 nhãn tiêu đề (mặt bằng, mặt đứng, mặt cắt, chi tiết cửa, chi tiết cầu thang...) — demo nêu rõ "có thể ≠ số tờ in" |
| A6 | Công trình này là gì, mấy tầng, mấy phòng? | **Nhà lớp học 2 tầng 8 phòng** (giai đoạn 1) |

## B — SỐ LƯỢNG CỬA (trọng tâm đối tác)

| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| B1 | Cửa S1 bao nhiêu bộ? | **16 bộ** |
| B2 | Cửa SW bao nhiêu bộ? | **16 bộ** |
| B3 | Cửa DW bao nhiêu bộ? | **8 bộ** |
| B4 | Cửa D2 bao nhiêu bộ? | **8 bộ** |
| B5 | Cửa CM1 bao nhiêu bộ? | **1 bộ** |
| B6 | Liệt kê tất cả các loại cửa và số lượng | D1=24, S1=16, SW=16, DW=8, D2=8, CM1=1 |
| B7 | **Tổng tất cả các loại cửa là bao nhiêu bộ?** | **73 bộ** (24+16+16+8+8+1) |
| B8 | So sánh số lượng cửa D1 và cửa D2 | D1=24, D2=8 (D1 nhiều hơn 16 bộ) |

## C — CHI TIẾT CỬA / CẤU KIỆN

| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| C1 | Cửa D1 có kích thước bao nhiêu? | Demo 2 trả kích thước **profile nhôm** (khung 54,8×66mm, cánh 54,8×87mm) từ ghi chú. ⚠️ Kích thước phủ bì **1300×2700mm** nằm ở ĐƯỜNG KÍCH THƯỚC cạnh hình — demo 2 **chưa gắn được vào "cửa D1"** (giai đoạn 2) |
| C2 | Cửa D1 dùng vật liệu và phụ kiện gì? | Cửa nhôm hệ **PMA XF55**, kính dán an toàn **6.38mm**, khung bao 54.8×66mm dày 2mm; phụ kiện: 01 bộ khóa đa điểm, **06 bộ bản lề 3D**, 01 bộ chốt cánh |
| C3 | Có bao nhiêu loại lan can (LC)? | 8 loại: LC1=5, LC2=4, LC3=1, LC4=8, LC5=1, LC6=2, LC7=6, LC8=1 |
| C4 | Vách kính VK1 bao nhiêu bộ? | **4 bộ** |

## D — THÉP

| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| D1 | Tổng khối lượng thép tròn của công trình? | **564,8 kg** (chỉ cốt thép tròn) |
| D2 | Thép Ø22 có bao nhiêu thanh, nặng bao nhiêu kg? | **20 thanh, 298,4 kg** |
| D3 | Liệt kê thép tròn theo từng đường kính | Ø22:298.4kg · Ø8:96.4kg · Ø16:68.5kg · Ø12:66.8kg · Ø10:23.6kg · Ø6:11.1kg |
| D4 | Bảng thống kê thép hình cầu thang thoát hiểm tổng bao nhiêu? | ~**2163 kg** *(lưu ý: demo có thể trả tổng cả bảng thép hình 3545.9kg — xem mục hạn chế)* |

## E — VẬT LIỆU / GIÁ TRỊ GHI SẴN (test đọc số trong ghi chú)

| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| E1 | Độ dốc mái bao nhiêu? | **i = 32%** và **i = 23%** |
| E2 | Diện tích lát gạch 600×600 là bao nhiêu m²? | **591 m²** và **545 m²** |
| E3 | Mác bê tông móng là bao nhiêu? | Móng/giằng **B20 (mác 250)** đá 1×2; lót móng **mác 150** đá 2×4 |
| E4 | Liệt kê các loại mác bê tông trong hồ sơ | Mác 250/B20, mác 200, mác 150, vữa mác 75 |

## F — TRỰC QUAN HÓA (điểm mới của demo 2)

| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| F1 | **Đánh dấu cửa D1 trên bản vẽ giúp tôi** | Ra **ảnh khoanh đỏ** vị trí nhãn cửa D1 |
| F2 | Khoanh đỏ cửa S1 trên bản vẽ | Ra ảnh khoanh đỏ vị trí S1 |

## G — BẪY CHỐNG BỊA (⭐ quan trọng — test nó KHÔNG bịa)

| # | Câu hỏi | Đáp án chuẩn (demo phải làm ĐÚNG thế này) |
|---|---|---|
| G1 | Công trình dài bao nhiêu mét? | **PHẢI TỪ CHỐI**: "chưa hỗ trợ suy ra kích thước tổng thể từ hình học" (KHÔNG được lấy số 58800mm làm chiều dài) |
| G2 | Cao độ tầng 2 là bao nhiêu? | **PHẢI TỪ CHỐI** (không lấy +3.600 làm cao độ tầng) |
| G3 | Công trình có bao nhiêu thang máy? | **PHẢI nói KHÔNG CÓ** (không bịa) |
| G4 | Có bao nhiêu cửa gỗ lim? | **PHẢI nói KHÔNG CÓ** |
| G5 | Chữ "cửa D1" xuất hiện bao nhiêu lần, có phải số bộ cửa không? | Phân biệt rõ: **số lần xuất hiện chữ ≠ 24 bộ** (số bộ thật = 24) |

---

## ⚠️ MỤC QUAN TRỌNG — CÂU DEMO 2 CHƯA LÀM ĐƯỢC (nói thẳng để không bị bất ngờ)

Đây là **giai đoạn 2 (tính toán/bóc tách)** — demo 2 hiện tại **CHỈ ĐỌC số có sẵn, CHƯA tính toán**:

| Câu hỏi | Vì sao chưa làm được | Cần gì |
|---|---|---|
| **Tổng diện tích cửa D1** (đối tác muốn) | = rộng × cao × SL = 1.3×2.7×24 = **84,24 m²** — là **phép TÍNH**, demo 2 đọc được 1300×2700 nhưng chưa nhân ra tổng | Giai đoạn 2 (takeoff) |
| Thể tích bê tông, diện tích ván khuôn | Phải tính từ hình học | Giai đoạn 2 |
| Tổng diện tích tất cả cửa | Phải tính rộng×cao×SL từng loại rồi cộng | Giai đoạn 2 |

→ **Nếu đối tác hỏi "diện tích cửa D1", demo 2 sẽ đọc được kích thước 1300×2700 nhưng KHÔNG tự tính 84,24m².** Đây là ranh giới đã thống nhất (demo 2 = đọc; tính toán = giai đoạn sau).

---

## 🔍 VỀ LO NGẠI "CÂU NGOÀI KỊCH BẢN" (rất đúng!)

Bạn lo đúng: demo 1 test xong hết nhưng đối tác hỏi câu lạ vẫn lòi lỗi. Mình đã cố phòng điều này:
- Đã test **198 câu đối kháng** (bẫy, câu lạ, font lỗi, nhiều phần, tiếng Anh) — không chỉ kịch bản đẹp.
- **Lõi đọc số = tất định, đúng 100%** → câu nào ánh xạ đúng công cụ thì số luôn chính xác.

**Các "điểm yếu" đã biết (để bạn không bị bất ngờ):**
1. Câu **quá nhiều phần cùng lúc** → đôi khi model trả lời thiếu 1 ý (không còn "bỏ cuộc" nữa, nhưng có thể sót ý phụ).
2. Câu hỏi **TÍNH TOÁN** (diện tích/thể tích/khối lượng bê tông) → chưa làm (giai đoạn 2).
3. Thép theo **hạng mục con** ("thép cầu thang") → trả tổng cả bảng thép hình.
4. Đánh dấu **mã cấu kiện KHÔNG tồn tại** → có thể khoanh nhầm text gần giống.

→ Nếu đối tác hỏi trúng mấy điểm này, **báo mình câu cụ thể**, mình vá tiếp — đây là cách chắc nhất (vá theo câu thật của đối tác, không đoán trước hết được).

---
---

# PHẦN 2 — BỘ TEST FILE KẾT CẤU ("2. KetCau CT-A.dwg")

> Tải file kết cấu lên demo 2 rồi hỏi. Đây là file **thép 67 tấn, cột/dầm/đài/cọc** — kiểm đa dạng domain khác kiến trúc.

## K-A — Tổng quát
| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| KA1 | Có bao nhiêu layer? | **126 layer** |
| KA2 | File có bao nhiêu đối tượng? | **21.077 đối tượng** |
| KA3 | Có bao nhiêu đường kích thước? | **3305** |

## K-B — Thép (trọng tâm file kết cấu)
| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| KB1 | **Tổng khối lượng thép của công trình?** | Thép tròn **67.370,7 kg** (≈67,4 tấn) + thép hình ~389 kg (nêu riêng, KHÔNG gộp) |
| KB2 | Thép Ø10 bao nhiêu thanh, bao nhiêu kg? | **4817 thanh, 25.752,6 kg** |
| KB3 | Đường kính thép nào NẶNG nhất (nhiều kg nhất)? | **Ø10** (25.752,6 kg) — KHÔNG phải Ø22 (bẫy: Ø22 nặng/thanh nhưng tổng Ø10 lớn nhất) |
| KB4 | Đường kính thép nào có NHIỀU THANH nhất? | **Ø6** (18.072 thanh, nhưng chỉ 3531,6 kg) |
| KB5 | Thép Ø18 bao nhiêu kg? | **13.379,9 kg** (997 thanh) |

## K-C — Số lượng cấu kiện
| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| KC1 | Tổng số cọc là bao nhiêu? | **131 cọc** (bản vẽ ghi "TỔNG SỐ CỌC: 131 CỌC, trong đó 3 cọc thí nghiệm") |
| KC2 | Đài cọc ĐC-3 có bao nhiêu? | **25** (ghi "ĐC-3 (SL-25)") |
| KC3 | Cột C-1 có số lượng bao nhiêu? | **27** (ghi "C-1 (SL: 27)") — đây là số đài/cọc dưới cột C1 |
| KC4 | Đài ĐC-1, ĐC-2 mỗi loại bao nhiêu? | ĐC-1=19, ĐC-2=10 |

## K-D — Tiết diện / vật liệu (chi tiết)
| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| KD1 | Cột C1 có tiết diện bao nhiêu? | **220×220 mm** |
| KD2 | Cột C4 tiết diện bao nhiêu? | ⚠️ Có **2 tiết diện: 220×500 và 220×400** (demo nên nêu cả hai) |
| KD3 | Mác bê tông cột là bao nhiêu? | **B20 (mác 250#)**, đá 1×2, đổ tại chỗ |
| KD4 | Thép Ø≥10 dùng loại gì, Ø<10 dùng loại gì? | Ø≥10: **CB300-V** (Rs=260MPa); Ø<10: **CB240-T** (Rs=210MPa) |

## K-E — Bẫy chống bịa (file kết cấu)
| # | Câu hỏi | Đáp án chuẩn |
|---|---|---|
| KE1 | Cao độ tầng 2 / tầng mái bao nhiêu? | **PHẢI TỪ CHỐI** (không lấy +3.600/+7.200/+10.800 làm cao độ tầng) |
| KE2 | Cột C1 cách cột C2 bao xa? | **PHẢI TỪ CHỐI** (không đọc khoảng cách 2 điểm) |
| KE3 | Đánh dấu cột C1 trên bản vẽ | Ra ảnh khoanh đỏ vị trí C1 (⚠️ có thể khoanh cả nhãn thép gần giống — điểm yếu đã biết) |

---

# PHẦN 3 — CÂU HỎI "KIỂU ĐỐI TÁC" / NGOÀI KỊCH BẢN (săn lỗi ẩn)

> Các cách hỏi **lạ, tự nhiên, đánh đố** — giống đối tác hỏi thật, để lộ lỗi ẩn (như bạn lo).

| # | Câu hỏi (kiểu tự nhiên) | Đáp án chuẩn / hành vi đúng |
|---|---|---|
| X1 | "cửa d1 mấy bộ vậy" (viết thường, cụt) | 24 bộ (phải hiểu dù viết tắt) |
| X2 | "cho anh xin số lượng cửa các loại" | Liệt kê D1=24, S1=16, SW=16, DW=8, D2=8, CM1=1 |
| X3 | "bản vẽ này của công trình gì" | Nhà lớp học 2 tầng 8 phòng |
| X4 | "có cửa nào bằng gỗ không" | Không có (cửa nhôm PMA XF55) — không bịa |
| X5 | "tính giúp anh khối lượng bê tông" | Chưa hỗ trợ tính (giai đoạn 2) — nói thẳng, không bịa |
| X6 | "thép phi 16 nằm ở đâu, bao nhiêu" | Ø16: (kiến trúc 68.5kg/22 thanh) — trả số + có thể highlight |
| X7 | "file này có mấy bản vẽ" | ~73 nhãn tiêu đề (nêu rõ có thể ≠ số tờ in) |
| X8 | "đọc giúp anh ghi chú chung" | Trích các dòng ghi chú (mác BT, thép, vật liệu...) |
| X9 | "windows S1 how many?" (tiếng Anh) | Cửa/cửa sổ S1 = 16 bộ (hiểu tiếng Anh) |
| X10 | "cửa D1 với cửa D2 cái nào nhiều hơn" | D1 (24) nhiều hơn D2 (8) — 16 bộ |
| X11 | "tổng cộng bao nhiêu m2 sàn" | Chưa hỗ trợ tính diện tích sàn (giai đoạn 2) — không bịa |
| X12 | "có bao nhiêu phòng vệ sinh / wc" | Tra text WC nếu có; không có thì nói không tìm thấy |

**Nếu bất kỳ câu nào demo trả SAI hoặc bịa → chụp lại gửi mình → vá ngay.**

---
---

# PHẦN 4 — GIAI ĐOẠN 2: TÍNH TOÁN (TAKEOFF) — đã kiểm live, khớp 100%

> Đây là tính năng MỚI: hỏi TÍNH một đại lượng. **Đủ số liệu → tính luôn (kèm sơ đồ + nguồn); thiếu → hiện có/thiếu → bạn nhắn số thiếu → tính tiếp.** Mọi số kèm nguồn + cờ "chưa chắc" (nếu lấy theo vị trí).

## 4A — Diện tích cửa (file KIẾN TRÚC) — đối tác muốn nhất
| Câu hỏi | Đáp án chuẩn (đã kiểm) |
|---|---|
| **Tổng diện tích cửa đi D1?** | **84,24 m²** (1300×2700×24) — kèm "kích thước lấy theo vị trí, chưa chắc 100%" |
| Diện tích cửa S1? | **34,56 m²** (1200×1800×16) |
| Diện tích cửa CM1? | **0,64 m²** (800×800×1) |

## 4B — Thể tích bê tông (file KẾT CẤU) — có màn "nhập bù"
| Câu hỏi | Đáp án chuẩn |
|---|---|
| Thể tích bê tông cột C1? | Báo **đã có** cạnh 220×220 + SL 27, **thiếu chiều cao** → mời cấp |
| *(nhắn tiếp)* "chiều cao cột là 3.6m" | **4,704 m³** (nhớ đang tính C1) |
| Thể tích bê tông cột C4, chiều cao 3.6m | **9,504 m³** + cảnh báo "C4 có 2 tiết diện (220×500 và 220×400)" |
| Thể tích bê tông dầm DR-3? | Đã có 220×300 + SL, **thiếu chiều dài** (KHÔNG lấy "L=9.82m" — đó là chiều dài THÉP, không phải nhịp) |
| *(nhắn tiếp)* "dầm dài 4m" | **0,264 m³** |
| Diện tích ván khuôn cột C1 với chiều cao 3.6m | **85,54 m²** |

## 4C — Bẫy takeoff (test không bịa)
| Câu hỏi | Hành vi đúng |
|---|---|
| Tính diện tích cửa gỗ lim GL9? (không có) | Báo **KHÔNG TÌM THẤY** cấu kiện GL9 trong bản vẽ — **KHÔNG hỏi thông số, KHÔNG bịa số** |
| Tính khối lượng bê tông toàn công trình | Cần bóc từng cấu kiện — không có 1 số tổng bịa |
| Công trình dài bao nhiêu? | Vẫn TỪ CHỐI (kích thước tổng thể ≠ takeoff cấu kiện) |

**Đại lượng đã hỗ trợ tính:** diện tích cửa · thể tích BT cột/dầm/sàn/móng · ván khuôn cột/dầm. Các đại lượng khác (đào đắp, xây/trát...) hoặc thiếu số liệu trong file → hệ sẽ báo cần bạn cấp thêm.
