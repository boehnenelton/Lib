// bejson_physics.ts
import { createEmpty104 } from "./index";
export class BEJSONPhysics {
    gravity;
    bodies;
    constructor(options = {}) {
        this.gravity = options.gravity || { x: 0, y: 9.8 };
        this.bodies = createEmpty104("PhysicsWorld", [
            { name: "id", type: "string" },
            { name: "x", type: "number" },
            { name: "y", type: "number" },
            { name: "w", type: "number" },
            { name: "h", type: "number" },
            { name: "vx", type: "number" },
            { name: "vy", type: "number" },
            { name: "isStatic", type: "boolean" },
            { name: "mass", type: "number" }
        ]);
    }
    addBody(id, x, y, w, h, options = {}) {
        this.bodies.Values.push([
            id, x, y, w, h,
            options.vx || 0, options.vy || 0,
            options.isStatic || false,
            options.mass || 1
        ]);
    }
    applyImpulse(id, ix, iy) {
        const b = this.bodies.Values.find(v => v[0] === id);
        if (!b)
            return;
        b[5] += ix;
        b[6] += iy;
    }
    moveBody(id, dx, dy, staticColliders = []) {
        const b = this.bodies.Values.find(v => v[0] === id);
        if (!b)
            return;
        const oldX = b[1];
        b[1] += dx;
        if (this._checkStaticCollisions(b, staticColliders)) {
            b[1] = oldX;
        }
        const oldY = b[2];
        b[2] += dy;
        if (this._checkStaticCollisions(b, staticColliders)) {
            b[2] = oldY;
        }
    }
    step(dt, staticColliders = []) {
        const values = this.bodies.Values;
        // 1. Integrate & Resolve Static
        for (let i = 0; i < values.length; i++) {
            const b = values[i];
            if (b[7])
                continue; // isStatic
            b[5] += this.gravity.x * dt; // vx
            b[6] += this.gravity.y * dt; // vy
            // Friction (Standardized 0.9)
            b[5] *= 0.9;
            b[6] *= 0.9;
            // X Axis
            const oldX = b[1];
            b[1] += b[5] * dt;
            if (this._checkStaticCollisions(b, staticColliders)) {
                b[1] = oldX;
                b[5] = 0;
            }
            // Y Axis
            const oldY = b[2];
            b[2] += b[6] * dt;
            if (this._checkStaticCollisions(b, staticColliders)) {
                b[2] = oldY;
                b[6] = 0;
            }
        }
        // 2. Resolve Dynamic (Simple Swap)
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
    _checkStaticCollisions(b, colliders) {
        for (const c of colliders) {
            const cx = Array.isArray(c) ? c[0] : c.x;
            const cy = Array.isArray(c) ? c[1] : c.y;
            const cw = Array.isArray(c) ? c[2] : (c.w || c.width);
            const ch = Array.isArray(c) ? c[3] : (c.h || c.height);
            if (b[1] < cx + cw && b[1] + b[3] > cx &&
                b[2] < cy + ch && b[2] + b[4] > cy) {
                return true;
            }
        }
        return false;
    }
    _checkAABB(a, b) {
        return (a[1] < b[1] + b[3] &&
            a[1] + a[3] > b[1] &&
            a[2] < b[2] + b[4] &&
            a[2] + a[4] > b[2]);
    }
    _resolveCollision(a, b) {
        if (a[7] && b[7])
            return; // both static
        // Simple push-apart logic would go here, 
        // for now we just swap velocities for dynamic-dynamic
        const tempVx = a[5];
        a[5] = b[5];
        b[5] = tempVx;
        const tempVy = a[6];
        a[6] = b[6];
        b[6] = tempVy;
    }
}
