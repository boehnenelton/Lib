/*
Library:     lib_bejson_grid.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/

/**
 * lib_bejson_grid.js
 * Status: OFFICIAL — BEJSON-Core/Lib (v1.4)
 * Version: 1.4 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

class BEJSONGrid {
    constructor(name, width, height) {
        this.width = width;
        this.height = height;
        this.bejson = BEJSON.BEJSON.create104(name, [
            { name: "layer_name", type: "string" },
            { name: "data", type: "array" }
        ], []);
    }

    createLayer(name, initialValue = 0) {
        const data = new Array(this.width * this.height).fill(initialValue);
        this.bejson.Values.push([name, data]);
    }

    getTile(layerName, x, y) {
        const layer = this.bejson.Values.find(v => v[0] === layerName);
        if (!layer || x < 0 || x >= this.width || y < 0 || y >= this.height) return null;
        return layer[1][y * this.width + x];
    }

    setTile(layerName, x, y, val) {
        const layer = this.bejson.Values.find(v => v[0] === layerName);
        if (!layer || x < 0 || x >= this.width || y < 0 || y >= this.height) return;
        layer[1][y * this.width + x] = val;
    }
}

BEJSON.Grid = BEJSONGrid;
