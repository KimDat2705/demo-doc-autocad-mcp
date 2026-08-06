# -*- coding: utf-8 -*-
"""do_residual_corpus.py — ĐO VÙNG CHƯA ĐỌC (residual) trên TOÀN corpus .dxf đã convert.

MỤC ĐÍCH: biến câu hỏi mơ hồ "đã đủ công cụ chưa?" thành **HÀNG ĐỢI CÔNG VIỆC ĐẾM ĐƯỢC**.
`residual` = đoạn chữ mà KHÔNG bộ nhận-diện nào hấp thụ (handle không nằm trong `used_handles`)
— nghĩa đen: "có chữ mà không hiểu".

KỶ LUẬT ĐO (bám `[[feedback-kiem-bo-trich-truoc-khi-tin-so]]`):
  * CHỈ MÔ TẢ, KHÔNG SUY DIỄN. Không dựng "bộ phân loại thông minh" rồi báo cáo đầu ra của nó
    như sự thật. Phân nhóm bằng DẤU HIỆU BỀ MẶT kiểm chứng được (có chữ số? có đơn vị? có dấu gán?).
  * IN MẪU từng nhóm để NGƯỜI đọc tay kiểm — bắt buộc trước khi tin bất kỳ con số tổng hợp nào.
  * THẤT BẠI PHẢI LỘ: file lỗi được đếm + liệt kê, không im lặng bỏ qua.
  * BÁO CÁO THEO NHÓM (thư mục gốc) để lỗi lệch-về-một-đơn-vị-thiết-kế lộ ra, không bị trung bình hoá.

⚠ PHẠM VI CỦA THƯỚC ĐO — ĐỌC TRƯỚC KHI DIỄN GIẢI SỐ:
  Thước này CHỈ đếm TEXT/MTEXT ở modelspace (`Drawing.texts`). NẰM NGOÀI:
    · bảng OLE nhúng  -> đọc bằng tool #27 `doc_bang_nhung` (ca thật: '4. Thong ke thep SUA.dxf'
      trông như rỗng — 17 đoạn chữ — nhưng có 8 bảng OLE, bảng đầu 254 hàng × 32 cột)
    · thuộc tính block (bảng thống kê thép) -> `thong_ke_thep`, đã nằm trong `used_handles`
    · chữ bên trong ĐỊNH NGHĨA block -> KHÔNG có trong `self.texts` (xem `test_vung_chua_doc.py`)
  ⇒ residual vừa NÓI QUÁ (gộp cả chữ ghi chú) vừa NÓI THIẾU (bỏ qua phần đọc bằng đường khác).
  ⇒ residual KHÔNG có nghĩa "AI không thấy" — `tim_kiem` vẫn tìm ra mọi chuỗi đó. Cái thiếu là
    bước từ "có chữ Ø16 ở N chỗ" sang "dầm D1 có 2Ø12 lớp trên, tổng X kg".

CHẠY (từ thư mục `demo_mcp_autocad/`):
    READFILE_MAX_MB=400 python tests/do_residual_corpus.py
  ⚠ PHẢI đặt READFILE_MAX_MB cao: cổng 45MB là giới hạn RAM CLOUD, không phải giới hạn logic.
    Để mặc định thì 14/86 file bị chặn — và đó CHÍNH LÀ các bản kết cấu LỚN NHẤT
    (nhà 9T 114MB, thống kê thép 68MB) ⇒ kết quả lệch nặng về file nhỏ. Đọc local là MIỄN PHÍ.
"""
import os
import sys
import io
import re
import json
import time
import glob
import random
from collections import Counter, defaultdict

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, PKG)
os.chdir(PKG)
from tools_core import Drawing   # noqa: E402

# ---- dấu hiệu BỀ MẶT (không suy diễn nghĩa) --------------------------------
SO_TRAN = re.compile(r"^\s*[-+]?\d+(?:[.,]\d+)?\s*$")
CO_SO = re.compile(r"\d")
DON_VI = re.compile(
    r"(?:\d\s*(?:m2|m²|m3|m³|kg|tấn|mm|cm|\bm\b|%|độ)\b)"
    r"|(?:\b[a-zA-Zàáâãèéêìíòóôõùúăđĩũơưăạảấầẩẫậ]{1,4}\s*=\s*\d)"
    r"|[ØøΦφ]\s*\d"
    r"|\d\s*[x×]\s*\d"
    r"|@\s*\d",
    re.I)
