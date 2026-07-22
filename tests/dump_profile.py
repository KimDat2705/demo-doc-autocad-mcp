# -*- coding: utf-8 -*-
"""Dump 'hồ sơ nội dung' từng file (text duy nhất, block, layer, qty, thép, dim) ra JSON
để phân tích GAP (đọc thiếu) + thiết kế câu hỏi. KHÔNG Gemini."""
import os, sys, io, json
os.environ["READFILE_MAX_MB"] = "300"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from tools_core import Drawing
from collections import Counter

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "_renders"))  # scratch chung
from corpus_local import KT, KC, HT   # corpus THAT giu ngoai repo (gitignored)
FILES = {"kientruc": KT, "ketcau": KC, "hatang": HT}

for key, path in FILES.items():
    d = Drawing(path)
    # text duy nhất (gộp trùng do lặp nhiều sheet), giữ thứ tự, cắt 700
    seen, uniq = set(), []
    for t in d.texts:
        v = (t["vn"] or "").strip()
        if v and v.lower() not in seen:
            seen.add(v.lower()); uniq.append(v)
    prof = {
        "file": os.path.basename(path), "dxfversion": d.dxfversion,
        "tong_doi_tuong": d.total, "counts": d.counts, "so_layer": len(d.layers),
        "layers": d.layers,
        "blocks_top": dict(sorted(d.blocks.items(), key=lambda x: -x[1])[:40]),
        "so_text_duy_nhat": len(uniq), "text_duy_nhat": uniq[:700],
        "qty_index": [{"label": e["label"], "so_luong": e["so_luong"], "nguon": e["nguon"]} for e in d.qty_index],
        "thep_by_dk": {k: {"so_thanh": v["so_thanh"], "kg": round(v["kg"], 1)} for k, v in (d.thep.get("by_dk") or {}).items()},
        "thep_hinh": {k: {"so": v["so"], "kg": round(v["kg"], 1)} for k, v in (d.thep_hinh.get("by_show") or {}).items()},
        "thep_tong_kg": d.thep.get("tong_kg"),
        "dim_pho_bien": d.dim_top[:20], "dim_min": d.dim_vals[0] if d.dim_vals else None,
        "dim_max": d.dim_vals[-1] if d.dim_vals else None, "so_dim": len(d.dims),
        "sheets": [s["title"] for s in d.sheets][:60],
    }
    fp = os.path.join(OUT, "profile_%s.json" % key)
    json.dump(prof, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%-9s -> %s | %d text duy nhat | %d qty | %d block | %d sheet | thep=%s kg"
          % (key, os.path.basename(fp), len(uniq), len(prof["qty_index"]), len(d.blocks), len(d.sheets), prof["thep_tong_kg"]))
