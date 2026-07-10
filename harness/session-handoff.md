# Session Handoff — demo 2

## Trạng thái hiện tại (2026-07-10 — TASK B trừ lỗ cửa | trước đó: chốt demo 2 + tích hợp HARNESS)
> Mỗi tuyên bố "xong" kèm BẰNG CHỨNG (commit + số test) truy được. Nhật ký chi tiết hơn: `GHI_CHU_HOAN_THIEN.md`.

- **✅ TASK B — TRỪ LỖ cửa/cửa sổ (xây tường & trát) [2026-07-10]:** `xay_tuong`/`dien_tich_trat` nhận `lo_cua` (list) trong `inputs_bo_sung` — mỗi lỗ `{ma,sl}` (tra `door_size_index` confident, có handle) HOẶC `{rong,cao,sl}` (mm). net = gross − Σ(R×C×SL)×(be_day|so_mat). SL do ĐỐI TÁC khai (mirror inox — KHÔNG tự đoán cửa nào thuộc tường nào). Backward-compat: không `lo_cua` → số cũ y hệt. Kiểm chứng đối kháng 2 vòng (loop-until-dry): vòng 1 bắt 4 bug thật → vá (over-count cộng dồn per-code; net<=0 SAU làm tròn; block `sl`≠`so_luong`; trần SL 100000); vòng 2 DRY. Code: `_resolve_lo_cua`/`_sl_hop_le`/`tinh_dai_luong` (`tools_core.py`) + docstring `mcp_server.py` + SYSTEM_PROMPT `mcp_bridge.py`. Test **[N] 27 ca** (`test_takeoff_chong_bia.py` 103/103). ⚠ CHƯA commit — chờ user duyệt.
- **QUYẾT ĐỊNH CHIẾN LƯỢC:** đối tác test 2 demo → ưng demo 2. Rà soát: khác biệt tốc độ do MODEL (demo 1 pro vs demo 2 flash), không phải kiến trúc; "thất bại" demo 2 (inox/diện tích sàn) là giới hạn CHUNG/chống-bịa. → **Chốt demo 2 là sản phẩm chính, DỪNG demo 1.** Nguyên tắc "2 demo cân bằng" NGHỈ.
- **VÁ PARITY cm/mm + đọc bảng cột nhà 9T** (`_build_section_index` ghép tọa độ + ngưỡng 130 + cờ mơ hồ): 9T C-3 = 80×80cm → **23.04 m³ KHỚP demo 1**; Gia Lộc mm 4.704 m³ không đổi. Commit `2a90a36`.
- **Endpoint `/version`** (RENDER_GIT_COMMIT + sect_cm_max + has_section_index) — verify deploy qua HTTP. Commit `e870074`.
- **Tính năng INOX = SL(đọc) × kg/bộ(đối tác cấp)** (feedback đối tác): inox S1 = 16×8.62 = **137.92 kg**. Commit `c034312`.
- **Kiểm chứng ĐỐI KHÁNG (workflow đa-agent) → hardening:** bắt lỗ `inf`/tràn số (16×1e308)/`bool` lọt cổng ra "Infinity kg" → vá `_nd` từ chối bool/inf/nan + cổng `math.isfinite` + kiểm KẾT QUẢ hữu hạn. Commit `c034312`.
- **Vá 3 lỗ BỊA SỐ** (workflow roadmap chạy code phát hiện): mã toàn chữ "GHOSTINOX"; "thể tích sàn" mã trống tự vơ diện tích; "thể tích inox" lệch đại lượng. Commit `4c597f3`.
- **Củng cố A + E:** tổng phụ theo (loại,đơn vị) trong tổng hợp+Excel; gợi ý m³ ghi sẵn (đào đất thiếu số → nêu "ĐÀO MÓNG 860 M3" [handle]). Commit `dd8d971`.
- **Tài liệu chiến lược:** ROADMAP_DEMO2 (hoãn dự toán chi phí, `fe4972c`), KE_HOACH_TONG_QUAT_HOA (độ phủ vs độ an toàn, KPI 0% bịa, `dd8d971`), NGHIEN_CUU_AI_TU_HOC (tự học an toàn, `2f51a8b`).
- **TÍCH HỢP HARNESS:** tạo `harness/` (12 file) — project-overview, tech-stack, feature_list.json (27 đầu mục), AGENTS.md, rubric, quality-document, clean-state-checklist, session-handoff, **claude-progress.md** (nhật ký phiên), README, benchmark_questions, scripts/check.sh. `check.sh` = **HARNESS GATE: PASS** (import + 20 tool + no-key + 76/76). Commit `de61ac5` (+ chốt sổ phiên cuối).
- **Test (chốt sổ 2026-07-09):** `test_takeoff_chong_bia.py` **76/76** (nhóm A-M) + đọc **129/129** + `check.sh` PASS. Deploy live + `/version` verify mỗi commit. Working tree sạch.
- **⚠ Lưu ý cấu trúc:** demo 2 KHÔNG có `specs/specs.json` (theo quy ước Harness đã ghi ở `AGENTS.md`) — `feature_list.json` thay cho specs/. Rà trạng thái tính năng ở `feature_list.json`, KHÔNG tìm specs/.

## Còn lại / Bước tiếp (xem `feature_list.json` + `ROADMAP_DEMO2.md`)
- **Củng cố treo:** ~~B (trừ lỗ cửa) — XONG 2026-07-10~~; C (liệt kê diện tích ghi sẵn), D (ứng viên kg/bộ 1-click), F (ước cao cột theo cao độ), G (test đối kháng đa-domain).
- **Robustness treo:** H (model fallback 429/503), I (chặn file lớn sớm), J (dọn file TTL), K (tách session), L (keep-alive + giám sát).
- **Đề xuất trước khi giao rộng:** audit an toàn đa-agent trên MỌI tool; xin 3-5 bản vẽ đơn vị thiết kế khác nhau; dựng KPI "tỷ lệ bịa".

## Quyết định đã chốt (chống lật lại)
- **Demo 2 = sản phẩm chính, DỪNG demo 1.** "2 demo cân bằng" nghỉ.
- **Phạm vi = ĐỌC + tính KHỐI LƯỢNG.** DỰ TOÁN CHI PHÍ (thành tiền) = HOÃN chờ đối tác chốt yêu cầu.
- **KHÔNG training/fine-tune** — tool-use. **KHÔNG** hardcode key. Ưu tiên **độ AN TOÀN > độ phủ** (KPI ~0% bịa).
- **AI tự học** (nếu làm): học CÁCH ĐỌC (verify được), KHÔNG học SỰ THẬT; hóa-cứng thì người duyệt.

## File quan trọng
- Code: `app.py`, `mcp_bridge.py`, `mcp_server.py`, `tools_core.py`, `dwgconv.py`, `vntext.py`
- Test: `tests/test_takeoff_chong_bia.py`, `tests/test_qa_data.py`
- Tài liệu: `GHI_CHU_HOAN_THIEN.md`, `ROADMAP_DEMO2.md`, `KE_HOACH_TONG_QUAT_HOA.md`, `NGHIEN_CUU_AI_TU_HOC.md`, `harness/`
- Cloud: https://doc-autocad-mcp-demo.onrender.com · repo private `KimDat2705/demo-doc-autocad-mcp`
