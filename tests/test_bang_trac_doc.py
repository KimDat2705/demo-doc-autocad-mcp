# -*- coding: utf-8 -*-
"""KHOÁ tool #36 `doc_bang_trac_doc` — đọc bảng trắc dọc (ghép NHÃN↔GIÁ TRỊ theo VỊ TRÍ).
Chạy:  python tests/test_bang_trac_doc.py      (offline, KHÔNG tốn API)

Nền: lát 0 (mục 4) quét 142 file -> 4 file kích hoạt, TẤT CẢ là trắc dọc thật; 0 file kiến
trúc/kết cấu/hạ tầng; đọc tay 104 lượt nhãn = 9 nhãn duy nhất, 0 rác; 520 giá trị, 0 SỐ ÂM.

Nhóm ca:
  [D] PHÂN BIỆT ĐƯỢC — phải ĐỎ nếu gỡ tool/gate (ghép đúng trên file đích).
  [S] SELECTIVITY — file kiến trúc/kết cấu/hạ tầng phải IM (co_bang=False).
  [N] RỔ NEO — chỉ giá trị ĐỌC ĐƯỢC vào rổ; metadata vị-trí/đếm KHÔNG được vào.
  [G] GATE — khoá từng ngưỡng ĐO ĐƯỢC; ai đổi phải đo lại.
  [E] ĐỐI CHỨNG chống-tautology + giới hạn đã biết.
"""
import os
import sys
import io
import copy

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from tools_core import Drawing               # noqa: E402
import mcp_bridge as B                       # noqa: E402

PASS = FAIL = SKIP = 0

# File đích của lát 0. Nằm ngoài repo (bộ đối tác) -> thiếu thì SKIP, KHÔNG fail oan.
F1 = r"D:\Dat-Antigravity\_f1_check\dxf\DongLac\10. Cat doc cong D600.dxf"
F2 = r"D:\Dat-Antigravity\_f1_check\dxf\GD2\2. CN duong GT GD2 chinh tuyen (Ha cong).dxf"
KT = os.path.join(ROOT, "_khao_sat", "_dxf", "BV+DT MN Gia Loc", "1. Kien truc MN Gia Loc.dxf")
KC = os.path.join(ROOT, "_khao_sat", "_dxf", "BV+DT MN Gia Loc", "2. KetCau MN GiaLoc.dxf")


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def bo_qua(name, ly_do):
    global SKIP
    SKIP += 1
    print("  [SKIP] %s  (%s)" % (name, ly_do))


def _nap(p):
    return Drawing(p) if os.path.isfile(p) else None


