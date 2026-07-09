# 📌 TRẠNG THÁI DEMO 2 & VIỆC TIẾP THEO — ĐỌC FILE NÀY TRƯỚC (bàn giao phiên mới)

> Cập nhật 2026-07-09. Đây là "điểm bắt đầu" cho phiên chat mới: tóm tắt demo 2 đang ở đâu + việc còn lại.
> **TRẠNG THÁI 1 DÒNG:** demo 2 (MCP) đã HOÀN THIỆN lõi + takeoff mở rộng + bóc tách + trực quan hoá, deploy live,
> test tất định **65/65** (thêm [I] cm/mm+9T, [J] inox=SL×kg/bộ, [K] hardening inf/tràn/bool). Đọc đúng bảng cột nhà 9T
> (cm). **QUYẾT ĐỊNH: chốt demo 2 là sản phẩm chính — demo 1 (`../demo_doc_autocad/`) DỪNG phát triển, không dùng nữa.**

## Demo 2 là gì (1 phút)
Web app đọc + tính toán bản vẽ AutoCAD **qua MCP (Model Context Protocol)**. LLM = **Google Gemini** (`gemini-2.5-flash`,
đổi qua env `GEMINI_MODEL`). Kiến trúc: `app.py` (Flask host, giữ lịch sử hội thoại) → `mcp_bridge.py` (cầu nối Gemini↔MCP,
system prompt chống bịa) → `mcp_server.py` (MCP server chuẩn, **20 tool**) → `tools_core.py` (lõi đọc ezdxf + engine tính toán).
ODA File Converter chuyển .dwg→.dxf. **KHÔNG cần AutoCAD → deploy cloud được.**
- **Live:** https://doc-autocad-mcp-demo.onrender.com  · **Repo:** github.com/KimDat2705/demo-doc-autocad-mcp (private)
- **KHÁC demo 1** (`../demo_doc_autocad/`, hướng gọi tool TRỰC TIẾP — nay đã hoàn thiện + parity; **ĐỪNG đụng code demo 1**, chỉ soạn bàn giao).

## Đã xong (cập nhật 2026-07-02)
- **GĐ1 — ĐỌC:** ~15 tool đọc số có sẵn (SL cửa/cấu kiện; thép bảng thống kê; kích thước; mác BT/độ dốc/diện tích ghi sẵn;
  layer/block/sheet) + `danh_dau_cau_kien` (KHOANH ĐỎ ảnh — điểm riêng demo 2). Chống bịa: số do CODE, kèm handle.
- **GĐ2 — TÍNH (takeoff):** `tinh_dai_luong` + **11 công thức** (diện tích cửa; BT cột/dầm/sàn/móng; ván khuôn cột/dầm; **xây tường/trát/đào đất/đắp đất**).
  Đủ input→tính + sơ đồ; thiếu→báo thiếu→đối tác nhập→tính tiếp. Gán-dim ĐÃ tinh chỉnh (neo theo mã, ổn định + lọc dim hợp lý).
  Chống bịa nhiều lớp: không tồn tại→`khong_tim_thay`; sai loại→`sai_loai`; input phi số/âm→báo không hợp lệ (không crash/không số âm).
- **Thêm (parity + mở rộng):** `size_index` (R×C bảng cửa→confident), `thong_tin_tang` (cao độ→tầng), `tong_hop_khoi_luong` (bảng tổng hợp),
  `xuat_excel_du_toan` (.xlsx), `boc_tach_kich_thuoc` (trích số đo ghi chú, không tự tính vật liệu).
- **Đã test:** đọc 129/129; takeoff khớp engine; **`tests/test_takeoff_chong_bia.py` 38/38** (chống bịa + parity + gán-dim + audit).
- **Parity 2 chiều với demo 1:** đạt (cross-consistency 5 hạng mục lõi KHỚP tuyệt đối). Xem `../BAN_GIAO_PARITY_DEMO*.md`.
- **So sánh 2 hướng:** đã làm (hội đồng 3 chuyên gia) → **khuyến nghị hướng MCP** (71.7 vs 54.0); user CHƯA chốt quyết định cuối.

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
- ✅ **Mở rộng takeoff + BÓC TÁCH (user duyệt) — dựng sẵn công thức, luôn theo luồng đọc/nhập-đủ-mới-tính, KHÔNG bịa:**
  (A) **4 đại lượng mới** trong `_FORMULAS`: xây tường (dài×cao×dày), trát (dài×cao×số_mặt), đào đất, đắp đất (dài×rộng×sâu).
  Input qua resolver `_rs_bs_only` (chỉ đối tác cấp) — bản vẽ ít ghi sẵn nên thiếu → hỏi (đúng quy trình). "đào móng"≠"bê tông móng".
  (B) **`boc_tach_kich_thuoc(tu_khoa)`** — TRÍCH số đo từ ghi chú tự do (3D, L=, m², m³, bề dày, SL) + NGUYÊN VĂN + handle,
  phân biệt đơn vị mm/m; **KHÔNG tự tính** (nhiều "AxBxC" là kích thước VẬT LIỆU) → chống bịa.
  **Kiểm chứng đối kháng (workflow 3 giám định):** công thức SẠCH; bắt + VÁ 2 lỗ hổng HIGH: (i) `_rs_chieu_day` khi mã rỗng
  quét cả file lấy "dày" bừa → thêm `if not codes: return None` (vá cả xây tường + sàn); (ii) phân loại đơn vị đuôi bất đối xứng
  ("65 mm" có dấu cách nhầm) → chuẩn hoá `unaccent`+strip đồng nhất, loại chữ số/²³. + vá 3 lỗi vừa (m2 liền, loại "N viên/m2"
  = mật độ, bề dày thập phân). MCP tools + SYSTEM_PROMPT (luật 10,13). Test **33/33** (nhóm F+G). → **HẾT TODO takeoff/parser.**
