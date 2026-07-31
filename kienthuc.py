# -*- coding: utf-8 -*-
"""kienthuc.py — KHO KIẾN THỨC DEV-SOẠN (L1, pivot AI-tự-học 2026-07-26). Xem KE_HOACH_KHO_KIEN_THUC.md.

NGUYÊN TẮC (bất biến — validator + test khoá):
  1. Kho chỉ giúp DIỄN GIẢI ký hiệu + HỎI ĐÚNG CHỖ. TUYỆT ĐỐI không sinh số, không đổi số nào của engine.
  2. MỌI chuỗi phát-ra-ngoài (mo_ta / nguon / cau_hoi / label / symbol_display / coverage chữ) CẤM chữ số
     — chống lọt rổ grounding (_collect_numbers) làm mỏ neo cho câu bịa (tiền lệ -22.75 / I3 NO_GO).
  3. Mọi identifier (id / meaning key / option key) TOÀN chữ thường + underscore.
  4. on_collision = "ASK" toàn bộ khi ship — KHÔNG auto-resolve nghĩa (mở RESOLVE_IF_SIGNAL chỉ sau ≥3 firm
     + holdout, và chỉ cho tín hiệu HÌNH THỨC scale-free).
  5. Đối tác CHỈ BẤM XÁC NHẬN trong options dev-soạn (luôn có 'khac_khong_chac'); không đường nhập tự do.
  6. Fail-open: ký hiệu ngoài kho → hệ nói "bí" và hỏi, KHÔNG đoán. Thiếu file này → hệ chạy y hệt cũ
     (mọi nơi import qua try/except — degrade-safe).
  7. Module DATA THUẦN: không I/O, không import gì từ dự án (tools_core norm ở call-site rồi tra khoá).

KHOÁ 2 TẦNG (chống sập Đ→D — bài học id84):
  - khoa_phan_biet: sinh từ _norm_ma phía call-site (GIỮ đ/d: 'ĐC'→'djc' ≠ 'DC'→'dc') — dùng cho text ĐỌC TỪ FILE.
  - khoa_sap: dạng unaccent-sập ('dc') — dùng cho QUERY NGƯỜI GÕ; trùng khoa_sap giữa các entry BẮT BUỘC
    có cạnh confusable_with (validator kiểm).

COVERAGE: n_file/n_firm là INT NỘI BỘ (không bao giờ emit); payload() đổi sang CHỮ ('một/hai/nhiều đơn vị').
Đổi kho: sửa entry → chạy harness/scripts/kb_refreeze.sh → dán KB_HASH mới vào test (byte-lock kiểu I9).
"""
import hashlib as _hashlib
import json as _json

KB_VERSION = "kb-2026.07.26-dot-dau"

# tier nguồn (trung thực về độ tin): chuan_quoc_gia > pho_bien_nganh > quan_sat_corpus / bai_hoc_noi_bo
_TIERS = ("chuan_quoc_gia", "pho_bien_nganh", "quan_sat_corpus", "bai_hoc_noi_bo")
_LOAI = ("ky_hieu", "mau_hinh", "bai_hoc")   # ky_hieu: token tra được; mau_hinh: pattern hình thức; bai_hoc: ghi chú ngữ nghĩa

_OPT_KHAC = {"key": "khac_khong_chac", "label": "Khác / không chắc (giữ nguyên trạng thái chưa đọc)"}


def _e(id, loai, symbol_display, khoa_phan_biet, khoa_sap, nghia, match=None,
       confusable=False, confusable_with=(), confirm_template=None, ghi_chu=""):
    return {"id": id, "loai": loai, "symbol_display": symbol_display,
            "khoa_phan_biet": khoa_phan_biet, "khoa_sap": khoa_sap, "match": match,
            "nghia": nghia, "confusable": confusable, "confusable_with": list(confusable_with),
            "on_collision": "ASK", "confirm_template": confirm_template, "ghi_chu": ghi_chu,
            "hieu_luc": "dang_dung"}


def _n(key, mo_ta, domain, tier, nguon, n_file=0, n_firm=0):
    return {"key": key, "mo_ta": mo_ta, "domain": domain, "tier": tier, "nguon": nguon,
            "coverage": {"n_file": n_file, "n_firm": n_firm}}


def _q(cau_hoi, *options):
    return {"cau_hoi": cau_hoi, "options": [dict(o) for o in options] + [dict(_OPT_KHAC)]}


