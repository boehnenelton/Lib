// bejson_assets.ts
import { createEmpty104a } from "./index";
export class BEJSONAssets {
    bejson;
    cache;
    constructor(name = "AssetRegistry") {
        this.bejson = createEmpty104a(name, [
            { name: "id", type: "string" },
            { name: "type", type: "string" },
            { name: "path", type: "string" },
            { name: "loaded", type: "boolean" }
        ]);
        this.cache = new Map();
    }
    async load(id, type, path) {
        if (this.cache.has(id))
            return this.cache.get(id);
        let asset;
        if (type === 'image')
            asset = await this._loadImage(path);
        else if (type === 'json')
            asset = await (await fetch(path)).json();
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
