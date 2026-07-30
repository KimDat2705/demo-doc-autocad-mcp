# -*- coding: utf-8 -*-
"""GATE SỐ BẢN VẼ (MAX_BAN_VE) — chặn ở CỬA VÀO thay vì để tràn RAM. TẤT ĐỊNH, OFFLINE, KHÔNG tốn API,
KHÔNG spawn subprocess (FakeBridge). Chạy:  python tests/test_admission.py

VÌ SAO CÓ GATE NÀY (đo thật 2026-07-30 — số Windows WorkingSet, gói free 512MB):
  web 104.9MB + 1 bản vẽ .dxf 23.31MiB = 289.2MB -> 394.1MB (77%) · 2 bản vẽ như vậy -> 683MB = OOM.
  Và MAX_SESSIONS KHÔNG bound được RAM: ma trận cap-vs-thread 5/5 cấu hình cho thấy số bản vẽ trong RAM
  bằng SỐ REQUEST ĐỒNG THỜI (--threads), không phụ thuộc cap (cap=2/threads=4 VẪN 4 bản vẽ).
  Đo thật lỗ cũ: MAX_SESSIONS=4 + 4 upload đang treo + 5 người mới -> 9 bridge sống, CẢ 9 trả HTTP 200.

MỖI CA DƯỚI ĐÂY LÀ 1 LỖ RED-TEAM ĐÃ LÀM VỠ bản thiết kế đầu (2 lỗ mức CHẶN) — không phải test cho đẹp:
  A.2/A.6 cửa vào thật sự chặn · A.4/A.5 degrade-safe · A.7 TOCTOU · A.8/A.9 fail-closed CÓ kế toán + tự lành
  A.10 KHÔNG rỉ suất qua các đường ra 400/413/500 (lỗ CHẶN: 1 request .txt làm app tự khoá mình VĨNH VIỄN)
  A.11 nói THẬT khi bản vẽ bị nhường (không im lặng mất bản vẽ)
"""
import os, sys, io, time, threading
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))
import app as A

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


MADE = []


class FakeBridge:
    """close(cho_giay) trả True = 'đã xác nhận chết' (khớp chữ ký MCPBridge.close)."""
    chet_duoc = True            # đặt False để mô phỏng close() HẾT GIỜ (ca A.8)

    def __init__(self):
        self.id = len(MADE) + 1
        self.closed = False
        MADE.append(self)

    def call(self, name, args, timeout=120):
        return {"name": os.path.basename(args.get("path", "x")), "dxfversion": "AC1032",
                "tong_doi_tuong": 10, "so_layer": 3}

    def close(self, cho_giay=0.0):
        self.closed = True
        return bool(FakeBridge.chet_duoc)


def _fake_tra_loi(bridge, q, summary="", history=None):
    return {"answer": "sum=%s|br=%d" % (summary, getattr(bridge, "id", -1)), "evidence": [], "ai": True}


def _reset():
    with A._SESS_LOCK:
        for sid in list(A.SESSIONS):
            A._close_session(sid)
    MADE.clear()
    FakeBridge.chet_duoc = True


def _upload(client, fname, kb=1):
    return client.post("/upload", data={"file": (io.BytesIO(b"0" * kb), fname)},
                       content_type="multipart/form-data")


def _dem():
    with A._SESS_LOCK:
        return A._dem_ban_ve()


