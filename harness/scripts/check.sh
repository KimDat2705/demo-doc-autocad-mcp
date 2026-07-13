#!/usr/bin/env bash
# Cong chat luong demo 2 (MCP) — chuan Harness. Chay tu thu muc demo_mcp_autocad/.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY="${PYTHON:-python}"
export READFILE_MAX_MB="${READFILE_MAX_MB:-300}"
fail=0

echo "=== [1/18] Import tools_core sach + dem MCP tool ==="
$PY -c "import tools_core; print('OK import tools_core')" || fail=1
n=$(grep -c "@mcp.tool" mcp_server.py 2>/dev/null || echo 0)
echo "MCP tools khai bao: $n (mong >=20)"
[ "$n" -ge 20 ] || { echo "FAIL: thieu MCP tool"; fail=1; }

echo "=== [2/18] Khong hardcode API key ==="
if grep -nE "AIza[0-9A-Za-z_-]{10,}" tools_core.py app.py mcp_bridge.py mcp_server.py 2>/dev/null; then
  echo "FAIL: tim thay API key trong source"; fail=1
else
  echo "OK: khong co key trong source"
fi

echo "=== [3/18] Test CHONG BIA takeoff (tat dinh, offline, khong ton API) ==="
out=$($PY tests/test_takeoff_chong_bia.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test chong bia co FAIL"; fail=1; }

echo "=== [4/18] Test MODEL FALLBACK 429/503 (robustness H, offline, mock, khong ton API) ==="
out=$($PY tests/test_model_fallback.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test model fallback co FAIL"; fail=1; }

echo "=== [5/18] Test SIZE GUARD chan file lon som (robustness I, offline, khong ton API) ==="
out=$($PY tests/test_size_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test size guard co FAIL"; fail=1; }

echo "=== [6/18] Test FILE TTL don file cu (robustness J, offline, khong ton API) ==="
out=$($PY tests/test_file_ttl.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test file ttl co FAIL"; fail=1; }

echo "=== [7/18] Test SESSION tach state theo phien (robustness K, offline, mock, khong ton API) ==="
out=$($PY tests/test_session.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test session co FAIL"; fail=1; }

echo "=== [8/18] Test HEALTH keep-alive + giam sat (robustness L, offline, khong ton API) ==="
out=$($PY tests/test_health.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test health co FAIL"; fail=1; }

echo "=== [9/18] Test HOC LOG WORM append-only + grep-guard (P2 AI tu hoc, offline, khong ton API) ==="
out=$($PY tests/test_hoc_log.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test hoc log co FAIL"; fail=1; }

echo "=== [10/18] Test HOC QUY UOC — LLM-exclusion + grep-guard hoc_phien (P3 AI tu hoc, offline, khong ton API) ==="
out=$($PY tests/test_hoc_quy_uoc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test hoc quy uoc co FAIL"; fail=1; }

echo "=== [11/18] Test VISUAL-HIGHLIGHT (danh_dau/render PNG, offline, khong ton API) ==="
out=$($PY tests/test_visual_highlight.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test visual highlight co FAIL"; fail=1; }

echo "=== [12/18] Test EXCEL CONTENT (mo lai .xlsx: cot/tong-phu/khoi hoc, offline) ==="
out=$($PY tests/test_excel_content.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test excel content co FAIL"; fail=1; }

echo "=== [13/18] Test MISC TOOLS (dem/tong_so_luong/thep_hinh/block/sheet/layer, offline) ==="
out=$($PY tests/test_misc_tools.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test misc tools co FAIL"; fail=1; }

echo "=== [14/18] Test VNTEXT to_unicode (TCVN3/%%C->O, offline) ==="
out=$($PY tests/test_vntext.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test vntext co FAIL"; fail=1; }

echo "=== [15/18] Test FUZZ INPUT (DXF rac/rong, inputs_bo_sung rac, ma emoji, offline) ==="
out=$($PY tests/test_fuzz_input.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test fuzz input co FAIL"; fail=1; }

echo "=== [16/18] Test DWGCONV (nhanh ODA khong cai, LO loi co nghia, offline) ==="
out=$($PY tests/test_dwgconv.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test dwgconv co FAIL"; fail=1; }

echo "=== [17/18] Test MCP STDIO (spawn mcp_server that + JSON-RPC, wiring hoclog, offline khong ton API) ==="
out=$($PY tests/test_mcp_stdio.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test mcp stdio co FAIL"; fail=1; }

echo "=== [18/18] Test APP ROUTES (/ /config /version /health + upload 400, offline khong ton API) ==="
out=$($PY tests/test_app_routes.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test app routes co FAIL"; fail=1; }

echo "------------------------------------"
if [ "$fail" -eq 0 ]; then echo "HARNESS GATE: PASS"; else echo "HARNESS GATE: FAIL"; fi
exit $fail
