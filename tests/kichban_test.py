# -*- coding: utf-8 -*-
"""Chạy BỘ KỊCH BẢN TEST (tổng quát -> chi tiết -> phức tạp -> bẫy) trên demo 2 (2.5-flash)
để lấy ĐÁP ÁN THẬT + đối chiếu ground truth. File: KIẾN TRÚC CT-A (file cửa đối tác dùng)."""
import os, sys, io, json, time
os.environ["READFILE_MAX_MB"] = "300"; os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import mcp_bridge

from corpus_local import KT as F   # corpus THAT giu ngoai repo (gitignored)
# (câu hỏi, nhóm, đáp án chuẩn từ ground truth)
QS = [
 ("Có bao nhiêu layer trong bản vẽ?", "TỔNG QUÁT", "141 layer"),
 ("File này có bao nhiêu đối tượng?", "TỔNG QUÁT", "8024 đối tượng"),
 ("Có bao nhiêu đường kích thước (dimension)?", "TỔNG QUÁT", "2355"),
 ("Số lượng cửa đi D1 là bao nhiêu?", "SỐ LƯỢNG (partner)", "24 bộ"),
 ("Tổng diện tích cửa D1?", "TAKEOFF (partner)", "GĐ2: cần tính 1.3x2.7x24=84.24m2 - demo 2 CHƯA tính"),
 ("Cửa S1 và cửa SW mỗi loại bao nhiêu bộ?", "SỐ LƯỢNG", "S1=16, SW=16"),
 ("Cửa DW và cửa D2 bao nhiêu bộ?", "SỐ LƯỢNG", "DW=8, D2=8"),
 ("Tổng tất cả các loại cửa là bao nhiêu bộ?", "PHỨC TẠP", "73 bộ (24+16+16+8+8+1)"),
 ("Cửa D1 có kích thước bao nhiêu?", "CHI TIẾT", "1300x2700mm"),
 ("Cửa D1 dùng vật liệu và phụ kiện gì?", "CHI TIẾT", "nhôm hệ PMA XF55, kính 6.38mm, 06 bộ bản lề 3D"),
 ("Tổng khối lượng thép tròn của công trình?", "THÉP", "564.8 kg"),
 ("Thép Ø22 có bao nhiêu thanh, nặng bao nhiêu kg?", "THÉP", "20 thanh, 298.4 kg"),
 ("Độ dốc mái bao nhiêu?", "GIÁ TRỊ GHI SẴN", "i=32% và i=23%"),
 ("Diện tích lát gạch 600x600 là bao nhiêu m2?", "GIÁ TRỊ GHI SẴN", "591m2 và 545m2"),
 ("Mác bê tông móng là bao nhiêu?", "VẬT LIỆU", "B20 (mác 250), lót móng mác 150"),
 ("Đánh dấu cửa D1 trên bản vẽ giúp tôi.", "HIGHLIGHT", "ra ảnh khoanh đỏ vị trí cửa D1"),
 ("Công trình dài bao nhiêu mét?", "BẪY (chống bịa)", "PHẢI TỪ CHỐI (không suy diễn kích thước tổng)"),
 ("Công trình có bao nhiêu thang máy?", "BẪY (chống bịa)", "PHẢI nói KHÔNG CÓ (không bịa)"),
 ("Chữ 'cửa D1' xuất hiện bao nhiêu lần, có phải số bộ cửa không?", "BẪY (kỹ thuật vs thực tế)", "phân biệt: số lần XH ≠ 24 bộ"),
]


def main():
    br = mcp_bridge.MCPBridge(["mcp_server.py"], env={"READFILE_MAX_MB": "300"})
    s = br.call("nap_ban_ve", {"path": F}, timeout=600)
    summ = "%s (%s đối tượng, %s layer)" % (s["name"], s["tong_doi_tuong"], s["so_layer"])
    out = []
    for q, nhom, dapan in QS:
        t = time.time()
        try: r = mcp_bridge.tra_loi_ai(br, q, summ); a = r["answer"]; anh = r.get("anh_id")
        except Exception as e: a = "[[LỖI]] " + str(e)[:40]; anh = None
        out.append({"nhom": nhom, "q": q, "dapan": dapan, "demo": a, "anh": anh, "s": round(time.time() - t, 1)})
        print("\n[%s] %s (%.0fs)" % (nhom, q, out[-1]["s"]))
        print("  ĐÁP ÁN CHUẨN:", dapan)
        print("  DEMO 2 ->", a[:220].replace("\n", " "), ("[có ảnh]" if anh else ""))
    br.close()
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "kichban_ketqua.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
