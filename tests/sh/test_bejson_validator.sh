#!/bin/bash
#===============================================================================
# Library:     test_bejson_validator.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.1)
# Author:      Elton Boehnen
# Version:     1.1 (OFFICIAL)
# Date:        2026-04-23
# Description: Core-Command library component.
#===============================================================================
#===============================================================================
# Test Suite:  test_bejson_validator.sh
# Target:      lib_bejson_validator.sh
#===============================================================================

LIB_SH_DIR="/storage/7B30-0E0B/Core-Command/Lib/sh"
source "${LIB_SH_DIR}/lib_bejson_validator.sh"

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

assert_false() {
    if ! "$@"; then
        ((TESTS_PASSED++))
    else
        echo "FAIL (expected failure): $*"
        ((TESTS_FAILED++))
    fi
}

echo "Running Bash Validator Tests..."

# 1. Dependency Check
echo "Testing dependencies..."
assert_true bejson_validator_check_dependencies

# 2. Syntax Check
echo "Testing JSON syntax..."
assert_true bejson_validator_check_json_syntax '{"a":1}'
assert_false bejson_validator_check_json_syntax '{"a":1'

# 3. Mandatory Keys
echo "Testing mandatory keys..."
valid_json='{"Format":"BEJSON","Format_Version":"104","Format_Creator":"Elton","Records_Type":["T"],"Fields":[],"Values":[]}'
assert_true bejson_validator_check_mandatory_keys "$valid_json"
assert_false bejson_validator_check_mandatory_keys '{"Format":"BEJSON"}'

# 4. Records Type
echo "Testing Records_Type..."
assert_true bejson_validator_check_records_type "$valid_json" "104"
bad_rt='{"Records_Type":[]}'
assert_false bejson_validator_check_records_type "$bad_rt" "104"

# 5. Full Validation
echo "Testing full validation..."
assert_true bejson_validator_validate_string "$valid_json"

# Create a temp file for file validation test
TMP_VAL="/storage/7B30-0E0B/Core-Command/Lib/tests/sh/tmp_test.bejson"
echo "$valid_json" > "$TMP_VAL"
assert_true bejson_validator_validate_file "$TMP_VAL"
rm -f "$TMP_VAL"

# 6. Report
echo "Testing report generation..."
report=$(bejson_validator_get_report "$valid_json")
if [[ "$report" == *"Status: VALID"* ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Report status mismatch"
    ((TESTS_FAILED++))
fi

echo "---------------------------------------"
echo "Bash Validator Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
