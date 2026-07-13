# -*- coding: utf-8 -*-
"""INV-10 + INV-12 (red-team P3, AI TỰ HỌC — MỞ KÊNH HỌC): TẤT ĐỊNH, offline, KHÔNG tốn API.
  INV-10: tool GHI (hoc_quy_uoc/thu_hoi_quy_uoc) KHÔNG phơi cho LLM (R8 — chống chữ-file lái LLM tự ghi quy ước).
  INV-12: MỌI truy cập self.hoc_phien nằm trong hàm cho phép (đọc TẬP TRUNG qua _quy_tac_hieu_luc; chống rải rác/quên lọc thu_hoi).
Chạy: python tests/test_hoc_quy_uoc.py"""
import os, sys, io, re, glob, tokenize
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

PASS = FAIL = 0


def _emit(name, ok):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s" % ("OK" if ok else "FAIL", name))


def main():
    print("[P3-INV] tool-layer LLM-exclusion (INV-10) + grep-guard hoc_phien (INV-12)")

    # ---- INV-10: hoc_quy_uoc/thu_hoi_quy_uoc KHÔNG trong gemini_tools (R8) ----
    import mcp_bridge

    class _FakeTool:
        def __init__(self, name):
            self.name = name; self.description = ""
            self.inputSchema = {"type": "object", "properties": {}}

    names = ["nap_ban_ve", "tinh_dai_luong", "hoi_de_hoc", "doi_chieu_nghi_ngo", "hoc_quy_uoc", "thu_hoi_quy_uoc"]
    tools = mcp_bridge.gemini_tools([_FakeTool(n) for n in names])
    exposed = {d.name for t in tools for d in t.function_declarations}
    _emit("INV-10: hoc_quy_uoc & thu_hoi_quy_uoc & nap_ban_ve KHÔNG phơi cho LLM; tool đọc (tinh_dai_luong/hoi_de_hoc) CÓ",
          exposed.isdisjoint({"hoc_quy_uoc", "thu_hoi_quy_uoc", "nap_ban_ve"})
          and {"tinh_dai_luong", "hoi_de_hoc", "doi_chieu_nghi_ngo"} <= exposed)

    # ---- INV-12: grep-guard — mọi truy cập THẬT self.hoc_phien nằm trong hàm cho phép ----
    # Dùng tokenize (KHÔNG regex thô) -> KHÔNG dính self.hoc_phien trong docstring/comment (đó là STRING/COMMENT token).
    ALLOWED = ("hoc_quy_uoc", "thu_hoi_quy_uoc", "_quy_tac_hieu_luc", "_extract")   # +_extract = init 'self.hoc_phien = []'
    _defline = re.compile(r"^(?:    def|def)\s+(\w+)\s*\(")   # def cấp method (thụt 4) hoặc module-level

    def _access_lines(path):
        out = set()
        with open(path, "rb") as f:
            toks = list(tokenize.tokenize(f.readline))
        for i in range(len(toks) - 2):
            a, b, c = toks[i], toks[i + 1], toks[i + 2]
            if (a.type == tokenize.NAME and a.string == "self" and b.type == tokenize.OP and b.string == "."
                    and c.type == tokenize.NAME and c.string == "hoc_phien"):
                out.add(a.start[0])   # truy cập THẬT (self.hoc_phien) — string/comment KHÔNG lọt vì là 1 token STRING/COMMENT
        return out

    def _def_at(defs, line):
        cur = "?"
        for (ln, name) in defs:
            if ln <= line: cur = name
            else: break
        return cur

    viol = []
    for path in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):   # ĐỆ QUY (bền hơn danh sách cứng)
        p = path.replace("\\", "/")
        if "/tests/" in p or "/vendor/" in p or "/spikes/" in p or "/__pycache__/" in p:
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            defs = [(i, m.group(1)) for i, ln in enumerate(f, 1) for m in [_defline.match(ln)] if m]
        for line in sorted(_access_lines(path)):
            cur = _def_at(defs, line)
            if cur not in ALLOWED:
                viol.append((os.path.basename(path), cur, line))
    _emit("INV-12: mọi truy cập THẬT self.hoc_phien nằm trong %s (đọc TẬP TRUNG, không rải rác)" % (ALLOWED,), not viol)
    if viol:
        for v in viol:
            print("     VI PHẠM:", v)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
