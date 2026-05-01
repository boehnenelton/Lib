# Phase 2: Rust Implementation Plan (`bejson-rs`)
**Date:** April 24, 2026
**Topic:** Porting BEJSON Core to Rust (CoreEvo v1.1 Standard)
## Status: Complete

## Objective
Create a high-performance, memory-safe Rust implementation of the BEJSON core library that maintains 100% functional parity with the Python CoreEvo v1.1 fork. (ACHIEVED)

## Architecture
- **Crate Name:** `bejson`
- **Dependencies:** 
    - `serde`: For JSON serialization/deserialization.
    - `serde_json`: For JSON manipulation.
    - `tempfile`: For atomic write operations.
    - `chrono`: For timestamped backups.

## Core Components
1. **Types (`types.rs`):**
    - `BEJSONDocument` struct.
    - `BEJSONField` struct.
    - `BEJSONVersion` enum (104, 104a, 104db).
    - `BEJSONValue` enum (wrapping `serde_json::Value`).

2. **Core Logic (`lib.rs`):**
    - `load_file` / `load_str`: Parse and validate.
    - `get_records_by_type`: Strict 104db logic (index 0 lookup).
    - `get_field_applicability`: Strict 104db validation.
    - `query_records` & `sort_by_field`.
    - `atomic_write`: Including directory syncing for durability.

3. **Error Handling:**
    - Custom `BEJSONError` enum with error codes matching the official spec (20-27).

## Implementation Roadmap
1. **Step 1:** Initialize crate and define types.
2. **Step 2:** Implement basic loading and querying.
3. **Step 3:** Implement 104db strict validation logic.
4. **Step 4:** Implement atomic write with `fsync` parity.
5. **Step 5:** Create test suite to verify parity with Python/JS.

## Verification Strategy
- Port existing Python test cases to Rust `#[test]` functions.
- Ensure identical error codes for edge cases (e.g., legacy `applies_to` detection).
