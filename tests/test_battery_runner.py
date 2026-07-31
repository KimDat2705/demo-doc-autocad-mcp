# -*- coding: utf-8 -*-
"""1.06 — RUN_BATTERY + ĐO ỔN ĐỊNH. TẤT ĐỊNH, OFFLINE, KHÔNG tốn API / KHÔNG spawn subprocess.
Chạy:  python tests/test_battery_runner.py

Bản cũ của run_battery.py mở file kết quả bằng mode "w" -> chạy một lần là XOÁ SẠCH lượt trước
(và xoá luôn bản ghi lịch sử 24/07), nên không đo được độ ổn định N-lượt. Suite này khoá:
  [R] run_battery: không ghi đè · chạy tiếp · chặn trộn phiên bản · fail-fast · không dối "XONG"
  [D] do_on_dinh : 5 rổ · so bằng SET · loại rổ tầm thường · bất biến theo N · chặn phép đo bẩn

Mọi ca chạy qua SEAM (bridge giả + hàm hỏi giả) trong thư mục tạm — không đụng tests/battery_runs/
thật, không đụng tests/battery_results.jsonl."""
import os, sys, io, json, glob, shutil, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import run_battery as RB
import do_on_dinh as DD

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


# ------------------------------------------------------------------ seam giả
class FakeBridge:
    def __init__(self):
        self.closed = False

    def call(self, name, args, timeout=120):
        return {"name": "x", "dxfversion": "AC1032", "tong_doi_tuong": 7, "so_layer": 3}

    def close(self, cho_giay=0.0):
        self.closed = True
        return True

    tools = []


def hoi_tot(bridge, q, summary="", history=None):
    """Đáp HỢP LỆ: có khoá `answer_goc` — đúng như tra_loi_ai trên 2 đường trả lời thật."""
    return {"answer": "Có 12 cột, mỗi cột 220 mm.", "answer_goc": "goc", "evidence": [], "ai": True}


def hoi_hong(bridge, q, summary="", history=None):
    """Đáp KHÔNG hợp lệ: đúng hình dạng đường quá-tải mcp_bridge.py:913 (KHÔNG có answer_goc)."""
    return {"answer": "⚠ AI đang quá tải hoặc hết lượt truy vấn (đã thử 1 model). "
                      "Vui lòng thử lại sau ít phút.", "evidence": [], "ai": True}


def hoi_no(bridge, q, summary="", history=None):
    raise RuntimeError("bridge chet")


def moi_truong(td, n_cau=6):
    """Dựng battery nhỏ + FILES giả trong thư mục tạm; trỏ mọi hằng đường dẫn của RB vào đó."""
    qs = []
    for i in range(n_cau):
        qs.append({"id": i + 1, "cau_hoi": "cau %d" % (i + 1),
                   "file": ["kientruc", "ketcau", "hatang"][i % 3],
                   "loai": ["so_luong", "chi_tiet"][i % 2],
                   "ky_vong": "kv%d" % i, "loi_san": "ls%d" % i, "tieu_chi_dat": "t"})
    bp = os.path.join(td, "battery.json")
    json.dump({"battery": qs}, open(bp, "w", encoding="utf-8"), ensure_ascii=False)
    ve = os.path.join(td, "ve.dxf")
    open(ve, "w").write("x")
    RB.BATTERY = bp
    RB.RUNS_DIR = os.path.join(td, "battery_runs")
    RB.META_DIR = os.path.join(RB.RUNS_DIR, "_meta")
    return {"kientruc": (ve, "KT"), "ketcau": (ve, "KC"), "hatang": (ve, "HT")}


def chay(argv, hoi=hoi_tot, files=None):
    return RB.main(argv, hoi=hoi, tao_bridge=FakeBridge, files=files)


