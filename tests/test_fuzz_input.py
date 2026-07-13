# -*- coding: utf-8 -*-
"""FUZZ ROBUSTNESS — TẤT ĐỊNH, KHÔNG gọi Gemini, KHÔNG mạng, KHÔNG tốn phí.
Chạy:  python tests/test_fuzz_input.py

Khoá 4 lớp CHƯA có test riêng (chống crash/treo/bịa trên input rác):
  (a) DXF RÁC / cắt cụt  -> Drawing(path) phải NÉM lỗi CÓ NGHĨA (bắt được), KHÔNG treo.
  (b) DXF hợp lệ 0-TEXT   -> Drawing nạp được; tra_cuu/tinh_dai_luong 1 mã -> 'không tìm thấy' TRUNG THỰC.
  (c) inputs_bo_sung RÁC  -> KHÔNG crash; nhánh M3 coerce {} (tools_core ~1936); trả can_bo_sung/lỗi LỘ.
  (d) ma_cau_kien EMOJI / ký tự điều khiển -> KHÔNG vỡ (trả dict hợp lệ).
Fixture thiếu -> SKIP (BO QUA), KHÔNG crash. Dọn sạch mọi file tạm."""
import os, sys, io, json, tempfile, shutil
os.environ.setdefault("READFILE_MAX_MB", "300")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import tools_core
from tools_core import Drawing

BASE = os.path.normpath(os.path.join(HERE, "..", "..", "input_files", "_dxf"))
KC = os.path.join(BASE, "BV+DT MN Gia Loc", "2. KetCau MN GiaLoc.dxf")

PASS = FAIL = SKIP = 0
_TMP = tempfile.mkdtemp(prefix="fuzz_dxf_")   # nơi chứa MỌI file tạm; dọn ở finally


def _emit(name, ok, extra=""):
    global PASS, FAIL
    ok = bool(ok)
    PASS += int(ok); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" " + extra) if extra else ""))


def _skip(nhom, ly_do):
    global SKIP
    SKIP += 1
    print("  [..] BO QUA %s — %s (KHONG phai da kiem)" % (nhom, ly_do))


def _write(fn, data, mode="w"):
    p = os.path.join(_TMP, fn)
    kw = {} if "b" in mode else {"encoding": "utf-8"}
    with open(p, mode, **kw) as f:
        f.write(data)
    return p


