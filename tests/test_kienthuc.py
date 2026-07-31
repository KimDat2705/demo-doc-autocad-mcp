# -*- coding: utf-8 -*-
"""L1 (kho kiến thức DEV-soạn, pivot 2026-07-26) — TẤT ĐỊNH, offline, KHÔNG tốn API.
Khoá bất biến kho: validator sạch + digit-free (chống lọt grounding, đo THẬT qua _collect_numbers) +
byte-lock KB_HASH (kiểu I9 — đổi kho phải chạy harness/scripts/kb_refreeze.sh rồi dán hash mới) +
2 tầng khoá (giữ đ/d) + fail-open + không import chéo dự án.
Chạy: python tests/test_kienthuc.py"""
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

PASS = FAIL = 0

# BYTE-LOCK (kiểu I9): đổi KB_ENTRIES -> hash đổi -> test này FAIL CÓ CHỦ ĐÍCH.
# Quy trình đổi kho: sửa kienthuc.py -> bash harness/scripts/kb_refreeze.sh -> dán hash mới vào đây.
KB_HASH_DONG_BANG = "e55ac112d1a327006159b4399bd5deaf57753a713c3bec4a9792240d772c5162"


def _emit(name, ok, note=""):
    global PASS, FAIL
    PASS += int(bool(ok)); FAIL += int(not ok)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, (" -> %s" % note) if note and not ok else ""))


