# Quality Document — demo 2 (chấm theo chuẩn Harness)

**Ngày:** 2026-07-09 · **Người chấm:** Tự động (test tất định + workflow đối kháng) + thủ công (đối chiếu file thật) ·
**Phạm vi:** Đọc dữ liệu + TÍNH khối lượng (takeoff). Dự toán chi phí = HOÃN (không tính điểm).

## Bảng điểm theo chiều
| Chiều | Hạng | Bằng chứng |
|---|---|---|
| Import / Build | **A** | `import tools_core` sạch; 20 MCP tool; requirements đủ (8 gói) |
| Bảo mật (key) | **A** | `grep AIza` source = 0; key qua env `GEMINI_API_KEY` |
| Đọc cơ bản (layer/đối tượng/dim) | **A** | QA đọc 129/129 (đối chiếu ezdxf ground truth + demo1 port-faithfulness, 3 file) |
| Số lượng cấu kiện THẬT | **A** | cửa D1=24/S1=16, tổng 73; đa quy ước + fold font TCVN3 |
| Khối lượng thép (tròn + hình/inox) | **A** | KC 67370.7 kg; tách loại; cảnh báo không gộp |
| Chống bịa / ảo giác | **A** | mã giả→không tìm thấy; inf/tràn/bool→chặn; **workflow đối kháng bắt+vá lỗ inf + 3 lỗ bịa số** |
| **Takeoff / TÍNH khối lượng** | **A** | 12 công thức; cửa 84.24 m²; cột 4.704 m³; inox S1 137.92 kg; 9T C-3 23.04 m³ (cm) |
| Trực quan (khoanh đỏ ảnh) | **A** | render_region + highlight + largest_cluster; điểm khác biệt cốt lõi demo 2 |
| Tổng quát / chống overfit | **A** | 9T(cm)/Gia Lộc(mm)/hạ tầng — cm/mm tự nhận ngưỡng 130; test đa-domain |
| Phân tầng độ tin cậy | **B+** | cờ verbatim/gán-vị-trí/suy_doan_don_vi/tạm-tính; gán-dim còn tinh chỉnh |
| Test hồi quy | **A** | test_takeoff_chong_bia 76/76 (13 nhóm A-M) + đọc 129/129, offline |
| Deploy + verify cloud | **A** | Render live + `/version` (commit + sect_cm_max=130); nhiều lần commit→push→verify |
| Vận hành (robustness) | **B** | 1 phiên/1 người OK; concurrency/TTL/model-fallback/file-lớn còn treo (roadmap H-L) |
| Hoàn thiện phạm vi | **A-** | Đọc + takeoff KHỐI LƯỢNG ~hoàn chỉnh; củng cố B/C/D/F/G còn treo; dự toán chi phí HOÃN |

## Điểm tổng (theo evaluator-rubric, 9 tiêu chí): **4.8 / 5**

## Bằng chứng cổng chất lượng
- Import: OK, 20 MCP tool
- Không key trong source: OK (grep AIza = rỗng)
- Test chống bịa takeoff: **76 PASS / 0 FAIL** (offline)
- QA đọc dữ liệu: **129 PASS / 0 FAIL**
- Cloud live: `/version` = commit khớp + `sect_cm_max:130` + `has_section_index:true`

## Thành thật về GIỚI HẠN (không tô hồng)
1. **Dự toán CHI PHÍ (thành tiền) = CHƯA làm** — HOÃN chờ đối tác chốt yêu cầu (phạm vi demo = khối lượng). Không phải lỗi.
2. **Độ phủ sẽ luôn có lỗ hổng** (bản vẽ VN không chuẩn) — chấp nhận; điều bảo đảm là **độ AN TOÀN** (gặp lạ → thú nhận, không bịa). KPI = "tỷ lệ bịa ≈ 0%", KHÔNG phải "trả lời 100%".
3. **Vận hành:** Render free ngủ 15p (cold-start chậm lượt đầu); 1 worker + 1 DRAWING chung → 2 người dùng đạp nhau; chưa dọn file TTL; file >45MB (vd 9T 114MB) bị chặn (cần nâng plan). Roadmap H/I/J/K/L.
4. **Model:** 2.5-flash ổn + nhanh; chưa có chuỗi model phụ khi 429/503 kéo dài (roadmap H).
5. **Củng cố còn treo:** trừ lỗ cửa khi xây/trát (đang tính vượt), liệt kê diện tích ghi sẵn, ứng viên kg/bộ 1-click.

## Kết luận
Demo 2 **ĐẠT chuẩn harness ở phạm vi ĐỌC + TÍNH KHỐI LƯỢNG**: chính xác, chống bịa (đã qua đối kháng), tính được takeoff,
trực quan khoanh đỏ, MCP chuẩn, có test/handle + deploy/verify. Điểm trừ đã ghi rõ (dự toán HOÃN + robustness treo), không che giấu.