KB_ENTRIES = (
    # ---------- cặp va chạm ĐÃ TRẢ GIÁ (id84) + tái hiện trong 1 file corpus ----------
    _e("dc_dai_coc", "ky_hieu", "ĐC-x", "djc", "dc",
       nghia=[_n("dai_coc", "đài cọc (kết cấu móng)", "ket_cau", "quan_sat_corpus",
                 "bài học nội bộ vụ đếm nhầm đài cọc hút cả dầm; corpus kết cấu", 3, 2)],
       match={"chu": "đc", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["ĐC-1", "ĐC1", "ĐC-3 (SL-25)"], "vi_du_khong_khop": ["DC-1", "ĐCN"]},
       confusable=True, confusable_with=("dc_dam_chi_tiet",),
       confirm_template=_q("Trong bản vẽ này, ký hiệu {ky_hieu} là gì?",
                           {"key": "dai_coc", "label": "Đài cọc (móng)"},
                           {"key": "dam", "label": "Dầm"},
                           {"key": "ma_chi_tiet_khac", "label": "Mã chi tiết khác (không phải đài cọc hay dầm)"})),
    _e("dc_dam_chi_tiet", "ky_hieu", "DC-x", "dc", "dc",
       nghia=[_n("dam", "dầm (kết cấu thân)", "ket_cau", "quan_sat_corpus", "corpus kết cấu nhiều file", 4, 2),
              _n("ma_chi_tiet_khac", "mã chi tiết khác trong bản móng (cạnh vùng thép đài)", "ket_cau",
                 "quan_sat_corpus", "corpus: cùng một bản móng chứa cả hai dạng có dấu và không dấu", 1, 1)],
       match={"chu": "dc", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["DC-1", "DC2"], "vi_du_khong_khop": ["ĐC-1", "DCN-2"]},
       confusable=True, confusable_with=("dc_dai_coc",),
       confirm_template=_q("Trong bản vẽ này, ký hiệu {ky_hieu} là gì?",
                           {"key": "dam", "label": "Dầm"},
                           {"key": "dai_coc", "label": "Đài cọc (móng)"},
                           {"key": "ma_chi_tiet_khac", "label": "Mã chi tiết khác"}),
       ghi_chu="unaccent sập ĐC↔DC — hai entry tách bằng khoa_phan_biet; đã tái hiện CẢ HAI trong cùng một file corpus."),

    # ---------- CH: ca CH-2.700 (chiều cao bị đọc thành cao độ âm) ----------
    _e("ch_da_nghia", "ky_hieu", "CH", "ch", "ch",
       nghia=[_n("cua_di", "cửa đi (kiến trúc, thường trong bảng thống kê cửa)", "kien_truc",
                 "pho_bien_nganh", "quy ước mã cửa phổ biến ngành", 2, 2),
              _n("chieu_cao", "chiều cao (ghi chú kích thước, hay viết tắt trước trị số)", "chung",
                 "bai_hoc_noi_bo", "bài học nội bộ: ghi chú chiều cao bị đọc nhầm thành cao độ âm", 1, 1),
              _n("cao_do_chuan", "cao độ (một số bản dùng chữ này cạnh mốc)", "chung",
                 "quan_sat_corpus", "quan sát corpus", 1, 1)],
       match={"chu": "ch", "duoi_so": False, "match_kieu": "keyword",
              "vi_du_khop": ["CH", "CH - 2.700"], "vi_du_khong_khop": ["CHỜ", "CHÂN"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} trong ngữ cảnh này nghĩa là gì?",
                           {"key": "cua_di", "label": "Cửa đi"},
                           {"key": "chieu_cao", "label": "Chiều cao (kích thước)"},
                           {"key": "cao_do_chuan", "label": "Cao độ (mốc)"})),

    # ---------- họ mã một-chữ dễ va TÊN TRỤC / loại cấu kiện ----------
    _e("d_da_nghia", "ky_hieu", "D-x", "d", "d",
       nghia=[_n("dam", "dầm (kết cấu)", "ket_cau", "quan_sat_corpus", "corpus kết cấu", 4, 2),
              _n("cua_di", "cửa đi (kiến trúc)", "kien_truc", "quan_sat_corpus", "corpus kiến trúc", 2, 2),
              _n("duong_kinh_ong", "đường kính ống (cấp thoát nước, hạ tầng)", "cap_thoat_nuoc",
                 "pho_bien_nganh", "quy ước ống phổ biến ngành nước", 2, 1),
              _n("ten_truc", "tên trục định vị", "chung", "pho_bien_nganh", "quy ước lưới trục bản vẽ", 2, 2)],
       match={"chu": "d", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["D1", "D-2", "D200"], "vi_du_khong_khop": ["DK", "DC-1", "DR-6"]},
       confusable=True, confusable_with=("dj_da_nghia",),
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "dam", "label": "Dầm"},
                           {"key": "cua_di", "label": "Cửa đi"},
                           {"key": "duong_kinh_ong", "label": "Đường kính ống"},
                           {"key": "ten_truc", "label": "Tên trục định vị"}),
       ghi_chu="bài học nội bộ: cùng mã hai loại (dầm và cửa) trong một công trình — dedup phải TÁCH không GỘP."),
    _e("dj_da_nghia", "ky_hieu", "Đ-x", "dj", "d",
       nghia=[_n("cua_di", "cửa đi (kiến trúc, một số bản dùng chữ có dấu)", "kien_truc",
                 "quan_sat_corpus", "corpus kiến trúc và phá dỡ", 2, 2),
              _n("doan_coc", "đoạn cọc (kết cấu móng)", "ket_cau", "quan_sat_corpus", "corpus móng cọc", 1, 1),
              _n("tam_dan", "tấm đan (bể, mương)", "ket_cau", "quan_sat_corpus", "corpus bể nước", 1, 1),
              _n("ma_ban_ve_dien", "mã bản vẽ điện", "dien", "quan_sat_corpus", "corpus bản vẽ điện", 1, 1)],
       match={"chu": "đ", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["Đ1", "Đ-01"], "vi_du_khong_khop": ["ĐC-1", "ĐK"]},
       confusable=True, confusable_with=("d_da_nghia",),
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "cua_di", "label": "Cửa đi"},
                           {"key": "doan_coc", "label": "Đoạn cọc (móng)"},
                           {"key": "tam_dan", "label": "Tấm đan (bể / mương)"},
                           {"key": "ma_ban_ve_dien", "label": "Mã bản vẽ điện"})),
    _e("c_da_nghia", "ky_hieu", "C-x", "c", "c",
       nghia=[_n("cot", "cột (kết cấu)", "ket_cau", "quan_sat_corpus", "corpus kết cấu nhiều file", 5, 3),
              _n("ten_truc", "tên trục định vị", "chung", "pho_bien_nganh", "quy ước lưới trục bản vẽ", 3, 2),
              _n("coc_tuyen", "cọc tuyến / cột mốc tuyến (hạ tầng)", "ha_tang", "quan_sat_corpus",
                 "corpus tuyến ống áp lực", 1, 1),
              _n("ong_cong", "ống / cống (thoát nước)", "cap_thoat_nuoc", "quan_sat_corpus", "corpus thoát nước", 1, 1)],
       match={"chu": "c", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["C1", "C-2", "C999"], "vi_du_khong_khop": ["CH", "CT.01", "CB300"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "cot", "label": "Cột"},
                           {"key": "ten_truc", "label": "Tên trục định vị"},
                           {"key": "coc_tuyen", "label": "Cọc tuyến (hạ tầng)"},
                           {"key": "ong_cong", "label": "Ống / cống"})),
    _e("t_da_nghia", "ky_hieu", "T-x", "t", "t",
       nghia=[_n("tang", "tầng (kiến trúc: tầng một, tầng hai...)", "kien_truc", "pho_bien_nganh",
                 "quy ước tên tầng phổ biến", 3, 2),
              _n("tuong", "tường (kết cấu / kiến trúc)", "chung", "quan_sat_corpus", "corpus", 1, 1),
              _n("thep_tam", "thép tấm / bản mã (kết cấu thép)", "ket_cau", "quan_sat_corpus",
                 "corpus bảng thép hình", 1, 1)],
       match={"chu": "t", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["T1", "T-2"], "vi_du_khong_khop": ["TL", "TB6", "TCVN"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "tang", "label": "Tầng"},
                           {"key": "tuong", "label": "Tường"},
                           {"key": "thep_tam", "label": "Thép tấm / bản mã"})),
    _e("s_da_nghia", "ky_hieu", "S-x", "s", "s",
       nghia=[_n("san", "sàn (kết cấu)", "ket_cau", "quan_sat_corpus", "corpus kết cấu", 2, 2),
              _n("cua_so", "cửa sổ (kiến trúc)", "kien_truc", "pho_bien_nganh", "quy ước mã cửa sổ phổ biến", 2, 2)],
       match={"chu": "s", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["S1", "S-2"], "vi_du_khong_khop": ["SK2", "SL-25"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "san", "label": "Sàn"},
                           {"key": "cua_so", "label": "Cửa sổ"})),
    _e("v_da_nghia", "ky_hieu", "V-x", "v", "v",
       nghia=[_n("vach", "vách (kết cấu / kiến trúc)", "chung", "quan_sat_corpus", "corpus", 1, 1),
              _n("thep_cho", "thép chờ (kết cấu)", "ket_cau", "bai_hoc_noi_bo",
                 "bài học nội bộ: nhãn thép chờ từng là nhãn lạ thật của bộ phân loại", 1, 1),
              _n("vi_keo", "vì kèo (mái)", "ket_cau", "pho_bien_nganh", "quy ước phổ biến", 1, 1)],
       match={"chu": "v", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["V1", "V-1"], "vi_du_khong_khop": ["VK1", "VXM"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "vach", "label": "Vách"},
                           {"key": "thep_cho", "label": "Thép chờ"},
                           {"key": "vi_keo", "label": "Vì kèo (mái)"})),
    _e("k_da_nghia", "ky_hieu", "K-x", "k", "k",
       nghia=[_n("khung", "khung (kết cấu)", "ket_cau", "quan_sat_corpus", "corpus", 1, 1),
              _n("ten_truc", "tên trục định vị", "chung", "pho_bien_nganh", "quy ước lưới trục bản vẽ", 2, 2)],
       match={"chu": "k", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["K1", "K-2"], "vi_du_khong_khop": ["KT", "KC", "Km"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "khung", "label": "Khung (kết cấu)"},
                           {"key": "ten_truc", "label": "Tên trục định vị"})),

    # ---------- vật liệu / tham số dễ nhầm mã ----------
    _e("b_da_nghia", "ky_hieu", "B / b-x", "b", "b",
       nghia=[_n("cap_ben_be_tong", "cấp độ bền bê tông (chữ B liền trị số)", "ket_cau", "chuan_quoc_gia",
                 "TCVN kết cấu bê tông và bê tông cốt thép (cấp độ bền B)", 3, 2),
              _n("ten_truc", "tên trục định vị", "chung", "pho_bien_nganh", "quy ước lưới trục", 2, 2),
              _n("ban", "bản / bề rộng (ghi chú kích thước)", "chung", "quan_sat_corpus", "corpus", 1, 1)],
       match={"chu": "b", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["B20", "B25", "B1"], "vi_du_khong_khop": ["BT", "BTCT"]},
       confusable=True, ghi_chu="mác vật liệu là KÝ HIỆU CHUẨN — bộ phân loại đã coi là notation chuẩn, KHÔNG hỏi khi ở ngữ cảnh ghi chú vật liệu.",
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "cap_ben_be_tong", "label": "Cấp độ bền bê tông (mác vật liệu)"},
                           {"key": "ten_truc", "label": "Tên trục định vị"},
                           {"key": "ban", "label": "Bản / bề rộng"})),
    _e("m_da_nghia", "ky_hieu", "M / M-x", "m", "m",
       nghia=[_n("mac_vua", "mác vữa / xi măng (chữ M liền trị số trong ghi chú vật liệu)", "ket_cau",
                 "chuan_quoc_gia", "TCVN vữa xây dựng (mác M)", 2, 2),
              _n("mong", "móng (mã cấu kiện)", "ket_cau", "quan_sat_corpus", "corpus kết cấu", 2, 2),
              _n("met", "mét (đơn vị chiều dài viết tắt trong ngoặc)", "chung", "quan_sat_corpus", "corpus", 1, 1),
              _n("ma_pha_do", "mã hạng mục phá dỡ", "kien_truc", "quan_sat_corpus", "corpus phá dỡ", 1, 1)],
       match={"chu": "m", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["M75", "M150", "M1"], "vi_du_khong_khop": ["MB", "MC", "MN"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "mac_vua", "label": "Mác vữa / xi măng (vật liệu)"},
                           {"key": "mong", "label": "Móng (mã cấu kiện)"},
                           {"key": "met", "label": "Mét (đơn vị)"},
                           {"key": "ma_pha_do", "label": "Mã hạng mục phá dỡ"})),
    _e("dk_duong_kinh", "ky_hieu", "DK", "dk", "dk",
       nghia=[_n("duong_kinh_header", "đường kính (tiêu đề cột trong bảng thống kê thép)", "ket_cau",
                 "quan_sat_corpus", "corpus bảng thống kê thép — engine đã đọc theo vị trí cột", 3, 2)],
       match={"chu": "dk", "duoi_so": False, "match_kieu": "structural",
              "vi_du_khop": ["DK", "ĐK"], "vi_du_khong_khop": ["DK-1"]},
       confusable=False,
       ghi_chu="nghĩa phân biệt được bằng tín hiệu vị trí (header bảng) engine đã có → KHÔNG sinh câu hỏi."),
    _e("tl_da_nghia", "ky_hieu", "TL", "tl", "tl",
       nghia=[_n("ty_le", "tỷ lệ bản vẽ (khung tên, dạng một-chia-n)", "chung", "pho_bien_nganh",
                 "quy ước khung tên phổ biến", 3, 3),
              _n("trong_luong", "trọng lượng (tiêu đề cột bảng thống kê thép)", "ket_cau",
                 "quan_sat_corpus", "corpus bảng thép", 2, 2)],
       match={"chu": "tl", "duoi_so": False, "match_kieu": "structural",
              "vi_du_khop": ["TL", "TL 1:100"], "vi_du_khong_khop": ["TLE"]},
       confusable=True,
       ghi_chu="hai nghĩa phân biệt được bằng vị trí (khung tên vs header bảng) — chỉ hỏi khi ngoài cả hai ngữ cảnh.",
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "ty_le", "label": "Tỷ lệ bản vẽ"},
                           {"key": "trong_luong", "label": "Trọng lượng (bảng thép)"})),
    _e("l_da_nghia", "ky_hieu", "L", "l", "l",
       nghia=[_n("chieu_dai", "chiều dài (chữ L kèm dấu bằng và trị số)", "chung", "pho_bien_nganh",
                 "quy ước ghi kích thước phổ biến", 3, 3),
              _n("thep_goc", "thép góc chữ L (kết cấu thép, dạng L nhân ba kích thước)", "ket_cau",
                 "pho_bien_nganh", "quy ước thép hình phổ biến", 2, 2)],
       match={"chu": "l", "duoi_so": False, "match_kieu": "structural",
              "vi_du_khop": ["L=800", "L63x63x6"], "vi_du_khong_khop": ["LG", "LAN CAN"]},
       confusable=False,
       ghi_chu="hai nghĩa phân biệt được bằng HÌNH THỨC (dấu bằng vs nhân kích thước) — không sinh câu hỏi."),
    _e("i_da_nghia", "ky_hieu", "i / I-x", "i", "i",
       nghia=[_n("do_doc", "độ dốc (chữ i kèm dấu bằng và phần trăm)", "ha_tang", "pho_bien_nganh",
                 "quy ước độ dốc phổ biến (thoát nước, đường)", 2, 1),
              _n("thep_hinh_i", "thép hình chữ I (kết cấu thép)", "ket_cau", "pho_bien_nganh",
                 "quy ước thép hình phổ biến", 1, 1)],
       match={"chu": "i", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["i=2%", "I200"], "vi_du_khong_khop": ["IN", "INOX"]},
       confusable=False,
       ghi_chu="phân biệt bằng hình thức (dấu bằng-phần-trăm vs chữ hoa liền số). Biến thể garble chữ-i-hỏi thay ký hiệu phi KHÔNG đưa vào kho — vá ở tầng code có đo corpus (lát riêng)."),

    # ---------- domain nước / hạ tầng (bài học TB6 + id135-family) ----------
    _e("ct_da_nghia", "ky_hieu", "CT-x / CT.x", "ct", "ct",
       nghia=[_n("chi_tiet", "chi tiết (mã hình trích dẫn)", "chung", "pho_bien_nganh",
                 "quy ước đánh số chi tiết phổ biến", 3, 2),
              _n("ma_thep", "mã thanh thép (một số bảng kết cấu)", "ket_cau", "quan_sat_corpus",
                 "corpus bảng thép", 1, 1),
              _n("cong_trinh", "công trình (chữ viết tắt trong khung tên)", "chung", "quan_sat_corpus",
                 "corpus khung tên", 2, 2)],
       match={"chu": "ct", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["CT.01", "CT1"], "vi_du_khong_khop": ["CTN", "CỘT"]},
       confusable=True,
       confirm_template=_q("Ký hiệu {ky_hieu} ở đây là gì?",
                           {"key": "chi_tiet", "label": "Chi tiết (hình trích dẫn)"},
                           {"key": "ma_thep", "label": "Mã thanh thép"},
                           {"key": "cong_trinh", "label": "Công trình (khung tên)"})),
    _e("ctn_he_nuoc", "ky_hieu", "CTN / CN", "ctn", "ctn",
       nghia=[_n("cap_thoat_nuoc", "cấp thoát nước (tên hệ / tên bản vẽ)", "cap_thoat_nuoc",
                 "pho_bien_nganh", "quy ước tên hệ phổ biến", 2, 2)],
       match={"chu": "ctn", "duoi_so": False, "match_kieu": "keyword",
              "vi_du_khop": ["CTN", "CN1"], "vi_du_khong_khop": ["CT.01"]},
       confusable=False),
    _e("km_ly_trinh", "mau_hinh", "Km + …", "km", "km",
       nghia=[_n("ly_trinh", "lý trình tuyến (vị trí dọc tuyến hạ tầng, dạng Km cộng khoảng cách)", "ha_tang",
                 "pho_bien_nganh", "quy ước lý trình tuyến phổ biến (đường, ống)", 1, 1)],
       match={"chu": "km", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["K0+500", "Km1+250"], "vi_du_khong_khop": ["KM PHÒNG"]},
       confusable=False,
       ghi_chu="trị số lý trình KHÔNG phải cao độ / số đo cấu kiện — chống nhầm khi đọc bản vẽ tuyến."),
    _e("cut_goc_ong", "mau_hinh", "cút + trị số góc", "cut", "cut",
       nghia=[_n("goc_chuyen_huong", "góc chuyển hướng của cút ống (đơn vị độ) — KHÔNG phải cao độ", "cap_thoat_nuoc",
                 "bai_hoc_noi_bo", "bài học nội bộ bộ hạ tầng độc lập: trị số cạnh chữ cút là góc ống, từng có nguy cơ bị coi là mốc sâu", 1, 1)],
       match={"chu": "cút", "duoi_so": True, "match_kieu": "keyword",
              "vi_du_khop": ["cút -11,25 độ"], "vi_du_khong_khop": ["cắt"]},
       confusable=False),
    _e("word_gach_so_am", "mau_hinh", "CHỮ - trị số thập phân", "word_gach", "word_gach",
       nghia=[_n("map_mo_chieu_cao_cao_do", "dạng mập mờ: chữ, dấu trừ CÓ KHOẢNG TRẮNG, trị số thập phân — có thể là chiều cao (kích thước) hoặc cao độ âm; engine đẩy vào cảnh báo, KHÔNG tự nạp vào mốc thấp nhất", "chung",
                 "bai_hoc_noi_bo", "bài học nội bộ: cùng một hình thức chứa CẢ ghi chú chiều cao LẪN mốc cao độ thật ở hai bản vẽ khác nhau", 2, 2)],
       match={"chu": "", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["CH - 2.700", "cốt - 14.260"], "vi_du_khong_khop": ["-2.700", "+8.500"]},
       confusable=True,
       confirm_template=_q("Bản vẽ có ghi chú dạng {ky_hieu} (dấu trừ tách rời). Trị số này là gì?",
                           {"key": "cao_do_am", "label": "Cao độ âm (mốc sâu)"},
                           {"key": "chieu_cao_kich_thuoc", "label": "Chiều cao / kích thước (không phải cao độ)"}),
       ghi_chu="móc kích hoạt: canh_bao của tool đọc cao độ min-max (đường kích hoạt thật duy nhất)."),
    _e("mui_coc_day_dai", "bai_hoc", "cao độ sâu nhất trên bản móng cọc", "mui_coc", "mui_coc",
       nghia=[_n("mui_coc_khac_day_dai", "trên bản vẽ móng cọc, mốc sâu nhất thường là MŨI CỌC — khác ĐÁY ĐÀI; hai đại lượng đều thật, không được lấy mốc này trả lời cho mốc kia", "ket_cau",
                 "bai_hoc_noi_bo", "bài học nội bộ vụ mốc sâu bản móng cọc: suýt vá hỏng vì suy đoán cảm tính miền", 1, 1)],
       match=None, confusable=False,
       ghi_chu="đã phản ánh trong ghi chú tool cao độ; entry này để tra cứu + soạn câu hỏi khi đối tác thắc mắc."),

    # ---------- word-like (mô tả tra cứu, CẤM suppression — chống nuốt token dị nghĩa firm mới) ----------
    _e("wc_khu_ve_sinh", "ky_hieu", "WC", "wc", "wc",
       nghia=[_n("khu_ve_sinh", "khu vệ sinh (kiến trúc)", "kien_truc", "pho_bien_nganh",
                 "quy ước mặt bằng phổ biến", 3, 3)],
       match={"chu": "wc", "duoi_so": False, "match_kieu": "keyword",
              "vi_du_khop": ["WC"], "vi_du_khong_khop": ["WC-1?"]},
       confusable=False, ghi_chu="word-like: CHỈ mô tả tra cứu, không dùng để nén cảnh báo của bộ phân loại."),
    _e("gm_giang_mong", "ky_hieu", "GM-x", "gm", "gm",
       nghia=[_n("giang_mong", "giằng móng (kết cấu)", "ket_cau", "quan_sat_corpus", "corpus kết cấu", 2, 2)],
       match={"chu": "gm", "duoi_so": True, "match_kieu": "structural",
              "vi_du_khop": ["GM.03b", "GM1"], "vi_du_khong_khop": ["GMAIL"]},
       confusable=False, ghi_chu="word-like prefix: chỉ mô tả; không suppression trừ khi đủ nhiều đơn vị thiết kế."),
)


