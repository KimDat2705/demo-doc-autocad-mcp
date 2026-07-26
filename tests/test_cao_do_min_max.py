# -*- coding: utf-8 -*-
"""cao_do_min_max (id135-recall) — CAO ĐỘ THẤP/SÂU NHẤT + CAO NHẤT đọc RAW từ marker, KÈM handle.
KHÁC thong_tin_tang: KHÔNG lọc tần suất ≥4 (đó là lý do id135 miss mốc sâu). TẤT ĐỊNH, OFFLINE.
Chạy:  python tests/test_cao_do_min_max.py

Kiểm: real CT-A KC/KT (min/max + HANDLE + nguyên văn) · file rỗng -> co_cao_do=False (LỘ) ·
synthetic: G1 bắt buộc dấu · G3 loại layer thép khỏi min/max (LỘ ở canh_bao) · inline/outlier -> nghi_ngo ·
2 thập phân (id135 -14.26) · tương tác grounding-guard.  (9T KC min=-3.0 đã verify thủ công — không nạp 120MB ở đây.)"""
import os, sys, io
os.environ.setdefault("READFILE_MAX_MB", "500")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import tools_core as tc

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
# Ten thu muc/file that giu NGOAI repo (gitignored) — xem corpus_local.example.py
try:
    from corpus_local import KT, KC
except Exception:
    KT = KC = ""
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
    """Đối tượng tối thiểu — cao_do_min_max đọc self.texts (+ L4 kho kiến thức: mượn method graft THẬT
    của Drawing + state hỏi, để nhánh marker-ÂM-dạng-cách chạy y hệt sản phẩm, không phải stub né)."""
    _kb_hoi_am_cach = tc.Drawing._kb_hoi_am_cach
    def __init__(self, texts):
        self.texts = texts
        self.kb_hoi, self.kb_da_phat = {}, set()


def _txt(vn, handle="H", layer="0"):
    return {"vn": vn, "handle": handle, "layer": layer, "text": vn, "x": 0.0, "y": 0.0}


