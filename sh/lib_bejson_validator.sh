#!/bin/bash
# # Library:     lib_bejson_validator.sh
# MFDB Version: 1.3.1
# Format_Creator: Elton Boehnen
# Status:      OFFICIAL - v1.3.1
# Date:        2026-05-06

#===============================================================================
# Library:     lib_bejson_validator.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.2)
# Author:      Elton Boehnen
# Version:     3.1.0 (OFFICIAL)
# Date:        2026-04-16
# Description: BEJSON validator — schema validation for 104, 104a, 104db.
#              MFDB validation functions are in lib_mfdb_validator.sh (decoupled).
#===============================================================================

set -o pipefail
set -o nounset

# Error codes
[[ -v E_VAL_NOT_JSON ]] || readonly E_VAL_NOT_JSON=1
[[ -v E_VAL_MISSING_KEY ]] || readonly E_VAL_MISSING_KEY=2
[[ -v E_VAL_BAD_FORMAT ]] || readonly E_VAL_BAD_FORMAT=3
[[ -v E_VAL_BAD_VERSION ]] || readonly E_VAL_BAD_VERSION=4
[[ -v E_VAL_BAD_CREATOR ]] || readonly E_VAL_BAD_CREATOR=5
[[ -v E_VAL_SCHEMA_MISMATCH ]] || readonly E_VAL_SCHEMA_MISMATCH=6
[[ -v E_VAL_INVALID_TYPE ]] || readonly E_VAL_INVALID_TYPE=7

#-------------------------------------------------------------------------------
# CORE VALIDATION
#-------------------------------------------------------------------------------

bejson_validator_check_dependencies() {
    if ! command -v jq >/dev/null 2>&1; then
        echo "ERROR: jq is required for BEJSON validation" >&2
        return 1
    fi
    local jq_ver=$(jq --version | sed 's/jq-//')
    # Simple check for jq >= 1.6
    if [[ "${jq_ver%%.*}" -lt 1 ]] || { [[ "${jq_ver%%.*}" -eq 1 ]] && [[ "${jq_ver#*.}" -lt 6 ]]; }; then
        echo "ERROR: jq >= 1.6 is required. Found: $jq_ver" >&2
        return 1
    fi
    return 0
}

bejson_validator_validate_file() {
    local file_path="$1"
    if [[ ! -f "$file_path" ]]; then
        echo "ERROR: File not found: $file_path" >&2
        return 1
    fi
    
    # 1. Basic JSON check
    if ! jq . "$file_path" >/dev/null 2>&1; then
        return $E_VAL_NOT_JSON
    fi

    # 2. Mandatory Keys check
    local keys=$(jq -r 'keys | join(",")' "$file_path")
    for k in Format Format_Version Format_Creator Records_Type Fields Values; do
        if [[ ! "$keys" =~ "$k" ]]; then
            return $E_VAL_MISSING_KEY
        fi
    done

    # 3. Format & Creator check
    local fmt=$(jq -r '.Format' "$file_path")
    local creator=$(jq -r '.Format_Creator' "$file_path")
    [[ "$fmt" != "BEJSON" ]] && return $E_VAL_BAD_FORMAT
    [[ "$creator" != "Elton Boehnen" ]] && return $E_VAL_BAD_CREATOR

    # 4. Records Length check
    local field_count=$(jq '.Fields | length' "$file_path")
    local bad_records=$(jq --argjson fc "$field_count" '.Values | map(select(length != $fc)) | length' "$file_path")
    if [[ "$bad_records" -gt 0 ]]; then
        return $E_VAL_SCHEMA_MISMATCH
    fi

    return 0
}

# Export functions
export -f bejson_validator_check_dependencies
export -f bejson_validator_validate_file
