/**
 * switch_assets.js
 * game1 aka the BEJSON Game Engine (#1)
 * Author: Elton Boehnen: BEJSON-Native Asset Registry (v1.0)
 * Date: 2026-05-03
 */

window.Switch = window.Switch || {};

class SwitchAssets {
    constructor(name = "AssetRegistry") {
        this.bejson = Switch.BEJSON.create104a(name, [
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

Switch.Assets = SwitchAssets;