# ---------------------------------------------------------------- helpers (data thuần, không I/O)
def theo_khoa_phan_biet(khoa):
    """Tra entry theo khoá PHÂN BIỆT (từ _norm_ma call-site, giữ đ/d). Trả list (có thể rỗng — fail-open)."""
    k = (khoa or "").strip().lower()
    return [e for e in KB_ENTRIES if e["khoa_phan_biet"] == k]


def theo_khoa_sap(khoa):
    """Tra theo khoá SẬP (query người gõ, unaccent). Trả NHÓM entry + kèm cạnh confusable (đủ ngữ cảnh hỏi)."""
    k = (khoa or "").strip().lower()
    nhom = [e for e in KB_ENTRIES if e["khoa_sap"] == k]
    ids = {e["id"] for e in nhom}
    for e in list(nhom):
        for cid in e.get("confusable_with", ()):  # kéo cạnh vào nhóm (ĐC kéo DC và ngược lại)
            if cid not in ids:
                ce = _theo_id(cid)
                if ce:
                    nhom.append(ce); ids.add(cid)
    return nhom


def _theo_id(eid):
    for e in KB_ENTRIES:
        if e["id"] == eid:
            return e
    return None


def theo_id(eid):
    """Tra 1 entry theo id (public — graft L4 dùng). None nếu không có (fail-open)."""
    return _theo_id(eid)


