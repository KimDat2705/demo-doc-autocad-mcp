# -*- coding: utf-8 -*-
"""
Chạy BỘ CÂU HỎI (battery.json) qua DEMO 2 (Gemini + MCP), lưu câu trả lời để chấm.

THIẾT KẾ (1.06 — 2026-07-31). Bản CŨ mở file bằng mode "w": chạy một lần là XOÁ SẠCH kết quả
lượt trước, nên (a) không đo được độ ổn định N-lượt, (b) docstring cũ hứa "không mất tiến độ nếu
gián đoạn" là NÓI DỐI — gián đoạn rồi chạy lại là mất trắng. Bản này:

  1. GHI THÊM, KHÔNG BAO GIỜ GHI ĐÈ. File dữ liệu chỉ mở bằng "x" (lượt mới) hoặc "a" (chạy tiếp).
     Không có đường nào rewrite/xoá/os.replace lên file kết quả. File lịch sử
     `tests/battery_results.jsonl` KHÔNG còn được script này đụng tới.
  2. MỖI LƯỢT MỘT FILE:  tests/battery_runs/run<NN>.jsonl  (NN = 01..99, tự chọn số trống).
     Định danh lượt nằm ở sidecar  tests/battery_runs/_meta/run<NN>.meta.json  (ghi MỘT LẦN, mode "x").
  3. MỖI DÒNG TỰ KHAI PHIÊN BẢN (prompt_hash8 / kb_hash8 / code_hash8 / battery_sha12 / model).
     Lý do có thật: bảng điểm 24/07 nay không ai dám trích vì không biết nó sinh từ prompt nào.
  4. CHẠY TIẾP (--tiep) chỉ hỏi lại các câu CHƯA CÓ câu trả lời hợp lệ; và TỪ CHỐI chạy tiếp nếu
     định danh (prompt/kb/code/battery) đã đổi — trộn hai phiên bản vào một lượt là phá phép đo.
  5. "HỢP LỆ" nhận biết bằng CẤU TRÚC, không bằng khớp chuỗi tiếng Việt: `tra_loi_ai` chỉ đính kèm
     khoá `answer_goc` trên hai đường trả lời THẬT (mcp_bridge.py:988 và :1008); cả 4 đường hỏng
     (quá tải :913 · rỗng :918 · rỗng-sau-nhắc :984 · hết lượt tool :1012) đều KHÔNG có khoá đó.
     Câu chữ tiếng Việt đổi lúc nào cũng được, cấu trúc thì không.
  6. TẮT CHUỖI MODEL DỰ PHÒNG. Mặc định `GEMINI_FALLBACK_MODELS` bị ép rỗng TRƯỚC khi import
     mcp_bridge (MODELS chốt lúc import). Nếu để nguyên, một cú 429 làm Gemini lặng lẽ nhảy sang
     2.0-flash/1.5-flash giữa lượt và không ai biết đang chấm model nào. Mở lại: BATTERY_CHUOI_MODEL=1.
  7. KHÔNG in "XONG" khi còn khuyết câu. Bản cũ `continue` im lặng khi thiếu file bản vẽ rồi vẫn in
     "XONG N câu" — một lượt khuyết 36 câu hạ tầng trông y hệt một lượt đủ.

Đo độ ổn định giữa các lượt: tests/do_on_dinh.py
"""
import os, sys, io, json, time, glob, hashlib, argparse, traceback, datetime

os.environ["READFILE_MAX_MB"] = "300"
# ⚠ PHẢI đặt TRƯỚC `import mcp_bridge` — MODELS được chốt lúc import (mcp_bridge.py:56).
if os.environ.get("BATTERY_CHUOI_MODEL", "") != "1":
    os.environ["GEMINI_FALLBACK_MODELS"] = ""

# Bọc stdout utf-8 nhưng KHÔNG bọc chồng (test import file này cũng đã tự bọc).
if (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "") != "utf8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, GOC)
import mcp_bridge

# corpus THẬT giữ ngoài repo (gitignored) — thiếu nó thì `import run_battery` VẪN phải chạy được,
# nếu không thì cổng check.sh đỏ trên máy sạch. Kiểm tra dời vào main().
try:
    from corpus_local import KT, KC, HT
except Exception:
    KT = KC = HT = None

