/*
Library:     bejson_types.ts
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/
// ---------------------------------------------------------------------------
// Error classes
// ---------------------------------------------------------------------------
export class BEJSONValidationError extends Error {
    code;
    constructor(code, message) {
        super(message);
        this.name = "BEJSONValidationError";
        this.code = code;
    }
}
export class BEJSONCoreError extends Error {
    code;
    constructor(code, message) {
        super(message);
        this.name = "BEJSONCoreError";
        this.code = code;
    }
}
export class MFDBValidationError extends Error {
    code;
    constructor(code, message) {
        super(message);
        this.name = "MFDBValidationError";
        this.code = code;
    }
}
export class MFDBCoreError extends Error {
    code;
    constructor(code, message) {
        super(message);
        this.name = "MFDBCoreError";
        this.code = code;
    }
}
// ---------------------------------------------------------------------------
// Validation error code catalogue
// ---------------------------------------------------------------------------
export const BEJSON_VALIDATION_CODES = {
    INVALID_JSON: 1,
    MISSING_MANDATORY_KEY: 2,
    INVALID_FORMAT_VALUE: 3,
    INVALID_FORMAT_VERSION: 4,
    INVALID_FORMAT_CREATOR: 5,
    INVALID_RECORDS_TYPE: 6,
    INVALID_FIELDS: 7,
    DUPLICATE_FIELD_NAME: 8,
    INVALID_VALUES_STRUCTURE: 9,
    RECORD_LENGTH_MISMATCH: 10,
    VALUE_TYPE_MISMATCH: 11,
    VERSION_CONSTRAINT: 12,
    FORBIDDEN_CUSTOM_KEY: 13,
    INVALID_CUSTOM_KEY: 14,
    MISSING_DISCRIMINATOR: 15,
};
export const BEJSON_CORE_CODES = {
    NULL_DOCUMENT: 20,
    INDEX_OUT_OF_BOUNDS: 21,
    FIELD_NOT_FOUND: 22,
    WRITE_LENGTH_MISMATCH: 23,
    SERIALIZATION_ERROR: 24,
    PARSE_ERROR: 25,
    WRITE_TYPE_MISMATCH: 26,
    UNSUPPORTED_OPERATION: 27,
};
export const MFDB_VALIDATION_CODES = {
    NOT_A_MANIFEST: 30,
    NOT_AN_ENTITY: 31,
    MANIFEST_RECORDS_TYPE_INVALID: 32,
    ENTITY_FILE_NOT_FOUND: 33,
    ENTITY_NAME_MISMATCH: 34,
    DUPLICATE_ENTRY: 35,
    MISSING_PARENT_HIERARCHY: 36,
    MANIFEST_FILE_NOT_FOUND: 37,
    BIDIRECTIONAL_PATH_FAILED: 38,
    FK_UNRESOLVED: 39,
    MISSING_REQUIRED_MANIFEST_FIELD: 40,
    NULL_IN_REQUIRED_MANIFEST_FIELD: 41,
};
export const MFDB_CORE_CODES = {
    NULL_MANIFEST: 50,
    NULL_ENTITY: 51,
    INVALID_MFDB_VERSION: 52,
    MISSING_DB_NAME: 53,
    ENTITY_NOT_IN_MANIFEST: 54,
    MANIFEST_READONLY: 55,
    SCHEMA_VERSION_CONFLICT: 56,
    RECORD_COUNT_SYNC_FAILED: 57,
    DUPLICATE_ENTITY_NAME: 58,
};
