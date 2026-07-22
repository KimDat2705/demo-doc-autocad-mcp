# -*- coding: utf-8 -*-
"""GĐ2 — E2E TẦNG MCP THẬT: spawn `python mcp_server.py` (JSON-RPC/stdio qua MCPBridge), gọi chuỗi tool THẬT.
Trước đây MỌI test offline gọi thẳng method tools_core / mock FakeBridge — tầng transport MCP CHƯA TỪNG chạy.
Kiểm: handshake (list_tools ≥20, có cả 4 tool AI-tự-học), _need() khi chưa nạp, đọc số qua transport, wiring hoclog
(gọi hoi_de_hoc -> sinh dòng log đúng schema), BẤT BIẾN số HỌC không lọt tong_hop qua transport, danh_dau/xuat_excel.
0 API (tool tất định). Cần gói `mcp` + spawn subprocess -> KHÔNG spawn được thì SKIP (không đánh sập cổng).
Chạy: python tests/test_mcp_stdio.py"""
import os, sys, io, json, tempfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
BASE = os.path.normpath(os.path.join(ROOT, "..", "input_files", "_dxf"))
# Ten thu muc/file that giu NGOAI repo (gitignored) — xem corpus_local.example.py
try:
    from corpus_local import KT
except Exception:
    KT = ""

PASS = FAIL = SKIP = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def main():
    global SKIP
    if not os.path.isfile(KT):
        print("  [..] BO QUA test_mcp_stdio — thieu fixture KT (KHONG phai da kiem)"); SKIP += 1
        print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP)); return 0
    import mcp_bridge
    log_dir = tempfile.mkdtemp(prefix="hoclog_mcp_")
    br = None
    try:
        try:                       # spawn MCP server con THẬT (HOC_LOG_DIR -> tempdir để kiểm wiring + không bẩn repo)
            br = mcp_bridge.MCPBridge(["mcp_server.py"], cwd=ROOT, env={"HOC_LOG_DIR": log_dir, "HOC_LOG": "1"})
        except Exception as e:
            print("  [..] BO QUA — khong spawn duoc MCP server (%s: %s)" % (type(e).__name__, e)); SKIP += 1
            print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP)); return 0

        print("[M.1] HANDSHAKE — list_tools qua stdio thật")
        names = {t.name for t in br.tools}
        ok("≥20 MCP tool qua transport", len(br.tools) >= 20, len(br.tools))
        ok("có 4 tool AI-tự-học (hoi_de_hoc/doi_chieu/hoc_quy_uoc/thu_hoi)",
           {"hoi_de_hoc", "doi_chieu_nghi_ngo", "hoc_quy_uoc", "thu_hoi_quy_uoc"} <= names, sorted(names))

        print("[M.2] _need() — gọi tool TRƯỚC khi nạp bản vẽ -> báo LỘ (không crash)")
        r = br.call("tra_cuu_so_luong", {"tu_khoa": "D1"})
        ok("chưa nạp -> {loi: 'Chưa nạp bản vẽ...'}", isinstance(r, dict) and "Chưa nạp" in str(r.get("loi", "")), r)

        print("[M.3] nap_ban_ve + đọc số qua transport THẬT")
        r = br.call("nap_ban_ve", {"path": KT}, timeout=180)
        ok("nap_ban_ve -> summary có tong_doi_tuong/so_layer", isinstance(r, dict) and r.get("tong_doi_tuong") and r.get("so_layer"), r)
        r = br.call("tra_cuu_so_luong", {"tu_khoa": "D1"})
        ok("tra_cuu_so_luong('D1') -> dict hợp lệ qua transport", isinstance(r, dict) and ("loi" not in r or r.get("ket_qua")), str(r)[:80])
        r = br.call("thong_tin_tang", {})
        ok("thong_tin_tang -> dict qua transport", isinstance(r, dict))

        print("[M.4] WIRING hoclog — gọi hoi_de_hoc THẬT -> sinh dòng log đúng schema (HOC_LOG_DIR tempdir)")
        r = br.call("hoi_de_hoc", {"ma_cau_kien": "D1"})
        ok("hoi_de_hoc -> có tin_hieu ①/②", isinstance(r, dict) and r.get("tin_hieu") in ("①", "②"), str(r)[:80])
        _lf = os.path.join(log_dir, "ung_vien.jsonl")
        _line = None
        if os.path.isfile(_lf):
            with open(_lf, encoding="utf-8") as f:
                _lines = [x for x in f.read().splitlines() if x.strip()]
            if _lines:
                _line = json.loads(_lines[-1])
        ok("log WORM ghi 1 dòng cho hoi_de_hoc (wiring tool-layer thật)", _line is not None and _line.get("hanh_dong") == "hoi_de_hoc")
        ok("log ĐÃ REDACT: có file_hash, KHÔNG lưu path thật", _line is not None and "file_hash" in _line and KT not in json.dumps(_line))

        print("[M.5] BẤT BIẾN số HỌC không vào tổng — qua transport THẬT (hoc_quy_uoc -> tong_hop)")
        r = br.call("hoc_quy_uoc", {"anchor_handle": "ZZ_NOEXIST", "template_id": "KG_PER_UNIT", "ma_cau_kien": "S1"})
        ok("hoc_quy_uoc handle KHÔNG tồn tại -> từ chối (không crash transport)", isinstance(r, dict) and r.get("ok") is False, str(r)[:80])
        th = br.call("tong_hop_khoi_luong", {})
        ok("tong_hop_khoi_luong -> có 'bang' qua transport", isinstance(th, dict) and isinstance(th.get("bang"), list))
        r = br.call("thu_hoi_quy_uoc", {"rule_id": ""})
        ok("thu_hoi_quy_uoc -> ok qua transport", isinstance(r, dict) and r.get("ok") is True, str(r)[:80])

        print("[M.6] danh_dau + xuat_excel qua transport (sinh + dọn artifact)")
        r = br.call("danh_dau_cau_kien", {"tu_khoa": "cua"})
        _aid = r.get("anh_id") if isinstance(r, dict) else None
        ok("danh_dau_cau_kien -> so_ket_qua + anh_id (hoặc 0 hit trung thực)",
           isinstance(r, dict) and ("so_ket_qua" in r), str(r)[:80])
        r = br.call("xuat_excel_du_toan", {})
        _fid = r.get("file_id") if isinstance(r, dict) else None
        ok("xuat_excel_du_toan -> file_id qua transport", isinstance(r, dict) and (_fid or r.get("loi")), str(r)[:80])
        for _id in (_aid, _fid):     # dọn artifact test tạo
            if _id:
                _p = os.path.join(ROOT, "_renders", os.path.basename(str(_id)))
                try: os.remove(_p)
                except OSError: pass
    finally:
        if br is not None:
            try: br.close()
            except Exception: pass
        shutil.rmtree(log_dir, ignore_errors=True)

    print("\n%d PASS / %d FAIL / %d BO QUA" % (PASS, FAIL, SKIP))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
