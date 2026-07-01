# KẾ HOẠCH GIAI ĐOẠN 2 — DEMO 2 (MCP + AutoCAD/ezdxf)
### Engine tính toán takeoff dựa trên số liệu CÓ SẴN trong bản vẽ

> Lập 2026-06-30. Nghiên cứu grounded vào 3 file mẫu thật + code demo 2. Có đánh dấu thẳng thắn chỗ khó/chưa chắc.

---

## PHẦN 1 — ĐỊNH NGHĨA (bám spec của user)

**Giai đoạn 1 (đã xong):** chỉ ĐỌC số CÓ SẴN — số lượng (`qty_index` từ "SL=/số lượng: N bộ"), thép (bảng thống kê block `TK_*`), kích thước (`DIMENSION`), text/layer/block, mác BT/độ dốc (ghi chú text).

**Giai đoạn 2 (cần làm):** cài các **CÔNG THỨC** để TÍNH dựa trên số liệu có sẵn. Khi đối tác hỏi 1 đại lượng cần tính:
- **ĐỦ input trong file → TÍNH LUÔN** + "sơ đồ hệ thống tính" (công thức + giá trị + nguồn + handle từng input).
- **THIẾU input → KHÔNG bịa.** Hiển thị: (a) input ĐÃ CÓ (giá trị+nguồn+handle), (b) input CÒN THIẾU → đối tác cấp số thiếu → hệ tính tiếp.

**4 luật chống bịa:** (1) CODE lấy input + CODE tính, LLM chỉ điều phối; (2) thiếu input → báo thiếu (bình thường, không phải lỗi); (3) mọi input có nguồn+handle+độ tin cậy; (4) minh bạch từng bước.

---

## PHẦN 2 — CATALOG CÔNG THỨC ƯU TIÊN (độ khả thi chấm trên file mẫu THẬT)

