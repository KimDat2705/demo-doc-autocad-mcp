# -*- coding: utf-8 -*-
"""Robustness J — DỌN FILE TTL: xoá file cũ trong _uploads/_renders để đĩa KHÔNG phình vô hạn.
Nhẹ (chỉ os/time) -> import được ở CẢ web process (app.py) LẪN MCP subprocess (tools_core) mà KHÔNG kéo
theo ezdxf/matplotlib. An toàn: chỉ xoá FILE (không đụng thư mục con), nuốt lỗi lẻ (không chặn luồng chính)."""
import os
import time


def cleanup_old_files(dirs, ttl_min, keep=None):
    """Xoá file có mtime CŨ HƠN ttl_min phút trong các thư mục `dirs`.
    - `keep`: iterable đường dẫn TUYỆT ĐỐI cần GIỮ (vd file vừa tạo / đang dùng) — không xoá dù cũ.
    - ttl_min <= 0 (hoặc None) -> KHÔNG dọn (trả 0,0) — cho phép TẮT qua env.
    Trả (so_xoa, so_loi). KHÔNG ném: mọi lỗi I/O lẻ được đếm vào so_loi, luồng chính không bị ảnh hưởng."""
    if not ttl_min or ttl_min <= 0:
        return 0, 0
    cutoff = time.time() - ttl_min * 60
    keep_set = {os.path.normcase(os.path.abspath(p)) for p in (keep or [])}
    removed = errors = 0
    for d in dirs:
        try:
            names = os.listdir(d)
        except OSError:
            continue                      # thư mục chưa tồn tại -> bỏ qua
        for nm in names:
            p = os.path.join(d, nm)
            try:
                if not os.path.isfile(p):
                    continue              # chỉ xoá FILE, không đụng thư mục con
                if os.path.normcase(os.path.abspath(p)) in keep_set:
                    continue
                if os.path.getmtime(p) < cutoff:
                    os.remove(p)
                    removed += 1
            except OSError:
                errors += 1               # file bị lock/đang ghi -> bỏ qua, không chặn
    return removed, errors
