# NGHIÊN CỨU ĐỐI SÁNH KIẾN TRÚC — demo 2 vs thế giới (2026-07-22)

> **Câu hỏi:** kiến trúc hiện tại (upload → ODA → engine đọc-thuần → 26 MCP tool → Gemini → grounding guard → trả lời)
> cần cải thiện ở bước gì, khâu nào cần bổ sung?
> **Phương pháp:** workflow 47 agent — 6 hướng quét (GitHub OSS · phần mềm takeoff thương mại · nghiên cứu hiểu bản vẽ ·
> guard chống bịa production · hệ sinh thái dự toán VN · kỹ thuật OLE/RAM) → 41 nguồn kiểm chứng hoài nghi (fetch thật).
> **Kết quả thô:** 61 finding · 38 ý ADOPT_NOW / 31 ROADMAP / 2 REJECT · **1 nguồn giả bị bắt và loại**
> (paper "Tool Receipts" — không tồn tại đúng như mô tả; các ý trùng nó đã có nguồn thật khác là GeoMCP/RefChecker).

---

## 1. KẾT LUẬN CHIẾN LƯỢC

1. **Hướng đi hiện tại KHÔNG có đối thủ OSS trực tiếp.** Hệ sinh thái MCP-CAD hiện nay chủ yếu là WRITE (vẽ mới);
   repo gần nhất (`dwg-mcp-server`, read-only LibreDWG) không có takeoff, không guard, không tiếng Việt.
   → Kiến trúc "đọc + truy nguồn handle + guard sau-model" là **khoảng trống thị trường thật**, tiếp tục giữ.
2. **Chuẩn ngành takeoff xác nhận ethos của mình:** không hãng nào (Togal/Kreo/STACK/Bluebeam/CostX) để AI tự chốt số —
   tất cả đều "AI đề xuất → người duyệt từng số → chỉ số đã duyệt vào báo cáo". KPI ~0% bịa của mình đi đúng chuẩn.
3. **Guard số ±1% của mình đang Ở TRÊN mặt bằng chung** (đa số chỉ có citation-link, không verify số);
   chỗ người khác làm hơn: validate ID trích dẫn, câu-không-cần-nguồn, claim phi-số, đơn vị.
4. **Điểm cần bổ sung tập trung ở tầng ENGINE (recall) và tầng ANSWER (khớp nghiệp vụ dự toán VN)** — trùng chẩn đoán nội bộ
   (điểm yếu = đọc thiếu, không phải bịa).

## 2. ĐỐI SÁNH THEO TỪNG KHÂU

| Khâu | Mặt bằng chung | Mình đang | Cần bổ sung |
|---|---|---|---|
| Upload/convert | tương đương | size-guard sớm, session riêng, lỗi lộ rõ | (P2) iterdxf streaming cho file lớn |
| **Engine đọc** | bảng = grid từ đường kẻ; zone; bounds-check | 8 chỉ mục y-band, OLE chỉ cảnh báo | **(P1) đọc OLE · nâng ghép bảng · bounds-check · (P2) vùng-chưa-phủ, phân vùng** |
| MCP tools | query tổng quát + phân trang; đếm theo block | 26 tool chuyên biệt | (P2) tool query phân trang + dem_theo_block |
| LLM | router câu mẫu; tách prompt bất biến/quy ước | 21 luật + fallback; ✅ I9 tách mảnh + version/hash (LIVE) | (P3) router câu mẫu |
| **Guard** | validate citation-ID; câu-không-cần-nguồn | số ±1% (hơn mặt bằng) | **(P1) validate handle** · (P2) giảm từ-chối-oan · (P3) claim phi-số |
| **Answer/Excel** | 6 cột tiên lượng VN; diễn giải công thức; HITL pin | Excel 8 cột riêng, không phẳng | **(P1) sheet Tiên lượng chuẩn VN + diễn giải + không ôm đơn giá** · (P2) UI màu cờ · (P3) pin-to-accept |
| Vision | VLM chỉ ĐỊNH VỊ, không đọc số (Enginuity: định vị recall 0.61–0.87 nhưng đọc nội dung F1 0.03–0.18) | chưa có | (P3) chốt luật thiết kế trước, SoM audit offline đo trước khi đầu tư |

## 3. KHUYẾN NGHỊ ƯU TIÊN

