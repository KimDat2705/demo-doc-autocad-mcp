#!/usr/bin/env bash
# Cong chat luong demo 2 (MCP) — chuan Harness. Chay tu thu muc demo_mcp_autocad/.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY="${PYTHON:-python}"
export READFILE_MAX_MB="${READFILE_MAX_MB:-300}"
fail=0

echo "=== [1/8] Import tools_core sach + dem MCP tool ==="
$PY -c "import tools_core; print('OK import tools_core')" || fail=1
n=$(grep -c "@mcp.tool" mcp_server.py 2>/dev/null || echo 0)
echo "MCP tools khai bao: $n (mong >=20)"
[ "$n" -ge 20 ] || { echo "FAIL: thieu MCP tool"; fail=1; }

echo "=== [2/8] Khong hardcode API key ==="
if grep -nE "AIza[0-9A-Za-z_-]{10,}" tools_core.py app.py mcp_bridge.py mcp_server.py 2>/dev/null; then
  echo "FAIL: tim thay API key trong source"; fail=1
else
  echo "OK: khong co key trong source"
fi

echo "=== [3/8] Test CHONG BIA takeoff (tat dinh, offline, khong ton API) ==="
out=$($PY tests/test_takeoff_chong_bia.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test chong bia co FAIL"; fail=1; }

echo "=== [4/8] Test MODEL FALLBACK 429/503 (robustness H, offline, mock, khong ton API) ==="
out=$($PY tests/test_model_fallback.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test model fallback co FAIL"; fail=1; }

echo "=== [5/8] Test SIZE GUARD chan file lon som (robustness I, offline, khong ton API) ==="
out=$($PY tests/test_size_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test size guard co FAIL"; fail=1; }

echo "=== [6/8] Test FILE TTL don file cu (robustness J, offline, khong ton API) ==="
out=$($PY tests/test_file_ttl.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test file ttl co FAIL"; fail=1; }

echo "=== [7/8] Test SESSION tach state theo phien (robustness K, offline, mock, khong ton API) ==="
out=$($PY tests/test_session.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test session co FAIL"; fail=1; }

echo "=== [8/8] Test HEALTH keep-alive + giam sat (robustness L, offline, khong ton API) ==="
out=$($PY tests/test_health.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test health co FAIL"; fail=1; }

echo "------------------------------------"
if [ "$fail" -eq 0 ]; then echo "HARNESS GATE: PASS"; else echo "HARNESS GATE: FAIL"; fi
exit $fail
