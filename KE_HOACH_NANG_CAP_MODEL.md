# KẾ HOẠCH NÂNG CẤP MODEL GEMINI (2.5-flash → 3.6-flash)

> **Nghiên cứu 2026-08-06.** Trạng thái: **NGHIÊN CỨU XONG — CHƯA CODE.**
> Nhóm việc: **A** (chức năng chính — model là tầng định tuyến + diễn giải của đường đọc-đúng).
> ⛔ **CHẶN:** API key đang bị Google khoá vì **chưa gia hạn thanh toán** (sếp xác nhận 2026-08-06).
> Mọi bước cần API **KHÔNG được khởi động** cho tới khi `/health` gọi thật trả 200.

---

## 0. VÌ SAO PHẢI LÀM (không phải "nâng cấp cho mới")

| Sự kiện | Bằng chứng | Hệ quả |
|---|---|---|
| `gemini-2.5-flash` bị khai tử | Google ấn định **16/10/2026** | Còn ~10 tuần. Không làm = demo chết |
| `gemini-2.0-flash` **đã tắt hẳn** | Trang deprecations liệt kê "shut down" | **Chuỗi dự phòng hiện tại đã mục 1 nấc** mà không ai biết |
| Google chỉ định bản thay | `gemini-3.6-flash` | Đường nâng cấp chính thức |

⚠ Chuỗi dự phòng hiện tại (`mcp_bridge.py:55`) là `gemini-2.0-flash,gemini-1.5-flash` — nấc đầu trỏ vào model **không còn tồn tại**. Model chết trả **404**, mà `_is_overloaded()` chỉ nhận `{429,500,502,503,504}` ⇒ **không fail-forward**, ném lỗi luôn. Đây là bug thật, độc lập với việc nâng cấp.

---

## 1. CHỐT MODEL

### 1.1 Model chính: **`gemini-3.6-flash`**

| Lý do | Số/nguồn |
|---|---|
| **GA, không phải preview** | Bắt buộc cho demo đối tác. 3.1 Pro vẫn là `gemini-3.1-pro-preview` |
| Google chỉ định thay 2.5-flash | Trang deprecations |
| Mạnh nhất dòng Flash về **gọi công cụ** | Ít bước suy luận + ít lượt gọi tool hơn 3.5-flash; HLE **18,0%** vs 2.5-flash **11,0%** |
| **Rẻ hơn 3.5-flash mà mạnh hơn** | Ra **$7,50** vs $9,00 ⇒ 3.5-flash bị loại thẳng khỏi vị trí model chính |
| Ít token đầu ra hơn ~17% | Bù một phần chênh giá |
| Giảm áp lực `MAX_TURNS=14` | Comment `mcp_bridge.py:27`: đã phải nới 8→14 vì "Flash gọi tool kém gọn hơn Pro" |

### 1.2 ⛔ KHÔNG chọn `gemini-3.1-pro` (dù user cho phép dùng model thông minh nhất)

