# -*- coding: utf-8 -*-
"""KỊCH BẢN TEST GIAI ĐOẠN 2 (takeoff) — chạy trên demo 2 (Gemini 2.5-flash) + đối chiếu ENGINE tất định.
Mỗi ca: (câu hỏi cho AI, [ten_dai_luong, ma, inputs_bo_sung] để lấy GROUND TRUTH từ engine).
Hỗ trợ hội thoại nhiều lượt (history). Ghi kichban_gd2_ketqua.jsonl."""
import os, sys, io, json, time
os.environ["READFILE_MAX_MB"] = "300"; os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge
from tools_core import Drawing

KT = r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/1. Kien truc MN Gia Loc.dxf"
KC = r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/2. KetCau MN GiaLoc.dxf"

# Mỗi scenario: (nhom, file, [turns]); mỗi turn = (cau_hoi, engine_call|None). engine_call=(ten,ma,bs).
SCEN = [
 ("A. Diện tích cửa (đối tác muốn)", "KT", [
    ("Tổng diện tích cửa đi D1 là bao nhiêu?", ("dien_tich_cua", "cửa D1", "")),
    ("Diện tích cửa S1?", ("dien_tich_cua", "cửa S1", "")),
    ("Diện tích cửa CM1?", ("dien_tich_cua", "CM1", "")),
 ]),
 ("B. BT cột — thiếu chiều cao rồi nhập bù (hội thoại)", "KC", [
    ("Thể tích bê tông cột C1 là bao nhiêu?", ("the_tich_be_tong_cot", "C1", "")),
    ("Chiều cao cột là 3.6m", ("the_tich_be_tong_cot", "C1", '{"chieu_cao":3600}')),  # nhập bù, KHÔNG nhắc C1
 ]),
 ("C. BT cột C4 — ĐA tiết diện (cảnh báo)", "KC", [
    ("Tính thể tích bê tông cột C4, chiều cao 3.6m", ("the_tich_be_tong_cot", "C4", '{"chieu_cao":3600}')),
 ]),
 ("D. BT dầm — BẪY L-thép (phải bắt nhập L nhịp)", "KC", [
    ("Thể tích bê tông dầm DR-3?", ("the_tich_be_tong_dam", "DR-3", "")),
    ("Dầm dài 4m", ("the_tich_be_tong_dam", "DR-3", '{"chieu_dai":4000}')),
 ]),
 ("E. Ván khuôn cột", "KC", [
    ("Diện tích ván khuôn cột C1 với chiều cao 3.6m", ("dien_tich_van_khuon_cot", "C1", '{"chieu_cao":3600}')),
 ]),
 ("F. Bẫy chống bịa (cấu kiện KHÔNG tồn tại)", "KT", [
    ("Tính diện tích cửa gỗ lim GL9?", ("dien_tich_cua", "GL9", "")),
 ]),
 ("G. Regression — đọc số vẫn đúng (không phá GĐ1)", "KT", [
    ("Số lượng cửa D1?", None),
    ("Tổng khối lượng thép tròn?", None),
 ]),
]


def eng_truth(dwg, call):
    if not call: return None
    ten, ma, bs = call
    r = dwg.tinh_dai_luong(ten, ma, bs)
    if r.get("co_ket_qua"): return "ĐỦ → %s %s" % (r["ket_qua"], r["don_vi"])
    if r.get("khong_tim_thay"): return "KHÔNG TÌM THẤY ('%s' không có trong bản vẽ)" % ma
    if r.get("sai_loai"): return "SAI LOẠI ('%s' là %s)" % (ma, "/".join(r.get("loai_thuc_te", [])))
    if r.get("can_bo_sung"): return "THIẾU: %s (đã có: %s)" % (
        ",".join(t["ten"] for t in r["inputs_thieu"]), ",".join("%s=%s" % (x["ten"], x["gia_tri"]) for x in r["inputs_da_co"]))
    return "KHÔNG: " + (r.get("loi") or r.get("ghi_chu", ""))[:60]


def main():
    dwgs = {"KT": Drawing(KT), "KC": Drawing(KC)}
    br = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
    summ = {"KT": "KIẾN TRÚC", "KC": "KẾT CẤU"}
    out = open(os.path.join(HERE, "kichban_gd2_ketqua.jsonl"), "w", encoding="utf-8")
    cur = None
    for nhom, fk, turns in SCEN:
        if cur != fk:
            s = br.call("nap_ban_ve", {"path": KT if fk == "KT" else KC}, timeout=600); cur = fk
        print("\n" + "=" * 70 + "\n### %s [%s] ###" % (nhom, fk))
        hist = []
        for q, call in turns:
            truth = eng_truth(dwgs[fk], call)
            try: r = mcp_bridge.tra_loi_ai(br, q, summ[fk], history=hist); a = r["answer"]
            except Exception as e: a = "[[LỖI]] " + str(e)[:40]
            hist.append({"role": "user", "text": q}); hist.append({"role": "model", "text": a})
            print("\nHỎI:", q)
            if truth: print("  GROUND TRUTH (engine):", truth)
            print("  DEMO 2:", a[:260].replace("\n", " "))
            out.write(json.dumps({"nhom": nhom, "q": q, "truth": truth, "demo": a}, ensure_ascii=False) + "\n"); out.flush()
    out.close(); br.close()


if __name__ == "__main__":
    main()
