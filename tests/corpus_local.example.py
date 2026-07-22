# -*- coding: utf-8 -*-
"""MAU cau hinh duong dan corpus.  COPY thanh `corpus_local.py` (GITIGNORED) roi dien
ten THU MUC / FILE ban ve THAT tren may nay.

VI SAO: giu TEN KHACH HANG (ten thu muc/file ban ve) NGOAI repo git de bao ve danh tinh.
`corpus_local.py` bi .gitignore chan -> khong bao gio len GitHub. File .example nay
(khong chua ten that) MOI la file duoc commit.

Quy trinh day du: harness/QUY_TRINH_AN_DANH_DU_LIEU_MAU.md
Neu KHONG tao corpus_local.py -> cac test dung fixture that se tu SKIP (guard os.path.isfile).
"""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_DXF = os.path.normpath(os.path.join(_HERE, "..", "..", "input_files", "_dxf"))
_UP = os.path.normpath(os.path.join(_HERE, "..", "..", "demo_doc_autocad", "_uploads"))

# --- Cong trinh A (vd: mam non) — dien ten thu muc + 2 file that ---
_CT_A = os.path.join(_DXF, "<thu-muc-cong-trinh-A>")
KT = os.path.join(_CT_A, "<CT-A - kien truc>.dxf")
KC = os.path.join(_CT_A, "<CT-A - ket cau>.dxf")

# --- Cong trinh B (vd: nha nhieu tang) ---
_CT_B = os.path.join(_DXF, "<thu-muc-cong-trinh-B>")
P9 = os.path.join(_CT_B, "<CT-B - ket cau>.dxf")
P9KT = os.path.join(_CT_B, "<CT-B - kien truc>.dxf")

# --- Cong trinh ha tang (nam trong demo_doc_autocad/_uploads) ---
HT = os.path.join(_UP, "<CT-K - ha tang>.dxf")
