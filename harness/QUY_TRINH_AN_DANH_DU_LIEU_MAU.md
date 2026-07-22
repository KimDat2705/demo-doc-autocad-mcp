# Quy trình AN DANH dữ liệu mẫu (bản vẽ khách hàng)

> **Nguyên tắc (theo yêu cầu đối tác 2026-07-22):** khi dùng **dữ liệu THẬT** làm mẫu,
> **CHE / ĐỔI** thông tin định danh (cá nhân + doanh nghiệp) để bảo vệ danh tính.
> **KHÔNG** vì "không che được" mà bỏ dữ liệu — cứ dùng, chỉ che phần định danh.
> Áp dụng cho **mọi dữ liệu mẫu về sau**, không chỉ corpus hiện tại.

---

## 1. Vì sao — bề mặt rò rỉ

Repo là **PRIVATE** nhưng vẫn đẩy lên GitHub → **mọi file được COMMIT** là bề mặt rò. Rủi ro nằm ở:
- **File bản vẽ thô** (`.dwg/.dxf`) nếu bị commit → lộ nguyên khung tên (tên KS, đơn vị TK, chủ đầu tư, công trình, địa chỉ).
- **Đường dẫn** chứa tên thư mục/file thật trong code test/script.
- **Tài liệu / comment / dữ liệu eval** (`.md`, `.jsonl`, `.json`) nhắc tên thật.
- **Docker image**: nếu build LOCAL mà không loại corpus → nướng dữ liệu thật vào image.

Dữ liệu thô hiện đặt **NGOÀI repo** (`../input_files/`, đã `.gitignore`) → không lộ qua git. Giữ nguyên nguyên tắc này.

---

## 2. Bí danh (codename)

Công trình dùng bí danh **CT-A … CT-K** trong MỌI file được commit. Người → `[tên đã ẩn]`.

- **Ánh xạ bí-danh → tên THẬT chỉ nằm ở `tests/corpus_local.py`** (đã `.gitignore`, KHÔNG commit).
- **TUYỆT ĐỐI KHÔNG** viết bảng ánh xạ "CT-A = tên thật" vào bất kỳ file được commit nào (kể cả file này) — làm vậy là tái định danh, mất công che.

---

## 3. Đường dẫn corpus — mẫu `.env`

Code test/script **KHÔNG hardcode** tên thư mục/file thật. Thay vào đó:

1. Tên thật → chỉ trong **`tests/corpus_local.py`** (gitignored). Tạo bằng cách copy **`tests/corpus_local.example.py`** rồi điền.
2. Test import bí danh: `from corpus_local import KT, KC, P9, P9KT, HT`.
3. Thiếu `corpus_local.py` → biến = `""` → test tự **SKIP** (đều có guard `os.path.isfile`).
4. **Mỗi máy** (kể cả máy làm từ xa qua Dispatch) cần tự tạo `corpus_local.py` — giống `.env`.

---

## 4. CHECKLIST khi có bản vẽ mẫu MỚI

- [ ] **KHÔNG** copy `.dwg/.dxf` thật vào trong `demo_mcp_autocad/`; để ở `../input_files/` (ngoài repo).
- [ ] Thêm đường dẫn file mới vào `tests/corpus_local.py` (gitignored) dưới **bí danh mới** (CT-L, CT-M…).
- [ ] Trong docs / comment / eval: gọi công trình bằng **bí danh**, người bằng `[tên đã ẩn]`.
- [ ] KHÔNG để SĐT / email / MST / số CCHN / tên chủ đầu tư trong file commit.
- [ ] Nếu commit kết quả eval (`.jsonl/.json`): che tên trong `answer` / `ky_vong`.
- [ ] Kiểm `.dockerignore` vẫn loại `input_files/`, `_khao_sat/`, `_hoc_log/`, `tests/corpus_local.py`, `tests/`.
- [ ] Chạy **lệnh rà** (mục 5) → phải **0 hit** (trừ `corpus_local.py` gitignored).

---

## 5. Lệnh rà nhanh (phải trả về 0 trên file tracked)

```bash
cd demo_mcp_autocad
git grep -nEi "bùi|văn mạnh|phùng|gia ?lộc|gia ?loc|gialoc|kẻ sặt|ke sat|ninh hải|ninh hai|nhị chiểu|nhi chiê?u|nhichieu|cộng hòa|cong hoa|hiệp cát|hiep cat|an lâm|an lam|tân phong|tan phong|rachmop" -- . ':(exclude)vendor/*' ':(exclude)harness/QUY_TRINH_AN_DANH_DU_LIEU_MAU.md'
```

Sạch → trả về **0**. ⚠ **Bắt buộc loại trừ chính file này** (`':(exclude)harness/QUY_TRINH_AN_DANH_DU_LIEU_MAU.md'`) — vì nó chứa danh sách token làm MẪU grep nên tự khớp chính nó; quên loại thì lệnh luôn ra ≥1 (báo động giả, KHÔNG phải rò rỉ).

Thêm token cho công trình mới khi mở rộng corpus. `git grep` chỉ soi file **tracked** nên `corpus_local.py` (gitignored) không bị tính — đúng ý (tên thật được phép nằm ở đó).

---

## 6. Ngoài phạm vi (giữ nguyên — quyết định 2026-07-22)

Định danh của **chính đội phát triển** (GitHub handle, tên máy trong đường dẫn tuyệt đối, URL Render deploy)
**KHÔNG** che — đó là của mình, không phải dữ liệu doanh nghiệp mẫu mà đối tác nhờ bảo vệ.
