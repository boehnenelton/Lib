// bejson_engine.ts
export class BEJSONEngine {
  public systems: Map<string, any>;
  public state: string;

  constructor() {
    this.systems = new Map();
    this.state = 'BOOT';
  }

  registerSystem(name: string, system: any) {
    this.systems.set(name, system);
  }

  getSystem(name: string): any {
    return this.systems.get(name);
  }

  loop(dt: number) {
    this.systems.forEach(s => {
      if (s.step) s.step(dt);
      if (s.update) s.update(dt);
    });
  }
}
