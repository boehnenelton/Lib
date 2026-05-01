#!/bin/bash
#===============================================================================
# Library:     bejson.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.1)
# Author:      Elton Boehnen
# Version:     1.1 (OFFICIAL)
# Date:        2026-04-23
# Description: Bash wrapper for all BEJSON tools.
Sources the BEJSON core library and provides a unified CLI.
Author:     Elton Boehnen / Gemini CLI
Version:    1.0.0
Usage:
source bejson.sh
bejson_validate file.bejson.json
bejson_info file.bejson.json -v
bejson_query file.bejson.json status "active"
bejson_create_104 MyType '[{"name":"id","type":"string"},{"name":"val","type":"integer"}]'
bejson_export file.bejson.json output.json
bejson_import data.json output.bejson.json
#===============================================================================
# Tool:       bejson.sh
# Description: Bash wrapper for all BEJSON tools.
#              Sources the BEJSON core library and provides a unified CLI.
#
# Usage:
#   source bejson.sh
#   bejson_validate file.bejson.json
#   bejson_info file.bejson.json -v
#   bejson_query file.bejson.json status "active"
#   bejson_create_104 MyType '[{"name":"id","type":"string"},{"name":"val","type":"integer"}]'
#   bejson_export file.bejson.json output.json
#   bejson_import data.json output.bejson.json

set -o pipefail
set -o nounset

# Source BEJSON core library
BEJSON_TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$BEJSON_TOOLS_DIR/lib_bejson_core.sh" ]]; then
    source "$BEJSON_TOOLS_DIR/lib_bejson_core.sh"
else
    echo "ERROR: lib_bejson_core.sh not found in $BEJSON_TOOLS_DIR" >&2
    return 1 2>/dev/null || exit 1
fi

# Color codes
BEJSON_GREEN='\033[0;32m'
BEJSON_YELLOW='\033[0;33m'
BEJSON_BLUE='\033[0;34m'
BEJSON_CYAN='\033[0;36m'
BEJSON_BOLD='\033[1m'
BEJSON_RESET='\033[0m'

bejson_ok()   { echo -e "${BEJSON_GREEN}✓ $1${BEJSON_RESET}"; }
bejson_warn() { echo -e "${BEJSON_YELLOW}⚠ $1${BEJSON_RESET}"; }
bejson_err()  { echo -e "${BEJSON_RED}✗ $1${BEJSON_RESET}" >&2; }
bejson_info() { echo -e "${BEJSON_CYAN}ℹ $1${BEJSON_RESET}"; }

# ─── Validate ──────────────────────────────────────────────────────────────

bejson_validate() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi

    if bejson_validator_validate_file "$file" 2>/dev/null; then
        bejson_ok "VALID: $file"
        return 0
    else
        bejson_err "INVALID: $file"
        local report
        report=$(bejson_validator_get_report "$file" 2>/dev/null)
        echo "$report"
        return 1
    fi
}

# ─── Info ──────────────────────────────────────────────────────────────────

bejson_info() {
    local file="$1"
    local verbose="${2:-}"

    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi

    local doc
    doc=$(cat "$file")

    local version field_count record_count records_types
    version=$(echo "$doc" | jq -r '.Format_Version')
    field_count=$(echo "$doc" | jq '.Fields | length')
    record_count=$(echo "$doc" | jq '.Values | length')
    records_types=$(echo "$doc" | jq -r '.Records_Type | join(", ")')

    echo -e "\n${BEJSON_BOLD}${BEJSON_BLUE}═══════════════════════════════════════════${BEJSON_RESET}"
    echo -e "${BEJSON_BOLD}  BEJSON File Info${BEJSON_RESET}"
    echo -e "${BEJSON_BOLD}${BEJSON_BLUE}═══════════════════════════════════════════${BEJSON_RESET}\n"
    echo -e "  Version:       ${BEJSON_BOLD}${version}${BEJSON_RESET}"
    echo -e "  Record Types:  ${BEJSON_BOLD}${records_types}${BEJSON_RESET}"
    echo -e "  Fields:        ${BEJSON_BOLD}${field_count}${BEJSON_RESET}"
    echo -e "  Records:       ${BEJSON_BOLD}${record_count}${BEJSON_RESET}"

    if [[ "$verbose" == "-v" || "$verbose" == "--verbose" ]]; then
        echo -e "\n${BEJSON_BOLD}Fields:${BEJSON_RESET}"
        echo "$doc" | jq -r '.Fields | to_entries[] | "  \(.key). \(.value.name) (\(.value.type))\(.value.Record_Type_Parent // "" | if . != "" then " (" + . + ")" else "" end)"'
    fi
}