- ✅ **AUDIT đối kháng 2 demo (workflow) — vá 5 bug demo 2:** (1) CRASH khi `inputs_bo_sung` phi số ('abc'); (2) input
  ÂM/0 vẫn ra `co_ket_qua` (thể tích -4.704). → thêm cửa "SỐ DƯƠNG hợp lệ" trước `compute` (phi số/≤0 → báo không hợp lệ,
  không tính). (3) gán-dim gắn `do_tin_cay='cao'` cho số chưa-chắc → cap 'trung_binh'. (4) `thong_ke_thep(16.0)` float key
  'Ø16.0' → chuẩn hoá bỏ '.0'. (5) `gioi_han` âm cắt cụt slice → kẹp ≥0. Test **38/38** (nhóm H). Cross-consistency: 5 hạng
  mục lõi KHỚP+ĐÚNG cả 2 demo. (Bug `_sect_to_m` ngưỡng 150 của demo 1 đã flag → **demo 1 tự vá xong 2026-07-03**,
  xem `../BAN_GIAO_PARITY_DEMO2_CM_MM.md`.)

## Vừa xong (2026-07-03) — VÁ PARITY cm/mm + ĐỌC BẢNG CỘT 9T (user duyệt "full parity")
- **Bối cảnh:** nhận bàn giao ngược demo 1 (`../BAN_GIAO_PARITY_DEMO2_CM_MM.md`) cảnh báo "mặc định mm" đọc sai 9T (cm) 100×.
  Probe file THẬT → nỗi lo KHÔNG xảy ra: demo 2 (cũ) *không đọc được* tiết diện kết cấu 9T nào (cổng `50≤a` thiên mm loại
  dầm cm nhỏ + tiết diện cột ở BẢNG, mã và `(80X80)` ở text riêng) → trả `can_bo_sung` (AN TOÀN, không bịa) — nhưng LỆCH
  COVERAGE với demo 1 (đọc + tính được). User chốt **full parity**.
- ✅ **Port cơ chế demo 1 vào `tools_core.py`:** `_sect_to_mm` (đọc đơn vị ghi rõ mm/cm + **ngưỡng 130** + cờ mơ hồ
  `suy_doan_don_vi`; cm→×10 ra mm-tương-đương để công thức ÷1e6/1e9 tính đúng), `_unit_ambiguous_sect`, **`_build_section_index`**
  (ghép mã↔tiết diện theo TỌA ĐỘ mutual-NN + inline, bán kính 1500 → đọc được bảng cột 9T), `_is_structcode` (loại vật
  liệu/rác vd `hop-50x100x2`). Cổng cũ `50≤a` thiên mm → thay `_plausible_section_mm` (unit-aware). `_doc_tiet_dien` ưu tiên
  section_index (fallback cùng-text). Surface `suy_doan_don_vi` khắp `_td_prov`/`tinh_dai_luong`/`tong_hop_khoi_luong`.
- ✅ **Phát hiện dữ liệu thật:** tiết diện cột 9T dùng **chữ X HOA** `(80X80)` → regex cũ `[x×*]` (x thường) không bắt →
  đổi `[xX×*]`. Đã flag cho demo 1 tự kiểm ở `../BAN_GIAO_DEMO1_9T_XHOA_PARITY.md`.
- ✅ **Kết quả (probe + test tất định):** 9T đọc **9 cột** (C-1..C-9) quy ước cm; **C-3 = 80×80cm → 23.04 m³ KHỚP demo 1**
  (cross-consistency). Gia Lộc KHÔNG đổi: C1 = 220×220mm → 4.704 m³, không cảnh báo nhiễu (file mm sạch). `mcp_bridge.py`
  SYSTEM_PROMPT thêm luật cảnh báo đơn vị suy đoán. Test `test_takeoff_chong_bia.py` thêm nhóm **[I]** → **50/50 PASS**; QA đọc **129/129** giữ nguyên.

