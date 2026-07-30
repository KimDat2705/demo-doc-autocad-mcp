# -*- coding: utf-8 -*-
"""RỔ NEO GROUNDING — cái gì được phép làm BẰNG CHỨNG cho một con số.
TẤT ĐỊNH, OFFLINE, KHÔNG tốn API. Bản vẽ SYNTHETIC (ezdxf) nên không phụ thuộc kho file gitignore.
Chạy:  python tests/test_neo_grounding.py

VÌ SAO CÓ SUITE NÀY — 2 lỗ ĐANG LIVE, đo thật 2026-07-30 (78 file, gọi tool THẬT):

(1) DẤU TRỪ GIẢ TỪ MÃ HIỆU. `_collect_numbers` quét rổ neo bằng `-?\\d+` trên MỌI chuỗi, nên gạch nối
    trong mã cấu kiện thành DẤU ÂM: 'DẦM D2-10' -> -10.0 · 'CỘT C-5' -> -5.0 · 'TB6-DV-CT-CN-27' -> -27.0.
    BẤT ĐỐI XỨNG CHÍ MẠNG: phía CÂU TRẢ LỜI, `_answer_numbers` strip mã-hiệu TRƯỚC khi lấy số, còn phía
    RỔ NEO không strip gì -> mã hiệu KHÔNG BAO GIỜ là "khẳng định" nhưng LUÔN là "bằng chứng".
    Đo: **68/76 file** có ≥1 neo ÂM; **24/76 file** có neo âm nằm ĐÚNG dải cao độ (-30..-0,1) sinh THUẦN
    từ mã hiệu/tên file. Tức TÊN DẦM/CỘT đang cấp phép cho model bịa cao độ âm — đúng lớp lỗi id135.

(2) TÊN FILE LÀM BẰNG CHỨNG. `thong_tin_file` trả {'name': <tên file>}, tool này KHÔNG nằm trong tuple
    loại-trừ -> mọi chữ số trong tên file vào thẳng rổ neo. Đây là kênh do NGƯỜI DÙNG kiểm soát 100%,
    KHÔNG cần đụng tới bản vẽ. Đo thật (CÙNG nội dung byte, chỉ đổi tên): tên gốc -> câu
    'Cao do day dai coc la -13,7 m.' CHẶN; đổi tên thành 'MC coc -13.7 va 7500.dxf' -> câu đó LỌT.
    Cộng luật ×1000/÷1000 của `_is_grounded`, mỗi số tên-file khoá được 3 bậc đơn vị.

⚠ NGUYÊN TẮC KHI SỬA: rổ neo CỐ TÌNH rộng tay (thà bỏ sót bịa còn hơn từ chối nhầm câu đúng). Bản vá
phải PHẪU THUẬT — chỉ bỏ đúng số âm BỊA RA TỪ GẠCH NỐI, tuyệt đối KHÔNG thu hẹp neo dương (Ø22, 4200)
và KHÔNG bỏ cao độ âm THẬT (-13.7). Các ca đối chứng dưới đây khoá đúng điều đó.
"""
import os, sys, io, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
os.environ.setdefault("READFILE_MAX_MB", "300")
os.environ.setdefault("HOC_LOG", "0")

import re
import ezdxf
import tools_core as tc
import mcp_bridge as B

PASS = FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = PASS + int(bool(cond)), FAIL + int(not cond)
    print("  [%s] %s%s" % ("OK" if cond else "FAIL", name, "" if cond else "   <<< " + str(extra)))


def _ro(obj):
    return B._collect_numbers(B._strip_neo(obj))


