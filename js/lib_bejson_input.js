/**
 * lib_bejson_input.js
 * Status: OFFICIAL — BEJSON-Core/Lib (v1.4)
 * Version: 1.4 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

class BEJSONInput {
    constructor(options = {}) {
        this.deadzone = options.deadzone || 12;
        this.bindings = {
            up: ['ArrowUp', 'w'], down: ['ArrowDown', 's'],
            left: ['ArrowLeft', 'a'], right: ['ArrowRight', 'd'],
            action: ['Enter', ' '], cancel: ['Escape', 'x'], menu: ['m', 'Tab']
        };

        this.keys = {};
        this.justPressed = {};
        this.touch = { active: false, x: 0, y: 0, vector: { x: 0, y: 0 } };
        
        // Virtual Controls Configuration
        this.controls = {
            joystick: { x: 80, y: 0, radius: 50, active: false, handleX: 0, handleY: 0 },
            btnA: { x: 0, y: 0, radius: 30, pressed: false },
            btnB: { x: 0, y: 0, radius: 30, pressed: false }
        };

        window.addEventListener('keydown', (e) => this._onKey(e, true));
        window.addEventListener('keyup', (e) => this._onKey(e, false));
        window.addEventListener('touchstart', (e) => this._onTouch(e, true), { passive: false });
        window.addEventListener('touchmove', (e) => this._onTouch(e, true), { passive: false });
        window.addEventListener('touchend', (e) => this._onTouch(e, false));
    }

    _onKey(e, isDown) {
        if (isDown && !this.keys[e.key]) this.justPressed[e.key] = true;
        this.keys[e.key] = isDown;
    }

    _onTouch(e, isActive) {
        if (!isActive) {
            this.touch.active = false;
            this.controls.joystick.active = false;
            this.controls.joystick.handleX = 0;
            this.controls.joystick.handleY = 0;
            this.controls.btnA.pressed = false;
            this.controls.btnB.pressed = false;
            return;
        }

        const rect = document.querySelector('canvas').getBoundingClientRect();
        for (const t of e.touches) {
            const tx = t.clientX - rect.left;
            const ty = t.clientY - rect.top;

            // Check Joystick
            const j = this.controls.joystick;
            const distJ = Math.sqrt((tx - j.x)**2 + (ty - j.y)**2);
            if (distJ < j.radius * 2) {
                j.active = true;
                const dx = tx - j.x;
                const dy = ty - j.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                const limit = j.radius;
                j.handleX = dist > limit ? (dx/dist)*limit : dx;
                j.handleY = dist > limit ? (dy/dist)*limit : dy;
                this.touch.vector.x = j.handleX / limit;
                this.touch.vector.y = j.handleY / limit;
            }

            // Check Buttons
            if (this._checkCircle(tx, ty, this.controls.btnA)) {
                if (!this.controls.btnA.pressed) this.justPressed['action'] = true;
                this.controls.btnA.pressed = true;
            }
            if (this._checkCircle(tx, ty, this.controls.btnB)) {
                if (!this.controls.btnB.pressed) this.justPressed['cancel'] = true;
                this.controls.btnB.pressed = true;
            }
        }
        e.preventDefault();
    }

    _checkCircle(tx, ty, circle) {
        const dist = Math.sqrt((tx - circle.x)**2 + (ty - circle.y)**2);
        return dist < circle.radius;
    }

    getVector() {
        let vx = 0, vy = 0;
        if (this._isBoundDown('left')) vx -= 1;
        if (this._isBoundDown('right')) vx += 1;
        if (this._isBoundDown('up')) vy -= 1;
        if (this._isBoundDown('down')) vy += 1;

        if (this.controls.joystick.active) {
            vx += this.touch.vector.x;
            vy += this.touch.vector.y;
        }

        const mag = Math.sqrt(vx * vx + vy * vy);
        if (mag > 1) { vx /= mag; vy /= mag; }
        return { x: vx, y: vy, action: this.justPressed['action'], cancel: this.justPressed['cancel'] };
    }

    update() {
        this.justPressed = {};
    }

    renderControls(renderer) {
        const j = this.controls.joystick;
        const canvas = renderer.canvas;
        const h = canvas.height / renderer.dpr;
        const w = canvas.width / renderer.dpr;

        // Position joystick in bottom left
        j.y = h - 80;
        
        // Render Base
        renderer.drawCircle(j.x, j.y, j.radius, "rgba(255,255,255,0.2)", true);
        // Render Handle
        renderer.drawCircle(j.x + j.handleX, j.y + j.handleY, j.radius/2, "rgba(255,255,255,0.5)", true);

        // Buttons in bottom right
        const bA = this.controls.btnA;
        const bB = this.controls.btnB;
        bA.x = w - 60; bA.y = h - 100;
        bB.x = w - 120; bB.y = h - 60;

        renderer.drawCircle(bA.x, bA.y, bA.radius, bA.pressed ? "#f56565" : "rgba(255,255,255,0.3)", true);
        renderer.drawText("A", bA.x - 5, bA.y + 5, { isHUD: true });

        renderer.drawCircle(bB.x, bB.y, bB.radius, bB.pressed ? "#4299e1" : "rgba(255,255,255,0.3)", true);
        renderer.drawText("B", bB.x - 5, bB.y + 5, { isHUD: true });
    }
}

BEJSON.Input = BEJSONInput;
