# -*- coding: utf-8 -*-
"""ĐO OFFLINE — nhánh ×1000 của `_is_grounded` thật sự BẮN bao nhiêu?  (KHÔNG gọi API)

Chạy:
    cd demo_mcp_autocad
    python tests/do_x1000_pham_vi.py                       # 3 lượt mặc định (run05, run06, run07)
    python tests/do_x1000_pham_vi.py run05 run06 run07     # nêu tên lượt tường minh

Trả lời:
  (a) trong 594 câu trả lời đã lưu, bao nhiêu câu CÓ khẳng định ĐO-LƯỜNG (`_answer_numbers` -> do_luong ≠ ∅)
  (b) phân bố ĐỘ LỚN của các số đó — dải "mm điển hình" (700..10000) vs dải "m điển hình" (0..50),
      và tỉ lệ số nằm trong VÙNG BẮC CẦU của nhánh ×1000
  (c/d) quần thể ĐỦ ĐIỀU KIỆN lật GIỮ->REFUSE nếu bỏ ×1000 (chặn TRÊN — phần còn lại cần rổ neo THẬT,
      xem `do_x1000_dung_lai_neo.py`)

⚠ MỌI phép đo ở đây dùng CHÍNH hàm của sản phẩm (`mcp_bridge._answer_numbers` / `_is_grounded`),
  không viết lại regex. Đọc `harness/QUY_TRINH_DO_AB.md` trước khi sửa file này.
"""
import os, re, io, sys, json, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, GOC)

if (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "") != "utf8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

import mcp_bridge

RUNS = os.path.join(HERE, "battery_runs")

# ---- dải khảo sát (khai báo TRƯỚC khi nhìn số liệu) --------------------------------
MM_LO, MM_HI = 700.0, 10000.0     # "mm điển hình" — bề rộng/chiều cao/khẩu độ cấu kiện viết bằng mm
M_LO,  M_HI  = 0.0,   50.0        # "m điển hình"  — kích thước/cao độ viết bằng m


def _code_hash():
    h = hashlib.sha256()
    for ten in ("mcp_bridge.py", "tools_core.py", "mcp_server.py", "kienthuc.py"):
        p = os.path.join(GOC, ten)
        h.update(open(p, "rb").read() if os.path.isfile(p) else b"")
    return h.hexdigest()


def nap(ten):
    p = os.path.join(RUNS, ten + ".jsonl")
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def do_luong_set(text):
    """Bộ GIÁ TRỊ đo-lường riêng biệt của một câu trả lời (khử trùng lặp — `_answer_numbers`
    trả LIST có lặp vì 1 số khớp cả _UNIT_NUM_RE lẫn _DECIMAL_RE)."""
    return set(mcp_bridge._answer_numbers(text or "")[1])


def tat_ca_set(text):
    return set(mcp_bridge._answer_numbers(text or "")[0])


def trong(x, lo, hi):
    return lo <= abs(x) <= hi