def main():
    print("[P.1] MÃ HIỆU có gạch nối KHÔNG được sinh neo ÂM")
    r = _ro({"ket_qua": [{"text": "DẦM D2-10 tiết diện 220x400"}, {"text": "CỘT C-5 trục A"},
                         {"text": "sheet TB6-DV-CT-CN-27"}, {"text": "dải 700-1500"}]})
    am = sorted(v for v in r if v < 0)
    ok("không còn số âm nào trong rổ", am == [], am)
    ok("nhưng phần DƯƠNG vẫn vào rổ bình thường (không thu hẹp)",
       {10.0, 5.0, 27.0, 220.0, 400.0, 700.0, 1500.0} <= r, sorted(r))

    print("[P.2] neo DƯƠNG dính chữ vẫn giữ (không được từ-chối-oan)")
    r = _ro({"ket_qua": [{"text": "thép Ø22 dài 4200 mm"}, {"text": "mác B20"}, {"text": "ống DN80"}]})
    ok("Ø22 -> 22 vẫn là neo", 22.0 in r, sorted(r))
    ok("4200 vẫn là neo", 4200.0 in r, sorted(r))
    ok("B20 -> 20 vẫn là neo", 20.0 in r, sorted(r))

    print("[P.3] cao độ ÂM THẬT vẫn phải là neo (dấu trừ đứng riêng)")
    r = _ro({"ket_qua": [{"text": "cao độ -13.7 m"}, {"text": "-3,5"}, {"text": "đáy móng -10.5"}]})
    ok("-13.7 giữ", -13.7 in r, sorted(r))
    ok("-3,5 giữ", -3.5 in r, sorted(r))
    ok("-10.5 giữ", -10.5 in r, sorted(r))

    print("[P.4] HỆ QUẢ: rổ chỉ có mã hiệu -> câu bịa cao độ âm bị CHẶN")
    ro_ma = _ro({"ket_qua": [{"text": "DẦM D2-10"}, {"text": "CỘT C-5"}, {"text": "TB6-DV-CT-CN-27"}]})
    for cau in ("Cao độ đáy móng là -10 m.", "Cao độ đáy đài là -5 m.", "Cao độ -27 m."):
        ok("CHẶN: %s" % cau, B._guard_text(cau, ro_ma) != cau)

    print("[P.5] ĐỐI CHỨNG: cao độ âm có neo THẬT thì vẫn LỌT (không nuke câu đúng)")
    ro_that = _ro({"ket_qua": [{"text": "cao độ đáy móng -10.0 m"}]})
    cau = "Cao độ đáy móng là -10 m."
    ok("LỌT khi có neo thật", B._guard_text(cau, ro_that) == cau)

    print("[P.6] TÊN FILE không được làm bằng chứng — khoá 'name' bị loại khỏi rổ")
    r = _ro({"name": "MC coc -13.7 va 7500.dxf", "so_layer": 35})
    ok("số trong tên file KHÔNG vào rổ", -13.7 not in r and 7500.0 not in r, sorted(r))
    ok("số metadata thật (so_layer) VẪN vào rổ", 35.0 in r, sorted(r))

    print("[P.7] END-TO-END: cùng nội dung byte, đổi TÊN -> rổ neo KHÔNG đổi")
    doc = ezdxf.new(); msp = doc.modelspace()
    msp.add_linear_dim(base=(0, 50), p1=(0, 0), p2=(1000, 0)).render()
    t = tempfile.mkdtemp()
    p1 = os.path.join(t, "ban ve thuong.dxf")
    p2 = os.path.join(t, "MC coc -13.7 va 7500.dxf")
    doc.saveas(p1); doc.saveas(p2)
    ro1 = _ro(tc.Drawing(p1).thong_tin_file())
    ro2 = _ro(tc.Drawing(p2).thong_tin_file())
    ok("hai rổ neo GIỐNG HỆT nhau", ro1 == ro2, (sorted(ro1), sorted(ro2)))
    for cau in ("Cao do day dai coc la -13,7 m.", "Chieu sau ho mong 7500 mm."):
        ok("CHẶN dù tên file mang đúng số đó: %s" % cau, B._guard_text(cau, ro2) != cau)

    print("[P.8] kho kiến thức VẪN không lọt rổ (_strip_neo phải lồng _strip_kb)")
    r = _ro({"ket_qua": [{"text": "cửa D1"}], "_kb": {"giai_thich": "rộng 25 sâu 12.5"}})
    ok("số trong '_kb' không vào rổ", 25.0 not in r and 12.5 not in r, sorted(r))

    print("[P.9] source-guard: call-site và cấu trúc lọc")
    bsrc = open(os.path.join(ROOT, "mcp_bridge.py"), encoding="utf-8").read()
    ok("call-site gom số đi qua _strip_neo", "_collect_numbers(_strip_neo(result))" in bsrc)
    ok("_strip_neo lồng _strip_kb", re.search(r"def _strip_neo\([\s\S]{0,400}?_strip_kb\(", bsrc) is not None)
    ok("_strip_neo lồng _strip_ten_file", re.search(r"def _strip_neo\([\s\S]{0,400}?_strip_ten_file\(", bsrc) is not None)

    print("\n%d PASS / %d FAIL" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