# ─── Query ─────────────────────────────────────────────────────────────────

bejson_query() {
    local file="$1"
    local field="$2"
    local value="$3"
    local entity="${4:-}"

    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi

    local doc
    doc=$(cat "$file")

    local version
    version=$(echo "$doc" | jq -r '.Format_Version')

    local results

    if [[ -n "$entity" && "$version" == "104db" ]]; then
        # Filter by entity first
        results=$(echo "$doc" | jq --arg ent "$entity" '
            [.Values[] | select(.[0] == $ent)] |
            . as $records |
            (.Fields | to_entries | map(select(.value.name == "'"$field"'")) | .[0].key) as $idx |
            [.[] | select(.[$idx] == (
                try ('"$(echo "$value" | jq '.' 2>/dev/null || echo "\"$value\"")"' // '"\"$value\""'
            ))]
        ')
    else
        results=$(echo "$doc" | jq '
            (.Fields | to_entries | map(select(.value.name == "'"$field"'")) | .[0].key) as $idx |
            [.Values[] | select(.[$idx] == (
                try ('"$(echo "$value" | jq '.' 2>/dev/null || echo "\"$value\"")"' // '"\"$value\""'
            ))]
        ')
    fi

    local count
    count=$(echo "$results" | jq 'length')

    if [[ "$count" -eq 0 ]]; then
        bejson_warn "No results found"
        return 0
    fi

    echo -e "\n${BEJSON_BOLD}${BEJSON_BLUE}═══════════════════════════════════════════${BEJSON_RESET}"
    echo -e "${BEJSON_BOLD}  Query Results ($count records)${BEJSON_RESET}"
    echo -e "${BEJSON_BOLD}${BEJSON_BLUE}═══════════════════════════════════════════${BEJSON_RESET}\n"

    local fnames
    fnames=$(echo "$doc" | jq -r '.Fields[].name')

    echo "$results" | jq -c '.[]' | while IFS= read -r rec; do
        local idx=0
        echo "$fnames" | while IFS= read -r fname; do
            local val
            val=$(echo "$rec" | jq -r ".[$idx] // empty")
            if [[ -n "$val" && "$val" != "null" ]]; then
                echo -e "  ${BEJSON_GREEN}${fname}${BEJSON_RESET}: ${val}"
            fi
            idx=$((idx + 1))
        done
        echo
    done
}

# ─── Export to plain JSON ─────────────────────────────────────────────────

bejson_export() {
    local file="$1"
    local output="${2:-${file%.bejson.json}.json}"

    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi

    jq '[.Values as $vals | .Fields | map(.name) as $names |
         $vals[] | . as $row |
         [range($names | length)] | map({($names[.]): $row[.]}) | add
    ]' "$file" > "$output"

    local count
    count=$(jq 'length' "$output")
    bejson_ok "Exported $count records → $output"
}

# ─── Import JSON array to BEJSON ──────────────────────────────────────────

bejson_import() {
    local file="$1"
    local output="${2:-${file%.json}.bejson.json}"
    local record_type="${3:-Imported}"

    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi

    # Auto-generate fields from first object
    local fields
    fields=$(jq '[to_entries[0].value | to_entries[] | {
        name: .key,
        type: (
            if (.value | type) == "boolean" then "boolean"
            elif (.value | type) == "number" then
                if (.value | floor) == .value then "integer" else "number" end
            elif (.value | type) == "array" then "array"
            elif (.value | type) == "object" then "object"
            else "string"
            end
        )
    }]' "$file" | head -1)

    # Build values
    local values
    values=$(jq '[.[] | [to_entries[] | .value]]' "$file")

    # Create BEJSON 104 document
    local doc
    doc=$(jq -n \
        --arg rt "$record_type" \
        --argjson fields "$fields" \
        --argjson values "$values" \
        '{
            "Format": "BEJSON",
            "Format_Version": "104",
            "Format_Creator": "Elton Boehnen",
            "Records_Type": [$rt],
            "Fields": $fields,
            "Values": $values
        }')

    # Validate and write
    echo "$doc" | jq '.' > "$output"
    if bejson_validator_validate_file "$output" 2>/dev/null; then
        local count
        count=$(echo "$doc" | jq '.Values | length')
        bejson_ok "Imported $count records → $output"
    else
        bejson_err "Validation failed after import"
        rm -f "$output"
        return 1
    fi
}

# ─── Create BEJSON 104 ────────────────────────────────────────────────────

bejson_create_104() {
    local records_type="$1"
    local fields_json="$2"
    local output="${3:-output.bejson.json}"

    local doc
    doc=$(bejson_core_create_104 "$records_type" "$fields_json" "[]")

    echo "$doc" | jq '.' > "$output"
    if bejson_validator_validate_file "$output" 2>/dev/null; then
        bejson_ok "Created 104 BEJSON: $output"
    else
        bejson_err "Validation failed"
        rm -f "$output"
        return 1
    fi
}

# ─── Sort by field ─────────────────────────────────────────────────────────

bejson_sort() {
    local file="$1"
    local field="$2"
    local desc="${3:-false}"

    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi

    local idx
    idx=$(jq --arg f "$field" '.Fields | to_entries[] | select(.value.name == $f) | .key' "$file")

    if [[ -z "$idx" ]]; then
        bejson_err "Field not found: $field"
        return 1
    fi

    local sorted
    if [[ "$desc" == "true" || "$desc" == "-d" ]]; then
        sorted=$(jq ".Values |= sort_by(.[${idx}]) | .Values |= reverse" "$file")
    else
        sorted=$(jq ".Values |= sort_by(.[${idx}])" "$file")
    fi

    echo "$sorted" | jq '.' > "$file"
    bejson_ok "Sorted by $field"
}

# ─── Count records ─────────────────────────────────────────────────────────

bejson_count() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi
    local count
    count=$(jq '.Values | length' "$file")
    echo "$count"
}

# ─── List fields ───────────────────────────────────────────────────────────

bejson_list_fields() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi
    jq -r '.Fields[] | "\(.name) (\(.type))\(.Record_Type_Parent // "" | if . != "" then " [" + . + "]" else "" end)"' "$file"
}

