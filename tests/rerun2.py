# -*- coding: utf-8 -*-
"""Re-run 23 câu còn fail/partial (sau vòng rerun) trên gemini-2.5-flash + fix ép-trả-lời.
Đối chiếu file mẫu. Ghi rerun2_results.jsonl."""
import os, sys, io, json, time
os.environ["READFILE_MAX_MB"] = "300"
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge

from corpus_local import KT, KC, HT   # corpus THAT giu ngoai repo (gitignored)
FILES = {
    "kientruc": (KT, "KIẾN TRÚC"),
    "ketcau":   (KC, "KẾT CẤU"),
    "hatang":   (HT, "HẠ TẦNG"),
}
TRAP_ON = "kientruc"

# fail+partial ids tu verify rerun (wejj5sktt)
V = json.load(open("C:/Users/ADMIN/AppData/Local/Temp/claude/D--Dat-Antigravity-HeThongThiCongXayDung-AnhTu/8719f77c-f8b8-4d18-93d1-752293042a4c/tasks/wejj5sktt.output", encoding="utf-8"))["result"]
ids = sorted(f["id"] for f in V["loi_con_lai"])
batt = {q["id"]: q for q in json.load(open(os.path.join(HERE, "battery.json"), encoding="utf-8"))["battery"]}
byfile = {}
for i in ids:
    q = batt.get(i)
    if not q: continue
    f = q.get("file", "any"); f = TRAP_ON if f == "any" else f
    byfile.setdefault(f, []).append(q)

print("Re-run %d cau tren %s" % (len(ids), os.environ["GEMINI_MODEL"]))
br = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
out = open(os.path.join(HERE, "rerun2_results.jsonl"), "w", encoding="utf-8")
for f in ["kientruc", "ketcau", "hatang"]:
    if f not in byfile: continue
    path, name = FILES[f]
    s = br.call("nap_ban_ve", {"path": path}, timeout=600)
    summ = "%s (%s đối tượng, %s layer)" % (name, s.get("tong_doi_tuong"), s.get("so_layer"))
    for q in byfile[f]:
        t = time.time()
        try: r = mcp_bridge.tra_loi_ai(br, q["cau_hoi"], summ)
        except Exception as e: r = {"answer": "[[LỖI]] " + str(e)[:50], "evidence": [], "anh_id": None}
        ev = r.get("evidence", []) or []
        rec = {"id": q["id"], "file": f, "loai": q["loai"], "cau_hoi": q["cau_hoi"], "ky_vong": q["ky_vong"],
               "loi_san": q["loi_san"], "answer": r.get("answer", ""), "anh_id": r.get("anh_id"),
               "n_evidence": len(ev), "handles": [e.get("handle") for e in ev][:20],
               "evidence_text": [e.get("text") for e in ev][:10]}
        out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
        bo = "quá nhiều bước" in rec["answer"] or "phức tạp" in rec["answer"]
        print("[%.0fs] id%-3d %-10s -> %s%s" % (time.time() - t, q["id"], q["loai"][:10],
              rec["answer"][:65].replace("\n", " "), "  ⚠️BỎCUỘC" if bo else ""))
out.close(); br.close()
print("XONG -> rerun2_results.jsonl")
