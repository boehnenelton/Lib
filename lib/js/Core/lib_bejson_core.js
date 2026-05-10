/*
Library:     lib_bejson_core.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/

/**
 * lib_bejson_core.js
 * Status:      OFFICIAL — BEJSON-Core/Lib (v1.5)
 * Version:     1.5 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

class BEJSONEngine {
    constructor() {
        this.systems = new Map();
        this.state = 'BOOT';
    }

    registerSystem(name, system) {
        this.systems.set(name, system);
    }

    getSystem(name) {
        return this.systems.get(name);
    }

    loop(dt) {
        this.systems.forEach(s => {
            if (s.step) s.step(dt);
            if (s.update) s.update(dt);
        });
    }
}

BEJSON.Engine = BEJSONEngine;
