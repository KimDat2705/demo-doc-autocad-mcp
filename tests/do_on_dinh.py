# -*- coding: utf-8 -*-
"""
ĐO ĐỘ ỔN ĐỊNH giữa N lượt chạy `run_battery.py` (chỉ ĐỌC, không sửa gì, không gọi API).

    python tests/do_on_dinh.py                     # đọc mọi lượt trong tests/battery_runs/
    python tests/do_on_dinh.py --luot 1,2,3        # chỉ 3 lượt này

VÌ SAO PHẢI CẨN THẬN VỚI CON SỐ NÓ IN RA — đã đo trước khi viết, trên 2 cặp lượt LỊCH SỬ thật:

  · So NGUYÊN VĂN là chỉ số CHẾT: hai lượt cùng model cách nhau 3 tuần giống nhau **3,5%**;
    khác model **0,0%**. Nó luôn nói "khác" nên không mang thông tin. -> chỉ để tham khảo.
  · So bằng LIST khác so bằng SET: `_answer_numbers` trả LIST (có thứ tự, có lặp). So thẳng `==`
    cho 43,4%; so bằng `set()` cho 53,0% — chênh 10 điểm THUẦN DO lỗi so sánh. -> luôn dùng set.
  · **29,3%** số cặp câu KHÔNG có số đo-lường ở CẢ HAI lượt (câu từ chối / câu văn xuôi). Chúng
    "giống nhau" một cách TẦM THƯỜNG. Gộp vào mẫu số thì gần một phần ba con số đẹp là do câu
    không có gì để lệch. -> rổ `khong_so_moi_luot` bị LOẠI khỏi mẫu, và luôn in ra để thấy.

BA SỐ, KHÔNG PHẢI MỘT. Ép một con số duy nhất là cách chắc chắn nhất để tự lừa mình:
  (1) MÂU THUẪN SỐ      — hai lượt cùng nói số, nhưng số đá nhau.
  (2) TRẢ LỜI vs TỪ CHỐI — lượt này ra số, lượt kia bảo "không có". Về mặt sản phẩm đây là hỏng
      NẶNG NHẤT (đối tác thấy máy lúc biết lúc không) nên KHÔNG được gộp chìm vào (1).
  (3) BẤT ỔN NGƯỜI DÙNG THẤY = (1) + (2).

Trung bình trên MỌI CẶP lượt C(N,2) — để con số KHÔNG tự trôi khi tăng N (chỉ số "tệ nhất qua mọi
cặp" thì luôn xấu đi khi N tăng, nên nó chỉ được in ở dòng chẩn đoán, kèm N).

KHÔNG có ngưỡng "đạt/không đạt" — đặt ngưỡng ở đây là tự sinh ra kết luận. Exit != 0 chỉ khi
PHÉP ĐO không hợp lệ (trộn phiên bản, thiếu định danh, quá nhiều lỗi hạ tầng).
"""
import os, sys, io, json, glob, argparse, itertools, collections, re

os.environ.setdefault("READFILE_MAX_MB", "300")
if (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "") != "utf8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge

RUNS_DIR = os.path.join(HERE, "battery_runs")
TRAN_HA_TANG = 0.05        # >5% câu hỏng hạ tầng trong 1 lượt -> KHÔNG công bố số
KHOA_DINH_DANH = ("prompt_hash8", "kb_hash8", "code_hash8", "battery_sha12", "model")

# id ảnh/Excel do CHÍNH hệ sinh ('hl_1a2b3c4d5e', 'th_...') mang chữ số ngẫu nhiên -> nếu để nguyên
# thì hai lượt trả lời y hệt vẫn bị tính là lệch. Đây là nhiễu của PHÉP ĐO, không phải của hệ.
_UUID_RE = re.compile(r"\b(?:hl|th)_[0-9a-f]{6,}\b")


def so_do_luong(text):
    """Tập số ĐO-LƯỜNG trong câu trả lời. Dùng CHÍNH bộ tách của hàng rào chống bịa
    (mcp_bridge._answer_numbers) — cố tình KHÔNG viết bộ tách thứ hai: hai bộ tách lệch nhau thì
    con số đo được sẽ không còn nói về cái mà hàng rào nhìn thấy."""
    return set(mcp_bridge._answer_numbers(_UUID_RE.sub(" ", text or ""))[1])


def ro(da, db):
    """Xếp một cặp câu trả lời vào 1 trong 5 rổ."""
    if not da and not db:
        return "khong_so_moi_luot"
    if da == db:
        return "dong_nhat"
    if not da or not db:
        return "mot_ben_rong"
    if da <= db or db <= da:
        return "bao_ham"
    return "mau_thuan"


