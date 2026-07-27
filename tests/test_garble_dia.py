# -*- coding: utf-8 -*-
"""L6 (kho kiến thức chỉ điểm — garble ĐƯỜNG KÍNH tầng CODE) — TẤT ĐỊNH, offline, KHÔNG tốn API.
Khoá: fold 'ỉ/Ỉ' + '/g|/G' (LIỀN SỐ, KHÔNG dính chữ trước) → 'ø' TRƯỚC unaccent; phản-khớp nguyên vẹn
('chỉ 10'/'nghỉ'/'thép I10'/'i=2%'/'kG//cm2'/'tỉ lệ'); canonical _norm('ỉ14')==_norm('Ø14'); 0 đổi số.
Bằng chứng corpus ≥3 firm: 'kim thu sét ỉ20' · 'Ỉ16X2400' vs 'Ø16 DÀI 2,4m' cùng file · '/g10' 67× cạnh a150
· 'MO/SC CA/M/RU /G8'=MÓC CẨU Ø8 · 'thép ỉ10 neo xà gồ' (KT CT-A). Quét 53 file: 98+568 hit, 0 phản-khớp.
Chạy: python tests/test_garble_dia.py"""
import os, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
os.environ.setdefault("READFILE_MAX_MB", "300")

import ezdxf
import tools_core as tc

PASS = FAIL = 0


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def main():
    print("[L6] garble đường kính: fold ỉ//g → ø có gông (trước unaccent), 0 phản-khớp, 0 đổi số")

    # ---- [G1] DƯƠNG: mọi dạng bằng-chứng-corpus fold đúng ----
    for s, want in [("dây tiếp địa ỉ14", "ø14"), ("kim thu sét ỉ20 dài 1000", "ø20"),
                    ("cọc thép mạ đồng Ỉ16X2400", "ø16x2400"), ("ống nhựa thông hơi ỉ50", "ø50"),
                    ("thép ỉ10 neo xà gồ", "ø10"), ("/g10", "ø10"),
                    ("MO/SC CA/M/RU /G8", "ø8"), ("2ỉ16", "2ø16")]:
        out = tc._norm_label(s)
        _emit("G1: %r chứa %r" % (s[:28], want), want in out, out)

    # ---- [G2] PHẢN-KHỚP: chữ-Việt-thật / thép hình I / độ dốc i / đơn vị — KHÔNG bị đụng ----
    for s in ["chỉ 10 ngày", "nghỉ 5 phút", "chỉ10", "thép I10", "i=2%",
              "Ra = 2800kG//cm2", "/gạch 10", "tỉ lệ 1:100", "Bỉ 2024", "xỉ than 20kg"]:
        khong_fold = tc.unaccent((s or "").translate(tc._GARBLE_FOLD))
        _emit("G2: phản-khớp %r nguyên vẹn" % s[:24], tc._norm_label(s) == khong_fold, tc._norm_label(s))

    # ---- [G3] CANONICAL: biến thể vỡ == dạng chuẩn sau _norm (tìm 'Ø14' thấy 'ỉ14') ----
    _emit("G3a: _norm('tiếp địa ỉ14') == _norm('tiếp địa Ø14')",
          tc._norm("tiếp địa ỉ14") == tc._norm("tiếp địa Ø14"), tc._norm("tiếp địa ỉ14"))
    _emit("G3b: _norm('/g10 a150') == _norm('Ø10 a150')",
          tc._norm("/g10 a150") == tc._norm("Ø10 a150"))

    # ---- [G4] ĐO ENGINE THẬT (synthetic): recall tăng, SỐ KHÔNG đổi ----
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for i, s in enumerate(["dây tiếp địa ỉ14", "chỉ 10 ngày", "+3.600", "-1.850", "/g10", "a150"]):
        msp.add_text(s).set_placement((0, i * 500))
    p = os.path.join(tempfile.mkdtemp(), "t.dxf"); doc.saveas(p)
    d = tc.Drawing(p)
    _emit("G4a: tìm 'Ø14' THẤY text vỡ 'ỉ14' (recall gain)",
          any("ỉ14" in h["vn"] or "ø14" in tc._norm_label(h["vn"]) for h in d.search_texts("Ø14")))
    _emit("G4b: tìm 'Ø10' thấy '/g10'", len(d.search_texts("Ø10")) >= 1)
    cd = d.cao_do_min_max()
    _emit("G4c: cao độ KHÔNG bị fold đụng (min -1.85 / max +3.6 giữ nguyên)",
          cd.get("cao_do_thap_nhat_m") == -1.85 and cd.get("cao_do_cao_nhat_m") == 3.6)
    _emit("G4d: 'chỉ 10 ngày' vẫn tìm được theo chữ thật (không bị biến dạng)",
          any("chỉ" in h["vn"] for h in d.search_texts("chỉ")))

    # ---- [G5] REAL-CORPUS (guard skip nếu thiếu — corpus gitignored) ----
    try:
        from corpus_local import KT
    except Exception:
        KT = ""
    if KT and os.path.isfile(KT):
        dk = tc.Drawing(KT)
        hits = [h["vn"] for h in dk.search_texts("Ø10")]
        _emit("G5: KT CT-A tìm 'Ø10' thấy 'thép ỉ10 neo xà gồ' (bằng chứng thật)",
              any("ỉ10" in v for v in hits), str(hits[:3]))
    else:
        print("  [..] BỎ QUA G5 (thiếu fixture corpus_local)")

    # ---- [G6] SOURCE-GUARD: fold nằm TRONG _garble_fold (chạy TRƯỚC unaccent ở cả _norm/_norm_label) ----
    src = open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read()
    _emit("G6: _GARBLE_DIA_RE áp trong _garble_fold + _norm_label = unaccent(_garble_fold(...))",
          "_GARBLE_DIA_RE.sub" in src and "unaccent(_garble_fold(s))" in src)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
