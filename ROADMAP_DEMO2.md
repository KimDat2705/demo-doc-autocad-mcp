# 🗺️ ROADMAP DEMO 2 — từ "bóc tách khối lượng" → "DỰ TOÁN"

> Soạn 2026-07-09. Demo 2 (MCP) là **sản phẩm chính** (đã chốt, demo 1 dừng). Tài liệu này = định hướng phát triển
> tiếp, ưu tiên hoá, dựa trên: rà soát code thật + feedback đối tác + kiểm chứng đối kháng (workflow đa-agent).
> **NGUYÊN TẮC BẤT DI xuyên suốt mọi hạng mục:** chống bịa — số/giá do CODE tính, kèm NGUỒN + HANDLE; thiếu → HỎI
> (không bịa); suy đoán/gán → gắn cờ "chưa chắc"; nhận-diện-quy-ước test ≥3 file khác domain (chống overfit).

## 1. Đang ở đâu (đã có)
- **Đọc:** SL cấu kiện, thép tròn + thép hình/inox, kích thước, tiết diện (tự suy **cm/mm** ngưỡng 130 + ghép tọa độ đọc
  được bảng cột 9T), cao độ → tầng, layer/block/sheet. Mỗi số kèm handle truy nguồn.
- **Takeoff (`tinh_dai_luong`, 12 công thức):** diện tích cửa; BT cột/dầm/sàn/móng; ván khuôn cột/dầm; xây tường/trát/đào/
  đắp đất; **khối lượng thép hình/inox = SL(đọc) × kg/bộ(đối tác cấp)**.
- **Tổng hợp + xuất Excel + khoanh ĐỎ ảnh cấu kiện** (điểm riêng). Suy đoán đơn vị có gắn cờ.
- **Chất lượng:** test tất định **71/71** (chống bịa + cm/mm + inox + hardening + đối kháng) + đọc **129/129**.
  Deploy Render (push main → auto), có `/version` verify commit qua HTTP.

## 2. Mục tiêu cuối
Đưa hệ từ **"đọc + bóc tách KHỐI LƯỢNG (m³/m²/kg)"** → **"DỰ TOÁN CHI PHÍ"** (khối lượng × đơn giá → thành tiền →
tổng hợp kinh phí), vẫn giữ chống-bịa: giá/hệ số phải có nguồn/trích dẫn, thiếu thì hỏi.

## 3. Ưu tiên

### 🔴 P0 — Mắt xích còn thiếu để thật sự thành "dự toán"
| # | Hạng mục | Effort | Chống bịa |
|---|---|---|---|
| 1 | **Lớp ĐƠN GIÁ → THÀNH TIỀN** (khối_lượng × đơn_giá do CODE tính; surface ở tổng hợp + Excel) | L | Đơn giá CHỈ từ đối tác cấp hoặc catalog có TRÍCH DẪN (mã ĐM + năm + tỉnh) — coi như 1 input có nguồn/handle; thiếu → hỏi (không lấy giá thị trường bịa); thành_tiền kế thừa độ tin cậy THẤP NHẤT của (khối lượng, đơn giá) |

Đây là khoảng trống lớn nhất: hiện engine dừng ở khối lượng, grep toàn repo **0** kết quả `don_gia/thanh_tien/VND`.