def _coverage_chu(n_firm):
    if n_firm >= 3: return "nhiều đơn vị thiết kế"
    if n_firm == 2: return "hai đơn vị thiết kế"
    if n_firm == 1: return "một đơn vị thiết kế"
    return "chưa gặp trong kho bản vẽ"


def payload(entry, token_khop=None):
    """Bản PHÁT-RA-NGOÀI của entry (đi trong tool-result dưới key '_kb'). BẤT BIẾN: không leaf số,
    không field match/coverage-INT; coverage đổi sang CHỮ; token_khop (nguyên văn TỪ FILE) do call-site
    tự đặt NGOÀI '_kb' nếu muốn nó vào rổ grounding — payload KHÔNG chứa nó."""
    ngs = []
    for n in entry["nghia"]:
        ngs.append({"key": n["key"], "mo_ta": n["mo_ta"], "domain": n["domain"], "tier": n["tier"],
                    "nguon": n["nguon"], "pho_bien": _coverage_chu(n["coverage"]["n_firm"])})
    out = {"id": entry["id"], "loai": entry["loai"], "ky_hieu": entry["symbol_display"],
           "nghia": ngs, "de_nham": bool(entry["confusable"]), "ghi_chu": entry.get("ghi_chu", "")}
    if entry.get("confirm_template"):
        out["cau_hoi"] = entry["confirm_template"]["cau_hoi"]
        out["phuong_an"] = [{"key": o["key"], "label": o["label"]} for o in entry["confirm_template"]["options"]]
    return out