def main():
    print("[L1] kho kiến thức kienthuc.py — validator + digit-free + byte-lock + tra cứu 2 tầng")
    import kienthuc

    # ---- [K1] validator bất biến sạch ----
    vi = kienthuc.kiem_tra_kho()
    _emit("K1: kiem_tra_kho() == 0 vi phạm", not vi, "; ".join(vi[:5]))
    _emit("K1b: số entry đợt đầu trong khoảng cam kết (>=20, <=30 — không soạn tràn lan)",
          20 <= len(kienthuc.KB_ENTRIES) <= 30, str(len(kienthuc.KB_ENTRIES)))

    # ---- [K2] byte-lock hash (I9-style) ----
    _emit("K2: KB_HASH khớp hash ĐÓNG BĂNG (đổi kho phải qua kb_refreeze.sh)",
          kienthuc.KB_HASH == KB_HASH_DONG_BANG, kienthuc.KB_HASH)

    # ---- [K3] B5-lite THẬT: payload mọi entry (bọc '_kb') KHÔNG đóng góp gì vào rổ grounding ----
    import mcp_bridge
    gop = set()
    for e in kienthuc.KB_ENTRIES:
        gop |= mcp_bridge._collect_numbers({"_kb": kienthuc.payload(e)})
    _emit("K3: _collect_numbers(payload mọi entry) == RỖNG (đo qua hàm THẬT của guard)", gop == set(), str(sorted(gop)[:8]))

    # ---- [K4] payload không rò field nội bộ ----
    ro = []
    for e in kienthuc.KB_ENTRIES:
        p = kienthuc.payload(e)
        if "match" in p or "coverage" in str(p):  # match (chứa ví dụ có SỐ) + coverage INT cấm phát ra ngoài
            ro.append(e["id"])
        for n in p.get("nghia", []):
            if any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in n.values()):
                ro.append(e["id"] + ":leaf-so")
    _emit("K4: payload KHÔNG chứa field match / coverage INT / leaf số", not ro, str(ro[:5]))

    # ---- [K5] tra cứu 2 tầng khoá: giữ đ/d (bài học id84) + kéo cạnh + fail-open ----
    pb = [e["id"] for e in kienthuc.theo_khoa_phan_biet("djc")]
    _emit("K5a: khoá PHÂN BIỆT 'djc' (ĐC) -> CHỈ đài cọc (không dính DC)", pb == ["dc_dai_coc"], str(pb))
    sap = sorted(e["id"] for e in kienthuc.theo_khoa_sap("dc"))
    _emit("K5b: khoá SẬP 'dc' (người gõ) -> NHÓM cả cặp ĐC+DC qua cạnh confusable",
          sap == ["dc_dai_coc", "dc_dam_chi_tiet"], str(sap))
    _emit("K5c: ký hiệu NGOÀI kho -> danh sách RỖNG (fail-open, không đoán, không crash)",
          kienthuc.theo_khoa_phan_biet("xyz_la") == [] and kienthuc.theo_khoa_sap("") == [])

    # ---- [K6] confirm-template: mọi entry dễ-nhầm có câu hỏi + option 'khác/không chắc' ----
    thieu = [e["id"] for e in kienthuc.KB_ENTRIES
             if e["confusable"] and e["loai"] != "bai_hoc"
             and (not e.get("confirm_template")
                  or "khac_khong_chac" not in [o["key"] for o in e["confirm_template"]["options"]])]
    _emit("K6: mọi entry confusable có confirm_template + option khac_khong_chac", not thieu, str(thieu))

    # ---- [K7] on_collision == ASK toàn bộ (trạng thái ship: KHÔNG auto-resolve nghĩa) ----
    auto = [e["id"] for e in kienthuc.KB_ENTRIES if e["on_collision"] != "ASK"]
    _emit("K7: on_collision == 'ASK' toàn bộ (không auto-chọn nghĩa khi ship)", not auto, str(auto))

    # ---- [K8] cô lập module: kienthuc KHÔNG import gì từ dự án + KHÔNG I/O (degrade-safe, không vòng) ----
    src = open(os.path.join(ROOT, "kienthuc.py"), encoding="utf-8").read()
    xau = re.findall(r"^\s*(?:import|from)\s+(tools_core|mcp_server|mcp_bridge|app|ezdxf|flask)\b",
                     src, re.M) + re.findall(r"\bopen\s*\(", src)
    _emit("K8: kienthuc.py là DATA THUẦN (không import dự án/ezdxf/flask, không open())", not xau, str(xau[:4]))

    # ---- [K9] L2 tầng-2 THẬT: số LÉN trong '_kb' (giả lập entry tương lai soạn lỗi) vẫn KHÔNG vào rổ ----
    ket_qua_gia = {"tin_hieu": "①", "ung_vien": [{"vn_verbatim": "ĐC-1", "handle": "ABCDE"}],
                   "_kb": {"nghia": [{"mo_ta": "gia lap LOI: cap ben B25 la 25 MPa"}],
                           "coverage_lot": 25, "nested": {"_sau": [12.5, "sau 3.6m"]}}}
    gop = mcp_bridge._collect_numbers(mcp_bridge._strip_kb(ket_qua_gia))
    _emit("K9: số lén trong '_kb' (25 / 12.5 / 3.6 — giả lập entry lỗi) KHÔNG lọt rổ sau _strip_kb",
          not ({25.0, 12.5, 3.6} & gop), str(sorted(gop)[:8]))

    # ---- [K10] đối chứng CHỐNG TỪ-CHỐI-OAN: số của FILE nằm NGOÀI '_kb' VẪN vào rổ ----
    ket_qua_file = {"nguyen_van": "L=800 (1 bộ)", "handle": "AF012",
                    "_kb": {"mo_ta": "đài cọc (kết cấu móng)"}}
    gop2 = mcp_bridge._collect_numbers(mcp_bridge._strip_kb(ket_qua_file))
    _emit("K10: số NGUYÊN VĂN FILE ngoài '_kb' (L=800) VẪN vào rổ grounding (không từ-chối-oan)",
          800.0 in gop2, str(sorted(gop2)[:8]))

    # ---- [K11] source-guard L2: call-site gom số phải qua _strip_kb + tuple loại có tra_ky_hieu ----
    bsrc = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    # ⚠ HỢP ĐỒNG ĐÃ MỞ RỘNG CÓ Ý THỨC (2026-07-30): call-site nay đi qua _strip_neo — cửa DUY NHẤT gộp
    # mọi nguồn không được làm bằng chứng: '_kb' (kho kiến thức, L2) + 'name' (TÊN FILE do người dùng đặt,
    # đo được là kênh bơm neo ngoài bản vẽ). Ý ĐỊNH GỐC của K11a (không bao giờ gom RAW, kho luôn bị strip)
    # được giữ NGUYÊN và còn được khoá CHẶT HƠN: kiểm thêm rằng _strip_neo thực sự lồng _strip_kb.
    _emit("K11a: call-site dùng _collect_numbers(_strip_neo(result)) (không gom raw)",
          "_collect_numbers(_strip_neo(result))" in bsrc)
    _emit("K11a2: _strip_neo VẪN lồng _strip_kb (đảm bảo kho kiến thức không bao giờ lọt rổ)",
          re.search(r"def _strip_neo\([\s\S]{0,400}?_strip_kb\(", bsrc) is not None)
    _emit("K11b: 'tra_ky_hieu' nằm trong tuple loại-toàn-phần khỏi rổ (tiền lệ doc_bang_nhung/I4a)",
          re.search(r"doc_bang_nhung\",\s*\"phat_hien_bang_ve_net\",\s*\"tra_ky_hieu\"", bsrc) is not None)

    # ---- [K12] TRA NGƯỢC cụm-từ-tiếng-Việt -> ký hiệu (1.05: hỏi 'đài cọc' mà máy trả ra thứ khác) ----
    # VẤN ĐỀ THẬT: bản vẽ ghi mã bằng KÝ HIỆU ('ĐC-1 (SL-19)'), đối tác hỏi bằng TIẾNG VIỆT ('đài cọc').
    # Đo trên corpus: `tra_cuu_so_luong('đài cọc')` trả 131 ('chi tiết nối cọc với đài') còn 59 đài cọc
    # THẬT biến mất; file khác trả RỖNG + câu "bản vẽ KHÔNG ghi sẵn số lượng" (SAI mà TỰ TIN).
    kb = kienthuc.theo_nghia_don("đài cọc")
    _emit("K12a: 'đài cọc' -> ký hiệu ĐC", bool(kb) and kb.get("chu") == "đc", kb)
    _emit("K12b: 'giằng móng' -> GM", (kienthuc.theo_nghia_don("giằng móng") or {}).get("chu") == "gm")
    _emit("K12c: cụm dài chứa cụm chuẩn vẫn tra được ('bao nhiêu đài cọc')",
          (kienthuc.theo_nghia_don("bao nhiêu đài cọc") or {}).get("chu") == "đc")
    # ⛔ ĐA NGHĨA TUYỆT ĐỐI KHÔNG TRA NGƯỢC — chọn giúp 1 nghĩa chính là ĐOÁN, và kho đã ghi ASK.
    # 'dầm' có ở CẢ dc_dam_chi_tiet (DC-x) LẪN d_da_nghia (D-x); 'cửa đi' có ở CH, D-x, Đ-x.
    for tu in ("dầm", "cửa đi", "cột", "sàn", "tầng", "vách"):
        _emit("K12d: ĐA NGHĨA '%s' -> KHÔNG tra ngược (không đoán)" % tu,
              kienthuc.theo_nghia_don(tu) is None, kienthuc.theo_nghia_don(tu))
    _emit("K12e: chuỗi rỗng/quá ngắn -> None (fail-open)",
          kienthuc.theo_nghia_don("") is None and kienthuc.theo_nghia_don("đc") is None)
    _emit("K12f: cụm lạ -> None, KHÔNG bịa ký hiệu", kienthuc.theo_nghia_don("xà gồ mạ kẽm zzz") is None)
    # tập an toàn phải đúng bằng số mục MỘT NGHĨA — nếu ai thêm nghĩa vào 1 entry thì ca này ĐỎ
    _mot_nghia = [e["id"] for e in kienthuc.KB_ENTRIES
                  if len(e.get("nghia") or []) == 1 and (e.get("match") or {}).get("chu")]
    _emit("K12g: tập tra-ngược = đúng các mục MỘT NGHĨA (đo được 7/24)",
          len(_mot_nghia) == 7, (len(_mot_nghia), _mot_nghia))
    # source-guard: không được gộp vào danh sách chính (chống mô hình CỘNG 131 + 59 = 190)
    tsrc = open(os.path.join(ROOT, "tools_core.py"), encoding="utf-8").read()
    _emit("K12h: kết quả theo-ký-hiệu để RIÊNG ở 'theo_ky_hieu', KHÔNG gộp vào danh_sach_so_luong",
          '"theo_ky_hieu"' in tsrc and 'r["theo_ky_hieu"] = them' in tsrc)
    _emit("K12i: ghi_chu CẤM cộng hai danh sách", "TUYỆT ĐỐI KHÔNG CỘNG hai" in tsrc)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