1. **Còn `-preview`** → Google đổi/rút bất kỳ lúc nào. Không đặt demo đối tác lên nền preview.
2. **Nút thắt dự án KHÔNG phải suy luận.** Đã đo: nút thắt là **ghép nhãn↔giá trị** ở tầng đọc (`[[project-nut-that-recall-ghep-nhan-gia-tri]]`, tool #36). Model thông minh hơn **không đọc được ô bảng mà tool không trả về**. Tiền bỏ vào Pro không mua được recall.
3. **Đã có tiền lệ trong chính dự án**: comment `mcp_bridge.py:34` — *"Pro preview thì quota ~25 req là cạn (429)"*.
4. Giá $2,00/$12,00 + `thinking_level` mặc định `high`.

→ **Giữ đường thoát:** cho phép đặt qua env `GEMINI_MODEL` để thử sau. **Không đặt mặc định.**

### 1.3 Chuỗi dự phòng — **đề xuất ngày 2026-08-06 lần đầu đã RÚT LẠI**

```
❌ CŨ (đã rút):  gemini-3.6-flash → gemini-3.5-flash-lite → gemini-2.5-flash
✅ MỚI:          gemini-3.6-flash → gemini-3.5-flash      → gemini-3.5-flash-lite
```

Ba lý do bác đề xuất cũ:

1. **Trộn thế hệ = lỗi 400.** Gemini 3 đính **chữ ký suy luận** (*thought signature*) vào mỗi `function_call` và **bắt buộc gửi lại nguyên vẹn**; thiếu → 400. Chữ ký của model này bị model khác từ chối ("Corrupted thought signature" — lỗi đang xảy ra hàng loạt ở LangChain/goose/windmill). Kết chuỗi bằng 2.5-flash (khác thế hệ) là ca dễ vỡ nhất.
2. **2.5-flash chết 16/10** → giữ làm chốt cuối = nợ kỹ thuật phải gỡ lại sau 10 tuần.
3. **Nhảy thẳng 3.6 → Lite hụt quá sâu.** 3.5-flash là nấc đệm cùng hạng.

> Ghi chú: comment `mcp_bridge.py:33` nói *"đã thử 3.5-flash nhưng hay 503 high demand"*. Phép đo đó chạy trên **free tier**. Sau khi gia hạn (paid tier) hành vi 429/503 khác hẳn ⇒ **phải đo lại**, không dùng kết luận cũ.

### 1.4 ⚠ THAY ĐỔI CODE BẮT BUỘC — không chỉnh env được

`_gen_fallback()` (`mcp_bridge.py:76-95`) đổi model **giữa chừng request**, trong khi `contents` đã tích luỹ `cand.content` mang chữ ký của model cũ (`mcp_bridge.py:1187,1239,1247`).

⇒ Với Gemini 3, đổi model giữa chừng = **gửi chữ ký lạ** = 400.

**Sửa:** khi phải đổi model mà **đã có lượt gọi tool nào rồi** → **chạy lại request từ đầu** với model mới (dựng lại `contents` sạch từ `history` + `q`), không mang `contents` nhiễm sang.

*(Tin tốt: code đang append **nguyên đối tượng** `cand.content` chứ không dựng lại từ text ⇒ trong CÙNG một model, chữ ký được giữ đúng. Chỉ đường đổi-model là hỏng.)*

---

## 2. BA RỦI RO PHẢI ĐO — KHÔNG ĐƯỢC GIẢ ĐỊNH

### R1 — `temperature=0` xung đột với Gemini 3 ⚠ **NGHIÊM TRỌNG NHẤT**

- Code: `temperature=0` (`mcp_bridge.py:1150`, `:1269`) — lựa chọn **chống bịa cốt lõi**, ghi rõ ở docstring dòng 10.
- Tài liệu Gemini 3: *"strongly recommend keeping the temperature parameter at its default value of 1.0"*; đặt dưới 1.0 *"may lead to unexpected behavior, such as looping or degraded performance"*.
- **Đây là xung đột thiết kế thật, không phải chuyện nhỏ.** Bỏ `temperature=0` có thể làm tăng phương sai câu trả lời — đúng thứ dự án chống suốt.
- **Phải A/B riêng biến này**: `{3.6-flash, temp=0}` vs `{3.6-flash, temp=1}` trên bộ bẫy ảo giác. **Không đổi model và temperature cùng lúc.**

### R2 — `max_output_tokens=8192` là ngân sách **CHUNG** cho thinking + câu trả lời

- Gemini 3 mặc định `thinking_level = "high"`.
- `max_output_tokens` **bao gồm cả token suy nghĩ** (trái với tài liệu, nhưng đã xác nhận qua issue `googleapis/python-genai#2062`).
- Thinking ăn hết ngân sách → `finishReason: MAX_TOKENS` → **câu trả lời RỖNG**.
- ⚠ Dự án **đã từng dính bug empty-response** (`[[feedback-e2e-test-kpi]]`) — biết rõ nó khó lộ ra sao.
- **Xử:** đưa `thinking_level` ra env (thử `minimal`/`low`), cân nhắc nâng `max_output_tokens`, rồi ĐO. Không bỏ trống `max_output_tokens` (bỏ trống → treo vô hạn).

### R3 — `FunctionResponse` có thể cần trường `id`

- Code hiện chỉ truyền `name` (`mcp_bridge.py:1193,1230`).
- Nguồn phụ nói Gemini 3 cần `id` khớp với `function_call`; tài liệu chính **không xác nhận**.
- **Phải thử thật bằng 1 ca nhỏ**, không suy đoán.

### Chi phí — chưa đo được, là một hạng mục của GĐ 2

| | vào ($/1M) | ra ($/1M) |
|---|---|---|
| `gemini-2.5-flash` (nay) | 0,30 | 2,50 |
| `gemini-3.6-flash` | **1,50** (×5) | **7,50** (×3) |

Cộng thêm token suy nghĩ tính vào **đầu ra** ⇒ thực tế **có thể cao hơn ×3**. Bù lại: ít lượt gọi tool + ít token ra 17%. **Phải đo chi phí thật/câu hỏi**, không suy từ bảng giá.

---

## 3. KẾ HOẠCH THỰC HIỆN

### GĐ 0 — ⛔ CHẶN: chờ gia hạn thanh toán
Không có bước nào chạy được nếu API còn 403. Kiểm bằng:
```bash
python -c "import io,json,urllib.request;k=[l.split('=',1)[1].strip() for l in io.open('demo_mcp_autocad/.env',encoding='utf-8') if l.startswith('GEMINI_API_KEY')][0];print(urllib.request.urlopen(urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key='+k,data=json.dumps({'contents':[{'parts':[{'text':'OK'}]}]}).encode(),headers={'Content-Type':'application/json'})).status)"
```
Ra `200` = thông.

### GĐ 1 — LÀM ĐƯỢC NGAY, KHÔNG CẦN API (offline)

| # | Việc | File |
|---|---|---|
| 1.1 | Gỡ `gemini-2.0-flash` (đã tắt) khỏi `_FALLBACK_DEFAULT`; đặt chuỗi mới | `mcp_bridge.py:55` |
| 1.2 | **Sửa `_gen_fallback`: đổi model ⇒ chạy lại request từ đầu**, không mang `contents` nhiễm chữ ký | `mcp_bridge.py:76-95` + call-site |
| 1.3 | Thêm `404`/`NOT_FOUND` vào đường fail-forward (model bị khai tử phải nhảy nấc, không ném lỗi) | `_is_overloaded()` |
| 1.4 | Đưa `thinking_level` + `max_output_tokens` + `temperature` ra **env** để đo được mà không sửa code | `mcp_bridge.py:1150` |
| 1.5 | Nâng `google-genai` 2.10.0 → bản mới nhất; đọc changelog phần thought-signature | `requirements.txt` |
| 1.6 | Test offline (mock, không tốn API): chứng minh đổi model **không** mang `contents` cũ sang | `tests/test_model_fallback.py` (đã có, mở rộng) |

**Cổng GĐ 1:** `bash harness/scripts/check.sh` xanh + `python tests/test_takeoff_chong_bia.py` 76/76.
⚠ Xoá `__pycache__` trước khi chạy cổng (`[[feedback-stale-pycache-lam-cong-sai]]`).

### GĐ 2 — CẦN API (chỉ chạy sau GĐ 0)

**2.1 Khói (rẻ, ~5 request).** 1 câu × `{3.6-flash, 3.5-flash, 3.5-flash-lite}` → xác nhận 200 + có chữ.

**2.2 Xác minh R1/R2/R3 bằng ca nhỏ TRƯỚC khi chạy 198 câu.**
- R3: 1 câu buộc gọi tool → xem có 400 vì thiếu `id` không.
- R2: 1 câu nhiều phần → đếm `finishReason`, log token suy nghĩ vs token trả lời.
- R1: 10 câu bẫy ảo giác × `{temp=0, temp=1}`.

> Chạy 198 câu trước khi xác minh 3 cái này = **đốt quota vào một cấu hình có thể sai**.

**2.3 A/B đầy đủ.** 198 câu (`tests/battery.json`) × `{gemini-2.5-flash, gemini-3.6-flash}`, cấu hình còn lại **giữ nguyên**.
- ⚠ **BẮT BUỘC chống 429**: nghỉ giữa lượt + **checkpoint theo dòng** để chạy tiếp được.
  *Lý do có thật:* `tests/battery_results_pro25.jsonl` **hỏng 127/198 dòng** vì hết quota giữa chừng — và suýt cho kết luận ngược ("Flash giỏi hơn Pro").
- Loại **mọi dòng lỗi** khỏi phép chấm; báo rõ số dòng bị loại.

**2.4 Chấm — 5 trục, không gộp thành 1 điểm.**

| Trục | Cách đo | Vì sao |
|---|---|---|
| **Bẫy ảo giác** | Các ca `loi_san` + `GHOSTINOX`/thang máy/`C1` | **Trục quyết định.** Bịa nhiều hơn = NO_GO bất kể trục khác |
| Đúng số | Khớp `ky_vong` | Chức năng chính |
| Recall | Số ca tìm ra dữ liệu có trong file | Điểm yếu đã biết |
| Thời gian | `thoi_gian_s` | Trải nghiệm demo |
| Token + chi phí | `usage_metadata` (tách token suy nghĩ) | Quyết định có kham nổi không |

**2.5 ⚠ Kỷ luật đo (bắt buộc — có tiền lệ hỏng trong chính phiên 2026-08-06):**
- **Đọc tay ≥10 ca** trước khi tin bất kỳ con số tổng hợp nào.
- Số "quá đẹp" và số "quá xấu" **đều** là dấu hiệu bộ trích hỏng (`[[feedback-so-qua-xau-cung-la-bo-trich-hong]]`, `[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`).
- *Trong phiên nghiên cứu này, phép đo cho **3 kết quả sai liên tiếp** (12,6% trùng khớp · 98/198 "không có neo" · "Flash giỏi hơn Pro") — cả 3 đều trông hợp lý.*

**Ngưỡng GO:** `3.6-flash` **không thua** `2.5-flash` ở trục **bẫy ảo giác**, và **không tụt recall**. Thắng ở tốc độ/tiền mà thua ở bẫy = **NO_GO**.

### GĐ 3 — Chốt & triển khai
Đổi `GEMINI_MODEL` trên Render → chạy lại cổng → E2E thật trên bản deploy → cập nhật `feature_list.json` + `session-handoff.md`.

### GĐ 4 — Dọn trước 16/10/2026
Gỡ `gemini-2.5-flash` khỏi mọi mặc định/tài liệu/test.

---

## 4. ĐIỂM ĐÁNG NHỚ

Đổi model = **sửa một biến môi trường** (`GEMINI_MODEL`) + một bản vá nhỏ ở đường dự phòng.
**36 công cụ đọc bản vẽ, hàng rào chống bịa, kho kiến thức — không đụng một dòng.**

Đây là phần thưởng của kiến trúc tool-use: nếu tháng 6 đã fine-tune trên 2.5-flash thì hôm nay 2.5 bị khai tử = **train lại từ đầu, toàn bộ công sức thành rác**.

---

## 5. NGUỒN

- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/deprecations.md.txt
- https://ai.google.dev/gemini-api/docs/gemini-3 (migration 2.5→3, temperature, thinking_level)
- https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures
- https://github.com/googleapis/python-genai/issues/2062 (max_output_tokens bao gồm token suy nghĩ)
- https://benchr.org/deprecations/gemini-2-5-pro (mốc 16/10/2026)
