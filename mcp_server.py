# -*- coding: utf-8 -*-
"""
mcp_server.py — MCP SERVER CHUẨN (FastMCP, stdio) cho đọc + trực quan hoá bản vẽ AutoCAD.

Đây là điểm cốt lõi của demo 2 (hướng MCP): một MCP server ĐỘC LẬP, đúng chuẩn —
có thể cắm vào BẤT KỲ MCP client nào (Claude Desktop, Gemini CLI, Cursor...), không chỉ host này.

Cách dùng: client gọi `nap_ban_ve(path)` trước (host đã lưu file vào server), rồi gọi các
công cụ đọc/đánh dấu. Mọi con số do CODE tất định tính (chống bịa) + kèm handle truy nguồn.
Chạy: python mcp_server.py   (giao tiếp JSON-RPC qua stdin/stdout)
"""
from mcp.server.fastmcp import FastMCP
from tools_core import Drawing

mcp = FastMCP("doc-autocad")
DRAWING = None  # bản vẽ ĐANG nạp (1 bản/lượt — đủ cho demo)


def _need():
    if DRAWING is None:
        return {"loi": "Chưa nạp bản vẽ. Hãy gọi nap_ban_ve(path) trước."}
    return None


@mcp.tool()
def nap_ban_ve(path: str) -> dict:
    """Nạp 1 file bản vẽ (.dwg/.dxf) trên máy chủ để bắt đầu tra cứu. Trả về tóm tắt (số layer/đối tượng...).

    Args:
        path: đường dẫn file trên máy chủ (host đã lưu khi người dùng upload).
    """
    global DRAWING
    DRAWING = Drawing(path)
    return DRAWING.tom_tat()


@mcp.tool()
def tim_kiem(tu_khoa: str = "", layer: str = "", gioi_han: int = 40) -> dict:
    """Tìm các đoạn chữ chứa từ khoá (không phân biệt dấu/hoa-thường). Trả nội dung + handle + layer.
    Dùng cho mọi câu 'tìm', 'có chữ', 'liệt kê ... chứa'. Để trống cả hai sẽ báo lỗi."""
    return _need() or DRAWING.tim_kiem(tu_khoa=tu_khoa, layer=layer, gioi_han=gioi_han)


@mcp.tool()
def dem_so_luong(tu_khoa: str) -> dict:
    """Đếm số ĐOẠN CHỮ chứa từ khoá (số đoạn chữ, KHÔNG phải số cấu kiện vật lý).
    Dùng cho 'có bao nhiêu lần xuất hiện', 'đếm chữ'."""
    return _need() or DRAWING.dem_so_luong(tu_khoa=tu_khoa)


@mcp.tool()
def tra_cuu_so_luong(tu_khoa: str) -> dict:
    """Tra SỐ LƯỢNG THẬT của cấu kiện khi bản vẽ GHI RÕ (nhãn 'số lượng: N bộ' / 'SL='). DÙNG cho
    'có bao nhiêu X', 'số lượng X' (X=dầm/cột/đài/cửa). Không ghi sẵn -> báo rõ KHÔNG có."""
    return _need() or DRAWING.tra_cuu_so_luong(tu_khoa=tu_khoa)


@mcp.tool()
def liet_ke_so_luong(loc: str = "") -> dict:
    """Liệt kê TẤT CẢ mục có ghi SỐ LƯỢNG trong 1 lần gọi (cửa, cấu kiện...). DÙNG cho
    'liệt kê các loại cửa và số lượng'. Có thể lọc bằng từ khoá 'loc'."""
    return _need() or DRAWING.liet_ke_so_luong(loc=loc)


@mcp.tool()
def tong_so_luong(loc: str = "") -> dict:
    """CỘNG tổng số lượng cấu kiện cùng nhóm — 'TỔNG bao nhiêu bộ cửa'. Hệ thống tự cộng + breakdown."""
    return _need() or DRAWING.tong_so_luong(loc=loc)


@mcp.tool()
def thong_ke_thep(duong_kinh: str = "") -> dict:
    """Đọc BẢNG THỐNG KÊ THÉP (cốt thép TRÒN): số thanh, chiều dài, KHỐI LƯỢNG kg theo đường kính —
    số THẬT do kỹ sư lập. DÙNG cho 'khối lượng thép', 'bao nhiêu kg/tấn thép', 'thép Ø16'. Trống = tổng."""
    return _need() or DRAWING.thong_ke_thep(duong_kinh=duong_kinh)


