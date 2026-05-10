/**
 * MFDB v1.2 Archive Test - JavaScript (Node.js Shim)
 */
const fs = require('fs');
const path = require('path');
const JSZip = require('jszip');

// Shims for vanilla JS in Node
global.window = {};
global.JSZip = JSZip;

// Mock FileSystemHandle for testing JSZip logic
class MockDirHandle {
    constructor(name, parent = null) {
        this.name = name;
        this.kind = 'directory';
        this.files = new Map();
        this.dirs = new Map();
    }
    async getDirectoryHandle(name, opts) {
        if (!this.dirs.has(name) && opts.create) this.dirs.set(name, new MockDirHandle(name, this));
        return this.dirs.get(name);
    }
    async getFileHandle(name, opts) {
        if (!this.files.has(name) && opts.create) {
            this.files.set(name, {
                name,
                kind: 'file',
                data: null,
                async createWritable() {
                    let outer = this;
                    return {
                        async write(d) { outer.data = d; },
                        async close() {}
                    };
                },
                async getFile() {
                    let d = this.data;
                    return {
                        name: this.name,
                        async arrayBuffer() { return d.buffer ? d.buffer.slice(d.byteOffset, d.byteOffset + d.byteLength) : d; }
                    };
                }
            });
        }
        return this.files.get(name);
    }
    async* values() {
        for (let d of this.dirs.values()) yield d;
        for (let f of this.files.values()) yield f;
    }
}

// Load library
const libText = fs.readFileSync('/storage/emulated/0/dev/lib/js/lib_mfdb_core.js', 'utf8');
eval(libText); // Injects into window.MFDB_CORE

const MFDB = window.MFDB_CORE;

async function runTests() {
    console.log("1. Testing JSZip Integration...");
    
    // Create a dummy zip buffer
    const zip = new JSZip();
    zip.file("104a.mfdb.bejson", JSON.stringify({Format:"BEJSON", Format_Version:"104a", Records_Type:["mfdb"], Fields:[{name:"entity_name",type:"string"}], Values:[["Test"]]}));
    zip.file("data/test.bejson", "{}");
    const zipBlob = await zip.generateAsync({type:"nodebuffer"});

    const mockRoot = new MockDirHandle("root");

    console.log("2. Testing Mount...");
    try {
        await MFDB.MFDBArchive.mount(zipBlob, mockRoot);
        console.log("[OK] Mount");
    } catch (e) {
        console.error("[FAIL] Mount", e);
        process.exit(1);
    }

    console.log("3. Testing Commit...");
    try {
        const resultBlob = await MFDB.MFDBArchive.commit(mockRoot);
        // In Node, resultBlob might be a Blob object or Buffer depending on shim
        const resultData = resultBlob.arrayBuffer ? await resultBlob.arrayBuffer() : resultBlob;
        const resultZip = await JSZip.loadAsync(resultData);
        if (resultZip.file("104a.mfdb.bejson")) {
            console.log("[OK] Commit");
        } else {
            throw new Error("Manifest missing in result");
        }
    } catch (e) {
        console.error("[FAIL] Commit", e);
        process.exit(1);
    }

    console.log("--- ALL JS TESTS PASSED ---");
}

runTests();
