# Evaluator Rubric — demo 2 (đọc & tính khối lượng bản vẽ AutoCAD)

> ⚖️ Cây thước chấm chất lượng ở mức NHIỆM VỤ (không gắn cách hiện thực). Mỗi tiêu chí chấm **1–5**, PHẢI kèm bằng chứng
> (câu hỏi cụ thể trên file thật + kết quả). Tách vai "chấm" khỏi vai "làm" (chống tự-chấm lạc quan).

## Cách chấm
- **5** = đúng + có handle truy nguồn + bền trên ≥3 file khác domain.
- **3** = đúng trên file quen nhưng chưa chắc trên file lạ (rủi ro overfit).
- **1** = sai / bịa / "hỏi một đằng trả một nẻo".

## Bộ tiêu chí (9)
| # | Tiêu chí | Hỏi mẫu (benchmark) | Đạt 5 khi |
|---|---|---|---|
| 1 | **Đọc cơ bản chính xác** | "bao nhiêu layer / đối tượng / kích thước?" | Số khớp parser tất định trên mọi file |
| 2 | **Số lượng cấu kiện THẬT** | "số lượng cửa D1?", "mấy đài ĐC-3?" | Trả số file ghi (SL=/N bộ); không ghi → nói thẳng; KHÔNG lấy đếm-chữ làm số lượng |
| 3 | **Khối lượng vật liệu** | "tổng thép?", "thép hình/inox bao nhiêu kg?" | Đọc đúng bảng + tách loại (tròn/hình); ghi rõ giới hạn |
| 4 | **Chống bịa / ảo giác** | bẫy: "thang máy?" file không có; mã giả "GHOSTINOX"; input inf/âm | "không có"/"không tìm thấy"/"không hợp lệ"; KHÔNG chế số/handle |
| 5 | **Trả đúng trọng tâm + TÍNH được** | "tổng diện tích cửa D1?", "thể tích cột C1 cao 3.6m?", "kg inox cửa S1?" | TÍNH ra số + sơ đồ + handle; thiếu → hỏi; KHÔNG trả lạc |
| 6 | **Truy nguồn (handle)** | mọi câu nội dung cụ thể | Kèm handle có thật trong file |
| 7 | **Tổng quát đa-file (chống overfit)** | cùng câu trên file khác domain (9T cm / CT-A mm / hạ tầng) | Đúng theo TỪNG file (cm/mm tự nhận, không học vẹt) |
| 8 | **Phân tầng độ tin cậy** | câu cần suy luận/tính | Rõ: đọc-verbatim / ghép-vị-trí ("chưa chắc") / suy-đoán-đơn-vị (cảnh báo) / phải-tính |
| 9 | **Tốc độ & độ bền** | hỏi 10 câu liên tiếp | Không treo (retry/ép-trả-lời); nhanh (2.5-flash 2–8s) |

## Bảng điểm — DEMO 2 (chấm 2026-07-09)
| # | Tiêu chí | Điểm | Bằng chứng |
|---|---|---|---|
| 1 | Đọc cơ bản | **5** | layer/đối tượng/dim khớp parser tất định; QA đọc 129/129 (đối chiếu ezdxf ground truth 3 file) |
| 2 | Số lượng cấu kiện | **5** | cửa D1=24, S1=16 (live đối tác), tổng 73; qty_index đa quy ước + fold font |
| 3 | Khối lượng vật liệu | **5** | thép tròn KC 67370.7 kg; thép hình/inox tách riêng; cảnh báo không gộp |
| 4 | Chống bịa | **5** | mã giả→không tìm thấy; inf/tràn số/bool→chặn (test [K][L]); hardening đối kháng workflow |
| 5 | Trọng tâm + tính | **5** | diện tích cửa D1=84.24 m²; cột C1=4.704 m³; **inox S1=137.92 kg**; 9T C-3=23.04 m³ — takeoff ĐÃ làm |
| 6 | Truy nguồn handle | **5** | mọi số kèm handle; test khoá handle∈file |
| 7 | Tổng quát đa-file | **5** | 9T (cm) vs CT-A (mm) tự nhận đúng đơn vị (ngưỡng 130); test [I] đa-domain |
| 8 | Phân tầng tin cậy | **4** | cờ verbatim/gán-vị-trí/suy_doan_don_vi/tạm-tính; gán-dim vẫn còn tinh chỉnh được |
| 9 | Tốc độ & độ bền | **4** | 2.5-flash nhanh + ép-trả-lời chống bỏ-cuộc; model fallback (429/503) CHƯA có (roadmap H) → chưa 5 |

**Điểm trung bình demo 2: 4.8 / 5.** Mạnh: đọc + chống bịa + **takeoff/tính khối lượng** + đa-file. Trừ điểm nhẹ: phân tầng tin cậy còn tinh chỉnh (8) + chưa có model fallback (9).

> So với bảng điểm demo 1 (4.6/5, thời điểm chưa làm takeoff): demo 2 cao hơn ở tiêu chí 5 (đã tính được) — nhưng lưu ý điểm demo 1 chấm ở phạm vi "đọc" (GĐ1), không phải để "so hơn kém" nữa (đã chốt demo 2).
