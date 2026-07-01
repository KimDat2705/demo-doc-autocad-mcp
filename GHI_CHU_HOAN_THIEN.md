# 📌 TRẠNG THÁI DEMO 2 & VIỆC TIẾP THEO — ĐỌC FILE NÀY TRƯỚC (bàn giao phiên mới)

> Cập nhật 2026-06-30. Đây là "điểm bắt đầu" cho phiên chat mới: tóm tắt demo 2 đang ở đâu + việc còn lại.

## Demo 2 là gì (1 phút)
Web app đọc + tính toán bản vẽ AutoCAD **qua MCP (Model Context Protocol)**. LLM = **Google Gemini** (`gemini-2.5-flash`,
đổi qua env `GEMINI_MODEL`). Kiến trúc: `app.py` (Flask host, giữ lịch sử hội thoại) → `mcp_bridge.py` (cầu nối Gemini↔MCP,
system prompt chống bịa) → `mcp_server.py` (MCP server chuẩn, 16 tool) → `tools_core.py` (lõi đọc ezdxf + engine tính toán).
ODA File Converter chuyển .dwg→.dxf. **KHÔNG cần AutoCAD → deploy cloud được.**
- **Live:** https://doc-autocad-mcp-demo.onrender.com  · **Repo:** github.com/KimDat2705/demo-doc-autocad-mcp (private)
- **KHÁC demo 1** (`../demo_doc_autocad/`, phiên khác đang làm giai đoạn 2 riêng — ĐỪNG đụng demo 1).

## Đã xong (Giai đoạn 1 + 2)
- **GĐ1 — ĐỌC:** 15 tool đọc số có sẵn (số lượng cửa/cấu kiện qua nhãn SL=/số lượng:N bộ; thép qua bảng thống kê;
  kích thước; mác BT/độ dốc/diện tích ghi sẵn; layer/block/sheet) + `danh_dau_cau_kien` (highlight ảnh). Chống bịa: số do CODE, kèm handle.
- **GĐ2 — TÍNH (takeoff):** tool `tinh_dai_luong` + 7 công thức (diện tích cửa; thể tích BT cột/dầm/sàn/móng; ván khuôn cột/dầm).
  Đủ input→tính + "sơ đồ hệ thống tính"; thiếu→hiện có/thiếu→đối tác nhắn số thiếu→tính tiếp (hội thoại có trí nhớ).
  Gắn dim↔cấu kiện theo vị trí (dim có toạ độ + hướng). 3 tầng tin cậy: đọc-verbatim / gán-vị-trí(chưa chắc) / đối-tác-nhập.
- **Đã test:** đọc 129/129 (đối chiếu ezdxf 3 file); takeoff khớp engine 100%; battery AI 198 câu. **2 lời chê đối tác đều giải quyết:**
  đếm cửa D1=24 ✅, diện tích cửa D1=84.24m² ✅.

## Tài liệu nên đọc (theo thứ tự)
1. `GHI_CHU_HOAN_THIEN.md` (file này) — trạng thái + TODO.
2. `README.md` — kiến trúc + cách chạy/deploy.
3. `KE_HOACH_GIAI_DOAN_2_DEMO2.md` — kế hoạch takeoff chi tiết (catalog 22 công thức, nút thắt gắn dim).
4. `BO_KICH_BAN_TEST_DEMO2.md` — bộ câu test kèm đáp án (4 phần).
5. `BAO_CAO_QA_DEMO2.md` — báo cáo QA (lỗi đã tìm/vá, đánh đổi model).

## Việc CÒN LẠI (TODO — ưu tiên trên xuống)
1. **Cấu kiện KHÔNG tồn tại** (vd "cửa gỗ lim GL9") → nên nói "không tìm thấy trong bản vẽ" thay vì hỏi thông số.
2. **Thêm đại lượng takeoff:** xây tường, trát, đào/đắp đất (nhóm 🔴 — chủ yếu đối tác nhập số; xem plan GĐ2).
3. **Tinh chỉnh gán dim↔cấu kiện:** ngưỡng bán kính thích nghi hơn; chọn đúng khi cửa vẽ cạnh nhau.
4. **Nhóm 🟢 đọc-verbatim** (thảm đá hạ tầng "(6x2x0.3)m L=56m") — parser riêng nếu cần.
5. (Theo dõi) model: 2.5-flash ổn; 3.5-flash mạnh hơn nhưng hay 503; Pro chất lượng cao nhất nhưng quota thấp (cần billing).

## Chạy/test local (Windows)
```
# .env có GEMINI_API_KEY (hoặc dùng ../demo_doc_autocad/.env). File lớn: đặt READFILE_MAX_MB=300.
python app.py                       # http://localhost:5050
python tests/test_qa_data.py        # regression đọc 129/129
python tests/kichban_gd2.py         # test takeoff (đối chiếu engine)
```

## Chống bịa (nguyên tắc BẤT DI BẤT DỊCH — mọi tính năng mới phải giữ)
Số do CODE tất định tính (không để LLM tự đếm/tính); mỗi số kèm NGUỒN + HANDLE; thiếu → báo thiếu (không bịa);
gán-theo-vị-trí → cờ "chưa chắc"; nhận-diện-quy-ước phải test ≥3 file khác domain (chống overfit).
