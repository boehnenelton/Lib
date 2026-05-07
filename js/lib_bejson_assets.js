/*
Library:     lib_bejson_assets.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/

/**
 * lib_bejson_assets.js
 * Status: OFFICIAL — BEJSON-Core/Lib (v1.4)
 * Version: 1.4 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

class BEJSONAssets {
    constructor(name = "AssetRegistry") {
        this.bejson = BEJSON.BEJSON.create104a(name, [
            { name: "id", type: "string" },
            { name: "type", type: "string" },
            { name: "path", type: "string" },
            { name: "loaded", type: "boolean" }
        ], []);
        this.cache = new Map();
    }

    async load(id, type, path) {
        if (this.cache.has(id)) return this.cache.get(id);
        let asset;
        if (type === 'image') asset = await this._loadImage(path);
        else if (type === 'json') asset = await (await fetch(path)).json();
        this.cache.set(id, asset);
        return asset;
    }

    _loadImage(path) {
        return new Promise((res, rej) => {
            const img = new Image();
            img.onload = () => res(img);
            img.onerror = rej;
            img.src = path;
        });
    }

    get(id) { return this.cache.get(id); }
}

BEJSON.Assets = BEJSONAssets;