def main():
    _mk, _tl, _ua = A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI
    _ms, _mbv, _lw, _rf = A.MAX_SESSIONS, A.MAX_BAN_VE, A.LOCK_WAIT_S, A.READFILE_MAX_MB
    A._make_bridge = lambda: FakeBridge()
    A.mcp_bridge.tra_loi_ai = _fake_tra_loi
    A.mcp_bridge.USE_AI = True
    A.MAX_SESSIONS, A.LOCK_WAIT_S = 8, 1
    upl = set()
    try:
        print("[A.1] trần=1, phiên A RẢNH -> B được vào; A bị NHƯỜNG chỗ nhưng PHIÊN vẫn còn (không pop)")
        _reset(); A.MAX_BAN_VE = 1
        ca, cb = A.app.test_client(), A.app.test_client()
        ra = _upload(ca, "a1.dxf"); upl.add("a1.dxf")
        ok("A upload 200", ra.status_code == 200, ra.status_code)
        sid_a = list(A.SESSIONS)[0]
        s_a = A.SESSIONS[sid_a]
        s_a["artifacts"].add("anh_cu.png")
        br_a = s_a["bridge"]
        rb = _upload(cb, "b1.dxf"); upl.add("b1.dxf")
        ok("B upload 200 (được nhường chỗ)", rb.status_code == 200, rb.status_code)
        ok("bridge của A ĐÃ đóng (bản vẽ ra khỏi RAM)", br_a.closed is True)
        ok("phiên A VẪN trong SESSIONS (KHÔNG pop) -> ảnh khoanh đỏ cũ không thành 404",
           sid_a in A.SESSIONS and "anh_cu.png" in A.SESSIONS[sid_a]["artifacts"])
        ok("phiên A có cờ da_nhuong (để /ask nói THẬT)", A.SESSIONS[sid_a].get("da_nhuong") is True)
        ok("số bản vẽ trong RAM vẫn = 1 (không bao giờ 2)", _dem() == 1, _dem())

        print("[A.2] trần=1, phiên A ĐANG BẬN -> B bị TỪ CHỐI tử tế, KHÔNG tạo bridge mới")
        _reset(); A.MAX_BAN_VE = 1
        ca, cb = A.app.test_client(), A.app.test_client()
        _upload(ca, "a2.dxf"); upl.add("a2.dxf")
        s_a = A.SESSIONS[list(A.SESSIONS)[0]]
        s_a["lock"].acquire()                       # giả lập A đang /ask
        try:
            n_truoc = len(MADE)
            rb = _upload(cb, "b2.dxf"); upl.add("b2.dxf")
            ok("B -> HTTP 503 (chặn ở cửa, không đi vào OOM)", rb.status_code == 503, rb.status_code)
            jb = rb.get_json() or {}
            ok("thông báo tiếng Việt, không phải trang lỗi kỹ thuật",
               "bản vẽ" in (jb.get("error") or "").lower(), jb.get("error"))
            ok("body đủ error+answer+loi+ly_do + da_thu_hoi=False",
               all(jb.get(k) for k in ("error", "answer", "loi", "ly_do")) and jb.get("da_thu_hoi") is False, jb)
            ok("KHÔNG tạo bridge mới (không tốn thêm RAM)", len(MADE) == n_truoc, (n_truoc, len(MADE)))
            ok("bridge của A KHÔNG bị đóng giữa request (bất biến F-A)", MADE[0].closed is False)
        finally:
            s_a["lock"].release()

        print("[A.3] nạp file THỨ HAI trong CÙNG phiên -> luôn được, không nhường ai, không bridge mới")
        _reset(); A.MAX_BAN_VE = 1
        ca = A.app.test_client()
        _upload(ca, "a3.dxf"); upl.add("a3.dxf")
        n1 = len(MADE)
        r2 = _upload(ca, "a3b.dxf"); upl.add("a3b.dxf")
        ok("upload lần 2 -> 200", r2.status_code == 200, r2.status_code)
        ok("KHÔNG spawn bridge mới (dùng lại tiến trình con)", len(MADE) == n1, (n1, len(MADE)))
        ok("số bản vẽ vẫn = 1", _dem() == 1, _dem())

        print("[A.4] MAX_BAN_VE=0 -> TẮT gate = đúng hành vi TRƯỚC bản vá (đường lùi khẩn cấp)")
        _reset(); A.MAX_BAN_VE = 0
        cs = [A.app.test_client() for _ in range(3)]
        ma = [_upload(c, "a4_%d.dxf" % i).status_code for i, c in enumerate(cs)]
        for i in range(3):
            upl.add("a4_%d.dxf" % i)
        ok("cả 3 phiên đều nạp được (gate tắt hoàn toàn)", ma == [200, 200, 200], ma)

        print("[A.5] env RÁC -> KHÔNG sập import app, về mặc định")
        ok("_env_int('X','1') với env rác trả mặc định", A._env_int("KHONG_TON_TAI_X", "1") == 1)
        os.environ["MAX_BAN_VE_THU"] = "abc"
        ok("_env_int đọc 'abc' -> mặc định 1 (không ném ValueError)", A._env_int("MAX_BAN_VE_THU", "1") == 1)
        os.environ.pop("MAX_BAN_VE_THU", None)

        print("[A.6] ĐUA 2 luồng upload cùng lúc (2 phiên khác nhau) -> KHÔNG bao giờ 2 bản vẽ")
        _reset(); A.MAX_BAN_VE = 1
        kq = {}
        dinh = {"max": 0}

        def _chay(i):
            c = A.app.test_client()
            kq[i] = _upload(c, "dua_%d.dxf" % i).status_code
            dinh["max"] = max(dinh["max"], _dem())

        ts = [threading.Thread(target=_chay, args=(i,)) for i in (1, 2)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(20)
        for i in (1, 2):
            upl.add("dua_%d.dxf" % i)
        ok("cả 2 request đều có phản hồi (không treo)", sorted(kq.keys()) == [1, 2], kq)
        ok("đỉnh số bản vẽ <= trần 1 trong suốt cuộc đua", dinh["max"] <= 1, dinh["max"])
        ok("kết thúc: đúng 1 bản vẽ trong RAM", _dem() == 1, _dem())

        print("[A.7] TOCTOU — phiên đang có request BAY (nap_tu mới) KHÔNG được ai nhường")
        _reset(); A.MAX_BAN_VE = 1
        ca, cb = A.app.test_client(), A.app.test_client()
        _upload(ca, "a7.dxf"); upl.add("a7.dxf")
        s_a = A.SESSIONS[list(A.SESSIONS)[0]]
        with A._SESS_LOCK:
            # Giả lập "request của CHÍNH A đang bay" ĐÚNG NHƯ SẢN PHẨM ghi nhận: bộ đếm request + mốc thời gian.
            # (Bản đầu chỉ đặt nap_tu; sau bản vá lỗi CHẶN 'bấm 2 lần', tín hiệu đang-bay là nap_dem — và trạng thái
            #  'nap_tu mới mà nap_dem=0' KHÔNG còn tồn tại được trong sản phẩm vì _tra_suat xoá cả hai cùng lúc.
            #  Ca 2-luồng THẬT của bất biến này là A.13.)
            s_a["nap_dem"], s_a["nap_tu"] = 1, time.time()
        br_a = s_a["bridge"]
        rb = _upload(cb, "b7.dxf"); upl.add("b7.dxf")
        ok("B bị TỪ CHỐI (không giật bản vẽ của phiên đang có request bay)", rb.status_code == 503, rb.status_code)
        ok("bridge của A KHÔNG bị đóng", br_a.closed is False)
        with A._SESS_LOCK:
            s_a["nap_dem"], s_a["nap_tu"] = 0, 0.0
        ok("không bao giờ có 2 phiên cùng co_ban_ve=True",
           sum(1 for v in A.SESSIONS.values() if v.get("co_ban_ve")) <= 1)

        print("[A.8] FAIL-CLOSED CÓ KẾ TOÁN — close() hết giờ -> từ chối, và bridge đó VẪN được đếm")
        _reset(); A.MAX_BAN_VE = 1
        ca, cb, cc = A.app.test_client(), A.app.test_client(), A.app.test_client()
        _upload(ca, "a8.dxf"); upl.add("a8.dxf")
        FakeBridge.chet_duoc = False                # close() không xác nhận chết được
        rb = _upload(cb, "b8.dxf"); upl.add("b8.dxf")
        ok("B -> 503 'đang dọn bộ nhớ' (KHÔNG nạp chồng lên bản vẽ chưa chắc đã chết)", rb.status_code == 503, rb.status_code)
        ok("bridge chưa xác nhận chết VẪN được đếm là đang giữ RAM (không thành RAM vô hình)", _dem() == 1, _dem())
        rc = _upload(cc, "c8.dxf"); upl.add("c8.dxf")
        ok("người thứ ba cũng bị chặn (fail-closed THẬT, không mở cửa vì kế toán tụt về 0)", rc.status_code == 503, rc.status_code)

        print("[A.9] TỰ LÀNH — khi bridge cũ thật sự chết thì cửa mở lại (không phải đợi TTL phiên)")
        FakeBridge.chet_duoc = True
        rc2 = _upload(cc, "c9.dxf"); upl.add("c9.dxf")
        ok("upload sau đó -> 200 (cờ dang_dong được gỡ, suất nhả)", rc2.status_code == 200, rc2.status_code)
        ok("số bản vẽ = 1", _dem() == 1, _dem())

        print("[A.10] KHÔNG RỈ SUẤT qua các đường ra 400/413/500 (lỗ CHẶN: app tự khoá mình VĨNH VIỄN)")
        _reset(); A.MAX_BAN_VE = 1
        c0 = A.app.test_client()
        r400 = c0.post("/upload", data={"file": (io.BytesIO(b"x"), "abc.txt")}, content_type="multipart/form-data")
        ok("upload .txt -> 400", r400.status_code == 400, r400.status_code)
        ok("sau 400: số bản vẽ = 0 (KHÔNG rỉ suất)", _dem() == 0, _dem())
        A.READFILE_MAX_MB = 0                        # ép mọi file vượt trần -> nhánh 413
        r413 = _upload(c0, "qua_to.dxf", kb=2048); upl.add("qua_to.dxf")
        A.READFILE_MAX_MB = _rf
        ok("upload quá trần -> 413", r413.status_code == 413, r413.status_code)
        ok("sau 413: số bản vẽ = 0 (KHÔNG rỉ suất)", _dem() == 0, _dem())

        class _BridgeLoi(FakeBridge):
            def call(self, name, args, timeout=120):
                return {"loi": "File khong phai DXF"}

        A._make_bridge = lambda: _BridgeLoi()
        r500 = _upload(c0, "rac.dxf"); upl.add("rac.dxf")
        A._make_bridge = lambda: FakeBridge()
        ok("nạp LỖI -> 500 + cờ reset_xac_nhan (sổ xác nhận của bản vẽ cũ đã mất)",
           r500.status_code == 500 and (r500.get_json() or {}).get("reset_xac_nhan") is True, r500.get_json())
        ok("sau 500: số bản vẽ = 0 (KHÔNG rỉ suất)", _dem() == 0, _dem())
        ok("sau 500: người MỚI vẫn vào được (cửa không bị khoá vĩnh viễn)",
           _upload(A.app.test_client(), "sau500.dxf").status_code == 200)
        upl.add("sau500.dxf")

        print("[A.11] NÓI THẬT — phiên bị nhường / nạp lỗi phải được BÁO, phiên chưa từng nạp giữ câu CŨ")
        _reset(); A.MAX_BAN_VE = 1
        ca, cb = A.app.test_client(), A.app.test_client()
        _upload(ca, "a11.dxf"); upl.add("a11.dxf")
        _upload(cb, "b11.dxf"); upl.add("b11.dxf")   # A bị nhường
        ans = (_ask_json(ca) or {}).get("answer", "")
        ok("A hỏi tiếp -> nói RÕ bản vẽ đã được nhường (không im lặng, không bịa)",
           "nhường" in ans and "tải lại" in ans.lower(), ans)
        xn = ca.post("/xac-nhan", json={"kb_id": "x", "option_key": "y", "ma": "z"})
        jxn = xn.get_json() or {}
        ok("A bấm xác nhận -> nói RÕ sổ đã reset + có ly_do (chống 'undo nói dối')",
           xn.status_code == 400 and "reset" in (jxn.get("ly_do") or "").lower(), jxn)
        ds = (ca.get("/xac-nhan/danh-sach").get_json() or {})
        ok("bảng xác nhận trả cờ da_reset (không ẩn bảng ÂM THẦM)", ds.get("da_reset") is True, ds)
        cz = A.app.test_client()
        ansz = (cz.post("/ask", json={"q": "hi"}).get_json() or {}).get("answer", "")
        ok("phiên CHƯA TỪNG nạp -> GIỮ NGUYÊN VĂN câu cũ (hợp đồng K.5)",
           ansz == "Chưa nạp bản vẽ cho phiên này. Hãy tải file .dxf/.dwg trước.", ansz)

        # === 4 ca DƯỚI ĐÂY do RED-TEAM-IMPLEMENTATION tìm ra (2026-07-30) — 42 ca đầu KHÔNG bắt được vì tất cả
        # đều TUẦN TỰ trong 1 luồng và đều đi qua FakeBridge "lịch sự". Đây là lớp lỗi CHÍNH BẢN VÁ sinh ra. ===
        print("[A.13] CHẶN(red-team): 2 upload ĐỒNG THỜI CÙNG PHIÊN không được xoá cờ đang-nạp của nhau")
        _reset(); A.MAX_BAN_VE = 1; A.LOCK_WAIT_S = 1

        class _BridgeCham(FakeBridge):
            def call(self, name, args, timeout=120):
                time.sleep(2.5)                      # mô phỏng parse file lớn
                return FakeBridge.call(self, name, args, timeout)

        A._make_bridge = lambda: _BridgeCham()
        ca = A.app.test_client()
        kq13, dinh13 = {}, {"max": 0}

        def _up_a(i):
            kq13[i] = _upload(ca, "a13_%d.dxf" % i).status_code

        t1 = threading.Thread(target=_up_a, args=(1,)); t1.start()
        time.sleep(0.4)
        t2 = threading.Thread(target=_up_a, args=(2,)); t2.start()
        time.sleep(0.3)
        # request 2 vừa thua khoá và ĐANG trong finally -> đây là khoảnh khắc cờ của request 1 từng bị xoá
        cb = A.app.test_client()
        time.sleep(1.2)
        r13b = _upload(cb, "b13.dxf")
        dinh13["max"] = max(dinh13["max"], _dem())
        for t in (t1, t2):
            t.join(20)
        for n in ("a13_1.dxf", "a13_2.dxf", "b13.dxf"):
            upl.add(n)
        A._make_bridge = lambda: FakeBridge()
        ok("request thứ 2 cùng phiên bị 503 (thua khoá) — đúng như trước", kq13.get(2) == 503, kq13)
        ok("PHIÊN KHÁC vào giữa lúc đó bị 503 (cờ đang-nạp KHÔNG bị xoá oan)", r13b.status_code == 503, r13b.status_code)
        ok("đỉnh số bản vẽ <= 1 trong suốt kịch bản (trước bản vá đo được 2, và 4 người = 4 bản vẽ)",
           dinh13["max"] <= 1, dinh13["max"])

        print("[A.14] CHẶN(red-team): nạp thất bại dạng THẬT ({'ket_qua': 'Error executing tool ...'}) phải LỘ")
        _reset(); A.MAX_BAN_VE = 1; A.LOCK_WAIT_S = 1

        class _BridgeIsError(FakeBridge):
            def call(self, name, args, timeout=120):
                # Hợp đồng THẬT khi tool NÉM trong tiến trình con (trước bản vá mcp_bridge: KHÔNG có khoá 'loi')
                return {"ket_qua": "Error executing tool nap_ban_ve: D:/x/_uploads/abc.dxf is not a DXF file"}

        A._make_bridge = lambda: _BridgeIsError()
        c14 = A.app.test_client()
        r14 = _upload(c14, "a14.dxf"); upl.add("a14.dxf")
        A._make_bridge = lambda: FakeBridge()
        j14 = r14.get_json() or {}
        ok("KHÔNG trả 200 '✅ Đã nạp' (trước bản vá: 200 + summary 'None (AutoCAD None)')", r14.status_code == 500, r14.status_code)
        ok("có cờ reset_xac_nhan", j14.get("reset_xac_nhan") is True, j14)
        ok("KHÔNG rỉ đường dẫn máy chủ ra trình duyệt", "_uploads" not in str(j14) and "D:/" not in str(j14), j14)
        s14 = list(A.SESSIONS.values())[0]
        ok("phiên KHÔNG bị dán co_ban_ve=True cho bản vẽ không tồn tại", s14.get("co_ban_ve") is False, s14.get("co_ban_ve"))
        ok("summary KHÔNG chứa 'None (AutoCAD None)' để bơm vào prompt Gemini", "None (AutoCAD" not in (s14.get("summary") or ""), s14.get("summary"))
        ok("số bản vẽ = 0 (suất bóng không tồn tại)", _dem() == 0, _dem())
        ans14 = (c14.post("/ask", json={"q": "hi"}).get_json() or {}).get("answer", "")
        ok("hỏi tiếp -> nói THẬT là chưa có bản vẽ", "tải" in ans14.lower() or "chưa nạp" in ans14.lower(), ans14)

        print("[A.15] CAO(red-team): 'đang bận' KHÔNG được suy ra 'không có mục nào' rồi ẩn bảng âm thầm")
        _reset(); A.MAX_BAN_VE = 1; A.LOCK_WAIT_S = 1
        c15 = A.app.test_client()
        _upload(c15, "a15.dxf"); upl.add("a15.dxf")
        s15 = list(A.SESSIONS.values())[0]
        s15["lock"].acquire()
        try:
            d15 = c15.get("/xac-nhan/danh-sach").get_json() or {}
            ok("bận -> trả dang_ban=True (không phải im lặng so_muc=0)", d15.get("dang_ban") is True, d15)
        finally:
            s15["lock"].release()
        _src = open(os.path.join(os.path.dirname(A.__file__), "app.py"), encoding="utf-8").read()
        ok("frontend BỎ QUA nhịp khi dang_ban (không ẩn bảng)", "if(r.dang_ban){return}" in _src)
        ok("nút 'Tải lên & nạp' bị KHOÁ trong lúc đang tải (chống bấm 2 lần)",
           'id="btnUp"' in _src and "bu.disabled=true" in _src)

        print("[A.16] CAO(red-team): TOCTOU — bản vẽ bị lấy đi SAU cửa kiểm phải NÓI THẬT, không lỗi Python")
        _reset(); A.MAX_BAN_VE = 1; A.LOCK_WAIT_S = 2
        c16 = A.app.test_client()
        _upload(c16, "a16.dxf"); upl.add("a16.dxf")
        s16 = list(A.SESSIONS.values())[0]
        s16["lock"].acquire()

        def _tuoc():                                  # mô phỏng đường NHƯỜNG CHỖ chen vào giữa 2 bước
            time.sleep(0.5)
            with A._SESS_LOCK:
                s16["bridge"], s16["co_ban_ve"], s16["da_nhuong"] = None, False, True
            s16["lock"].release()

        threading.Thread(target=_tuoc).start()
        r16 = c16.post("/ask", json={"q": "hoi"})
        j16 = r16.get_json() or {}
        ok("/ask -> 200 + câu NÓI THẬT 'đã được nhường' (không NoneType error)",
           r16.status_code == 200 and "nhường" in (j16.get("answer") or ""), (r16.status_code, j16))
        d16 = c16.get("/xac-nhan/danh-sach").get_json() or {}
        ok("bảng xác nhận -> da_reset=True (không ẩn âm thầm)", d16.get("da_reset") is True, d16)
        x16 = c16.post("/xac-nhan", json={"kb_id": "x", "option_key": "y", "ma": "z"})
        ok("nút xác nhận -> 400 + ly_do trung thực", x16.status_code == 400 and (x16.get_json() or {}).get("ly_do"), x16.get_json())

        print("[A.17] TB(red-team): env RÁC trên dashboard KHÔNG được làm sập boot; cờ lý do phải được GỠ")
        _src2 = open(os.path.join(os.path.dirname(A.__file__), "app.py"), encoding="utf-8").read()
        ok("KHÔNG còn int() trần cho các nút đã phơi trong render.yaml (gõ sai = deploy fail 100%)",
           'int(os.environ.get("MAX_SESSIONS"' not in _src2 and 'int(os.environ.get("LOCK_WAIT_S"' not in _src2
           and 'int(os.environ.get("KEEPALIVE_MIN"' not in _src2 and 'int(os.environ.get("SESSION_TTL_MIN"' not in _src2)
        ok("LOCK_WAIT_S bị KẸP >= 0 (số âm = acquire chờ VÔ HẠN = tắt âm thầm chính bản vá)", A.LOCK_WAIT_S >= 0, A.LOCK_WAIT_S)
        ok("vòng giữ-thức có lưới an toàn quanh THÂN (1 ngoại lệ không được tắt lặng lẽ tính năng)",
           "LOI VONG LAP" in _src2)
        _reset(); A.MAX_BAN_VE = 1; A.LOCK_WAIT_S = 1
        ca, cb = A.app.test_client(), A.app.test_client()
        _upload(ca, "a17.dxf"); upl.add("a17.dxf")
        _upload(cb, "b17.dxf"); upl.add("b17.dxf")      # A bị nhường
        s17 = [v for v in A.SESSIONS.values() if v.get("da_nhuong")]
        ok("A có cờ da_nhuong sau khi bị nhường", len(s17) == 1, len(s17))
        _upload(ca, "a17b.dxf"); upl.add("a17b.dxf")    # A nạp lại thành công
        ok("nạp lại THÀNH CÔNG -> cờ da_nhuong được GỠ (lần mất bản vẽ sau không báo sai lý do)",
           s17[0].get("da_nhuong") is False, s17[0].get("da_nhuong"))

        print("[A.12] /health phơi số để xác minh SAU khi deploy (đường miễn phí duy nhất)")
        j = A.app.test_client().get("/health").get_json() or {}
        ok("/health có ban_ve/dang_nap/dang_dong/max_ban_ve là int",
           all(isinstance(j.get(k), int) for k in ("ban_ve", "dang_nap", "dang_dong", "max_ban_ve")), j)
        ok("ram_mb là số hoặc None (None trên Windows, có số trên Render/Linux)",
           j.get("ram_mb") is None or isinstance(j.get("ram_mb"), (int, float)), j.get("ram_mb"))
        _reset()
        ok("sau _reset: số bản vẽ về 0", _dem() == 0, _dem())
    finally:
        _reset()
        A._make_bridge, A.mcp_bridge.tra_loi_ai, A.mcp_bridge.USE_AI = _mk, _tl, _ua
        A.MAX_SESSIONS, A.MAX_BAN_VE, A.LOCK_WAIT_S, A.READFILE_MAX_MB = _ms, _mbv, _lw, _rf
        for nm in upl:
            for _f in os.listdir(A.UPLOAD_DIR):
                if _f == nm or _f.endswith("_" + nm):
                    try:
                        os.remove(os.path.join(A.UPLOAD_DIR, _f))
                    except OSError:
                        pass

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


def _ask_json(client):
    return client.post("/ask", json={"q": "hoi tiep"}).get_json()


if __name__ == "__main__":
    sys.exit(main())
