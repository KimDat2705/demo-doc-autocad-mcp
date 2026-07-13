# 🔴 KẾT QUẢ RED-TEAM ĐA-AGENT — THIẾT KẾ P3 (MỞ KÊNH HỌC "AI tự học")

> Chạy 2026-07-13, TRƯỚC khi viết 1 dòng code P3 (đúng quy trình chốt: P3 = ranh giới rủi ro CAO NHẤT,
> cần red-team đa-agent mạnh trước). Bản này là tầng KIỂM ĐỊNH ĐỐI KHÁNG của
> [`KE_HOACH_AI_TU_HOC_CHI_TIET.md`](KE_HOACH_AI_TU_HOC_CHI_TIET.md) §2–§6.
>
> **Workflow:** 119 agent — 9 hướng tấn công song song (đọc code THẬT + neo finding) → mỗi finding qua
> **3 giám định độc lập mặc-định-refute** (lăng kính code-reality / design-blocks / exploitability) → chỉ sống sót
> khi ≥2 CONFIRMED (hoặc 1 CONFIRMED & 0 REFUTE) → completeness-critic → tổng hợp spec gia cố.
> **Kết quả: 36 finding → 24 SỐNG SÓT (5 CAO · 15 TRUNG BÌNH · 4 THẤP).**
>
> **Xác minh lại trên code thật (không tin mù subagent — [[feedback-bia-tai-sinh-tang-code]]):** 2 finding CAO
> chặn-ship (R1, R2) neo vào code ĐANG TỒN TẠI đã được TỰ tái hiện: `co_gan_dim` (tools_core.py:1871) chỉ
> whitelist `nguon=='gan_vi_tri'`; nhánh ghi_chu "đáng tin" (:1889); `resp` (:1902) thiếu cờ `chua_chac`.
> **R1 là lỗ tồn tại NGAY BÂY GIỜ trong đường E2 xác-nhận-theo-handle** (ship ở P-1), không chỉ thiết kế P3.

---

## 1. TÓM TẮT RỦI RO (đã tái-giám định)

**Khung chốt:** bàn giao THỰC tới đối tác là **prose `r.answer` của Gemini** (app.py → `bot`), được nạp
`inputs_thieu[].ung_vien` + `ghi_chu`. Vì thế cụm "nhãn độ-tin-cậy sai" NẶNG hơn mức "cờ cấu trúc bị chôn" —
đó đúng là thứ LLM đọc-và-thuật lại cho đối tác.

### CAO — chặn ship tới khi vá (vá NẰM TRONG P3, KHÔNG lùi sang P4)

| # | Lỗ (gộp finding) | Neo code | Vá bắt buộc |
|---|---|---|---|
| **R1** | `flow-dang-tin-mislabel-1` + `dang-tin-note-mislabels-1` + `resp-no-toplevel-chuachac-1`: input `chua_chac=True` nguồn ≠ `gan_vi_tri` (E2, P3) bị dán "đọc trực tiếp từ file (đáng tin)"; `resp` thiếu cờ `chua_chac` máy-đọc → LLM thuật số CHƯA CHẮC là "đáng tin". | tools_core.py:1871, :1888-1889, :1902 | Điều kiện nhánh = `not any(x['chua_chac'] for x in da_co)`; thêm `resp['chua_chac']` + `resp['can_doi_chieu']`. |
| **R2** | `flow-no-provenance-gate-2`: không cổng nào đọc `so_file_da_kiem`/nguồn-học; tập input toàn-học đã xác-nhận → `thieu` rỗng → `compute` → `co_ket_qua=True, ket_qua=<số>, so_file_da_kiem=0`. | tools_core.py:1789, :1831, :1902 | **Cổng provenance TRUNG TÂM** (§2.6): input `nguon` bắt đầu `doc_lai_theo_quy_uoc`/`doi_tac_xac_nhan_learned` HOẶC `so_file_da_kiem<3` → ép `co_ket_qua=False`, trả `uoc_luong_hoc` + `can_bo_sung=True`. |
| **R3** | `substring-token-boundary-1` + `substring-gate-vs-to-num-vn-1000x` + `substring-mu-don-vi-1` + `enum-unit-laundering-cm-mm`: cổng "chuỗi-con" (KE_HOACH bước c) là substring KÝ-TỰ → `'1'⊂'1250'`, `'8'⊂'8.62'` lọt; mù đơn vị (cm↔mm 100×); mâu thuẫn `_to_num_vn` (`'1.130'`→1130 vs 1.13). | KE_HOACH §2.4 bước c; tools_core.py `_to_num`/`_to_num_vn` | Thay bằng **khớp TOKEN NGUYÊN VẸN** + parser đúng + cổng đơn-vị/biên theo `y_nghia` (§2.2 bước 7-8). |
| **R4** | `y-nghia-khac-wildcard` + `ma-anchor-khong-kiem-band-2` + `in-block-attribute-ngap-residual`: `y_nghia='khac'` không parser/đơn-vị/biên; NEO chỉ đòi residual, KHÔNG đòi anchor gần `ma_cau_kien` → số vô chủ / note chéo-mã thành ứng viên handle-thật; residual bị attribute-noise thống trị. | KE_HOACH §2.3; tools_core.py `_build_used_handles` | **Bỏ `'khac'`**; MỌI `y_nghia` buộc `anchor.vn` chứa `_tok_bound(ma_cau_kien)` HOẶC từ-khoá loại; đăng ký thép-handle vào `used_handles`. |

