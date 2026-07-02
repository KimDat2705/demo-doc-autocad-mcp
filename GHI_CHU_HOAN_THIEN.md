# 📌 TRẠNG THÁI DEMO 2 & VIỆC TIẾP THEO — ĐỌC FILE NÀY TRƯỚC (bàn giao phiên mới)

> Cập nhật 2026-07-01. Đây là "điểm bắt đầu" cho phiên chat mới: tóm tắt demo 2 đang ở đâu + việc còn lại.

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

## Vừa xong (2026-07-01)
- ✅ **TODO #1 — Cấu kiện KHÔNG tồn tại:** `tinh_dai_luong` giờ kiểm tra TẤT ĐỊNH mã cấu kiện có xuất hiện trong
  bản vẽ không (helper `_cau_kien_hien_dien`, dựa token mã có chữ số + `_tok_bound`). Vắng mặt hoàn toàn → trả
  `khong_tim_thay=true` (đối tác chưa cấp số) thay vì mời nhập thông số. SYSTEM_PROMPT luật 10 + docstring tool cập nhật.
  Test tất định 14/14 PASS trên 3 domain (KT/KC MN Gia Lộc + Bảng TK cửa): cấu kiện thật KHÔNG báo nhầm, giả bắt đúng.
  End-to-end 3/3 PASS (GL9→không tìm thấy; D1→84.24m²; C1→hỏi chiều cao).
- 📋 **Rà soát parity demo 1 ↔ demo 2:** phát hiện 2 điểm LỆCH — (1) demo 1 CHƯA có xử lý "cấu kiện không tồn tại", còn
  trả NHẦM ("cột GL9"→9 cấu kiện, `tinh_duoc=True`); (2) diện tích cửa D1 demo 2 tính được (gán dim) còn demo 1 chưa.
  Đã soạn spec bàn giao ở **`../BAN_GIAO_PARITY_DEMO1.md`** (thư mục gốc) cho phiên demo 1 tự vá — demo 2 KHÔNG sửa demo 1.

## Vừa xong (2026-07-02) — bàn giao NGƯỢC từ demo 1 (`../BAN_GIAO_PARITY_DEMO2.md`)
- ✅ **VÁ LỖ HỔNG CHỐNG BỊA:** trước đây `_cau_kien_hien_dien` chỉ chạy khi `thieu AND not bs` → cấp `inputs_bo_sung`
  cho mã KHÔNG tồn tại vẫn tính ra số ảo (vd sàn SAN1 + {dien_tich,chieu_day} → 5.0 m³). ĐÃ SIẾT: kiểm tra tồn tại
  chuyển lên ĐẦU `tinh_dai_luong`, chặn **bất kể có inputs_bo_sung** (chỉ cho tính khi mã để trống = nhập tay thuần).
  Test hồi quy cố định `tests/test_takeoff_chong_bia.py` (A: existence đa-domain; B: lỗ hổng + regression).
- ✅ **VÁ SAI LOẠI (DM-1):** `("thể tích móng","DM-1")` trước ra 0.36 m³ (lấy tiết diện DẦM tính MÓNG). Nay chặn bằng
  `_loai_tu_ban_ve` — suy loại theo NHÃN bản vẽ ghi rõ ('DẦM DM-1' → {dam}), data-driven KHÔNG đoán prefix (tránh overfit);
  công thức có loại kỳ vọng (`_FORMULA_LOAI`) mà loại thực khác → trả `sai_loai=true`. Chỉ chặn khi có BẰNG CHỨNG xung đột
  (bản vẽ không ghi loại liền mã → vẫn tính, không phá C1/C4/DR-3).
