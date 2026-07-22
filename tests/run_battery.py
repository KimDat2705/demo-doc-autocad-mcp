# -*- coding: utf-8 -*-
"""
Chạy BỘ CÂU HỎI (battery.json do workflow thiết kế) qua DEMO 2 (Gemini + MCP), lưu câu trả lời.
Tuần tự, ghi JSONL từng câu -> không mất tiến độ nếu gián đoạn. Mỗi câu lưu kèm anh_id + handle
(để pha verify đối chiếu ground truth).
"""
import os, sys, io, json, time, traceback
os.environ["READFILE_MAX_MB"] = "300"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge

from corpus_local import KT, KC, HT   # corpus THAT giu ngoai repo (gitignored)
FILES = {
    "kientruc": (KT, "KIẾN TRÚC CT-A"),
    "ketcau":   (KC, "KẾT CẤU CT-A"),
    "hatang":   (HT, "HẠ TẦNG CT-K"),
}
TRAP_ON = "kientruc"   # câu 'any' (bẫy) chạy trên file kiến trúc (giàu cấu kiện nhất)
ORDER = ["kientruc", "ketcau", "hatang"]

BATTERY = os.path.join(HERE, "battery.json")
OUTJSONL = os.path.join(HERE, "battery_results.jsonl")


def main():
    battery = json.load(open(BATTERY, encoding="utf-8"))
    qs = battery["battery"] if isinstance(battery, dict) else battery
    by_file = {k: [] for k in FILES}
    for q in qs:
        f = q.get("file", "any")
        by_file.setdefault(TRAP_ON if f == "any" else f, []).append(q)
    total = sum(len(by_file[f]) for f in ORDER)
    print("Battery: %d câu (kientruc=%d, ketcau=%d, hatang=%d)" %
          (total, len(by_file["kientruc"]), len(by_file["ketcau"]), len(by_file["hatang"])))

    bridge = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
    print("Bridge OK, %d tool. USE_AI=%s MODEL=%s" % (len(bridge.tools), mcp_bridge.USE_AI, mcp_bridge.MODEL))
    out = open(OUTJSONL, "w", encoding="utf-8")
    done = 0
    t0 = time.time()
    for f in ORDER:
        path, summ_name = FILES[f]
        if not os.path.isfile(path):
            print("BỎ QUA (không có):", path); continue
        s = bridge.call("nap_ban_ve", {"path": path}, timeout=600)
        summary = "%s (AutoCAD %s), %s đối tượng, %s layer." % (
            summ_name, s.get("dxfversion"), s.get("tong_doi_tuong"), s.get("so_layer"))
        print("\n### NẠP %s: %s ###" % (f, summary))
        for q in by_file[f]:
            done += 1
            cau = q.get("cau_hoi", "")
            t = time.time()
            try:
                r = mcp_bridge.tra_loi_ai(bridge, cau, summary)
                ans = r.get("answer", ""); ev = r.get("evidence", []) or []
                rec = {"id": q.get("id"), "file": f, "loai": q.get("loai"), "cau_hoi": cau,
                       "ky_vong": q.get("ky_vong"), "loi_san": q.get("loi_san"),
                       "answer": ans, "anh_id": r.get("anh_id"),
                       "n_evidence": len(ev),
                       "handles": [e.get("handle") for e in ev][:30],
                       "evidence_text": [e.get("text") for e in ev][:15],
                       "thoi_gian_s": round(time.time() - t, 1)}
            except Exception as e:
                rec = {"id": q.get("id"), "file": f, "loai": q.get("loai"), "cau_hoi": cau,
                       "ky_vong": q.get("ky_vong"), "loi_san": q.get("loi_san"),
                       "answer": "[[LỖI]] %s: %s" % (type(e).__name__, e), "anh_id": None,
                       "n_evidence": 0, "handles": [], "evidence_text": [],
                       "thoi_gian_s": round(time.time() - t, 1)}
                traceback.print_exc()
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
            print("[%d/%d] (%s) %.0fs | %s -> %s" %
                  (done, total, q.get("loai", "?"), rec["thoi_gian_s"], cau[:55], rec["answer"][:90].replace("\n", " ")))
    out.close(); bridge.close()
    print("\nXONG %d câu trong %.0fs -> %s" % (done, time.time() - t0, OUTJSONL))


if __name__ == "__main__":
    main()