def main():
    print("[a] DXF RÁC / CẮT CỤT -> Drawing NÉM lỗi bắt được, KHÔNG treo (không trả Drawing câm)")
    casos = [
        ("rac_thuan.dxf", "day khong phai file DXF gi ca\nrandom junk 12345\n"),
        ("rac_nhi_phan.dxf", b"\x00\x01\x02\xff\xfe rac nhi phan khong phai dxf \x00\x00", "wb"),
        ("cat_cut.dxf", "0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1024\n"),   # header mở, KHÔNG EOF -> cắt cụt
        ("rong.dxf", ""),                                                      # file 0 byte
    ]
    for c in casos:
        fn, data = c[0], c[1]
        mode = c[2] if len(c) > 2 else "w"
        p = _write(fn, data, mode)
        try:
            Drawing(p)
            _emit("%-16s -> NÉM lỗi" % fn, False, "<<< KHÔNG ném lỗi mà nạp được (rác lọt qua)")
        except Exception as ex:
            msg = str(ex)
            # 'có nghĩa' = là Exception thường (bắt được), có thông điệp -> không phải treo/segfault câm
            _emit("%-16s -> NÉM lỗi bắt được" % fn, isinstance(ex, Exception), "(%s: %s)" % (type(ex).__name__, msg[:48]))

    print("[b] DXF HỢP LỆ 0-TEXT -> nạp được; tra cứu 1 mã -> 'không tìm thấy' TRUNG THỰC (không bịa)")
    try:
        import ezdxf
    except Exception as ex:
        _skip("b", "khong import duoc ezdxf (%s)" % ex)
        ezdxf = None
    if ezdxf is not None:
        empty_path = os.path.join(_TMP, "hop_le_rong.dxf")
        doc = ezdxf.new("R2010")   # doc rỗng, KHÔNG text/entity nào
        doc.saveas(empty_path)
        try:
            dwg = Drawing(empty_path)
            _emit("Drawing nạp DXF rỗng OK (không crash)", True, "-> %d text" % len(dwg.texts))
            _emit("DXF rỗng: 0 text (không bịa entity)", len(dwg.texts) == 0)
            # tra_cuu_so_luong 1 mã -> KHÔNG ghi số lượng (trung thực, không đếm chữ)
            r = dwg.tra_cuu_so_luong("C1")
            _emit("tra_cuu_so_luong('C1') -> co_ghi_so_luong=False (trung thực)",
                  r.get("co_ghi_so_luong") is False and r.get("so_muc_co_ghi") == 0)
            # tinh_dai_luong mã có chữ số trên file rỗng -> khong_tim_thay (không mời nhập số cho thứ vắng mặt)
            r = dwg.tinh_dai_luong("thể tích bê tông cột", "C1", "")
            _emit("tinh_dai_luong cột 'C1' trên file rỗng -> khong_tim_thay=True",
                  r.get("khong_tim_thay") is True and r.get("co_ket_qua") is False and not r.get("can_bo_sung"))
            # mã TRỐNG + nhập tay đủ số -> vẫn tính được (không chặn oan trên file rỗng)
            r = dwg.tinh_dai_luong("thể tích bê tông sàn", "", '{"dien_tich":50,"chieu_day":100}')
            _emit("mã trống + nhập tay đủ số trên file rỗng -> vẫn tính", r.get("co_ket_qua") is True,
                  "-> %s" % r.get("ket_qua"))
        except Exception as ex:
            _emit("Drawing nạp DXF rỗng KHÔNG crash", False, "<<< %s: %s" % (type(ex).__name__, ex))

    print("[c] inputs_bo_sung RÁC -> KHÔNG crash; coerce {} (M3); trả can_bo_sung/khong_tim_thay LỘ")
    if not os.path.isfile(KC):
        _skip("c", "khong thay fixture KC (%s)" % KC)
    else:
        kc = Drawing(KC)
        # RÁC JSON: list / số / '{bad json / chuỗi emoji / rỗng -> tất cả coerce {} -> đào đất mã trống = THIẾU
        for tag, bs in [("list '[1,2]'", "[1,2]"), ("số '5'", "5"), ("'{bad json'", "{bad json"),
                        ("chuỗi '\"🔥\"'", '"🔥"'), ("rỗng ''", ""), ("null", "null"),
                        ("mảng object '[{\"a\":1}]'", '[{"a":1}]')]:
            try:
                r = kc.tinh_dai_luong("khối lượng đào đất", "", bs)
                ok = isinstance(r, dict) and r.get("can_bo_sung") is True and not r.get("co_ket_qua")
                _emit("bs %-24s -> KHÔNG crash + can_bo_sung (coerce {})" % tag, ok,
                      "" if ok else "<<< %r" % ({k: r.get(k) for k in ("co_ket_qua", "can_bo_sung", "khong_tim_thay")}))
            except Exception as ex:
                _emit("bs %-24s -> KHÔNG crash" % tag, False, "<<< CRASH %s: %s" % (type(ex).__name__, ex))
        # RÁC bs TRÊN MÃ GIẢ -> vẫn khong_tim_thay (rác không cứu được mã vắng); không crash
        for tag, bs in [("list", "[9,9]"), ("số", "42"), ("hỏng", "{oops")]:
            try:
                r = kc.tinh_dai_luong("thể tích bê tông cột", "C999ZZ", bs)
                _emit("mã GIẢ 'C999ZZ' + bs rác %-6s -> khong_tim_thay" % tag,
                      isinstance(r, dict) and r.get("khong_tim_thay") is True and not r.get("co_ket_qua"))
            except Exception as ex:
                _emit("mã GIẢ + bs rác %-6s -> KHÔNG crash" % tag, False, "<<< %s: %s" % (type(ex).__name__, ex))
        # bs là dict Python trực tiếp (không phải chuỗi) — dict(inputs_bo_sung) path; số bù đủ -> tính
        try:
            r = kc.tinh_dai_luong("thể tích bê tông sàn", "", {"dien_tich": 50, "chieu_day": 100})
            _emit("bs là DICT python (không chuỗi) đủ số -> tính, KHÔNG crash",
                  isinstance(r, dict) and r.get("co_ket_qua") is True, "-> %s" % r.get("ket_qua"))
        except Exception as ex:
            _emit("bs là DICT python -> KHÔNG crash", False, "<<< %s: %s" % (type(ex).__name__, ex))

    print("[d] ma_cau_kien EMOJI / KÝ TỰ ĐIỀU KHIỂN -> KHÔNG vỡ (trả dict hợp lệ)")
    if not os.path.isfile(KC):
        _skip("d", "khong thay fixture KC (%s)" % KC)
    else:
        kc = Drawing(KC)
        # Nhóm 1 — RÁC THUẦN (KHÔNG chứa mã cấu kiện thật): trả dict hợp lệ + KHÔNG bịa kết quả.
        ma_rac = ["🔥", "\x00\x01\x02", "‮gnp", "💣" * 50, "\x1b[31m\x1b[0m",
                  "  ", "\U0001F600\U0001F4A9", "﻿﻿", "🔥🔥🔥ZZ🔥🔥"]
        for m in ma_rac:
            try:
                r = kc.tinh_dai_luong("thể tích bê tông cột", m, "")
                # KHÔNG vỡ = trả dict; RÁC THUẦN -> KHÔNG bịa kết quả (co_ket_qua phải False)
                ok = isinstance(r, dict) and r.get("co_ket_qua") is not True
                _emit("ma RÁC THUẦN %-12r -> dict hợp lệ, KHÔNG bịa kết quả" % (m[:10]), ok,
                      "" if ok else "<<< %r" % r)
            except Exception as ex:
                _emit("ma RÁC THUẦN %-12r -> KHÔNG crash" % (m[:10]), False, "<<< %s: %s" % (type(ex).__name__, ex))
        # Nhóm 2 — MÃ THẬT 'C1' bọc NHIỄU (khoảng trắng/điều khiển) -> chỉ đòi KHÔNG crash (trả dict).
        # Nhiễu khoảng-trắng tách token sạch 'c1' -> có thể nhận đúng C1 & tính (HỢP LỆ, không phải bịa).
        for m in ["C1\n\t", "  C1  ", "\x00C1\x00", "C1" + "﻿", "\x1b[0mC1\x1b[0m"]:
            try:
                r = kc.tinh_dai_luong("thể tích bê tông cột", m, "")
                _emit("ma 'C1'+nhiễu %-14r -> dict hợp lệ (KHÔNG crash)" % (m[:12]), isinstance(r, dict))
            except Exception as ex:
                _emit("ma 'C1'+nhiễu %-14r -> KHÔNG crash" % (m[:12]), False, "<<< %s: %s" % (type(ex).__name__, ex))
        # emoji trong ma + bs rác cùng lúc -> vẫn không crash
        try:
            r = kc.tinh_dai_luong("khối lượng inox", "S1🔥💣", "{bad")
            _emit("ma emoji + bs hỏng đồng thời -> KHÔNG crash", isinstance(r, dict))
        except Exception as ex:
            _emit("ma emoji + bs hỏng -> KHÔNG crash", False, "<<< %s: %s" % (type(ex).__name__, ex))
        # ten_dai_luong emoji/rác -> không nhận ra công thức -> lỗi LỘ, không crash
        try:
            r = kc.tinh_dai_luong("🔥 khong ton tai 💣", "C1", "")
            _emit("ten_dai_luong rác -> loi LỘ (không crash, không tính)",
                  isinstance(r, dict) and r.get("co_ket_qua") is not True and ("loi" in r or "cac_dai_luong_ho_tro" in r))
        except Exception as ex:
            _emit("ten_dai_luong rác -> KHÔNG crash", False, "<<< %s: %s" % (type(ex).__name__, ex))


if __name__ == "__main__":
    try:
        main()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    print("\n%d PASS / %d FAIL / %d SKIP" % (PASS, FAIL, SKIP))
    sys.exit(1 if FAIL else 0)
