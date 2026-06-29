# ============================================================================
# Dockerfile — DEMO 2 (hướng MCP) chạy trên cloud (Render / Railway / VPS).
#   - Python 3.10 + Flask + ezdxf + matplotlib (render) + mcp + google-genai (Gemini)
#   - ODA File Converter (Linux) + xvfb  (tự chuyển .dwg -> .dxf trên server)
#   - KHÔNG cần AutoCAD (đây là lý do deploy được lên cloud — khác hẳn MCP-điều-khiển-AutoCAD-live)
#
# CHUẨN BỊ TRƯỚC KHI BUILD:
#   Tải "ODA File Converter" bản Linux Qt6 x64 .deb từ https://www.opendesign.com/guestfiles
#   đặt vào:  vendor/ODAFileConverter.deb   (KHÔNG commit công khai — license + dung lượng; dùng repo PRIVATE)
#
# RUNTIME ENV cần đặt trên Render:
#   GEMINI_API_KEY = <khoá Gemini của bạn>     (BẮT BUỘC để bật AI)
# ============================================================================
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    ODA_EXE=/usr/bin/ODAFileConverter \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

# 1) Thư viện hệ thống cho ODA (Qt6) chạy headless dưới màn hình ảo (xvfb).
RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb xauth \
        libgl1 libegl1 libglib2.0-0 libdbus-1-3 \
        libx11-6 libx11-xcb1 libxext6 libxrender1 libsm6 libice6 \
        libxkbcommon0 libxkbcommon-x11-0 \
        libxcb1 libxcb-cursor0 libxcb-glx0 libxcb-icccm4 libxcb-image0 \
        libxcb-keysyms1 libxcb-randr0 libxcb-render0 libxcb-render-util0 \
        libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-util1 \
        libxcb-xfixes0 libxcb-xinerama0 libxcb-xkb1 \
        libfontconfig1 libfreetype6 \
        fontconfig fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# 2) Cài ODA File Converter từ vendor/.
COPY vendor/ODAFileConverter.deb /tmp/oda.deb
RUN apt-get update \
    && apt-get install -y --no-install-recommends /tmp/oda.deb \
    && rm -f /tmp/oda.deb \
    && rm -rf /var/lib/apt/lists/* \
    && if [ ! -e /usr/bin/ODAFileConverter ]; then \
         ln -sf "$(ls /usr/bin/ODAFileConverter* | head -n1)" /usr/bin/ODAFileConverter; \
       fi

# 3) Code Python.
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5050

# 4) Production: gunicorn 1 worker (host giữ 1 phiên MCP + 1 bản vẽ/lượt — đủ demo),
#    nhiều threads cho hỏi-đáp đồng thời, timeout dài vì nạp/convert/render file lớn có thể lâu.
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5050} --workers 1 --threads 4 --timeout 600"]
