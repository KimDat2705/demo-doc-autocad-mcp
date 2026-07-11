# Claude Progress — demo 2 (nhật ký tiến độ theo phiên)

> Continuity Artifact (chuẩn Harness): lưu "đã làm gì / kết quả test / quyết định / đang chờ" để phiên sau không mất ngữ cảnh.
> Mới nhất ở TRÊN CÙNG. Bàn giao đầy đủ: `session-handoff.md`. Nhật ký chi tiết hơn nữa: `../GHI_CHU_HOAN_THIEN.md`.

---
## Session 2026-07-10 (CHỐT SỔ) — Củng cố B/C/D/F + clean-state
**Tóm tắt phiên:** làm 4 đầu việc củng cố ROADMAP theo cùng quy trình (probe → design panel → triển khai → kiểm chứng đối kháng loop-until-dry → test → docs → commit/push/deploy/verify). Chi tiết từng task ở các entry (b)/(c)/(d) bên dưới.

**Đã làm (4 task, mỗi task commit riêng + live + verify `/version`):**
- **B — Trừ lỗ cửa/cửa sổ** (`lo_cua` cho xây/trát). Commit `7095614`. Adversarial: 4 bug thật → vá.
- **C — Liệt kê diện tích ghi sẵn** (`liet_ke_dien_tich_ghi_san`, tool #21). Commit `4113a8a`. Adversarial: bịa đuôi thập phân + density-space → vá.
- **D — Ứng viên gợi ý** (kg/bộ + số đo, `ung_vien` trong inputs_thieu, 1-click). Commit `4168708`. Adversarial: garble bộ→bé → vá.
- **F — Ước cao cột theo cao độ** (1 tầng, cờ giả định; móng resolver riêng). Commit `a775825`. Adversarial: 0 lỗ (tách móng ở tầng công thức).
- (E — gợi ý m³ ghi sẵn: ĐÃ XONG từ trước = `goi_y_ghi_san`; user chốt bỏ qua, làm F.)
- Chốt sổ: cập nhật số cũ trong `clean-state-checklist.md` (20→21 tool, 76→149 test); thêm `.gitignore` cho artifact test (kichban_*_ketqua, verify*_chunks); rà `feature_list.json` (A-F done, G planned, H-L partial); **KHÔNG có `specs/specs.json`** (demo 2 dùng feature_list.json thay specs/ — đúng AGENTS.md).

**Kết quả test (clean-state cuối phiên, ĐỀU XANH):** `test_takeoff_chong_bia.py` **149/149** (17 nhóm A-Q) · `test_qa_data.py` **129/129** · `harness/scripts/check.sh` = **HARNESS GATE: PASS** (import + 21 tool + no-key). Working tree TRACKED sạch, đã push hết, HEAD `a775825` LIVE. (Lưu ý: dùng SCRIPT runner, KHÔNG pytest — pytest crash do test đổi sys.stdout lúc import.)

**Quyết định dài hạn (đã lưu memory):** quy trình củng cố chuẩn (probe→design→adversarial verify) + gotcha TCVN garble (heuristic phải bền garble).

**Đang chờ / bước tiếp:** **G** (mở rộng test đối kháng đa-domain trên KC/KT/9T — khoá regression) + robustness **H** (model fallback 429/503), **I** (chặn file lớn sớm), **J** (dọn file TTL), **K** (tách session), **L** (keep-alive). Dự toán chi phí = HOÃN (chờ đối tác chốt). Trước khi giao rộng: audit an toàn đa-agent + xin 3-5 bản vẽ đơn vị khác + KPI tỷ lệ bịa.

---
## Session 2026-07-10 (d) — Task F: ƯỚC CHIỀU CAO CỘT theo cao độ
**Mục tiêu:** đầu việc F (ROADMAP) — ước "cột cao 1 tầng" ở luồng takeoff lẻ (trước luôn bắt nhập tay). (E đã xong từ trước = goi_y_ghi_san; user chốt bỏ qua E, làm F.)

**Đã làm:**
- **PROBE:** KC typical_floor_h=3.6m (n_tang 2); 9T 3.3m (n_tang 10). `_loai_tu_ban_ve`: C1/C4 loai=[] + mã c<digit>; DM-1={dam}; M1/D1 không phải cột.
- **Nghiên cứu (design panel 3 lens):** CHỐT tách MÓNG ở tầng CÔNG THỨC — `the_tich_be_tong_mong` đổi input chieu_cao sang resolver RIÊNG `_rs_chieu_cao_mong` (luôn hỏi) → móng KHÔNG BAO GIỜ ước, tất định, không phụ thuộc nhãn. `_la_cot` là phòng-thủ-chiều-sâu trong `_rs_chieu_cao_cot`.
- **Triển khai (`tools_core.py`):** `_la_cot(ma)` (nhãn thắng prefix) + `_rs_chieu_cao_cot` (thêm nhánh ước = typical_floor_h×1000mm, cờ gia_dinh_cao_tang/nguon suy_tu_cao_do/chua_chac) + `_rs_chieu_cao_mong`. Propagate `gia_dinh_cao_tang` vào da_co; ghi_chu TÁCH 'GIẢ ĐỊNH 1 tầng' khỏi 'GÁN VỊ TRÍ' (co_gan_dim = nguon=='gan_vi_tri'). Docstring `mcp_server` + SYSTEM_PROMPT.
- **CHỐNG BỊA (suy đoán CÓ CỜ, được phép):** ước LUÔN gắn cờ + nguồn + chua_chac + câu ghi_chu 'xác nhận nếu cột cao khác'; đối tác cấp → override sạch; KHÔNG levels → hỏi (không bịa mặc định); móng KHÔNG ước; `_la_cot`+sai_loai chặn không-cột.
- **⚠ ĐỔI HÀNH VI:** test cũ B 'C1 chưa cấp cao → thieu' NAY thành 'tính được (ước 1 tầng)' → cập nhật. Test D nhóm P.3 (chieu_cao cột không có ứng viên) đổi sang kiểm DISPATCH trực tiếp (vì F nay điền chieu_cao → không còn ở inputs_thieu).
- **KIỂM CHỨNG ĐỐI KHÁNG (3 lens/29 probe) = 0 lỗ hổng** (F1-F7). Móng không ước kể cả mã cột thật C-3; override sạch; đa-cờ 9T lộ đủ.

**Kết quả test:** `test_takeoff_chong_bia.py` **149/149** (nhóm mới **[Q]** 14 ca) · `test_qa_data.py` **129/129** · 21 MCP tool.

**Bài học:** tách hàng rào ở tầng CÔNG THỨC (resolver riêng cho móng) tất định hơn phân biệt trong 1 resolver dùng chung; đổi-hành-vi phải rà MỌI test gọi công thức đó (bắt được cả B lẫn P.3 interaction D↔F).

**Đang chờ:** commit F + push (C+D `4168708` đã live); còn G (test đối kháng đa-domain) + robustness H/I/J/K/L.

---
## Session 2026-07-10 (c) — Task D: ỨNG VIÊN GỢI Ý cho input thiếu (1-click)
**Mục tiêu:** đầu việc D (ROADMAP) — tự nêu ứng viên 'X kg/bộ' / số đo gần mã để đối tác 1-click xác nhận (feedback "AI hỏi nhiều").

**Đã làm:**
- **PROBE:** KT có ghi chú '[67FFC] khung inox 304 ... (1 bé):13.42m= 8.62 kg' = ứng viên kg/bộ VÀNG (khớp inox S1 task B). Cạnh đó '4,35kg' (không /bộ), nhiều 'TỔNG KHỐI LƯỢNG (kG): X' (tổng, nhiễu), 'xà gồ ... 2472.64kg' (tổng). Dim cột C1 có 'ngang=220' (tiết diện) lẫn nhiều '0.0' (nhiễu).
- **Nghiên cứu (design panel 3 lens):** chốt DISPATCH THEO RESOLVER (`rs_name`) không theo 'ten' — vì `chieu_cao` dùng cả `_rs_chieu_cao_cot` (cao độ, KHÔNG gợi: dim 220 là tiết diện không phải chiều cao) lẫn `_rs_bs_only` (tường, gợi được).
- **Triển khai (`tools_core.py`):** `_ung_vien_kg_moi_bo` (verbatim 'X kg', loại 'TỔNG', cờ per-unit `_KG_PU_RE`='(1 …)'/'kg/bộ', KHÔNG proximity) + `_ung_vien_dim` (dim gần mã, đòi code_toks, loại 0.0, LUÔN 'thap'+khoảng cách) + `_ung_vien_cho_input` (dispatch). Gắn `ung_vien` vào từng `inputs_thieu[i]` (chỉ khi non-empty → additive). Docstring `mcp_server` + SYSTEM_PROMPT luật ↳.
- **CHỐNG BỊA:** ứng viên KHÔNG vào vals/da_co, KHÔNG lật co_ket_qua/can_bo_sung; CHỈ `inputs_bo_sung` (đối tác xác nhận) mới tính (đường cũ 137.92 không đổi). kg KHÔNG khẳng định thuộc mã nào (chống bịa liên kết kg-mã, giữ luật task B).
- **KIỂM CHỨNG ĐỐI KHÁNG (1 vòng, 3 lens 27 probe) = 0 lỗ hổng** (D1-D7 giữ). Test [P] tự bắt bug garble 'bộ'->'bé' (perl-unit dùng bare '\bbo\b' → sai) → vá `_KG_PU_RE='(1 …)'` bền garble + không nhầm '02 bộ bản lề' (phụ kiện).

**Kết quả test:** `test_takeoff_chong_bia.py` **134/134** (nhóm mới **[P]** 14 ca) · `test_qa_data.py` **129/129** · 21 MCP tool (D KHÔNG thêm tool — ứng viên nằm trong response `tinh_dai_luong`).

**Bài học:** garble TCVN 'bộ'->'bé' lặp lại (như 'diÖn tÝch' ở C) → heuristic từ-khoá phải BỀN garble; dispatch theo RESOLVER (không theo tên input) tránh gợi sai cho cao-độ-cột.

**Đang chờ:** commit D + push (C `4113a8a` đã commit CHƯA push); còn F (ước cao cột theo cao độ), G (test đa-domain) + robustness H/I/J/K/L.

---
## Session 2026-07-10 (b) — Task C: LIỆT KÊ DIỆN TÍCH GHI SẴN
**Mục tiêu:** nghiên cứu chi tiết + triển khai đầu việc C (ROADMAP) — liệt kê nhãn 'X m²' ghi sẵn (verbatim + handle) để đối tác đối chiếu/cấp diện tích sàn.

**Đã làm:**
- **PROBE file thật TRƯỚC (⚠ ROADMAP yêu cầu):** KT Gia Lộc có ~17-20 nhãn m² HỖN TẠP (mái 634, sàn 591/545, sơn 117/44.5/38.1, tường 77.5, granit 52/30/22, trống 67/22.7/18/11 [garbled 'diÖn tÝch'], vách 3.3); KC có 'mật độ 16 cọc//1m2' NHIỄU + 'diện tích 7,04 m2' THẬT; KC 9T = 0 nhãn; hạ tầng 9 nhãn 'S=…m2'. → KẾT LUẬN: nhãn KHÔNG đều là 'sàn' → phải liệt kê verbatim, KHÔNG phân loại.
- **Nghiên cứu (design panel 3 lens: chống-bịa/UX/regex):** chốt hợp đồng mirror `stated_vol`.
- **Triển khai (`tools_core.py`):** `_build_stated_areas` + `self.stated_area` + `_STATED_M2_RE` + `_DT_KW_RE`; method `liet_ke_dien_tich_ghi_san` (trả {co_du_lieu, so_nhan, so_co_tu_khoa, danh_sach[{text,m2,handle,layer,co_tu_khoa_dien_tich}], goi_y khi 0, ghi_chu}, KHÔNG có field tổng). Tích hợp `tong_hop_khoi_luong` loại 'Diện tích (ghi sẵn)' + `_khong_cong` (KHÔNG cộng gộp mái+sơn+granit). MCP tool #21 + SYSTEM_PROMPT luật 14.
- **CHỐNG BỊA:** không khẳng định 'sàn', không suy hình học (0 nhãn → gợi ý đối tác CẤP), không cộng gộp; lọc mật độ + đuôi thập phân; mã DM2/mm2 tự loại; KHÔNG min (giữ 0.12m²).
- **KIỂM CHỨNG ĐỐI KHÁNG (loop-until-dry):** test [O] tự bắt **bug BỊA đuôi thập phân** ('117m2/44,5m2' → bịa 4.5/8.1) → vá regex `(?<![/.,\d])`. Vòng 1 (3 lens) bắt **density-space** ('16 cọc/ 1m2' → bịa 1.0) → vá normalize `'/\s+'→'/'`. Vòng 2 (2 lens) xác nhận MỌI vector BỊA đã kín; 3 ca còn lại là DROP-class (comma-no-space/slash-area/dedup) — an toàn (không bịa) + verbatim giữ đủ + không xuất hiện trên file thật → GHI CHÚ giới hạn (thất bại phải lộ), KHÔNG vá (fix mong manh).

**Kết quả test:** `test_takeoff_chong_bia.py` **120/120** (nhóm mới **[O]** 15 ca) · `test_qa_data.py` **129/129** · `check.sh` **PASS** (21 MCP tool).

**Bài học:** probe TRƯỚC khi thiết kế là quyết định (data thật cho thấy nhãn hỗn tạp → chốt "không phân loại"); test tự bắt bug bịa số thập phân trước cả adversarial → viết test-với-số-kỳ-vọng đáng giá.

**Đang chờ / bước tiếp:** commit + push (CHƯA — chờ user); D (ứng viên kg/bộ 1-click), F (ước cao cột), G (test đa-domain) + robustness H/I/J/K/L.

---
## Session 2026-07-10 — Task B: TRỪ LỖ cửa/cửa sổ (xây tường & trát)
**Mục tiêu:** nghiên cứu chi tiết + triển khai đầu việc B (ROADMAP) — trừ lỗ cửa/cửa sổ khi tính xây tường & trát.

**Đã làm:**
- **Nghiên cứu (workflow design panel 3 lens):** chống-bịa / hợp-đồng-UX / QS-xây-dựng → CHỐT hợp đồng: `lo_cua` (list) trong `inputs_bo_sung`, chỉ cho `xay_tuong` + `dien_tich_trat` (cờ `tru_lo`). Nguyên tắc mirror INOX: CODE cấp phần verify được (R×C), ĐỐI TÁC khai phần không tự-liên-kết (mã+SL lỗ) — hệ KHÔNG tự đoán cửa nào thuộc tường nào.
- **Triển khai (`tools_core.py`):** `_resolve_lo_cua` + `_sl_hop_le` + tích hợp trong `tinh_dai_luong`. Mỗi lỗ: `{ma,sl}` (tra `door_size_index` confident, có handle) HOẶC `{rong,cao,sl}` (mm, đối tác cấp; nhận cả `sl`/`so_luong`). net = gross − Σ(R×C×SL)×(be_day/1e9 | so_mat/1e6). KHÔNG cộng reveal/bệ cửa (lộ ghi chú). Cập nhật docstring `mcp_server.py` + SYSTEM_PROMPT `mcp_bridge.py` để Gemini biết dùng + trình bày gross→net.
- **Backward-compat tuyệt đối:** không `lo_cua`/`[]` → số CŨ y hệt, KHÔNG field mới → 76 test cũ không đổi.
- **KIỂM CHỨNG ĐỐI KHÁNG (loop-until-dry, workflow đa-agent):** Vòng 1 (4 lens) bắt **4 bug THẬT** (đã chạy xác nhận): (1) over-count lách bằng tách 1 mã thành nhiều entry (36 d2 > 18); (2) net làm tròn về 0.0 vẫn báo co_ket_qua=True; (3) `sl` vs `so_luong` mâu thuẫn bị bỏ im lặng; (4) sl khổng lồ → so_lo là int 300 chữ số. → VÁ cả 4 (cộng dồn per-code canonical; gate net<=0 SAU làm tròn; block khi sl≠so_luong; trần `_SL_LO_MAX=100000`). Vòng 2 (3 lens, 25+ ca) = **DRY, 0 lỗ hổng** — mọi biến thể hoa/thường/gạch/space/unicode/NaN/overflow đều BLOCK an toàn.

**Kết quả test:** `test_takeoff_chong_bia.py` **103/103** (nhóm mới **[N]** 27 ca trừ lỗ, gồm N.4 hardening 4 bug) · `test_qa_data.py` **129/129** (không regression) · `harness/scripts/check.sh` = **HARNESS GATE: PASS**.

**Quyết định thiết kế (đã cân nhắc):** (1) chuỗi số "900"→900 GIỮ (đồng nhất `_nd` toàn hệ, Gemini hay gửi số dạng chuỗi) — KHÔNG coi là lỗi kiểu; (2) mode kích-thước-trực-tiếp KHÔNG có trần `_door_qty_for` (dims+SL đối tác cấp, không verify được) — chỉ trần-mỗi-lỗ 100000 + gate net>0 + cờ `confident=False` minh bạch; (3) so sánh `==trần` được PHÉP (đối tác có thể có đúng N lỗ), `trần+1` chặn.

**Đang chờ / bước tiếp:** commit (CHƯA commit — chờ user duyệt); các củng cố treo còn lại C/D/F/G + robustness H/I/J/K/L (xem `feature_list.json` + `ROADMAP_DEMO2.md`).

---
## Session 2026-07-09 — Chốt demo 2 + củng cố + tích hợp Harness
**Mục tiêu:** phản hồi feedback đối tác (chọn demo 2, thêm tính năng inox) → củng cố → tích hợp bộ Harness cho demo 2.

**Đã làm:**
- **Quyết định chiến lược:** đối tác test 2 demo → ưng demo 2. Rà soát bằng chứng (tốc độ do MODEL flash-vs-pro, không phải kiến trúc; "thất bại" demo 2 là giới hạn CHUNG/chống-bịa). → **CHỐT demo 2 là sản phẩm chính, DỪNG demo 1.** "2 demo cân bằng" NGHỈ.
- **Vá parity cm/mm + đọc bảng cột nhà 9T** (`_build_section_index` ghép tọa độ + ngưỡng 130 + cờ mơ hồ): 9T C-3 = 80×80cm → 23.04 m³ (khớp demo 1); Gia Lộc 4.704 m³ không đổi. `2a90a36`.
- **Endpoint `/version`** verify deploy qua HTTP. `e870074`.
- **Tính năng INOX = SL(đọc)×kg/bộ(đối tác cấp)** (feedback): inox S1 = 16×8.62 = **137.92 kg**. `c034312`.
- **Kiểm chứng ĐỐI KHÁNG (workflow đa-agent):** bắt lỗ `inf`/tràn số/`bool` lọt cổng ra "Infinity kg" → hardening (`_nd` từ chối bool/inf/nan + `math.isfinite` + kiểm KẾT QUẢ hữu hạn). `c034312`.
- **Vá 3 lỗ BỊA SỐ** (workflow roadmap chạy code): mã toàn chữ "GHOSTINOX", "thể tích sàn" tự vơ diện tích, "thể tích inox" lệch đại lượng. `4c597f3`.
- **Củng cố A + E:** tổng phụ theo (loại,đơn vị) + gợi ý m³ ghi sẵn (đào đất thiếu → nêu "ĐÀO MÓNG 860 M3"). `dd8d971`.
- **Tài liệu chiến lược:** ROADMAP_DEMO2 (hoãn dự toán chi phí `fe4972c`), KE_HOACH_TONG_QUAT_HOA (độ phủ vs độ an toàn, KPI 0% bịa `dd8d971`), NGHIEN_CUU_AI_TU_HOC (tự học an toàn `2f51a8b`).
- **Tích hợp HARNESS:** tạo `harness/` 12 file (project-overview, tech-stack, feature_list.json 27 đầu mục, AGENTS, rubric, quality-document, clean-state-checklist, session-handoff, claude-progress, README, benchmark_questions, scripts/check.sh). `de61ac5`.

**Kết quả test:** `test_takeoff_chong_bia.py` **76/76 PASS** (nhóm A-M) · `test_qa_data.py` đọc **129/129 PASS** · `harness/scripts/check.sh` = **HARNESS GATE: PASS** (20 MCP tool + no-key). Deploy live, `/version` verify từng commit.

**Quyết định dài hạn:** (1) demo 2 = sản phẩm chính, bỏ demo 1; (2) phạm vi = ĐỌC + tính KHỐI LƯỢNG, dự toán chi phí HOÃN chờ đối tác chốt; (3) ưu tiên ĐỘ AN TOÀN > độ phủ (KPI ~0% bịa); (4) AI tự học (nếu làm) = học CÁCH ĐỌC không học SỰ THẬT, hóa-cứng thì người duyệt.

**Bài học:** TÔI từng đẩy "dự toán chi phí (thành tiền)" lên P0 dựa trên tầm nhìn gốc dự án — nhưng đối tác CHƯA yêu cầu và phạm vi vốn "chưa chốt" → sai ưu tiên, user bắt đúng. → Phân biệt "đối tác đã yêu cầu" vs "tôi suy từ tầm nhìn"; không tự nâng scope hoãn thành hướng chính.

**Đang chờ / bước tiếp:** củng cố treo B/C/D/F/G + robustness H/I/J/K/L (xem `feature_list.json` + `../ROADMAP_DEMO2.md`); trước khi giao rộng: audit an toàn đa-agent + xin 3-5 bản vẽ đơn vị thiết kế khác + dựng KPI "tỷ lệ bịa".
