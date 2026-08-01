# -*- coding: utf-8 -*-
"""E2(b) — tool #35 doc_chu_trang_in: đọc chữ trên TRANG IN (paperspace). Tất định, offline.

VÌ SAO CÓ TOOL NÀY — quét ĐỦ 95/98 file .dxf (2026-08-01, lần đầu không bỏ file lớn):
  · 2.721 chuỗi CHỈ tồn tại trên trang in, ở 24/95 file. Hôm nay MỌI tool đều mù, và máy trả
    "không có" bằng giọng chắc chắn -> đúng loại THẤT BẠI IM LẶNG dự án đã cấm.
  · NHƯNG chỉ 10/2.721 chuỗi mang GIÁ TRỊ ĐO, và 9/10 nằm trong rachmop.dxf (đã có trong battery).
    Ngoài rachmop, toàn corpus còn ĐÚNG 1 chuỗi: 'd315-HDPE-l421m-I=0.33%'.
    => Tool này KHÔNG giúp bóc khối lượng. Giá trị là TIÊU ĐỀ / DANH MỤC / KHUNG TÊN.
  · File 202MB tên '...-trangin-chiHoa.dxf' — thứ hai vòng nghiên cứu trước đều CHỜ — đo ra
    **0 chuỗi chỉ-ở-trang-in**. Điều kiện tiên quyết cũ đuổi theo chỗ trống.
  · File đóng góp nhiều nhất (XR-KHAO SAT TKCS, 1.517 chuỗi = 56%) có 46,3% là LƯỚI TOẠ ĐỘ
    ('581000','581200'…) -> trần mặc định phải THẤP.

⛔ ĐIỀU KIỆN SỐNG CÒN: tool PHẢI nằm trong tuple loại-trừ rổ neo ở mcp_bridge. KHÔNG phải phòng xa —
   đo LIVE trên file thật: nếu không loại, tool bơm DÃY ÂM LIỀN -1,0 … -10,0 vào rổ neo, sinh THUẦN
   từ SỐ TỜ ('… LƯU VỰC TB.6 -7/10'). Dãy đó bảo lãnh cho CAO ĐỘ ÂM TRÒN BỊA (-2,0m / -5,0m) =
   đúng lớp lỗi id135 mà dự án tốn nhiều công mới đóng.

Chạy: python tests/test_trang_in.py
"""
import os, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
os.environ.setdefault("READFILE_MAX_MB", "300")

import ezdxf                       # noqa: E402
import tools_core as tc            # noqa: E402
import mcp_bridge as mb            # noqa: E402

PASS = FAIL = 0
_TMP = []


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def _dung(model_texts, paper_texts, ten_lay="IN"):
    """SYNTHETIC tất định. ezdxf.new() KHÔNG setup=True (setup tạo kiểu dáng mang hệ số 100)."""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    for i, s in enumerate(model_texts):
        msp.add_text(s, dxfattribs={"layer": "GHICHU", "insert": (0, i * 10)})
    psp = doc.layouts.new(ten_lay)
    for i, s in enumerate(paper_texts):
        psp.add_text(s, dxfattribs={"layer": "KHUNGTEN", "insert": (0, i * 10)})
    fd, path = tempfile.mkstemp(suffix=".dxf"); os.close(fd)
    doc.saveas(path); _TMP.append(path)
    return tc.Drawing(path)


