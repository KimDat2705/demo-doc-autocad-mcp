# -*- coding: utf-8 -*-
"""L5 (kho kiến thức — CONFIRM-ONLY, chỉ NGƯỜI bấm) — TẤT ĐỊNH, offline, KHÔNG tốn API.
Khoá: fail-closed 3 lớp (kb_id + option ∈ ENUM + ĐÃ-PHÁT) + state (xác nhận/không-chắc/thu-hồi/hỏi-lại)
+ KHÔNG đổi số + LLM-exclusion 2 hàng rào (declaration + dispatch L0) + collector kb_cau_hoi cho frontend
+ endpoint /xac-nhan (400 khi chưa nạp; pass-through; KHÔNG qua chat) + PAGE có hook nút bấm.
Chạy: python tests/test_kb_xacnhan.py"""
import os, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("READFILE_MAX_MB", "300")

import ezdxf
import tools_core
import mcp_bridge as MB

PASS = FAIL = 0


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def lam(texts):
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for (x, y, s) in texts:
        msp.add_text(s).set_placement((x, y))
    p = os.path.join(tempfile.mkdtemp(), "t.dxf"); doc.saveas(p)
    return tools_core.Drawing(p)


def main():
    print("[L5] xác nhận confirm-only: fail-closed + state + host-only + endpoint + frontend hook")

    # ---- [X1] FAIL-CLOSED 3 lớp ----
    d = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    kb = d.phan_loai_tin_hieu("ĐC-1").get("_kb") or {}
    _emit("X1a: câu hỏi phát kèm 'ma' echo cho frontend", kb.get("ma") == "ĐC-1" and "cau_hoi" in kb)
    _emit("X1b: kb_id lạ -> tu_choi kb_id_la", d.xac_nhan_ky_hieu("xyz_la", "dam", "ĐC-1").get("tu_choi") == "kb_id_la")
    _emit("X1c: option ngoài ENUM -> tu_choi option_la",
          d.xac_nhan_ky_hieu("dc_dai_coc", "bay_bia", "ĐC-1").get("tu_choi") == "option_la")
    d_moi = lam([(0, 0, "ĐC-9")])
    _emit("X1d: câu hỏi CHƯA PHÁT trong phiên -> tu_choi chua_phat (không xác nhận khống)",
          d_moi.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "ĐC-9").get("tu_choi") == "chua_phat")

    # ---- [X2] FLOW: xác nhận -> nhãn -> thu hồi -> hỏi lại được ----
    rc = d.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "ĐC-1")
    _emit("X2a: xác nhận hợp lệ -> ok + ket_qua da_xac_nhan + mô tả nghĩa",
          rc.get("ok") is True and rc.get("ket_qua") == "da_xac_nhan" and "đài cọc" in rc.get("nghia_mo_ta", ""))
    _emit("X2b: ghi_chu nêu rõ KHÔNG đổi số + hiệu lực phiên file", "KHÔNG con số" in rc.get("ghi_chu", ""))
    r_re = d._kb_cau_hoi_neu_can("ĐC-1") or {}
    _emit("X2c: tra lại sau xác nhận -> nhãn 'theo xác nhận trong phiên file này', KHÔNG hỏi lại",
          r_re.get("da_xac_nhan") is True and r_re.get("nghia_key") == "dai_coc"
          and r_re.get("ghi_chu") == "theo xác nhận trong phiên file này")
    rt = d.xac_nhan_ky_hieu("dc_dai_coc", "", "ĐC-1", thu_hoi=True)
    _emit("X2d: thu_hoi -> ok + da_thu_hoi", rt.get("ok") is True and rt.get("da_thu_hoi") is True)
    _emit("X2e: sau thu_hoi -> hỏi lại ĐƯỢC (câu hỏi đầy đủ)", "cau_hoi" in (d._kb_cau_hoi_neu_can("ĐC-1") or {}))

    # ---- [X3] 'khac_khong_chac' = giữ trạng thái bí, không nhãn, không hỏi lại ----
    rk = d.xac_nhan_ky_hieu("dc_dai_coc", "khac_khong_chac", "ĐC-1")
    _emit("X3a: khac_khong_chac -> ok + ket_qua khong_chac (KHÔNG dán nhãn nghĩa)",
          rk.get("ok") is True and rk.get("ket_qua") == "khong_chac" and "nghia_key" not in rk)
    _emit("X3b: state = da_hoi_bo_qua + tra lại chỉ note (suppress re-ask)",
          d.kb_hoi.get("dc_dai_coc|djc-1") == "da_hoi_bo_qua"
          and (d._kb_cau_hoi_neu_can("ĐC-1") or {}).get("da_hoi_trong_phien") is True)

    # ---- [X4] HOST-ONLY 2 hàng rào: declaration + dispatch (L0) ----
    class _T:
        def __init__(self, n):
            self.name = n; self.description = ""
            self.inputSchema = {"type": "object", "properties": {}}
    fake = [_T("xac_nhan_ky_hieu"), _T("tim_kiem"), _T("hoi_de_hoc")]
    exposed = {dd.name for t in MB.gemini_tools(fake) for dd in t.function_declarations}
    _emit("X4a: 'xac_nhan_ky_hieu' KHÔNG trong declaration cho Gemini", "xac_nhan_ky_hieu" not in exposed)
    _emit("X4b: 'xac_nhan_ky_hieu' KHÔNG trong tập dispatch (L0) — AI phát đúng tên cũng bị chặn",
          "xac_nhan_ky_hieu" not in MB._ten_tool_cho_llm(fake) and "tim_kiem" in MB._ten_tool_cho_llm(fake))

    # ---- [X5] collector kb_cau_hoi cho frontend ----
    acc = []
    MB._kb_hoi_tu_result({"_kb": kb}, acc)                          # top-level
    MB._kb_hoi_tu_result({"nghi_ngo": [{"_kb": kb}]}, acc)          # nested (dedupe)
    MB._kb_hoi_tu_result({"_kb": {"id": "x", "da_hoi_trong_phien": True}}, acc)   # note -> bỏ
    MB._kb_hoi_tu_result("khong_phai_dict", acc)                    # fail-open
    _emit("X5: collector gom top-level + nested, DEDUPE, bỏ note, fail-open", len(acc) == 1)

    # ---- [X6] endpoint /xac-nhan (Flask test_client, offline) ----
    import app as A
    c = A.app.test_client()
    r400 = c.post("/xac-nhan", json={"kb_id": "dc_dai_coc", "option_key": "dai_coc"})
    _emit("X6a: chưa nạp bản vẽ -> 400 + ok=False", r400.status_code == 400 and r400.get_json().get("ok") is False)

    class _FB:                                    # fake bridge: pass-through để soi args tới đúng tool
        def call(self, name, args): return {"ok": True, "echo_tool": name, "echo": dict(args)}
    with A._SESS_LOCK:
        for v in A.SESSIONS.values(): v["bridge"] = _FB()
    r200 = c.post("/xac-nhan", json={"kb_id": "dc_dai_coc", "option_key": "dai_coc", "ma": "ĐC-1"})
    j = r200.get_json() or {}
    _emit("X6b: pass-through đúng tool 'xac_nhan_ky_hieu' + đủ args",
          r200.status_code == 200 and j.get("echo_tool") == "xac_nhan_ky_hieu"
          and j.get("echo", {}).get("kb_id") == "dc_dai_coc" and j.get("echo", {}).get("ma") == "ĐC-1")
    with A._SESS_LOCK:                            # dọn: trả phiên về không-bridge (không rò sang test khác)
        for v in A.SESSIONS.values(): v["bridge"] = None

    # ---- [X7] frontend PAGE có hook nút bấm + esc chống chèn thuộc tính ----
    _emit("X7a: PAGE có '/xac-nhan' + kbHtml + xacNhanBtn (nút bấm render từ kb_cau_hoi)",
          "/xac-nhan" in A.PAGE and "kbHtml" in A.PAGE and "xacNhanBtn" in A.PAGE and "kb_cau_hoi" in A.PAGE)
    _emit("X7b: esc() escape cả dấu nháy kép (chống chèn thuộc tính qua mã người gõ)", "&quot;" in A.PAGE)

    # ---- [X8] tra_loi_ai trả 'kb_cau_hoi' ở điểm trả thành công (source-guard) ----
    src = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    _emit("X8: các return thành công của tra_loi_ai mang 'kb_cau_hoi'",
          src.count('"kb_cau_hoi": kb_cau_hoi') >= 3 and "_kb_hoi_tu_result(result, kb_cau_hoi)" in src)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