*(R5 gốc "dang-tin-note-mislabels-1" đã gộp vào R1.)*

### TRUNG BÌNH — vá trong P3

| # | Lỗ | Vá |
|---|---|---|
| **R5** | `flow-substring-cherrypick-3` + `kg-bien-vo-dinh-1`: anchor đa-số + thiếu trần kg → chọn nhầm '8000 kG' (tải) làm kg/bộ; `_ung_vien_kg_moi_bo` (:1325) chỉ chặn `val>0`. | ràng số kề dấu-hiệu `y_nghia` (`_KG_PU_RE`); từ chối khi ≥2 số hợp-`y_nghia`; thêm `_KG_PU_MAX`, áp cho CẢ kênh cũ lẫn học. |
| **R6** | `confirm-laundered-via-nd-1` + `confirm-channel-not-wired-1`: `_ung_vien_cho_input` (:1379-1386) KHÔNG đọc `hoc_phien` → kênh giữ-provenance chết; đối tác bị dồn gõ SỐ TRẦN → `_nd` (:541) tẩy `chua_chac=False`. | nối `hoc_phien` vào `_ung_vien_cho_input`; `bs[ten]` khớp giá trị ứng viên học → ép `chua_chac=True`, không qua `_nd` trần. |
| **R7** | `thu-hoi-khong-loc-o-cua-xac-nhan-2` + `relearn-same-handle-duplicate-rules` + `spam-no-cap-dedupe-purge-3`: `thu_hoi` chỉ đánh cờ; đọc rải rác; không dedupe/cap. | helper `_quy_tac_hieu_luc()` TẬP TRUNG (grep-guard); `thu_hoi` XÓA khỏi RAM + ghi WORM; dedupe `(anchor_handle,y_nghia,template_id)` + cap 200. |
| **R8** | `llm-goi-hoc-quy-uoc-tu-dong-1`: `gemini_tools` phơi mọi tool trừ `nap_ban_ve` → chữ-file lái LLM tự GHI quy ước không cổng người-thật. | thêm `hoc_quy_uoc`+`thu_hoi_quy_uoc` vào loại-trừ (mcp_bridge.py:173); chỉ gọi từ UI app.py. |
| **R9** | `filehash-uuid-defeats-3domain-gate-1` + sid-less: `hoclog` băm path uuid, không truyền `sid` → gate P5 "≥3 domain" bị 1 đối tác re-upload đánh lừa. | `content_hash=sha1(bytes gốc)` làm `file_id`; truyền `sid_hash`. |

### THẤP — defense-in-depth (ghi nợ có ticket)

