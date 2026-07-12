# -*- coding: utf-8 -*-
"""P2 (AI tự học) — LOG WORM append-only. TẤT ĐỊNH, OFFLINE, KHÔNG tốn API.
Chạy:  python tests/test_hoc_log.py
Kiểm: (1) hoclog.ghi APPEND đúng schema + REDACT (file_hash thay path, không lộ đường dẫn thật);
      (2) HOC_LOG off -> không ghi; (3) GREP-GUARD BẤT BIẾN: KHÔNG module inference nào ĐỌC-LẠI log (chống
          warm-start/đầu-độc chéo phiên); (4) tool hoi_de_hoc/doi_chieu_nghi_ngo có WIRING gọi hoclog.ghi."""
import os, sys, io, json, tempfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
import hoclog

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _src(fn):
    with open(os.path.join(ROOT, fn), encoding="utf-8") as f:
        return f.read()


def main():
    global PASS, FAIL
    print("[P2.A] hoclog.ghi — APPEND-ONLY + schema + REDACT")
    tmp = tempfile.mkdtemp(prefix="hoclog_")
    _dir, _file, _on = hoclog.HOC_LOG_DIR, hoclog.HOC_LOG_FILE, hoclog.HOC_LOG_ON
    try:
        hoclog.HOC_LOG_DIR = tmp
        hoclog.HOC_LOG_FILE = os.path.join(tmp, "ung_vien.jsonl")
        hoclog.HOC_LOG_ON = True
        r1 = hoclog.ghi("hoi_de_hoc", file_id="/real/secret/duong-dan-nhay-cam.dxf", ma="C1",
                        tin_hieu="①", handle="ABC12", vn="THÉP CHỜ V-1", ts=1000.0,
                        them={"so_ung_vien": 1, "nhan": ["THÉP CHỜ V-1"]})
        r2 = hoclog.ghi("doi_chieu_nghi_ngo", file_id="/real/secret/duong-dan-nhay-cam.dxf", ma="C4",
                        tin_hieu="③", ts=1001.0, them={"so_nghi": 1, "loai": ["đa tiết diện"]})
        ok("ghi trả True (đã ghi)", r1 and r2)
        lines = [l for l in open(hoclog.HOC_LOG_FILE, encoding="utf-8").read().split("\n") if l.strip()]
        ok("APPEND 2 lần -> 2 dòng (không đè)", len(lines) == 2)
        rec = json.loads(lines[0])
        ok("schema đủ trường", all(k in rec for k in
           ("ts", "hanh_dong", "tin_hieu", "file_hash", "ma", "handle", "vn_redacted")))
        blob = open(hoclog.HOC_LOG_FILE, encoding="utf-8").read()
        ok("REDACT: KHÔNG lộ đường dẫn thật (chỉ file_hash)",
           "secret" not in blob and "duong-dan-nhay-cam" not in blob and "/real/" not in blob)
        ok("cùng file -> cùng file_hash (dev nhóm được theo file)",
           json.loads(lines[0])["file_hash"] == json.loads(lines[1])["file_hash"] and len(rec["file_hash"]) == 12)
        ok("vn giữ verbatim (redact=cắt ngắn, KHÔNG mã hoá) + them field vào rec",
           rec["vn_redacted"] == "THÉP CHỜ V-1" and rec.get("so_ung_vien") == 1 and rec.get("nhan") == ["THÉP CHỜ V-1"])
        ok("ts tất định (truyền vào)", rec["ts"] == 1000.0)
        hoclog.HOC_LOG_ON = False
        n_truoc = len([l for l in open(hoclog.HOC_LOG_FILE, encoding="utf-8").read().split("\n") if l.strip()])
        r3 = hoclog.ghi("x", ma="y")
        n_sau = len([l for l in open(hoclog.HOC_LOG_FILE, encoding="utf-8").read().split("\n") if l.strip()])
        ok("HOC_LOG off -> KHÔNG ghi (trả False, số dòng không đổi)", r3 is False and n_truoc == n_sau)
    finally:
        hoclog.HOC_LOG_DIR, hoclog.HOC_LOG_FILE, hoclog.HOC_LOG_ON = _dir, _file, _on
        shutil.rmtree(tmp, ignore_errors=True)

    print("[P2.B] GREP-GUARD — BẤT BIẾN 'KHÔNG reader' (chống warm-start/đầu-độc chéo phiên)")
    hl = _src("hoclog.py")
    ok("hoclog CHỈ có ĐÚNG 1 open() và là APPEND 'a' (chặn cả open() mặc-định-ĐỌC + iterator-read)",
       hl.count("open(") == 1 and 'open(HOC_LOG_FILE, "a"' in hl)
    ok("hoclog KHÔNG có bất kỳ đọc-lại nào (.read/.readlines/readline/json.load)",
       not any(p in hl for p in (".read(", ".readlines(", "readline", "json.load(")))
    import glob as _glob
    for _p in sorted(_glob.glob(os.path.join(ROOT, "*.py"))):     # GLOB MỌI *.py (trừ hoclog=writer) — bền hơn danh sách cứng
        _b = os.path.basename(_p)
        if _b == "hoclog.py":
            continue
        _s = open(_p, encoding="utf-8").read()
        ok("%s KHÔNG đụng file log trực tiếp (chỉ được gọi hoclog.ghi)" % _b,
           not any(x in _s for x in ("ung_vien.jsonl", "HOC_LOG_FILE", "HOC_LOG_DIR", "_hoc_log")))

    print("[P2.C] WIRING — tool hoi_de_hoc/doi_chieu_nghi_ngo gọi hoclog.ghi (không đụng core thuần)")
    ms = _src("mcp_server.py")
    ok("mcp_server import hoclog + gọi hoclog.ghi", "import hoclog" in ms and "hoclog.ghi(" in ms)
    ok("core phan_loai_tin_hieu/doi_chieu_nghi_ngo (tools_core) KHÔNG tự ghi log (giữ THUẦN, test không sinh rác)",
       "hoclog" not in _src("tools_core.py"))

    print("[P2.D] ROTATION — cap kích thước, xoay .1 (chống phình đĩa vô hạn)")
    tmp2 = tempfile.mkdtemp(prefix="hoclog_rot_")
    _d2, _f2, _o2, _c2 = hoclog.HOC_LOG_DIR, hoclog.HOC_LOG_FILE, hoclog.HOC_LOG_ON, hoclog.HOC_LOG_MAX_MB
    try:
        hoclog.HOC_LOG_DIR = tmp2
        hoclog.HOC_LOG_FILE = os.path.join(tmp2, "ung_vien.jsonl")
        hoclog.HOC_LOG_ON = True
        hoclog.HOC_LOG_MAX_MB = 0.00001            # ~10 byte -> dòng thứ 2 vượt cap -> XOAY .1
        hoclog.ghi("a", ma="line1", ts=1.0)        # tạo file (~100 byte > cap)
        hoclog.ghi("b", ma="line2", ts=2.0)        # file > cap -> os.replace .1 rồi ghi line2 vào file mới
        ok("xoay: .1 GIỮ line1 + file chính có line2 (bound đĩa, giữ mẫu mới)",
           os.path.exists(hoclog.HOC_LOG_FILE + ".1")
           and "line1" in open(hoclog.HOC_LOG_FILE + ".1", encoding="utf-8").read()
           and "line2" in open(hoclog.HOC_LOG_FILE, encoding="utf-8").read())
    finally:
        hoclog.HOC_LOG_DIR, hoclog.HOC_LOG_FILE, hoclog.HOC_LOG_ON, hoclog.HOC_LOG_MAX_MB = _d2, _f2, _o2, _c2
        shutil.rmtree(tmp2, ignore_errors=True)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