def kiem_tra_kho():
    """Validator bất biến (chạy trong TEST, không chạy lúc import — degrade-safe). Trả list vi phạm (rỗng = sạch)."""
    import re
    vi_pham = []
    _id_re = re.compile(r"^[a-z_]+$")
    ids = set()
    sap_map = {}
    for e in KB_ENTRIES:
        eid = e["id"]
        if not _id_re.match(eid): vi_pham.append("id có ký tự ngoài chữ+underscore: %r" % eid)
        if eid in ids: vi_pham.append("id trùng: %r" % eid)
        ids.add(eid)
        if e["loai"] not in _LOAI: vi_pham.append("%s: loai lạ %r" % (eid, e["loai"]))
        if e["on_collision"] != "ASK": vi_pham.append("%s: on_collision phải ASK khi ship" % eid)
        # digit-free MỌI chuỗi phát-ra-ngoài (đo trên payload thật)
        p = payload(e)
        chuoi = _json.dumps(p, ensure_ascii=False)
        if re.search(r"\d", chuoi):
            vi_pham.append("%s: payload chứa CHỮ SỐ (cấm — chống lọt grounding): %s"
                           % (eid, re.findall(r"[^\s\"]*\d[^\s\"]*", chuoi)[:4]))
        # số leaf trong payload (int/float) — cấm tuyệt đối
        def _quet(v, duong):
            if isinstance(v, bool): return
            if isinstance(v, (int, float)): vi_pham.append("%s: payload leaf SỐ tại %s" % (eid, duong))
            elif isinstance(v, dict):
                for k2, v2 in v.items(): _quet(v2, duong + "." + str(k2))
            elif isinstance(v, (list, tuple)):
                for i2, v2 in enumerate(v): _quet(v2, duong)
        _quet(p, eid)
        for n in e["nghia"]:
            if n["tier"] not in _TIERS: vi_pham.append("%s: tier lạ %r" % (eid, n["tier"]))
            if not _id_re.match(n["key"]): vi_pham.append("%s: nghia.key %r ngoài chữ+underscore" % (eid, n["key"]))
        if e["confusable"] and e["loai"] != "bai_hoc":
            ct = e.get("confirm_template")
            if not ct: vi_pham.append("%s: confusable nhưng thiếu confirm_template" % eid)
            else:
                keys = [o["key"] for o in ct["options"]]
                if "khac_khong_chac" not in keys: vi_pham.append("%s: thiếu option khac_khong_chac" % eid)
                for o in ct["options"]:
                    if not _id_re.match(o["key"]): vi_pham.append("%s: option key %r ngoài chữ+underscore" % (eid, o["key"]))
                if "{ky_hieu}" not in ct["cau_hoi"]: vi_pham.append("%s: cau_hoi thiếu placeholder {ky_hieu}" % eid)
        sap_map.setdefault(e["khoa_sap"], []).append(e)
        for cid in e.get("confusable_with", ()):
            ce = _theo_id(cid)
            if ce is None: vi_pham.append("%s: confusable_with trỏ id không tồn tại %r" % (eid, cid))
            elif eid not in ce.get("confusable_with", ()) and ce["khoa_sap"] != e["khoa_sap"]:
                vi_pham.append("%s <-> %s: cạnh confusable không ĐỐI XỨNG (và không cùng khoa_sap)" % (eid, cid))
    # trùng khoa_sap giữa các entry KHÁC khoa_phan_biet -> bắt buộc có cạnh nối
    for k, es in sap_map.items():
        pb = {e["khoa_phan_biet"] for e in es}
        if len(es) > 1 and len(pb) > 1:
            for e in es:
                others = {x["id"] for x in es if x is not e}
                if not (others & set(e.get("confusable_with", ()))):
                    vi_pham.append("khoa_sap %r: %s trùng khoá-sập với %s nhưng THIẾU cạnh confusable_with"
                                   % (k, e["id"], sorted(others)))
    return vi_pham


