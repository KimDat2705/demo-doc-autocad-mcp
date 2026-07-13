# -*- coding: utf-8 -*-
"""KHOÁ VISUAL-HIGHLIGHT (0 test trước đây) — TẤT ĐỊNH, KHÔNG gọi Gemini/mạng, KHÔNG tốn phí.
Chạy:  python tests/test_visual_highlight.py

Khoá 3 hành vi cốt lõi của Drawing.highlight / render_region (tools_core ~2327-2391):
  (a) TỪ KHOÁ CÓ trong file -> anh_id dạng 'hl_*.png' + file PNG TỒN TẠI + header hợp lệ (b'\\x89PNG').
  (b) TỪ KHOÁ KHÔNG có       -> so_ket_qua=0, anh_id=None, KHÔNG bịa ảnh (không tạo PNG).
  (c) INPUT RỖNG (không tu_khoa/layer) -> trả lỗi có kiểm soát, KHÔNG crash.
Dọn mọi PNG do test tạo ra ở cuối (giữ _renders sạch)."""
import os, sys, io
os.environ.setdefault("READFILE_MAX_MB", "300")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
from tools_core import Drawing, RENDER_DIR

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
KT = os.path.join(BASE, "BV+DT MN Gia Loc", "1. Kien truc MN Gia Loc.dxf")
KC = os.path.join(BASE, "BV+DT MN Gia Loc", "2. KetCau MN GiaLoc.dxf")

PASS = FAIL = SKIP = 0
_created = set()   # anh_id PNG do test tạo -> dọn cuối


def _emit(name, ok, extra=""):
    global PASS, FAIL
    okk = bool(ok); PASS += int(okk); FAIL += int(not okk)
    print("  [%s] %s%s" % ("OK" if okk else "FAIL", name, (" " + extra) if extra else ""))


def skip(nhom, ly_do):
    global SKIP
    SKIP += 1
    print("  [..] BO QUA %s — %s (KHONG phai da kiem)" % (nhom, ly_do))


def _png_ok(anh_id):
    """anh_id -> (ton_tai, header_hop_le). Đọc 8 byte đầu, kiểm chữ ký PNG."""
    if not anh_id:
        return False, False
    _created.add(anh_id)
    p = os.path.join(RENDER_DIR, anh_id)
    if not os.path.isfile(p):
        return False, False
    with open(p, "rb") as f:
        head = f.read(8)
    return True, head.startswith(b"\x89PNG\r\n\x1a\n")


