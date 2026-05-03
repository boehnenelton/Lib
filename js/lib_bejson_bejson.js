/**
 * lib_bejson_bejson.js
 * Status: OFFICIAL — BEJSON-Core/Lib (v1.4)
 * Version: 1.4 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

BEJSON.BEJSON = {
    version: "1.0",

    create104(name, fields, values) {
        return {
            Format: "BEJSON",
            Format_Version: "104",
            Schema_Name: name,
            Fields: fields,
            Values: values
        };
    },

    create104a(name, fields, values, metadata = {}) {
        return {
            Format: "BEJSON",
            Format_Version: "104a",
            Schema_Name: name,
            ...metadata,
            Fields: fields,
            Values: values
        };
    },

    create104db(name, recordTypes, fields, values) {
        return {
            Format: "BEJSON",
            Format_Version: "104db",
            Schema_Name: name,
            Records_Type: recordTypes,
            Fields: fields,
            Values: values
        };
    },

    getFieldIndex(doc, fieldName) {
        return doc.Fields.findIndex(f => f.name === fieldName);
    },

    query(doc, fieldName, value) {
        const idx = this.getFieldIndex(doc, fieldName);
        if (idx === -1) return [];
        return doc.Values.filter(row => row[idx] === value);
    },

    isValid(doc) {
        return doc && doc.Format === "BEJSON" && ["104", "104a", "104db"].includes(doc.Format_Version);
    }
};
