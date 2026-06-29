ODA File Converter (Linux) cho deploy cloud — KHÔNG commit công khai.

Để build Docker (chuyển .dwg -> .dxf trên server), cần đặt file:
    vendor/ODAFileConverter.deb

Cách lấy:
  1. Vào https://www.opendesign.com/guestfiles
  2. Tải "ODA File Converter" bản LINUX, Qt6, x64, định dạng .deb
  3. Đổi tên thành ODAFileConverter.deb và đặt vào thư mục vendor/ này.

Lưu ý license: ODA miễn phí cho demo/đánh giá; nếu thương mại hoá SaaS cần membership OpenDesign.
-> Dùng repo PRIVATE để tôn trọng license + vì file ~50MB.

CHẠY LOCAL (Windows) KHÔNG cần file này — chỉ cần đặt biến môi trường ODA_EXE trỏ tới
ODAFileConverter.exe (vd D:\Downloads\ODAFileConverter.exe), hoặc chỉ test với file .dxf.
