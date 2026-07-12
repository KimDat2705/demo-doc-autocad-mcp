# -*- coding: utf-8 -*-
"""
hoclog.py — WORM APPEND-ONLY log cho AI TỰ HỌC (cổng 4: NHIÊN LIỆU cho DEV rà, KHÔNG hồi-tiếp vào inference).

BẤT BIẾN (khoá bằng grep-guard test trong tests/test_hoc_log.py):
  1. CHỈ mở file mode 'a' (APPEND). TUYỆT ĐỐI KHÔNG có hàm ĐỌC-LẠI trong module này hay bất kỳ module inference
     nào (tools_core/mcp_server/mcp_bridge/app) -> chống warm-start self.hoc_phien từ log = rò/đầu-độc CHÉO PHIÊN
     (red-team: 'nếu ai thêm reader seed hoc_phien từ JSONL thì rule phiên A ngấm sang phiên B').
  2. REDACT: file_hash (KHÔNG lưu đường dẫn thật); vn cắt ngắn. sid (nếu có) -> hash.
  3. BEST-EFFORT: nuốt MỌI lỗi I/O (không bao giờ chặn luồng inference). Ephemeral trên Render free (mất khi
     restart) -> KHÔNG phải nguồn tin cậy lâu dài, chỉ để dev quan sát mẫu 'chỗ bí' tích luỹ qua nhiều file.

Đọc-lại log CHỈ do CON NGƯỜI / công cụ dev NGOÀI tiến trình chạy (KHÔNG import module này để read — module này không có read).
"""
import os, json, hashlib, time

HOC_LOG_DIR = os.environ.get("HOC_LOG_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_hoc_log"))
HOC_LOG_FILE = os.path.join(HOC_LOG_DIR, "ung_vien.jsonl")
# Mặc định BẬT; tắt bằng env HOC_LOG=0/false/off (vd môi trường không cần ghi log).
HOC_LOG_ON = os.environ.get("HOC_LOG", "1").strip().lower() not in ("0", "false", "no", "off", "")
# CAP kích thước (chống phình đĩa vô hạn): file vượt ngưỡng -> XOAY 1 vòng (đổi tên .1, đè bản .1 cũ) -> bound ~2×cap,
# giữ mẫu MỚI nhất. 0 = tắt cap. Ephemeral trên Render nhưng cap vẫn cần cho local/dev chạy dài.
HOC_LOG_MAX_MB = int(os.environ.get("HOC_LOG_MAX_MB", "5"))


def _hash(s):
    """SHA1 rút gọn 12 kí tự — ẩn danh đường dẫn/sid (KHÔNG lưu giá trị thật, không phục hồi được)."""
    return hashlib.sha1((s or "").encode("utf-8", "replace")).hexdigest()[:12]


def ghi(hanh_dong, file_id="", ma="", tin_hieu="", handle="", vn="", sid="", them=None, ts=None):
    """Ghi 1 SỰ KIỆN học vào log WORM (APPEND-ONLY, mode 'a'). Redact: file_hash + vn[:80].
    ⛔ Hàm này CHỈ GHI — KHÔNG có đường đọc-lại. Nuốt mọi lỗi (trả False), KHÔNG chặn luồng inference.
    ts: truyền được cho test tất định (mặc định time.time()). Trả True nếu đã ghi."""
    if not HOC_LOG_ON:
        return False
    try:
        rec = {"ts": round(float(ts) if ts is not None else time.time(), 3),
               "hanh_dong": str(hanh_dong)[:24], "tin_hieu": str(tin_hieu)[:4],
               "file_hash": _hash(file_id), "ma": str(ma or "")[:40],
               "handle": str(handle or "")[:20], "vn_redacted": str(vn or "")[:80]}
        if sid:
            rec["sid_hash"] = _hash(sid)
        if them and isinstance(them, dict):
            for k, v in them.items():
                rec[str(k)[:24]] = v
        os.makedirs(HOC_LOG_DIR, exist_ok=True)
        try:                                                      # CAP: file vượt ngưỡng -> xoay .1 (bound đĩa ~2×cap)
            if HOC_LOG_MAX_MB > 0 and os.path.getsize(HOC_LOG_FILE) > HOC_LOG_MAX_MB * 1024 * 1024:
                os.replace(HOC_LOG_FILE, HOC_LOG_FILE + ".1")
        except OSError:
            pass
        with open(HOC_LOG_FILE, "a", encoding="utf-8") as f:      # mode a = APPEND-ONLY (WORM); khong doc, khong ghi-de
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False   # best-effort: KHÔNG BAO GIỜ chặn luồng inference