## Vừa xong (2026-07-09) — CHỐT demo 2 + tính năng INOX (feedback đối tác) + hardening đối kháng
- **QUYẾT ĐỊNH CHIẾN LƯỢC:** đối tác test 2 demo → ưng demo 2 (nhanh + đọc kích thước từ bảng + khoanh đỏ ảnh). Rà soát:
  khác biệt tốc độ là do **MODEL** (demo 1 `gemini-3.1-pro-preview` chậm vs demo 2 `2.5-flash`), không phải kiến trúc; các
  "thất bại" demo 2 (inox, diện tích sàn) là **giới hạn CHUNG / chống-bịa cố ý**, không phải điểm yếu riêng. → **Chốt demo 2
  là sản phẩm chính, DỪNG demo 1.** Nguyên tắc "2 demo cân bằng" NGHỈ.
- ✅ **Tính năng MỚI — khối lượng thép hình/INOX = SL(đọc) × kg/bộ(đối tác cấp)** (`khoi_luong_thep_hinh` trong `_FORMULAS`;
  ánh xạ "inox"/"thép hình" ĐẦU `_TEN_MAP`, TRƯỚC "cua" để 'kg inox cửa S1' không nhầm diện tích cửa). Giải đúng nỗi bực
  đối tác: bản vẽ chỉ có GHI CHÚ "khung inox (1 bộ): 8.62 kg" (không bảng tách theo cửa) → nay `inox S1 = 16×8.62 = 137.92 kg`.
  Chống bịa: kg/bộ CHỈ đối tác cấp (KHÔNG tự lấy số từ ghi chú gán mã — chống bịa liên kết); SL đọc tự động (đối tác override).
  SYSTEM_PROMPT rule **8c**. MCP KHÔNG cần tool mới (dùng `tinh_dai_luong` sẵn có).
- ✅ **Kiểm chứng ĐỐI KHÁNG (workflow 4 giám định) → bắt + vá lỗ hổng chống-bịa CHUNG cho engine:** (1) `kg/bộ=inf`/`1e400`/
  `"inf"` lọt cổng `x==x and x>0` (inf qua cả hai) → ra `Infinity kg`; (2) input hữu hạn `1e308` × 16 **tràn số** thành inf
  (code chỉ validate INPUT, không validate KẾT QUẢ); (3) `kg/bộ=true` → `_nd` chạy `float(True)=1.0` TRƯỚC validate nên chốt
  `not isinstance(bool)` thành code chết → ra 16 kg từ giá trị không cấp. **VÁ:** `import math`; `_nd` từ chối bool+inf+nan;
  cổng dùng `math.isfinite`; **thêm kiểm KẾT QUẢ hữu hạn** sau compute. Áp cho MỌI công thức.
- ✅ **Test:** thêm nhóm [J] (inox) + [K] (hardening) → `test_takeoff_chong_bia.py` **65/65 PASS**; QA đọc **129/129**.
- 📋 **Còn nợ (LOW, từ đối kháng — đưa vào roadmap):** mã TOÀN CHỮ ("GHOSTINOX") + đủ số bù → không bị `_cau_kien_hien_dien`
  chặn (chỉ verify mã có token chữ số); "thể tích inox" định tuyến sang công thức KHỐI LƯỢNG (đổi m³→kg, chỉ đổi nhãn không cảnh báo).

## Việc CÒN LẠI (TODO)
- (Theo dõi) model: 2.5-flash ổn; 3.5-flash mạnh hơn nhưng hay 503; Pro chất lượng cao nhất nhưng quota thấp (cần billing).
- ✅ **XONG (2026-07-03):** endpoint `/version` (trả `RENDER_GIT_COMMIT` + `sect_cm_max`/`has_section_index`). Đã dùng để
  verify bản parity cm/mm LIVE: `commit=e870074`, `sect_cm_max=130`, `has_section_index=true` (khớp commit đã push).

## Chạy/test local (Windows)
```
# .env có GEMINI_API_KEY (hoặc dùng ../demo_doc_autocad/.env). File lớn: đặt READFILE_MAX_MB=300.
python app.py                       # http://localhost:5050
python tests/test_qa_data.py        # regression đọc 129/129
python tests/test_takeoff_chong_bia.py  # KHOÁ chống bịa + parity + gán-dim + takeoff mở rộng + bóc tách (miễn phí) — 33/33
python tests/kichban_gd2.py         # test takeoff end-to-end (đối chiếu engine, tốn API)
```

## Chống bịa (nguyên tắc BẤT DI BẤT DỊCH — mọi tính năng mới phải giữ)
Số do CODE tất định tính (không để LLM tự đếm/tính); mỗi số kèm NGUỒN + HANDLE; thiếu → báo thiếu (không bịa);
gán-theo-vị-trí → cờ "chưa chắc"; nhận-diện-quy-ước phải test ≥3 file khác domain (chống overfit).