TRAP_ON = "kientruc"      # câu 'any' (bẫy) chạy trên file kiến trúc (giàu cấu kiện nhất)
ORDER = ["kientruc", "ketcau", "hatang"]
BATTERY = os.path.join(HERE, "battery.json")
RUNS_DIR = os.path.join(HERE, "battery_runs")
META_DIR = os.path.join(RUNS_DIR, "_meta")
THU_LAI_TOI_DA = 2        # trần cứng số lần hỏi lại 1 câu trong CÙNG một lượt (chống livelock)

# ---- SEAM bắt RỔ NEO grounding (tuỳ chọn, --ghi-ro-neo) ------------------------------------
# Rổ neo (`tool_numbers`) chỉ tồn tại BÊN TRONG `tra_loi_ai` và KHÔNG nằm trong dict trả về.
# ⛔ KHÔNG thêm nó vào dict trả về: `app.py` làm `return jsonify(r)` -> mọi số nội bộ của tool
#    sẽ bị đẩy thẳng ra trình duyệt ở MỌI câu hỏi. Thay vào đó bọc `_guard_text` TỪ PHÍA TEST
#    (nó nhận đúng tham số đó, mcp_bridge.py:986 và :1006) -> 0 dòng code sản phẩm bị chạm.
_NEO = {"n": None, "khong_neo_do": None, "khong_neo_tat_ca": None}


def _bat_ro_neo():
    goc = mcp_bridge._guard_text
    if getattr(goc, "_la_spy_battery", False):
        return
    def spy(text, tool_numbers):
        try:
            pool = set(tool_numbers or ())
            tat_ca, do_luong = mcp_bridge._answer_numbers(text or "")
            _NEO["n"] = len(pool)
            _NEO["khong_neo_do"] = sorted({x for x in do_luong if not mcp_bridge._is_grounded(x, pool)})
            _NEO["khong_neo_tat_ca"] = sorted({x for x in tat_ca if not mcp_bridge._is_grounded(x, pool)})
        except Exception:
            pass
        return goc(text, tool_numbers)
    spy._la_spy_battery = True
    mcp_bridge._guard_text = spy

# Mã thoát
OK, E_DA_CO, E_HONG, E_CHUOI_MODEL, E_LECH_BAN, E_KHUYET, E_THIEU_BAN_VE = 0, 2, 3, 4, 5, 8, 9


def files_mac_dinh():
    return {
        "kientruc": (KT, "KIẾN TRÚC CT-A"),
        "ketcau":   (KC, "KẾT CẤU CT-A"),
        "hatang":   (HT, "HẠ TẦNG CT-K"),
    }


# ---------------------------------------------------------------- đường dẫn (một nguồn duy nhất)
def duong_dan_luot(n):
    return os.path.join(RUNS_DIR, "run%02d.jsonl" % int(n))


def duong_dan_meta(n):
    return os.path.join(META_DIR, "run%02d.meta.json" % int(n))


def chon_luot_moi():
    """Số lượt trống nhỏ nhất trong 1..99. Không bao giờ trả về số đã có file."""
    for n in range(1, 100):
        if not os.path.exists(duong_dan_luot(n)):
            return n
    raise RuntimeError("Đã dùng hết 99 số lượt trong %s" % RUNS_DIR)


# ---------------------------------------------------------------- định danh phiên bản
def _sha(b, n=None):
    h = hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()
    return h[:n] if n else h


def _commit():
    """Đọc commit từ .git mà KHÔNG sinh tiến trình con. Không có git -> None (KHÔNG bịa 'unknown')."""
    try:
        head = open(os.path.join(GOC, ".git", "HEAD"), encoding="utf-8").read().strip()
        if head.startswith("ref:"):
            ref = head.split(" ", 1)[1].strip()
            p = os.path.join(GOC, ".git", ref.replace("/", os.sep))
            if os.path.isfile(p):
                return open(p, encoding="utf-8").read().strip()
            for l in open(os.path.join(GOC, ".git", "packed-refs"), encoding="utf-8"):
                if l.strip().endswith(" " + ref):
                    return l.split(" ", 1)[0].strip()
            return None
        return head or None
    except Exception:
        return None


