# KẾ HOẠCH KHO KIẾN THỨC DEV-SOẠN + CONFIRM-ONLY (pivot AI-tự-học 2026-07-26)

> **Định hướng (user chốt 2026-07-26):** "DEV dạy trước, đối tác CHỈ XÁC NHẬN." BỎ kênh đối-tác-dạy-mở
> (`hoc_quy_uoc` không phơi đối tác — thành công cụ DEV nội bộ) + BỎ P5 auto-codify + BỎ F-B web-teaching.
> Thay bằng: **kho kiến thức DEV soạn sẵn** (ký hiệu/quy ước đa-domain, kiểm-chứng-được, fail-open) +
> khi gặp ký hiệu dễ-nhầm/bí → HỎI với **phương án soạn sẵn**, đối tác **chỉ bấm xác nhận**.
> Nghiên cứu: workflow `wf_f83e8fa0-19f` (10 agent: 3 probe + 2 design + 4 red-team + synth).
> **Verdict: GO_WITH_ADJUSTMENTS** (4/4 red-team; mọi finding CHẶN/CAO đã có cách sửa cụ thể — xem §5).

## 1. Bằng chứng nền (probe chạy thật, không phỏng đoán)

- **Inventory code:** "kiến thức ngành" đang RẢI RÁC ~25+ chỗ trong `tools_core.py` (regex ký hiệu, ngưỡng
  plausibility, từ vựng loại cấu kiện, quy tắc disambiguation) — nhiều mục provenance = "dev đoán" hoặc
  "rút từ 1-2 firm", chưa hệ thống hoá, chưa version.
- **Corpus probe (10 file .dxf đại diện, 4 file qua `Drawing` thật):** tìm được **7 va chạm
  cùng-token-khác-nghĩa CÓ BẰNG CHỨNG nguyên văn**: `D/Dxx` (Ø ống ↔ Ø thép ↔ tên trục), **`ĐC↔DC` tái
  hiện NGAY TRONG 1 FILE** (đài cọc ↔ mã chi tiết khác, handle `16AA1F` vs `17F56D`, file kết cấu móng C1
  corpus), `Đ1` (cửa đi ↔ đoạn cọc ↔ tấm đan ↔ mã bản vẽ điện), `C1/C2/B/E/K/H` (mã cấu kiện ↔ TÊN TRỤC ↔
  tham số), `CT/CTN/CN`, `M/L/T1/R`, `CH` (cửa ↔ chiều cao ↔ cao độ — bài học CH-2.700).
- **Đo bão-hỏi:** nếu cứ "thấy đa nghĩa là hỏi" → 50-80% câu hỏi THỪA trên 7 file thử (vd C2 xuất hiện 48×
  thuần cột vẫn bị hỏi) → alarm fatigue, đối tác bấm bừa. ⇒ gate hỏi là phần thiết kế QUAN TRỌNG NHẤT.
- **Nguồn kiểm chứng:** phân 3 tầng trung thực — `chuan_quoc_gia` (TCVN cụ thể) / `pho_bien_nganh` (quy ước
  không chuẩn hoá) / `quan_sat_corpus` (+`bai_hoc_noi_bo`). ~30-60 seed đề xuất; **đợt đầu chỉ ~20-25 entry**
  theo tần suất ĐO ĐƯỢC (ca đã trả giá: ĐC/DC, CH, D1, C1, T1, DK, mác B/M, mũi cọc≠đáy đài, Km+, cút-góc,
  'WORD - n.nnn'); seed chưa-soi-corpus vào hàng chờ, chỉ codify khi WORM log gặp thật.

## 2. Thiết kế chốt (lai A-khung + B-não)

- **Storage kiểu I9:** module data thuần `kienthuc.py` (`KB_ENTRIES` tuple, không I/O) + `KB_VERSION` +
  `KB_HASH` (sha256, đóng băng trong test, lộ ở `/version`). Import `try/except` → thiếu file = hệ chạy
  y hệt (degrade-safe).
- **Data model entry:** id/option_key/meaning_key **TOÀN CHỮ+underscore (cấm chữ số)**; 2 tầng khoá —
  `khoa_phan_biet` (từ `_norm_ma`, GIỮ đ/d) + `khoa_sap` (`_norm_label` cho query người gõ; trùng khoá-sập
  bắt buộc có cạnh `confusable_with`, check lúc build); `match` (tok_res 2-slot chữ+đuôi-số, token dương/âm,
  `match_kieu` structural|keyword); `nghia[]` (mo_ta KHÔNG-chữ-số, domain, tier, nguồn, coverage INT nội bộ
  nhưng **emit bằng CHỮ**); `on_collision` (ship: **ASK/NEVER_AUTO toàn bộ** — không auto-resolve);
  `confirm_template` (câu hỏi + options ngôn ngữ thường, luôn có 'khác/không chắc' ngang hàng).
