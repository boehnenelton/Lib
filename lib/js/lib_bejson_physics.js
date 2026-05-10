/*
Library:     lib_bejson_physics.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/

/**
 * lib_bejson_physics.js
 * Status: OFFICIAL — BEJSON-Core/Lib (v1.4)
 * Version: 1.4 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

class BEJSONPhysics {
    constructor(options = {}) {
        this.gravity = options.gravity || { x: 0, y: 9.8 };
        this.bodies = BEJSON.BEJSON.create104("PhysicsWorld", [
            { name: "id", type: "string" },
            { name: "x", type: "number" },
            { name: "y", type: "number" },
            { name: "w", type: "number" },
            { name: "h", type: "number" },
            { name: "vx", type: "number" },
            { name: "vy", type: "number" },
            { name: "isStatic", type: "boolean" },
            { name: "mass", type: "number" }
        ], []);
    }

    addBody(id, x, y, w, h, options = {}) {
        this.bodies.Values.push([
            id, x, y, w, h, 
            options.vx || 0, options.vy || 0, 
            options.isStatic || false, 
            options.mass || 1
        ]);
    }

    step(dt) {
        const values = this.bodies.Values;
        // 1. Integrate
        for (let i = 0; i < values.length; i++) {
            const b = values[i];
            if (b[7]) continue; // isStatic

            b[5] += this.gravity.x * dt; // vx
            b[6] += this.gravity.y * dt; // vy
            b[1] += b[5] * dt; // x
            b[2] += b[6] * dt; // y
        }

        // 2. Resolve (Simple AABB)
        for (let i = 0; i < values.length; i++) {
            const bA = values[i];
            for (let j = i + 1; j < values.length; j++) {
                const bB = values[j];
                if (this._checkAABB(bA, bB)) {
                    this._resolveCollision(bA, bB);
                }
            }
        }
    }

    _checkAABB(a, b) {
        return (a[1] < b[1] + b[3] && a[1] + a[3] > b[1] && a[2] < b[2] + b[4] && a[2] + a[4] > b[2]);
    }

    _resolveCollision(a, b) {
        // Simple static/dynamic resolution
        if (a[7] && b[7]) return;
        
        // Swap velocities for dynamic-dynamic for now
        const tempVx = a[5]; a[5] = b[5]; b[5] = tempVx;
        const tempVy = a[6]; a[6] = b[6]; b[6] = tempVy;
    }
}

BEJSON.Physics = BEJSONPhysics;