def _code_hash():
    """Hash gộp của các file quyết định hành vi trả lời. Đổi code -> đổi hash -> lượt cũ/mới không trộn."""
    h = hashlib.sha256()
    for ten in ("mcp_bridge.py", "tools_core.py", "mcp_server.py", "kienthuc.py"):
        p = os.path.join(GOC, ten)
        h.update(open(p, "rb").read() if os.path.isfile(p) else b"")
    return h.hexdigest()


def dinh_danh():
    """Định danh phiên bản của LƯỢT CHẠY. Các khoá *_hash là thứ dùng để chặn trộn lượt."""
    try:
        import kienthuc
        kb_v, kb_h = kienthuc.KB_VERSION, kienthuc.KB_HASH
    except Exception:
        kb_v, kb_h = None, None
    batt = open(BATTERY, "rb").read() if os.path.isfile(BATTERY) else b""
    c = _commit()
    return {
        "prompt_version": getattr(mcp_bridge, "PROMPT_VERSION", None),
        "prompt_hash": getattr(mcp_bridge, "PROMPT_HASH", None),
        "kb_version": kb_v,
        "kb_hash": kb_h,
        "code_hash": _code_hash(),
        "battery_sha": _sha(batt),
        "model": (mcp_bridge.MODELS or [None])[0],
        "models_cau_hinh": list(mcp_bridge.MODELS),
        "fallback_bi_tat": len(mcp_bridge.MODELS) == 1,
        "max_turns": getattr(mcp_bridge, "MAX_TURNS", None),
        "commit": c,
        "python": sys.version.split()[0],
    }


KHOA_CHAN_TRON = ("prompt_hash", "kb_hash", "code_hash", "battery_sha")


def _rut(d):
    """Phần định danh nhét vào TỪNG dòng (ngắn, đủ để phát hiện trộn lượt mà không phình file)."""
    return {
        "prompt_hash8": (d.get("prompt_hash") or "")[:8] or None,
        "kb_hash8": (d.get("kb_hash") or "")[:8] or None,
        "code_hash8": (d.get("code_hash") or "")[:8] or None,
        "battery_sha12": (d.get("battery_sha") or "")[:12] or None,
        "model": d.get("model"),
    }


# ---------------------------------------------------------------- đọc lại file lượt (resume)
def doc_luot(path):
    """Đọc file lượt -> (danh sách bản ghi, số dòng hỏng). Dòng CỤT Ở CUỐI (mất điện giữa lúc ghi)
    là bình thường và được bỏ qua; dòng hỏng Ở GIỮA là dấu hiệu file bị can thiệp -> caller dừng."""
    recs, hong_giua = [], 0
    if not os.path.isfile(path):
        return recs, hong_giua
    dong = [l for l in open(path, encoding="utf-8").read().splitlines()]
    for i, l in enumerate(dong):
        if not l.strip():
            continue
        try:
            recs.append(json.loads(l))
        except Exception:
            if i < len(dong) - 1:
                hong_giua += 1
    return recs, hong_giua


def id_da_xong(recs):
    """id đã có ÍT NHẤT một câu trả lời HỢP LỆ. id chỉ toàn bản ghi hỏng -> chưa xong, sẽ hỏi lại."""
    return {r.get("id") for r in recs if r.get("hop_le")}


# ---------------------------------------------------------------- bản ghi
def ban_ghi(q, f, r, luot, lan_thu, dd, giay):
    """Dựng 1 dòng kết quả. GIỮ NGUYÊN 12 khoá cũ (tests/prep_verify.py đọc trực tiếp) + thêm khoá mới."""
    ev = (r.get("evidence") or []) if isinstance(r, dict) else []
    ans = r.get("answer", "") if isinstance(r, dict) else ""
    rec = {
        # --- 12 khoá CŨ, không đổi tên/kiểu (hợp đồng với prep_verify.py) ---
        "id": q.get("id"), "file": f, "loai": q.get("loai"), "cau_hoi": q.get("cau_hoi", ""),
        "ky_vong": q.get("ky_vong"), "loi_san": q.get("loi_san"),
        "answer": ans if isinstance(ans, str) else str(ans),
        "anh_id": r.get("anh_id") if isinstance(r, dict) else None,
        "n_evidence": len(ev),
        "handles": [e.get("handle") for e in ev][:30],
        "evidence_text": [e.get("text") for e in ev][:15],
        "thoi_gian_s": round(giay, 1),
        # --- MỚI ---
        "luot": luot, "lan_thu": lan_thu,
        "ts": datetime.datetime.now().replace(microsecond=0).isoformat(),
        # HỢP LỆ = CẤU TRÚC (xem docstring §5). KHÔNG suy từ câu chữ tiếng Việt.
        "hop_le": bool(isinstance(r, dict) and "answer_goc" in r),
        "n_kb_cau_hoi": len((r.get("kb_cau_hoi") or []) if isinstance(r, dict) else []),
    }
    rec.update(_rut(dd))
    return rec


