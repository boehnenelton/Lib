/**
 * switch_input.js
 * game1 aka the BEJSON Game Engine (#1)
 * Author: Elton Boehnen: Unified Input Manager (v1.0)
 * Date: 2026-05-03
 */

window.Switch = window.Switch || {};

class SwitchInput {
    constructor(options = {}) {
        this.deadzone = options.deadzone || 12;
        this.bindings = {
            up: ['ArrowUp', 'w'], down: ['ArrowDown', 's'],
            left: ['ArrowLeft', 'a'], right: ['ArrowRight', 'd'],
            action: ['Enter', ' '], cancel: ['Escape', 'x'], menu: ['m', 'Tab']
        };

        this.keys = {};
        this.justPressed = {};
        this.touch = { active: false, startX: 0, startY: 0, currentX: 0, currentY: 0, vector: { x: 0, y: 0 } };

        window.addEventListener('keydown', (e) => this._onKey(e, true));
        window.addEventListener('keyup', (e) => this._onKey(e, false));
        window.addEventListener('touchstart', (e) => this._onTouchStart(e), { passive: false });
        window.addEventListener('touchmove', (e) => this._onTouchMove(e), { passive: false });
        window.addEventListener('touchend', (e) => this._onTouchEnd(e));
    }

    _onKey(e, isDown) {
        if (isDown && !this.keys[e.key]) this.justPressed[e.key] = true;
        this.keys[e.key] = isDown;
    }

    _onTouchStart(e) {
        const t = e.touches[0];
        this.touch.active = true;
        this.touch.startX = t.clientX; this.touch.startY = t.clientY;
        this.touch.currentX = t.clientX; this.touch.currentY = t.clientY;
    }

    _onTouchMove(e) {
        if (!this.touch.active) return;
        const t = e.touches[0];
        this.touch.currentX = t.clientX; this.touch.currentY = t.clientY;
        const dx = this.touch.currentX - this.touch.startX;
        const dy = this.touch.currentY - this.touch.startY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > this.deadzone) {
            this.touch.vector.x = dx / dist; this.touch.vector.y = dy / dist;
        } else {
            this.touch.vector.x = 0; this.touch.vector.y = 0;
        }
    }

    _onTouchEnd(e) { this.touch.active = false; this.touch.vector.x = 0; this.touch.vector.y = 0; }

    getVector() {
        let vx = 0, vy = 0;
        if (this._isBoundDown('left')) vx -= 1;
        if (this._isBoundDown('right')) vx += 1;
        if (this._isBoundDown('up')) vy -= 1;
        if (this._isBoundDown('down')) vy += 1;
        if (this.touch.active) { vx += this.touch.vector.x; vy += this.touch.vector.y; }
        const mag = Math.sqrt(vx * vx + vy * vy);
        if (mag > 1) { vx /= mag; vy /= mag; }
        return { x: vx, y: vy, action: this._isBoundJustPressed('action'), cancel: this._isBoundJustPressed('cancel'), menu: this._isBoundJustPressed('menu') };
    }

    _isBoundDown(a) { return this.bindings[a].some(k => this.keys[k]); }
    _isBoundJustPressed(a) { return this.bindings[a].some(k => this.justPressed[k]); }
    update() { this.justPressed = {}; }
}

Switch.Input = SwitchInput;
