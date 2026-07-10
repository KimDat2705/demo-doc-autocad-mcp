# 🗺️ ROADMAP DEMO 2 — củng cố "ĐỌC + TÍNH KHỐI LƯỢNG"

> Soạn 2026-07-09, chỉnh lại cùng ngày sau khi user làm rõ phạm vi. Demo 2 (MCP) là **sản phẩm chính** (chốt, demo 1 dừng).
> **⚠️ PHẠM VI ĐÃ CHỐT:** demo = **đọc dữ liệu trong file + trả lời + học/tính CÔNG THỨC (ra KHỐI LƯỢNG: m²/m³/kg/bộ)**.
> **DỰ TOÁN CHI PHÍ (thành tiền = khối lượng × đơn giá + định mức + thuế) = HOÃN** — chờ đối tác nêu yêu cầu cụ thể rồi
> mới quyết (user chốt 2026-07-09). Lý do: ngay từ đầu dự án đã ghi "phạm vi 'dự toán' chỉ khối lượng hay cả thành tiền —
> CHƯA CHỐT", và phạm vi demo đã chốt = chỉ dữ liệu trong file (định mức/giá NGOÀI file chưa cần). Xem mục 4.
>
> **NGUYÊN TẮC BẤT DI:** chống bịa — số do CODE tính, kèm NGUỒN + HANDLE; thiếu → HỎI (không bịa); suy đoán/gán → cờ
> "chưa chắc"; nhận-diện-quy-ước test ≥3 file khác domain (chống overfit).

## 1. Đang ở đâu (đã có)
- **Đọc:** SL cấu kiện, thép tròn + thép hình/inox, kích thước, tiết diện (tự suy **cm/mm** + ghép tọa độ đọc được bảng cột 9T),
  cao độ → tầng, layer/block/sheet. Mỗi số kèm handle.
- **Takeoff (12 công thức):** diện tích cửa; BT cột/dầm/sàn/móng; ván khuôn cột/dầm; xây/trát/đào/đắp đất; **inox = SL×kg/bộ**.
- **Tổng hợp bảng + xuất Excel (khối lượng) + khoanh ĐỎ ảnh.** Suy đoán đơn vị có gắn cờ.
- Test **71/71** + đọc **129/129**. Deploy Render + `/version`.

## 2. Định hướng TRƯỚC MẮT
**Củng cố + hoàn thiện chức năng đọc/tính KHỐI LƯỢNG hiện tại** (theo feedback đối tác thật + độ chính xác + trải nghiệm +
độ bền). KHÔNG mở rộng sang thành tiền/định mức cho tới khi đối tác chốt.

## 3. Việc CỦNG CỐ (đang làm) — bám sát demo hiện tại + feedback đối tác
| # | Hạng mục | Effort | Ghi chú / chống bịa |
|---|---|---|---|
| A | **TỔNG PHỤ theo đơn vị** (tổng cửa m², tổng thép kg, tổng BT m³) trong tổng hợp + Excel | S | Con số headline đối tác hay cần; hiện phải tự nhẩm. Chỉ cộng ô numeric đã có nguồn (lọc ô chuỗi tiết diện). Salvage demo 1 |
| B | ✅ **XONG** — **Trừ lỗ cửa/cửa sổ** khi tính xây tường & trát | M | `lo_cua` trong inputs_bo_sung: {ma,sl} (tra bảng cửa confident, có handle) hoặc {rong,cao,sl} (mm). SL do đối tác khai (KHÔNG tự đoán cửa nào thuộc tường nào). net=gross−Σ(R×C×SL)×(be_day\|so_mat). Chống bịa: mã giả/không-confident/lỗ≥tường/sl bẩn/lẫn đơn vị/over-count đều BLOCK+LỘ, không âm, không bịa size. Backward-compat số cũ y hệt. Test [N] 20 ca offline (`test_takeoff_chong_bia.py` 96/96) |
| C | **Liệt kê diện tích GHI SẴN** (nhãn "… m²" nguyên văn + handle) để đối tác đối chiếu/cấp diện tích sàn | M | Feedback đối tác hỏi diện tích sàn. CHỈ đọc nhãn ghi sẵn (không khẳng định là "sàn xây dựng") hoặc đối tác cấp; **KHÔNG** suy từ hình học (giữ luật cũ). ⚠ cần probe xem file có nhãn diện-tích-sàn đáng tin không |
| D | **Tự NÊU ứng viên "X kg/bộ" / số đo** gần mã để đối tác **1-click xác nhận** (thay gõ tay) | M | Feedback "AI phải hỏi nhiều". Ứng viên = GỢI Ý (nguyên văn + handle + khoảng cách), chỉ thành input khi đối tác xác nhận (không tự cắm) |
| E | **Gợi ý m³ GHI SẴN** khi takeoff (đào/đắp/xây/trát) báo thiếu input | S | Demo đã trích `stated_vol` nhưng nhánh "thiếu" chưa tham chiếu → bỏ lỡ dữ liệu đã đọc. Salvage demo 1 |
| F | **Ước chiều cao cột theo cao độ** ("cột X cao 1 tầng") ở luồng tính lẻ (giờ luôn bắt nhập tay) | M | Giữ cờ "giả định 1 tầng, xác nhận nếu khác" + nguồn "hệ thống suy từ cao độ". Salvage demo 1 |
| G | **Mở rộng test đối kháng đa-domain** (mã toàn-chữ giả; lệch đại lượng; auto-grab) chạy trên KC/KT/9T | M | Khoá regression cho các vá chống-bịa |

