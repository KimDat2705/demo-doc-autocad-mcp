#!/usr/bin/env bash
# Cong chat luong demo 2 (MCP) — chuan Harness. Chay tu thu muc demo_mcp_autocad/.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY="${PYTHON:-python}"
export READFILE_MAX_MB="${READFILE_MAX_MB:-300}"
fail=0

echo "=== [1/48] Import tools_core sach + dem MCP tool ==="
$PY -c "import tools_core; print('OK import tools_core')" || fail=1
n=$(grep -c "@mcp.tool" mcp_server.py 2>/dev/null || echo 0)
echo "MCP tools khai bao: $n (mong >=20)"
[ "$n" -ge 20 ] || { echo "FAIL: thieu MCP tool"; fail=1; }

echo "=== [2/48] Khong hardcode API key ==="
if grep -nE "AIza[0-9A-Za-z_-]{10,}" tools_core.py app.py mcp_bridge.py mcp_server.py 2>/dev/null; then
  echo "FAIL: tim thay API key trong source"; fail=1
else
  echo "OK: khong co key trong source"
fi

echo "=== [3/48] Test CHONG BIA takeoff (tat dinh, offline, khong ton API) ==="
out=$($PY tests/test_takeoff_chong_bia.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test chong bia co FAIL"; fail=1; }

echo "=== [4/48] Test MODEL FALLBACK 429/503 (robustness H, offline, mock, khong ton API) ==="
out=$($PY tests/test_model_fallback.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test model fallback co FAIL"; fail=1; }

echo "=== [5/48] Test SIZE GUARD chan file lon som (robustness I, offline, khong ton API) ==="
out=$($PY tests/test_size_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test size guard co FAIL"; fail=1; }

echo "=== [6/48] Test FILE TTL don file cu (robustness J, offline, khong ton API) ==="
out=$($PY tests/test_file_ttl.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test file ttl co FAIL"; fail=1; }

echo "=== [7/48] Test SESSION tach state theo phien (robustness K, offline, mock, khong ton API) ==="
out=$($PY tests/test_session.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test session co FAIL"; fail=1; }

echo "=== [8/48] Test HEALTH keep-alive + giam sat (robustness L, offline, khong ton API) ==="
out=$($PY tests/test_health.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test health co FAIL"; fail=1; }

echo "=== [9/48] Test HOC LOG WORM append-only + grep-guard (P2 AI tu hoc, offline, khong ton API) ==="
out=$($PY tests/test_hoc_log.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test hoc log co FAIL"; fail=1; }

echo "=== [10/48] Test HOC QUY UOC — LLM-exclusion + grep-guard hoc_phien (P3 AI tu hoc, offline, khong ton API) ==="
out=$($PY tests/test_hoc_quy_uoc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test hoc quy uoc co FAIL"; fail=1; }

echo "=== [11/48] Test VISUAL-HIGHLIGHT (danh_dau/render PNG, offline, khong ton API) ==="
out=$($PY tests/test_visual_highlight.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test visual highlight co FAIL"; fail=1; }

echo "=== [12/48] Test EXCEL CONTENT (mo lai .xlsx: cot/tong-phu/khoi hoc, offline) ==="
out=$($PY tests/test_excel_content.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test excel content co FAIL"; fail=1; }

echo "=== [13/48] Test MISC TOOLS (dem/tong_so_luong/thep_hinh/block/sheet/layer, offline) ==="
out=$($PY tests/test_misc_tools.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test misc tools co FAIL"; fail=1; }

echo "=== [14/48] Test VNTEXT to_unicode (TCVN3/%%C->O, offline) ==="
out=$($PY tests/test_vntext.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test vntext co FAIL"; fail=1; }

echo "=== [15/48] Test FUZZ INPUT (DXF rac/rong, inputs_bo_sung rac, ma emoji, offline) ==="
out=$($PY tests/test_fuzz_input.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test fuzz input co FAIL"; fail=1; }

echo "=== [16/48] Test DWGCONV (nhanh ODA khong cai, LO loi co nghia, offline) ==="
out=$($PY tests/test_dwgconv.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test dwgconv co FAIL"; fail=1; }

echo "=== [17/48] Test MCP STDIO (spawn mcp_server that + JSON-RPC, wiring hoclog, offline khong ton API) ==="
out=$($PY tests/test_mcp_stdio.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test mcp stdio co FAIL"; fail=1; }

echo "=== [18/48] Test APP ROUTES (/ /config /version /health + upload 400, offline khong ton API) ==="
out=$($PY tests/test_app_routes.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test app routes co FAIL"; fail=1; }

echo "=== [19/48] Test GROUNDING-GUARD (id135 chan bia so do-luong khong nguon, mock offline, khong ton API) ==="
out=$($PY tests/test_grounding_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test grounding guard co FAIL"; fail=1; }

echo "=== [20/48] Test CAO DO MIN/MAX (id135-recall: doc cao do thap/cao nhat + handle, offline) ==="
out=$($PY tests/test_cao_do_min_max.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test cao do min/max co FAIL"; fail=1; }

echo "=== [21/48] Test KHAO SAT CORPUS (cong cu soi ban ve doi tac moi: RAM/kich thuoc/bang-TK, offline) ==="
out=$($PY tests/test_khao_sat_corpus.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test khao sat corpus co FAIL"; fail=1; }

echo "=== [22/48] Test OLE CANH BAO (bug C GD4: bang Excel nhung -> LO 'khong doc duoc/DOC DUOC', offline) ==="
out=$($PY tests/test_ole_canh_bao.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test ole canh bao co FAIL"; fail=1; }

echo "=== [23/48] Test OLEEXCEL (U3: doc bang Excel nhung OLE qua binary olefile/xlrd, offline) ==="
out=$($PY tests/test_oleexcel.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test oleexcel co FAIL"; fail=1; }

echo "=== [24/48] Test HANDLE-GUARD (I1: doi chieu handle model trich dan vs tool phat/entitydb, offline) ==="
out=$($PY tests/test_handle_guard.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test handle guard co FAIL"; fail=1; }

echo "=== [25/48] Test I3-B BOUNDS (duong kinh thep tron o DK bang -> LO nghi_ngo, khong lot grounding, offline) ==="
out=$($PY tests/test_i3_bounds.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test i3 bounds co FAIL"; fail=1; }

echo "=== [26/48] Test BANG VE-NET (I4a: detector bang ke-bang-net LINE+TEXT -> LO co, khong lot grounding, offline) ==="
out=$($PY tests/test_bang_ve_net.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test bang ve-net co FAIL"; fail=1; }

echo "=== [27/48] Test PROMPT TAXONOMY (I9: SYSTEM_PROMPT tach manh + version/hash, byte-lock sha256, offline) ==="
out=$($PY tests/test_prompt_taxonomy.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test prompt taxonomy co FAIL"; fail=1; }

echo "=== [28/48] Test DISPATCH GATE (L0 kho kien thuc: chan thi hanh tool host-only/ten la truoc bridge.call, offline) ==="
out=$($PY tests/test_dispatch_gate.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test dispatch gate co FAIL"; fail=1; }

echo "=== [29/48] Test KIENTHUC (L1+L2 kho kien thuc: validator digit-free + byte-lock KB_HASH + strip _kb chong lot ro, offline) ==="
out=$($PY tests/test_kienthuc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test kienthuc co FAIL"; fail=1; }

echo "=== [30/48] Test KB GRAFT (L4 kho kien thuc: gate bang-chung-duong + confirm-only + khong lot grounding + degrade-safe, offline) ==="
out=$($PY tests/test_kb_graft.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test kb graft co FAIL"; fail=1; }

echo "=== [31/48] Test KB XAC NHAN (L5 kho kien thuc: confirm-only fail-closed + host-only 2 hang rao + endpoint /xac-nhan + frontend hook, offline) ==="
out=$($PY tests/test_kb_xacnhan.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test kb xac nhan co FAIL"; fail=1; }

echo "=== [32/48] Test TRA KY HIEU (L3 kho kien thuc: tra kho read-only fail-open + nhom de-nham + khong lot grounding + R18, offline) ==="
out=$($PY tests/test_tra_ky_hieu.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test tra ky hieu co FAIL"; fail=1; }

echo "=== [33/48] Test GARBLE DIA (L6: fold i-hoi + /g -> Ø co gong, 0 phan-khop, 0 doi so, canonical search, offline) ==="
out=$($PY tests/test_garble_dia.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test garble dia co FAIL"; fail=1; }

echo "=== [34/48] Test ADMISSION (gate SO BAN VE: 503 lich su, khong vuot tran, khong ri suat, fail-closed, offline) ==="
out=$($PY tests/test_admission.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test admission co FAIL"; fail=1; }

echo "=== [35/48] Test BRIDGE CLOSE (close(cho_giay) xac nhan chet + call sau close khong treo + khong mo coi) ==="
out=$($PY tests/test_bridge_close.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test bridge close co FAIL"; fail=1; }

echo "=== [36/48] Test TY LE DO (DIMLFAC: ap he so ban ve tu khai, fail-open, co BOOL + prose sach so, offline) ==="
out=$($PY tests/test_ty_le_do.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test ty le do co FAIL"; fail=1; }

echo "=== [37/48] Test SO DO DIM (nguon so do: uu tien code42 AutoCAD tu luu + loai duong do GOC, offline) ==="
out=$($PY tests/test_so_do_dim.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test so do dim co FAIL"; fail=1; }

echo "=== [38/48] Test NEO GROUNDING (ma hieu khong sinh neo AM + ten file khong lam bang chung, offline) ==="
out=$($PY tests/test_neo_grounding.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test neo grounding co FAIL"; fail=1; }

echo "=== [39/48] Test CHU IN KICH THUOC (LO cho chu in khac so may do; co BOOL + prose sach so, offline) ==="
out=$($PY tests/test_chu_in_kich_thuoc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test chu in kich thuoc co FAIL"; fail=1; }

echo "=== [40/48] Test VUNG CHUA DOC (co chu trong khoi DUOC CHEN; cong kep, khong khop raw, offline) ==="
out=$($PY tests/test_vung_chua_doc.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test vung chua doc co FAIL"; fail=1; }

echo "=== [41/48] Test CHU TRONG KY HIEU (tool doc khoi duoc chen; khong truong dem, ngan sach ro neo) ==="
out=$($PY tests/test_chu_trong_ky_hieu.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test chu trong ky hieu co FAIL"; fail=1; }

echo "=== [42/48] Test BATTERY RUNNER + DO ON DINH (1.06: khong ghi de, do on dinh N-luot, offline) ==="
out=$($PY tests/test_battery_runner.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test battery runner co FAIL"; fail=1; }

echo "=== [43/48] Test MA DINH DANG (A3: ten phong/ma mau/%%C khong lam moi khop ao, offline) ==="
out=$($PY tests/test_ma_dinh_dang.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test ma dinh dang co FAIL"; fail=1; }

echo "=== [44/48] Test C1 PHI NO_GO (khoa BAT BIEN: cau tong-hop mang PHI khong bi guard giet, offline) ==="
out=$($PY tests/test_c1_phi_no_go.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test c1 phi no_go co FAIL"; fail=1; }

echo "=== [45/48] Test TRANG IN (E2b: tool #35 doc chu trang in; KHONG bom ro neo, offline) ==="
out=$($PY tests/test_trang_in.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test trang in co FAIL"; fail=1; }

echo "=== [46/48] Test NEO RONG TU CHOI (A2: ro neo rong vi CHINH SACH -> cau trung thuc, offline) ==="
out=$($PY tests/test_neo_rong_tu_choi.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test neo rong tu choi co FAIL"; fail=1; }

echo "=== [47/48] Test A3 TRICH TRANG IN (cuu cau DUNG trich nguyen van; all + gop-rieng, offline) ==="
out=$($PY tests/test_a3_trich_trang_in.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test a3 trich trang in co FAIL"; fail=1; }

echo "=== [48/48] Test VNI (bang ma VNI-Windows + cong nhan dien CAU TRUC, offline) ==="
out=$($PY tests/test_vni.py 2>&1); rc=$?
echo "$out" | tail -1
[ "$rc" -eq 0 ] || { echo "FAIL: test vni co FAIL"; fail=1; }

echo "------------------------------------"
if [ "$fail" -eq 0 ]; then echo "HARNESS GATE: PASS"; else echo "HARNESS GATE: FAIL"; fi
exit $fail
