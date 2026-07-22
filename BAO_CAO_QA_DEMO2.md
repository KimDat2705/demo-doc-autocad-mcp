# BÁO CÁO QA DEMO 2 (hướng MCP) — 2026-06-30

> Vai: QA chuyên nghiệp. Phương pháp: đối chiếu GROUND TRUTH độc lập (ezdxf đọc lại), test đa file
> (chống overfit), đào sâu 4 loại lỗi: **ảo giác / đọc thiếu / đọc sai / lạc đề**.
> Bối cảnh: demo 1 từng "pass test nội bộ" nhưng đối tác vẫn chê → lần này test triệt để.

## Phạm vi test
- **3 file thật, 3 domain:** Kiến trúc CT-A (8024 đối tượng), Kết cấu CT-A (21077, thép 67 tấn), Hạ tầng CT-K (khảo sát địa hình + biển báo giao thông).
- **Tầng A — Dữ liệu (tất định, không AI):** 129 kiểm tra.
- **Tầng B — AI (Gemini):** 198 câu hỏi thiết kế tự động (grounded vào nội dung thật), chấm đối kháng 159 câu hợp lệ.

## TẦNG A — DỮ LIỆU: 129/129 PASS ✅
- **Port-faithfulness:** demo 2 (tools_core) == demo 1 (app.py) tuyệt đối.
- **Ground truth:** demo 2 == ezdxf đọc độc lập (layer/đối tượng/đếm/SL/thép/sheet).
- **2 bug tầng tool:**
  - 🔴→✅ **ĐÃ VÁ:** `tra_so_luong` khớp SUBSTRING ('C-4' ↔ 'C-40' trong ghi chú cọc) → token có chữ số giờ khớp theo RANH GIỚI TỪ.
  - 🟠 **Ghi nhận (giai đoạn 2):** khối lượng xà gồ 2472kg nằm trong TEXT note, không vào tổng thép tự động (AI vẫn search ra khi hỏi cụ thể).

## TẦNG B — AI: phân tích thật/nhiễu
Chấm 159 câu: raw **111 đạt / 23 một phần / 25 lỗi (69.8%)**. Sau khi soi từng lỗi:

### 🔴 BUG THẬT — đã VÁ & re-test đạt
| Bug | Số ca | Nguyên nhân | Cách vá | Re-test |
|---|---|---|---|---|
| **MAX_TURNS bỏ cuộc** | ~11 | Câu nhiều phần cần >8 lượt tool → AI trả "Câu hỏi cần quá nhiều bước" dù data có | Nới `MAX_TURNS` 8→14 | ✅ id187/195/51 trả lời được |
| **Sa bẫy chiều dài/cao độ** | ~6 | AI lấy DIMENSION max (58800mm) làm "chiều dài công trình" | System prompt rule 8 cấm dứt khoát + từ chối | ✅ id15/151/152/178 từ chối đúng |
| **Gộp nhầm thép tròn+hình** | ~3 | AI cộng 564.8+3545.9=4110.7kg | Prompt rule 8b: cấm cộng, nêu riêng | ✅ id38 tách riêng |

### ⚪ KHÔNG phải bug (đã loại trừ)
- **Verifier chấm gắt (false-positive):** id173/174/176/177 bị báo "ảo giác PMA XF55/bản lề 3D" — nhưng **cross-check: text CÓ THẬT trong file** ("cửa nhôm hệ pma xf55"). Verifier không thấy trong factsheet rút gọn nên báo nhầm.
- **Lỗi đề test:** id188 "file hạ tầng có 4110kg thép" — câu bẫy hỏi về file hạ tầng nhưng harness chạy trên file kiến trúc → AI trả đúng theo file đang nạp.

### 🟡 Hạn chế còn lại (chưa vá / giai đoạn 2)
- id22: hỏi thép cầu thang thoát hiểm → trả tổng cả bảng thép hình (3545.9kg) thay vì riêng cầu thang (2163kg). Tool không tách được nhóm con theo hạng mục.
- Highlight: 5/8 câu ra ảnh (vài câu AI không gọi tool đánh dấu / tìm 0 vị trí).
- 14 câu chưa có kết quả do lỗi 503 (xem dưới).

## 🔴🔴 2 PHÁT HIỆN HẠ TẦNG QUAN TRỌNG (không phải lỗi đọc, nhưng ảnh hưởng đối tác)
1. **QUOTA model Pro preview quá thấp:** `gemini-3.1-pro-preview` chạy ~25 câu là `429 RESOURCE_EXHAUSTED`. **Rất có thể là lý do đối tác chê demo 1 "chưa ổn"** — hỏi vài chục câu là demo báo "AI tạm lỗi". → **Đã đổi demo 2 sang `gemini-3.5-flash`** (quota cao hơn nhiều, giữ chất lượng vì số do tool tất định lo).
2. **Flash đôi lúc 503 "high demand":** model 3.5-flash mới/đông người dùng → ~8% câu dính 503 (bridge có retry, đa số tự khỏi). Cần theo dõi; nếu nặng có thể cân nhắc `gemini-2.5-flash` (ổn định hơn) hoặc bật billing dùng Pro.

## Quan trọng: Flash YẾU HƠN Pro ở các bẫy
25 câu chạy được trên Pro **không sa bẫy nào** (Pro từ chối "chiều dài công trình" đúng). Flash thì sa bẫy nhiều hơn (đã vá bằng prompt mạnh). → Đây là đánh đổi **chất lượng (Pro) vs quota/độ ổn định (Flash)**. Với demo này (số do tool lo), Flash + prompt vá là đủ tốt + chạy được; nhưng nếu cần độ chính xác cao nhất trên câu suy luận khó, Pro (kèm billing) nhỉnh hơn.

## Kết luận
- **Lõi đọc dữ liệu (tất định) RẤT CHẮC** — 129/129, đa domain, đã vá bug substring.
- **Tầng AI: 3 bug thật đã vá & xác nhận**; phần lớn "lỗi" còn lại là verifier chấm gắt hoặc lỗi đề test.
- **Việc cần làm tiếp:** deploy bản đã vá; chạy lại 14 câu 503 + full battery để có số sạch; cân nhắc model (Flash vs Pro+billing); id22/highlight là cải tiến nhỏ.
