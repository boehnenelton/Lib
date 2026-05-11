#!/bin/bash
# # Library:     lib_bejson_parse.sh
MFDB Version: 1.3.1
# Format_Creator: Elton Boehnen
# Status:      OFFICIAL - v1.3.1
# Date:        2026-05-06

#===============================================================================
# Library:     lib_bejson_parse.sh
# Jurisdiction: ["BASH", "CORE_COMMAND"]
# Status:      OFFICIAL — Core-Command/Lib (v1.5)
# Author:      Elton Boehnen
# Version:     1.5 OFFICIAL
# Date:        2026-04-23
# Description: BEJSON structured parser — extracts files from BEJSON 104 / 104a /
104db schemas. Sources lib_bejson_core.sh and lib_bejson_validator.sh.
Author:      Elton Boehnen
Version:     1.5 OFFICIAL
Date:        2026-04-16
Compatibility: Bash 4.0+, Termux/Android
Dependencies:  lib_bejson_core.sh, lib_bejson_validator.sh, jq, zip
Changelog v2.0.0:
[FIX] Integrated `sync` call after batch file extraction to ensure 
durability on flash media (Termux/Android).
#===============================================================================
#===============================================================================
# Library:     lib_bejson_parse.sh
# Description: BEJSON structured parser — extracts files from BEJSON 104 / 104a /
#              104db schemas. Sources lib_bejson_core.sh and lib_bejson_validator.sh.
# Compatibility: Bash 4.0+, Termux/Android
# Dependencies:  lib_bejson_core.sh, lib_bejson_validator.sh, jq, zip
#
# Changelog v2.0.0:
#   [FIX] Integrated `sync` call after batch file extraction to ensure 
#         durability on flash media (Termux/Android).

set -o pipefail
set -o nounset

# ------------------------------------------------------------------
# Source BEJSON ecosystem — core + validator
# ------------------------------------------------------------------
BEJSON_PARSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$BEJSON_PARSE_DIR/lib_bejson_core.sh" ]]; then
    source "$BEJSON_PARSE_DIR/lib_bejson_core.sh"
elif [[ -f "$BEJSON_PARSE_DIR/lib-bejson_core.sh" ]]; then
    source "$BEJSON_PARSE_DIR/lib-bejson_core.sh"
else
    echo "ERROR: lib_bejson_core.sh not found in $BEJSON_PARSE_DIR" >&2
    return 1 2>/dev/null || exit 1
fi

# Default output directory (callers may override via argument)
BEJSON_PARSE_DEFAULT_OUT="${BEJSON_PARSE_DIR}/output"

# Globals populated by bejson_extract_data
BEJSON_PROJECT_NAME="My_Project"
BEJSON_FILES_NAMES=()
BEJSON_FILES_CONTENTS=()

# ------------------------------------------------------------------
# PARSER CORE — functions mirrored from lib_bejson_parse.py
# ------------------------------------------------------------------

