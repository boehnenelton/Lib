/*
Library:     mfdb_core.ts
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/
import { MFDBCoreError, MFDB_CORE_CODES as E, } from "./bejson_types";
import { decodeManifestRecords } from "./mfdb_validators";
import { appendRecord, deleteRecord, getFieldIndex, setFieldValue, createEmpty104a, } from "./bejson_core";
export function createManifest(opts) {
    if (!opts.db_name || opts.db_name.trim() === "") {
        throw new MFDBCoreError(E.MISSING_DB_NAME, "DB_Name is required when creating a manifest.");
    }
    const includeOptional = opts.includeOptionalFields !== false;
    const fields = [
        { name: "entity_name", type: "string" },
        { name: "file_path", type: "string" },
    ];
    if (includeOptional) {
        fields.push({ name: "description", type: "string" }, { name: "record_count", type: "integer" }, { name: "schema_version", type: "string" }, { name: "primary_key", type: "string" });
    }
    const customHeaders = {
        MFDB_Version: opts.mfdb_version ?? "1.3.1",
        DB_Name: opts.db_name,
    };
    if (opts.db_description)
        customHeaders["DB_Description"] = opts.db_description;
    if (opts.schema_version)
        customHeaders["Schema_Version"] = opts.schema_version;
    if (opts.author)
        customHeaders["Author"] = opts.author;
    if (opts.created_at)
        customHeaders["Created_At"] = opts.created_at;
    return createEmpty104a("mfdb", fields, customHeaders);
}
export function registerEntity(manifest, record) {
    _assertManifest(manifest);
    const existing = decodeManifestRecords(manifest);
    if (existing.some((r) => r.entity_name === record.entity_name)) {
        throw new MFDBCoreError(E.DUPLICATE_ENTITY_NAME, "Entity \"" + record.entity_name + "\" is already registered.");
    }
    const fieldNames = manifest.Fields.map((f) => f.name);
    const row = fieldNames.map((name) => {
        switch (name) {
            case "entity_name": return record.entity_name;
            case "file_path": return record.file_path;
            case "description": return record.description ?? null;
            case "record_count": return record.record_count ?? null;
            case "schema_version": return record.schema_version ?? null;
            case "primary_key": return record.primary_key ?? null;
            default: return null;
        }
    });
    return appendRecord(manifest, row);
}
export function unregisterEntity(manifest, entityName) {
    _assertManifest(manifest);
    const idx = _findEntityIndex(manifest, entityName);
    return deleteRecord(manifest, idx);
}
export function syncRecordCount(manifest, entityName, count) {
    _assertManifest(manifest);
    const idx = _findEntityIndex(manifest, entityName);
    try {
        getFieldIndex(manifest, "record_count");
    }
    catch {
        throw new MFDBCoreError(E.RECORD_COUNT_SYNC_FAILED, "Manifest lacks \"record_count\" field.");
    }
    return setFieldValue(manifest, idx, "record_count", count);
}
function _assertManifest(doc) {
    if (!doc) {
        throw new MFDBCoreError(E.NULL_MANIFEST, "Manifest is null or undefined.");
    }
}
function _findEntityIndex(manifest, entityName) {
    const enIdx = getFieldIndex(manifest, "entity_name");
    for (let i = 0; i < manifest.Values.length; i++) {
        if (manifest.Values[i][enIdx] === entityName)
            return i;
    }
    throw new MFDBCoreError(E.ENTITY_NOT_IN_MANIFEST, "Entity \"" + entityName + "\" not found.");
}