def main():
    print("[E2b] tool #35 doc_chu_trang_in — đọc chữ trang in, KHÔNG bơm rổ neo")

    MODEL = ["MAT BANG TANG 1", "COT C1 300x300"]
    PAPER = ["BANG THONG KE KHOI LUONG CONG DICH VU",
             "MẶT BẰNG TỔNG THỂ TUYẾN CỐNG DỊCH VỤ LƯU VỰC TB.6 -7/10",
             "TL 1:150", "581000", "MAT BANG TANG 1"]      # chuỗi cuối TRÙNG modelspace

    # ── [T1] ĐỌC ĐƯỢC vùng mà tim_kiem mù ────────────────────────────────────────────────────
    print("\n-- [T1] đọc được vùng tim_kiem mù --")
    d = _dung(MODEL, PAPER)
    r = d.doc_chu_trang_in(tu_khoa="lưu vực")
    _emit("T1a: doc_chu_trang_in('lưu vực') CÓ kết quả", r["co_ket_qua"], str(r)[:120])
    _emit("T1b: cùng từ khoá thì tim_kiem = 0 (chứng minh đây là vùng mù)",
          d.tim_kiem(tu_khoa="lưu vực")["so_ket_qua"] == 0)
    _emit("T1c: trả đúng TÊN TRANG in", any(k.get("trang") == "IN" for k in r["ket_qua"]), str(r["ket_qua"])[:120])
    _emit("T1d: trả HANDLE thật", all(k.get("handle") for k in r["ket_qua"]))

    # ── [T2] KHÔNG trả lại chuỗi đã đọc được ở modelspace ────────────────────────────────────
    print("\n-- [T2] không trả lại chuỗi modelspace (tránh đếm trùng + bơm neo cửa hai) --")
    r2 = d.doc_chu_trang_in(tu_khoa="mat bang tang")
    _emit("T2a: chuỗi TRÙNG modelspace KHÔNG được trả lại", not r2["co_ket_qua"], str(r2["ket_qua"])[:120])
    _emit("T2b: chuỗi đó VẪN tìm được bằng tim_kiem (không mất gì)",
          d.tim_kiem(tu_khoa="mat bang tang")["so_ket_qua"] >= 1)

    # ── [T3] ⛔ RỔ NEO — ca quan trọng nhất của lát này ───────────────────────────────────────
    print("\n-- [T3] rổ neo: số trang in KHÔNG được làm bằng chứng --")
    src_b = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    _emit("T3a: 'doc_chu_trang_in' NẰM TRONG tuple loại-trừ rổ neo", '"doc_chu_trang_in"' in src_b)
    # Chứng minh việc loại trừ là CẦN THIẾT chứ không thừa: nếu KHÔNG loại, tool bơm ra số gì?
    r3 = d.doc_chu_trang_in(tu_khoa="")
    so = mb._collect_numbers(mb._strip_neo(r3))
    am = sorted(x for x in so if x < 0)
    _emit("T3b: nếu KHÔNG loại thì tool BƠM SỐ ÂM vào rổ (lý do phải loại)", len(am) >= 1, str(sorted(so))[:110])
    _emit("T3c: số âm đó đến từ SỐ TỜ '-7/10' chứ không phải cao độ", -7.0 in am, str(am))

    # ── [T4] ghi_chu phải CẢNH BÁO đúng 3 điều ───────────────────────────────────────────────
    print("\n-- [T4] ghi_chu cảnh báo --")
    g = r3.get("ghi_chu") or ""
    _emit("T4a: cảnh báo KHÔNG lấy số làm khối lượng", "không lấy số" in g.lower() or "không được lấy" in g.lower(), g[:90])
    _emit("T4b: cảnh báo tiêu đề bảng KHÔNG suy ra thân bảng", "thân bảng" in g.lower(), g[:90])
    _emit("T4c: nêu rõ đây là chữ trang in", "trang in" in g.lower())

    # ── [T5] fail-open + biên ────────────────────────────────────────────────────────────────
    print("\n-- [T5] fail-open + biên --")
    d0 = _dung(["CHI CO MODELSPACE"], [])
    r0 = d0.doc_chu_trang_in(tu_khoa="bat ky")
    _emit("T5a: bản vẽ KHÔNG có trang in -> rỗng, KHÔNG ném", r0["co_ket_qua"] is False)
    _emit("T5b: gioi_han âm -> không vỡ", isinstance(d.doc_chu_trang_in(tu_khoa="", gioi_han=-5), dict))
    _emit("T5c: gioi_han khổng lồ bị kẹp (trần 40)", len(d.doc_chu_trang_in(tu_khoa="", gioi_han=99999)["ket_qua"]) <= 40)
    goc = tc.to_unicode
    try:
        d2 = _dung(MODEL, PAPER)
        tc.to_unicode = lambda s: (_ for _ in ()).throw(RuntimeError("bom"))
        d2._tik = None
        _emit("T5d: to_unicode NÉM -> trả rỗng, KHÔNG crash", d2.doc_chu_trang_in(tu_khoa="x")["co_ket_qua"] is False)
    finally:
        tc.to_unicode = goc

    # ── [T6] khớp MÙ DẤU bị chặn (cùng luật tool #34) ────────────────────────────────────────
    print("\n-- [T6] không khớp mù dấu --")
    d3 = _dung([], ["CỬA ĐI CHÍNH D1", "CỦA NHÀ THẦU"])
    _emit("T6a: hỏi 'cửa' KHÔNG hút 'của'",
          all("CỦA" not in k["text"] for k in d3.doc_chu_trang_in(tu_khoa="cửa")["ket_qua"]))

    # ── [T7] source-guard: KHÔNG nạp vào self.texts ──────────────────────────────────────────
    print("\n-- [T7] source-guard --")
    _emit("T7a: chữ trang in KHÔNG vào self.texts (không đổi index/rổ neo toàn hệ)",
          all("LƯU VỰC" not in (t.get("vn") or "") for t in d.texts))
    src_t = open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read()
    _emit("T7b: kho trang in dựng LƯỜI (chỉ khi tool được gọi)", "_tik" in src_t and "def _trang_in_kho" in src_t)
    n_tool = open(os.path.join(ROOT, "mcp_server.py"), encoding="utf-8").read().count("@mcp.tool")
    _emit("T7c: đã đăng ký thành tool MCP (>=35)", n_tool >= 35, str(n_tool))

    for p in _TMP:
        try: os.remove(p)
        except Exception: pass
    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
