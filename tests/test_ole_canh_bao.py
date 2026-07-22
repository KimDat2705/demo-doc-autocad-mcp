# -*- coding: utf-8 -*-
"""BUG C (GĐ4) — LỘ đối tượng NHÚNG (OLE2FRAME = bảng Excel dán vào bản vẽ).
TẤT ĐỊNH, OFFLINE, KHÔNG tốn API.  Chạy:  python tests/test_ole_canh_bao.py

BỐI CẢNH: GĐ4 trên corpus 8 firm đo được 19/65 file có OLE. Ca nặng '4. Thong ke thep SUA.dwg' (CT-D):
cả bảng thống kê thép nằm trong 8 OLE -> engine đọc 0 thanh và trả 'bản vẽ KHÔNG có bảng thống kê thép',
trong khi file TÊN LÀ 'thống kê thép' => đối tác hiểu SAI. Vá = CHỈ LỘ cảnh báo, KHÔNG đổi số nào.

Kiểm: helper (không OLE -> None) · gắn cờ ADDITIVE (không OLE -> dict Y HỆT) · non-dict không vỡ ·
REAL CT-A KT (2 OLE) lộ cảnh báo + KC (0 OLE) KHÔNG đổi số (chống hồi quy) · thép/thép-hình/tổng-hợp
đều mang cảnh báo · luật prompt 8c tồn tại · guard grounding không bị cảnh báo làm hỏng."""
import os
import sys
import io

os.environ.setdefault("READFILE_MAX_MB", "500")
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import tools_core as tc

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
# Ten thu muc/file that giu NGOAI repo (gitignored) — xem corpus_local.example.py
try:
    from corpus_local import KT, KC   # KT: CO 2 OLE · KC: KHONG co OLE
except Exception:
    KT = KC = ""

PASS = FAIL = SKIP = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def skip(name):
    global SKIP
    SKIP += 1
    print("  [..] BO QUA %s (thieu fixture)" % name)


class _Fake:
    """Đối tượng tối thiểu — 2 helper chỉ đọc self.ole_nhung."""
    _canh_bao_nhung = tc.Drawing._canh_bao_nhung
    _gan_canh_bao_nhung = tc.Drawing._gan_canh_bao_nhung

    def __init__(self, ole):
        self.ole_nhung = ole


