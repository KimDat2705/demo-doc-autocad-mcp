# -*- coding: utf-8 -*-
"""
SPIKE render + highlight (Cot moc 0, PA-D).
Muc tieu kiem chung 3 dieu, KHONG can AutoCAD:
  1. ezdxf.addons.drawing render duoc file CAD that ra PNG tren may (headless Agg).
  2. Lay duoc toa do (x,y) cac doan chu khop tu khoa (de highlight cau kien AI dem).
  3. Ve khoanh do quanh cac cau kien do + zoom -> "AI chi tan tay".

Chay: python spike_render.py <duong_dan.dxf> <tu_khoa>
"""
import os, sys, time, glob
import matplotlib
matplotlib.use("Agg")  # headless, khong can man hinh -> chay duoc tren cloud Linux
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, HatchPolicy
from ezdxf.bbox import extents
from ezdxf.math import BoundingBox2d, Vec2

# Tai dung bo giai ma font TCVN3 cua demo 1
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "demo_doc_autocad")))
try:
    from vntext import to_unicode
except Exception:
    to_unicode = lambda s: s

OUT = os.path.dirname(os.path.abspath(__file__))


def collect_texts(msp):
    """Gom (vn, x, y, handle) cho TEXT/MTEXT + ATTRIB trong block — giong _collect_entities demo 1."""
    items = []
    for e in msp:
        t = e.dxftype()
        if t in ("TEXT", "MTEXT"):
            raw = e.dxf.text if t == "TEXT" else e.text
            try:
                ins = e.dxf.insert; x, y = float(ins.x), float(ins.y)
            except Exception:
                x = y = 0.0
            items.append({"vn": to_unicode(raw), "x": x, "y": y, "handle": e.dxf.handle})
        elif t == "INSERT":
            try:
                for att in e.attribs:
                    raw = att.dxf.text
                    try:
                        ins = att.dxf.insert; x, y = float(ins.x), float(ins.y)
                    except Exception:
                        x = y = 0.0
                    items.append({"vn": to_unicode(raw), "x": x, "y": y, "handle": att.dxf.handle})
            except Exception:
                pass
    return items


# Cau hinh render NHE: BO hatch (thu pham MemoryError + timeout tren file nhieu sheet),
# gioi han do day net. -> render on dinh tren cloud.
_CFG = Configuration(hatch_policy=HatchPolicy.IGNORE, min_lineweight=0.3)


def quick_point(e):
    """Diem dai dien RE cua entity (doc thang dxf, KHONG qua bbox machinery -> nhanh ~50x).
    Du de clip theo SHEET (cac sheet cach xa nhau trong modelspace)."""
    d = e.dxf
    for attr in ("insert", "center", "start", "location"):
        if d.hasattr(attr):
            try:
                p = d.get(attr); return float(p[0]), float(p[1])
            except Exception:
                pass
    # polyline: dinh dau tien
    try:
        if e.dxftype() == "LWPOLYLINE":
            pts = list(e.get_points())
            if pts:
                return float(pts[0][0]), float(pts[0][1])
    except Exception:
        pass
    return None


def entities_in_window(msp, window, hard_cap=20000):
    """Lay entity co DIEM DAI DIEN nam trong 'window' (xmin,ymin,xmax,ymax). Re + nhanh."""
    x0, y0, x1, y1 = window
    out = []
    for e in msp:
        p = quick_point(e)
        if p is None:
            continue
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
            out.append(e)
            if len(out) >= hard_cap:
                break
    return out


def render_region(msp, doc, png_path, window, highlights=None, dpi=110):
    """Render CHI cac entity trong 'window' + khoanh do cau kien. window=(xmin,ymin,xmax,ymax)."""
    t0 = time.time()
    t_scan = time.time()
    ents = entities_in_window(msp, window)
    scan_s = time.time() - t_scan
    n = len(ents)
    fig = plt.figure(figsize=(16, 11))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    backend = MatplotlibBackend(ax)
    Frontend(RenderContext(doc), backend, config=_CFG).draw_entities(ents)
    ax.set_xlim(window[0], window[2]); ax.set_ylim(window[1], window[3])
    ax.set_aspect("equal")
    if highlights:
        r = max(window[2] - window[0], window[3] - window[1]) * 0.02
        for h in highlights:
            ax.add_patch(plt.Rectangle((h["x"] - r, h["y"] - r), 2 * r, 2 * r,
                                       fill=False, edgecolor="red", linewidth=2.0))
    fig.savefig(png_path, dpi=dpi)
    plt.close(fig)
    print("   (scan loc entity: %.1fs, ve+luu: %.1fs)" % (scan_s, time.time() - t0 - scan_s))
    return time.time() - t0, n


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    kw = (sys.argv[2] if len(sys.argv) > 2 else "C").lower()
    if not path or not os.path.isfile(path):
        print("Khong tim thay file:", path); return

    print("== Doc file:", os.path.basename(path), "(%.0f MB) ==" % (os.path.getsize(path) / 1e6))
    t0 = time.time()
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    print("  read: %.1fs, dxfversion=%s" % (time.time() - t0, doc.dxfversion))

    texts = collect_texts(msp)
    print("  so doan chu:", len(texts))

    # Tim cau kien khop tu khoa -> toa do
    kw_l = kw.lower()
    hits = [t for t in texts if kw_l in (t["vn"] or "").lower() and (t["x"] or t["y"])]
    print("== Tu khoa '%s': %d doan chu khop (co toa do)" % (kw, len(hits)))
    if not hits:
        print("  (khong co de highlight; thu tu khoa khac)"); return
    for h in hits[:6]:
        print("   [%s] (%.0f,%.0f) %s" % (h["handle"], h["x"], h["y"], (h["vn"] or "")[:40]))

    xs = [h["x"] for h in hits]; ys = [h["y"] for h in hits]
    mx, Mx, my, My = min(xs), max(xs), min(ys), max(ys)
    padx = max((Mx - mx) * 0.12, 2500); pady = max((My - my) * 0.12, 2500)
    window = (mx - padx, my - pady, Mx + padx, My + pady)
    print("== Vung render (clip): rong=%.0f cao=%.0f" % (window[2] - window[0], window[3] - window[1]))

    # Render CHI vung chua cau kien + khoanh do (KHONG render ca file -> tranh MemoryError)
    p = os.path.join(OUT, "out_highlight_region.png")
    dt, n = render_region(msp, doc, p, window, highlights=hits)
    print("== Render vung + highlight: %.1fs, %d entity trong vung -> %s (%.0f KB)"
          % (dt, n, p, os.path.getsize(p) / 1024))
    print("\nXONG. Mo file PNG de kiem chat luong render + highlight.")


if __name__ == "__main__":
    main()
