# -*- coding: utf-8 -*-
"""
QA TẦNG DỮ LIỆU (tất định, KHÔNG Gemini). Đối chiếu 3 chiều cho mỗi file:
  (1) demo 2 tools_core  ==  demo 1 (app.py)        -> PORT-FAITHFULNESS (chống regression khi port)
  (2) demo 2 tools_core  ==  ezdxf đọc ĐỘC LẬP      -> GROUND TRUTH (chống đọc sai/thiếu ở chính lõi)
Chạy đa file (chống overfit). In bảng PASS/FAIL từng hạng mục.
"""
import os, sys, io
os.environ["READFILE_MAX_MB"] = "300"   # nâng cap để test cả file hạ tầng lớn (local RAM đủ)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import importlib.util
from collections import Counter
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
D2 = os.path.normpath(os.path.join(HERE, ".."))
D1 = os.path.normpath(os.path.join(HERE, "..", "..", "demo_doc_autocad"))
sys.path.insert(0, D2)
from tools_core import Drawing  # demo 2

# import demo 1 app.py dưới tên riêng (tránh đụng 'app' của demo 2)
def _load_demo1():
    sys.path.insert(0, D1)
    spec = importlib.util.spec_from_file_location("demo1app", os.path.join(D1, "app.py"))
    m = importlib.util.module_from_spec(spec); spec.modules = m
    sys.modules["demo1app"] = m
    spec.loader.exec_module(m)
    return m

from corpus_local import KT, KC, HT   # corpus THAT giu ngoai repo (gitignored)
FILES = [
    ("KIẾN TRÚC", KT),
    ("KẾT CẤU",  KC),
    ("HẠ TẦNG",  HT),
]
KEYWORDS = ["bê tông", "thép", "Ø16", "cửa", "móng", "cột", "dầm", "cống", "rãnh", "mương", "BTCT", "mác"]


def ground_truth_ezdxf(path):
    """Đọc ĐỘC LẬP bằng ezdxf (cách tối thiểu, khác tools_core) để làm chuẩn so."""
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    counts = Counter()
    n_text = n_attrib = 0
    for e in msp:
        t = e.dxftype(); counts[t] += 1
        if t in ("TEXT", "MTEXT"): n_text += 1
        if t == "INSERT":
            try:
                for _ in e.attribs: n_attrib += 1
            except Exception: pass
    return {"total": sum(counts.values()), "counts": dict(counts),
            "n_layers": len(list(doc.layers)), "n_text_mtext": n_text, "n_attrib": n_attrib,
            "dxfversion": doc.dxfversion}


def chk(results, name, a, b, note=""):
    ok = (a == b)
    results.append((ok, name, a, b, note))
    return ok


def run_file(label, path, demo1):
    print("\n" + "=" * 78)
    print("FILE [%s]: %s" % (label, os.path.basename(path)))
    print("=" * 78)
    results = []
    gt = ground_truth_ezdxf(path)
    d2 = Drawing(path)
    demo1.parse(path); S1 = demo1.STATE

    # (2) demo2 vs GROUND TRUTH ezdxf
    chk(results, "GT: tổng đối tượng", d2.total, gt["total"])
    chk(results, "GT: số layer", len(d2.layers), gt["n_layers"])
    chk(results, "GT: dxfversion", d2.dxfversion, gt["dxfversion"])
    # đếm TEXT+MTEXT+ATTRIB của d2.texts so với gt
    chk(results, "GT: số đoạn chữ (text+mtext+attrib)", len(d2.texts), gt["n_text_mtext"] + gt["n_attrib"])
    # đếm theo loại: INSERT, LINE, DIMENSION
    for t in ("INSERT", "LINE", "DIMENSION", "LWPOLYLINE", "MTEXT", "TEXT"):
        chk(results, "GT: counts[%s]" % t, d2.counts.get(t, 0), gt["counts"].get(t, 0))

    # (1) demo2 vs DEMO1 (port-faithfulness)
    chk(results, "PORT: tổng đối tượng", d2.total, S1.get("total"))
    chk(results, "PORT: số layer", len(d2.layers), len(S1.get("layers", [])))
    chk(results, "PORT: tên layer (set)", set(d2.layers), set(S1.get("layers", [])))
    chk(results, "PORT: số đoạn chữ", len(d2.texts), len(S1.get("texts", [])))
    chk(results, "PORT: số DIMENSION", len(d2.dims), len(S1.get("dims", [])))
    chk(results, "PORT: thép tổng kg", d2.thep.get("tong_kg"), S1.get("thep", {}).get("tong_kg"))
    chk(results, "PORT: thép hình tổng kg", d2.thep_hinh.get("tong_kg"), S1.get("thep_hinh", {}).get("tong_kg"))
    chk(results, "PORT: số mục qty_index", len(d2.qty_index), len(S1.get("qty_index", [])))
    chk(results, "PORT: số sheet", len(d2.sheets), len(S1.get("sheets", [])))

    # so search_texts + tra_so_luong cho từng từ khoá (port-faithfulness sâu)
    for kw in KEYWORDS:
        a = len(d2.search_texts(kw)); b = len(demo1.search_texts(kw))
        chk(results, "PORT search('%s') số kết quả" % kw, a, b)
        qa = [(m["label"], m["so_luong"]) for m in d2.tra_so_luong(kw)]
        qb = [(m["label"], m["so_luong"]) for m in demo1.tra_so_luong(kw)]
        chk(results, "PORT tra_so_luong('%s')" % kw, qa, qb)

    npass = sum(1 for r in results if r[0])
    print("Kết quả: %d/%d PASS" % (npass, len(results)))
    for ok, nm, a, b, note in results:
        if not ok:
            print("  🔴 FAIL %-40s demo2=%r  ref=%r %s" % (nm, a, b, note))
    # in vài chỉ số chính để mắt thường soi
    print("  • dxfversion=%s · %d layer · %d đối tượng · %d chữ · %d dim · %d sheet · thép=%s kg · qty=%d mục"
          % (d2.dxfversion, len(d2.layers), d2.total, len(d2.texts), len(d2.dims), len(d2.sheets),
             d2.thep.get("tong_kg"), len(d2.qty_index)))
    return npass, len(results)


def main():
    demo1 = _load_demo1()
    tot_p = tot_n = 0
    for label, path in FILES:
        if not os.path.isfile(path):
            print("BỎ QUA (không có):", path); continue
        try:
            p, n = run_file(label, path, demo1)
            tot_p += p; tot_n += n
        except Exception as e:
            import traceback; traceback.print_exc()
            print("🔴 LỖI khi test %s: %s" % (label, e))
    print("\n" + "#" * 78)
    print("TỔNG TẦNG DỮ LIỆU: %d/%d PASS" % (tot_p, tot_n))
    print("#" * 78)


if __name__ == "__main__":
    main()
