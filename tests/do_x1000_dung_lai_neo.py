# -*- coding: utf-8 -*-
"""DỰNG LẠI RỔ NEO THẬT bằng ENGINE THẬT (OFFLINE, KHÔNG gọi API) rồi đo:
nếu BỎ nhánh ×1000 của `_is_grounded` thì bao nhiêu câu lật GIỮ -> REFUSE?

VÌ SAO PHẢI DỰNG LẠI: bản ghi battery chỉ lưu `ro_neo_n` (SỐ LƯỢNG neo), KHÔNG lưu GIÁ TRỊ.
Không có giá trị thì không phân biệt được "số khớp CHÍNH NÓ" với "số chỉ khớp nhờ ×1000".

CÁCH: mỗi bản ghi đã lưu `tool_goi = [{tool, args}, ...]` — ĐỦ để gọi lại đúng chuỗi tool đó
trên đúng bản vẽ, qua CHÍNH `MCPBridge` + `mcp_server.py` (tiến trình con, không mạng).

DỤNG CỤ TỰ KIỂM (điểm mấu chốt): bản ghi CÓ lưu `ro_neo_n`, `so_do_luong_khong_neo`,
`so_tat_ca_khong_neo` — sinh từ rổ neo THẬT lúc chạy. Rổ dựng lại phải TÁI TẠO ĐÚNG cả ba.
Bản ghi nào không tái tạo được -> LOẠI khỏi mẫu, KHÔNG đoán.

Chạy:
    cd demo_mcp_autocad
    python tests/do_x1000_dung_lai_neo.py                        # run05+06+07
    python tests/do_x1000_dung_lai_neo.py run06 --gioi-han 40    # thử nhanh
"""
import os, io, sys, json, time, hashlib, argparse, collections

HERE = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, GOC)
os.environ["READFILE_MAX_MB"] = "300"

if (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "") != "utf8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

import mcp_bridge

RUNS = os.path.join(HERE, "battery_runs")
ORDER = ["kientruc", "ketcau", "hatang"]

# Tool có GHI (log học / kho kiến thức) -> KHÔNG replay, để không bơm rác vào kho của dự án.
TOOL_KHONG_REPLAY = {"hoi_de_hoc"}

# Bản sao tuple LOẠI-TRỪ khỏi rổ neo trong `_tra_loi_ai_mot_lan`. Có cổng kiểm trôi ở `kiem_hop_dong()`.
LOAI_TRU = ("doc_bang_nhung", "phat_hien_bang_ve_net", "tra_ky_hieu", "doc_chu_trang_in")

# Thông điệp lỗi tool mà mcp_bridge thay vào khi bridge.call NÉM (M4 — cố ý SẠCH SỐ).
LOI_TOOL = {"loi": "Không chạy được công cụ này (chi tiết đã ghi ở log máy chủ)."}


def kiem_hop_dong():
    """Chặn TRÔI LỆCH giữa script đo và sản phẩm: tuple loại-trừ phải còn nguyên trong mcp_bridge.py."""
    src = open(os.path.join(GOC, "mcp_bridge.py"), encoding="utf-8").read()
    can = 'fc.name not in ("doc_bang_nhung", "phat_hien_bang_ve_net",\n' \
          '                                                                "tra_ky_hieu", "doc_chu_trang_in")'
    return can in src


def _is_grounded_khong_x1000(a, nums):
    """BẢN ĐỐI CHỨNG: y hệt `_is_grounded` nhưng CHỈ giữ nhánh khớp-chính-nó."""
    for t in nums:
        if abs(a - t) <= max(abs(t) * 0.01, 0.05):
            return True
    return False


_NGHIN_VN = None      # nạp trễ (cần `re`)


