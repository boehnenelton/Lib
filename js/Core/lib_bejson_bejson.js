/*
Library:     lib_bejson_bejson.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-10
*/

/**
 * switch_bejson.js
 * Status: OFFICIAL — BEJSON-Core/Lib
 */
window.Switch = window.Switch || {};

Switch.BEJSON = {
    version: "1.0",

    create104(name, fields, values) {
        return {
            Format: "BEJSON",
            Version:     1.5 OFFICIAL
            Schema_Name: name,
            Fields: fields,
            Values: values
        };
    },

    create104a(name, fields, values, metadata = {}) {
        return {
            Format: "BEJSON",
            Version:     1.5 OFFICIAL
            Schema_Name: name,
            ...metadata,
            Fields: fields,
            Values: values
        };
    },

    create104db(name, recordTypes, fields, values) {
        return {
            Format: "BEJSON",
            Version:     1.5 OFFICIAL
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

export default Switch.BEJSON;