def main():
    print("[R] REAL CT-A — min/max + HANDLE + nguyên văn (chống regress khi engine đổi thứ tự)")
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

    print("[COC] HỢP ĐỒNG NGỮ NGHĨA: 'thấp nhất trên bản vẽ' ≠ 'đáy móng' (GĐ4 — móng cọc CT-C)")
    # GĐ4 tưởng -22.75 (mầm non 3T) là RÁC → suýt vá. Red-team + tự kiểm chứng BÁC BỎ: file là MÓNG CỌC
    # (TCVN 10304, nhãn 'ĐẦU CỌC', sơ đồ cọc tỷ lệ 1:1 khớp 0.996, marker lặp 2 lần) ⇒ -22.75 = MŨI CỌC THẬT,
    # -1.85 = ĐÁY ĐÀI. Tool trả ĐÚNG. Rủi ro thật nằm ở MÔ TẢ (hứa 'đáy móng' mà trả min mọi marker).
    # Test này KHOÁ: (a) KHÔNG được lọc mốc sâu cô lập; (b) mô tả phải cảnh báo mũi-cọc-≠-đáy-đài.
    r = tc.Drawing.cao_do_min_max(_Fake([
        _txt("-1.850", "A", "KC-CHUNG-KYHIEU"), _txt("-1.150", "B", "KC-CHUNG-KYHIEU"),
        _txt("±0.000", "C", "KC-CHUNG-KYHIEU"), _txt("+3.600", "D", "KC-CHUNG-KYHIEU"),
        _txt("-22.750", "E", "KC-CHUNG-KYHIEU")]))
    ok("mốc cọc sâu cô lập -22.75 VẪN được trả (KHÔNG lọc — lọc = tái sinh id135)",
       r["cao_do_thap_nhat_m"] == -22.75 and r["thap_nhat"]["handle"] == "E", r.get("thap_nhat"))
    ok("ghi_chu CẢNH BÁO 'mũi cọc' ≠ 'đáy móng' (vá hợp đồng ngữ nghĩa, KHÔNG vá số)",
       "MŨI CỌC" in r["ghi_chu"] and "đáy móng" in r["ghi_chu"], r["ghi_chu"][-120:])
    import mcp_bridge as _B
    ok("SYSTEM_PROMPT: bỏ 'đáy móng' khỏi mô tả tool + dặn HỎI LẠI khi hỏi đáy móng",
       "MŨI CỌC" in _B.SYSTEM_PROMPT and "HỎI LẠI" in _B.SYSTEM_PROMPT)

    print("[F1] G3-fallback: MỌI marker ở layer thép -> LỘ THẤT BẠI, KHÔNG phong số thép làm cao độ")
    # TRƯỚC: `pool = [...] or found` -> -44.1 (thép) vừa là đáp án (nghi_ngo=false) VỪA nằm trong canh_bao
    # ghi 'đã loại khỏi min/max' => output tự mâu thuẫn + prompt cấm lấy số canh_bao -> AI hết số hợp lệ.
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("-44.100", "S1", "KCS_SOTHEP"), _txt("+33.700", "S2", "rebar_note")]))
    ok("co_cao_do=False (KHÔNG trả -44.1 làm cao độ)", r.get("co_cao_do") is False, r.get("cao_do_thap_nhat_m"))
    ok("KHÔNG có cao_do_thap_nhat_m (không mâu thuẫn với canh_bao)", "cao_do_thap_nhat_m" not in r, sorted(r.keys()))
    ok("2 giá trị thép VẪN lộ ở canh_bao (không giấu)", {-44.1, 33.7} == {c["gia_tri_m"] for c in r["canh_bao"]})
    ok("ghi_chu nói rõ vì sao + cấm ước đoán", "layer THÉP" in r["ghi_chu"] and "đừng ước" in r["ghi_chu"].lower())

    print("[F2] _nghi(): 2 giá trị duy nhất PHẢI cờ được (trước: thr=max(3g,5)>=3g>g -> không bao giờ cờ)")
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("-22.750", "B")]))
    ok("2 giá trị, gap 22.75 -> MIN=-22.75 nghi_ngo=TRUE (trước là False)",
       r["cao_do_thap_nhat_m"] == -22.75 and r["thap_nhat"]["nghi_ngo"] is True, r.get("thap_nhat"))
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("-0.050", "B"), _txt("-22.750", "C")]))
    ok("3 giá trị 0/-0.05/-22.75 -> cờ (trước: median-TRÊN chọn gap 22.7 -> thr=68.1 -> thoát)",
       r["thap_nhat"]["nghi_ngo"] is True, r.get("thap_nhat"))
    # outlier KHÔNG còn tự thổi ngưỡng: thêm/bớt 1 marker vô can KHÔNG được lật cờ
    a = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("+3.600", "B"), _txt("+7.200", "C"), _txt("-22.750", "D")]))
    b = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("+3.600", "B"), _txt("-22.750", "D")]))
    ok("bớt 1 marker vô can (+7.2) KHÔNG lật cờ của -22.75 (ổn định)",
       a["thap_nhat"]["nghi_ngo"] is True and b["thap_nhat"]["nghi_ngo"] is True,
       (a["thap_nhat"]["nghi_ngo"], b["thap_nhat"]["nghi_ngo"]))
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("-1.850", "A")]))
    ok("1 giá trị duy nhất -> KHÔNG cờ (không có gì để so, không bịa nghi ngờ)",
       r["thap_nhat"]["nghi_ngo"] is False, r.get("thap_nhat"))

    print("[F3] _CD_INL v2 (sau red-team): '-' dạng CÁCH -> canh_bao (LỘ); '+/±' dạng cách -> THU LẠI vào min/max")
    # FP 'CH - 2.700': KHÔNG bịa thành min, NHƯNG cũng KHÔNG biến mất -> LỘ ở canh_bao (đối chiếu tay).
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("-1.600", "A"), _txt("±0.000", "B"), _txt("CH - 2.700", "C", "Net Text")]))
    cb = {c["gia_tri_m"] for c in r.get("canh_bao", [])}
    ok("'CH - 2.700' KHÔNG vào min/max (min=-1.6, -2.7 ngoài tat_ca)",
       r["cao_do_thap_nhat_m"] == -1.6 and -2.7 not in r["tat_ca_cao_do_m"], r["tat_ca_cao_do_m"])
    ok("'CH - 2.700' LỘ ở canh_bao (không mất âm thầm)", -2.7 in cb, cb)
    # RED-TEAM ADJUSTMENT (bắt buộc): id135 'cốt - 14.260' dạng CÁCH inline PHẢI nằm trong canh_bao, KHÔNG vắng
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("cọc cốt - 14.260 (mặt cắt)", "H1"), _txt("±0.000", "H2"), _txt("+3.600", "H3")]))
    cb = {c["gia_tri_m"] for c in r.get("canh_bao", [])}
    ok("id135 'cốt - 14.260' dạng CÁCH -> LỘ ở canh_bao (thất bại phải lộ, KHÔNG mất âm thầm)", -14.26 in cb, cb)
    ok("... và KHÔNG tự bịa thành min (min không phải -14.26)", r.get("cao_do_thap_nhat_m") != -14.26)
    # THU LẠI mốc THẬT dạng cách +/±: audit bác tiền đề 'cao độ luôn dính liền'
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("mặt bằng cốt + 7.690", "B"),
                                          _txt("sàn mái + 8.500", "C"), _txt("CÈT + 9.800", "D")]))
    ok("mốc THẬT dạng cách '+ 7.690'/'+ 8.500'/'+ 9.800' THU LẠI vào min/max (max=9.8)",
       {7.69, 8.5, 9.8} <= set(r["tat_ca_cao_do_m"]) and r["cao_do_cao_nhat_m"] == 9.8, r["tat_ca_cao_do_m"])
    # CHỐNG QUÁ TAY: inline dấu DÍNH LIỀN vẫn phải đọc được (recall id135)
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("±0.000", "A"), _txt("CỐT NỀN HOÀN THIỆN -2.700 (mặt cắt)", "B", "Net Text")]))
    ok("inline dấu DÍNH LIỀN '-2.700' VẪN vào min/max (không cắt nhầm recall)",
       -2.7 in r["tat_ca_cao_do_m"], r["tat_ca_cao_do_m"])
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("ĐÁY CỐNG -14.26 (hạ tầng)", "H1"), _txt("±0.000", "H2")]))
    ok("id135 inline '-14.26' dính liền VẪN vào min/max", r["cao_do_thap_nhat_m"] == -14.26, r["tat_ca_cao_do_m"])
    # standalone '- 14.260' (cả ô) VẪN vào min/max (không phải 'WORD - n', không mập mờ)
    r = tc.Drawing.cao_do_min_max(_Fake([_txt("- 14.260", "A"), _txt("±0.000", "B")]))
    ok("standalone '- 14.260' (cả ô) -> vào min/max (rõ ràng, không đẩy canh_bao)",
       r["cao_do_thap_nhat_m"] == -14.26 and r["thap_nhat"]["dang"] == "standalone", r.get("thap_nhat"))

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
