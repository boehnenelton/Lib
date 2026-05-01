#!/bin/bash
# MFDB v1.2 Archive Test - Bash (Internal Storage Edition)
export PATH="/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/bin/applets:$PATH"
source /storage/emulated/0/dev/lib/sh/lib_mfdb_core.sh
source /storage/emulated/0/dev/lib/sh/lib_mfdb_validator.sh

# Use internal Termux storage to avoid Android FUSE/Shared Storage permission issues
TEST_ROOT="$HOME/mfdb_test_space"
ARCHIVE="$TEST_ROOT/test.mfdb.zip"
MOUNT_DIR="$TEST_ROOT/workspace"

mkdir -p "$TEST_ROOT"
rm -rf "$MOUNT_DIR"
rm -f "$ARCHIVE"
rm -rf "$TEST_ROOT/db_source"

echo "1. Testing Database Creation & Manual Zipping..."
ENTITIES='[{"name":"ShellEntity","fields":[{"name":"id","type":"integer"}]}]'

# Capture output to see if creation fails
MANIFEST_SRC=$(mfdb_core_create_database "$TEST_ROOT/db_source" "ShellDB" "" "$ENTITIES")

if [[ ! -f "$MANIFEST_SRC" ]]; then
    echo "[FAIL] Database creation failed in $TEST_ROOT"
    exit 1
fi

(cd "$TEST_ROOT/db_source" && zip -r -q "$ARCHIVE" .)

echo "2. Testing Discovery..."
ROLE=$(mfdb_core_discover "$ARCHIVE")
if [[ "$ROLE" == "archive" ]]; then echo "[OK] Discovery"; else echo "[FAIL] Discovery (Got: $ROLE)"; exit 1; fi

echo "3. Testing Mount..."
# Using force=true to ensure we override any lingering locks
MANIFEST=$(mfdb_archive_mount "$ARCHIVE" "$MOUNT_DIR" "true")
if [[ -f "$MANIFEST" && -f "$MOUNT_DIR/.mfdb_lock" ]]; then 
    echo "[OK] Mount"
else 
    echo "[FAIL] Mount"
    ls -la "$MOUNT_DIR"
    exit 1
fi

echo "4. Testing Write & Commit..."
mfdb_core_add_entity_record "$MANIFEST" "ShellEntity" '[101]' > /dev/null
COMMIT_RESULT=$(mfdb_archive_commit "$MOUNT_DIR")
if [[ -f "$COMMIT_RESULT" ]]; then echo "[OK] Commit"; else echo "[FAIL] Commit"; exit 1; fi

# Verify content inside zip
if unzip -p "$ARCHIVE" data/shellentity.bejson | grep -q "101"; then
    echo "[OK] Content Integrity"
else
    echo "[FAIL] Content Integrity"
    unzip -p "$ARCHIVE" data/shellentity.bejson
    exit 1
fi

echo "5. Testing Validation..."
if mfdb_validator_validate_archive "$ARCHIVE"; then echo "[OK] Validation"; else echo "[FAIL] Validation"; exit 1; fi

# Cleanup
rm -rf "$TEST_ROOT"
echo "--- ALL BASH TESTS PASSED ---"
