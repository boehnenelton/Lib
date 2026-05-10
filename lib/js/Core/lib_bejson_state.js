/*
Library:     lib_bejson_state.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/

/**
 * lib_bejson_state.js
 * Status:      OFFICIAL — BEJSON-Core/Lib (v1.5)
 * Version:     1.5 OFFICIAL
 * Date: 2026-05-03
 */
window.BEJSON = window.BEJSON || {};

class BEJSONState {
    constructor(initialState = {}, options = {}) {
        this.schema_name = options.name || "BEJSONState";
        this.bejson = BEJSON.BEJSON.create104db(this.schema_name, ["StateNode", "History"], [
            { name: "Record_Type_Parent", type: "string" },
            { name: "key", type: "string", Record_Type_Parent: "StateNode" },
            { name: "value", type: "string", Record_Type_Parent: "StateNode" },
            { name: "timestamp", type: "string", Record_Type_Parent: "History" },
            { name: "snapshot", type: "string", Record_Type_Parent: "History" }
        ], []);

        this._listeners = new Map();
        this._historyIndex = -1;
        this._activeEffect = null;
        this._dependencyGraph = new Map(); // path -> Set of effects

        // Reactive Proxy
        this.state = this._createProxy(initialState, '');
        
        // Initialize BEJSON values from initial state
        this._syncToBEJSON();
        this._saveHistory();
    }

    _createProxy(target, path) {
        const self = this;
        return new Proxy(target, {
            get(obj, prop) {
                const fullPath = path ? `${path}.${prop}` : prop;
                if (self._activeEffect) {
                    if (!self._dependencyGraph.has(fullPath)) self._dependencyGraph.set(fullPath, new Set());
                    self._dependencyGraph.get(fullPath).add(self._activeEffect);
                }
                const value = obj[prop];
                if (value && typeof value === 'object') return self._createProxy(value, fullPath);
                return value;
            },
            set(obj, prop, value) {
                const fullPath = path ? `${path}.${prop}` : prop;
                const oldValue = obj[prop];
                if (oldValue !== value) {
                    obj[prop] = value;
                    self._syncToBEJSON();
                    self._saveHistory();
                    self._notify(fullPath, value, oldValue);
                    self._triggerEffects(fullPath);
                }
                return true;
            }
        });
    }

    _syncToBEJSON() {
        // Clear StateNodes
        this.bejson.Values = this.bejson.Values.filter(r => r[0] !== "StateNode");
        // Flatten and add
        for (const [key, value] of Object.entries(this.state)) {
            this.bejson.Values.push(["StateNode", key, JSON.stringify(value), null, null]);
        }
    }

    _saveHistory() {
        const snapshot = JSON.stringify(this.state);
        this.bejson.Values.push(["History", null, null, new Date().toISOString(), snapshot]);
        const historyRows = this.bejson.Values.filter(r => r[0] === "History");
        this._historyIndex = historyRows.length - 1;
    }

    _notify(path, newValue, oldValue) {
        if (this._listeners.has(path)) this._listeners.get(path).forEach(cb => cb(newValue, oldValue, path));
        if (this._listeners.has('*')) this._listeners.get('*').forEach(cb => cb(newValue, oldValue, path));
    }

    _triggerEffects(path) {
        if (this._dependencyGraph.has(path)) this._dependencyGraph.get(path).forEach(effect => effect());
        // Handle nested paths (e.g., user.name triggers user)
        const parts = path.split('.');
        let currentPath = '';
        for (let i = 0; i < parts.length - 1; i++) {
            currentPath += (currentPath ? '.' : '') + parts[i];
            if (this._dependencyGraph.has(currentPath)) this._dependencyGraph.get(currentPath).forEach(e => e());
        }
    }

    subscribe(path, callback) {
        if (!this._listeners.has(path)) this._listeners.set(path, new Set());
        this._listeners.get(path).add(callback);
        return () => this._listeners.get(path).delete(callback);
    }

    effect(fn) {
        const runner = () => {
            this._activeEffect = runner;
            fn(this.state);
            this._activeEffect = null;
        };
        runner();
    }

    undo() {
        const historyRows = this.bejson.Values.filter(r => r[0] === "History");
        if (this._historyIndex <= 0) return false;
        this._historyIndex--;
        this._restore(JSON.parse(historyRows[this._historyIndex][4]));
        return true;
    }

    _restore(snapshot) {
        Object.keys(this.state).forEach(k => delete this.state[k]);
        Object.assign(this.state, snapshot);
        this._notify('*', this.state, null);
    }
}

BEJSON.State = BEJSONState;