### P1 — làm ngay (lợi/công cao nhất)
1. **Chỉ mục thứ 9: đọc nội dung bảng Excel nhúng OLE** *(effort M — recall win lớn nhất, 19/65 file)*
   Chuỗi: ezdxf lấy binary OLE2FRAME (tag 310, chính mozman xác nhận — issue #96) → quét magic CFBF `D0CF11E0` →
   `olefile` phân loại stream (`Workbook`→xlrd · `Package`→openpyxl) → bảng cấu trúc, nguồn `ole:<handle>:<sheet>:<R,C>`,
   **mặc định cờ nghi_ngo** + parse fail thì giữ cảnh báo cũ. **BẮT BUỘC probe 19 file thật trước khi code**
   (đo % blob có magic/stream; kiểm ODA-DXF có bảo toàn binary 310). Nguồn: ezdxf#96, olefile/oletools, Aspose forum (end-to-end thật).
2. **Guard: validate HANDLE theo tập-đã-cấp** *(S — vá lỗ bịa thật)*: gom mọi handle tool đã trả trong phiên vào set;
   handle trong answer không thuộc set → loại citation đó. (Pattern Anthropic Citations. Guard hiện chỉ check SỐ, handle model chép tự do.)
3. **Excel khớp nghiệp vụ dự toán VN** *(S–M — biến demo thành thứ cắm thẳng vào G8/F1/Eta/GXD)*:
   (a) thêm sheet `Tien_luong` PHẲNG 6 cột chuẩn `STT | Mã hiệu | Tên công tác | Đơn vị | Khối lượng | Diễn giải` (+2 cột Handle/Ghi chú cuối);
   (b) cột **Diễn giải = biểu thức tái lập** kiểu nghề QS: `4 x (0,8x2,2) : cửa D1 [handle]` — engine đã có sẵn toán hạng;
   (c) ghi **công thức Excel thật** (`=4*0.8*2.2`, `=SUBTOTAL`) thay số chết; (d) **KHÔNG ôm đơn giá** — cột giá để trống
   + ghi chú "áp giá tỉnh/quý trong phần mềm dự toán" + thêm luật từ chối câu hỏi giá; (e) sheet README định vị file =
   "Bảng khối lượng đo bóc + truy nguồn" (mắt xích 1 chuỗi TT 11/2021). Nguồn: manual G8 54tr, docs F1, cuckinhtexd.gov.vn.
4. **Bounds-check vật lý + benchmark tỷ lệ ngành** *(S — bắt lỗi garble/độ-lớn + lộ đọc-thiếu)*:
   bảng khoảng hợp lý theo loại đại lượng (thép Ø6–51, tầng 1.8–12m…) → ngoài khoảng gắn nghi_ngo (KHÔNG sửa số);
   ratio kg thép/m³ BT, m² cửa/m² sàn lệch dải → canh_bao. Nguồn: GeoMCP (arXiv 2603.01022), QTO Buccaneer.
5. **Nâng cấp ghép bảng thống kê** *(M — sửa điểm mù y-band trên corpus đa-firm)*:
   ưu tiên 1 = lưới từ **đường kẻ thật** LINE/LWPOLYLINE (port chiến lược "lines" pdfplumber: snap→join→giao điểm→ô, kể cả
   entity trong INSERT qua virtual_entities); ưu tiên 2 = **suy cột bằng rãnh trống trục x** (Camelot stream) khi bảng không kẻ;
   kèm 4 metric chất lượng lưới → lệch thì tự gắn nghi_ngo. Giữ y-band làm baseline đối chứng.

### P2 — kế tiếp
6. **Tool #27 query tổng quát có phân trang** (dxftype/layer/regex trên text đã giải mã TCVN) + **#28 dem_theo_block**
   (INSERT cùng tên block, trả handle+toạ độ+ảnh khoanh; block ẩn danh *U → LỘ "N block chưa phân loại"). Recall trực tiếp.
7. **Detector "vùng có mực chưa phủ"** — grid-binning đầu mút primitive chưa được chỉ mục nào tham chiếu → cảnh báo vùng nghi bỏ sót
   (thất-bại-phải-lộ cho recall; thay thế tất định cho CV).
8. **Phân vùng trang (zone)**: gán mỗi TEXT vào {khung_tên, bảng, ghi chú, khu vẽ} tất định → chống lấy nhầm nguồn số.
9. **Guard: cờ "câu không cần nguồn"** (dẫn nhập/chuyển tiếp/echo câu hỏi) → giảm từ-chối-oan (instrument log trước, whitelist tất định sau).
10. **UI phân tầng tin cậy**: panel trạng thái 8 chỉ mục ngay sau upload (đỏ/xám/vàng) + màu per-field từ cờ sẵn có + audit trail
    persist ánh xạ số↔nguồn mà guard đã tính. (Togal/Zensets/CostX — toàn surfacing cờ đã có, không thêm heuristic.)
11. **iterdxf streaming** khi `size×7 > RAM budget` (add-on chính thức ezdxf, file >5GB): đọc-một-phần-tự-khai thay vì từ chối
    hẳn file lớn; tiền đề = assert ODA xuất DXF ASCII. Ảnh hưởng quyết định HELD RAM (có thể đọc lớn hơn cùng gói tiền).
12. **Tách SYSTEM_PROMPT** = LUẬT-BẤT-BIẾN (chống bịa) + QUY-ƯỚC-VN có version (`quyuoc-vn-v1`) — log version mỗi phiên, đường cho P5.

### P3 — roadmap / cần điều kiện
- **Kênh vision tăng recall**: CHỐT LUẬT trước khi code — *VLM chỉ ĐỊNH VỊ vùng bỏ sót, tuyệt đối không đọc giá trị*
  (bằng chứng Enginuity: đọc nội dung F1 0.03–0.18); bước đo rẻ = SoM audit offline (render + lưới A1..H8, so độ phủ chỉ mục).
- **Router câu hỏi mẫu** → chuỗi tool tất định cho 10–15 mẫu phổ biến (cần log thật; worst-case fallback vòng tự do).
- **Guard claim phi-số** kiểu triplet RefChecker (tên cấu kiện/loại thép đối chiếu về 8 chỉ mục; từ điển thực thể dựng từ chính bản vẽ).
- **Pin-to-accept HITL** khi làm UI làm-việc-thật: số phải được người dùng duyệt mới vào Excel chốt.
- **Corpus GĐ4/P5**: diễn đàn **giaxaydung.vn** (persona QS thật) xin bản vẽ ≥3 firm; dataset **FloorPlanCAD** (~10k bản vẽ vector)
  làm corpus đa-domain test recall — gỡ đúng nút thắt "cần bản vẽ nhiều firm".
- **Đẩy parse về local** (pattern libredwg-web/WASM): local đọc → chỉ upload chỉ mục JSON nhỏ — khớp chiến lược "đọc local free".
- LibreDWG (GPL) = plan B converter cho nhánh public-ready (ODA không phân phối được).

## 4. NHỮNG ĐIỀU **KHÔNG** LÀM (đã cân nhắc và loại)
- **Không ôm đơn giá/định mức vào hệ** — giá theo tỉnh+quý, định mức sửa liên tục (TT12/2021, 09/2024, 08/2025, 60/2025):
  ôm vào = nhận nợ cập nhật + nguồn bịa mới. Chỉ (roadmap) tool tất định GỢI Ý mã hiệu từ danh mục công khai, trống khi không chắc.
- **Không cho VLM đọc số** trên bản vẽ (chỉ định vị) — số liệu Enginuity chứng minh.
- **Không dùng dxfgrabber** (unmaintained) — iterdxf là đường chính thức.
- **Không tin judge/checker tiếng Anh** (HHEM-2.1 English-only) cho tiếng Việt — chỉ làm máy chấm phụ offline nếu cần.
- 2 ý REJECT + 1 nguồn giả ("Tool Receipts") đã loại trong vòng kiểm chứng.

## 5. NGUỒN CHÍNH (đã fetch kiểm chứng)
ezdxf issue #96 (mozman, OLE 310) · olefile/oletools (decalage2) · ezdxf iterdxf docs · pdfplumber · Camelot ·
dwg-mcp-server · cad-ai-agent · autocad-mcp (puran-water) · OpenConstructionERP · QTO Buccaneer (IfcOpenShell) ·
Togal.AI/eTakeoff pinning · Kreo agentic-CV · STACK Floor Plan AI · Bluebeam Quantity Link · RIB CostX · Zensets ·
Enginuity (arXiv 2606.03410) · GeoMCP (arXiv 2603.01022) · RefChecker (Amazon) · Google Check Grounding · Anthropic Citations ·
Set-of-Mark (Microsoft) · FloorPlanCAD/CADTransformer/SymPoint · manual G8 · docs F1 · giaxaydung.vn · cuckinhtexd.gov.vn · TT 11/2021.

> Chi tiết đầy đủ 61 finding + verdict từng ý: log workflow `wf_b5c4e066-7e7` (phiên 2026-07-22).
