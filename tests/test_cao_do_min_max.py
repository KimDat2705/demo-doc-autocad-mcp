# -*- coding: utf-8 -*-
"""cao_do_min_max (id135-recall) — CAO ĐỘ THẤP/SÂU NHẤT + CAO NHẤT đọc RAW từ marker, KÈM handle.
KHÁC thong_tin_tang: KHÔNG lọc tần suất ≥4 (đó là lý do id135 miss mốc sâu). TẤT ĐỊNH, OFFLINE.
Chạy:  python tests/test_cao_do_min_max.py

Kiểm: real Gia Lộc KC/KT (min/max + HANDLE + nguyên văn) · file rỗng -> co_cao_do=False (LỘ) ·
synthetic: G1 bắt buộc dấu · G3 loại layer thép khỏi min/max (LỘ ở canh_bao) · inline/outlier -> nghi_ngo ·
2 thập phân (id135 -14.26) · tương tác grounding-guard.  (9T KC min=-3.0 đã verify thủ công — không nạp 120MB ở đây.)"""
import os, sys, io
os.environ.setdefault("READFILE_MAX_MB", "500")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import tools_core as tc

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
KC = os.path.join(BASE, "BV+DT MN Gia Loc", "2. KetCau MN GiaLoc.dxf")
KT = os.path.join(BASE, "BV+DT MN Gia Loc", "1. Kien truc MN Gia Loc.dxf")
CUA = os.path.join(BASE, "0. Demo - Bang thong ke cua.dxf")

PASS = FAIL = SKIP = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def skip(name):
    global SKIP
    SKIP += 1
    print("  [..] BO QUA %s (thieu fixture)" % name)


class _Fake:
    """Đối tượng tối thiểu — cao_do_min_max chỉ đọc self.texts."""
    def __init__(self, texts): self.texts = texts


def _txt(vn, handle="H", layer="0"):
    return {"vn": vn, "handle": handle, "layer": layer, "text": vn, "x": 0.0, "y": 0.0}


def main():
    print("[R] REAL Gia Lộc — min/max + HANDLE + nguyên văn (chống regress khi engine đổi thứ tự)")
    if os.path.isfile(KC):
        r = tc.Drawing(KC).cao_do_min_max()
        ok("KC: co_cao_do + MIN=-1.85 handle FEF03 '-1.850'",
           r.get("co_cao_do") and r["cao_do_thap_nhat_m"] == -1.85
           and r["thap_nhat"]["handle"] == "FEF03" and r["thap_nhat"]["nguyen_van"] == "-1.850",
           r.get("thap_nhat"))
        ok("KC: MAX=+10.8 handle 11FA7D '+10.800'",
           r["cao_do_cao_nhat_m"] == 10.8 and r["cao_nhat"]["handle"] == "11FA7D" and r["cao_nhat"]["nguyen_van"] == "+10.800",
           r.get("cao_nhat"))
    else:
        skip("KC")
    if os.path.isfile(KT):
        r = tc.Drawing(KT).cao_do_min_max()
        ok("KT: MIN=-2.1 handle A51A7, MAX=+10.8 handle 40ABE",
           r.get("co_cao_do") and r["cao_do_thap_nhat_m"] == -2.1 and r["thap_nhat"]["handle"] == "A51A7"
           and r["cao_do_cao_nhat_m"] == 10.8 and r["cao_nhat"]["handle"] == "40ABE",
           (r.get("cao_do_thap_nhat_m"), r.get("cao_do_cao_nhat_m")))
    else:
        skip("KT")
    if os.path.isfile(CUA):
        r = tc.Drawing(CUA).cao_do_min_max()
        ok("Demo cửa: co_cao_do=False, so_marker=0 (LỘ thất bại, KHÔNG bịa)", r.get("co_cao_do") is False and r.get("so_marker") == 0)
    else:
        skip("CUA")

    print("[G1] BẮT BUỘC dấu +/-/± (toạ độ/kích thước trơn KHÔNG thành marker)")
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("123456.789"), _txt("3.600"), _txt("-1.850", "A", "0"), _txt("±0.000", "B", "0")]))
    ok("chỉ '-1.850' và '±0.000' là marker (3.600/toạ độ trơn bị loại)",
       r.get("co_cao_do") and r["cao_do_thap_nhat_m"] == -1.85 and r["cao_do_cao_nhat_m"] == 0.0 and r["so_marker"] == 2,
       (r.get("cao_do_thap_nhat_m"), r.get("cao_do_cao_nhat_m"), r.get("so_marker")))

    print("[G3] LOẠI marker layer THÉP khỏi min/max, LỘ ở canh_bao")
    r = tc.Drawing.cao_do_min_max(_Fake([
        _txt("-44.100", "S1", "KCS_SOTHEP_TEXT"), _txt("-3.000", "T1", "KCS_TEXT"),
        _txt("+7.200", "T2", "0"), _txt("+33.700", "S2", "rebar_note")]))
    ok("MIN=-3.0 (KHÔNG -44.1 thép), MAX=+7.2 (KHÔNG +33.7 rebar)",
       r["cao_do_thap_nhat_m"] == -3.0 and r["cao_do_cao_nhat_m"] == 7.2, (r["cao_do_thap_nhat_m"], r["cao_do_cao_nhat_m"]))
    ok("-44.1 & +33.7 nằm trong canh_bao (không giấu)",
       {-44.1, 33.7} <= {c["gia_tri_m"] for c in r["canh_bao"]})

    print("[G4/G5] extreme cô lập / inline -> nghi_ngo=true (chỉ FLAG, không âm thầm loại)")
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("+3.600", "B"), _txt("+7.200", "C"), _txt("-99.999", "D")]))
    ok("MIN=-99.999 vẫn báo (raw) NHƯNG nghi_ngo=true (outlier-gap)",
       r["cao_do_thap_nhat_m"] == -99.999 and r["thap_nhat"]["nghi_ngo"] is True)
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("CỐT NỀN HOÀN THIỆN -2.700 (mặt cắt)", "B", "Net Text")]))
    ok("marker inline ('... -2.700 ...') -> nghi_ngo=true", any(c == -2.7 for c in r["tat_ca_cao_do_m"]) and r["thap_nhat"]["nghi_ngo"] is True)

    print("[id135] 2 thập phân (-14.26) đọc được (không chỉ 3 thập phân)")
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("-14.26", "H1"), _txt("±0.000", "H2"), _txt("+3.60", "H3")]))
    ok("'-14.26' (2 thập phân) -> MIN=-14.26 handle H1", r["cao_do_thap_nhat_m"] == -14.26 and r["thap_nhat"]["handle"] == "H1")

    print("[guard] tương tác grounding-guard (mcp_bridge)")
    import mcp_bridge as B
    nums = B._collect_numbers({"cao_do_thap_nhat_m": -1.85, "cao_do_cao_nhat_m": 10.8, "canh_bao": [{"gia_tri_m": -44.1}]})
    ok("số cao_do vào tool_numbers -> answer '-1.85m' GIỮ", B._guard_text("Cao độ thấp nhất là -1.85m.", nums) != B.REFUSE_MESSAGE)
    ok("answer bịa '-99m' (không trong tool) -> guard CHẶN", B._guard_text("Cao độ thấp nhất là -99m.", nums) == B.REFUSE_MESSAGE)

    if SKIP:
        print("CANH BAO: %d nhom BO QUA (thieu fixture)" % SKIP)
    print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
