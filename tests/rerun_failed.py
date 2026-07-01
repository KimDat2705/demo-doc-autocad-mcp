# -*- coding: utf-8 -*-
"""Chạy lại các câu fail/partial/lỗi/chưa-chạy trên bản ĐÃ VÁ. Chống 503 bằng retry backoff.
Đối chiếu FILE MẪU (ground truth), không liên quan demo 1. Ghi rerun_results.jsonl."""
import os, sys, io, json, time, traceback
os.environ["READFILE_MAX_MB"] = "300"
os.environ.setdefault("GEMINI_MODEL", "gemini-3.5-flash")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge

FILES = {
    "kientruc": (r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/1. Kien truc MN Gia Loc.dxf", "KIẾN TRÚC MN Gia Lộc"),
    "ketcau":   (r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/input_files/_dxf/BV+DT MN Gia Loc/2. KetCau MN GiaLoc.dxf", "KẾT CẤU MN Gia Lộc"),
    "hatang":   (r"D:/Dat-Antigravity/HeThongThiCongXayDung-AnhTu/demo_doc_autocad/_uploads/rachmop.dxf", "HẠ TẦNG rachmop"),
}
TRAP_ON = "kientruc"
ORDER = ["kientruc", "ketcau", "hatang"]


def ask_robust(br, q, summ, tries=6):
    """Hỏi với retry backoff khi 503/lỗi tạm (Flash 'high demand')."""
    delay = 5
    for k in range(tries):
        try:
            return mcp_bridge.tra_loi_ai(br, q, summ)
        except Exception as e:
            msg = str(e)
            if k == tries - 1:
                return {"answer": "[[LỖI sau %d lần]] %s" % (tries, msg[:70]), "evidence": [], "anh_id": None}
            time.sleep(min(delay, 60)); delay *= 2   # 5,10,20,40,60,60s


def main():
    ids = set(json.load(open(os.path.join(HERE, "rerun_ids.json"))))
    # RESUME: bỏ qua câu đã có trong rerun_results.jsonl (ghi tiếp, không chạy lại)
    outpath = os.path.join(HERE, "rerun_results.jsonl")
    done_ids = set()
    if os.path.isfile(outpath):
        for l in open(outpath, encoding="utf-8"):
            try: done_ids.add(json.loads(l)["id"])
            except Exception: pass
    ids = ids - done_ids
    print("Resume: đã xong %d, còn %d câu." % (len(done_ids), len(ids)))
    batt = {q["id"]: q for q in json.load(open(os.path.join(HERE, "battery.json"), encoding="utf-8"))["battery"]}
    byfile = {k: [] for k in FILES}
    for i in sorted(ids):
        q = batt.get(i)
        if not q: continue
        f = q.get("file", "any")
        byfile.setdefault(TRAP_ON if f == "any" else f, []).append(q)
    total = sum(len(byfile[f]) for f in ORDER)
    print("Chạy lại %d câu trên bản đã vá. MODEL=%s MAX_TURNS=%s" % (total, mcp_bridge.MODEL, mcp_bridge.MAX_TURNS))

    br = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
    out = open(outpath, "a", encoding="utf-8")   # APPEND -> giữ kết quả cũ
    done = 0; t0 = time.time()
    for f in ORDER:
        path, name = FILES[f]
        if not os.path.isfile(path) or not byfile[f]: continue
        s = br.call("nap_ban_ve", {"path": path}, timeout=600)
        summ = "%s (AutoCAD %s), %s đối tượng, %s layer." % (name, s.get("dxfversion"), s.get("tong_doi_tuong"), s.get("so_layer"))
        print("\n### NẠP %s ###" % f)
        for q in byfile[f]:
            done += 1
            r = ask_robust(br, q["cau_hoi"], summ)
            ev = r.get("evidence", []) or []
            rec = {"id": q["id"], "file": f, "loai": q["loai"], "cau_hoi": q["cau_hoi"],
                   "ky_vong": q["ky_vong"], "loi_san": q["loi_san"], "answer": r.get("answer", ""),
                   "anh_id": r.get("anh_id"), "n_evidence": len(ev),
                   "handles": [e.get("handle") for e in ev][:20], "evidence_text": [e.get("text") for e in ev][:10]}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
            err = "[[LỖI" in rec["answer"]
            print("[%d/%d] %s id%d %s -> %s" % (done, total, q["loai"][:12], q["id"],
                  "⚠️503" if err else "ok", rec["answer"][:70].replace("\n", " ")))
    out.close(); br.close()
    print("\nXONG %d câu / %.0fs -> rerun_results.jsonl" % (done, time.time() - t0))


if __name__ == "__main__":
    main()
