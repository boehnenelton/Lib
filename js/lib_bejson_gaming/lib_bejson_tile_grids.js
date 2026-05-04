/**
 * switch_grid.js
 * game1 aka the BEJSON Game Engine (#1)
 * Author: Elton Boehnen: BEJSON-Native Tile Grid Manager (v1.0)
 * Date: 2026-05-03
 */

window.Switch = window.Switch || {};

class SwitchGrid {
    constructor(name, width, height) {
        this.width = width;
        this.height = height;
        this.bejson = Switch.BEJSON.create104(name, [
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

Switch.Grid = SwitchGrid;
