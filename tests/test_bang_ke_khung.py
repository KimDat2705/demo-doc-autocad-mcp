# -*- coding: utf-8 -*-
"""KHOÁ tool #37 `doc_bang_ke_khung` — đọc bảng theo KHUNG NÉT + tự-chứng-minh.
Chạy:  python tests/test_bang_ke_khung.py      (offline, KHÔNG tốn API)

NGUỒN KỲ VỌNG — KHÔNG chép hành vi hiện tại (chống tautology):
  · bảng kỳ vọng từng fixture ĐÃ ĐÓNG BĂNG + reviewer người duyệt ở B1/B3
    (`_lat4/b3fix_fixtures_final.txt`, `_lat4/b1_ket_qua.jsonl`);
  · sự-thật-nền ĐỌC TAY 391 hàng/4.283 ô/5 file (`_lat4/su_that_nen_doc_tay.json`);
  · mốc hồi quy #36 (`_lat4/v_hoiquy_kq.json`).
Ca nào cũng đi kèm ĐỐI CHỨNG: một fixture bắn + một fixture KHÔNG bắn, để phép đo
chứng minh nó PHÂN BIỆT được chứ không phải luôn-đúng.

Fixture nằm TRONG repo (`tests/fixtures_khung/`, 47 file tổng hợp, không có dữ liệu khách
hàng) ⇒ nhóm [D]/[G]/[N]/[B]/[E]/[R] LUÔN CHẠY, kể cả trên cloud.
File corpus THẬT nằm ngoài repo (bộ đối tác) ⇒ nhóm [T] thiếu file thì SKIP, KHÔNG fail oan
— cùng khuôn `test_bang_trac_doc.py`.

Nhóm ca:
  [D] PHÂN BIỆT ĐƯỢC — đọc đúng ô/thứ tự/mỏ neo trên fixture đã đo.
  [G] GATE — từng vế từ chối đích danh, mỗi vế một cặp bắn/không-bắn.
  [N] RỔ NEO — prose 0 chữ số; số đếm/handle/echo KHÔNG được vào rổ; số ĐỌC ĐƯỢC thì phải vào.
  [B] NGÂN SÁCH — min/max bất biến theo gioi_han; mục lục hàng bị cắt; tham số dị dạng.
  [E] TỪ CHỐI ĐÚNG LOẠI — mỗi trạng thái một câu riêng, không phán sai về nội dung bản vẽ.
  [R] HỒI QUY — #37 là lát ADDITIVE: hàm #36 + test #36 + SYSTEM_PROMPT phải bất biến.
  [T] FILE THẬT — flagship 1.740/1.840, F5 đẳng thức, 6 hàng hồi quy #36 (SKIP nếu thiếu file).
"""
import hashlib
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
FIX = os.path.join(HERE, "fixtures_khung")
sys.path.insert(0, ROOT)
os.environ.setdefault("READFILE_MAX_MB", "300")

import tools_core as T                       # noqa: E402
from tools_core import Drawing               # noqa: E402
import mcp_bridge as B                       # noqa: E402

PASS = FAIL = SKIP = 0

# ── Mốc ĐÓNG BĂNG cho nhóm [R] (lát additive: 3 thứ này KHÔNG được đổi) ────────────────
HASH_TEST36 = "8186f9c3281687a4"                                    # tests/test_bang_trac_doc.py
HASH_HAM36 = "275f19e956e7e6e10cd2da2ff6f33b1496342e42298bf66ac313867c615f2f26"
HASH_PROMPT = "239e8b7ba707d5a0dd53c065af3397c8fcfb2c9f689a6f20d4249c09994f11c0"

# ── File corpus THẬT (ngoài repo) — thiếu thì SKIP ─────────────────────────────────────
A2 = r"D:\Dat-Antigravity\_f1_check\dxf\GD2\10. Cat doc cong D600.dxf"
F5 = r"D:\Dat-Antigravity\_f1_check\dxf\KDC\4. Thoat nuoc mua\2. TD.dxf"
HOI_QUY = r"D:\Dat-Antigravity\_lat4\v_hoiquy_kq.json"


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def bo_qua(name, ly_do):
    global SKIP
    SKIP += 1
    print("  [SKIP] %s  (%s)" % (name, ly_do))


# ── tiện ích đọc payload ──────────────────────────────────────────────────────────────
def doc(ten, **kw):
    return T.doc_bang_ke_khung(os.path.join(FIX, ten), **kw)