# ─── Pretty print ──────────────────────────────────────────────────────────

bejson_pretty() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi
    jq '.' "$file"
}

# ─── Quick stats ───────────────────────────────────────────────────────────

bejson_quick_stats() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        bejson_err "File not found: $file"
        return 1
    fi
    local version field_count record_count
    version=$(jq -r '.Format_Version' "$file")
    field_count=$(jq '.Fields | length' "$file")
    record_count=$(jq '.Values | length' "$file")
    echo -e "${BEJSON_BOLD}$(basename "$file")${BEJSON_RESET}: $version | $field_count fields | $record_count records"
}

# ─── Help ──────────────────────────────────────────────────────────────────

bejson_help() {
    echo -e "${BEJSON_BOLD}${BEJSON_BLUE}╔══════════════════════════════════════════════╗${BEJSON_RESET}"
    echo -e "${BEJSON_BOLD}${BEJSON_BLUE}║       BEJSON Bash Tools v1.0.0              ║${BEJSON_RESET}"
    echo -e "${BEJSON_BOLD}${BEJSON_BLUE}╚══════════════════════════════════════════════╝${BEJSON_RESET}"
    echo ""
    echo -e "${BEJSON_BOLD}Available Commands:${BEJSON_RESET}"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_validate${BEJSON_RESET} <file>"
    echo -e "    Validate a BEJSON file"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_info${BEJSON_RESET} <file> [-v]"
    echo -e "    Show file info and schema (verbose with -v)"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_query${BEJSON_RESET} <file> <field> <value> [entity]"
    echo -e "    Query records by field value"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_export${BEJSON_RESET} <file> [output]"
    echo -e "    Export BEJSON to plain JSON array"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_import${BEJSON_RESET} <json_file> [output] [record_type]"
    echo -e "    Import JSON array to BEJSON 104"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_create_104${BEJSON_RESET} <type> <fields_json> [output]"
    echo -e "    Create new BEJSON 104 document"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_sort${BEJSON_RESET} <file> <field> [-d]"
    echo -e "    Sort records by field (descending with -d)"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_count${BEJSON_RESET} <file>"
    echo -e "    Count records"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_list_fields${BEJSON_RESET} <file>"
    echo -e "    List all field names and types"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_pretty${BEJSON_RESET} <file>"
    echo -e "    Pretty-print BEJSON"
    echo ""
    echo -e "  ${BEJSON_GREEN}bejson_quick_stats${BEJSON_RESET} <file>"
    echo -e "    One-line summary"
    echo ""
}
