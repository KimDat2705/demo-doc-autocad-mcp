# -*- coding: utf-8 -*-
"""A3 — NEO-THEO-TRÍCH-DẪN cho chữ TRANG IN: lấy lại câu ĐÚNG mà guard xoá oan. Tất định, offline.

BÀI TOÁN (đo bằng CHÍNH `Drawing._trang_in_kho`: 18 file / 2.180 lượt / 621 chuỗi riêng biệt):
  20/621 = 3,2% chuỗi (34/2.180 = 1,6% lượt) khi TRÍCH NGUYÊN VĂN đủ kích `do_luong` -> rổ neo rỗng
  vì CHÍNH SÁCH -> REFUSE -> A2 hạ xuống KHONG_TRA_DUOC. Đọc tay 20/20: 0 lưới toạ độ · 0 số tờ ·
  0 tỉ lệ · 0 mã hiệu (chúng cho do_luong=[] nên guard THOÁT SỚM, không bao giờ vào tập này).
  Tập bị giết: 7 kích thước THẬT · 6 danh tính công trình · 7 rác.

⛔ BA QUYẾT ĐỊNH THIẾT KẾ, mỗi cái có ca test riêng vì mỗi cái đã ĐO ra hỏng ở bản ngây thơ:
 · `all(...)` chứ KHÔNG `any(...)` — bản ANY để lọt 10-12/12 ca ĂN THEO (trích đúng 1 chuỗi rồi
   chở thêm số bịa; ANY-GROUNDED bảo lãnh cả câu).                                  -> ca [G1]
 · gộp vùng RIÊNG TỪNG CHUỖI — bản gộp-chung để lọt ca KHÂU VÁ: ghép đuôi chuỗi A ('…trải mái m=3')
   với đầu chuỗi B ('1.5m - L=394,5m') ĐẺ RA số MỚI 31.5 không có ở đâu cả.          -> ca [G2]
 · số của A3 KHÔNG vào `tool_numbers` — không để lại "giấy phép" cho lượt SAU.       -> ca [G6]

⛔ KHÔNG bỏ tool #35 khỏi tuple loại-trừ: MỘT lượt doc_chu_trang_in(15) trên rachmop bơm 10 số vào
   rổ neo, TRONG ĐÓ -7.0 (sinh thuần từ SỐ TỜ '-7/10') = đúng nguyên liệu lớp lỗi id135.

📌 RỦI RO TỒN DƯ (không chặn hết được): model trích ĐÚNG nhưng GÁN SAI NGHĨA — 'Tel: 0220.3855952'
   -> "chiều dài tuyến 220,38 m". 4/17 số cấp phép được thuộc loại này. Cờ CO_TRANG_IN là thứ duy
   nhất giảm nhẹ.

Chạy: python tests/test_a3_trich_trang_in.py
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import mcp_bridge as B   # noqa: E402

PASS = FAIL = 0
R = B.REFUSE_MESSAGE
KTD = getattr(B, "KHONG_TRA_DUOC", "<chua-va-A2>")
CO = getattr(B, "CO_TRANG_IN", "<chua-va-A3>")


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


class _FC:
    def __init__(self, name, args): self.name, self.args = name, args
class _Part:
    def __init__(self, text=None, function_call=None, thought=False):
        self.text, self.function_call, self.thought = text, function_call, thought
class _Content:
    def __init__(self, parts, role="model"): self.parts, self.role = parts, role
class _Cand:
    def __init__(self, parts, fr=None): self.content, self.finish_reason = _Content(parts), fr
class _Resp:
    def __init__(self, parts): self.candidates = [_Cand(parts)]
class _FakeTool:
    def __init__(self, name): self.name = name
class _Bridge:
    def __init__(self, ket): self.ket, self.tools, self.n_call = ket, [_FakeTool(n) for n in ket], 0
    def call(self, name, args):
        self.n_call += 1
        return self.ket.get(name, {})


def kq_trangin(*chuoi):
    """Kết quả tool #35 đúng hình dạng thật (có handle -> mới sinh evidence)."""
    return {"co_ket_qua": True, "bi_cat": False,
            "ket_qua": [{"handle": "A%03d" % i, "trang": "A1", "text": s} for i, s in enumerate(chuoi)]}