def hang(r):
    return [h for bg in (r.get("bang") or []) for h in (bg.get("hang") or [])]


def tu_choi(r):
    return [tc for bg in (r.get("bang") or [])
            for tc in ((bg.get("_vitri") or {}).get("hang_tu_choi") or [])]


def tim(r, nhan):
    return next((h for h in hang(r) if h["nhan"].strip().startswith(nhan)), None)


def ly_do(r, nhan):
    tc = next((t for t in tu_choi(r) if t["nhan"].strip().startswith(nhan)), None)
    return tc["ly_do"] if tc else None


def gt(h):
    return [g["so"] for g in (h.get("gia_tri") or h.get("day_cong_don") or [])]


def cap_tu_choi(ten_ban, nhan_ban, ly_do_mong, ten_doi, nhan_doi, ma):
    """Một vế gate = MỘT CẶP: fixture BẮN (từ chối đích danh) + fixture ĐỐI CHỨNG (đọc bình
    thường). Cặp này chứng minh vế PHÂN BIỆT được, không phải giết sạch."""
    rb, rd = doc(ten_ban), doc(ten_doi)
    ok("%s bắn: %r -> %s" % (ma, nhan_ban, ly_do_mong),
       ly_do(rb, nhan_ban) == ly_do_mong,
       "được %r; hàng đọc=%s" % (ly_do(rb, nhan_ban), [h["nhan"] for h in hang(rb)]))
    hd = tim(rd, nhan_doi)
    ok("%s ĐỐI CHỨNG %s: đọc bình thường, 0 từ chối" % (ma, ten_doi),
       hd is not None and not tu_choi(rd),
       "hàng=%s tu_choi=%s" % ([h["nhan"] for h in hang(rd)], [t["ly_do"] for t in tu_choi(rd)]))