def main():
    print("[C1] _canh_bao_nhung — KHONG OLE thi IM (khong canh bao oan)")
    ok("ole_nhung=[] -> None", _Fake([])._canh_bao_nhung() is None)
    ok("thieu han attr ole_nhung -> None (khong vo)", tc.Drawing._canh_bao_nhung(object()) is None)

    print("[C2] _canh_bao_nhung — CO OLE thi LO du: so luong + handle + loi canh bao")
    cb = _Fake([{"handle": "A1", "layer": "L"}, {"handle": "B2", "layer": "L"}])._canh_bao_nhung()
    ok("so_doi_tuong_nhung = 2", cb["so_doi_tuong_nhung"] == 2, cb)
    ok("co handles de truy nguon", cb["handles"] == ["A1", "B2"], cb["handles"])
    ok("canh_bao noi 'KHONG doc duoc' + 'THIEU' (khong phai 'ban ve khong co')",
       "KHÔNG đọc được" in cb["canh_bao"] and "THIẾU" in cb["canh_bao"], cb["canh_bao"])

    print("[C3] _gan_canh_bao_nhung — ADDITIVE: khong OLE thi dict Y HET (backward-compat)")
    goc = {"co_bang_thong_ke": True, "tong_khoi_luong_kg": 123.4, "ghi_chu": "so THAT"}
    ra = _Fake([])._gan_canh_bao_nhung(dict(goc))
    ok("khong OLE -> dict KHONG doi 1 byte", ra == goc, ra)
    ra2 = _Fake([{"handle": "H", "layer": "L"}])._gan_canh_bao_nhung(dict(goc))
    ok("co OLE -> THEM key canh_bao_nhung", "canh_bao_nhung" in ra2)
    ok("co OLE -> so KHONG bi sua (123.4 giu nguyen)", ra2["tong_khoi_luong_kg"] == 123.4, ra2)
    ok("co OLE -> ghi_chu duoc NOI them (LLM chac chan thay)",
       ra2["ghi_chu"].startswith("so THAT") and "⚠" in ra2["ghi_chu"], ra2["ghi_chu"])
    ok("non-dict -> tra nguyen xi, KHONG vo", _Fake([{"handle": "H"}])._gan_canh_bao_nhung("abc") == "abc")

    print("[C3b] CA MOTIVATING (synthetic) — bang thep trong OLE. Thiet ke U3: OLE loai='excel' -> DOC DUOC")
    # Ca that '4. Thong ke thep SUA.dwg' = 8 OLE loai='excel' (probe U3). Native thep rong (nam trong OLE).
    class _FakeThep:
        _canh_bao_nhung = tc.Drawing._canh_bao_nhung
        _gan_canh_bao_nhung = tc.Drawing._gan_canh_bao_nhung
        thong_ke_thep = tc.Drawing.thong_ke_thep
        thong_ke_thep_hinh = tc.Drawing.thong_ke_thep_hinh
        doc_bang_nhung = tc.Drawing.doc_bang_nhung
        def __init__(self, ole):
            self.ole_nhung = ole
            self.thep = {"by_dk": {}}       # native thep rong (thep nam trong OLE)
            self.thep_hinh = {"by_show": {}}
    # (a) OLE DOC DUOC (loai='excel' + rows) — thiet ke moi
    ole_doc = [{"handle": "BC70%02X" % i, "layer": "0", "loai": "excel", "sheet": "Thep",
                "nrows": 3, "ncols": 2, "rows": [["STT", "KL thep"], [1, 581.7], [2, 1963.9]]} for i in range(8)]
    fk = _FakeThep(ole_doc)
    r = fk.thong_ke_thep()
    ok("native thep rong -> co_bang_thong_ke=False", r.get("co_bang_thong_ke") is False)
    cb = r.get("canh_bao_nhung") or {}
    ok("canh_bao_nhung: so_bang_doc_duoc=8 + so_doi_tuong=8 (KHONG 'ban ve khong co')",
       cb.get("so_bang_doc_duoc") == 8 and cb.get("so_doi_tuong_nhung") == 8, cb)
    ok("canh bao TRO doc_bang_nhung + noi KHONG tu cong (khong tu bia tong)",
       "doc_bang_nhung" in cb.get("canh_bao", "") and "TỔNG" in cb.get("canh_bao", ""))
    ok("ghi_chu co ⚠", "⚠" in (r.get("ghi_chu") or ""))
    bn = fk.doc_bang_nhung()
    ok("doc_bang_nhung: so_bang=8, moi bang co nguon 'ole:...'",
       bn["so_bang"] == 8 and all("ole:" in b["nguon"] for b in bn["bang"]))
    ok("doc_bang_nhung ghi_chu TRUNG TINH (KHONG xac dinh o TONG, KHONG tu cong)",
       "TỔNG" in bn["ghi_chu"] and "KHÔNG tự" in bn["ghi_chu"])
    ok("doc_bang_nhung tra SO THAT trong hang (581.7 doc duoc)",
       any(581.7 in row for b in bn["bang"] for row in b["cac_hang"]))
    # (b) OLE la ANH (loai != excel) -> giu canh bao CU 'khong doc duoc/THIEU'
    cb2 = _FakeThep([{"handle": "IMG1", "layer": "0", "loai": "anh"}] * 3).thong_ke_thep().get("canh_bao_nhung") or {}
    ok("OLE anh -> so_bang_doc_duoc=0, canh bao co 'THIEU' (khong doc duoc)",
       cb2.get("so_bang_doc_duoc") == 0 and "THIẾU" in cb2.get("canh_bao", ""), cb2)
    # doi chung: 0 OLE -> KHONG canh bao (chan mutation 'luon canh bao')
    r0 = _FakeThep([]).thong_ke_thep()
    ok("doi chung: thep rong + 0 OLE -> co_bang=False NHUNG KHONG canh bao (khong bia)",
       r0.get("co_bang_thong_ke") is False and "canh_bao_nhung" not in r0)
    ok("doi chung: 0 OLE -> doc_bang_nhung so_bang=0", _FakeThep([]).doc_bang_nhung()["so_bang"] == 0)

    print("[C4] REAL CT-A KT (2 OLE) — thep/thep-hinh/tong-hop deu LO canh bao")
    if os.path.isfile(KT):
        d = tc.Drawing(KT)
        ok("doc duoc dung 2 OLE tu file that", len(d.ole_nhung) == 2, len(d.ole_nhung))
        r = d.thong_ke_thep()
        ok("thong_ke_thep: co canh_bao_nhung", "canh_bao_nhung" in r, sorted(r.keys()))
        ok("thong_ke_thep: ghi_chu KHONG con khang dinh tron 'khong co bang' (co ⚠)",
           "⚠" in (r.get("ghi_chu") or ""), r.get("ghi_chu"))
        rh = d.thong_ke_thep_hinh()
        ok("thong_ke_thep_hinh: co canh_bao_nhung", "canh_bao_nhung" in rh, sorted(rh.keys()))
        rt = d.tong_hop_khoi_luong()
        ok("tong_hop_khoi_luong (nguon Excel ban giao): co canh_bao_nhung", "canh_bao_nhung" in rt)
        ok("tong_hop: so_hang KHONG bi doi boi canh bao", isinstance(rt.get("so_hang"), int))
    else:
        skip("CT-A KT")

    print("[C5] REAL CT-A KC (0 OLE) — CHONG HOI QUY: khong canh bao, so y nguyen")
    if os.path.isfile(KC):
        d2 = tc.Drawing(KC)
        ok("KC khong co OLE", len(d2.ole_nhung) == 0, len(d2.ole_nhung))
        r2 = d2.thong_ke_thep()
        ok("thong_ke_thep: KHONG co canh_bao_nhung (khong canh bao oan)", "canh_bao_nhung" not in r2)
        ok("thong_ke_thep: tong thep tron = 67370.7 (so CU, khong regress)",
           r2.get("tong_khoi_luong_kg") == 67370.7, r2.get("tong_khoi_luong_kg"))
        ok("ghi_chu KHONG dinh ⚠ oan", "⚠" not in (r2.get("ghi_chu") or ""), r2.get("ghi_chu"))
        r3 = d2.tong_hop_khoi_luong()
        ok("tong_hop: KHONG co canh_bao_nhung", "canh_bao_nhung" not in r3)
    else:
        skip("CT-A KC")

    print("[C6] SYSTEM_PROMPT rule 8c — bat buoc LO, cam noi 'ban ve khong co'")
    import mcp_bridge as B
    sp = B.SYSTEM_PROMPT
    ok("co rule 8c ve doi tuong nhung", "8c." in sp and "canh_bao_nhung" in sp)
    ok("cam khang dinh 'khong co bang thong ke' khi co canh_bao_nhung",
       "canh_bao_nhung" in sp and "không đọc được" in sp.lower(), None)
    ok("readable OLE -> huong dan goi doc_bang_nhung (khong tu cong tong)",
       "doc_bang_nhung" in sp and "so_bang_doc_duoc" in sp)
    ok("cam khang dinh '0 kg' khi co canh bao", "0 kg" in sp)

    print("[F1] Canh bao OLE cam vao TUYEN SO-LUONG/KICH-THUOC khi ket qua RONG (audit GD4)")
    # Truoc: chi tuyen thep co canh bao -> hoi so luong tren file 8-OLE tra 'khong ghi so luong'
    # ma KHONG lo OLE = dung failure mode rule 8c dinh chong. Nay cam them 3 tuyen, CHI khi RONG.
    if os.path.isfile(KT):
        d = tc.Drawing(KT)  # CT-A KT co 2 OLE + CO qty (38 muc)
        ok("KT co OLE (2)", len(d.ole_nhung) == 2, len(d.ole_nhung))
        # Ma KHONG ton tai -> ket qua am -> PHAI canh bao
        r = d.tra_cuu_so_luong("MA_KHONG_CO_XYZ")
        ok("tra_cuu ket qua AM tren file OLE -> co canh_bao_nhung", "canh_bao_nhung" in r and r.get("co_ghi_so_luong") is False, sorted(r.keys()))
        r = d.liet_ke_so_luong("MA_KHONG_CO_XYZ")
        ok("liet_ke loc-khong-khop tren file OLE -> co canh_bao_nhung", "canh_bao_nhung" in r and r.get("so_muc") == 0)
        # CHONG NHIEU: liet_ke KHONG loc -> co 38 muc -> KHONG canh bao (tranh alarm fatigue)
        r = d.liet_ke_so_luong()
        ok("liet_ke TIM THAY (>0 muc) tren file OLE -> KHONG canh bao (chong nhieu)",
           r.get("so_muc") > 0 and "canh_bao_nhung" not in r, (r.get("so_muc"), "canh_bao_nhung" in r))
    else:
        skip("F1 real KT")
    # File 0-OLE: 3 tuyen KHONG bao gio canh bao oan + so KHONG doi
    if os.path.isfile(KC):
        d = tc.Drawing(KC)
        ok("KC (0 OLE): tra_cuu am KHONG canh bao", "canh_bao_nhung" not in d.tra_cuu_so_luong("ZZZ"))
        r = d.thong_tin_kich_thuoc()
        ok("KC (0 OLE): thong_tin_kich_thuoc KHONG canh bao + so_duong>0 giu nguyen",
           "canh_bao_nhung" not in r and r.get("so_duong_kich_thuoc") > 0)
    else:
        skip("F1 real KC")
    # Synthetic: thong_tin_kich_thuoc voi 0 dim tren file OLE -> canh bao
    class _FakeDim:
        _canh_bao_nhung = tc.Drawing._canh_bao_nhung
        _gan_canh_bao_nhung = tc.Drawing._gan_canh_bao_nhung
        def __init__(self, ole):
            self.ole_nhung = ole
            self.dims = []
            self.dim_vals = []
            self.dim_top = []
            class _D:
                class header:
                    @staticmethod
                    def get(k, d=0): return 0
            self.doc = _D()
    r = tc.Drawing.thong_tin_kich_thuoc(_FakeDim([{"handle": "H", "layer": "L"}]))
    ok("thong_tin_kich_thuoc 0-dim + OLE -> canh bao", "canh_bao_nhung" in r, sorted(r.keys()))
    r = tc.Drawing.thong_tin_kich_thuoc(_FakeDim([]))
    ok("thong_tin_kich_thuoc 0-dim + 0-OLE -> KHONG canh bao", "canh_bao_nhung" not in r)

    print("[F2] Quet OLE ca PAPERSPACE (layout in an), khong chi modelspace (audit hardening)")
    class _FE:
        def __init__(s, t, h="H", ly="0"):
            s._t = t
            s.dxf = type("d", (), {"handle": h, "get": lambda self, k, d=None: ly})()
        def dxftype(s): return s._t
    class _FakeDoc:
        def __init__(s, layouts): s._l = layouts
        def layout_names(s): return list(s._l.keys())
        def layout(s, n): return s._l[n]
    d = _FakeDoc({"Model": [_FE("LINE")], "Layout1": [_FE("OLE2FRAME", "PS1"), _FE("TEXT")],
                  "Layout2": [_FE("OLE2FRAME", "PS2")]})
    r = tc._ole_ngoai_modelspace(d)
    ok("tim 2 OLE o paperspace (bo qua Model + TEXT)", len(r) == 2 and [x["handle"] for x in r] == ["PS1", "PS2"], r)
    ok("danh dau khong_gian=paperspace", all(x.get("khong_gian") == "paperspace" for x in r))
    class _BadDoc:
        def layout_names(s): return ["Model", "Bad"]
        def layout(s, n): raise RuntimeError("loi API")
    ok("fail-soft: layout loi -> [] khong vo", tc._ole_ngoai_modelspace(_BadDoc()) == [])
    ok("doc khong co layout_names -> []", tc._ole_ngoai_modelspace(object()) == [])
    # corpus THAT: 0 paperspace-OLE -> so OLE KHONG doi (khong regress/canh bao oan)
    if os.path.isfile(KT):
        ok("real KT: ole_nhung van = 2 (0 paperspace, khong doi)", len(tc.Drawing(KT).ole_nhung) == 2, len(tc.Drawing(KT).ole_nhung))
    else:
        skip("F2 real KT")

    print("[F3] thong_ke_thep nhanh co_trong_bang=False (hoi co dk vang) cung LO OLE")
    class _FT:
        _canh_bao_nhung = tc.Drawing._canh_bao_nhung
        _gan_canh_bao_nhung = tc.Drawing._gan_canh_bao_nhung
        thong_ke_thep = tc.Drawing.thong_ke_thep
        def __init__(s, ole):
            s.ole_nhung = ole
            s.thep = {"by_dk": {"Ø16": {"so_thanh": 10, "dai_m": 50.0, "kg": 79.0}}}
            s.thep_hinh = {"by_show": {}}
    r = _FT([{"handle": "O", "layer": "0"}]).thong_ke_thep("22")   # hoi Ø22, bang chi co Ø16
    ok("co_trong_bang=False + co OLE -> co canh_bao_nhung",
       r.get("co_trong_bang") is False and "canh_bao_nhung" in r, r)
    ok("cung nhanh + 0 OLE -> KHONG canh bao (khong bia)", "canh_bao_nhung" not in _FT([]).thong_ke_thep("22"))

    print("[C7] Tuong tac grounding-guard: canh bao KHONG lam vo guard")
    nums = B._collect_numbers({"co_bang_thong_ke": False,
                               "canh_bao_nhung": {"so_doi_tuong_nhung": 8, "handles": ["BC7020"]}})
    ok("so 8 (dem OLE) vao tool_numbers -> cau noi '8 doi tuong nhung' KHONG bi chan",
       B._guard_text("Bản vẽ có 8 đối tượng nhúng, máy không đọc được.", nums) != B.REFUSE_MESSAGE)

    if SKIP:
        print("CANH BAO: %d nhom BO QUA (thieu fixture)" % SKIP)
    print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