### 🟠 P1 — Độ chính xác khối lượng + cấu trúc BOQ + đầu ra dự toán
| # | Hạng mục | Effort | Ghi chú |
|---|---|---|---|
| 2 | **TỔNG PHỤ theo đơn vị** (m²/m³/kg) trong tổng hợp + Excel — con số headline (tổng cửa/thép/BT) | S | Salvage từ demo 1; chỉ cộng ô numeric đã có nguồn, lọc ô chuỗi (dòng tiết diện) |
| 3 | **Trừ lỗ cửa/cửa sổ** khi tính xây tường & trát (đang ghi "CHƯA trừ" → vượt khối lượng) | M | Hệ đã tính được diện tích cửa; đối tác XÁC NHẬN lỗ cần trừ, không tự đoán cửa nào thuộc tường nào |
| 4 | **Gắn MÁC bê tông** (B20/B25/M250…) vào dòng thể tích BT → map đúng đơn giá | M | Chỉ gắn khi bản vẽ GHI RÕ mác liền mã (data-driven như `_loai_tu_ban_ve`), mơ hồ → hỏi |
| 5 | **Nhóm HẠNG MỤC + gợi ý mã hiệu công tác** (phần ngầm/thân/hoàn thiện) thay danh sách phẳng | M | Nhóm theo loại đã nhận diện từ nhãn; mã hiệu chỉ GỢI Ý, gắn cờ "cần đối tác chốt" |
| 6 | **Mẫu Excel DỰ TOÁN** (Mã hiệu·Công tác·ĐVT·KL·Đơn giá VL/NC/M·Thành tiền) + sheet **Tổng hợp kinh phí** (trực tiếp→chung→TNCTTT→VAT) | L | Ô tiền chỉ điền khi có đơn giá nguồn; hệ số (%) do đối tác cấp/theo thông tư có trích dẫn; thiếu → để trống + "cần bổ sung" |
| 7 | **Diện tích SÀN**: tool liệt kê nhãn "diện tích … m²" ghi sẵn + đối tác cấp (cho lát/trần/sơn) | M | Feedback đối tác. CHỈ đọc nhãn ghi sẵn (nguyên văn + handle) hoặc đối tác cấp; **KHÔNG** suy từ hình học (giữ luật cũ) |
| 8 | **Tự NÊU ứng viên "X kg/bộ" / số đo** gần mã để đối tác **1-click xác nhận** (thay gõ tay) | M | Feedback ("AI phải hỏi nhiều"). Ứng viên = GỢI Ý (nguyên văn + handle + khoảng cách), chỉ thành input khi đối tác xác nhận |
| 9 | **Mở rộng test đối kháng đa-domain** (mã toàn-chữ giả mọi công thức; lệch đại lượng; auto-grab) | M | Khoá regression cho các vá chống-bịa; chạy trên KC/KT/9T |
| 10 | **Model fallback** (429/503 kéo dài) → chuỗi model phụ qua env trước khi báo lỗi | M | 2.5-flash hay 503; hiện chỉ retry cùng model rồi trả "⚠ Lỗi khi hỏi AI" |
| 11 | **Chặn file lớn SỚM** ở `/upload` (MAX_UPLOAD 150MB ≫ READFILE 45MB; .dwg convert xong mới chối) | S | Kiểm size trước khi save/convert; căn 2 hằng số; hoặc nâng plan cho file 9T (114MB) |

### 🟡 P2 — Chi tiết chuẩn & vận hành
| # | Hạng mục | Effort |
|---|---|---|
| 12 | **ĐỊNH MỨC hao phí VL/NC/Máy** (số hiệu ĐM có trích dẫn) → đơn giá chi tiết đúng chuẩn nhà nước | L |
| 13 | Ước chiều cao cột theo cao độ ("cột X cao 1 tầng") ở luồng tính lẻ (salvage demo 1; giữ cờ giả định) | M |
| 14 | Gợi ý m³ GHI SẴN khi takeoff báo thiếu (salvage demo 1) | S |
| 15 | Dọn file `_uploads/_renders` theo TTL (đĩa free đầy) | S |
| 16 | Concurrency: tách state theo session (hiện 1 DRAWING/SUMMARY chung → 2 người đạp nhau) | M |
| 17 | Cold-start keep-alive + giám sát lỗi qua Render Logs / `/version` | S |

## 4. Đã xử lý NGAY trong phiên này (từ kiểm chứng đối kháng)
- ✅ **Hardening chống bịa (engine):** `_nd` từ chối bool/inf/nan; cổng dùng `math.isfinite`; **kiểm KẾT QUẢ hữu hạn**
  sau compute (chặn tràn số 16×1e308=inf trả "Infinity kg").
- ✅ **3 lỗ BỊA SỐ (agent chạy code xác nhận) đã VÁ:** (1) mã TOÀN CHỮ "GHOSTINOX" lọt kiểm-tồn-tại → bịa số cho mọi
  công thức; (2) "thể tích bê tông sàn" mã TRỐNG tự quét cả file vơ "diện tích Xm2" → bịa thể tích sàn; (3) "thể tích inox"
  ép sang công thức khối lượng không cảnh báo. Test nhóm [K]+[L] khoá lại.

## 5. KHÔNG làm (đã cân nhắc, loại)
- ❌ Port script chứng minh demo 1 (`chung_minh_so.py`, `reader_kiem_chung.py`) — overfit cứng `ban_ve_mau.dxf`
  (hardcode token/số layer/block). Giá trị đã đạt bằng test 71/71 + đọc 129/129.
- ❌ Port renderer cũ demo 1 (`demo_visual.py`, `render_zoom.py`) — demo 2 `render_region`/`highlight` mạnh & tích hợp MCP hơn.

## 6. Đề xuất thứ tự triển khai (sprint)
1. **Sprint 1 (biến demo thành "dự toán sơ bộ" thật):** #2 Tổng phụ (S) + #1 Đơn giá→Thành tiền MVP (đối tác cấp đơn giá) →
   lần đầu có cột thành tiền + tổng chi phí.
2. **Sprint 2 (độ chính xác + BOQ):** #4 mác BT → #5 nhóm hạng mục → #3 trừ lỗ → #6 mẫu Excel dự toán + tổng hợp kinh phí.
3. **Sprint 3 (trải nghiệm theo feedback + bền):** #7 diện tích sàn, #8 ứng viên kg/bộ 1-click; #9/#10/#11 robustness.
4. **Sau:** P2 (#12 định mức chi tiết, #13–#17 tiện ích + vận hành).