# ==================================================================================
# PHẦN 0 — ĐỊNH DANH + ĐỐI CHỨNG ÂM (bắt buộc: chứng minh phép đo CÓ THỂ ra số khác)
# ==================================================================================
def phan_0(ten_luot):
    print("=" * 88)
    print("PHẦN 0 — ĐỊNH DANH CÂY MÃ ĐANG CHẠY")
    print("=" * 88)
    print("mcp_bridge.__file__ = %s" % os.path.abspath(mcp_bridge.__file__))
    ch = _code_hash()
    print("code_hash8 (cây hiện tại) = %s" % ch[:8])
    for t in ten_luot:
        mp = os.path.join(RUNS, "_meta", t + ".meta.json")
        dd = json.load(open(mp, encoding="utf-8"))["dinh_danh"]
        print("  %s: model=%-22s code_hash8=%s  %s" % (
            t, dd["model"], dd["code_hash"][:8],
            "TRÙNG cây hiện tại" if dd["code_hash"][:8] == ch[:8] else "KHÁC cây hiện tại"))
    print()

    print("=" * 88)
    print("ĐỐI CHỨNG ÂM — phép đo có phản ứng thật không?")
    print("=" * 88)
    ok = True

    # ĐC-1: hai câu từ chối chuẩn của hệ -> KHÔNG có khẳng định đo-lường
    for nhan, s in (("REFUSE_MESSAGE", mcp_bridge.REFUSE_MESSAGE),
                    ("KHONG_TRA_DUOC", mcp_bridge.KHONG_TRA_DUOC),
                    ("câu thuần chữ", "Bản vẽ này là hồ sơ kiến trúc, gồm mặt bằng và mặt cắt.")):
        d = do_luong_set(s)
        print("  ĐC-1 %-16s -> do_luong=%s  %s" % (nhan, sorted(d), "ĐẠT" if not d else "!!! HỎNG"))
        ok &= (not d)

    # ĐC-2: câu CÓ đơn vị -> PHẢI bắt (nếu không bắt thì bộ trích chết, mọi số dưới đều là 0 giả)
    for s, cho in (("Dầm rộng 220 mm.", 220.0), ("Cao độ đáy đài -13,7 m.", -13.7),
                   ("Diện tích sàn 1740.4 m2.", 1740.4)):
        d = do_luong_set(s)
        print("  ĐC-2 %-28s -> do_luong=%s  %s" % (s, sorted(d), "ĐẠT" if cho in d else "!!! HỎNG"))
        ok &= (cho in d)

    # ĐC-3: bộ chia dải phải phân biệt được (không phải hằng số)
    mau = [0.22, 3.6, 220.0, 5000.0, 62900.0]
    got = [trong(x, MM_LO, MM_HI) for x in mau]
    cho = [False, False, False, True, False]
    print("  ĐC-3 chia dải mm trên mẫu %s -> %s  %s" % (mau, got, "ĐẠT" if got == cho else "!!! HỎNG"))
    ok &= (got == cho)

    print("  => ĐỐI CHỨNG ÂM TĨNH: %s" % ("ĐẠT" if ok else "HỎNG — DỪNG"))
    print()
    return ok


# ==================================================================================
# PHẦN A — (a) bao nhiêu câu chứa khẳng định ĐO-LƯỜNG
# ==================================================================================
def phan_a(recs):
    print("=" * 88)
    print("PHẦN A — (a) BAO NHIÊU CÂU CÓ KHẲNG ĐỊNH ĐO-LƯỜNG")
    print("=" * 88)
    tong = len(recs)
    hop_le = [r for r in recs if r.get("hop_le")]
    co_truoc_guard = [r for r in hop_le if isinstance(r.get("answer_truoc_guard"), str)]
    print("Tổng dòng                                  : %d" % tong)
    print("  hợp lệ (có answer_goc = qua đường thật)  : %d" % len(hop_le))
    print("  có answer_truoc_guard (đầu vào của guard): %d   <-- MẪU SỐ CHÍNH" % len(co_truoc_guard))

    n_do_truoc = sum(1 for r in co_truoc_guard if do_luong_set(r["answer_truoc_guard"]))
    n_do_sau = sum(1 for r in co_truoc_guard if do_luong_set(r.get("answer") or ""))
    print()
    print("Câu CÓ do_luong ≠ ∅ (TRƯỚC guard, = thứ guard nhìn thấy): %d/%d = %.1f%%"
          % (n_do_truoc, len(co_truoc_guard), 100.0 * n_do_truoc / max(1, len(co_truoc_guard))))
    print("Câu CÓ do_luong ≠ ∅ (SAU guard, = thứ người dùng đọc)   : %d/%d = %.1f%%"
          % (n_do_sau, len(co_truoc_guard), 100.0 * n_do_sau / max(1, len(co_truoc_guard))))

    # tách theo lượt/model
    print()
    print("  Theo lượt:")
    theo = collections.defaultdict(lambda: [0, 0])
    for r in co_truoc_guard:
        k = "%s / luot%02d" % (r.get("model"), r.get("luot") or 0)
        theo[k][1] += 1
        if do_luong_set(r["answer_truoc_guard"]):
            theo[k][0] += 1
    for k in sorted(theo):
        a, b = theo[k]
        print("    %-32s %3d/%3d = %.1f%%" % (k, a, b, 100.0 * a / max(1, b)))

    # ---- ĐỐI CHỨNG ÂM ĐỘNG (chạy trên CHÍNH dữ liệu này) ----
    print()
    print("  ĐỐI CHỨNG ÂM ĐỘNG (phá dữ liệu -> số phải đổi):")
    khong_chu_so = [r for r in co_truoc_guard if not any(c.isdigit() for c in r["answer_truoc_guard"])]
    xau = sum(1 for r in khong_chu_so if do_luong_set(r["answer_truoc_guard"]))
    print("    ĐC-4 dòng KHÔNG có chữ số nào: %d dòng, trong đó có do_luong = %d  %s"
          % (len(khong_chu_so), xau, "ĐẠT" if xau == 0 else "!!! HỎNG"))
    bo_so = sum(1 for r in co_truoc_guard
                if do_luong_set(re.sub(r"\d", "", r["answer_truoc_guard"])))
    print("    ĐC-5 XOÁ mọi chữ số khỏi 594 câu -> số câu có do_luong = %d  %s"
          % (bo_so, "ĐẠT (không phải hằng số)" if bo_so == 0 else "!!! HỎNG"))
    them = sum(1 for r in co_truoc_guard
               if do_luong_set(r["answer_truoc_guard"] + " Chiều dài 12,5 m."))
    print("    ĐC-6 NỐI ' 12,5 m' vào mọi câu -> số câu có do_luong = %d/%d  %s"
          % (them, len(co_truoc_guard), "ĐẠT" if them == len(co_truoc_guard) else "!!! HỎNG"))
    print()
    return co_truoc_guard


