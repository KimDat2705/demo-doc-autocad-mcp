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

    # ---- [X9] LÁT 1 — cổng fail-closed khoá theo ĐÚNG MÃ (bug: hỏi 1 mã mở khoá MỌI mã) ----
    d9 = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    d9.phan_loai_tin_hieu("ĐC-1")                      # hệ CHỈ hỏi về ĐC-1
    _emit("X9a: xác nhận cho mã KHÁC (hệ chưa hỏi) -> tu_choi chua_phat",
          d9.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "MA-KHAC-999").get("tu_choi") == "chua_phat")
    _emit("X9b: xác nhận cho mã KHÔNG TỒN TẠI trong bản vẽ -> tu_choi chua_phat",
          d9.xac_nhan_ky_hieu("dc_dai_coc", "dam", "ZZZ-404").get("tu_choi") == "chua_phat")
    _emit("X9c: ma='' (lấn không gian khoá kênh CAO ĐỘ) -> tu_choi chua_phat",
          d9.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "").get("tu_choi") == "chua_phat")
    _emit("X9d: xác nhận ĐÚNG mã đã hỏi -> vẫn chạy bình thường (không siết oan)",
          d9.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "ĐC-1").get("ket_qua") == "da_xac_nhan")
    _emit("X9e: kb_da_phat lưu BỘ BA (entry, option, ma_key) — không còn cặp 2 phần tử",
          all(len(t) == 3 for t in d9.kb_da_phat) and ("dc_dai_coc", "dai_coc", "djc-1") in d9.kb_da_phat)

    # ---- [X10] LÁT 0 — undo TRUNG THỰC (bug: luôn ok=True + 'đã gỡ (nếu có)') ----
    d10 = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    d10.phan_loai_tin_hieu("ĐC-1"); d10.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "ĐC-1")
    r10a = d10.xac_nhan_ky_hieu("dc_dai_coc", "", "CHUA-TUNG-BAM", thu_hoi=True)
    _emit("X10a: gỡ mã CHƯA từng bấm -> ok=False + tu_choi khong_co_gi_de_go (KHÔNG báo đã gỡ)",
          r10a.get("ok") is False and r10a.get("da_thu_hoi") is False
          and r10a.get("tu_choi") == "khong_co_gi_de_go" and "Đã gỡ" not in r10a.get("ly_do", ""))
    r10b = d10.xac_nhan_ky_hieu("dc_dai_coc", "", "DC-1", thu_hoi=True)   # trượt khoá đ/d (bản vá id84)
    _emit("X10b: gỡ TRƯỢT KHOÁ ('DC-1' vs khoá 'djc-1') -> ok=False, state CÒN NGUYÊN",
          r10b.get("ok") is False and ("dc_dai_coc|djc-1" in d10.kb_xacnhan))
    r10c = d10.xac_nhan_ky_hieu("dc_dai_coc", "", "ĐC-1", thu_hoi=True)
    _emit("X10c: gỡ ĐÚNG khoá -> ok=True + da_thu_hoi=True + loai_da_go='xac_nhan' + state sạch",
          r10c.get("ok") is True and r10c.get("da_thu_hoi") is True
          and r10c.get("loai_da_go") == "xac_nhan" and not d10.kb_xacnhan)
    _emit("X10d: sau khi gỡ -> câu hỏi HỎI LẠI được", "cau_hoi" in (d10._kb_cau_hoi_neu_can("ĐC-1") or {}))

    # ---- [X11] LÁT 2 — 'khác/không chắc' PHẢI gỡ được (trước: khoá câu hỏi tới hết phiên) ----
    d11 = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    d11.phan_loai_tin_hieu("ĐC-1"); d11.xac_nhan_ky_hieu("dc_dai_coc", "khac_khong_chac", "ĐC-1")
    _emit("X11a: sau 'khác/không chắc' -> câu hỏi tạm ẩn (hành vi cũ giữ nguyên)",
          "cau_hoi" not in (d11._kb_cau_hoi_neu_can("ĐC-1") or {}))
    ds = d11.danh_sach_xac_nhan()
    _emit("X11b: danh_sach_xac_nhan LIỆT KÊ cả mục 'bỏ qua' (để gỡ được)",
          ds.get("so_muc") == 1 and ds["cac_muc"][0]["loai"] == "bo_qua")
    r11 = d11.xac_nhan_ky_hieu("dc_dai_coc", "", "ĐC-1", thu_hoi=True)
    _emit("X11c: gỡ 'khác/không chắc' -> ok=True + loai_da_go='trang_thai_hoi'",
          r11.get("ok") is True and r11.get("loai_da_go") == "trang_thai_hoi")
    _emit("X11d: câu hỏi QUAY LẠI sau khi gỡ (hết khoá vĩnh viễn)",
          "cau_hoi" in (d11._kb_cau_hoi_neu_can("ĐC-1") or {})
          and d11.danh_sach_xac_nhan().get("so_muc") == 0)

    # ---- [X12] LÁT 2 — endpoint danh sách + frontend nút Hoàn tác ----
    import app as A12
    _emit("X12a: PAGE có nút '↩ Hoàn tác' + gửi cờ thu_hoi + bảng xnbox thường trực",
          "Hoàn tác" in A12.PAGE and "thu_hoi:true" in A12.PAGE
          and "hoanTacBtn" in A12.PAGE and "xnbox" in A12.PAGE and "taiDanhSach" in A12.PAGE)
    _emit("X12b: frontend kiểm 'da_thu_hoi' (KHÔNG kiểm r.ok) khi hoàn tác — chống undo nói dối",
          "r.da_thu_hoi" in A12.PAGE)
    _emit("X12c: route /xac-nhan/danh-sach có mặt",
          any(str(r.rule) == "/xac-nhan/danh-sach" for r in A12.app.url_map.iter_rules()))

    # ---- [X13] RED-TEAM CAO-1 — hệ HỎI thì PHẢI chấp nhận chính câu nó hỏi (lệch khoá strip/truncate) ----
    d13 = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    kb13 = (d13.phan_loai_tin_hieu("ĐC-1 ") or {}).get("_kb") or {}      # mã có khoảng trắng thừa
    _emit("X13a: mã có KHOẢNG TRẮNG thừa -> bấm đúng nút hệ render = được chấp nhận",
          d13.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", kb13.get("ma", "")).get("ket_qua") == "da_xac_nhan")
    d13b = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    MA_DAI = "ĐC-1 (SL-25) trục A-B mong khu nha xe tang ham"           # 46 ký tự > trần 40
    it13 = [n for n in d13b.doi_chieu_nghi_ngo(MA_DAI).get("nghi_ngo", []) if n.get("_kb")]
    kb13b = it13[0]["_kb"] if it13 else {}
    _emit("X13b: mã DÀI >40 (bị cắt khi echo) -> bấm nút hệ render vẫn được chấp nhận",
          len(kb13b.get("ma", "")) == 40
          and d13b.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", kb13b["ma"]).get("ket_qua") == "da_xac_nhan")
    _emit("X13c: và GỠ lại được bằng đúng mã đó (không kẹt chết như trước)",
          d13b.xac_nhan_ky_hieu("dc_dai_coc", "", kb13b.get("ma", ""), thu_hoi=True).get("da_thu_hoi") is True)

    # ---- [X14] RED-TEAM TB — xác nhận xong thì doi_chieu KHÔNG đòi xác nhận lại (2 kênh không nói ngược) ----
    d14 = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    d14.doi_chieu_nghi_ngo("ĐC-1"); d14.xac_nhan_ky_hieu("dc_dai_coc", "dai_coc", "ĐC-1")
    r14 = d14.doi_chieu_nghi_ngo("ĐC-1")
    _emit("X14: sau xác nhận -> doi_chieu KHÔNG còn item 'đa nghĩa ký hiệu' đòi xác nhận",
          not any(n.get("loai") == "đa nghĩa ký hiệu (kho kiến thức)" for n in r14.get("nghi_ngo", [])))

    # ---- [X15] RED-TEAM THẤP — bảng hiện mã NGƯỜI ĐỌC, không phơi khoá nội bộ ----
    d15 = lam([(0, 0, "ĐC-1"), (5000, 0, "DC-1")])
    d15.phan_loai_tin_hieu("ĐC-1"); d15.xac_nhan_ky_hieu("dc_dai_coc", "khac_khong_chac", "ĐC-1")
    _emit("X15: mục 'bỏ qua' hiện 'ĐC-1' (KHÔNG phải khoá nội bộ 'djc-1')",
          (d15.danh_sach_xac_nhan()["cac_muc"] or [{}])[0].get("ma") == "ĐC-1")

    # ---- [X16] RED-TEAM CAO-2 — route xác nhận KHÔNG được tạo phiên (chống đuổi phiên đối tác qua LRU) ----
    import app as A16
    c16 = A16.app.test_client()
    with A16._SESS_LOCK:
        A16.SESSIONS.clear()
    for _ in range(6):
        c16.get("/xac-nhan/danh-sach")
    c16.post("/xac-nhan", json={"kb_id": "dc_dai_coc", "option_key": "dai_coc"})
    _emit("X16a: 6 GET danh-sách + 1 POST VÔ DANH -> KHÔNG tạo phiên nào (không đẩy LRU)",
          len(A16.SESSIONS) == 0, str(len(A16.SESSIONS)))
    _emit("X16b: app.py dùng _phien_hien_co() (không get_session) ở CẢ 2 route xác nhận",
          open(os.path.join(ROOT, "app.py"), encoding="utf-8").read().count("_phien_hien_co()") >= 2)

    # ---- [X17] RED-TEAM THẤP — thu_hoi ép kiểu CHẶT (chuỗi 'false' KHÔNG được hiểu là gỡ) ----
    src17 = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    _emit("X17: /xac-nhan không dùng bool(d.get('thu_hoi')) trần (chuỗi 'false' là truthy)",
          'bool(d.get("thu_hoi"))' not in src17 and '_th.strip().lower() in ("1", "true", "yes")' in src17)

    # ---- [X18] RED-TEAM CAO-3 — bảng tự làm mới lúc tải trang + sau khi nạp file khác ----
    _emit("X18: PAGE gọi taiDanhSach() ở init VÀ trong showSum (không giữ mục của file cũ)",
          src17.count("taiDanhSach()") >= 5 and "ready(true);taiDanhSach();" in src17)

    # ---- [X4] HOST-ONLY 2 hàng rào: declaration + dispatch (L0) ----
    class _T:
        def __init__(self, n):
            self.name = n; self.description = ""
            self.inputSchema = {"type": "object", "properties": {}}
    fake = [_T("xac_nhan_ky_hieu"), _T("danh_sach_xac_nhan"), _T("tim_kiem"), _T("hoi_de_hoc")]
    exposed = {dd.name for t in MB.gemini_tools(fake) for dd in t.function_declarations}
    _emit("X4a: 'xac_nhan_ky_hieu' + 'danh_sach_xac_nhan' KHÔNG trong declaration cho Gemini",
          exposed.isdisjoint({"xac_nhan_ky_hieu", "danh_sach_xac_nhan"}))
    _emit("X4b: cả 2 tool xác nhận KHÔNG trong tập dispatch (L0) — AI phát đúng tên cũng bị chặn",
          MB._ten_tool_cho_llm(fake).isdisjoint({"xac_nhan_ky_hieu", "danh_sach_xac_nhan"})
          and "tim_kiem" in MB._ten_tool_cho_llm(fake))

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
    # RT-fix (CAO-2): route xác nhận KHÔNG còn TỰ TẠO phiên -> test phải DỰNG phiên tường minh (đúng ý định
    # hơn bản cũ, vốn ăn ké phiên do chính get_session() trong route sinh ra).
    import threading as _th6, time as _t6
    _sid6 = "test-sid-xacnhan"
    with A._SESS_LOCK:
        A.SESSIONS[_sid6] = {"bridge": _FB(), "summary": "", "history": [],
                             "lock": _th6.Lock(), "last": _t6.time(), "artifacts": set()}
    c.set_cookie("sid", _sid6)
    r200 = c.post("/xac-nhan", json={"kb_id": "dc_dai_coc", "option_key": "dai_coc", "ma": "ĐC-1"})
    j = r200.get_json() or {}
    _emit("X6b: pass-through đúng tool 'xac_nhan_ky_hieu' + đủ args",
          r200.status_code == 200 and j.get("echo_tool") == "xac_nhan_ky_hieu"
          and j.get("echo", {}).get("kb_id") == "dc_dai_coc" and j.get("echo", {}).get("ma") == "ĐC-1")
    with A._SESS_LOCK:                            # dọn: xoá phiên test (không rò sang test khác)
        A.SESSIONS.pop(_sid6, None)

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
