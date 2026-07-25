# -*- coding: utf-8 -*-
"""I9 — SYSTEM_PROMPT tách thành MẢNH có TÊN + phân nhóm + version (byte-identical).
KHOÁ BẤT BIẾN: prompt là lõi CHỐNG BỊA lái Gemini → mọi refactor phải giữ NGUYÊN byte.
Test này (offline, 0 API — chỉ import module) là CỔNG chặn trôi text: bất kỳ thay đổi
byte nào của SYSTEM_PROMPT đều làm sha256 lệch FROZEN → FAIL to, buộc phải bump
PROMPT_VERSION + cập nhật FROZEN + ĐO LIVE (không cho đổi lõi chống bịa âm thầm).
Chạy: python tests/test_prompt_taxonomy.py"""
import os, sys, io, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import mcp_bridge as B  # noqa  (import offline = 1 phần điều kiện DoD)

# sha256 ĐÓNG BĂNG của SYSTEM_PROMPT trước+sau I9 (byte-identical). ĐỔI = cố ý mới được sửa.
# 2026-07-26: ĐỔI CÓ CHỦ ĐÍCH (routing R7b + prompt-half R10) — ĐÃ đo LIVE A/B (recall↑, anti-bịa traps GIỮ,
# prompt-half OK) + bump PROMPT_VERSION. Hash cũ (byte-identical I9) = bea17c6eec56…a70e18.
FROZEN = "e5e05d7d487d31484f0428d8f2504866539e57c6bef6bd93f1602f3e0512ceaa"

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def main():
    sp = B.SYSTEM_PROMPT
    sha = hashlib.sha256(sp.encode("utf-8")).hexdigest()

    print("[T.1] BYTE-LOCK — SYSTEM_PROMPT không đổi byte (lõi chống bịa)")
    ok("sha256(SYSTEM_PROMPT) == FROZEN bea17c6e…", sha == FROZEN, sha)
    ok("SYSTEM_PROMPT là str không rỗng", isinstance(sp, str) and len(sp) > 1000, len(sp))

    print("[T.2] LẮP RÁP — SYSTEM_PROMPT = ''.join(_EMIT_ORDER)")
    ok("''.join(_EMIT_ORDER) == SYSTEM_PROMPT", "".join(B._EMIT_ORDER) == sp)
    ok("_EMIT_ORDER có đúng 24 mảnh (+R7b routing 2026-07-26)", len(B._EMIT_ORDER) == 24, len(B._EMIT_ORDER))

    print("[T.3] VERSION + HASH")
    ok("PROMPT_VERSION là str không rỗng", isinstance(B.PROMPT_VERSION, str) and B.PROMPT_VERSION.strip(), B.PROMPT_VERSION)
    ok("PROMPT_HASH == sha256(SYSTEM_PROMPT) (tự nhất quán)", B.PROMPT_HASH == sha, B.PROMPT_HASH)
    ok("PROMPT_HASH == FROZEN", B.PROMPT_HASH == FROZEN)

    print("[T.4] PHÂN NHÓM — toàn phần + phân hoạch (không sót, không trùng, không lạc)")
    groups = tuple(B._HEADER_GROUP) + tuple(B._INVARIANT) + tuple(B._VN_CONVENTION)
    ok("|_HEADER|+|_INVARIANT|+|_VN_CONVENTION| == 24 (mỗi mảnh 1 nhóm)", len(groups) == 24, len(groups))
    ok("multiset(3 nhóm) == multiset(_EMIT_ORDER) (phủ hết + không dư)", sorted(groups) == sorted(B._EMIT_ORDER))
    # phân hoạch chặt: không mảnh nào ở >1 nhóm (so theo id để không bị nhầm khi text trùng)
    inv_ids, vn_ids, hdr_ids = set(map(id, B._INVARIANT)), set(map(id, B._VN_CONVENTION)), set(map(id, B._HEADER_GROUP))
    ok("_INVARIANT ∩ _VN_CONVENTION == ∅", inv_ids.isdisjoint(vn_ids))
    ok("_HEADER_GROUP ∩ (_INVARIANT ∪ _VN_CONVENTION) == ∅", hdr_ids.isdisjoint(inv_ids | vn_ids))
    ok("_INVARIANT có 7 mảnh, _VN_CONVENTION có 15, _HEADER_GROUP có 1",
       (len(B._INVARIANT), len(B._VN_CONVENTION), len(B._HEADER_GROUP)) == (7, 16, 1),
       (len(B._INVARIANT), len(B._VN_CONVENTION), len(B._HEADER_GROUP)))

    print("[T.5] VỊ TRÍ — header đầu, style (rule 9) cuối; đúng byte order hiện tại")
    ok("_EMIT_ORDER[0] là _P_HEADER và mở đầu 'Bạn là'", B._EMIT_ORDER[0] is B._P_HEADER and sp.startswith("Bạn là"))
    ok("SYSTEM_PROMPT kết thúc bằng rule 9 (không có \\n cuối)", sp.rstrip("\n") == sp and sp.endswith("kỹ sư."))

    print("[T.6] REGRESSION — byte-identical GIỮ mọi anchor mà test khác/hàng-rào phụ thuộc")
    for anchor in ("MŨI CỌC", "HỎI LẠI", "canh_bao_nhung", "doc_bang_nhung",
                   "so_bang_doc_duoc", "0 kg", "CHỐNG THAO TÚNG"):
        ok("anchor còn: %r" % anchor, anchor in sp)
    ok("anchor 'không đọc được' (lower) còn", "không đọc được" in sp.lower())
    # 2 nhãn '8c.' TRÙNG được GIỮ NGUYÊN có chủ đích (dọn nhãn = việc của Option B, cần đo LIVE)
    ok("giữ nguyên 2 nhãn '8c.' (wart hoãn sang Option B)", sp.count("8c.") == 2, sp.count("8c."))
    # nhưng ở SOURCE đã tách tên riêng 2 mảnh 8c (khử trùng lặp mức mã nguồn)
    ok("source đã tách _P_R8c_OLE ≠ _P_R8c_INOX", B._P_R8c_OLE is not B._P_R8c_INOX and B._P_R8c_OLE != B._P_R8c_INOX)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