# ==================================================================================
# PHẦN B — (b) phân bố độ lớn + vùng bắc cầu ×1000
# ==================================================================================
def phan_b(mau):
    print("=" * 88)
    print("PHẦN B — (b) PHÂN BỐ ĐỘ LỚN CỦA SỐ ĐO-LƯỜNG")
    print("=" * 88)
    so = []          # mọi GIÁ TRỊ đo-lường riêng biệt, tính theo (câu, giá trị)
    for r in mau:
        for x in do_luong_set(r["answer_truoc_guard"]):
            so.append(x)
    n = len(so)
    print("Tổng cặp (câu, giá-trị-đo-lường riêng biệt): %d" % n)
    if not n:
        return

    bins = [("|x| < 0,7          ", lambda x: abs(x) < 0.7),
            ("0,7 ≤ |x| < 50     ", lambda x: 0.7 <= abs(x) < 50),
            ("50 ≤ |x| < 700     ", lambda x: 50 <= abs(x) < 700),
            ("700 ≤ |x| ≤ 10.000 ", lambda x: 700 <= abs(x) <= 10000),
            ("|x| > 10.000       ", lambda x: abs(x) > 10000)]
    for ten, f in bins:
        c = sum(1 for x in so if f(x))
        print("  %s : %5d = %5.1f%%" % (ten, c, 100.0 * c / n))

    n_mm = sum(1 for x in so if trong(x, MM_LO, MM_HI))
    n_m = sum(1 for x in so if trong(x, M_LO, M_HI))
    print()
    print("  Dải 'mm điển hình' [%.0f..%.0f] : %d = %.1f%%" % (MM_LO, MM_HI, n_mm, 100.0 * n_mm / n))
    print("  Dải 'm  điển hình' [%.0f..%.0f] : %d = %.1f%%" % (M_LO, M_HI, n_m, 100.0 * n_m / n))

    # VÙNG BẮC CẦU: số a trong dải mm mà a/1000 rơi vào dải m  (và ngược lại)
    bac_xuong = sum(1 for x in so if trong(x, MM_LO, MM_HI) and trong(x / 1000.0, M_LO, M_HI))
    bac_len = sum(1 for x in so if trong(x, M_LO, M_HI) and trong(x * 1000.0, MM_LO, MM_HI))
    print()
    print("  Số ở dải mm mà ÷1000 rơi vào dải m  : %d = %.1f%% tổng   (nhánh ÷1000 bắc cầu)"
          % (bac_xuong, 100.0 * bac_xuong / n))
    print("  Số ở dải m  mà ×1000 rơi vào dải mm : %d = %.1f%% tổng   (nhánh ×1000 bắc cầu)"
          % (bac_len, 100.0 * bac_len / n))
    print("  => TỔNG số nằm trong VÙNG BẮC CẦU   : %d = %.1f%% tổng"
          % (bac_xuong + bac_len, 100.0 * (bac_xuong + bac_len) / n))

    # theo CÂU: câu nào có ÍT NHẤT 1 số trong vùng bắc cầu
    c_cau = sum(1 for r in mau
                if any(trong(x, MM_LO, MM_HI) or trong(x, M_LO, M_HI)
                       for x in do_luong_set(r["answer_truoc_guard"])))
    co_do = [r for r in mau if do_luong_set(r["answer_truoc_guard"])]
    print("  Theo CÂU: %d/%d = %.1f%% câu-có-đo-lường có ≥1 số nằm trong 2 dải trên"
          % (c_cau, len(co_do), 100.0 * c_cau / max(1, len(co_do))))

    # top giá trị hay gặp
    dem = collections.Counter(so)
    print()
    print("  20 giá trị đo-lường hay gặp nhất: %s"
          % ", ".join("%g(%d)" % (v, c) for v, c in dem.most_common(20)))
    print()
    return so


