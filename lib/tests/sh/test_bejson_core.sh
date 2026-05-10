#!/bin/bash
#===============================================================================
# Library:     test_bejson_core.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.5)
# Author:      Elton Boehnen
# Version:     1.5 OFFICIAL
# Date:        2026-05-01
# Description: Core-Command library component.
#===============================================================================
#===============================================================================
# Test Suite:  test_bejson_core.sh
# Target:      lib_bejson_core.sh
#===============================================================================

LIB_SH_DIR="/storage/7B30-0E0B/Core-Command/Lib/sh"
source "${LIB_SH_DIR}/lib_bejson_core.sh"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

assert_true() {
    if "$@"; then
        ((TESTS_PASSED++))
    else
        echo "FAIL: $*"
        ((TESTS_FAILED++))
    fi
}

echo "Running Bash Core Tests..."

# 1. Document Creation
echo "Testing creation..."
doc=$(bejson_core_create_104 "Test" '[{"name":"f1","type":"string"}]' '[["v1"]]')
if [[ "$(echo "$doc" | jq -r '.Format_Version')" == "104" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Creation version mismatch"
    ((TESTS_FAILED++))
fi

# 2. File I/O & Atomic Write
echo "Testing atomic write..."
TMP_DIR="/storage/7B30-0E0B/Core-Command/Lib/tests/sh/tmp_core"
mkdir -p "$TMP_DIR"
TEST_FILE="${TMP_DIR}/test.bejson"

assert_true bejson_core_atomic_write "$TEST_FILE" "$doc"

# 3. Backup & Restore
echo "Testing backup/restore..."
# Create explicit backup
backup_path=$(__bejson_core_atomic_backup "$TEST_FILE")
if [[ -f "$backup_path" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Backup file not created"
    ((TESTS_FAILED++))
fi

# Corrupt main file and restore
echo "corrupt" > "$TEST_FILE"
assert_true __bejson_core_restore_backup "$TEST_FILE" "$backup_path"

# Robust structural comparison using jq
actual_content=$(cat "$TEST_FILE")
if jq --argjson expected "$doc" --argjson actual "$actual_content" -n '$expected == $actual' &>/dev/null; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Restore content mismatch"
    ((TESTS_FAILED++))
fi

# 4. Accessors
echo "Testing accessors..."
v=$(bejson_core_get_version "$doc")
if [[ "$v" == "104" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Version accessor mismatch"
    ((TESTS_FAILED++))
fi

rc=$(bejson_core_get_record_count "$doc")
if [[ "$rc" -eq 1 ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Record count mismatch"
    ((TESTS_FAILED++))
fi

# Cleanup
rm -rf "$TMP_DIR"

echo "---------------------------------------"
echo "Bash Core Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
