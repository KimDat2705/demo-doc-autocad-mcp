#!/usr/bin/env bash
# kb_refreeze.sh — nghi thức ĐỔI KHO KIẾN THỨC (kienthuc.py), theo KE_HOACH_KHO_KIEN_THUC.md.
# Chạy TRỌN bộ kiểm của kho trong 1 lệnh rồi in KB_HASH mới để dán vào tests/test_kienthuc.py.
# (Tách chu kỳ sửa-kho khỏi chu kỳ sửa-prompt: thêm entry KHÔNG cần A/B lại SYSTEM_PROMPT.)
set -u
cd "$(dirname "$0")/../.." || exit 1
PY="${PYTHON:-python}"
fail=0

echo "=== [1/2] Validator + digit-free + grounding-rỗng + tra cứu (tests/test_kienthuc.py, BỎ QUA hash cũ) ==="
# chạy test nhưng chấp nhận hash lệch (đang đổi kho): lọc dòng K2
out=$($PY tests/test_kienthuc.py 2>&1); rc=$?
echo "$out" | grep -v "^  \[FAIL\] K2" | tail -20
that_bai_khac=$(echo "$out" | grep "^  \[FAIL\]" | grep -cv "K2")
[ "$that_bai_khac" -eq 0 ] || { echo "FAIL: kho có vi phạm NGOÀI hash (xem trên) — KHÔNG được freeze"; fail=1; }

echo "=== [2/2] KB_HASH mới (dán vào KB_HASH_DONG_BANG của tests/test_kienthuc.py) ==="
$PY -c "import kienthuc; print('KB_VERSION:', kienthuc.KB_VERSION); print('KB_HASH:', kienthuc.KB_HASH)" || fail=1

echo "------------------------------------"
if [ "$fail" -eq 0 ]; then
  echo "KB REFREEZE: OK — dán hash mới vào test, chạy lại tests/test_kienthuc.py rồi FULL check.sh trước khi commit."
else
  echo "KB REFREEZE: FAIL — sửa vi phạm trước, KHÔNG dán hash."
fi
exit $fail