| # | Lỗ | Vá |
|---|---|---|
| **R10** | `grepguard-nonrecursive-substring-2`: grep-guard "không reader" chỉ quét ROOT/*.py non-recursive + substring cứng. | `os.walk` đệ quy + kiểm AST. |
| **R11** | `render-artifact-idor-3`: `/file/<id>`, `/image/<id>` phục vụ theo basename KHÔNG kiểm chủ-phiên → phiên B tải Excel/ảnh của phiên A. | gắn `s['artifacts']`, 404 nếu không thuộc phiên. |

---

## 2. SPEC P3 GIA CỐ

### 2.1 Chữ ký + ENUM template

```python
# ENUM template_id CỐ ĐỊNH — dev cấp parser, KHÔNG regex do đối tác/LLM đưa. Ngoài tập -> FAIL-CLOSED.
_TEMPLATE_ENUM = {
    "SL_NGUYEN":     dict(y_nghia="so_luong",  parser="_p_int",        don_vi=None, lo=1,        hi=_SL_LO_MAX),
    "KICH_THUOC_MM": dict(y_nghia="kich_thuoc",parser="_p_dim_mm",     don_vi="mm", lo=None,     hi=None),   # qua _sect_to_mm
    "TIET_DIEN_AXB": dict(y_nghia="tiet_dien",  parser="_p_axb",       don_vi="mm", lo=None,     hi=None),   # qua _plausible_section_mm
    "KG_PER_UNIT":   dict(y_nghia="kg_moi_bo",  parser="_p_kg_per_unit",don_vi="kg", lo=_KG_PU_LO,hi=_KG_PU_MAX),
}
_KG_PU_LO, _KG_PU_MAX = 0.01, 5000.0   # trần kg/bộ hợp lý (TẠM — hiệu chỉnh theo corpus P5)

def hoc_quy_uoc(self, anchor_handle, template_id, ma_cau_kien, y_nghia=""):
    """Học CÁCH ĐỌC theo PHIÊN (ánh xạ handle THẬT -> diễn giải). KHÔNG lưu SỐ; re-parse mỗi lần dùng.
    Trả {ok, rule_id, ung_vien_xem_truoc} hoặc {ok:False, tu_choi, ly_do}."""

def thu_hoi_quy_uoc(self, rule_id=""):
    """rule_id rỗng -> thu hồi TẤT CẢ. XÓA phần tử khỏi self.hoc_phien (KHÔNG chỉ đánh cờ) + ghi WORM 'thu_hoi'."""
```

**Data model rule (khác gốc):** `{rule_id, anchor_handle(THẬT), y_nghia∈{so_luong,kich_thuoc,tiet_dien,kg_moi_bo},
template_id(ENUM), ma_ap_dung, suy_doan_don_vi, xung_dot, nhan='theo đối tác, chưa xác nhận', nguon='doi_tac_day',
scope='PHIEN', so_file_da_kiem=0, created_ts}` — **KHÔNG có cờ `thu_hoi`** (dùng XÓA, không đánh cờ).

### 2.2 Cổng `hoc_quy_uoc` (thứ tự, fail-closed)

1. **ENUM (R3):** `template_id in _TEMPLATE_ENUM` else từ chối; `y_nghia` (nếu cấp) khớp enum. **Bỏ `'khac'`** (R4).
2. **NEO + tái-kiểm:** `anchor_handle` ∈ `self.texts` VÀ ∈ `{t['handle'] for t in self._residual_texts()}`.
3. **NGỮ CẢNH (R4):** `anchor.vn` chứa `_tok_bound(ma_cau_kien, _norm_label(anchor.vn))` HOẶC từ-khoá loại theo `y_nghia`. Không neo → từ chối ('150' trục lưới không gán T1).
4. **KHÔNG câu-mệnh-lệnh:** tái dùng `_co_chi_thi_dang_ngo` — anchor không phải câu văn dài/có động từ mệnh lệnh.
5. **Không-đã-tiêu-thụ (R4):** `_build_used_handles` phải gồm thép-handle (§2.5); anchor thuộc INSERT bảng thép → từ chối "đã thuộc bảng thống kê".
6. **Re-parse ENUM:** gọi `parser` cố định. `kg_moi_bo`/`so_luong` dùng `_to_num`; nhãn m²/m³ dùng `_to_num_vn`; `kich_thuoc`/`tiet_dien` BẮT BUỘC qua `_sect_to_mm` → nhận `suy_doan_don_vi` (nếu anchor không ghi mm/cm → `do_tin_cay='thap'`).
7. **CỔNG TOKEN-NGUYÊN-VẸN (thay chuỗi-con, R3):**
   ```python
   toks = re.findall(r'(?<![\d.,])\d+(?:[.,]\d+)?(?![\d.,])', anchor.vn)
   giatri_tok = [_to_num_vn(t) if _label_la_m2m3(anchor.vn) else _to_num(t) for t in toks]
   if not any(abs(so_reparse - g) <= EPS for g in giatri_tok if g is not None): tu_choi
   ```
   `'1'` không khớp token `'1250'`; `'8'` không khớp `'8.62'`; `'B21'`→`'21'` loại (dính chữ). VN-nghìn `'1.130'` đọc `_to_num_vn`=1130, buộc parser trả 1130.
8. **BIÊN theo `y_nghia` (R5):** `kg_moi_bo` ∈ `[_KG_PU_LO,_KG_PU_MAX]` VÀ anchor có `_KG_PU_RE`; `tiet_dien`/`kich_thuoc` qua `_plausible_section_mm`; `so_luong` ∈ `[1,_SL_LO_MAX]`. Ngoài biên → từ chối. **KHÔNG nhận số trần.**
9. **Đa-số mơ hồ (R5):** ≥2 token hợp-`y_nghia` → từ chối, buộc đối tác anchor rõ hơn.
10. **Dedupe + cap (R7):** khoá `(anchor_handle, y_nghia, template_id)`; trùng → cập nhật `created_ts`. `len(hoc_phien) >= 200` → từ chối.
11. **Comparator mâu thuẫn:** cùng `anchor_handle` ≥2 `y_nghia` → `xung_dot=True`; `kg_moi_bo` mà anchor thuộc INSERT thép → `co_nghi_ngo`.
12. **Log WORM:** `hoclog.ghi('hoc_quy_uoc', file_id=self.content_hash, sid=..., handle=anchor_handle, them={template_id,y_nghia})`.

### 2.3 Helper thu_hoi TẬP TRUNG (R7)

```python
def _quy_tac_hieu_luc(self):
    """DUY NHẤT điểm đọc self.hoc_phien. Grep-guard: cấm truy cập self.hoc_phien[ ngoài
    hoc_quy_uoc / thu_hoi_quy_uoc / _quy_tac_hieu_luc."""
    return list(self.hoc_phien)   # thu_hoi đã XÓA phần tử -> không rác
```
`thu_hoi_quy_uoc`: `self.hoc_phien = [r for r in self.hoc_phien if r['rule_id']!=rule_id]` (rỗng→`[]`) + WORM 'thu_hoi'.

### 2.4 Map handle→text cho re-parse

`self.hoc_phien` chỉ lưu `anchor_handle`. Re-parse LIVE: dựng `self._text_by_handle = {t['handle']: t for t in self.texts}`
1 lần ở `__init__`; parser đọc `anchor = self._text_by_handle.get(rule['anchor_handle'])`; None → bỏ ứng viên. **KHÔNG cache số.**

### 2.5 Nối kênh xác-nhận + used_handles (R6, R4)

- `_ung_vien_cho_input` thêm nhánh: `(ma, ten)` khớp `y_nghia` → sinh ứng viên từ `_quy_tac_hieu_luc()` (re-parse LIVE) →
  `nguon='doc_lai_theo_quy_uoc_doi_tac'`, `chua_chac=True`, `la_goi_y=True`, `do_tin_cay='thap'`, `handle=anchor_handle`.
  Nhờ đó `_xac_nhan_ung_vien_theo_handle` (:1394) tự khớp và giữ provenance.
- Confirm-bằng-số-trần: trước `_rs_bs_only`, `bs[ten]` trùng giá trị 1 ứng viên học → ép `chua_chac=True,
  nguon='doi_tac_xac_nhan_learned', can_doi_chieu=True` thay `_nd`.
- `_build_used_handles`: ghi `att.dxf.handle` của mọi ATTRIB của INSERT-bảng thép vào `used`.

### 2.6 Cổng provenance TRUNG TÂM (R2 + G4 — backstop P3-trước-P4) ★ ĐIỂM KHÁC GỐC QUAN TRỌNG NHẤT

**P3 KHÔNG được lùi backstop cho P4.** Thêm sau resolver, trước compute:
```python
learned_in = [x for x in da_co if str(x.get('nguon','')).startswith(('doc_lai_theo_quy_uoc','doi_tac_xac_nhan_learned'))]
if learned_in:
    resp = {..., "co_ket_qua": False, "uoc_luong_hoc": kq, "can_bo_sung": True,
            "chua_chac": True, "can_doi_chieu": True, "nguon_hoc": [...]}   # KHÔNG 'ket_qua'/co_ket_qua=True
```
**G5 (TOCTOU):** tại điểm DÙNG, tái-kiểm anchor còn trong `_residual_texts()` + không mâu thuẫn recognizer; mâu thuẫn → hạ ứng viên + LỘ.

---

## 3. BẤT BIẾN PHẢI KHOÁ BẰNG TEST (nhóm `[Z]`)

- **INV-1 không-mutate-index:** trước/sau `hoc_quy_uoc`: `id()/len()` của `qty_index`/`section_index`/`used_handles` KHÔNG đổi.
- **INV-2 learned KHÔNG vào tổng/Excel:** dựng rule + confirm → `tong_hop_khoi_luong()`/`xuat_excel()` KHÔNG chứa `anchor_handle` học.
- **INV-3 chua_chac sống sót + nhãn trung thực (R1):** input học/E2 → `'đáng tin' NOT in resp['ghi_chu']` AND `resp['chua_chac'] is True` AND `so_do` chứa 'CHƯA CHẮC'.
- **INV-4 không số-chốt từ học (R2):** tập input toàn-học → `resp['co_ket_qua'] is False` AND `'ket_qua' not in resp` AND có `uoc_luong_hoc`.
- **INV-5 cô-lập-phiên:** Drawing mới (nạp file khác) → `self.hoc_phien==[]`; phiên B `/file/<id>` của A → 404 (R11).
- **INV-6 thu-hồi-sạch (R7):** `thu_hoi_quy_uoc('')` → `len(self.hoc_phien)==0`; sau đó confirm-theo-handle trả None/từ chối.
- **INV-7 token-nguyên-vẹn (R3):** '1250'+template→1 TỪ CHỐI; 'H 8.62 m'→8 TỪ CHỐI, →8.62 CHẤP NHẬN; 'ĐÀO MÓNG 1.130 M3'→1130.
- **INV-8 biên/đơn-vị (R3/R5):** '(1 bộ)=99999 kg' TỪ CHỐI; 'C-3 250' không đơn vị → `suy_doan_don_vi==True`, `do_tin_cay=='thap'`; 'tải 8000 kG' template kg TỪ CHỐI (đa-số/không kề per-unit).
- **INV-9 neo-ngữ-cảnh (R4):** anchor '150' không chứa 'T1' → TỪ CHỐI; `template_id` lạ → TỪ CHỐI, `hoc_phien` không đổi (G2).
- **INV-10 không auto-ghi qua LLM (R8):** `'hoc_quy_uoc' not in {tên tool trong gemini_tools}`.
- **INV-11 content-hash (R9):** 2 path khác cùng bytes → cùng `file_id` hash; 3 bytes khác → 3 hash.
- **INV-12 grep-guard mở rộng (R7/R10):** `os.walk` đệ quy, không có `self.hoc_phien[` ngoài 3 hàm cho phép; không reader `_hoc_log`.

---

## 4. THỨ TỰ IMPLEMENT (lát-cắt-dọc) + test đối kháng nhóm `[Z]`

| Lát | Nội dung | Test |
|---|---|---|
| **Lát 0** ★ | **Backstop + nhãn trung thực** (R1 @1871/1888-1889/1902, R2/§2.6 cổng provenance trung tâm, `resp['chua_chac']`). **KHÔNG có = NO-GO.** Cũng vá lỗ E2 ĐANG TỒN TẠI. | `[Z0]`: INV-3, INV-4 |
| **Lát 1** | used_handles + thép-handle; `_text_by_handle`; `_quy_tac_hieu_luc()`; grep-guard; data model. | `[Z1]`: INV-1, INV-12, used-handles |
| **Lát 2** | `hoc_quy_uoc` cổng đầy đủ (ENUM, NEO+ngữ-cảnh, token-nguyên-vẹn, biên/đơn-vị, dedupe/cap, comparator). | `[Z2]`: INV-7, INV-8, INV-9, R5 |
| **Lát 3** | Nối `hoc_phien` vào `_ung_vien_cho_input`; confirm-số-trần ép `chua_chac`; `thu_hoi` XÓA + WORM. | `[Z3]`: INV-6, R6 |
| **Lát 4** | Loại `hoc_quy_uoc`/`thu_hoi_quy_uoc` khỏi `gemini_tools`; `content_hash`+`sid`; artifact ownership. | `[Z4]`: INV-10, INV-11, INV-5, INV-2, R10 |

---

## 5. GO / NO-GO

**CONDITIONAL GO** — code P3 được, NHƯNG **Lát 0 (R1+R2+§2.6) là điều kiện chặn; KHÔNG được lùi sang P4.**

**Lý do (neo code):** KILL-CRITERIA §6 kế hoạch ("learned-value thành số bàn giao / không có backstop fail-closed")
bị CHẠM nếu ship theo thiết kế GỐC: R2 chứng minh tập input toàn-học ra `co_ket_qua=True, ket_qua=<số>,
so_file_da_kiem=0`; R1 chứng minh `ghi_chu` (thứ LLM thuật) dán "đáng tin" cho input CHƯA CHẮC. Vì bàn giao thực là
prose (G1) và tổng/Excel-fail-closed thuộc P4 (chưa xây, G4), P3-gốc KHÔNG có lưới chặn thứ hai. → Lỗ CAO có vá khả thi
NHƯNG vá đó PHẢI nằm trong P3 (§2.6). Các lỗ CAO còn lại (R3/R4) đều có vá cụ thể, khoá được bằng `[Z2]`.

**NO-GO nếu bất kỳ:** (a) Lát 0 bị tách khỏi P3 để "chờ P4"; (b) cổng token-nguyên-vẹn (R3) không thay được substring;
(c) `y_nghia='khac'` được giữ. Ba điều này biến learned-value thành số bàn giao có provenance-GIẢ — phá trực tiếp KPI ≈0% bịa.

**Ghi nợ THẤP** (R10/R11): theo sau nhưng phải có ticket; R9 content-hash nên làm trong Lát 4 để không đặt bẫy overfit cho P5.

---

## 6. KHOẢNG TRỐNG (completeness-critic — chưa hướng nào chạm, cần theo dõi)

- **G1 — Narrative laundering:** bàn giao thực là prose Gemini; invariant "không vào tổng/Excel" chỉ canh cấu trúc, KHÔNG canh `r.answer`. Cổng CODE (không phải prompt) nào chặn số `la_goi_y/chua_chac` xuất hiện như KẾT QUẢ trong prose? → §2.6 hạ `co_ket_qua` là biện pháp CHÍNH; cần theo dõi prose thực tế.
- **G2 — `template_id` ngoài ENUM:** hành vi fail-open chưa đặc tả → **§2.2 bước 1 fail-closed** + INV-9.
- **G3 — `thu_hoi` không ghi WORM 'đã rút':** P5 codify có thể overfit lên rule đã retract → §2.3 ghi WORM 'thu_hoi'.
- **G4 — Cửa sổ P3-trước-P4:** thiếu backstop tập trung → §2.6 cổng provenance trung tâm (đã đưa vào Lát 0).
- **G5 — TOCTOU residual:** anchor chỉ verify lúc HỌC, chưa tái kiểm lúc DÙNG → §2.6 tái-kiểm at-use.
- **G6 — Overfit 1 domain:** ngưỡng plausibility (130, kg>0) đặc-thù kết cấu nhà VN; red-team chạy trên 1 loại bản vẽ → **cần test ≥1 domain NGOÀI kết cấu** (trùng nhu cầu "xin 3-5 bản vẽ đa-domain" đã treo; là điều kiện gate P5).

> Liên quan: [[project-huong-2-mcp-autocad]] · [[project-ai-tu-hoc-ke-hoach]] · [[feedback-bia-tai-sinh-tang-code]] · [[feedback-tranh-overfit-quy-uoc-ban-ve]]
