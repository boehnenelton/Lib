#!/bin/bash
#===============================================================================
# Library:     test_be_core.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.1)
# Author:      Elton Boehnen
# Version:     1.1 (OFFICIAL)
# Date:        2026-04-23
# Description: Core-Command library component.
#===============================================================================
#===============================================================================
# Test Suite:  test_be_core.sh
# Target:      lib_be_core.sh
#===============================================================================

LIB_SH_DIR="/storage/7B30-0E0B/Core-Command/Lib/sh"
# Set BEC_ROOT before sourcing
export TEST_ROOT=$(mktemp -d)
export BEC_ROOT="$TEST_ROOT"

source "${LIB_SH_DIR}/lib_be_core.sh"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "Running Bash Core System Tests..."

# 1. Root Resolution
echo "Testing get_root..."
res=$(bec_core_get_root)
if [[ "$res" == "$TEST_ROOT" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Root mismatch: $res"
    ((TESTS_FAILED++))
fi

# 2. State Management
echo "Testing state management..."
bec_core_save_state "test" "key" "value"
val=$(bec_core_load_state "test" "key")
if [[ "$val" == "value" ]]; then
    ((TESTS_PASSED++))
else
    echo "FAIL: State mismatch: $val"
    ((TESTS_FAILED++))
fi

# Cleanup
rm -rf "$TEST_ROOT"
unset BEC_ROOT

echo "---------------------------------------"
echo "Bash Core System Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
