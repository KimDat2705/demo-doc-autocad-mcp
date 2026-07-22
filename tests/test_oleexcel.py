# -*- coding: utf-8 -*-
"""KHOÁ module oleexcel — đọc bảng Excel NHÚNG (OLE) qua BINARY. TẤT ĐỊNH, OFFLINE, KHÔNG API.
Chạy:  python tests/test_oleexcel.py

Unit test dùng blob TỰ CHẾ (không cần corpus): .xlsx zip trực tiếp · gói packager · ảnh · rác · rỗng.
Bất biến cốt lõi: SỐ đọc ra chính xác; không-Excel -> loai != 'excel' (để caller cảnh báo, KHÔNG bịa)."""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import oleexcel

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _xlsx_blob(rows, sheet="TK"):
    """Tạo blob .xlsx THẬT (PKZIP) bằng openpyxl."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def main():
    print("[A] .xlsx zip TRỰC TIẾP -> loai=excel + SỐ chính xác")
    blob = _xlsx_blob([["STT", "Ø(mm)", "Khối lượng"], [1, 16, 1654.17], [2, 20, 581.69]], sheet="THEP")
    r = oleexcel.doc_tu_blob(blob)
    ok("loai=excel", r.get("loai") == "excel", r.get("loai"))
    ok("sheet='THEP'", r.get("sheet") == "THEP", r.get("sheet"))
    ok("đọc đúng số 1654.17 (không sai 1 chữ số)", any(1654.17 in [c for c in row] for row in r.get("rows", [])), r.get("rows"))
    ok("đọc đúng 581.69", any(581.69 in row for row in r.get("rows", [])))
    ok("Ø(mm) header giữ nguyên", any("Ø(mm)" in [str(c) for c in row] for row in r.get("rows", [])))

    print("[B] .xlsx LỒNG trong 'packager' (header rác trước magic PK) -> vẫn rút được")
    inner = _xlsx_blob([["A", "B"], [10, 20]])
    wrapped = b"\x02\x00Package\x00C:\\tmp\\x.xlsx\x00" + b"\x00" * 8 + inner  # giả header packager
    r = oleexcel.doc_tu_blob(wrapped)
    ok("tìm PK lồng -> loai=excel", r.get("loai") == "excel", r.get("loai"))
    ok("đọc đúng số lồng (20.0)", any(20 in row for row in r.get("rows", [])))

    print("[C] KHÔNG phải Excel -> loai != 'excel' (KHÔNG bịa bảng)")
    ok("rỗng -> loai=rong", oleexcel.doc_tu_blob(b"").get("loai") == "rong")
    ok("None -> loai=rong", oleexcel.doc_tu_blob(None).get("loai") == "rong")
    ok("rác không magic -> loai=khac", oleexcel.doc_tu_blob(b"khong-phai-ole-blob-12345").get("loai") == "khac")
    wmf = bytes.fromhex("d7cdc69a") + b"\x00" * 40
    ok("WMF header -> loai=anh (ảnh, để OCR)", oleexcel.doc_tu_blob(wmf).get("loai") == "anh", oleexcel.doc_tu_blob(wmf))
    emf = b"\x01\x00\x00\x00" + b"\x00" * 36 + b" EMF"
    ok("EMF header -> loai=anh", oleexcel.doc_tu_blob(emf).get("loai") == "anh")

    print("[D] CFBF nhưng KHÔNG có bảng Excel -> loai != 'excel' (không tự nhận là bảng)")
    import olefile  # tạo 1 CFBF rỗng hợp lệ để test nhánh 'khac'
    ok("olefile có sẵn (dependency)", olefile is not None)
    # blob CFBF magic nhưng nội dung rác -> olefile mở lỗi -> loai=khac (không excel)
    fake_cfb = oleexcel.CFBF + b"\x00" * 500
    r = oleexcel.doc_tu_blob(fake_cfb)
    ok("CFBF rác -> loai != 'excel'", r.get("loai") != "excel", r.get("loai"))

    print("[E] doc_bang_ole: doc=None -> [] (fail-soft)")
    ok("None -> list rỗng", oleexcel.doc_bang_ole(None) == [])

    print("[F] Trần chống bảng khổng lồ (RAM)")
    big = _xlsx_blob([["x"] * 5] * 3000)  # 3000 hàng
    r = oleexcel.doc_tu_blob(big)
    ok("cắt <= _MAX_ROWS hàng (chống OOM)", len(r.get("rows", [])) <= oleexcel._MAX_ROWS, len(r.get("rows", [])))

    # --- Tuỳ chọn: kiểm trên corpus THẬT nếu có corpus_local (fixture OLE) ---
    print("[R] REAL corpus (nếu có corpus_local.THEP_OLE) — bảng thép nhúng đọc được")
    try:
        from corpus_local import THEP_OLE
    except Exception:
        THEP_OLE = ""
    if THEP_OLE and os.path.isfile(THEP_OLE):
        import ezdxf
        os.environ.setdefault("READFILE_MAX_MB", "600")
        bang = oleexcel.doc_bang_ole(ezdxf.readfile(THEP_OLE))
        exc = [b for b in bang if b["loai"] == "excel"]
        ok("có >=1 bảng Excel nhúng đọc được", len(exc) >= 1, len(bang))
        # phải có số thép thật (không rỗng)
        has_num = any(isinstance(c, (int, float)) and c > 0 for b in exc for row in b["rows"] for c in row)
        ok("bảng có SỐ > 0 (thép thật, không phải 0)", has_num)
    else:
        print("  [..] BỎ QUA [R] — thiếu corpus_local.THEP_OLE (không phải lỗi)")

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
