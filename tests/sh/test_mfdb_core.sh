#!/bin/bash
#===============================================================================
# Library:     test_mfdb_core.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.1)
# Author:      Elton Boehnen
# Version:     1.1 (OFFICIAL)
# Date:        2026-04-23
# Description: Core-Command library component.
#===============================================================================
#===============================================================================
# Test Suite:  test_mfdb_core.sh
# Target:      lib_mfdb_core.sh
#===============================================================================

LIB_SH_DIR="/storage/7B30-0E0B/Core-Command/Lib/sh"
source "${LIB_SH_DIR}/lib_mfdb_core.sh"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "Running Bash MFDB Core Tests..."

TMP_DB="/storage/7B30-0E0B/Core-Command/Lib/tests/sh/tmp_mfdb"
mkdir -p "$TMP_DB"
MANIFEST="${TMP_DB}/104a.mfdb.bejson"

# 1. Create a dummy manifest manually
echo "Creating dummy manifest..."
cat <<EOF > "$MANIFEST"
{
  "Format": "BEJSON",
  "Format_Version": "104a",
  "Format_Creator": "Elton",
  "Records_Type": ["mfdb"],
  "Fields": [
    {"name": "entity_name", "type": "string"},
    {"name": "file_path", "type": "string"},
    {"name": "record_count", "type": "integer"}
  ],
  "Values": [
    ["User", "data/user.bejson", 0]
  ]
}
EOF

mkdir -p "${TMP_DB}/data"
cat <<EOF > "${TMP_DB}/data/user.bejson"
{
  "Format": "BEJSON",
  "Format_Version": "104",
  "Format_Creator": "Elton",
  "Parent_Hierarchy": "../104a.mfdb.bejson",
  "Records_Type": ["User"],
  "Fields": [{"name": "id", "type": "string"}],
  "Values": []
}
EOF

# 2. Discovery
echo "Testing discovery..."
res=$(mfdb_core_discover "$MANIFEST")
if [[ "$res" == "manifest" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Discovery manifest mismatch: $res"
    ((TESTS_FAILED++))
fi

res=$(mfdb_core_discover "${TMP_DB}/data/user.bejson")
if [[ "$res" == "entity" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Discovery entity mismatch: $res"
    ((TESTS_FAILED++))
fi

# 3. Sync
echo "Testing sync..."
# Add a record manually to entity
cat <<EOF > "${TMP_DB}/data/user.bejson"
{
  "Format": "BEJSON",
  "Format_Version": "104",
  "Format_Creator": "Elton",
  "Parent_Hierarchy": "../104a.mfdb.bejson",
  "Records_Type": ["User"],
  "Fields": [{"name": "id", "type": "string"}],
  "Values": [["u1"]]
}
EOF

# capture output but we check manifest file
mfdb_core_sync_manifest_count "$MANIFEST" "User" > /dev/null
count=$(jq -r '.Values[0][2]' "$MANIFEST")
if [[ "$count" -eq 1 ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Sync record count mismatch: $count"
    ((TESTS_FAILED++))
fi

# Cleanup
rm -rf "$TMP_DB"

echo "---------------------------------------"
echo "Bash MFDB Core Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
