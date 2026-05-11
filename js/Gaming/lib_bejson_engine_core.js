// bejson_engine.ts
export class BEJSONEngine {
    systems;
    state;
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
            if (s.step)
                s.step(dt);
            if (s.update)
                s.update(dt);
        });
    }
}