def main():
    global PASS, FAIL
    if not (os.path.isfile(KT) and os.path.isfile(KC)):
        skip("ALL", "khong thay fixture KT/KC (%s)" % BASE)
        print("\n%d PASS / %d FAIL  (SKIP %d)" % (PASS, FAIL, SKIP))
        sys.exit(1 if FAIL else 0)

    kt, kc = Drawing(KT), Drawing(KC)

    print("[A] TỪ KHOÁ CÓ TRONG FILE -> khoanh đỏ + ảnh PNG thật (anh_id='hl_*.png', header hợp lệ)")
    # 'cot' (cột) có 38 nhãn có toạ độ trên KC — khớp -> phải trả anh_id + PNG tồn tại + đọc được.
    r = kc.highlight(tu_khoa="cot")
    _emit("KC highlight('cot'): so_ket_qua>0", r.get("so_ket_qua", 0) > 0, "-> %s" % r.get("so_ket_qua"))
    aid = r.get("anh_id")
    _emit("KC: anh_id dạng 'hl_*.png'", isinstance(aid, str) and aid.startswith("hl_") and aid.endswith(".png"), "-> %s" % aid)
    ton_tai, header = _png_ok(aid)
    _emit("KC: file PNG TỒN TẠI trong _renders", ton_tai)
    _emit("KC: PNG đọc được — header b'\\x89PNG' hợp lệ (không phải ảnh rỗng/rác)", header)
    _emit("KC: so_danh_dau_tren_anh<=so_ket_qua, so_entity_ve>0",
          0 < r.get("so_danh_dau_tren_anh", 0) <= r.get("so_ket_qua", 0) and r.get("so_entity_ve", 0) > 0,
          "-> danh_dau=%s entity=%s" % (r.get("so_danh_dau_tren_anh"), r.get("so_entity_ve")))
    _emit("KC: vi_tri là list có handle+text cho từng vị trí khoanh",
          isinstance(r.get("vi_tri"), list) and len(r["vi_tri"]) > 0 and all("handle" in v and "text" in v for v in r["vi_tri"]))

    # KT bằng layer= (đường lọc theo layer, không tu_khoa) — 'cua' hoặc rơi về từ khoá phổ biến.
    r2 = kt.highlight(tu_khoa="cua")
    if r2.get("so_ket_qua", 0) > 0:
        aid2 = r2.get("anh_id"); t2, h2 = _png_ok(aid2)
        _emit("KT highlight('cua'): anh_id 'hl_*.png' + PNG tồn tại + header hợp lệ",
              isinstance(aid2, str) and aid2.startswith("hl_") and t2 and h2, "-> %s" % aid2)
    else:
        skip("A-KT-cua", "tu khoa 'cua' khong co toa do tren KT (so_ket_qua=0)")

    print("[B] TỪ KHOÁ KHÔNG CÓ -> so_vi_tri=0, KHÔNG bịa ảnh (anh_id rỗng, không tạo PNG)")
    r = kc.highlight(tu_khoa="zzqqxx_khong_ton_tai")
    _emit("KC highlight(giả): so_ket_qua=0", r.get("so_ket_qua", 1) == 0)
    _emit("KC highlight(giả): anh_id là None/rỗng (KHÔNG bịa ảnh)", not r.get("anh_id"))
    _emit("KC highlight(giả): có ghi_chu 'Không tìm thấy' (LỘ, không im lặng)",
          "Không tìm thấy" in (r.get("ghi_chu") or ""), "-> %s" % (r.get("ghi_chu") or "")[:40])
    # KHÔNG được tạo file PNG rác cho truy vấn không khớp:
    n_hl_before = len([f for f in os.listdir(RENDER_DIR) if f.startswith("hl_")])
    kc.highlight(tu_khoa="another_ghost_zzz")
    n_hl_after = len([f for f in os.listdir(RENDER_DIR) if f.startswith("hl_")])
    _emit("truy vấn giả KHÔNG sinh thêm PNG nào trong _renders", n_hl_after == n_hl_before,
          "-> before=%d after=%d" % (n_hl_before, n_hl_after))

    print("[C] INPUT RỖNG / BIÊN -> KHÔNG crash, trả lỗi có kiểm soát")
    for tag, kw, ly in [("cả tu_khoa lẫn layer rỗng", "", ""),
                        ("tu_khoa=None layer=None", None, None),
                        ("chỉ khoảng trắng", "   ", "  ")]:
        try:
            r = kc.highlight(tu_khoa=kw, layer=ly)
            ok = isinstance(r, dict) and r.get("so_ket_qua", 1) == 0 and not r.get("anh_id")
            _emit("empty (%s) -> dict so_ket_qua=0, không ảnh, không crash" % tag, ok, "-> %s" % (r.get("loi") or r.get("ghi_chu") or "")[:30])
        except Exception as e:
            _emit("empty (%s) -> KHÔNG crash" % tag, False, "<<< CRASH: %r" % e)

    print("[D] render_region trực tiếp — vẽ đúng vùng, trả PNG thật (không cần highlights)")
    # Lấy 1 toạ độ hit thật để dựng window nhỏ quanh nó.
    hits = [h for h in kc.search_texts("cot") if (h.get("x") or h.get("y"))]
    if hits:
        cx, cy = hits[0]["x"], hits[0]["y"]
        window = (cx - 5000, cy - 5000, cx + 5000, cy + 5000)
        try:
            fid, fpath, n_ent = kc.render_region(window, highlights=[{"x": cx, "y": cy}])
            _created.add(fid)
            ok_png = os.path.isfile(fpath)
            with open(fpath, "rb") as f:
                hdr = f.read(8).startswith(b"\x89PNG")
            _emit("render_region: trả (fid 'hl_*.png', path tồn tại, n_ent int) + header PNG",
                  fid.startswith("hl_") and ok_png and hdr and isinstance(n_ent, int), "-> %d entity" % n_ent)
        except Exception as e:
            _emit("render_region KHÔNG crash trên window hợp lệ", False, "<<< CRASH: %r" % e)
    else:
        skip("D", "khong lay duoc toa do hit tren KC")

    # ---- DỌN: xoá mọi PNG test tạo ra để giữ _renders sạch ----
    for aid in _created:
        try:
            p = os.path.join(RENDER_DIR, aid)
            if os.path.isfile(p): os.remove(p)
        except Exception:
            pass

    print("\n%d PASS / %d FAIL  (SKIP %d)" % (PASS, FAIL, SKIP))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
