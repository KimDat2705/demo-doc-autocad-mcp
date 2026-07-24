# -*- coding: utf-8 -*-
"""I3-B — BOUNDS-CHECK đường kính THÉP TRÒN trên ô DK bảng thống kê (LỘ nghi_ngo, KHÔNG sửa số).
TẤT ĐỊNH, OFFLINE, KHÔNG API, KHÔNG cần corpus.
Chạy:  python tests/test_i3_bounds.py

Bối cảnh: plan I3 CŨ = NO_GO (gắn bound vào TÊN Ô 'chieu_cao' [5 nghĩa] -> FP 87.5% + số biên lọt rổ
grounding -> câu bịa 'Móng sâu 100m' lọt). I3-B là phần SỐNG SÓT: khoá vào MỘT đại lượng (đường kính thép
tròn) tại MỘT cấu trúc (ô DK qua _acc_thep) — KHÔNG chạm _norm/_FORMULAS/_rs_*.

BẤT BIẾN khoá test (chống tái sinh -22.75 + thap_nhat_dang_tin):
  - T4: hằng biên (60) + đường kính bất-khả (1600) KHÔNG LỌT rổ neo grounding (_collect_numbers).
  - T5: KHÔNG field tin-cậy/ranking (dang_tin/hop_le/do_tin_cay).
  - T2: kg/so_thanh/dai_m + tong_kg BẤT BIẾN (chỉ THÊM cờ, không sửa số, không loại hàng)."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import tools_core as TC
import mcp_bridge as B

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


class _D:
    """Drawing tối thiểu để gọi thong_ke_thep (bỏ qua lớp OLE — orthogonal, test nơi khác)."""
    def __init__(self, by, tong_kg, thep_hinh=None):
        self.thep = {"by_dk": by, "tong_kg": tong_kg, "so_dong": len(by)}
        self.thep_hinh = thep_hinh or {}
    def _gan_canh_bao_nhung(self, r): return r


def main():
    global PASS, FAIL

    print("[T1] UNIT _dk_bat_kha (dùng _to_num BARE — KHÔNG bóc Ø/d)")
    POS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 40, 50, 60, "6.5", "6,5", "4", "5", "3"]
    FLAGV = [61, 80, 160, 800, 1600, 4680, 0, -16]
    UNP = ["Ø16", "d16", "2Ø16", "16-18", "16/18", "Ø1600", "D800", ""]
    ok("POS (thép/lưới hàn hợp lệ) -> False hết", all(TC._dk_bat_kha(x) is False for x in POS),
       [x for x in POS if TC._dk_bat_kha(x)])
    ok("FLAG (bất-khả <=0 hoặc >60) -> True hết", all(TC._dk_bat_kha(x) is True for x in FLAGV),
       [x for x in FLAGV if not TC._dk_bat_kha(x)])
    ok("UNPARSE ('2Ø16' KHÔNG thành 216=FP) -> False hết", all(TC._dk_bat_kha(x) is False for x in UNP),
       [x for x in UNP if TC._dk_bat_kha(x)])
    ok("KHÔNG siết cận dưới (lưới hàn D3/D4/D5 hợp lệ)", not TC._dk_bat_kha(3) and not TC._dk_bat_kha(4))

    print("[T2] UNIT _acc_thep — gắn cờ ADDITIVE, SỐ không đổi")
    thep = {}
    TC._acc_thep(thep, {"DK": "16", "TL": "100", "SLA": "2", "DT": "12"})
    TC._acc_thep(thep, {"DK": "1600", "TL": "5", "SLA": "1", "DT": "3"})
    ok("Ø1600 -> nghi_dk=True", thep["Ø1600"].get("nghi_dk") is True)
    ok("Ø16 -> KHÔNG cờ", "nghi_dk" not in thep["Ø16"])
    ok("kg/so_thanh/dai_m GIỮ NGUYÊN (không sửa số)",
       thep["Ø16"]["kg"] == 100.0 and thep["Ø16"]["so_thanh"] == 2 and thep["Ø1600"]["kg"] == 5.0)
    tong = round(sum(v["kg"] for v in thep.values()), 1)
    ok("tong_kg BẤT BIẾN (hàng nghi VẪN cộng)", tong == 105.0)
    # ô DK rỗng -> không cờ oan
    thep2 = {}
    TC._acc_thep(thep2, {"DK": "", "TL": "9"})
    ok("DK rỗng ('Ø?') -> KHÔNG cờ", "nghi_dk" not in thep2["Ø?"])

    print("[T3] INTEGRATION thong_ke_thep — nhánh TỔNG")
    d = _D({"Ø16": {"so_thanh": 2, "dai_m": 12.0, "kg": 100.0, "rows": 1},
            "Ø1600": {"so_thanh": 1, "dai_m": 3.0, "kg": 5.0, "rows": 1, "nghi_dk": True}}, 105.0)
    res = TC.Drawing.thong_ke_thep(d)
    ok("co_nghi_ngo_duong_kinh=True", res.get("co_nghi_ngo_duong_kinh") is True)
    ok("theo['Ø1600'].nghi_ngo=True", res["theo_duong_kinh"]["Ø1600"].get("nghi_ngo") is True)
    ok("theo['Ø16'] KHÔNG nghi_ngo", "nghi_ngo" not in res["theo_duong_kinh"]["Ø16"])
    ok("⚠ trong ghi_chu", "⚠" in res["ghi_chu"])
    ok("tong_khoi_luong_kg giữ 105.0", res["tong_khoi_luong_kg"] == 105.0)
    # file CHỈ-THƯỜNG -> KHÔNG cờ (chống hồi quy output cũ)
    dclean = _D({"Ø16": {"so_thanh": 2, "dai_m": 12.0, "kg": 100.0, "rows": 1}}, 100.0)
    resc = TC.Drawing.thong_ke_thep(dclean)
    ok("file sạch -> KHÔNG co_nghi_ngo_duong_kinh + không cờ theo cỡ",
       "co_nghi_ngo_duong_kinh" not in resc and "nghi_ngo" not in resc["theo_duong_kinh"]["Ø16"])

    print("[T4] KHOÁ KHÔNG-LỌT-GROUNDING (chống tái sinh -22.75) — GATE")
    nums = B._collect_numbers(res)
    ok("hằng biên 60 ∉ rổ neo grounding", 60 not in nums, sorted(nums))
    ok("đường kính bất-khả 1600 ∉ rổ neo (chỉ ở KEY 'Ø1600')", 1600 not in nums, sorted(nums))
    ok("prose ghi_chu I3-B KHÔNG chứa chữ số", "⚠" in res["ghi_chu"] and
       not any(c.isdigit() for c in res["ghi_chu"].split("⚠", 1)[1]))
    ok("cờ là BOOLEAN (không phải int) -> _collect_numbers bỏ",
       res["co_nghi_ngo_duong_kinh"] is True and res["theo_duong_kinh"]["Ø1600"]["nghi_ngo"] is True)

    print("[T5] KHOÁ CHỐNG NHÃN TIN-CẬY (chống thap_nhat_dang_tin)")
    import json as _j
    blob = _j.dumps(res, ensure_ascii=False)
    ok("KHÔNG field dang_tin/hop_le/do_tin_cay/ranking",
       all(w not in blob for w in ("dang_tin", "hop_le", "do_tin_cay", "xep_hang", "ranking")))

    print("[T6] HỎI-1-CỠ")
    d2 = _D({"Ø16": {"so_thanh": 2, "dai_m": 12.0, "kg": 100.0, "rows": 1},
             "Ø1600": {"so_thanh": 1, "dai_m": 3.0, "kg": 5.0, "rows": 1, "nghi_dk": True}}, 105.0)
    r_ok = TC.Drawing.thong_ke_thep(d2, duong_kinh="16")
    ok("hỏi Ø16 (hợp lệ) -> KHÔNG nghi_ngo_duong_kinh", "nghi_ngo_duong_kinh" not in r_ok and r_ok["khoi_luong_kg"] == 100.0)
    r_bad = TC.Drawing.thong_ke_thep(d2, duong_kinh="1600")
    ok("hỏi Ø1600 (bất-khả, có trong bảng) -> nghi_ngo_duong_kinh=True + số kg giữ",
       r_bad.get("nghi_ngo_duong_kinh") is True and r_bad["khoi_luong_kg"] == 5.0)

    print("[T7] ĐỐI KHÁNG — không âm thầm loại hàng nghi, không FP tiền tố")
    # hàng nghi VẪN nằm trong theo_duong_kinh (không bị loại) + vẫn cộng tổng
    ok("hàng nghi Ø1600 VẪN có trong theo_duong_kinh (không loại)", "Ø1600" in res["theo_duong_kinh"])
    # ô DK ghi '2Ø16' (dính callout) -> _to_num None -> KHÔNG cờ oan
    thep3 = {}
    TC._acc_thep(thep3, {"DK": "2Ø16", "TL": "50"})
    key3 = list(thep3.keys())[0]
    ok("DK '2Ø16' -> KHÔNG cờ oan (parser BARE)", "nghi_dk" not in thep3[key3])

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