- **Chống lọt rổ grounding 3 TẦNG:** (1) payload phát-ra-ngoài cấm mọi leaf số + cấm chữ số trong identifier;
  (2) mọi dữ liệu gốc-kho trong tool-result nằm dưới **đúng 1 key `_kb`** → bridge strip đệ quy key này
  TRƯỚC `_collect_numbers` (allowlist-of-one-key); (3) test B5 chạy `_collect_numbers` trên RESULT THẬT
  end-to-end, assert đóng góp rỗng. Nguyên văn file + handle nằm NGOÀI `_kb` → số hợp lệ vẫn vào rổ
  (không từ-chối-oan — repro '800 mm' của red-team).
- **Gate hỏi = BẰNG-CHỨNG-DƯƠNG NỘI-FILE (chống bão-hỏi):** chỉ hỏi khi (a) chính file có bằng chứng
  nghĩa-thứ-hai (≥2 index khác loại / cả 2 dạng raw cùng tồn tại như ĐC-1 & DC-1 / domain-sheet mâu thuẫn)
  VÀ (b) mã liên quan trực tiếp câu user hỏi VÀ (c) engine-index CHƯA tự ghép được loại VÀ (d) chưa
  hỏi/bỏ-qua trong phiên. **CAP 1 câu hỏi confirm/lượt**; 3 trạng thái per-(entry,phiên):
  chua_hoi / da_hoi_bo_qua / da_xac_nhan. **LEGEND-FIRST:** file có bảng chú thích riêng → option
  'theo chú thích trong bản vẽ' đứng đầu; tier hiển thị là NGUỒN, prompt cấm dùng tier để chọn nghĩa.
- **Confirm-only THẬT host-only:** kênh bấm = endpoint **POST `/xac-nhan`** (frontend gọi thẳng
  `bridge.call`, KHÔNG qua chat/Gemini); tool `xac_nhan_ky_hieu` vào `_TOOL_KHONG_CHO_LLM` **+ GATE
  DISPATCH-SIDE mới (L0)**; validation fail-closed (kb_id tồn tại + option ∈ ENUM + câu hỏi ĐÃ phát trong
  phiên). Hiệu lực: `Drawing.kb_xacnhan` per-phiên-file, keyed (mã `_norm_ma` + chữ-ký-ngữ-cảnh
  sheet/cụm-handle/loại-nhãn) — 1 file có thể chứa 'DẦM D1' lẫn 'CỬA D1' nên KHÔNG áp toàn file, cấm đè
  occurrence có nhãn loại tường minh; mâu thuẫn hậu-kiểm → tự re-ask + gỡ nhãn; reset lộ rõ khi đổi file;
  nhãn trung thực "theo xác nhận trong phiên file này". **Xác nhận KHÔNG vào grounding, KHÔNG đổi số.**
- **Vận hành:** 1 lệnh `kb-refreeze` trong `harness/scripts/` chạy trọn (schema-validate → B5 grounding-rỗng
  → B4 garble TCVN3+non-SIG+phản-khớp → battery 25-ca dễ-nhầm → classifier-diff + guard-recall → in hash);
  **tách chu kỳ sửa-kho khỏi chu kỳ sửa-prompt** (thêm entry không phải A/B lại prompt).

## 3. Lát cắt triển khai (mỗi lát ship + test được riêng)

| Lát | Nội dung | Rủi ro |
|---|---|---|
| **L0** | **Gate dispatch-side** (mcp_bridge ~:697-700): `fc.name` ∈ host-only hoặc ∉ declare → trả lỗi, không gọi. **Vá lỗ AN NINH HIỆN HỮU** (đã tự xác minh: `_TOOL_KHONG_CHO_LLM` chỉ lọc declaration, dispatch thi hành mọi tên) — độc lập kho, làm ngay được | thấp |
| **L1** | `kienthuc.py` ~20-25 entry + validator bất biến + KB_VERSION/HASH + lệnh `kb-refreeze` + 2 dòng `/version`. Zero đổi hành vi | thấp |
| **L2** | Bridge strip key `_kb` trước `_collect_numbers` + thêm 2 tool mới vào tuple loại-grounding (tiền lệ U3/I4a). Ship TRƯỚC mọi payload kho | thấp |
| **L3** | Tool `tra_ky_hieu` (read-only, phơi LLM, nhận symbol thô kể cả chỉ-chữ, fail-open) + mảnh prompt `_P_R18` (chỉ luật trình bày) → bump PROMPT_VERSION + **đo A/B LIVE** theo `[[feedback-do-thay-doi-prompt-ab]]` | vừa |
| **L4** | Graft có gate vào `phan_loai_tin_hieu` + `doi_chieu_nghi_ngo` (norm từ RAW bằng `_norm_ma`, nhánh chỉ-chữ, gate bằng-chứng-dương, móc 'WORD - n.nnn' từ canh_bao `cao_do_min_max`, LEGEND-FIRST, cap 1 câu/lượt); siết `_la_notation_chuan` chỉ nhận ký-hiệu-hình-thức-token | vừa |
| **L5** | Endpoint `/xac-nhan` + tool `xac_nhan_ky_hieu` host-only + `Drawing.kb_xacnhan` + WORM log | vừa |
| **L6** | Vá garble tầng CODE do kho chỉ điểm ('ỉ'=Ø vào `_DIAM_RE` có gông ngữ cảnh; đo corpus 86 file trước/sau; test phản-khớp 'thép I10'/'i=2%') — TÁCH khỏi kho | vừa |
| **L7** | ⛔ **HOÃN** — xác nhận ảnh hưởng SỐ (dedup/tổng). Chỉ mở sau red-team 2 tầng + validate độc lập | cao |