| # | Đại lượng | Công thức | Khả thi trên file mẫu |
|---|---|---|---|
| 1 | **Thép các loại** | tổng theo Ø từ bảng thống kê | 🟢 **TÍNH NGAY** — `thep_by_dk` có sẵn (kết cấu 67.370kg, kiến trúc 564.8kg) |
| 2 | **Diện tích hoàn thiện** (lát/ốp/sơn) | đọc thẳng số ghi chú | 🟢 **TÍNH NGAY** — "diện tích lát…591m2" verbatim. Cần tool parse "…N m2" |
| 3 | **Thảm đá** (hạ tầng) | tiết diện × L | 🟢 **TÍNH NGAY** — "(6x2x0.3)m - L=56m" trong 1 chuỗi. Cần parser |
| 4 | **Thể tích BT cột** | a×b×H×SL | 🟡 a,b,SL ngay ("C1 (220x220)", SL); H suy từ chênh cao độ (cảnh báo) |
| 5 | **Diện tích cửa** ⭐(đối tác muốn nhất) | rộng×cao×SL | 🟡 **CẦN GÁN dim↔cấu kiện** — SL ngay (D1=24); 1300×2700 nằm ở dim chưa có x,y |
| 6 | **Thể tích BT dầm** | b×h×L×SL | 🟠 **BẪY** — b,h,SL ngay; nhưng "L=25.42m" trong file là **L-thép (gồm nối)**, KHÔNG dùng cho BT |
| 7 | **Ván khuôn cột/dầm** | chu_vi×H/L×SL | 🟠 tiết diện ngay; H/L kẹt như BT |
| 8 | **Thể tích BT sàn** | S_sàn×dày | 🟡 cần polyline bao sàn/tích 2 dim; dày từ text "bản dày 100" |
| 9-10 | **Xây/trát tường** | (L×H−S_cửa)×t | 🟡 chuỗi phụ thuộc (cần L tường, H tầng, t, S_cửa từ #5) |
| 11-13 | **Đào đất / đắp nền / cọc** | (a+2c)(b+2c)×H... | 🔴 **THIẾU trong file → đối tác nhập** (hạ tầng không có S đào; chiều dài cọc/hệ số taluy không có) |

**3 nhóm:** 🟢 làm ngay (thép, diện tích hoàn thiện, thảm đá — chỉ cần tool parse số); 🟡 cần gán dim↔cấu kiện (diện tích cửa, BT cột/dầm/sàn, ván khuôn, xây/trát); 🔴 thiếu số liệu → đối tác nhập (đào đắp, chiều dài cọc, hệ số).

---

## PHẦN 3 — PREREQ KỸ THUẬT: GẮN DIM ↔ CẤU KIỆN (nút thắt số 1)

Gần như mọi công thức 🟡 cần kích thước — mà kích thước nằm rải trong `DIMENSION` chưa gắn được vào cấu kiện.

**Vấn đề (đã xác nhận trong code):** `tools_core.py` khi đọc DIMENSION chỉ lưu `{handle, value}` — **KHÔNG có x,y**. Nên không biết đường kích thước "1300" thuộc cửa nào. (Trong khi `qty_index` gắn được số lượng nhờ có x,y.)

**Bước 1 — thêm x,y (+dimtype) cho DIMENSION:** neo tốt nhất là `e.dxf.text_midpoint` (chỗ đặt chữ số), fallback `defpoint/defpoint2/defpoint3`; nếu cả 4 rỗng → cờ `khong_co_toa_do=True` (thất bại phải lộ). *Chống overfit: phải có chuỗi fallback, không đóng cứng.*

**Bước 2 — chỉ mục neo cấu kiện:** neo = nhãn mã cấu kiện có x,y (tái dùng `qty_index` + text mã cấu kiện).

**Bước 3 — gắn theo VỊ TRÍ + độ tin cậy:** với mỗi dim có toạ độ, tìm neo gần nhất trong **ngưỡng thích nghi** (bội số bước-cột-phổ-biến, KHÔNG đóng cứng), gắn độ tin cậy theo khoảng cách (cao/trung bình/thấp). **Chống bịa cốt lõi:** hàm KHÔNG tự khẳng định "rộng=1300"; chỉ trả **tập ứng viên** + độ tin cậy; phân biệt rộng/cao theo `dimtype`; không phân biệt được → trả cả tập cho đối tác chọn. Mọi input gán-vị-trí **luôn** mang cờ `chua_chac=True`.

---

## PHẦN 4 — CÔNG CỤ MCP MỚI + LUỒNG DỮ/THIẾU + UX NHẬP BÙ

**Engine:** module mới `cong_thuc.py` — Formula Registry: mỗi công thức = {biểu thức + danh sách Input + resolver lấy từng input từ STATE}. Thêm công thức = thêm 1 object, không đụng engine.

**Tool MCP mới `tinh_dai_luong(ten_dai_luong, ma_cau_kien, inputs_bo_sung)`** (thêm vào `mcp_server.py`, bridge tự thành FunctionDeclaration).

**Luồng:** chuẩn hoá tên → tra registry → với mỗi input: có trong `inputs_bo_sung` (nguồn=người dùng) / resolver() / None→thiếu. **Đủ → TÍNH + sơ đồ tính. Thiếu → `inputs_da_co` + `inputs_thieu` + `can_bo_sung=true` (KHÔNG tính).**

**Ví dụ ĐỦ (diện tích cửa D1):** `{ket_qua: 84.24, don_vi: m2, cach_tinh: "rộng×cao×SL", inputs_da_co: [rộng=1300 (gán vị trí, chưa chắc), cao=2700 (chưa chắc), SL=24 (verbatim, cao)], so_do_he_thong_tinh: [...], canh_bao: "rộng/cao gán vị trí — đối tác xác nhận để tính chắc"}`.

**Ví dụ THIẾU (thể tích BT cột C1 thiếu chiều cao):** `{co_ket_qua: false, inputs_da_co: [b=220, h=220, SL=27], inputs_thieu: [{ten: chieu_cao, goi_y: "khoảng cách 2 cốt sàn", cach_cung_cap: "nhập chat: 'chiều cao cột C1 = 3.6m'"}], ghi_chu: "ĐÃ CÓ 3/4 input, cấp chiều cao → tính ngay"}`.

**UX nhập bù:** đối tác gõ chat "chiều cao cột C1 = 3.6m" → Gemini gọi lại `tinh_dai_luong(..., inputs_bo_sung='{"chieu_cao":3600}')`. Input nhập bù **luôn** mang `nguồn=người_dùng_cung_cap` ("do đối tác cấp, không đọc từ file"), CODE tự quy đổi đơn vị.

---

## PHẦN 5 — LỘ TRÌNH (làm diện tích cửa trước — đối tác muốn nhất)

1. **Sửa đọc DIMENSION thêm x,y,dimtype** (nền cho mọi thứ). Regen profile verify dim có toạ độ.
2. **`gan_dim_vao_cau_kien`** — test in dims quanh neo "cöa d1" xem ra 1300/2700 không, **chạy cả 3 file** (chống overfit).
3. **`cong_thuc.py` + đăng ký `dien_tich_cua`** trước. Resolver dùng lại `tra_cuu_so_luong` (SL) + `gan_dim` (kích thước).
4. **`tinh_dai_luong` tool MCP** + đăng ký.
5. **UX thiếu số liệu + `inputs_bo_sung`**.
6. **System prompt:** "hỏi TÍNH diện tích/thể tích/khối lượng → gọi `tinh_dai_luong`, KHÔNG tự nhân/cộng; tool báo thiếu → hỏi đối tác cấp; tôn trọng cờ `chua_chac`".
7. **Mở rộng:** nhóm 🟢 (diện tích lát verbatim, thảm đá) → rồi BT cột, xây/trát.

---

## PHẦN 6 — RỦI RO + CHỐNG BỊA

**3 tầng độ tin cậy:** `doc_verbatim` (cao, chắc) · `gan_vi_tri` (cao/TB/thấp theo khoảng cách, **chua_chac=true**) · `nguoi_dung_cung_cap` (ghi rõ nguồn) · `suy_tu_cong_thuc` (kế thừa tầng thấp nhất). **Kết quả cuối kế thừa độ tin cậy THẤP NHẤT** trong các input.

**Rủi ro chính:**
- **Gán dim sai cửa** (nhiều cửa gần nhau) → ngưỡng thích nghi + độ tin cậy theo khoảng cách + cờ chua_chac + cho đối tác override. Không trình bày số gán-vị-trí như số chắc.
- **⛔ BẪY L-thép ≠ L-cấu-kiện:** file ghi "L=25.42m" nhưng là chiều dài đã gồm nối thép + tổng cây (file ghi rõ "ĐÃ TÍNH CẢ ĐOẠN NỐI"). **CẤM** đổ con này vào công thức BT → sẽ bịa. Thiếu L nhịp thật → hiển thị input-còn-thiếu.
- **File hạ tầng KHÁC giả định:** không có S đào/đắp → để đối tác nhập (không giả định).
- **Test đa domain:** chạy resolver cả kết cấu + hạ tầng, không chỉ kiến trúc.

---

## PHẦN 7 — KHÁC BIỆT GIAI ĐOẠN 2: DEMO 2 vs DEMO 1

| | Demo 1 (bóc tách → Excel) | **Demo 2 GĐ2 (MCP, tương tác)** |
|---|---|---|
| Cách dùng | Chạy 1 lượt → bảng khối lượng | **Hội thoại**: hỏi từng đại lượng, trả tức thì |
| Thiếu số liệu | Cờ cảnh báo trong báo cáo | **Hỏi ngược đối tác → nhận nhập bù → tính tiếp** (vòng lặp) |
| Minh bạch | Cột nguồn Excel | **"Sơ đồ hệ thống tính"** mỗi câu: input+nguồn+handle+độ tin cậy |
| Trực quan | File tĩnh | highlight live + hội thoại |

**Điểm mạnh riêng demo 2:** vòng lặp người-máy — không cố bịa cho đủ, mà phơi bày "có gì/thiếu gì" rồi để đối tác cấp phần thiếu. Biến điểm yếu (thiếu số liệu) thành điểm mạnh tương tác.

---

## ⚠️ CÁC CHỖ KHÓ / CHƯA CHẮC (cần chốt khi review)
1. **Nút thắt = gắn dim↔cấu kiện.** Chưa làm xong thì diện tích cửa (thứ đối tác muốn nhất) chưa chạy. → làm bước 1.
2. **Gán vị trí là heuristic — luôn "chưa chắc".** Không hứa 100%; mời đối tác xác nhận. Muốn chắc hơn cần **bảng thống kê cửa (block TK_*)** nếu file có.
3. **Bẫy L-thép** là rủi ro bịa cao nhất (số trông như dùng được) → chặn cứng trong code.
4. **Hạ tầng đào/đắp thiếu S thật** → nhóm 🔴 gần như luôn để đối tác nhập (là hành vi ĐÚNG, không phải làm chưa tới).
5. **Thứ tự demo đề xuất:** trình diễn nhóm 🟢 (thép/thảm đá/diện tích hoàn thiện — "tính ngay có nguồn") trước cho thuyết phục; rồi diện tích cửa (có màn hỏi-nhập-bù) để khoe vòng lặp minh bạch.
