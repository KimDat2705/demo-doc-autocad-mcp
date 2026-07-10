# Harness — demo 2 (đọc & tính khối lượng bản vẽ qua MCP)

Bộ "kỷ luật kỹ thuật" theo chuẩn **Harness Engineering**, adapt cho app Python/Flask + MCP.
Mục tiêu: **chứng minh chất lượng bằng BẰNG CHỨNG** (không nói miệng) + cho một phiên mới tinh nắm được **bức tranh
tổng quát** (hệ thống là gì / tổ chức ra sao / chạy-kiểm thế nào / tiến độ tới đâu) chỉ bằng đọc repo.

> ℹ️ Trước đây có 2 demo (demo 1 gọi trực tiếp vs demo 2 MCP) chấm chung "cây thước" để so sánh. **2026-07-09 đã CHỐT
> demo 2 là sản phẩm chính, DỪNG demo 1** → khung "so sánh A vs B" NGHỈ. Harness này giờ phục vụ chất lượng của RIÊNG demo 2.

## Các file
| File | Vai trò |
|---|---|
| `project-overview.md` | ⭐ **BỨC TRANH TỔNG QUÁT** — Cold-Start 5 câu hỏi + giai đoạn + đầu mục đã/chưa làm |
| `tech-stack.md` | Công nghệ sử dụng + **LƯU TRỮ/database** (không có DB — in-RAM + file) |
| `feature_list.json` | Đầu mục tính năng + status (done/partial/planned/deferred) + **bằng chứng** |
| `AGENTS.md` | Quy tắc khởi động + lệnh kiểm tra + Definition of Done + 4 nguyên tắc chống overfit |
| `evaluator-rubric.md` | Chấm 1–5 theo 9 tiêu chí (mức nhiệm vụ) + bảng điểm demo 2 |
| `quality-document.md` | Bảng điểm theo chiều (A/B) + bằng chứng cổng + **giới hạn thật** (không tô hồng) |
| `clean-state-checklist.md` | Checklist trước commit / cuối phiên |
| `session-handoff.md` | Bàn giao phiên (làm gì / còn gì / quyết định / file sửa / commit) |
| `benchmark_questions.json` | Bộ câu hỏi + đáp án chuẩn (đọc từ file thật) — neo về tiêu chí rubric |
| `scripts/check.sh` | Cổng: import+đếm tool / no-key / test chống bịa → "HARNESS GATE: PASS/FAIL" |

## Chạy các cổng (từ `demo_mcp_autocad/`)
```bash
bash harness/scripts/check.sh            # import + đếm tool + no-key + test chống bịa (76/76)
python tests/test_takeoff_chong_bia.py   # 76/76 offline (không tốn API)
python tests/test_qa_data.py             # 129/129 đọc dữ liệu (cần ../input_files/_dxf + ../demo_doc_autocad)
```

## Điểm hiện tại (demo 2): xem `quality-document.md`
Mạnh: đọc chính xác + chống bịa (đã hardening đối kháng) + **takeoff/tính khối lượng** + trực quan khoanh đỏ + MCP chuẩn.
Giới hạn thật: dự toán chi phí HOÃN; một số củng cố/robustness còn treo (xem `feature_list.json`).
