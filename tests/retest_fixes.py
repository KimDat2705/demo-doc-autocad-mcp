# -*- coding: utf-8 -*-
"""Re-test các câu đã FAIL sau khi vá (MAX_TURNS, bẫy chiều dài/cao độ, gộp thép)."""
import os, sys, io, json
os.environ["READFILE_MAX_MB"] = "300"
os.environ.setdefault("GEMINI_MODEL", "gemini-3.5-flash")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge

FILES = {
    "kientruc": r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/1. Kien truc MN Gia Loc.dxf",
    "ketcau":   r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/2. KetCau MN GiaLoc.dxf",
}
# id -> (file chay, loai loi cu, ky vong tom tat)
RETEST = {
    181: ("kientruc", "MAX_TURNS", "phai tra: 2 tang 8 phong (khong bo cuoc)"),
    187: ("kientruc", "MAX_TURNS", "phai tra thep mong M1 (khong bo cuoc)"),
    195: ("kientruc", "MAX_TURNS", "phai tra D2-2 (khong bo cuoc)"),
    51:  ("kientruc", "MAX_TURNS", "phai tra (khong bo cuoc)"),
    15:  ("kientruc", "BAY",       "phai TU CHOI chieu dai cong trinh"),
    151: ("kientruc", "BAY",       "phai TU CHOI chieu dai"),
    152: ("ketcau",   "BAY",       "phai TU CHOI cao do tang"),
    178: ("ketcau",   "BAY",       "phai noi day chi la dim, khong phai kich thuoc cong trinh"),
    38:  ("kientruc", "THEP_GOP",  "KHONG cong thep tron+hinh thanh 1 so"),
    22:  ("kientruc", "THEP",      "thong ke thep hinh cau thang ~2163kg"),
}
batt = {q["id"]: q for q in json.load(open(os.path.join(HERE, "battery.json"), encoding="utf-8"))["battery"]}

print("MODEL:", mcp_bridge.MODEL, "| MAX_TURNS:", mcp_bridge.MAX_TURNS)
br = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
cur = None
for i in sorted(RETEST, key=lambda x: RETEST[x][0]):
    f, loai, kv = RETEST[i]
    if f != cur:
        s = br.call("nap_ban_ve", {"path": FILES[f]}, timeout=600)
        summ = "%s (%s doi tuong, %s layer)" % (s["name"], s["tong_doi_tuong"], s["so_layer"])
        cur = f
    q = batt[i]["cau_hoi"]
    import time
    a = None
    for attempt in range(3):   # 503 Flash hay xảy ra -> thử lại vài lần
        try:
            r = mcp_bridge.tra_loi_ai(br, q, summ)
            a = r["answer"].replace("\n", " ")
            break
        except Exception as e:
            if attempt == 2:
                a = "[[503/lỗi sau 3 lần]] %s" % str(e)[:60]
    bo_cuoc = a and "quá nhiều bước" in a
    print("\n[id%d|%s] %s" % (i, loai, q[:60]))
    print("  KV:", kv)
    print("  ->", (a or "")[:210], ("  ⚠️BỎ CUỘC" if bo_cuoc else ""))
br.close()