Test gate chi tiết từng lát: xem journal workflow `wf_f83e8fa0-19f` (synth.slices_final).

## 4. KPI trung thực (chống overclaim)

- Kho làm hệ **HỎI ĐÚNG CHỖ + bớt hiểu nhầm ký hiệu**; KHÔNG hứa tăng recall đọc-số, KHÔNG tự làm máy
  đọc thêm số ở bản vẽ điện/nước (đó là bộ đọc riêng, việc khác).
- KPI kép cho suppression: giảm báo-động-① trên corpus **VÀ** zero-mất-ứng-viên trên firm giữ lại
  ('/g10', 'caSi' phải còn lộ). KPI hỏi: số câu hỏi/file trên 10 file probe ≤ cap.
- KPI bất biến: 0% bịa; đóng-góp-grounding của mọi payload kho = ∅; câu đúng ('L=800') không bị refuse.

## 5. Finding CHẶN/CAO đã xử lý trong thiết kế (tóm tắt)

1. **[CHẶN] Số của kho lọt rổ grounding** (repro: coverage INT {2,5,15,20,25,30} → câu bịa '25 MPa' PASS
   guard — đúng lớp lỗi -22.75) → 3 tầng chống-lọt ở §2.
2. **[CHẶN] Auto-resolve theo proximity/layer** (tiền lệ I3-U: corpus mm-scale → sai ở firm gốc-mét) →
   ship ASK/NEVER_AUTO 100%; RESOLVE_IF_SIGNAL chỉ mở sau ≥3 firm + holdout, đợt đầu 0 entry.
3. **[CHẶN] Gemini tự-xác-nhận** → host-only + L0 dispatch-gate + kênh bấm là endpoint riêng.
4. **[CHẶN] Lỗ dispatch hiện hữu** (đã tự xác minh code) → L0.
5. **[CAO] Đ→D sập trước khi tra kho** (ĐC-1 đến graft đã thành dc-1 — repro) → norm từ RAW `t['vn']`
   bằng `_norm_ma`; kho 2 tầng khoá.
6. **[CAO] Token chỉ-chữ (CH, ĐC, WC) chết vì filter đòi chữ số** → nhánh tra riêng + móc canh_bao
   cao_do_min_max (đường kích hoạt thật duy nhất cho CH-2.700).
7. **[CAO] Bão-hỏi 50-80% thừa** → gate bằng-chứng-dương + suppression engine-đã-ghép + cap 1 câu/lượt.
8. **[CAO] ENUM đóng lái người bấm phương án gần-giống** → option kèm nguyên văn+handle; nghĩa 1-firm
   phrased dè dặt "ở nơi khác từng là X — có đúng ở bản vẽ NÀY không?"; 'khác/không chắc' là mặc định.
9. **[CAO] Alias garble bare-token va chạm mới** ('ỉ10'→'i10' ≡ thép hình I10 — repro) → kho KHÔNG chứa
   alias garble; việc đó là L6 tầng code có đo corpus.
10. **[CAO] Suppression nuốt token dị nghĩa firm mới** → chỉ ký-hiệu-hình-thức-token được suppress;
    word-like cấm trừ chuẩn-quốc-gia + ≥3 firm + holdout.

## 6. Câu hỏi chờ user quyết (trước khi code L3+)

1. **Nút bấm xác nhận trên web:** đồng ý thêm endpoint `/xac-nhan` + nút trong giao diện demo? (Không có
   nút → tính năng xác nhận chưa dùng được cho đối tác; chat KHÔNG được làm kênh xác nhận.)
2. **Danh sách ~20-25 ký hiệu đợt đầu:** user duyệt trước, hay giao dev tự chốt theo tiêu chí tần suất?
3. (Mặc định theo quyết định đã có) Demo không đăng nhập → xác nhận hiệu lực "phiên file đang mở", ghi chú
   trung thực. 4. L7 HOÃN. 5. Giới thiệu tính năng đúng mức (§4).