def main():
    print("[#36] doc_bang_trac_doc — ghép nhãn↔giá trị theo VỊ TRÍ")

    # ══ [D] PHÂN BIỆT ĐƯỢC ═══════════════════════════════════════════════════════════════
    print("\n-- [D] ghép đúng trên bảng trắc dọc thật --")
    d1 = _nap(F1)
    if d1 is None:
        bo_qua("D1-D4: cần file đích của lát 0", F1)
    else:
        r = d1.doc_bang_trac_doc()
        ok("D1: nhận ra bảng trắc dọc (co_bang=True)", r.get("co_bang") is True, r.get("ghi_chu", "")[:60])
        nhan = [h["nhan"] for b in r.get("blocks", []) for h in b["hang"]]
        ok("D2: đọc được hàng 'cao độ đáy cống' — thứ mà cao_do_min_max MÙ (ô ghi KHÔNG DẤU)",
           any("đáy cống" in (n or "").lower() for n in nhan), nhan[:4])
        ok("D3: mỗi hàng có giá trị + handle truy nguồn (đọc-và-trích)",
           all(h["gia_tri"] and all(g.get("handle") for g in h["gia_tri"])
               for b in r.get("blocks", []) for h in b["hang"]))
        # đối chứng: cao_do_min_max VẪN mù ở đúng file này -> chứng minh tool #36 mở đường MỚI
        cd = d1.cao_do_min_max()
        ok("D4: [đối chứng] cao_do_min_max VẪN không đọc được file này (tool #36 mở đường mới, "
           "KHÔNG phải làm lại việc đã có)", cd.get("co_cao_do") is False, cd.get("so_marker"))
        rl = d1.doc_bang_trac_doc(nhan_chua="đáy cống")
        nl = [h["nhan"] for b in rl.get("blocks", []) for h in b["hang"]]
        ok("D5: lọc nhan_chua chỉ trả hàng khớp (1 lượt gọi = 1 câu hỏi, không dump cả bảng)",
           bool(nl) and all("đáy cống" in (n or "").lower() for n in nl), nl[:3])

    # ══ [S] SELECTIVITY ══════════════════════════════════════════════════════════════════
    print("\n-- [S] file KHÔNG có bảng trắc dọc phải IM (chống ghép bừa) --")
    for p, ten in ((KT, "kiến trúc"), (KC, "kết cấu")):
        d = _nap(p)
        if d is None:
            bo_qua("S: %s" % ten, p)
            continue
        r = d.doc_bang_trac_doc()
        ok("S: file %s -> co_bang=False (lát 0: detector lỏng ghép bừa bảng MẪU TÔ AutoCAD "
           "'ansi31'->[500,300] và tên dầm)" % ten, r.get("co_bang") is False,
           str(r.get("_vitri")))

    # ══ [N] RỔ NEO ═══════════════════════════════════════════════════════════════════════
    print("\n-- [N] rổ neo: CHỈ giá trị đọc được, KHÔNG metadata --")
    if d1 is None:
        bo_qua("N1-N5: cần file đích", F1)
    else:
        r = d1.doc_bang_trac_doc()
        sach = B._collect_numbers(B._strip_neo(r))
        that = set()
        for b in r["blocks"]:
            for h in b["hang"]:
                for g in h["gia_tri"]:
                    try:
                        that.add(float(str(g["so"]).replace(",", ".")))
                    except Exception:
                        pass
        ok("N1: MỌI giá trị đọc được VẪN vào rổ neo (loại cả tool khỏi rổ đã đo ra GIẾT câu "
           "đúng 2/2 file — đúng lớp lỗi A3)", that and that <= sach, sorted(that - sach)[:5])
        ok("N2: rổ neo KHÔNG có số lạ ngoài giá trị đọc được (4 rò rỉ đã bịt: so_block/"
           "tong_gia_tri ngoài _vitri · ví dụ số trong ghi_chu · khoá 'nhan_handle' không được "
           "_strip_handle nhận · tên cảnh báo 'bo_1_hang...' mang chữ số)",
           not (sach - that), sorted(sach - that)[:8])
        # phân biệt được: số đánh dấu trong _vitri phải bị loại, ngoài _vitri phải còn
        g = copy.deepcopy(r)
        g["_vitri"]["so_block"] = 987654.0
        g["blocks"][0]["_vitri"]["buoc_hang"] = 876543.0
        sau = B._collect_numbers(B._strip_neo(g))
        ok("N3: số nằm trong '_vitri' BỊ LOẠI khỏi rổ (toạ độ/số đếm không được làm bằng chứng)",
           987654.0 not in sau and 876543.0 not in sau)
        g2 = copy.deepcopy(r)
        g2["so_dat_ngoai_vitri"] = 555111.0
        ok("N4: [đối chứng] số đặt NGOÀI '_vitri' vẫn vào rổ -> ca N3 phân biệt được, không tautology",
           555111.0 in B._collect_numbers(B._strip_neo(g2)))
        ok("N5: ghi_chu KHÔNG chứa chữ số (mọi chuỗi trong result đều bị _collect_numbers quét; "
           "một con số nêu làm VÍ DỤ sẽ thành bằng chứng bảo lãnh câu bịa)",
           not B._collect_numbers({"x": r.get("ghi_chu", "")}),
           sorted(B._collect_numbers({"x": r.get("ghi_chu", "")})))
        r0 = _nap(KT).doc_bang_trac_doc() if _nap(KT) else None
        if r0:
            ok("N5b: ghi_chu nhánh co_bang=False cũng 0 chữ số",
               not B._collect_numbers({"x": r0.get("ghi_chu", "")}))
        am = [g["so"] for b in r["blocks"] for h in b["hang"] for g in h["gia_tri"]
              if str(g["so"]).strip().startswith("-")]
        ok("N6: 0 SỐ ÂM trong kết quả (lát 0 đo 520 giá trị/4 file: 0 âm) -> tool này KHÔNG mở "
           "kênh bịa cao độ âm kiểu id135", not am, am[:5])

    # ══ [R] RED-TEAM — 5 lỗi bản vá tự đẻ ra, mỗi ca khoá đúng một lỗ ════════════════════
    # Nguồn: wf_cd35e271 (4 góc tấn công tự chạy engine thật + 1 vòng thẩm định).
    # ⚠ 23 ca ở trên KHÔNG bắt được lỗ nào trong số này — đó là lý do phải red-team riêng.
    print("\n-- [R] khoá 5 lỗ do red-team tìm ra --")
    if d1 is None:
        bo_qua("R1-R6: cần file đích", F1)
    else:
        r = d1.doc_bang_trac_doc(nhan_chua="đáy cống")
        ok("R1: 'loc_nhan' nằm TRONG '_vitri' — tham số nhan_chua là CHUỖI DO MODEL TỰ CHỌN, "
           "để ngoài thì nhan_chua='-600' bơm -600.0 vào rổ và lật 2 câu bịa cao-độ-âm từ CHẶN "
           "sang LỌT (đối chứng '600' không bơm gì)",
           "loc_nhan" not in r and "loc_nhan" in (r.get("_vitri") or {}))
        # rổ của MỖI lượt phải ⊆ giá trị đọc được CỦA CHÍNH LƯỢT ĐÓ (không so với lượt khác:
        # lượt không-lọc bị cap che nên thiếu giá trị thật -> so chéo sẽ báo động giả)
        for kw in (None, "đáy cống", "-600", "1.7"):
            rk = d1.doc_bang_trac_doc(nhan_chua=kw)
            ro = B._collect_numbers(B._strip_neo(rk))
            that = set()
            for b in rk.get("blocks", []):
                for h in b["hang"]:
                    for g in h["gia_tri"]:
                        v = Drawing._btd_num(g["so"])
                        if v is not None:
                            that.add(v)
            ok("R2: rổ neo lượt lọc %-10r ⊆ giá trị ĐỌC ĐƯỢC của chính lượt đó" % (kw,),
               ro <= that, sorted(ro - that)[:5])
        # min/max BẤT BIẾN theo gioi_han
        vals = []
        for g in (6, 12, 17, 18, 60):
            rg = d1.doc_bang_trac_doc(nhan_chua="đầu cọc", gioi_han=g)
            for b in rg.get("blocks", []):
                for h in b["hang"]:
                    vals.append(((h["nho_nhat"] or {}).get("so"), g))
                    break
                break
        ok("R3: nho_nhat BẤT BIẾN với mọi gioi_han — bản đầu tính min/max trên tập ĐÃ CẮT nên "
           "gioi_han=12 báo 2.930 trong khi thật là 2.710 (SAI 0,22m), KHÔNG cảnh báo, và số sai "
           "đó nằm TRONG rổ neo nên _guard_text không bắt được (lớp SAI-TỰ-TIN I3-U L1)",
           len(set(v for v, _ in vals)) == 1, vals)
        r6 = d1.doc_bang_trac_doc(nhan_chua="đầu cọc", gioi_han=6)
        ok("R4: cắt bớt PHẢI LỘ — cờ khong_day_du + cảnh báo (bản đầu `break` CÂM, giấu cả block "
           "chứa đúng giá trị mà docstring tool nêu làm lý do tồn tại)",
           r6.get("khong_day_du") is True
           and any("cat" in c for b in r6.get("blocks", []) for c in b["canh_bao"]))
        ok("R5: ghi_chu khi CHƯA ĐẦY ĐỦ vẫn 0 chữ số (câu cảnh báo thêm không được mang số)",
           not B._collect_numbers({"x": r6.get("ghi_chu", "")}),
           sorted(B._collect_numbers({"x": r6.get("ghi_chu", "")})))
        ok("R6: mỗi hàng có cờ co_chi_thi_dang_ngo (nhãn là chữ NGUYÊN VĂN từ bản vẽ mà tool tuyên "
           "bố có thẩm quyền ngữ nghĩa — phải lộ chỉ thị giả dạng dữ liệu, khuôn tool #34/#35)",
           all("co_chi_thi_dang_ngo" in h for b in r.get("blocks", []) for h in b["hang"]))
    ok("R7: _strip_handle lọc theo TÊN KHOÁ, không phải danh sách cứng — danh sách cứng đã hỏng "
       "2 lần IM LẶNG: 'handle_khong_khop' (giá trị là chuỗi TUỲ Ý do model cấp qua inputs_bo_sung: "
       "'-13.7' -> câu id135 từ CHẶN sang LỌT) và 'nhan_handle'",
       all(B._la_khoa_handle(k) for k in ("handle", "nhan_handle", "handle_khong_khop",
                                          "qty_handle", "anchor_handle", "handles")))
    ok("R7b: [đối chứng] khoá thường KHÔNG bị nhận nhầm là handle (ca R7 phân biệt được)",
       not any(B._la_khoa_handle(k) for k in ("so_hang", "nhan", "gia_tri", "buoc_hang")))
    ok("R8: _btd_num chuẩn hoá dấu trừ Unicode (U+2212 '−') — _BTD_SO_RE nhận nó nhưng bản đầu "
       "float() ném -> ô '−1.740' vừa lệch G9 vừa mất khỏi min/max",
       Drawing._btd_num("−1.740") == -1.74 and Drawing._btd_num("-1.740") == -1.74,
       Drawing._btd_num("−1.740"))

    # ══ [G] GATE — khoá ngưỡng ĐO ĐƯỢC ═══════════════════════════════════════════════════
    print("\n-- [G] ngưỡng gate: là SỐ ĐO, đổi thì phải đo lại --")
    ok("G1: mật độ >=12 (đo lát 0: nhóm trắc dọc min=15 median=18 · nhóm nhiễu median=2 p75=2; "
       "nâng lên 18 thì MẤT 2/5 block đích)", Drawing._BTD_MATDO == 12, Drawing._BTD_MATDO)
    ok("G2: cùng-bậc-độ-lớn <=10x ở MỨC HÀNG (loại ghi chú giả dạng bảng "
       "'- phía trong trát vữa xi măng 75#' -> [4,5,1,150,200,8150,200])",
       Drawing._BTD_BAC == 10.0, Drawing._BTD_BAC)
    ok("G3: band ghép cùng hàng = 0.45*p (plateau đo được 0.35-0.60, 828/828 đúng)",
       Drawing._BTD_BAND_P == 0.45, Drawing._BTD_BAND_P)
    ok("G4: cap tổng <=60 XUYÊN block (chỉ cap mỗi block thì 21 block trả 294 số)",
       Drawing._BTD_CAP_TONG == 60, Drawing._BTD_CAP_TONG)
    src = io.open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read()
    ok("G5: mọi ngưỡng THÍCH NGHI theo h/p — KHÔNG có hằng số theo đơn vị bản vẽ trong _btd_*",
       "_BTD_P_H" in src and "_BTD_QX_H" in src)
    ok("G6: ⛔ gate 'thẳng hàng theo cột' KHÔNG được thêm lại — lát 0 đo: rác thẳng hàng HOÀN "
       "HẢO 1.000 (bảng mẫu tô) còn bảng trắc dọc THẬT chỉ 0.806; quét 0.50-0.90 không có "
       "ngưỡng nào tách được", "thang_hang" not in src.split("def doc_bang_trac_doc")[1][:6000])

    # ══ [E] ĐỐI CHỨNG + GIỚI HẠN ═════════════════════════════════════════════════════════
    print("\n-- [E] đối chứng chống-tautology --")
    d2 = _nap(F2)
    if d2 is None:
        bo_qua("E1: cần file đích thứ hai", F2)
    else:
        r2 = d2.doc_bang_trac_doc()
        ok("E1: tool CÓ THỂ trả True trên file KHÁC (không phải chỉ thuộc lòng 1 file)",
           r2.get("co_bang") is True)
    ok("E2: tool CÓ THỂ trả False (không phải luôn bắn)",
       (_nap(KC).doc_bang_trac_doc().get("co_bang") is False) if _nap(KC) else True)
    if d1 is not None:
        rz = d1.doc_bang_trac_doc(nhan_chua="chuoi_khong_bao_gio_co_trong_ban_ve_xyz")
        ok("E3: lọc không khớp -> co_bang=False + ghi_chu, KHÔNG bịa hàng rỗng",
           rz.get("co_bang") is False and bool(rz.get("ghi_chu")))

    print("\n%d PASS / %d FAIL%s" % (PASS, FAIL, (" / %d SKIP" % SKIP) if SKIP else ""))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