def main():
    global PASS, FAIL
    _batt, _runs, _meta = RB.BATTERY, RB.RUNS_DIR, RB.META_DIR
    td = tempfile.mkdtemp(prefix="batt_test_")
    try:
        F = moi_truong(td)

        # ---------------------------------------------------------------- [R.1]
        print("[R.1] lượt mới -> đủ câu, 1 dòng/id, exit 0, có in XONG")
        rc = chay(["--luot", "1"], files=F)
        p1 = RB.duong_dan_luot(1)
        recs = [json.loads(l) for l in open(p1, encoding="utf-8") if l.strip()]
        ok("exit 0", rc == 0, rc)
        ok("đủ 6 dòng, 6 id khác nhau", len(recs) == 6 and len({r["id"] for r in recs}) == 6, len(recs))
        ok("mọi dòng hop_le=True (đáp có answer_goc)", all(r["hop_le"] for r in recs))
        ok("có sidecar meta", os.path.isfile(RB.duong_dan_meta(1)))
        ok("mỗi dòng tự khai phiên bản", all(r.get("prompt_hash8") and r.get("code_hash8") for r in recs))
        ok("giữ đủ 12 khoá CŨ (hợp đồng prep_verify)",
           all(k in recs[0] for k in ("id", "file", "loai", "cau_hoi", "ky_vong", "loi_san", "answer",
                                      "anh_id", "n_evidence", "handles", "evidence_text", "thoi_gian_s")))

        # ---------------------------------------------------------------- [R.2] KHÔNG GHI ĐÈ
        print("\n[R.2] lượt đã tồn tại + KHÔNG --tiep -> từ chối, file KHÔNG đổi 1 byte")
        truoc = open(p1, "rb").read()
        rc = chay(["--luot", "1"], files=F)
        ok("exit = E_DA_CO(2)", rc == RB.E_DA_CO, rc)
        ok("file y nguyên từng byte", open(p1, "rb").read() == truoc)

        print("\n[R.2b] sidecar MỒ CÔI (meta còn, dữ liệu bị xoá tay) -> DỪNG, không đội định danh cũ")
        os.rename(p1, p1 + ".tam")
        rc = chay(["--luot", "1"], files=F)
        ok("exit = E_DA_CO(2)", rc == RB.E_DA_CO, rc)
        ok("KHÔNG tạo lại file lượt 1", not os.path.exists(p1))
        os.rename(p1 + ".tam", p1)

        # ---------------------------------------------------------------- [R.3] auto không đụng lượt cũ
        print("\n[R.3] --luot auto -> chọn số TRỐNG, không bao giờ trỏ vào lượt đã có")
        rc = chay([], files=F)
        ok("exit 0", rc == 0, rc)
        ok("sinh run02, run01 còn nguyên", os.path.isfile(RB.duong_dan_luot(2))
           and open(p1, "rb").read() == truoc)

        # ---------------------------------------------------------------- [R.4] resume
        print("\n[R.4] lượt hỏng dở -> --tiep chỉ hỏi câu CÒN THIẾU, nội dung cũ vẫn ở đầu file")
        rc = chay(["--luot", "5"], hoi=hoi_hong, files=F)
        p5 = RB.duong_dan_luot(5)
        ok("lượt toàn hỏng -> exit 0 nhưng KHÔNG có câu hợp lệ", rc == 0
           and not any(json.loads(l)["hop_le"] for l in open(p5, encoding="utf-8") if l.strip()))
        n_hong = len([l for l in open(p5, encoding="utf-8") if l.strip()])
        ok("đã hỏi lại tới trần %d lần/câu" % RB.THU_LAI_TOI_DA, n_hong == 6 * RB.THU_LAI_TOI_DA, n_hong)
        dau_cu = open(p5, "rb").read()
        rc = chay(["--luot", "5", "--tiep"], files=F)
        moi = open(p5, "rb").read()
        ok("exit 0 sau khi chạy tiếp", rc == 0, rc)
        ok("nội dung CŨ vẫn nằm nguyên ở ĐẦU file (append, không rewrite)", moi.startswith(dau_cu))
        r5 = [json.loads(l) for l in open(p5, encoding="utf-8") if l.strip()]
        ok("mọi id nay đã có bản ghi hợp lệ", {r["id"] for r in r5 if r["hop_le"]} == {1, 2, 3, 4, 5, 6})

        print("\n[R.5] --tiep lần 2 khi đã đủ -> KHÔNG hỏi lại câu nào, file không dài thêm")
        dai = len(open(p5, "rb").read())
        rc = chay(["--luot", "5", "--tiep"], files=F)
        ok("exit 0 + file không đổi kích thước", rc == 0 and len(open(p5, "rb").read()) == dai)

        # ---------------------------------------------------------------- [R.6] chặn trộn phiên bản
        print("\n[R.6] --tiep khi ĐỊNH DANH đã đổi -> chặn (trộn 2 phiên bản = phá phép đo)")
        m = json.load(open(RB.duong_dan_meta(1), encoding="utf-8"))
        m["dinh_danh"]["prompt_hash"] = "0" * 64
        json.dump(m, open(RB.duong_dan_meta(1), "w", encoding="utf-8"))
        truoc = open(p1, "rb").read()
        rc = chay(["--luot", "1", "--tiep"], files=F)
        ok("exit = E_LECH_BAN(5)", rc == RB.E_LECH_BAN, rc)
        ok("không ghi thêm gì vào file", open(p1, "rb").read() == truoc)

        # ---------------------------------------------------------------- [R.7] fail-fast bản vẽ
        print("\n[R.7] thiếu bản vẽ -> DỪNG TRƯỚC khi tiêu API, KHÔNG tạo file, KHÔNG nói XONG")
        F2 = dict(F); F2["hatang"] = (os.path.join(td, "khong_co.dxf"), "HT")
        rc = chay(["--luot", "9"], files=F2)
        ok("exit = E_THIEU_BAN_VE(9)", rc == RB.E_THIEU_BAN_VE, rc)
        ok("KHÔNG tạo file lượt 9", not os.path.exists(RB.duong_dan_luot(9)))

        # ---------------------------------------------------------------- [R.8] không dối XONG
        print("\n[R.8] có câu KHÔNG bao giờ ra bản ghi -> báo CHƯA XONG, exit != 0")
        goc_ghi = RB.ban_ghi

        def ban_ghi_bo_id3(q, f, r, luot, lan, dd, giay):
            if q.get("id") == 3:
                raise KeyboardInterrupt("bo qua id3")
            return goc_ghi(q, f, r, luot, lan, dd, giay)
        RB.ban_ghi = ban_ghi_bo_id3
        try:
            rc = chay(["--luot", "11"], files=F)
        except KeyboardInterrupt:
            rc = "ngat"
        finally:
            RB.ban_ghi = goc_ghi
        con = [json.loads(l)["id"] for l in open(RB.duong_dan_luot(11), encoding="utf-8") if l.strip()]
        ok("file lượt 11 thiếu id3", 3 not in con, con)
        rc2 = chay(["--luot", "11", "--tiep"], hoi=hoi_no, files=F)
        ok("chạy tiếp mà câu vẫn hỏng -> KHÔNG in XONG, exit 0 với cờ hỏng ghi rõ", rc2 == 0)
        r11 = [json.loads(l) for l in open(RB.duong_dan_luot(11), encoding="utf-8") if l.strip()]
        ok("bản ghi lỗi được LƯU (không nuốt), đánh dấu hop_le=False",
           any(r["id"] == 3 and not r["hop_le"] and r["answer"].startswith("[[LỖI") for r in r11))

        # ---------------------------------------------------------------- [R.9] chuỗi model
        print("\n[R.9] chuỗi model dự phòng BẬT -> từ chối chạy (phép đo bẩn: 429 lặng lẽ đổi model)")
        import mcp_bridge as MB
        _m = MB.MODELS
        MB.MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
        try:
            rc = chay(["--luot", "12"], files=F)
        finally:
            MB.MODELS = _m
        ok("exit = E_CHUOI_MODEL(4)", rc == RB.E_CHUOI_MODEL, rc)
        ok("KHÔNG tạo file lượt 12", not os.path.exists(RB.duong_dan_luot(12)))
        ok("mặc định script TỰ TẮT chuỗi (env ép rỗng trước import)",
           os.environ.get("GEMINI_FALLBACK_MODELS") == "")

        # ---------------------------------------------------------------- [R.10] không đụng file lịch sử
        print("\n[R.10] KHÔNG còn đường nào trỏ vào tests/battery_results.jsonl")
        src = open(os.path.join(HERE, "run_battery.py"), encoding="utf-8").read()
        ok("hằng OUTJSONL đã bị xoá khỏi source", "OUTJSONL" not in src)
        ok("không còn open(..., 'w') cho file kết quả",
           'open(path, "w"' not in src and "open(OUT" not in src)
        ok("mọi đường dẫn lượt nằm trong battery_runs/",
           all(os.path.basename(os.path.dirname(RB.duong_dan_luot(n))) == "battery_runs"
               for n in (1, 7, 99)))
        ok("--chay-thu không gọi API và không tạo file", chay(["--luot", "40", "--chay-thu"], files=F) == 0
           and not os.path.exists(RB.duong_dan_luot(40)))

        # ---------------------------------------------------------------- [R.11]
        # Ca này sinh ra từ một lỗi THẬT của chính bản vá (2026-07-31): `parse_args([] if argv is
        # None else argv)` làm MỌI tham số dòng lệnh bị vứt im lặng, nên `--chay-thu` vô tác dụng
        # và script chạy THẬT, tiêu API 42 câu. Mọi ca test khác đều truyền argv tường minh nên
        # MÙ hoàn toàn với lỗi này — phải có ca đi đúng đường người dùng gõ lệnh.
        print("\n[R.11] tham số DÒNG LỆNH phải thật sự có tác dụng (argv=None -> đọc sys.argv)")
        truoc_ds = set(glob.glob(os.path.join(RB.RUNS_DIR, "run*.jsonl")))
        _argv, _out = sys.argv, sys.stdout
        sys.argv = ["run_battery.py", "--chay-thu", "--luot", "77"]
        sys.stdout = io.StringIO()
        try:
            rc = RB.main(hoi=hoi_tot, tao_bridge=FakeBridge, files=F)     # argv=None = như gõ lệnh
            man_hinh = sys.stdout.getvalue()
        finally:
            sys.argv, sys.stdout = _argv, _out
        sau_ds = set(glob.glob(os.path.join(RB.RUNS_DIR, "run*.jsonl")))
        ok("exit 0", rc == 0, rc)
        ok("--luot 77 ĐƯỢC đọc (in ra 'LƯỢT 77')", "LƯỢT 77" in man_hinh, man_hinh[:80])
        ok("--chay-thu ĐƯỢC đọc -> KHÔNG sinh file lượt nào", truoc_ds == sau_ds, sau_ds - truoc_ds)

        # ---------------------------------------------------------------- [D] đo ổn định
        print("\n[D.1] 5 rổ phân loại đúng")
        ok("cả hai rỗng -> khong_so_moi_luot", DD.ro(set(), set()) == "khong_so_moi_luot")
        ok("bằng nhau -> dong_nhat", DD.ro({1.0, 2.0}, {2.0, 1.0}) == "dong_nhat")
        ok("một bên rỗng -> mot_ben_rong", DD.ro({1.0}, set()) == "mot_ben_rong")
        ok("tập con -> bao_ham", DD.ro({1.0}, {1.0, 2.0}) == "bao_ham")
        ok("đá nhau -> mau_thuan", DD.ro({1.0}, {2.0}) == "mau_thuan")

        print("\n[D.2] so bằng SET, không phải LIST (bẫy đã đo: chênh ~10 điểm)")
        a1 = DD.so_do_luong("Dài 3,5 m và rộng 2,5 m.")
        a2 = DD.so_do_luong("Rộng 2,5 m và dài 3,5 m.")
        ok("đảo thứ tự vẫn dong_nhat", DD.ro(a1, a2) == "dong_nhat", (a1, a2))
        ok("hàm trả về set", isinstance(a1, set))

        print("\n[D.3] id ảnh hl_<hex> KHÔNG được tính là số (nhiễu do chính phép đo sinh ra)")
        b1 = DD.so_do_luong("Đã khoanh đỏ, ảnh hl_1a2b3c4d5e.png")
        b2 = DD.so_do_luong("Đã khoanh đỏ, ảnh hl_9f8e7d6c5b.png")
        ok("hai uuid khác nhau -> vẫn giống nhau", DD.ro(b1, b2) == "khong_so_moi_luot", (b1, b2))

        print("\n[D.4] chạy thật trên 3 lượt dựng tay")
        dd_dir = os.path.join(td, "dor")
        os.makedirs(dd_dir)
        mau = {"loai": "so_luong", "cau_hoi": "c", "hop_le": True, "prompt_hash8": "aaaaaaaa",
               "kb_hash8": "bbbbbbbb", "code_hash8": "cccccccc", "battery_sha12": "dddddddddddd",
               "model": "gemini-2.5-flash"}

        def viet(n, answers):
            with open(os.path.join(dd_dir, "run%02d.jsonl" % n), "w", encoding="utf-8") as f:
                for i, a in enumerate(answers, 1):
                    r = dict(mau); r["id"] = i; r["answer"] = a
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        # id1 ổn định · id2 mâu thuẫn · id3 một-bên-rỗng · id4 không số ở mọi lượt
        viet(1, ["Cao 3,5 m", "Rộng 2,2 m", "Dài 7,7 m", "Không tìm thấy thông tin."])
        viet(2, ["Cao 3,5 m", "Rộng 9,9 m", "Không tìm thấy.", "Không tìm thấy thông tin."])
        viet(3, ["Cao 3,5 m", "Rộng 9,9 m", "Dài 7,7 m", "Không có trong bản vẽ."])
        rc = DD.main(["--thu-muc", dd_dir])
        ok("chạy được, exit 0", rc == 0, rc)

        print("\n[D.5] chặn phép đo BẨN")
        r = json.loads(open(os.path.join(dd_dir, "run03.jsonl"), encoding="utf-8").readline())
        r["prompt_hash8"] = "ZZZZZZZZ"
        lines = open(os.path.join(dd_dir, "run03.jsonl"), encoding="utf-8").read().splitlines()
        lines[0] = json.dumps(r, ensure_ascii=False)
        open(os.path.join(dd_dir, "run03.jsonl"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        ok("lệch prompt_hash8 giữa các lượt -> TỪ CHỐI đo (exit 1)", DD.main(["--thu-muc", dd_dir]) == 1)

        dd2 = os.path.join(td, "dor2"); os.makedirs(dd2)
        for n in (1, 2):
            with open(os.path.join(dd2, "run%02d.jsonl" % n), "w", encoding="utf-8") as f:
                for i in range(1, 11):
                    r = dict(mau); r["id"] = i; r["answer"] = "Cao 3,5 m"
                    r["hop_le"] = not (n == 1 and i <= 2)      # lượt 1 hỏng 20% > trần 5%
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        ok("lượt có >5% hỏng hạ tầng -> TỪ CHỐI công bố số (exit 1)", DD.main(["--thu-muc", dd2]) == 1)

        dd3 = os.path.join(td, "dor3"); os.makedirs(dd3)
        shutil.copy(os.path.join(HERE, "battery_results.jsonl"), os.path.join(dd3, "run01.jsonl"))
        shutil.copy(os.path.join(HERE, "battery_results_25flash.jsonl"), os.path.join(dd3, "run02.jsonl"))
        ok("file bản CŨ (không có hop_le/định danh) -> TỪ CHỐI đo, không im lặng ra số",
           DD.main(["--thu-muc", dd3]) == 1)
        ok("1 lượt thôi -> từ chối (cần ≥2 để so)", DD.main(["--thu-muc", dd2, "--luot", "1"]) == 1)

        # ⚠ Ca này ban đầu tôi viết SAI: dựng A,B,A,B rồi đòi headline N=2 phải BẰNG headline N=4.
        # Tính tay thì code ĐÚNG còn kỳ vọng SAI — nhân đôi lượt đẻ thêm 2 cặp GIỐNG HỆT (0%), nên
        # trung bình 6 cặp = (4×33,3 + 2×0)/6 = 22,2%. "Bất biến theo N" nói về việc thêm lượt ĐỘC
        # LẬP từ cùng một hệ, KHÔNG phải nhân bản lượt cũ. Thứ ĐÁNG khoá là LUẬT GỘP:
        # headline = TRUNG BÌNH các cặp (không phải cặp tệ nhất — cái đó luôn xấu đi khi N tăng).
        print("\n[D.6] LUẬT GỘP: headline = TRUNG BÌNH mọi cặp, KHÔNG phải cặp tệ nhất")
        dd4 = os.path.join(td, "dor4"); os.makedirs(dd4)
        A = ["Cao 3,5 m", "Rộng 2,2 m", "Dài 7,7 m"]
        B = ["Cao 3,5 m", "Rộng 9,9 m", "Dài 7,7 m"]
        for n, ans in ((1, A), (2, B), (3, A), (4, B)):
            with open(os.path.join(dd4, "run%02d.jsonl" % n), "w", encoding="utf-8") as f:
                for i, a in enumerate(ans, 1):
                    r = dict(mau); r["id"] = i; r["answer"] = a
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")

        def bat(args):
            _o = sys.stdout
            sys.stdout = io.StringIO()
            try:
                DD.main(args); return sys.stdout.getvalue()
            finally:
                sys.stdout = _o

        def lay(t, khoa):
            for l in t.splitlines():
                if khoa in l:
                    return l.split(":")[-1].strip()
            return None
        t4 = bat(["--thu-muc", dd4])
        t2 = bat(["--thu-muc", dd4, "--luot", "1,2"])
        # 6 cặp: 4 cặp A-B (1/3 mâu thuẫn) + 2 cặp giống hệt (0) -> (4*33,33+0+0)/6 = 22,2%
        ok("A,B,A,B: headline = trung bình 6 cặp = 22.2% (tính tay)", lay(t4, "MÂU THUẪN SỐ") == "22.2%",
           lay(t4, "MÂU THUẪN SỐ"))
        ok("A,B: headline = 33.3%", lay(t2, "MÂU THUẪN SỐ") == "33.3%", lay(t2, "MÂU THUẪN SỐ"))
        ok("cặp TỆ NHẤT được in RIÊNG và cao hơn headline (nên KHÔNG được dùng làm headline)",
           "33.3%" in (lay(t4, "cặp TỆ NHẤT") or ""), lay(t4, "cặp TỆ NHẤT"))
        ok("cặp tệ nhất luôn in kèm N (số này xấu đi khi N tăng)", "(N=4)" in t4)
    finally:
        RB.BATTERY, RB.RUNS_DIR, RB.META_DIR = _batt, _runs, _meta
        shutil.rmtree(td, ignore_errors=True)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
