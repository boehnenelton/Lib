#!/bin/bash
#===============================================================================
# Library:     test_bejson_parse.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.1)
# Author:      Elton Boehnen
# Version:     1.1 (OFFICIAL)
# Date:        2026-04-23
# Description: Core-Command library component.
#===============================================================================
#===============================================================================
# Test Suite:  test_bejson_parse.sh
# Target:      lib_bejson_parse.sh
#===============================================================================

LIB_SH_DIR="/storage/7B30-0E0B/Core-Command/Lib/sh"
source "${LIB_SH_DIR}/lib_bejson_parse.sh"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "Running Bash Parser Tests..."

SAMPLE_104='{
  "Format": "BEJSON",
  "Format_Version": "104",
  "Format_Creator": "Elton",
  "Records_Type": ["File"],
  "Fields": [
    {"name": "file1name", "type": "string"},
    {"name": "file1content", "type": "string"}
  ],
  "Values": [
    ["test.txt", "Hello World"]
  ]
}'

# 1. Parse JSON
echo "Testing parse_json..."
res=$(bejson_parse_json "$SAMPLE_104")
if [[ "$(echo "$res" | jq -r '.Format')" == "BEJSON" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Parse failed"
    ((TESTS_FAILED++))
fi

# 2. Save Files
echo "Testing save_files..."
TMP_OUT="/storage/7B30-0E0B/Core-Command/Lib/tests/sh/tmp_parse"
mkdir -p "$TMP_OUT"

# extract data first
bejson_extract_data "$SAMPLE_104"
save_res=$(bejson_save_files "TestProj" "$TMP_OUT" "true")
saved_path=$(echo "$save_res" | jq -r '.path')

if [[ "$(echo "$save_res" | jq -r '.success')" == "true" && -f "${saved_path}/test.txt" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Save files failed"
    echo "SAVE_RES: $save_res"
    ((TESTS_FAILED++))
fi

# Cleanup
rm -rf "$TMP_OUT"

echo "---------------------------------------"
echo "Bash Parser Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
