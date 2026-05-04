/**
 * switch_core.js
 * game1 aka the BEJSON Game Engine (#1)
 * Author: Elton Boehnen: Main Orchestrator (v1.0)
 * Date: 2026-05-03
 */

window.Switch = window.Switch || {};

class SwitchEngine {
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

Switch.Engine = SwitchEngine;