def vi_sao_can_x1000(text, pool):
    """Với câu bị LẬT: liệt kê các số ĐÃ cứu câu (chỉ khớp nhờ ×1000/÷1000) + PHÂN LOẠI nguyên nhân.

    Ba nguyên nhân KHÁC HẲN nhau về cách xử:
      · 'nghin_vn'  — số viết kiểu VN '8.024' bị `_answer_numbers` đọc thành 8,024 (BUG PARSER đã ghi sổ);
                      ×1000 đang CHE bug này. Chữa được bằng vá parser, KHÔNG cần ×1000.
      · 'm_sang_mm' — model đổi đơn vị THẬT: tool trả mét, câu trả lời viết mm (a ≈ t×1000).
      · 'mm_sang_m' — chiều ngược lại (a ≈ t÷1000).
    """
    global _NGHIN_VN
    if _NGHIN_VN is None:
        import re as _re
        _NGHIN_VN = _re.compile(r"(?<!\d)\d{1,3}\.\d{3}(?!\d)")
    co_nghin = set()
    for m in _NGHIN_VN.finditer(text or ""):
        try:
            co_nghin.add(float(m.group(0)))          # '8.024' -> 8.024 (đúng cách _to_f đọc)
        except Exception:
            pass
    tat_ca, _ = mcp_bridge._answer_numbers(text or "")
    ra = []
    for a in sorted(set(tat_ca)):
        if _is_grounded_khong_x1000(a, pool):
            continue                                  # số này tự đứng được -> không phải lý do
        if not mcp_bridge._is_grounded(a, pool):
            continue                                  # số này vốn không neo được -> không cứu ai
        moc = [t for t in pool
               if abs(a - t * 1000.0) <= max(abs(t * 1000.0) * 0.01, 0.05)
               or abs(a - t / 1000.0) <= max(abs(t / 1000.0) * 0.01, 0.05)]
        huong = "m_sang_mm" if any(abs(a - t * 1000.0) <= max(abs(t * 1000.0) * 0.01, 0.05)
                                   for t in pool) else "mm_sang_m"
        if any(abs(a - x) < 1e-9 for x in co_nghin) and huong == "m_sang_mm":
            huong = "nghin_vn"
        ra.append((a, huong, sorted(moc)[:3]))
    return ra


def quyet_dinh(text, pool, ham_neo):
    """Tái dựng phán quyết của `_guard_text` với MỘT luật neo cho trước.
    Trả 'KHONG_DUNG' (không có khẳng định đo-lường) / 'GIU' / 'REFUSE'."""
    tat_ca, do_luong = mcp_bridge._answer_numbers(text or "")
    if not do_luong:
        return "KHONG_DUNG"
    return "GIU" if any(ham_neo(a, pool) for a in tat_ca) else "REFUSE"


