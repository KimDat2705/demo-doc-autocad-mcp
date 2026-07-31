# -*- coding: utf-8 -*-
"""Quét lỗi hệ thống + chia chunk + factsheet cho workflow verify."""
import os, sys, io, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
RDIR = os.path.normpath(os.path.join(HERE, "..", "_renders"))
# argv[1] = ten file jsonl ket qua (mac dinh snapshot); argv[2] = thu muc chunk
SRC_NAME = sys.argv[1] if len(sys.argv) > 1 else "battery_results_flash_snapshot.jsonl"
_SUB = sys.argv[2] if len(sys.argv) > 2 else "verify_chunks"
# ⚠ HANG RAO CHONG XOA NHAM (them 2026-07-31). Truoc day: CH = join(HERE, argv[2]) roi
# `os.remove` MOI *.json trong CH. Da kiem bang duong dan: argv[2] = "" hoac "." cho CH == tests/
# -> lenh xoa quet trung `battery.json` (bo 198 cau, GITIGNORED nen chi co MOT ban), kem
# `kichban_ketqua.json` va `rerun_ids.json`. Mot lan go nham la mat.
if _SUB.strip() in ("", ".", "..") or os.path.isabs(_SUB):
    sys.exit("DUNG: argv[2] (thu muc chunk) khong duoc rong / '.' / '..' / duong dan tuyet doi.")
CH = os.path.abspath(os.path.join(HERE, _SUB))
if os.path.dirname(CH.rstrip(os.sep)) != os.path.abspath(HERE) or CH.rstrip(os.sep) == os.path.abspath(HERE):
    sys.exit("DUNG: thu muc chunk phai la MOT thu muc con TRUC TIEP cua tests/ (nhan duoc: %s)" % CH)
os.makedirs(CH, exist_ok=True)
if glob.glob(os.path.join(CH, "*.jsonl")):
    sys.exit("DUNG: %s chua file .jsonl -> trong nhu thu muc DU LIEU, khong phai thu muc chunk." % CH)
for f in glob.glob(os.path.join(CH, "chunk_*.json")): os.remove(f)   # CHI xoa chunk do chinh no sinh

SRC = os.path.join(HERE, SRC_NAME)
R = [json.loads(l) for l in open(SRC, encoding="utf-8")]
R = [r for r in R if "[[LỖI" not in r["answer"]]   # bỏ câu lỗi 503/504 (không có gì để chấm)

# --- factsheet tu profile ---
def factsheet(key):
    fp = os.path.join(RDIR, "profile_%s.json" % key)
    if not os.path.isfile(fp):      # LO ro nguyen nhan thay vi nem FileNotFoundError tran
        sys.exit("DUNG: thieu %s. Chay `python tests/dump_profile.py` de sinh lai profile truoc." % fp)
    p = json.load(open(fp, encoding="utf-8"))
    return {
        "tong_doi_tuong": p["tong_doi_tuong"], "so_layer": p["so_layer"], "so_dim": p["so_dim"],
        "dim_min": p["dim_min"], "dim_max": p["dim_max"],
        "qty_index": {e["label"]: e["so_luong"] for e in p["qty_index"]},
        "thep_tron_kg": p["thep_tong_kg"], "thep_tron_by_dk": p["thep_by_dk"], "thep_hinh": p["thep_hinh"],
        "so_block_loai": len(p.get("blocks_top", {})), "counts": p["counts"],
    }
FS = {k: factsheet(k) for k in ("kientruc", "ketcau", "hatang")}

# --- quét lỗi hệ thống ---
errs = [r for r in R if "[[LỖI]]" in r["answer"]]
malformed = [r for r in R if "gọi công cụ sai định dạng" in r["answer"] or "MALFORMED" in r["answer"]]
cut = [r for r in R if "quá dài" in r["answer"] or "MAX_TOKENS" in r["answer"]]
empty = [r for r in R if len(r["answer"].strip()) < 15]
hl = [r for r in R if r["loai"] == "highlight"]
hl_img = [r for r in hl if r.get("anh_id")]
print("=== LỖI HỆ THỐNG ===")
print("  [[LỖI]] (504/exception):", len(errs), [r["id"] for r in errs])
print("  MALFORMED_FUNCTION_CALL:", len(malformed), [r["id"] for r in malformed])
print("  MAX_TOKENS cắt:", len(cut), [r["id"] for r in cut])
print("  Trả lời rỗng/quá ngắn:", len(empty), [r["id"] for r in empty])
print("  Highlight ra ảnh: %d/%d" % (len(hl_img), len(hl)), "| thiếu ảnh:", [r["id"] for r in hl if not r.get("anh_id")])

# --- chia chunk theo file, ~12 cau/chunk ---
byfile = {"kientruc": [], "ketcau": [], "hatang": []}
for r in R:
    byfile.setdefault(r["file"], []).append(r)
n = 0
for f, items in byfile.items():
    for i in range(0, len(items), 12):
        n += 1
        chunk = {"file": f, "factsheet": FS.get(f, {}),
                 "items": [{"id": x["id"], "loai": x["loai"], "cau_hoi": x["cau_hoi"],
                            "ky_vong": x["ky_vong"], "loi_san": x["loi_san"],
                            "answer": x["answer"], "anh_id": x.get("anh_id"),
                            "n_evidence": x.get("n_evidence"), "handles": x.get("handles", [])[:12],
                            "evidence_text": x.get("evidence_text", [])[:8]} for x in items[i:i+12]]}
        json.dump(chunk, open(os.path.join(CH, "chunk_%02d.json" % n), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
print("\nĐã ghi %d chunk vào %s" % (n, CH))
