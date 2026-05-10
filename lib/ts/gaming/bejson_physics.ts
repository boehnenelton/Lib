// bejson_physics.ts
import { BEJSONDocument, createEmpty104 } from "./index";

export class BEJSONPhysics {
  public gravity: { x: number; y: number };
  public bodies: BEJSONDocument;

  constructor(options: any = {}) {
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

  addBody(id: string, x: number, y: number, w: number, h: number, options: any = {}) {
    this.bodies.Values.push([
      id, x, y, w, h, 
      options.vx || 0, options.vy || 0, 
      options.isStatic || false, 
      options.mass || 1
    ]);
  }

  step(dt: number) {
    const values = this.bodies.Values;
    // 1. Integrate
    for (let i = 0; i < values.length; i++) {
      const b = values[i];
      if (b[7]) continue; // isStatic

      (b[5] as number) += this.gravity.x * dt; // vx
      (b[6] as number) += this.gravity.y * dt; // vy
      (b[1] as number) += (b[5] as number) * dt; // x
      (b[2] as number) += (b[6] as number) * dt; // y
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

  private _checkAABB(a: any[], b: any[]) {
    return ((a[1] as number) < (b[1] as number) + (b[3] as number) && 
            (a[1] as number) + (a[3] as number) > (b[1] as number) && 
            (a[2] as number) < (b[2] as number) + (b[4] as number) && 
            (a[2] as number) + (a[4] as number) > (b[2] as number));
  }

  private _resolveCollision(a: any[], b: any[]) {
    if (a[7] && b[7]) return; // both static
    
    // Simple push-apart logic would go here, 
    // for now we just swap velocities for dynamic-dynamic
    const tempVx = a[5]; a[5] = b[5]; b[5] = tempVx;
    const tempVy = a[6]; a[6] = b[6]; b[6] = tempVy;
  }
}
