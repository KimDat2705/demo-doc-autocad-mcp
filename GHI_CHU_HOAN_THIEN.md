# Ghi chú hoàn thiện demo 2 (làm dần)

Demo 2 đã chạy đầy đủ local + có scaffolding deploy. Ưu tiên hiện tại: **deploy lên link riêng**.
Các việc dưới đây để hoàn thiện dần sau khi đã xem demo chạy thật:

## 1. Test thêm file đa dạng (chống overfit) — QUAN TRỌNG
- Chạy demo 2 trên: `2. KetCau MN GiaLoc` (kết cấu, AC1021/2007), `1.+2. nhà 9 tầng` (file lớn 19MB/15MB .dwg).
- Kiểm: tra cứu số lượng, thống kê thép, và **highlight** có đúng/đẹp trên file kết cấu + hạ tầng không
  (kịch bản khác file kiến trúc cửa). Theo nguyên tắc: nhận-diện-theo-quy-ước phải test ≥3 file khác domain.
- Lưu ý file nhà 9 tầng .dxf >45MB sẽ bị chặn (READFILE_MAX_MB) — cần nâng gói RAM để test.

## 2. Tối ưu tốc độ render (highlight ~10-19s/lần)
- Nút thắt: `draw_entities` xử lý INSERT nở ra nhiều sub-entity trong vùng.
- Hướng: giảm `dpi` (110→90), giới hạn số entity vẽ (hard_cap nhỏ hơn cho vùng), bỏ qua block ký hiệu phụ,
  hoặc cache ảnh theo (từ khoá+vùng). Mục tiêu < ~5s.

## 3. Polish UI / trải nghiệm
- Hiện cụm khác khi highlight trải nhiều cụm (nút "xem cụm khác"?).
- Nút tải ảnh highlight về máy.
- Có thể thêm: gõ "đánh dấu" tự gợi ý cấu kiện có trong bản vẽ.

## 4. (Tương lai, giai đoạn 2) Bóc tách/tính toán
- "Tổng diện tích cửa" = rộng×cao×SL (cần lưu toạ độ DIMENSION — hiện chưa).
- Thể tích bê tông/ván khuôn từ hình học.

## 5. Demo "chuẩn MCP đa-client" (minh hoạ cho sếp)
- Quay video cắm `mcp_server.py` vào Gemini CLI / Claude Desktop để cho thấy cùng 1 server dùng nhiều nơi
  (điểm mạnh "chuẩn hoá" của MCP mà demo 1 không có).