def theo_nghia_don(cum_tu):
    """TRA NGƯỢC: cụm từ tiếng Việt -> ký hiệu. CHỈ với mục có ĐÚNG MỘT nghĩa.

    VÌ SAO CẦN: mã cấu kiện trên bản vẽ ghi bằng KÝ HIỆU ('ĐC-1'), còn đối tác hỏi bằng TIẾNG VIỆT
    ('đài cọc'). Không nối được hai đầu thì máy trả lời sai mà tự tin. ĐO THẬT trên corpus:
    `tra_cuu_so_luong('đài cọc')` trên `2. KetCau MN GiaLoc` trả về **131** ('chi tiết nối cọc với đài')
    trong khi 59 đài cọc thật (`ĐC-1 SL-19`, `ĐC-2 SL-10`, `ĐC-3 SL-25`…) BIẾN MẤT; trên
    `2. KET CAU MONG` thì trả về **rỗng** hoàn toàn dù file có `chi tiết móng ĐC1 (sl: 40)`.

    ⛔ CHỈ mục MỘT NGHĨA. Mục ĐA NGHĨA (15/24: 'dầm'→D-x lẫn DC-x, 'cửa đi'→CH lẫn D-x lẫn Đ-x…)
    TUYỆT ĐỐI không tra ngược — chọn giúp một nghĩa chính là ĐOÁN, và chính kho đã ghi
    `on_collision: ASK` cho chúng. Tra ngược mục đa nghĩa = biến kho chống-nhầm thành nguồn gây nhầm.
    Tập an toàn đo được: 7/24 mục (đài cọc · đường kính · cấp thoát nước · lý trình tuyến · cút ống ·
    khu vệ sinh · giằng móng).

    Trả None nếu không chắc — fail-open, KHÔNG đoán."""
    s = (cum_tu or "").strip().lower()
    if len(s) < 3:
        return None
    for e in KB_ENTRIES:
        ng = e.get("nghia") or []
        chu = (e.get("match") or {}).get("chu")
        if len(ng) != 1 or not chu:
            continue                                  # đa nghĩa hoặc không có khoá chữ -> BỎ QUA
        mo_ta = (ng[0].get("mo_ta") or "").split("(")[0].strip().lower()
        if not mo_ta or len(mo_ta) < 3:
            continue
        if s == mo_ta or (len(mo_ta) >= 4 and mo_ta in s):
            return {"id": e["id"], "chu": chu, "symbol": e.get("symbol_display"),
                    "nghia": ng[0].get("mo_ta")}
    return None


def _canonical():
    return _json.dumps(KB_ENTRIES, ensure_ascii=False, sort_keys=True)


KB_HASH = _hashlib.sha256(_canonical().encode("utf-8")).hexdigest()