def main():
    print("[#37] doc_bang_ke_khung — đọc bảng theo KHUNG NÉT")
    if not os.path.isdir(FIX):
        print("THIẾU tests/fixtures_khung/ — không chạy được"); return 1

    # ══ [D] PHÂN BIỆT ĐƯỢC ══════════════════════════════════════════════════════════
    print("\n-- [D] đọc đúng ô / thứ tự / mỏ neo (kỳ vọng đóng băng ở b3fix_fixtures_final.txt) --")
    r = doc("f1_khungnho.dxf")
    hA, hB = tim(r, "HANG A"), tim(r, "HANG B")
    ok("D1 f1: 2 hàng đọc đúng ô", hA and hB and gt(hA) == ["1", "2"] and gt(hB) == ["3", "4"],
       [h["nhan"] for h in hang(r)])
    # B3-3: khung 2..4 vạch chưa đủ bằng chứng cấu trúc bảng -> KHÔNG đọc, nhưng PHẢI để vết.
    vt = r.get("_vitri") or {}
    ok("D2 f1: khung nhỏ để VẾT bằng số đếm (khung_nho=3), KHÔNG đọc",
       (vt.get("so_dai_bo_qua") or {}).get("khung_nho") == 3, vt.get("so_dai_bo_qua"))
    s = json.dumps(r, ensure_ascii=False)
    ok("D3 f1: nội dung khung nhỏ KHÔNG lọt payload ('5.1' và 'CAO DO M' vắng)",
       "5.1" not in s and "CAO DO M" not in s)

    r = doc("s16b_thutu.dxf")      # V-F: mỏ neo align_point quyết định THỨ TỰ trong hàng
    h = tim(r, "CAO DO")
    ok("D4 s16b: dau_tien/cuoi_cung theo MỎ NEO đúng hình (9 -> 7.1)",
       h and (h["dau_tien"] or {}).get("so") == "9" and (h["cuoi_cung"] or {}).get("so") == "7.1",
       h and (h.get("dau_tien"), h.get("cuoi_cung")))
    r = doc("s16a_band.dxf")
    h = tim(r, "LY TRINH")
    ok("D5 s16a: band '41/42' KHÔNG biến mất", h and gt(h) == ["41", "42"], h and gt(h))
    r, rd = doc("s5_min_lech.dxf"), doc("s5_doi_chung.dxf")
    h, hd = tim(r, "CAO DO A"), tim(rd, "CAO DO A")
    ok("D6 s5: ô lệch căn lề vẫn vào hàng -> nho_nhat='0.5'",
       h and (h["nho_nhat"] or {}).get("so") == "0.5", h and h.get("nho_nhat"))
    ok("D7 ĐỐI CHỨNG s5_doi_chung (không căn lề): kết quả Y HỆT (vá không phá đường insert)",
       hd and gt(hd) == gt(h), (h and gt(h), hd and gt(hd)))
    # V-K: nhãn hàng TRỐNG có chữ số phải lộ vào _vitri (model biết nhãn tồn tại, không cấp neo)
    r = doc("s6_trong_so.dxf")
    tcs = [m["nhan"] for bg in r["bang"] for m in ((bg.get("_vitri") or {}).get("nhan_hang_trong_co_so") or [])]
    ok("D8 s6: nhãn hàng-trống mang chữ số lộ ở _vitri (V-K)",
       any("DCT-1" in x for x in tcs), tcs)
    # V-G: tràn mép -> cờ bật; hàng khác CÙNG FILE không bị bật oan (đối chứng nội bộ)
    r = doc("f8_tranmep_oan.dxf")
    ht, hk = tim(r, "CAO DO A"), tim(r, "HANG K")
    ok("D9 f8: hàng tràn mép bật tran_mep_khung + khong_day_du",
       ht and ht["tran_mep_khung"] is True and ht["khong_day_du"] is True, ht)
    ok("D10 f8 ĐỐI CHỨNG cùng file: hàng trong khung KHÔNG bật cờ oan",
       hk and hk["tran_mep_khung"] is False and hk["khong_day_du"] is False, hk)
    # V-F guard align_point RÁC -> quay về insert
    for ten, so in (("sap0_rac.dxf", "7.7"), ("sapx_rac.dxf", "8.8")):
        h = tim(doc(ten), "CAO DO R")
        ok("D11 %s: guard ap rác -> ô %r vẫn đọc đủ" % (ten, so), h and so in gt(h), h and gt(h))

    # ══ [G] GATE — mỗi vế MỘT CẶP bắn / không-bắn ═══════════════════════════════════
    print("\n-- [G] từ chối đích danh: mỗi vế một cặp bắn + đối chứng --")
    cap_tu_choi("s2_tron.dxf", "KHOANG CACH LE", "nghi_tron_hang_mat_vach",
                "s2c_doi_chung.dxf", "KHOANG CACH LE", "G-04a V-B trộn-hàng-mất-vạch")
    ok("G-04b s2a biến thể 2-nhãn cũng bị bắt",
       ly_do(doc("s2a_2nhan.dxf"), "KC LE") == "nghi_tron_hang_mat_vach")
    ok("G-04c s2b biến thể khe-mức cũng bị bắt",
       ly_do(doc("s2b_khe.dxf"), "KHOANG CACH LE") == "nghi_tron_hang_mat_vach")

    r1, r3 = doc("s1_1pt.dxf"), doc("s1c_3pt.dxf")
    h1, h3 = tim(r1, "KC CONG DON"), tim(r3, "KC CONG DON")
    pt1 = [c["so_phuong_trinh"] for bg in r1["bang"] for c in ((bg.get("_vitri") or {}).get("chung_minh") or [])]
    ok("G-05 gate chứng minh: 1 phương trình -> da_chung_minh=False, so_phuong_trinh=1",
       h1 and h1["da_chung_minh"] is False and pt1 == [1], (h1 and h1["da_chung_minh"], pt1))
    ok("G-05 ĐỐI CHỨNG 3 phương trình xen kẽ -> True (gate PHÂN BIỆT, không tắt claim vô điều kiện)",
       h3 and h3["da_chung_minh"] is True, h3 and h3["da_chung_minh"])
    ok("G-05b hàng trượt gate VẪN trả đủ 2 dãy (chỉ mất claim, không mất dữ liệu)",
       h1 and len(h1.get("day_cong_don") or []) >= 2 and "day_le" in h1, h1 and list(h1))

    rc, rd = doc("s17_cat_duoi.dxf"), doc("s17_doi_chung.dxf")
    hc, hdd = tim(rc, "KHOANG CACH CO"), tim(rd, "KHOANG CACH CO")
    ok("G-07 tràn mép -> tran_mep + khong_day_du + MẤT claim",
       hc and hc["tran_mep_khung"] and hc["khong_day_du"] and hc["da_chung_minh"] is False, hc)
    ok("G-07 ĐỐI CHỨNG cột cuối TRONG khung -> cờ tắt, claim giữ",
       hdd and hdd["tran_mep_khung"] is False and hdd["da_chung_minh"] is True, hdd)

    cap_tu_choi("f3b_giant_mode.dxf", "CAO DO Y", "nghi_chu_trang_tri_kho_lon",
                "f7b_2hang.dxf", "TOA DO M1", "B3-1 mode-flip chữ khổ lớn")
    ok("B3-1 ĐỐI CHỨNG f3a (không mode-flip) -> lý do KHÁC, không dán nhầm nhãn",
       ly_do(doc("f3a_giant2.dxf"), "CAO DO Y") == "hang_chu_it_o_so")

    r, rd = doc("f4_gop2bang.dxf"), doc("f4b_doichung.dxf")
    hl = tim(r, "HANG L1")
    ok("B3-2 ghép-x: hai bảng thật kề nhau TÁCH đúng (2 bảng, hàng trái không nuốt số phải)",
       len(r["bang"]) == 2 and hl and "91" not in gt(hl),
       (len(r["bang"]), hl and gt(hl)))
    ok("B3-2 ĐỐI CHỨNG f4b (khe rộng hơn) cũng 2 bảng", len(rd["bang"]) == 2)

    cap_tu_choi("s4_lap.dxf", "BUOC GIAN", "khung_nghi_luoi_truc",
                "s4c_khac.dxf", "BUOC GIAN", "V-H lưới trục (giá trị lặp hệt)")
    cap_tu_choi("f6_gachngang.dxf", "-", "nhan_lap_trong_o",
                "f6b_doichung.dxf", "-", "V-H2a nhãn-lặp (fixture f6)")
    cap_tu_choi("h2a_ban.dxf", "ONG THOAT NUOC", "nhan_lap_trong_o",
                "h2a_doi.dxf", "ONG THOAT NUOC", "V-H2a nhãn-lặp (fixture h2a)")
    cap_tu_choi("f7_percell.dxf", "TOA DO MOC", "nghi_cum_callout_roi",
                "f7b_2hang.dxf", "TOA DO M1", "V-H2b callout-rải-khối (fixture f7)")
    cap_tu_choi("h2b_ban.dxf", "KT-99", "nghi_cum_callout_roi",
                "h2b_doi1.dxf", "NEO GACH", "V-H2b callout-rải-khối (fixture h2b)")
    for ten in ("h2b_doi2.dxf", "h2b_doi3.dxf"):
        ok("V-H2b ĐỐI CHỨNG %s: hàng thật vẽ bằng block KHÔNG bị giết oan" % ten,
           not tu_choi(doc(ten)) and len(hang(doc(ten))) >= 1)
    cap_tu_choi("h2c_ban.dxf", "CHU THEP DUNG", "nhan_dung_dung",
                "h2c_doi.dxf", "CHU THEP DUNG", "V-H2c nhãn-dựng-đứng 90°")
    ok("V-H2c biến thể 270° cũng bị bắt",
       ly_do(doc("h2c_ban270.dxf"), "CHU THEP DUNG") == "nhan_dung_dung")

    # V-I dedup khung lồng
    ok("V-I s5_long: hàng trùng giữa khung lồng bị gỡ, để VẾT so_hang_trung_khung_gop",
       (doc("s5_long.dxf").get("_vitri") or {}).get("so_hang_trung_khung_gop") == 2,
       (doc("s5_long.dxf").get("_vitri") or {}).get("so_hang_trung_khung_gop"))
    ok("V-I ĐỐI CHỨNG s5c_roi (khung KHÔNG lồng): không gỡ gì",
       (doc("s5c_roi.dxf").get("_vitri") or {}).get("so_hang_trung_khung_gop") is None)

    # ⛔ KHOÁ MỘT QUYẾT ĐỊNH NO_GO: vế RATIO 'bảng cao >> bước hàng' ĐÃ BỎ (đính chính mục 1).
    #    Ai định thêm lại ngưỡng NGƯỠNG_CAO phải đọc b1c4_censu_ketluan.md trước: hàng THẬT trải
    #    ratio 2.64-46.0 ĐAN XEN hàng chế tạo 3.63-506 -> không tồn tại ngưỡng, mọi ngưỡng giết
    #    hàng thật. Ca này ĐỎ nếu ai đó lén thêm vế ratio trở lại.
    rc, rt = doc("s3_luoi_cao.dxf"), doc("s3c_thap.dxf")
    hc, ht = tim(rc, "CAO DO SAN"), tim(rt, "CAO DO SAN")
    ok("G-NOGO vế ratio ĐÃ BỎ: bảng CAO và bảng THẤP đọc GIỐNG HỆT nhau",
       hc and ht and gt(hc) == gt(ht) == ["3.60", "7.20", "10.80"],
       (hc and gt(hc), ht and gt(ht)))

    # ══ [N] RỔ NEO ═════════════════════════════════════════════════════════════════
    print("\n-- [N] kỷ luật rổ neo (đo bằng chính _strip_neo/_collect_numbers của mcp_bridge) --")
    prose = [T.GHI_CHU_DOC, T.GHI_CHU_CAT] + list(T.TU_CHOI.values()) + list(T.LY_DO_TU_CHOI.values())
    xau = [p for p in prose if any(c.isdigit() for c in p)]
    ok("G-11a prose 0 CHỮ SỐ (%d chuỗi: ghi_chu + %d nhánh từ chối + %d lý do)"
       % (len(prose), len(T.TU_CHOI), len(T.LY_DO_TU_CHOI)), not xau, xau[:2])
    # SELF-CHECK: bơm 1 chữ số vào BẢN SAO -> phép đo PHẢI thấy (chứng minh nó nhìn được lỗi)
    ok("G-11a self-check: bơm chữ số vào bản sao thì phép đo báo đỏ",
       any(c.isdigit() for c in (T.GHI_CHU_DOC + " 7")))
    dinh = [p for p in prose if any(m in p.lower() for m in B._REFUSAL_MARKERS)]
    ok("G-11b prose KHÔNG chứa cụm _REFUSAL_MARKERS (dính = _guard_text thoát sớm, bỏ kiểm cả bài)",
       not dinh, dinh[:1])

    r = doc("s1c_3pt.dxf")
    neo = B._collect_numbers(B._strip_neo(r))
    hop_phap = set()
    for h in hang(r):
        for k in ("gia_tri", "day_cong_don", "day_le"):
            for g in (h.get(k) or []):
                hop_phap |= B._collect_numbers(g.get("so"))
        for k in ("nho_nhat", "lon_nhat", "dau_tien", "cuoi_cung", "cong_don_cuoi_cung",
                  "nho_nhat_cong_don", "lon_nhat_cong_don", "nho_nhat_le", "lon_nhat_le"):
            if h.get(k):
                hop_phap |= B._collect_numbers(h[k].get("so"))
        for c in (h.get("o_chu") or []):
            hop_phap |= B._collect_numbers(c.get("chu"))
        hop_phap |= B._collect_numbers(h.get("nhan"))
    ok("N1 rổ neo ĐÓNG KÍN: ⊆ số suy từ nguyên văn ô/nhãn-ĐỌC/o_chu đã trả",
       not (neo - hop_phap), sorted(neo - hop_phap)[:6])
    # G-12 hai chiều: trong _vitri PHẢI bị loại, ngoài _vitri PHẢI vào rổ (máy đo thấy được cả hai)
    import copy
    r2 = copy.deepcopy(r)
    r2["bang"][0]["_vitri"]["moc_thu"] = 987654
    ok("G-12a số đặt TRONG _vitri bị _strip_vitri loại khỏi rổ",
       987654.0 not in B._collect_numbers(B._strip_neo(r2)))
    r3 = copy.deepcopy(r)
    r3["moc_thu_ngoai"] = 987654
    ok("G-12b ĐỐI CHỨNG: số đặt NGOÀI _vitri PHẢI vào rổ (phép đo nhìn thấy tác động)",
       987654.0 in B._collect_numbers(B._strip_neo(r3)))
    # N2: handle không được thành neo
    hs = set()
    for h in hang(r):
        hs.add(h.get("handle"))
        for g in (h.get("gia_tri") or h.get("day_cong_don") or []):
            hs.add(g.get("handle"))
    hexn = set()
    for x in hs:
        try:
            hexn.add(float(int(x, 16)))
        except Exception:
            pass
    ok("N2 handle KHÔNG lọt rổ neo", not ((hexn - hop_phap) & neo), sorted((hexn - hop_phap) & neo)[:4])

    # ══ [B] NGÂN SÁCH ══════════════════════════════════════════════════════════════
    print("\n-- [B] ngân sách: min/max bất biến, mục lục hàng bị cắt, tham số dị dạng --")
    day = {}
    rf = doc("s16a_band.dxf", gioi_han=200)
    for h in hang(rf):
        day[h["handle"]] = json.dumps([h.get("nho_nhat"), h.get("lon_nhat"),
                                       h.get("dau_tien"), h.get("cuoi_cung")], ensure_ascii=False)
    bat_bien, doi_dai = True, set()
    for gh in (1, 6, 12, 60, 200):
        rg = doc("s16a_band.dxf", gioi_han=gh)
        for h in hang(rg):
            cur = json.dumps([h.get("nho_nhat"), h.get("lon_nhat"),
                              h.get("dau_tien"), h.get("cuoi_cung")], ensure_ascii=False)
            if day.get(h["handle"]) and cur != day[h["handle"]]:
                bat_bien = False
        doi_dai.add(sum(len(h.get("gia_tri") or []) for h in hang(rg)))
    ok("G-13 min/max/dau/cuoi BẤT BIẾN với gioi_han ∈ {1,6,12,60,200} (chống lỗi R3 của #36)",
       bat_bien)
    ok("G-13 ĐỐI CHỨNG: số ô TRẢ VỀ phải ĐỔI theo gioi_han (phép đo thấy tác động ngân sách)",
       len(doi_dai) > 1, sorted(doi_dai))
    r1 = doc("s16a_band.dxf", gioi_han=1)
    ml = [m["nhan"] for bg in r1["bang"] for m in ((bg.get("_vitri") or {}).get("muc_luc_hang_chua_tra") or [])]
    ok("G-18 hàng bị cắt TRỌN vẫn để lại nhãn ở mục lục (hàng TỒN TẠI, không biến mất)",
       len(ml) >= 1 and r1.get("khong_day_du") is True, (len(ml), r1.get("khong_day_du")))
    ok("G-18b nhãn mục lục nằm trong _vitri nên KHÔNG bơm số vào rổ",
       not (B._collect_numbers(B._strip_neo({"_vitri": {"muc_luc_hang_chua_tra":
                                                        [{"nhan": "COC 987654", "handle": "1"}]}}))))
    # đính chính mục 6: gioi_han falsy -> rơi về mặc định 60, KHÔNG kẹp lên 1
    kq = {}
    for v in (0, None, "", "abc", True, -5, 2.9, 10 ** 9):
        try:
            kq[repr(v)] = ((doc("s16a_band.dxf", gioi_han=v).get("_vitri") or {})
                           .get("tham_so", {}).get("gioi_han"))
        except Exception as e:
            kq[repr(v)] = "CRASH:%s" % e
    ok("B1 gioi_han dị dạng KHÔNG crash", not any(str(v).startswith("CRASH") for v in kq.values()), kq)
    ok("B2 gioi_han falsy (0/None/'') -> mặc định %d, KHÔNG phải 1 (đính chính mục 6)" % T.CAP_TONG,
       kq["0"] == kq["None"] == kq["''"] == T.CAP_TONG, kq)
    ok("B3 gioi_han vượt trần bị kẹp về %d" % T.CAP_TRAN, kq["1000000000"] == T.CAP_TRAN, kq)

    # ══ [E] TỪ CHỐI ĐÚNG LOẠI ══════════════════════════════════════════════════════
    print("\n-- [E] mỗi trạng thái một câu riêng, không phán sai về nội dung bản vẽ --")
    r = T.doc_bang_ke_khung(os.path.join(FIX, "khong_ton_tai_xyz.dxf"))
    tt = (r.get("_vitri") or {}).get("trang_thai")
    ok("G-10 đường dẫn không tồn tại -> 'loi_mo_file' (KHÔNG phán 'lỗi cấu trúc DXF')",
       tt == "loi_mo_file", tt)
    ok("G-10b câu từ chối nói ĐÚNG loại (lỗi mở file), không kết luận về nội dung bản vẽ",
       r.get("ghi_chu") == T.TU_CHOI["loi_mo_file"])
    r = doc("s16a_band.dxf", nhan_chua="chuoi_khong_bao_gio_co_xyz")
    ok("G-09 lọc trượt -> 'loc_khong_khop', KHÔNG phải 'khung_khong_bang'",
       (r.get("_vitri") or {}).get("trang_thai") == "loc_khong_khop",
       (r.get("_vitri") or {}).get("trang_thai"))
    ok("G-09 ĐỐI CHỨNG: cùng file không lọc -> co_bang=True (file THẬT SỰ có bảng)",
       doc("s16a_band.dxf").get("co_bang") is True)
    # G-15: #37 đứng SAU cổng cỡ file của Drawing -> file quá cỡ thì Drawing không tồn tại,
    # người dùng nhận ĐÚNG câu quá-cỡ mà #36 đang dùng (chung một cổng, theo cấu trúc).
    cu = T.READFILE_MAX_MB
    try:
        T.READFILE_MAX_MB = -1
        loi_txt = ""
        try:
            Drawing(os.path.join(FIX, "s16a_band.dxf"))
        except Exception as e:
            loi_txt = str(e)
        ok("G-15 file quá cỡ bị CHẶN ở cổng Drawing (chung cổng với #36), #37 không kịp chạy",
           "quá lớn" in loi_txt, loi_txt[:70])
    finally:
        T.READFILE_MAX_MB = cu
    ok("G-15 ĐỐI CHỨNG: cỡ bình thường thì KHÔNG kích hoạt cổng",
       Drawing(os.path.join(FIX, "s16a_band.dxf")).doc_bang_ke_khung().get("co_bang") is True)

    # ══ [R] HỒI QUY — lát ADDITIVE ═════════════════════════════════════════════════
    print("\n-- [R] #37 là lát ADDITIVE: #36 + prompt phải BẤT BIẾN --")
    h36 = hashlib.sha256(io.open(os.path.join(HERE, "test_bang_trac_doc.py"), "rb").read()).hexdigest()
    ok("G-16a hash tests/test_bang_trac_doc.py không đổi", h36[:16] == HASH_TEST36, h36[:16])
    src = io.open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read()
    i = src.index("    def doc_bang_trac_doc(self")
    j = src.index("    def ", src.index("def _btd_num", i))
    hh = hashlib.sha256(src[i:j].encode("utf-8")).hexdigest()
    ok("G-16b vùng hàm #36 trong tools_core.py = 0 BYTE đổi", hh == HASH_HAM36, hh[:16])
    hp = hashlib.sha256(B.SYSTEM_PROMPT.encode("utf-8")).hexdigest()
    ok("G-16c SYSTEM_PROMPT byte-lock không đổi (đăng ký tool KHÔNG được đụng prompt)",
       hp == HASH_PROMPT, hp[:16])
    ok("G-16d #37 KHÔNG bị giấu khỏi LLM (phải nằm trong danh sách declaration)",
       "doc_bang_ke_khung" not in B._TOOL_KHONG_CHO_LLM)

    # ══ [T] FILE THẬT (SKIP nếu thiếu) ═════════════════════════════════════════════
    print("\n-- [T] file corpus THẬT: flagship + đẳng thức + hồi quy #36 --")
    if not os.path.isfile(A2):
        bo_qua("T1-T4: cần file đích A2 (ngoài repo)", A2)
    else:
        d = Drawing(A2)
        rk = d.doc_bang_ke_khung(nhan_chua="đáy kênh", gioi_han=200)
        rc = d.doc_bang_ke_khung(nhan_chua="đáy cống", gioi_han=200)
        ok("T1 FLAGSHIP: nhan_chua='đáy kênh' (Unicode SẠCH) trúng nhãn TCVN3 lỗi phông -> min=1.740",
           any((h["nho_nhat"] or {}).get("so") == "1.740" for h in hang(rk)),
           [(h["nhan"][:40], (h["nho_nhat"] or {}).get("so")) for h in hang(rk)])
        ok("T2 FLAGSHIP: nhan_chua='đáy cống' -> min=1.840 (hàng KHÁC, không lẫn)",
           any((h["nho_nhat"] or {}).get("so") == "1.840" for h in hang(rc)))
        ok("T3 ĐỐI CHỨNG chống tautology: gọi MẶC ĐỊNH không chứa '1.740' "
           "(số đến từ đường LỌC, không có sẵn trong payload)",
           "1.740" not in json.dumps(d.doc_bang_ke_khung(), ensure_ascii=False))
        # ĐỐI CHỨNG 2: mô phỏng TẮT normalizer (so bằng .lower() như proto) -> phải 0 hàng
        qs = T.quet_bang(d.doc)
        cu_n = sum(1 for bg in qs["bang"] for rr in bg["rows"]
                   if rr["tang"] in ("a", "b")
                   and "đáy kênh" in " ".join(rr["nhan"]["txt"].split()).lower())
        ok("T4 ĐỐI CHỨNG: TẮT garble-normalizer -> 0 hàng (normalizer đúng là thứ làm nên việc)",
           cu_n == 0, cu_n)

    if not os.path.isfile(F5):
        bo_qua("T5-T6: cần file đích F5 (ngoài repo)", F5)
    else:
        # ⚠ PHẢI nới CAP_TRAN mới thấy TRỌN bảng ở tầng payload: gioi_han=10**9 một mình KHÔNG
        # đủ vì tang_ket_qua kẹp về CAP_TRAN=200 (chính là hành vi ca B3 khoá). Mốc nền của
        # tiêu chí (3) đo trên bề mặt ĐẦY ĐỦ — đo trên bề mặt bị cắt sẽ ra 4 hàng/3 claim và
        # cho kết luận ngược. Đối chứng ngân sách nằm ở nhóm [B], không trộn vào đây.
        cu_cap = T.CAP_TRAN
        try:
            T.CAP_TRAN = 10 ** 9
            r = Drawing(F5).doc_bang_ke_khung(gioi_han=10 ** 9)
        finally:
            T.CAP_TRAN = cu_cap
        hb = [h for h in hang(r) if "day_cong_don" in h]
        ok("T5 F5: đủ 23 hàng hai-dãy (cấm 9-bỏ-làm-10)", len(hb) == 23, len(hb))
        ok("T5b F5: đúng 9 hàng giữ claim sau gate V-A (23 -> 9, không phải tắt claim vô điều kiện)",
           sum(1 for h in hb if h["da_chung_minh"]) == 9,
           sum(1 for h in hb if h["da_chung_minh"]))
        ok("T5c F5: 171/171 ô của hai dãy có mặt (hàng trượt gate VẪN trả đủ dữ liệu)",
           sum(len(h["day_cong_don"]) + len(h["day_le"]) for h in hb) == 171,
           sum(len(h["day_cong_don"]) + len(h["day_le"]) for h in hb))
        # kiểm ĐỘC LẬP bằng Decimal parse từ CHUỖI payload — KHÔNG tin trường bool.
        # Đếm trên CẢ 23 hàng (74 là tổng phương trình của toàn bộ hàng b; riêng 9 hàng giữ
        # claim chứa 60 — hai đại lượng KHÁC nhau, đừng lẫn).
        from decimal import Decimal
        npt = 0
        for h in hb:
            cd = [Decimal(g["so"].replace(",", ".")) for g in h["day_cong_don"]]
            le = [Decimal(g["so"].replace(",", ".")) for g in h["day_le"]]
            for k in range(min(len(cd) - 1, len(le))):
                if cd[k + 1] - cd[k] == le[k]:
                    npt += 1
        ok("T6 F5: 74/74 phương trình khớp khi kiểm ĐỘC LẬP bằng Decimal từ chuỗi payload",
           npt == 74, npt)

    if not os.path.isfile(HOI_QUY):
        bo_qua("T7: cần v_hoiquy_kq.json (mốc hồi quy #36, ngoài repo)", HOI_QUY)
    else:
        hq = json.load(io.open(HOI_QUY, encoding="utf-8"))
        import json as _j
        nguon = _j.load(io.open(r"D:\Dat-Antigravity\_lat4\su_that_nen_doc_tay.json",
                                encoding="utf-8"))["nguon"] if os.path.isfile(
            r"D:\Dat-Antigravity\_lat4\su_that_nen_doc_tay.json") else {}
        thieu = [x for x in hq["hang_dung"] if not os.path.isfile(nguon.get(x["file"], ""))]
        if thieu or not nguon:
            bo_qua("T7: thiếu file corpus cho mốc hồi quy", "%d/%d" % (len(thieu), len(hq["hang_dung"])))
        else:
            cache, sai = {}, []
            for x in hq["hang_dung"]:
                if x["file"] not in cache:
                    cache[x["file"]] = Drawing(nguon[x["file"]])
                # gọi theo ĐƯỜNG CALLER THẬT: nhan_chua trỏ đúng hàng, rồi khớp theo HANDLE.
                # ⚠ KHÔNG khớp theo CHỮ: C1 có 30 hàng TRÙNG Y HỆT nhãn 'Cao trình tự nhiên (m)'.
                rr = cache[x["file"]].doc_bang_ke_khung(nhan_chua=x["nhan"], gioi_han=200)
                h = next((y for y in hang(rr) if y["handle"] == x["handle"]), None)
                if not (h and T.to_num((h["nho_nhat"] or {}).get("so")) == x["gt_min"]
                        and T.to_num((h["lon_nhat"] or {}).get("so")) == x["gt_max"]):
                    sai.append((x["file"], x["nhan"][:30]))
            ok("T7 KHÔNG hồi quy: %d/%d hàng #36 đang đọc ĐÚNG thì #37 đọc đúng y giá trị"
               % (len(hq["hang_dung"]) - len(sai), len(hq["hang_dung"])), not sai, sai)

    print("\n%d PASS / %d FAIL%s" % (PASS, FAIL, (" / %d SKIP" % SKIP) if SKIP else ""))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