#-------------------------------------------------------------------------------
# bejson_parse_json <text>
#   Strip any prose wrapper from <text> and print valid JSON to stdout.
#   Mirrors parse_json() in lib_bejson_parse.py.
#   Returns 0 on success, 1 on parse failure.
#-------------------------------------------------------------------------------
bejson_parse_json() {
    local text="$1"

    # Try to extract a JSON object using awk (handles multi-line)
    local clean
    clean=$(echo "$text" | awk '
        /\{/ { found=1 }
        found { buf = buf $0 "\n" }
        END   { print buf }
    ' | sed 's/^[^{]*//')   # trim anything before first {

    # Validate with jq
    if echo "$clean" | jq '.' > /dev/null 2>&1; then
        echo "$clean" | jq '.'
        return 0
    fi

    # Fallback: try raw text as-is
    if echo "$text" | jq '.' > /dev/null 2>&1; then
        echo "$text" | jq '.'
        return 0
    fi

    echo "ERROR: parse_json — could not parse JSON from input" >&2
    return 1
}

#-------------------------------------------------------------------------------
# bejson_extract_data <json_string>
#   Walk a BEJSON object and populate:
#     BEJSON_PROJECT_NAME      (string)
#     BEJSON_FILES_NAMES[]     (array)
#     BEJSON_FILES_CONTENTS[]  (array)
#   Mirrors extract_data() in lib_bejson_parse.py — same logic.
#   Returns 0 on success, 1 if no files found.
#-------------------------------------------------------------------------------
bejson_extract_data() {
    local json="$1"

    BEJSON_PROJECT_NAME="My_Project"
    BEJSON_FILES_NAMES=()
    BEJSON_FILES_CONTENTS=()

    # ---- Resolve project name from first matching key across all rows ----
    # Priority: zip_file_name / project_name → zip_file_name → container_name
    local proj_raw=""

    # Try zip_file_name first (104a)
    proj_raw=$(echo "$json" | jq -r '
        .Values[] |
        to_entries |
        . as $row |
        ( .[] | select(.key == (
            [ .[] | .key ] | index(
              (.[] | select(
                (.value | type == "object") and (.value.name // "" | ascii_downcase | gsub("[^a-z0-9]";"";"g")) == "zipfilename"
              ) // empty)
            )
          ))
        ) | .value
    ' 2>/dev/null | head -1)

    # Simpler approach: use jq to find field index for each candidate key, then read value
    _bejson_parse_get_project_name() {
        local j="$1"
        local result="My_Project"

        local field_count
        field_count=$(echo "$j" | jq '.Fields | length')

        # Build a map: normalised_name -> index
        local cands=("zipfilename" "projectname" "containername")

        for cand in "${cands[@]}"; do
            local idx
            idx=$(echo "$j" | jq --arg c "$cand" '
                .Fields | to_entries[] |
                select((.value.name | ascii_downcase | gsub("[^a-z0-9]";"")) == $c) |
                .key
            ' 2>/dev/null | head -1)

            if [[ -n "$idx" ]]; then
                local val
                val=$(echo "$j" | jq -r --argjson i "$idx" '
                    .Values[] |
                    if (. | length) > $i then .[$i] else null end |
                    select(. != null and . != "") |
                    tostring
                ' 2>/dev/null | head -1)

                if [[ -n "$val" && "$val" != "null" ]]; then
                    result="$val"
                    break
                fi
            fi
        done

        echo "$result"
    }

    BEJSON_PROJECT_NAME=$(_bejson_parse_get_project_name "$json")
    # Sanitise (strip chars forbidden in dir names)
    BEJSON_PROJECT_NAME=$(echo "$BEJSON_PROJECT_NAME" | sed 's/[<>:"\/\\|?*]/_/g')

    # ---- Extract file1..file50 name/content pairs from every row ----
    local field_count
    field_count=$(echo "$json" | jq '.Fields | length')

    for i in $(seq 1 50); do
        local name_key="file${i}name"
        local cont_key="file${i}content"

        # Find column indices
        local name_idx cont_idx
        name_idx=$(echo "$json" | jq --arg k "$name_key" '
            .Fields | to_entries[] |
            select((.value.name | ascii_downcase | gsub("[^a-z0-9]";"")) == $k) |
            .key
        ' 2>/dev/null | head -1)

        cont_idx=$(echo "$json" | jq --arg k "$cont_key" '
            .Fields | to_entries[] |
            select((.value.name | ascii_downcase | gsub("[^a-z0-9]";"")) == $k) |
            .key
        ' 2>/dev/null | head -1)

        [[ -z "$name_idx" || -z "$cont_idx" ]] && continue

        # Scan every row for this pair
        local row_count
        row_count=$(echo "$json" | jq '.Values | length')

        for r in $(seq 0 $(( row_count - 1 ))); do
            local fname fcont
            fname=$(echo "$json" | jq -r --argjson r "$r" --argjson ni "$name_idx" '
                .Values[$r][$ni] // empty | select(. != null and . != "")
            ' 2>/dev/null)
            fcont=$(echo "$json" | jq -r --argjson r "$r" --argjson ci "$cont_idx" '
                .Values[$r][$ci] // empty | select(. != null and . != "")
            ' 2>/dev/null)

            if [[ -n "$fname" && -n "$fcont" ]]; then
                BEJSON_FILES_NAMES+=("$fname")
                BEJSON_FILES_CONTENTS+=("$fcont")
            fi
        done
    done

    if [[ ${#BEJSON_FILES_NAMES[@]} -eq 0 ]]; then
        echo "ERROR: extract_data — no file entries found in schema" >&2
        return 1
    fi

    return 0
}

#-------------------------------------------------------------------------------
# bejson_save_files <proj> <out_dir> [overwrite]
#   Write files to disk, generate _REPORT.txt, and zip everything.
#   Uses global arrays BEJSON_FILES_NAMES[] and BEJSON_FILES_CONTENTS[].
#   Mirrors save_files() in lib_bejson_parse.py — same logic.
#
#   Arguments:
#     proj      - project name (used as folder/zip base name)
#     out_dir   - base output directory (default: ./output)
#     overwrite - "true" = merge/update mode; anything else = timestamped
#
#   Echoes result JSON: {"success":true/false,"message":"...","path":"...","file_count":N}
#   Returns 0 on success, 1 on failure.
#-------------------------------------------------------------------------------
bejson_save_files() {
    local proj="${1:-My_Project}"
    local base_dir="${2:-$BEJSON_PARSE_DEFAULT_OUT}"
    local overwrite="${3:-false}"

    # Ensure base dir exists
    if [[ ! -d "$base_dir" ]]; then
        mkdir -p "$base_dir" 2>/dev/null || {
            echo '{"success":false,"message":"Cannot create output dir: '"$base_dir"'"}'
            return 1
        }
    fi

    local target
    if [[ "$overwrite" == "true" ]]; then
        target="${base_dir}/${proj}"
        local bak_target="${base_dir}/${proj}_BACKUP"
        if [[ -d "$target" ]]; then
            [[ -d "$bak_target" ]] && rm -rf "$bak_target"
            cp -r "$target" "$bak_target" 2>/dev/null \
                || echo "WARNING: backup of $target failed" >&2
        fi
    else
        local ts
        ts=$(date +"%Y%m%d_%H%M%S")
        target="${base_dir}/${ts}_${proj}"
    fi

    mkdir -p "$target" 2>/dev/null || {
        echo '{"success":false,"message":"Cannot create target dir: '"$target"'"}'
        return 1
    }

    local file_count=${#BEJSON_FILES_NAMES[@]}

    # Write each file
    local i
    for i in $(seq 0 $(( file_count - 1 ))); do
        local fname="${BEJSON_FILES_NAMES[$i]}"
        local fcont="${BEJSON_FILES_CONTENTS[$i]}"
        local fpath="${target}/${fname}"
        local fdir
        fdir=$(dirname "$fpath")
        [[ ! -d "$fdir" ]] && mkdir -p "$fdir"
        printf '%s' "$fcont" > "$fpath"
    done
    
    # CRITICAL FIX: explicit disk sync after batch write
    if command -v sync &>/dev/null; then
        sync "$target" 2>/dev/null || sync 2>/dev/null || true
    fi

    # Build report
    local ts_now mode_str sep52 dash52 report_lines report_text
    ts_now=$(date +"%Y-%m-%d %H:%M:%S")
    if [[ "$overwrite" == "true" ]]; then
        mode_str="Merge/Update (overwrite)"
    else
        mode_str="Timestamped (new folder)"
    fi
    sep52=$(printf '=%.0s' {1..52})
    dash52=$(printf -- '-%.0s' {1..52})

    report_text="${sep52}
  STRUCTURED PARSER — BUILD REPORT
${sep52}
Project    : ${proj}
Generated  : ${ts_now}
Mode       : ${mode_str}
Output Dir : ${target}
Files      : ${file_count}
${dash52}
FILE LIST
${dash52}"

    for i in $(seq 0 $(( file_count - 1 ))); do
        local fname="${BEJSON_FILES_NAMES[$i]}"
        local fpath="${target}/${fname}"
        local size_b=0
        [[ -f "$fpath" ]] && size_b=$(wc -c < "$fpath" | tr -d ' ')
        local size_s
        if (( size_b >= 1024 )); then
            size_s="$(echo "scale=1; $size_b/1024" | bc) KB"
        else
            size_s="${size_b} B"
        fi
        local idx_padded
        idx_padded=$(printf '%02d' $(( i + 1 )))
        report_text="${report_text}
  [${idx_padded}] ${fname}  (${size_s})"
    done

    report_text="${report_text}
${dash52}
Zip        : ${proj}_update.zip
${sep52}
"

    # Write report
    printf '%s\n' "$report_text" > "${target}/_REPORT.txt"
    if command -v sync &>/dev/null; then
        sync "${target}/_REPORT.txt" 2>/dev/null || sync 2>/dev/null || true
    fi

    # Build zip
    local zip_path="${target}/${proj}_update.zip"
    local zip_ok=true

    if command -v zip &>/dev/null; then
        (
            cd "$target" || exit 1
            local files_to_zip=()
            for i in $(seq 0 $(( file_count - 1 ))); do
                files_to_zip+=("${BEJSON_FILES_NAMES[$i]}")
            done
            zip -r "${proj}_update.zip" "${files_to_zip[@]}" "_REPORT.txt" > /dev/null 2>&1
        ) || zip_ok=false
    else
        echo "WARNING: 'zip' not found — skipping zip step (pkg install zip)" >&2
        zip_ok=false
    fi

    local zip_note=""
    [[ "$zip_ok" == "false" ]] && zip_note=" (zip skipped)"

    local escaped_target
    escaped_target=$(echo "$target" | sed 's/"/\\"/g')

    echo "{\"success\":true,\"message\":\"Saved ${file_count} file(s)${zip_note}\",\"path\":\"${escaped_target}\",\"file_count\":${file_count}}"
    return 0
}
