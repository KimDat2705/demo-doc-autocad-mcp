# Hướng dẫn deploy DEMO 2 (MCP) lên link riêng

Demo 2 deploy GIỐNG demo 1 (Render + Docker + ODA), chỉ khác **repo riêng** + dùng **GEMINI_API_KEY**.
Code đã commit local sẵn (`git log` thấy commit đầu). Việc còn lại:

## Bước 1 — Đặt file ODA vào `vendor/`  (BẮT BUỘC)
Demo 2 cần đúng file ODA Linux .deb như demo 1 (để Render build Docker chuyển .dwg→.dxf).
Lấy 1 trong 2 cách:
- **Copy từ demo 1:** file `vendor/ODAFileConverter.deb` (hoặc `ODAFileConverter_QT6_lnxX64_*.deb`) bạn đã
  dùng cho demo 1 (có trong repo GitHub `KimDat2705/demo-doc-autocad`). Tải về rồi đặt vào:
  `demo_mcp_autocad/vendor/ODAFileConverter.deb`
- **Hoặc tải mới:** https://www.opendesign.com/guestfiles → "ODA File Converter" Linux Qt6 x64 .deb →
  đổi tên `ODAFileConverter.deb` → đặt vào `vendor/`.

> File này KHÔNG bị .gitignore (Render cần) → sẽ được commit. Vì vậy repo phải **PRIVATE**.

## Bước 2 — Tạo repo GitHub PRIVATE mới (riêng demo 2)
Ví dụ tên: `demo-doc-autocad-mcp` (ĐỪNG dùng chung repo demo 1).
Trên GitHub: New repository → Private → KHÔNG thêm README/gitignore (repo này đã có code).

## Bước 3 — Push code lên repo mới
Trong thư mục `demo_mcp_autocad/` (đã `git init` + commit sẵn):
```
git remote add origin https://github.com/<tài-khoản>/demo-doc-autocad-mcp.git
git add vendor/ODAFileConverter.deb        # thêm file ODA vừa đặt ở Bước 1
git commit -m "them ODA converter cho deploy"
git branch -M main
git push -u origin main
```

## Bước 4 — Deploy trên Render (Blueprint)
1. Render → **New** → **Blueprint** → chọn repo `demo-doc-autocad-mcp`.
2. Render đọc `render.yaml` (service `doc-autocad-mcp-demo`).
3. Khi được hỏi **GEMINI_API_KEY** → dán khoá Gemini của bạn (KHÔNG commit khoá).
4. **Apply / Create** → chờ build Docker (~5-10 phút lần đầu).
5. Xong → có **link riêng** dạng `https://doc-autocad-mcp-demo.onrender.com`.

## Lưu ý vận hành (giống demo 1)
- Gói **Free**: ngủ sau 15 phút (mở lại chờ ~50s), RAM 512MB → OK file nhỏ/vừa.
- File lớn (.dxf >45MB): bị chặn thân thiện. Cần nâng gói → tăng env `READFILE_MAX_MB` (~250).
- Render highlight tốn vài giây–~20s/lần (đang ở danh sách tối ưu — xem `GHI_CHU_HOAN_THIEN.md`).
- Demo 1 vẫn chạy nguyên ở link cũ — 2 demo độc lập, 2 link khác nhau.

## Kiểm thử sau deploy
Mở link → upload 1 file .dwg/.dxf → hỏi:
"Có bao nhiêu bộ cửa D1?" · "Đánh dấu cửa D1 trên bản vẽ" (phải hiện ẢNH khoanh đỏ) · "Tổng số bộ cửa?"