def e2e(ket, answer_text):
    parts = [_Part(function_call=_FC(n, {"tu_khoa": "x"})) for n in ket]
    script = [_Resp(parts), _Resp([_Part(text=answer_text)])]
    st = {"n": 0}
    def fake_gen(client, contents, cfg, mstate):
        r = script[min(st["n"], len(script) - 1)]; st["n"] += 1
        return r
    _sc, _sg, _st = B._get_client, B._gen_fallback, B.gemini_tools
    B._get_client = lambda: object(); B._gen_fallback = fake_gen; B.gemini_tools = lambda t: []
    try:
        return B.tra_loi_ai(_Bridge(ket), "câu hỏi test")["answer"]
    finally:
        B._get_client, B._gen_fallback, B.gemini_tools = _sc, _sg, _st


S_DAI = "Hoàn trả đường dân sinh - B=1.5m - L=394,5m"
S_TANG = "DANH MỤC BẢN VẼ PHẦN KẾT CẤU ĐƠN NGUYÊN 2: 3 TẦNG 9 PHÒNG"
S_THAM = "Thảm đá dày 30cm trải mái m=3 kết hợp tự nhiên"


def main():
    print("[A3] neo-theo-trích-dẫn: cứu câu ĐÚNG trích nguyên văn chữ trang in")

    # ══ [D] PHÂN BIỆT ĐƯỢC — phải ĐỎ nếu gỡ A3 ═══════════════════════════════════════════════
    print("\n-- [D] phân biệt được --")
    a = e2e({"doc_chu_trang_in": kq_trangin(S_DAI)}, "Bản vẽ ghi: %s." % S_DAI)
    ok("D1: câu TRÍCH NGUYÊN VĂN không còn bị xoá", a not in (R, KTD), a[:70])
    ok("D2: và có gắn cờ CO_TRANG_IN", CO in a, a[:70])
    b = e2e({"doc_chu_trang_in": kq_trangin(S_TANG)}, "Đây là %s." % S_TANG)
    ok("D3: ca DANH TÍNH công trình (số ĐẾM) cũng được cứu", CO in b, b[:70])
    ok("D4: hàm _a3_trich_trang_in tồn tại", hasattr(B, "_a3_trich_trang_in"))

    # ══ [G] CHỐNG HỒI QUY — mỗi ca khoá một quyết định thiết kế đã ĐO ra hỏng ở bản ngây thơ ══
    print("\n-- [G] chống hồi quy (all/gộp-riêng/scope) --")
    c = e2e({"doc_chu_trang_in": kq_trangin(S_DAI)},
            "Bản vẽ ghi: %s. Cao độ đáy là -13.7 m." % S_DAI)
    ok("G1: MỘT số nằm NGOÀI đoạn trích -> KHÔNG cứu (all, không any)", c in (R, KTD), c[:70])
    d = e2e({"doc_chu_trang_in": kq_trangin(S_THAM, S_DAI)}, "Bề rộng là 31.5m.")
    ok("G2: KHÂU VÁ hai chuỗi đẻ số MỚI (31.5) -> KHÔNG cứu (gộp RIÊNG từng chuỗi)",
       d in (R, KTD), d[:70])
    e = e2e({"tra_ky_hieu": {"ky_hieu": "Ø", "nghia": "đường kính"}},
            "Bản vẽ ghi: %s." % S_DAI)
    ok("G3: tool KHÁC (tra_ky_hieu) không được làm nguồn trích dẫn", e in (R, KTD), e[:70])
    f = e2e({"doc_chu_trang_in": kq_trangin(S_DAI), "thong_ke_thep": {"tong_kg": 25752.6}},
            "Tổng khối lượng thép là 25752.6 kg.")
    ok("G4: rổ neo KHÔNG rỗng -> A3 ngoài phạm vi, guard xử như cũ", CO not in f, f[:70])
    g = e2e({"tim_kiem": {}}, "Cao độ thấp nhất là -10m.")
    ok("G5: id135 gốc -> VẪN từ chối", g == R, g[:70])
    # ⚠ Danh từ phải NẰM TRONG `_DEM_TU` thì guard mới kích. Bản nháp đầu dùng "5 cống hộp" ->
    # `do_luong=[]` ("cống" KHÔNG có trong danh sách) -> guard THOÁT SỚM -> câu chưa bao giờ bị chặn
    # -> ca ĐỎ vì assert sai, KHÔNG phải vì code sai. "bộ" thì CÓ trong danh sách.
    h = e2e({"doc_chu_trang_in": kq_trangin("GIA CỐ BỜ TRÁI")}, "Bản vẽ có 5 bộ cửa.")
    ok("G6: số KHÔNG có trong chuỗi tool trả -> KHÔNG cứu", h in (R, KTD), h[:70])
    h2 = e2e({"doc_chu_trang_in": kq_trangin("GIA CỐ BỜ TRÁI")}, "Bản vẽ có 5 cống hộp.")
    ok("G6b: câu KHÔNG kích guard (danh từ ngoài _DEM_TU) -> A3 cũng không gắn cờ",
       CO not in h2 and h2 not in (R, KTD), h2[:70])
    i = e2e({"doc_chu_trang_in": kq_trangin("+1.63")}, "Cao độ là +1.63.")
    ok("G7: chuỗi NGẮN hơn ngưỡng K -> KHÔNG cứu (giới hạn cố ý)", i in (R, KTD), i[:70])
    j = e2e({"doc_chu_trang_in": kq_trangin(S_DAI)}, "Bản vẽ có nội dung hoàn trả đường dân sinh.")
    ok("G8: câu KHÔNG có số -> guard không kích, A3 cũng không gắn cờ", CO not in j, j[:70])

    # ══ [M] BẤT BIẾN bộ trích NHÂN BẢN — chỗ nguy hiểm nhất của bản vá ═══════════════════════
    print("\n-- [M] bất biến: _a3_do_luong_vitri PHẢI khớp _answer_numbers --")
    mau = [S_DAI, S_TANG, S_THAM, "Phạm vi vùng có dừa nước tổng diện tích S= 1740.4m2",
           "d315-HDPE-l421m-I=0.33%", "Nhà mái bằng 1 tầng, 2 tầng", "581000", "TL 1:150",
           "Đ-0.01", "GIA CỐ BỜ TRÁI", "Tổng 1384.83 kg gồm 9 mục", "Diện tích sàn 43 m2",
           "Có 12 bộ cửa D1", "Cao độ -13.7 m", "MẶT CẮT 4-4 tại cọc AL1.13"]
    lech = [s for s in mau
            if sorted(B._answer_numbers(s)[1]) != sorted(v for v, _i, _j in B._a3_do_luong_vitri(s))]
    ok("M1: 0 lệch trên mẫu (nếu ai sửa _MAHIEU_RES/_DEM_NUM_RE mà quên -> ĐỎ)", not lech, str(lech[:3]))
    co_so = sum(1 for s in mau if B._answer_numbers(s)[1])
    ok("M2: đối chứng — mẫu CÓ chuỗi sinh số (ca M1 không tautology)", co_so >= 6, str(co_so))
    ok("M3: cờ CO_TRANG_IN KHÔNG chứa chữ số", not any(ch.isdigit() for ch in CO), CO)
    ok("M4: chỉ số trả về khớp text GỐC (kiểm bằng cắt lát)",
       all(S_DAI[i:j].strip().replace(",", ".").rstrip(".") in ("1.5", "394.5")
           for _v, i, j in B._a3_do_luong_vitri(S_DAI)),
       str([(v, S_DAI[i:j]) for v, i, j in B._a3_do_luong_vitri(S_DAI)]))

    # ══ [S] SOURCE-GUARD ════════════════════════════════════════════════════════════════════
    print("\n-- [S] source-guard --")
    src = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    ok("S1: A3 cắm ở CẢ HAI call-site", src.count("_a3_trich_trang_in(_goc,") == 2,
       str(src.count("_a3_trich_trang_in(_goc,")))
    ok("S2: A3 đặt TRƯỚC A2 (nếu ngược, A2 ghi đè câu vừa cứu)",
       src.index("_a3_trich_trang_in(_goc,") < src.index("_a2_khong_tra_duoc(_goc,"))
    ok("S3: tool #35 VẪN nằm trong tuple loại-trừ rổ neo (A3 không thay việc đó)",
       '"doc_chu_trang_in"' in src.split("fc.name not in (")[1][:200])
    ok("S4: dùng all(...) — có vòng lặp trả sớm khi MỘT số nằm ngoài vùng trích",
       "return guarded          # có MỘT số nằm ngoài" in src)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