## 3b. ROBUSTNESS / VẬN HÀNH (nền, làm xen kẽ)
| # | Hạng mục | Effort |
|---|---|---|
| H | **Model fallback** (429/503 kéo dài) → chuỗi model phụ qua env trước khi báo lỗi | M |
| I | **Chặn file lớn SỚM** ở `/upload` (MAX_UPLOAD 150MB ≫ READFILE 45MB; .dwg convert xong mới chối) | S |
| J | Dọn file `_uploads/_renders` theo TTL (đĩa free đầy) | S |
| K | Concurrency: tách state theo session (1 DRAWING chung → 2 người đạp nhau) | M |
| L | Cold-start keep-alive + giám sát lỗi qua Render Logs / `/version` | S |

## 4. HOÃN — chờ đối tác chốt yêu cầu (KHÔNG làm cho tới khi có yêu cầu cụ thể)
> Đây là mở rộng sang **DỰ TOÁN CHI PHÍ**. Đối tác CHƯA yêu cầu; phạm vi "thành tiền" trong dự án vẫn để "chưa chốt".
> Chỉ mở khi đối tác nêu rõ họ muốn gì (đơn giá ở đâu ra? định mức nào? mẫu dự toán ra sao?).
- Lớp **đơn giá → thành tiền** (khối lượng × đơn giá).
- **Định mức** hao phí VL/NC/Máy (số hiệu ĐM có trích dẫn).
- **Mẫu Excel DỰ TOÁN** + sheet tổng hợp kinh phí (trực tiếp → chung → TNCTTT → VAT).
- Gắn **mác bê tông** + **nhóm hạng mục / mã hiệu công tác** (BOQ chuẩn) — chỉ cần khi làm đơn giá.

## 5. Đã xử lý trong phiên này (2026-07-09)
- ✅ Tính năng **inox = SL × kg/bộ** (feedback đối tác) → inox S1 = 16 × 8.62 = 137.92 kg.
- ✅ **Hardening chống bịa** (từ workflow đối kháng): `_nd` từ chối bool/inf/nan; cổng `math.isfinite`; kiểm KẾT QUẢ hữu hạn.
- ✅ **Vá 3 lỗ BỊA SỐ** (workflow chạy code phát hiện): mã toàn chữ "GHOSTINOX"; "thể tích sàn" mã trống tự vơ diện tích;
  "thể tích inox" lệch đại lượng. Test [J][K][L] → 71/71.

## 6. KHÔNG làm (đã cân nhắc, loại)
- ❌ Port script chứng minh demo 1 (overfit `ban_ve_mau.dxf`). Giá trị đã đạt bằng test 71/71 + đọc 129/129.
- ❌ Port renderer cũ demo 1 (demo 2 `render_region`/`highlight` mạnh & tích hợp MCP hơn).

## 7. Đề xuất thứ tự
1. **A (tổng phụ, S)** + **E (gợi ý m³ ghi sẵn, S)** — nhanh, tăng giá trị ngay, rủi ro thấp.
2. **C (liệt kê diện tích ghi sẵn)** — trả lời được câu diện tích sàn của đối tác (theo cách an toàn) → *probe trước xem file có nhãn đáng tin*.
3. **D (ứng viên kg/bộ 1-click)** + **B (trừ lỗ cửa)** — trải nghiệm + độ chính xác.
4. **G (test đối kháng)** + robustness (**H/I** trước).
