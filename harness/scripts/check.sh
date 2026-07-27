#!/usr/bin/env bash
# Cong chat luong demo 2 (MCP) — chuan Harness. Chay tu thu muc demo_mcp_autocad/.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY="${PYTHON:-python}"
export READFILE_MAX_MB="${READFILE_MAX_MB:-300}"
fail=0

echo "=== [1/22] Import tools_core sach + dem MCP tool ==="
$PY -c "import tools_core; print('OK import tools_core')" || fail=1
n=$(grep -c "@mcp.tool" mcp_server.py 2>/dev/null || echo 0)
echo "MCP tools khai bao: $n (mong >=20)"
[ "$n" -ge 20 ] || { echo "FAIL: thieu MCP tool"; fail=1; }

echo "=== [2/22] Khong hardcode API key ==="
if grep -nE "AIza[0-9A-Za-z_-]{10,}" tools_core.py app.py mcp_bridge.py mcp_server.py 2>/dev/null; then
  echo "FAIL: tim thay API key trong source"; fail=1
else
  echo "OK: khong co key trong source"
fi

echo "=== [3/23] Test CHONG BIA takeoff (tat dinh, offline, khong ton API) ==="
out=$($PY tests/test_takeoff_chong_bia.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test chong bia co FAIL"; fail=1; }

echo "=== [4/23] Test MODEL FALLBACK 429/503 (robustness H, offline, mock, khong ton API) ==="
out=$($PY tests/test_model_fallback.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test model fallback co FAIL"; fail=1; }

echo "=== [5/23] Test SIZE GUARD chan file lon som (robustness I, offline, khong ton API) ==="
out=$($PY tests/test_size_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test size guard co FAIL"; fail=1; }

echo "=== [6/23] Test FILE TTL don file cu (robustness J, offline, khong ton API) ==="
out=$($PY tests/test_file_ttl.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test file ttl co FAIL"; fail=1; }

echo "=== [7/23] Test SESSION tach state theo phien (robustness K, offline, mock, khong ton API) ==="
out=$($PY tests/test_session.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test session co FAIL"; fail=1; }

echo "=== [8/23] Test HEALTH keep-alive + giam sat (robustness L, offline, khong ton API) ==="
out=$($PY tests/test_health.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test health co FAIL"; fail=1; }

echo "=== [9/23] Test HOC LOG WORM append-only + grep-guard (P2 AI tu hoc, offline, khong ton API) ==="
out=$($PY tests/test_hoc_log.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test hoc log co FAIL"; fail=1; }

echo "=== [10/23] Test HOC QUY UOC — LLM-exclusion + grep-guard hoc_phien (P3 AI tu hoc, offline, khong ton API) ==="
out=$($PY tests/test_hoc_quy_uoc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test hoc quy uoc co FAIL"; fail=1; }

echo "=== [11/23] Test VISUAL-HIGHLIGHT (danh_dau/render PNG, offline, khong ton API) ==="
out=$($PY tests/test_visual_highlight.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test visual highlight co FAIL"; fail=1; }

echo "=== [12/23] Test EXCEL CONTENT (mo lai .xlsx: cot/tong-phu/khoi hoc, offline) ==="
out=$($PY tests/test_excel_content.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test excel content co FAIL"; fail=1; }

echo "=== [13/23] Test MISC TOOLS (dem/tong_so_luong/thep_hinh/block/sheet/layer, offline) ==="
out=$($PY tests/test_misc_tools.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test misc tools co FAIL"; fail=1; }

echo "=== [14/23] Test VNTEXT to_unicode (TCVN3/%%C->O, offline) ==="
out=$($PY tests/test_vntext.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test vntext co FAIL"; fail=1; }

echo "=== [15/23] Test FUZZ INPUT (DXF rac/rong, inputs_bo_sung rac, ma emoji, offline) ==="
out=$($PY tests/test_fuzz_input.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test fuzz input co FAIL"; fail=1; }

echo "=== [16/23] Test DWGCONV (nhanh ODA khong cai, LO loi co nghia, offline) ==="
out=$($PY tests/test_dwgconv.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test dwgconv co FAIL"; fail=1; }

echo "=== [17/23] Test MCP STDIO (spawn mcp_server that + JSON-RPC, wiring hoclog, offline khong ton API) ==="
out=$($PY tests/test_mcp_stdio.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test mcp stdio co FAIL"; fail=1; }

echo "=== [18/23] Test APP ROUTES (/ /config /version /health + upload 400, offline khong ton API) ==="
out=$($PY tests/test_app_routes.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test app routes co FAIL"; fail=1; }

echo "=== [19/23] Test GROUNDING-GUARD (id135 chan bia so do-luong khong nguon, mock offline, khong ton API) ==="
out=$($PY tests/test_grounding_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test grounding guard co FAIL"; fail=1; }

echo "=== [20/23] Test CAO DO MIN/MAX (id135-recall: doc cao do thap/cao nhat + handle, offline) ==="
out=$($PY tests/test_cao_do_min_max.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test cao do min/max co FAIL"; fail=1; }

echo "=== [21/23] Test KHAO SAT CORPUS (cong cu soi ban ve doi tac moi: RAM/kich thuoc/bang-TK, offline) ==="
out=$($PY tests/test_khao_sat_corpus.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test khao sat corpus co FAIL"; fail=1; }

echo "=== [22/23] Test OLE CANH BAO (bug C GD4: bang Excel nhung -> LO 'khong doc duoc/DOC DUOC', offline) ==="
out=$($PY tests/test_ole_canh_bao.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test ole canh bao co FAIL"; fail=1; }

echo "=== [23/24] Test OLEEXCEL (U3: doc bang Excel nhung OLE qua binary olefile/xlrd, offline) ==="
out=$($PY tests/test_oleexcel.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test oleexcel co FAIL"; fail=1; }

echo "=== [24/25] Test HANDLE-GUARD (I1: doi chieu handle model trich dan vs tool phat/entitydb, offline) ==="
out=$($PY tests/test_handle_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test handle guard co FAIL"; fail=1; }

echo "=== [25/26] Test I3-B BOUNDS (duong kinh thep tron o DK bang -> LO nghi_ngo, khong lot grounding, offline) ==="
out=$($PY tests/test_i3_bounds.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test i3 bounds co FAIL"; fail=1; }

echo "=== [26/27] Test BANG VE-NET (I4a: detector bang ke-bang-net LINE+TEXT -> LO co, khong lot grounding, offline) ==="
out=$($PY tests/test_bang_ve_net.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test bang ve-net co FAIL"; fail=1; }

echo "=== [27/28] Test PROMPT TAXONOMY (I9: SYSTEM_PROMPT tach manh + version/hash, byte-lock sha256, offline) ==="
out=$($PY tests/test_prompt_taxonomy.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test prompt taxonomy co FAIL"; fail=1; }

echo "=== [28/29] Test DISPATCH GATE (L0 kho kien thuc: chan thi hanh tool host-only/ten la truoc bridge.call, offline) ==="
out=$($PY tests/test_dispatch_gate.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test dispatch gate co FAIL"; fail=1; }

echo "=== [29/30] Test KIENTHUC (L1+L2 kho kien thuc: validator digit-free + byte-lock KB_HASH + strip _kb chong lot ro, offline) ==="
out=$($PY tests/test_kienthuc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test kienthuc co FAIL"; fail=1; }

echo "=== [30/31] Test KB GRAFT (L4 kho kien thuc: gate bang-chung-duong + confirm-only + khong lot grounding + degrade-safe, offline) ==="
out=$($PY tests/test_kb_graft.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test kb graft co FAIL"; fail=1; }

echo "=== [31/32] Test KB XAC NHAN (L5 kho kien thuc: confirm-only fail-closed + host-only 2 hang rao + endpoint /xac-nhan + frontend hook, offline) ==="
out=$($PY tests/test_kb_xacnhan.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test kb xac nhan co FAIL"; fail=1; }

echo "=== [32/33] Test TRA KY HIEU (L3 kho kien thuc: tra kho read-only fail-open + nhom de-nham + khong lot grounding + R18, offline) ==="
out=$($PY tests/test_tra_ky_hieu.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test tra ky hieu co FAIL"; fail=1; }

echo "=== [33/33] Test GARBLE DIA (L6: fold i-hoi + /g -> Ø co gong, 0 phan-khop, 0 doi so, canonical search, offline) ==="
out=$($PY tests/test_garble_dia.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test garble dia co FAIL"; fail=1; }

echo "------------------------------------"
if [ "$fail" -eq 0 ]; then echo "HARNESS GATE: PASS"; else echo "HARNESS GATE: FAIL"; fi
exit $fail