@mcp.tool()
def thong_ke_thep_hinh() -> dict:
    """Đọc bảng THÉP HÌNH / INOX / xà gồ (tiết diện hộp/I/U): số lượng + kg theo tiết diện.
    Dùng cho 'khối lượng thép hình', 'inox bao nhiêu kg'. RIÊNG với cốt thép tròn."""
    return _need() or DRAWING.thong_ke_thep_hinh()


@mcp.tool()
def liet_ke_chu_theo_layer(layer: str, gioi_han: int = 60) -> dict:
    """Liệt kê các đoạn chữ trên một layer (lớp) cụ thể, kèm handle."""
    return _need() or DRAWING.liet_ke_chu_theo_layer(layer=layer, gioi_han=gioi_han)


@mcp.tool()
def liet_ke_sheet() -> dict:
    """Liệt kê các bản vẽ con (sheet/tiêu đề) trong file, kèm handle."""
    return _need() or DRAWING.liet_ke_sheet()


@mcp.tool()
def liet_ke_layer() -> dict:
    """Liệt kê toàn bộ tên layer (lớp) trong bản vẽ."""
    return _need() or DRAWING.liet_ke_layer()


@mcp.tool()
def liet_ke_block() -> dict:
    """Liệt kê các loại block (ký hiệu/cấu kiện lặp) và số lần dùng."""
    return _need() or DRAWING.liet_ke_block()


@mcp.tool()
def thong_ke_doi_tuong() -> dict:
    """Thống kê tổng số đối tượng + số lượng theo loại (LINE, TEXT, INSERT...)."""
    return _need() or DRAWING.thong_ke_doi_tuong()


@mcp.tool()
def thong_tin_kich_thuoc() -> dict:
    """Thông tin các đường kích thước (DIMENSION): số lượng, min/max, giá trị phổ biến (mm)."""
    return _need() or DRAWING.thong_tin_kich_thuoc()


@mcp.tool()
def danh_dau_cau_kien(tu_khoa: str = "", layer: str = "") -> dict:
    """⭐ TRỰC QUAN HOÁ: KHOANH ĐỎ vị trí các cấu kiện khớp từ khoá NGAY TRÊN ẢNH bản vẽ và trả 'anh_id'.
    DÙNG khi người dùng muốn 'chỉ ra', 'đánh dấu', 'cho xem ở đâu', 'highlight' cấu kiện X trên bản vẽ.
    Trả số vị trí + anh_id (host hiển thị ảnh). KHÔNG phải số lượng thật (xem tra_cuu_so_luong)."""
    return _need() or DRAWING.highlight(tu_khoa=tu_khoa, layer=layer)


@mcp.tool()
def tinh_dai_luong(ten_dai_luong: str, ma_cau_kien: str = "", inputs_bo_sung: str = "") -> dict:
    """⭐ GIAI ĐOẠN 2 — TÍNH một đại lượng (takeoff) từ số liệu CÓ SẴN trong file:
    diện tích cửa, thể tích bê tông cột, ván khuôn cột... DÙNG khi người dùng hỏi TÍNH
    ('tổng diện tích cửa D1', 'thể tích bê tông cột C1', 'ván khuôn cột C1').
    - ten_dai_luong: 'diện tích cửa' | 'thể tích bê tông cột' | 'ván khuôn cột' (hoặc mô tả tự do).
    - ma_cau_kien: mã cấu kiện, vd 'D1', 'C1', 'cửa D1'.
    - inputs_bo_sung: JSON số liệu ĐỐI TÁC cấp khi tool báo thiếu, vd '{"chieu_cao":3600}' (đơn vị mm). Trống nếu chưa có.
    Trả: ĐỦ input -> ket_qua + so_do_he_thong_tinh; THIẾU -> inputs_da_co + inputs_thieu + can_bo_sung=true (KHÔNG bịa số thiếu)."""
    return _need() or DRAWING.tinh_dai_luong(ten_dai_luong, ma_cau_kien, inputs_bo_sung)


if __name__ == "__main__":
    mcp.run()