def ban_ghi_loi(q, f, e, luot, lan_thu, dd, giay):
    r = {"answer": "[[LỖI]] %s: %s" % (type(e).__name__, e), "evidence": [], "anh_id": None}
    return ban_ghi(q, f, r, luot, lan_thu, dd, giay)


# ---------------------------------------------------------------- nạp battery
def nap_battery():
    b = json.load(open(BATTERY, encoding="utf-8"))
    qs = b["battery"] if isinstance(b, dict) else b
    bf = {k: [] for k in ORDER}
    for q in qs:
        f = q.get("file", "any")
        bf.setdefault(TRAP_ON if f == "any" else f, []).append(q)
    return qs, bf


# ---------------------------------------------------------------- main
def main(argv=None, hoi=None, tao_bridge=None, files=None):
    ap = argparse.ArgumentParser(description="Chạy bộ 198 câu, ghi thêm không ghi đè.")
    ap.add_argument("--luot", default="auto", help="số lượt 1..99 (mặc định: số trống nhỏ nhất)")
    ap.add_argument("--tiep", action="store_true", help="chạy tiếp vào lượt đã có (chỉ hỏi câu còn thiếu)")
    ap.add_argument("--chi-id", default="", help="chỉ chạy các id này (ngăn phẩy) — để thử nhanh")
    ap.add_argument("--gioi-han", type=int, default=0, help="chỉ chạy N câu đầu (thử nhanh)")
    ap.add_argument("--ghi-chu", default="", help="ghi chú tự do lưu vào meta")
    ap.add_argument("--chay-thu", action="store_true",
                    help="kiểm mọi điều kiện + chốt đường dẫn rồi DỪNG, không gọi API")
    ap.add_argument("--ghi-ro-neo", action="store_true",
                    help="ghi thêm thông tin RỔ NEO grounding vào bản ghi (bọc _guard_text phía test)")
    # ⚠ PHẢI là parse_args(argv). Viết `[] if argv is None else argv` thì khi chạy TỪ DÒNG LỆNH
    # (argv=None) argparse nhận danh sách RỖNG -> MỌI tham số bị vứt IM LẶNG -> `--chay-thu` không
    # có tác dụng và script chạy thật, TIÊU TIỀN API. Đã mắc đúng lỗi này ngày 2026-07-31 (42 câu).
    # argparse tự lấy sys.argv[1:] khi nhận None — đừng "giúp" nó. (khao_sat_corpus.py:486 làm đúng.)
    a = ap.parse_args(argv)

    FILES = files if files is not None else files_mac_dinh()
    dd = dinh_danh()

    # --- cổng 1: chuỗi model phải đúng 1 (phép đo bẩn nếu 429 nhảy model giữa chừng) ---
    if not dd["fallback_bi_tat"]:
        print("DỪNG: chuỗi model dự phòng đang BẬT (%s). Benchmark phải đo ĐÚNG MỘT model."
              % ", ".join(dd["models_cau_hinh"]))
        print("      Bỏ biến BATTERY_CHUOI_MODEL=1 để script tự tắt chuỗi.")
        return E_CHUOI_MODEL

    # --- cổng 2: đủ 3 file bản vẽ TRƯỚC khi tiêu đồng API nào ---
    thieu = [f for f in ORDER if not (FILES.get(f) and FILES[f][0] and os.path.isfile(FILES[f][0]))]
    if thieu:
        print("DỪNG: thiếu bản vẽ cho nhóm: %s" % ", ".join(thieu))
        print("      (corpus_local.py giữ ngoài repo — xem harness/QUY_TRINH_AN_DANH_DU_LIEU_MAU.md)")
        return E_THIEU_BAN_VE

    # --- chốt số lượt + đường dẫn ---
    if a.luot == "auto":
        luot = chon_luot_moi() if not a.tiep else max(
            [int(os.path.basename(p)[3:5]) for p in glob.glob(os.path.join(RUNS_DIR, "run[0-9][0-9].jsonl"))] or [0])
        if a.tiep and luot == 0:
            print("DỪNG: --tiep nhưng chưa có lượt nào trong %s" % RUNS_DIR)
            return E_KHUYET
    else:
        luot = int(a.luot)
    if not (1 <= luot <= 99):
        print("DỪNG: --luot phải trong 1..99")
        return E_THIEU_BAN_VE
    path, mpath = duong_dan_luot(luot), duong_dan_meta(luot)
    da_co = os.path.exists(path)

    # --- cổng 3: KHÔNG BAO GIỜ ghi đè ---
    if da_co and not a.tiep:
        print("DỪNG: %s đã tồn tại. Muốn chạy tiếp thì thêm --tiep; muốn lượt mới thì bỏ --luot." % path)
        return E_DA_CO
    if not da_co and os.path.exists(mpath):
        # meta MỒ CÔI (file dữ liệu đã bị xoá tay). Nếu chạy tiếp thì lượt mới sẽ đội định danh CŨ
        # của meta -> sidecar nói dối về lượt. Bắt người dùng dọn tay, không tự đoán.
        print("DỪNG: có %s nhưng KHÔNG có %s. Sidecar mồ côi — xoá nó hoặc chọn số lượt khác."
              % (mpath, path))
        return E_DA_CO

    cu, hong_giua = doc_luot(path) if da_co else ([], 0)
    if hong_giua:
        print("DỪNG: %s có %d dòng hỏng KHÔNG phải ở cuối file — không ghi tiếp lên file nghi vấn."
              % (path, hong_giua))
        return E_HONG

    # --- cổng 4: chạy tiếp mà định danh đã đổi -> trộn phiên bản -> chặn ---
    if da_co and os.path.isfile(mpath):
        cu_dd = json.load(open(mpath, encoding="utf-8")).get("dinh_danh", {})
        lech = [k for k in KHOA_CHAN_TRON if cu_dd.get(k) != dd.get(k)]
        if lech:
            print("DỪNG: lượt %02d chạy trên bản KHÁC (lệch: %s). Trộn hai phiên bản vào một lượt"
                  " làm hỏng phép đo — hãy mở LƯỢT MỚI." % (luot, ", ".join(lech)))
            for k in lech:
                print("      %-13s cũ=%s  nay=%s" % (k, str(cu_dd.get(k))[:12], str(dd.get(k))[:12]))
            return E_LECH_BAN

    qs, by_file = nap_battery()
    chi = {int(x) for x in a.chi_id.split(",") if x.strip().isdigit()}
    if chi:
        by_file = {f: [q for q in v if q.get("id") in chi] for f, v in by_file.items()}
    if a.gioi_han > 0:
        con = a.gioi_han
        for f in ORDER:
            by_file[f] = by_file[f][:max(0, con)]
            con -= len(by_file[f])
    xong = id_da_xong(cu)
    can = {f: [q for q in by_file[f] if q.get("id") not in xong] for f in ORDER}
    tong_can = sum(len(can[f]) for f in ORDER)
    tong_ky_vong = sum(len(by_file[f]) for f in ORDER)

    os.makedirs(RUNS_DIR, exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)
    print("LƯỢT %02d -> %s" % (luot, path))
    print("Battery: %d câu kỳ vọng (kientruc=%d, ketcau=%d, hatang=%d) | đã xong %d | cần chạy %d"
          % (tong_ky_vong, len(by_file["kientruc"]), len(by_file["ketcau"]), len(by_file["hatang"]),
             len(xong), tong_can))
    print("Model: %s | prompt %s (%s) | kb %s | code %s"
          % (dd["model"], dd["prompt_version"], (dd["prompt_hash"] or "?")[:8],
             (dd["kb_hash"] or "?")[:8], (dd["code_hash"] or "?")[:8]))
    if a.chay_thu:
        print("--chay-thu: mọi điều kiện ĐẠT, không gọi API. Dừng.")
        return OK

    # --- meta ghi MỘT LẦN, mode "x" (không rewrite -> không có đường mất meta) ---
    if not os.path.exists(mpath):
        with open(mpath, "x", encoding="utf-8") as m:
            json.dump({"luot": luot, "bat_dau": datetime.datetime.now().replace(microsecond=0).isoformat(),
                       "ghi_chu": a.ghi_chu, "dinh_danh": dd,
                       "ids_ky_vong": sorted(q.get("id") for f in ORDER for q in by_file[f])},
                      m, ensure_ascii=False, indent=1)

    # Mở file KẾT QUẢ TRƯỚC khi dựng bridge: nếu đường ghi hỏng (hết đĩa/không quyền/đua tạo file)
    # thì hỏng LÚC RẺ, chưa spawn tiến trình con nào để mà rò.
    out = open(path, "a" if da_co else "x", encoding="utf-8")
    br = None
    stt, done, t0 = 0, 0, time.time()
    if a.ghi_ro_neo:
        _bat_ro_neo()
    try:
        br = (tao_bridge or (lambda: mcp_bridge.MCPBridge(["mcp_server.py"],
                                                          env={"READFILE_MAX_MB": "300"})))()
        hoi_fn = hoi or mcp_bridge.tra_loi_ai
        print("Bridge OK, %d tool. USE_AI=%s" % (len(getattr(br, "tools", []) or []), mcp_bridge.USE_AI))
        for f in ORDER:
            if not can[f]:
                continue
            p, ten = FILES[f]
            s = br.call("nap_ban_ve", {"path": p}, timeout=600) or {}
            summary = "%s (AutoCAD %s), %s đối tượng, %s layer." % (
                ten, s.get("dxfversion"), s.get("tong_doi_tuong"), s.get("so_layer"))
            print("\n### NẠP %s: %s ###" % (f, summary))
            for q in can[f]:
                stt += 1
                lan = 1
                while True:
                    done += 1
                    t = time.time()
                    _NEO.update({"n": None, "khong_neo_do": None, "khong_neo_tat_ca": None})
                    try:
                        r = hoi_fn(br, q.get("cau_hoi", ""), summary)
                        rec = ban_ghi(q, f, r, luot, lan, dd, time.time() - t)
                        if a.ghi_ro_neo:
                            rec["ro_neo_n"] = _NEO["n"]
                            rec["so_do_luong_khong_neo"] = _NEO["khong_neo_do"]
                            rec["so_tat_ca_khong_neo"] = _NEO["khong_neo_tat_ca"]
                    except Exception as e:
                        rec = ban_ghi_loi(q, f, e, luot, lan, dd, time.time() - t)
                        traceback.print_exc()
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    out.flush()
                    print("[%d/%d]%s (%s) %.0fs %s | %s -> %s"
                          % (stt, tong_can, "" if lan == 1 else " lần%d" % lan,
                             q.get("loai", "?"), rec["thoi_gian_s"],
                             "ok" if rec["hop_le"] else "HỎNG",
                             (q.get("cau_hoi") or "")[:50], rec["answer"][:80].replace("\n", " ")))
                    if rec["hop_le"] or lan >= THU_LAI_TOI_DA:
                        break
                    lan += 1
    finally:
        # Đóng ĐỘC LẬP: out.close() ném thì br vẫn phải được đóng (nếu không là rò tiến trình con).
        try:
            out.close()
        except Exception:
            traceback.print_exc()
        try:
            if br is not None:
                br.close()
        except Exception:
            pass

    # --- kết: chỉ in XONG khi ĐỦ ---
    recs, _ = doc_luot(path)
    co_ban_ghi = {r.get("id") for r in recs}
    can_co = {q.get("id") for f in ORDER for q in by_file[f]}
    khuyet = sorted(can_co - co_ban_ghi)
    khong_hop_le = sorted(can_co - id_da_xong(recs))
    print("\n%d/%d câu có bản ghi | %d câu KHÔNG hợp lệ (hạ tầng/model): %s"
          % (len(co_ban_ghi & can_co), len(can_co), len(khong_hop_le),
             ", ".join("id%s" % i for i in khong_hop_le[:12]) or "không"))
    print("Thời gian %.0fs -> %s" % (time.time() - t0, path))
    if khuyet:
        print("CHƯA XONG: khuyết %d câu (%s). Chạy lại với --tiep --luot %02d."
              % (len(khuyet), ", ".join("id%s" % i for i in khuyet[:12]), luot))
        return E_KHUYET
    print("XONG lượt %02d — đủ %d câu." % (luot, len(can_co)))
    return OK


if __name__ == "__main__":
    sys.exit(main())