def nap(ten):
    p = os.path.join(RUNS, ten + ".jsonl")
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("luot", nargs="*", default=None)
    ap.add_argument("--gioi-han", type=int, default=0, help="chỉ replay N bản ghi đầu mỗi lượt (thử nhanh)")
    ap.add_argument("--khong-cache", action="store_true", help="không nhớ kết quả tool trùng (chậm, dùng đối chứng)")
    a = ap.parse_args(argv[1:])
    ten_luot = a.luot or ["run05", "run06", "run07"]

    try:
        from corpus_local import KT, KC, HT
    except Exception as e:
        print("THIẾU corpus_local.py -> không dựng lại được rổ neo: %s" % e); return 9
    FILES = {"kientruc": KT, "ketcau": KC, "hatang": HT}
    for k, p in FILES.items():
        if not os.path.isfile(p):
            print("THIẾU bản vẽ %s: %s" % (k, p)); return 9

    print("=" * 92)
    print("ĐỊNH DANH")
    print("=" * 92)
    print("mcp_bridge.__file__ = %s" % os.path.abspath(mcp_bridge.__file__))
    h = hashlib.sha256()
    for t in ("mcp_bridge.py", "tools_core.py", "mcp_server.py", "kienthuc.py"):
        h.update(open(os.path.join(GOC, t), "rb").read())
    print("code_hash8 cây hiện tại = %s" % h.hexdigest()[:8])
    print("hợp đồng tuple loại-trừ còn nguyên: %s" % ("CÓ" if kiem_hop_dong() else "KHÔNG -> DỪNG"))
    if not kiem_hop_dong():
        return 3
    print()

    recs = []
    for t in ten_luot:
        r = nap(t)
        if a.gioi_han:
            r = r[:a.gioi_han]
        recs += r
    theo_file = collections.defaultdict(list)
    for r in recs:
        theo_file[r.get("file")].append(r)

    br = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
    print("Bridge OK, %d tool (tiến trình con, KHÔNG mạng)." % len(br.tools or []))
    cache = {}
    ket = []
    t0 = time.time()
    try:
        for f in ORDER:
            if not theo_file.get(f):
                continue
            print("\n### NẠP %s: %s" % (f, os.path.basename(FILES[f])))
            br.call("nap_ban_ve", {"path": FILES[f]}, timeout=900)
            cache.clear()          # rổ cache theo TỪNG bản vẽ (đổi bản vẽ -> kết quả tool khác)
            for i, r in enumerate(theo_file[f]):
                tg = r.get("tool_goi") or []
                if any(x.get("tool") in TOOL_KHONG_REPLAY for x in tg):
                    ket.append({"r": r, "trang_thai": "BO_QUA_GHI", "pool": None}); continue
                pool = set()
                loi_replay = None
                for x in tg:
                    ten, args = x.get("tool"), x.get("args") or {}
                    if "loi" in x:                       # lúc chạy thật tool đã NÉM -> mcp_bridge thay bằng LOI_TOOL
                        res = dict(LOI_TOOL)
                    else:
                        key = (ten, json.dumps(args, sort_keys=True, ensure_ascii=False))
                        if (not a.khong_cache) and key in cache:
                            res = cache[key]
                        else:
                            try:
                                res = br.call(ten, args, timeout=300)
                            except Exception as e:
                                res = dict(LOI_TOOL); loi_replay = "%s: %s" % (type(e).__name__, e)
                            if not a.khong_cache:
                                cache[key] = res
                    if isinstance(res, dict) and ten not in LOAI_TRU:
                        pool |= mcp_bridge._collect_numbers(mcp_bridge._strip_neo(res))
                # --- TỰ KIỂM: rổ dựng lại có tái tạo đúng 3 dấu vân tay đã lưu không? ---
                txt = r.get("answer_truoc_guard") or ""
                tat_ca, do_luong = mcp_bridge._answer_numbers(txt)
                lai_do = sorted({x for x in do_luong if not mcp_bridge._is_grounded(x, pool)})
                lai_ta = sorted({x for x in tat_ca if not mcp_bridge._is_grounded(x, pool)})
                khop_n = (len(pool) == r.get("ro_neo_n"))
                khop_do = (lai_do == (r.get("so_do_luong_khong_neo") or []))
                khop_ta = (lai_ta == (r.get("so_tat_ca_khong_neo") or []))
                tt = "KHOP" if (khop_n and khop_do and khop_ta) else (
                     "LECH_N" if not khop_n else "LECH_TAP")
                ket.append({"r": r, "trang_thai": tt, "pool": pool, "loi": loi_replay,
                            "khop_n": khop_n, "khop_do": khop_do, "khop_ta": khop_ta,
                            "n_lai": len(pool), "n_luu": r.get("ro_neo_n")})
                if (i + 1) % 25 == 0:
                    print("   ... %d/%d (%.0fs)" % (i + 1, len(theo_file[f]), time.time() - t0))
    finally:
        try:
            br.close()
        except Exception:
            pass

    # ================================================================ BÁO CÁO
    print("\n" + "=" * 92)
    print("BƯỚC 1 — RỔ NEO DỰNG LẠI CÓ TRUNG THỰC KHÔNG? (tự kiểm bằng 3 dấu vân tay đã lưu)")
    print("=" * 92)
    dem = collections.Counter(k["trang_thai"] for k in ket)
    tong = len(ket)
    for k in ("KHOP", "LECH_N", "LECH_TAP", "BO_QUA_GHI"):
        print("  %-11s : %4d / %d = %5.1f%%" % (k, dem[k], tong, 100.0 * dem[k] / max(1, tong)))

    lech = [k for k in ket if k["trang_thai"] in ("LECH_N", "LECH_TAP")]
    if lech:
        tool_lech = collections.Counter()
        for k in lech:
            for x in (k["r"].get("tool_goi") or []):
                tool_lech[x.get("tool")] += 1
        print("\n  Tool hay xuất hiện trong bản ghi LỆCH (nghi nguồn phi-tất-định):")
        for t, c in tool_lech.most_common(12):
            print("     %-26s %d" % (t, c))
        print("\n  10 ca lệch đầu (n_dựng_lại vs n_đã_lưu):")
        for k in lech[:10]:
            print("     id%-4s luot%-3s n=%-5s luu=%-5s tool=%s"
                  % (k["r"].get("id"), k["r"].get("luot"), k["n_lai"], k["n_luu"],
                     [x.get("tool") for x in (k["r"].get("tool_goi") or [])][:4]))

    hop_le = [k for k in ket if k["trang_thai"] == "KHOP"]
    print("\n=> MẪU DÙNG ĐƯỢC (rổ neo đã xác minh): %d bản ghi" % len(hop_le))

    # ---- ĐỐI CHỨNG ÂM cho bộ so phán quyết ----
    print("\n" + "=" * 92)
    print("ĐỐI CHỨNG ÂM — bộ so phán quyết có phản ứng thật không?")
    print("=" * 92)
    n_co_do = sum(1 for k in hop_le
                  if quyet_dinh(k["r"]["answer_truoc_guard"], k["pool"], mcp_bridge._is_grounded) != "KHONG_DUNG")
    # ĐC-A: luật "neo cái gì cũng đúng" -> KHÔNG được có ca REFUSE nào (bộ so phải nhận ra chiều NỚI)
    n_het_giu = sum(1 for k in hop_le
                    if quyet_dinh(k["r"]["answer_truoc_guard"], k["pool"], lambda a, n: True) == "REFUSE")
    print("  ĐC-A luật NEO-MỌI-THỨ              -> REFUSE %d / %d câu-có-đo-lường  %s"
          % (n_het_giu, n_co_do, "ĐẠT" if n_het_giu == 0 else "!!! HỎNG"))
    # ĐC-B: ép rổ neo RỖNG -> MỌI câu có đo-lường phải REFUSE (bộ so phải nhận ra chiều SIẾT)
    n_rong = sum(1 for k in hop_le
                 if quyet_dinh(k["r"]["answer_truoc_guard"], set(), mcp_bridge._is_grounded) == "REFUSE")
    print("  ĐC-B ép rổ neo RỖNG                -> REFUSE %d / %d câu-có-đo-lường  %s"
          % (n_rong, n_co_do, "ĐẠT" if n_rong == n_co_do else "!!! HỎNG"))
    if n_het_giu or n_rong != n_co_do:
        print("  => ĐỐI CHỨNG ÂM HỎNG, KHÔNG công bố số bước 2."); return 3

    # ---- BƯỚC 2: bỏ ×1000 thì bao nhiêu câu lật? ----
    print("\n" + "=" * 92)
    print("BƯỚC 2 — BỎ NHÁNH ×1000 THÌ BAO NHIÊU CÂU LẬT GIỮ -> REFUSE?")
    print("=" * 92)
    lat, giu_giu, ko_dung, lat_ids = 0, 0, 0, []
    for k in hop_le:
        txt = k["r"]["answer_truoc_guard"]
        a1 = quyet_dinh(txt, k["pool"], mcp_bridge._is_grounded)
        a2 = quyet_dinh(txt, k["pool"], _is_grounded_khong_x1000)
        if a1 == "KHONG_DUNG":
            ko_dung += 1
        elif a1 == "GIU" and a2 == "REFUSE":
            lat += 1; lat_ids.append(k)
        elif a1 == "GIU":
            giu_giu += 1
    co_do = len(hop_le) - ko_dung
    print("  Mẫu đã xác minh                       : %d" % len(hop_le))
    print("    · không có khẳng định đo-lường      : %d" % ko_dung)
    print("    · CÓ khẳng định đo-lường            : %d   <-- MẪU SỐ của tỉ lệ dưới" % co_do)
    print("      - vẫn GIỮ khi bỏ ×1000            : %d = %.1f%%" % (giu_giu, 100.0 * giu_giu / max(1, co_do)))
    print("      - LẬT sang REFUSE khi bỏ ×1000    : %d = %.1f%%" % (lat, 100.0 * lat / max(1, co_do)))
    print("  (tính trên TOÀN mẫu %d bản ghi: %.1f%%)" % (len(hop_le), 100.0 * lat / max(1, len(hop_le))))

    # phân nhóm câu LẬT theo nhãn độc lập (`ky_vong` / `loai`) — LẬT trên câu ĐÚNG mới là GIẾT OAN
    if lat_ids:
        print("\n  Phân loại %d câu LẬT theo `loai` của battery:" % lat)
        for t, c in collections.Counter(k["r"].get("loai") for k in lat_ids).most_common():
            print("     %-22s %d" % (t, c))

        print("\n  VÌ SAO câu đó CẦN ×1000 (phân loại theo SỐ đã cứu câu):")
        theo_cau = collections.Counter()
        theo_so = collections.Counter()
        for k in lat_ids:
            ly = vi_sao_can_x1000(k["r"]["answer_truoc_guard"], k["pool"])
            k["ly_do"] = ly
            h = {x[1] for x in ly}
            theo_cau["+".join(sorted(h)) or "(khong ro)"] += 1
            for x in ly:
                theo_so[x[1]] += 1
        print("     -- theo CÂU (tổ hợp nguyên nhân trong cùng câu):")
        for t, c in theo_cau.most_common():
            print("        %-28s %d = %.1f%%" % (t, c, 100.0 * c / max(1, lat)))
        print("     -- theo SỐ (mỗi số cứu câu tính 1):")
        for t, c in theo_so.most_common():
            print("        %-28s %d" % (t, c))
        print("\n  20 ca LẬT đầu (để ĐỌC TAY — bắt buộc, không chấm bằng máy):")
        for k in lat_ids[:20]:
            r = k["r"]
            print("     id%-4s luot%-3s [%s] hỏi: %s" % (r.get("id"), r.get("luot"), r.get("loai"),
                                                        (r.get("cau_hoi") or "")[:60]))
            print("            kỳ vọng: %s" % ((r.get("ky_vong") or "")[:100]))
            print("            trả lời: %s" % (r["answer_truoc_guard"][:150].replace("\n", " ")))

    # xuất JSON cho phân tích tiếp / đọc tay
    out = os.path.join(RUNS, "_x1000_lat.json")
    with open(out, "w", encoding="utf-8") as fo:
        json.dump([{"id": k["r"].get("id"), "luot": k["r"].get("luot"), "file": k["r"].get("file"),
                    "loai": k["r"].get("loai"), "cau_hoi": k["r"].get("cau_hoi"),
                    "ky_vong": k["r"].get("ky_vong"),
                    "answer_truoc_guard": k["r"]["answer_truoc_guard"],
                    "ly_do": [[x[0], x[1], x[2]] for x in (k.get("ly_do") or [])],
                    "ro_neo": sorted(k["pool"])} for k in lat_ids], fo, ensure_ascii=False, indent=1)
    print("\n  Chi tiết ca LẬT -> %s" % out)
    print("\nTổng thời gian: %.0fs" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
