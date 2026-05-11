#!/bin/bash
#===============================================================================
# Library:     test_mfdb_validator.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.5)
# Author:      Elton Boehnen
# Version:     1.5 OFFICIAL
# Date:        2026-05-01
# Description: Core-Command library component.
#===============================================================================
#===============================================================================
# Test Suite:  test_mfdb_validator.sh
# Target:      lib_mfdb_validator.sh
#===============================================================================

LIB_SH_DIR="/storage/7B30-0E0B/Core-Command/Lib/sh"
source "${LIB_SH_DIR}/lib_mfdb_validator.sh"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "Running Bash MFDB Validator Tests..."

TMP_DB="/storage/7B30-0E0B/Core-Command/Lib/tests/sh/tmp_mfdb_val"
mkdir -p "$TMP_DB"
MANIFEST="${TMP_DB}/104a.mfdb.bejson"

# Create dummy manifest
cat <<EOF > "$MANIFEST"
{
  "Format": "BEJSON",
  "Format_Version": "104a",
  "Format_Creator": "Elton",
  "Records_Type": ["mfdb"],
  "Fields": [
    {"name": "entity_name", "type": "string"},
    {"name": "file_path", "type": "string"}
  ],
  "Values": [
    ["User", "data/user.bejson"]
  ]
}
EOF

# 1. Manifest Validation
echo "Testing manifest validation..."
if mfdb_validator_validate_manifest "$MANIFEST"; then
    ((TESTS_PASSED++))
else
    echo "FAIL: Manifest validation failed"
    mfdb_validator_get_errors
    ((TESTS_FAILED++))
fi

# Cleanup
rm -rf "$TMP_DB"

echo "---------------------------------------"
echo "Bash MFDB Validator Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