MAU_LOAI = [
    ("dien tich  (X m2)",      re.compile(r"\d\s*(?:m2|m²)\b", re.I)),
    ("the tich   (X m3)",      re.compile(r"\d\s*(?:m3|m³)\b", re.I)),
    ("khoi luong (X kg/tan)",  re.compile(r"\d\s*(?:kg|tấn)\b", re.I)),
    ("duong kinh (OX)",        re.compile(r"[ØøΦφ]\s*\d")),
    ("gan nhan   (s=/L=/h=)",  re.compile(r"\b[a-zA-Zàáâãèéêìíòóôõùúăđ]{1,4}\s*=\s*\d", re.I)),
    ("tiet dien  (AxB)",       re.compile(r"\d\s*[x×]\s*\d")),
    ("buoc/khoang(@X)",        re.compile(r"@\s*\d")),
    ("do dai     (X m/mm/cm)", re.compile(r"\d\s*(?:mm|cm|\bm\b)\b", re.I)),
    ("phan tram  (X%)",        re.compile(r"\d\s*%")),
]
# ⚠ BẮT NHẦM ĐÃ BIẾT (đọc tay 2026-08-06) — đừng tin nhóm "có đơn vị" là sạch 100%:
#     'V=1:100' / 'H=1:500'          -> TỶ LỆ bản vẽ, không phải số liệu
#     'cút thép hàn DN100x45°'       -> '100x45' là DN100 × GÓC 45°, KHÔNG phải tiết diện
#     'cho 1m3 nước, nước dùng...'   -> ghi chú bảo dưỡng bê tông, '1m3' là văn nói
#   ⇒ nhóm này là TÍN HIỆU MẠNH nhưng KHÔNG TINH KHIẾT -> phải qua NGƯỜI duyệt,
#     TUYỆT ĐỐI không tự động đổ vào dự toán.


def txt(t):
    return (t.get("vn") or t.get("text") or "").strip()


def nhom_cua(p):
    q = os.path.normpath(p).split(os.sep)
    try:
        return q[q.index("_dxf") + 1]
    except Exception:
        return "(goc)"


def main():
    files = sorted(glob.glob(os.path.join(PKG, "_khao_sat", "_dxf", "**", "*.dxf"), recursive=True))
    print("TONG FILE .dxf tim thay:", len(files), flush=True)
    if not files:
        print("KHONG co .dxf — chay `python tests/khao_sat_corpus.py` truoc de convert.", flush=True)
        return

    kq = {"meta": {"so_file": len(files)}, "files": [], "loi": []}
    loai_dem, loai_mau = Counter(), defaultdict(list)
    mau_so_tran, mau_chu_thuan = [], []
    g = defaultdict(Counter)
    t0 = time.time()

    for i, p in enumerate(files, 1):
        ten = os.path.basename(p)
        try:
            d = Drawing(p)
        except Exception as e:
            kq["loi"].append({"file": ten, "loi": "%s: %s" % (type(e).__name__, str(e)[:140])})
            print("  [%3d/%d] LOI  %s  (%s)" % (i, len(files), ten[:48], type(e).__name__), flush=True)
            continue

        nh = nhom_cua(p)
        c = Counter(text=len(d.texts))
        res = [t for t in d.texts if t.get("handle") not in d.used_handles]
        c["residual"] = len(res)
        for t in res:
            s = txt(t)
            if not s:
                continue
            if not CO_SO.search(s):
                c["chu_thuan"] += 1
                if len(mau_chu_thuan) < 40 and random.random() < 0.02:
                    mau_chu_thuan.append(s[:70])
            elif DON_VI.search(s):
                c["co_don_vi"] += 1
                for ten_loai, rx in MAU_LOAI:
                    if rx.search(s):
                        loai_dem[ten_loai] += 1
                        if len(loai_mau[ten_loai]) < 12:
                            loai_mau[ten_loai].append((s[:60], ten[:28]))
                        break
                else:
                    loai_dem["(co don vi, khong khop mau)"] += 1
            elif SO_TRAN.match(s):
                c["so_tran"] += 1
                if len(mau_so_tran) < 40 and random.random() < 0.03:
                    mau_so_tran.append((s, (t.get("layer") or "")[:22], ten[:26]))
            else:
                c["hon_hop"] += 1        # chữ + số, không đơn vị (mã hiệu / tiêu đề / tham chiếu)
        g[nh].update(c)
        kq["files"].append({"file": ten, "nhom": nh, **dict(c)})
        del d
        if i % 10 == 0:
            print("  ...%d/%d (%.0fs)" % (i, len(files), time.time() - t0), flush=True)

    kq["theo_nhom"] = {k: dict(v) for k, v in g.items()}
    kq["loai_bo_sot"] = dict(loai_dem)
    kq["loai_mau"] = dict(loai_mau)
    kq["mau_so_tran"] = mau_so_tran
    kq["mau_chu_thuan"] = mau_chu_thuan
    kq["meta"]["giay"] = round(time.time() - t0, 1)

    out = os.path.join(PKG, "_khao_sat", "residual_toan_corpus.json")
    with io.open(out, "w", encoding="utf-8") as f:
        json.dump(kq, f, ensure_ascii=False, indent=1)

    T = sum(f.get("text", 0) for f in kq["files"])
    R = sum(f.get("residual", 0) for f in kq["files"])
    print("\nDA GHI:", out, "| %.0fs" % kq["meta"]["giay"], flush=True)
    print("File doc duoc: %d | File LOI: %d" % (len(kq["files"]), len(kq["loi"])), flush=True)
    print("Tong doan chu: %d | residual: %d (%.1f%%)" % (T, R, 100.0 * R / max(1, T)), flush=True)
    print("\n--- XEP HANG LOAI DU LIEU BI BO SOT ---", flush=True)
    tot = sum(loai_dem.values())
    for k, v in sorted(loai_dem.items(), key=lambda x: -x[1]):
        print("  %7d  (%5.1f%%)  %s" % (v, 100.0 * v / max(1, tot), k), flush=True)
    print("\n⚠ ĐỌC TAY mau trong JSON (`loai_mau`) TRUOC KHI TIN SO TREN.", flush=True)


if __name__ == "__main__":
    random.seed(11)
    main()