def doc_luot_file(path):
    """Đọc 1 file lượt -> {id: bản ghi CUỐI CÙNG}. Bản ghi sau ghi đè bản ghi trước cùng id
    (đó là các lần hỏi lại của chính lượt đó)."""
    d = {}
    for l in open(path, encoding="utf-8"):
        if not l.strip():
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        d[r.get("id")] = r
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description="Đo độ ổn định giữa các lượt chạy battery.")
    ap.add_argument("--luot", default="", help="danh sách số lượt, vd 1,2,3 (mặc định: tất cả)")
    ap.add_argument("--thu-muc", default=RUNS_DIR)
    ap.add_argument("--top", type=int, default=12, help="in bao nhiêu câu bất ổn nhất")
    a = ap.parse_args(argv)      # xem ghi chú ở run_battery.py — KHÔNG được thay bằng []

    paths = sorted(glob.glob(os.path.join(a.thu_muc, "run[0-9][0-9].jsonl")))
    if a.luot.strip():
        giu = {int(x) for x in a.luot.split(",") if x.strip().isdigit()}
        paths = [p for p in paths if int(os.path.basename(p)[3:5]) in giu]
    if len(paths) < 2:
        print("DỪNG: cần ít nhất 2 lượt để đo ổn định (tìm thấy %d trong %s)." % (len(paths), a.thu_muc))
        return 1

    luot = [(os.path.basename(p), doc_luot_file(p)) for p in paths]
    N = len(luot)

    # --- cổng A: mọi bản ghi phải có định danh, và định danh phải ĐỒNG NHẤT ---
    thieu = [ten for ten, d in luot if not d or not all("hop_le" in r for r in d.values())]
    if thieu:
        print("DỪNG: các file sau không có trường `hop_le`/định danh — sinh bởi bản run_battery CŨ "
              "(trước 1.06), không đo được: %s" % ", ".join(thieu))
        return 1
    dinh_danh = {}
    for ten, d in luot:
        for k in KHOA_DINH_DANH:
            dinh_danh.setdefault(k, set()).update(str(r.get(k)) for r in d.values())
    lech = [k for k, v in dinh_danh.items() if len(v) > 1]
    if lech:
        print("DỪNG: các lượt KHÔNG cùng một phiên bản — so sánh chúng là phép đo vô nghĩa.")
        for k in lech:
            print("   %-14s có %d giá trị: %s" % (k, len(dinh_danh[k]), ", ".join(sorted(dinh_danh[k]))[:100]))
        return 1

    # --- cổng B: lỗi hạ tầng ---
    print("=" * 78)
    print("ĐỘ PHỦ — %d lượt, model %s, prompt %s, code %s"
          % (N, list(dinh_danh["model"])[0], list(dinh_danh["prompt_hash8"])[0],
             list(dinh_danh["code_hash8"])[0]))
    qua_tran = []
    for ten, d in luot:
        n = len(d)
        hong = sum(1 for r in d.values() if not r.get("hop_le"))
        print("   %-16s %3d câu · %3d hỏng hạ tầng (%.1f%%)" % (ten, n, hong, 100.0 * hong / max(n, 1)))
        if n and hong / n > TRAN_HA_TANG:
            qua_tran.append(ten)
    chung = set.intersection(*[set(d) for _, d in luot])
    print("   id chung cả %d lượt: %d" % (N, len(chung)))
    if qua_tran:
        print("\nDỪNG: %s vượt trần %.0f%% câu hỏng hạ tầng — chạy `--tiep` cho hết rồi hãy đo. "
              "Loại bỏ câu hỏng KHÔNG ngẫu nhiên (câu nặng dễ 503 hơn) nên số sẽ lệch."
              % (", ".join(qua_tran), 100 * TRAN_HA_TANG))
        return 1

    # chỉ đo trên câu HỢP LỆ ở MỌI lượt
    dung = sorted(i for i in chung if all(d[i].get("hop_le") for _, d in luot))
    print("   id hợp lệ ở MỌI lượt (mẫu đo): %d" % len(dung))
    if not dung:
        print("DỪNG: không còn câu nào hợp lệ ở mọi lượt.")
        return 1

    # --- đếm rổ, trung bình trên mọi cặp ---
    cap = list(itertools.combinations(range(N), 2))
    tong = collections.Counter()
    per_cap, per_cau = [], collections.Counter()
    theo_loai = collections.defaultdict(collections.Counter)
    for x, y in cap:
        dx, dy = luot[x][1], luot[y][1]
        c = collections.Counter()
        for i in dung:
            b = ro(so_do_luong(dx[i]["answer"]), so_do_luong(dy[i]["answer"]))
            c[b] += 1
            tong[b] += 1
            theo_loai[dx[i].get("loai")][b] += 1
            if b in ("mau_thuan", "mot_ben_rong"):
                per_cau[i] += 1
        mau = sum(v for k, v in c.items() if k != "khong_so_moi_luot")
        per_cap.append((luot[x][0], luot[y][0], c, mau))

    def pct(k):
        mau = sum(v for kk, v in tong.items() if kk != "khong_so_moi_luot")
        return 100.0 * tong[k] / mau if mau else 0.0

    mau_tb = sum(v for k, v in tong.items() if k != "khong_so_moi_luot") / len(cap)
    print("\n" + "=" * 78)
    print("5 RỔ (cộng dồn %d cặp lượt, số tuyệt đối)" % len(cap))
    for k in ("khong_so_moi_luot", "dong_nhat", "bao_ham", "mot_ben_rong", "mau_thuan"):
        print("   %-20s %5d" % (k, tong[k]))
    print("   %-20s %5.0f  <- MẪU SỐ (đã loại rổ 1)" % ("mau_so_moi_cap", mau_tb))

    print("\n" + "=" * 78)
    print("BA SỐ (trung bình trên %d cặp lượt — bất biến theo N)" % len(cap))
    print("   (1) MÂU THUẪN SỐ        : %5.1f%%" % pct("mau_thuan"))
    print("   (2) TRẢ LỜI vs TỪ CHỐI  : %5.1f%%" % pct("mot_ben_rong"))
    print("   (3) BẤT ỔN NGƯỜI DÙNG THẤY = (1)+(2) : %5.1f%%" % (pct("mau_thuan") + pct("mot_ben_rong")))
    print("   [chẩn đoán] bao hàm (chi tiết hơn/kém, không đá nhau): %5.1f%%" % pct("bao_ham"))
    xau = max(((100.0 * c["mau_thuan"] / m if m else 0), a1, b1) for a1, b1, c, m in per_cap)
    print("   [chẩn đoán] cặp TỆ NHẤT (N=%d): %.1f%% giữa %s và %s" % (N, xau[0], xau[1], xau[2]))

    print("\n" + "=" * 78)
    print("THEO NHÓM CÂU (mix bộ câu đổi thì số tổng cũng đổi — nên luôn xem bảng này)")
    print("   %-24s %6s %6s %6s" % ("loai", "n", "mthuan", "1benR"))
    vi_mo = []
    for lo in sorted(theo_loai):
        c = theo_loai[lo]
        m = sum(v for k, v in c.items() if k != "khong_so_moi_luot")
        p = 100.0 * c["mau_thuan"] / m if m else 0.0
        q = 100.0 * c["mot_ben_rong"] / m if m else 0.0
        vi_mo.append(p)
        print("   %-24s %6.0f %5.1f%% %5.1f%%" % (lo, m / len(cap), p, q))
    print("   %-24s %6s %5.1f%%  <- macro-average (ít nhạy với mix bộ câu)"
          % ("(trung bình %d nhóm)" % len(vi_mo), "", sum(vi_mo) / len(vi_mo) if vi_mo else 0))

    print("\n" + "=" * 78)
    print("TỈ LỆ TỪ CHỐI TỪNG LƯỢT (số ở trên GIẢM khi hệ trả lời ÍT đi — phải xem cùng nhau)")
    for ten, d in luot:
        khong_so = sum(1 for i in dung if not so_do_luong(d[i]["answer"]))
        print("   %-16s %3d/%d câu không nêu số đo-lường (%.1f%%)"
              % (ten, khong_so, len(dung), 100.0 * khong_so / len(dung)))

    if per_cau:
        print("\n" + "=" * 78)
        print("TOP %d CÂU BẤT ỔN NHẤT (số cặp lượt bất đồng / %d cặp)" % (a.top, len(cap)))
        for i, n in per_cau.most_common(a.top):
            r0 = luot[0][1][i]
            print("   id%-5s %-22s %d/%d | %s" % (i, (r0.get("loai") or "")[:22], n, len(cap),
                                                 (r0.get("cau_hoi") or "")[:44]))

    print("\n" + "=" * 78)
    print("ĐỌC SỐ NÀY CHO ĐÚNG:")
    print(" · Đây là ĐỘ ỔN ĐỊNH (chạy lại có ra như cũ không), KHÔNG phải ĐỘ ĐÚNG. Hai lượt cùng sai")
    print("   giống nhau vẫn cho 0% mâu thuẫn.")
    print(" · Số (1) GIẢM khi hệ trả lời ÍT đi — luôn đọc kèm bảng tỉ lệ từ chối ở trên.")
    print(" · Đo tại MỘT thứ tự câu hỏi CỐ ĐỊNH; 198 câu chạy tuần tự trong cùng một phiên nên trạng")
    print("   thái theo phiên có thể truyền từ câu trước sang câu sau. Đổi thứ tự chưa đo bao giờ.")
    print(" · Rổ `khong_so_moi_luot` (%d) ĐÃ bị loại khỏi mẫu — nếu tính vào, con số đẹp lên một cách"
          % tong["khong_so_moi_luot"])
    print("   vô nghĩa vì câu không có số thì không thể lệch.")
    print(" · Bộ tách số là bộ của hàng rào chống bịa, kể cả các hạn chế đã biết của nó (dấu ngăn")
    print("   nghìn kiểu VN). Hai lượt bị tách sai GIỐNG NHAU nên phần lớn triệt tiêu, nhưng không phải hết.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