- ✅ **4 TÍNH NĂNG PARITY (bàn giao ngược) — ĐÃ THÊM đủ:**
  (a) **size_index** (`_build_door_size_index`) — R×C cửa từ bảng thống kê → diện tích cửa *confident*; resolver `_rs_rong/_rs_cao`
  ưu tiên bảng, không có → rơi về gán-dim (chua_chac). Fixture bảng cửa: 7 cửa/404.09 m² (khớp demo 1 ~404.11).
  (b) **thong_tin_tang** (`_build_levels`) — cao độ → chiều cao tầng điển hình + số tầng ƯỚC TÍNH (KT 3.6m/3 tầng, KC 3.6m/2 tầng).
  Report-only, KHÔNG tự bơm vào resolver chiều cao (an toàn, đúng khuyến nghị handoff).
  (c) **tong_hop_khoi_luong** — bảng tổng hợp (SL + diện tích cửa + thể tích cột/dầm + thép + m³ ghi sẵn + tầng) + cột NGUỒN
  + `can_bo_sung` + `gia_dinh`. KC: 118 hàng, cột TẠM TÍNH khớp trị trực tiếp (C1=4.704, C4=9.504).
  (d) **xuat_excel** — ghi `.xlsx` (openpyxl) ra `_renders/`, trả `file_id`; host route `/file/<id>` + link tải ở frontend (song song `anh_id`).
  MCP tools + SYSTEM_PROMPT (luật 11,12) + `requirements.txt (openpyxl)` cập nhật. Test `test_takeoff_chong_bia.py` **23/23** (thêm smoke D).
- ✅ **TODO #3 — Tinh chỉnh GÁN-DIM (chỉ dùng cho cửa):** e2e phát hiện "cửa đi D1" ra 25.92 (neo nhầm vào ghi chú),
  nha 9T còn neo vào TRỤC LƯỚI (rộng 5450) / cao 50 phi lý. Viết lại `_gan_dim_cau_kien` + `_neo_ung_vien`/`_neo_score`:
  (1) **neo theo token MÃ** (bỏ từ mô tả thừa 'đi'/'cửa' → ỔN ĐỊNH: mọi biến thể cùng mã → cùng kết quả);
  (2) **chấm điểm neo** ưu tiên nhãn khớp từ mô tả + có "cửa" → tránh trục lưới/ghi chú;
  (3) **lọc dim hợp lý** cho ô cửa `_OPENING_DIM_LO/HI=[400,6000]mm` → loại dim 50/5450 (không có dim hợp lý → None = báo thiếu, không bịa);
  (4) chọn neo có CẶP DIM tốt nhất (xử lý cửa vẽ cạnh nhau). Test đa-domain (MN + nha 9T): MN D1 4 biến thể → 1300×2700 duy nhất;
  nha 9T D1 → 1500×1450 (hết loạn). Test `test_takeoff_chong_bia.py` nay **24/24** (thêm nhóm E bất biến). Vẫn gắn cờ "chưa chắc".

## Việc CÒN LẠI (TODO — ưu tiên trên xuống)
1. **Thêm đại lượng takeoff:** xây tường, trát, đào/đắp đất (nhóm 🔴 — chủ yếu đối tác nhập số; xem plan GĐ2).
2. **Nhóm 🟢 đọc-verbatim** (thảm đá hạ tầng "(6x2x0.3)m L=56m") — parser riêng nếu cần.
4. (Theo dõi) model: 2.5-flash ổn; 3.5-flash mạnh hơn nhưng hay 503; Pro chất lượng cao nhất nhưng quota thấp (cần billing).

## Chạy/test local (Windows)
```
# .env có GEMINI_API_KEY (hoặc dùng ../demo_doc_autocad/.env). File lớn: đặt READFILE_MAX_MB=300.
python app.py                       # http://localhost:5050
python tests/test_qa_data.py        # regression đọc 129/129
python tests/test_takeoff_chong_bia.py  # KHOÁ chống bịa + parity + gán-dim ổn định (tất định, miễn phí) — 24/24
python tests/kichban_gd2.py         # test takeoff end-to-end (đối chiếu engine, tốn API)
```

## Chống bịa (nguyên tắc BẤT DI BẤT DỊCH — mọi tính năng mới phải giữ)
Số do CODE tất định tính (không để LLM tự đếm/tính); mỗi số kèm NGUỒN + HANDLE; thiếu → báo thiếu (không bịa);
gán-theo-vị-trí → cờ "chưa chắc"; nhận-diện-quy-ước phải test ≥3 file khác domain (chống overfit).