# ==================================================================================
# PHẦN C — quần thể ĐỦ ĐIỀU KIỆN lật GIỮ->REFUSE nếu bỏ ×1000  (chặn TRÊN)
# ==================================================================================
def phan_c(mau):
    print("=" * 88)
    print("PHẦN C — QUẦN THỂ ĐỦ ĐIỀU KIỆN LẬT (chặn TRÊN cho câu hỏi (d))")
    print("=" * 88)
    R = mcp_bridge.REFUSE_MESSAGE
    K = mcp_bridge.KHONG_TRA_DUOC
    co_do = [r for r in mau if do_luong_set(r["answer_truoc_guard"])]
    def la_tu_choi(r):
        a = r.get("answer") or ""
        return a.startswith(R) or a.startswith(K)
    bi_tu_choi = [r for r in co_do if la_tu_choi(r)]
    giu = [r for r in co_do if not la_tu_choi(r)]
    print("Câu có do_luong ≠ ∅                       : %d" % len(co_do))
    print("  trong đó guard ĐÃ từ chối (REFUSE/KTĐ)  : %d" % len(bi_tu_choi))
    print("  trong đó ĐƯỢC GIỮ (≥1 số truy được)     : %d   <-- QUẦN THỂ CÓ THỂ LẬT" % len(giu))

    # phân rã quần thể GIỮ theo `so_do_luong_khong_neo` (đã lưu trong bản ghi)
    het_neo = sum(1 for r in giu if not (r.get("so_do_luong_khong_neo") or []))
    con_ho = len(giu) - het_neo
    print()
    print("  Trong %d câu GIỮ:" % len(giu))
    print("    · MỌI số đo-lường đều đã truy được          : %d" % het_neo)
    print("    · CÒN số đo-lường KHÔNG truy được (ANY cứu) : %d" % con_ho)
    print()
    print("  ⚠ KHÔNG suy được từ đây bao nhiêu câu sẽ LẬT khi bỏ ×1000: bản ghi CHỈ lưu SỐ LƯỢNG")
    print("    rổ neo (`ro_neo_n`), KHÔNG lưu GIÁ TRỊ -> không biết số nào khớp CHÍNH NÓ, số nào chỉ")
    print("    khớp nhờ ×1000. Xem `tests/do_x1000_dung_lai_neo.py` (dựng lại rổ neo bằng engine thật).")
    print()
    return giu


def main(argv):
    ten_luot = argv[1:] or ["run05", "run06", "run07"]
    if not phan_0(ten_luot):
        print("ĐỐI CHỨNG ÂM HỎNG -> KHÔNG công bố số nào."); return 3
    recs = []
    for t in ten_luot:
        recs += nap(t)
    mau = phan_a(recs)
    phan_b(mau)
    phan_c(mau)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
