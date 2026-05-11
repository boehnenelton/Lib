// bejson_events.ts
import { createEmpty104 } from "./index";
export class BEJSONEvents {
    events;
    stateManager;
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.events = createEmpty104("Events", [
            { name: "id", type: "string" },
            { name: "type", type: "string" },
            { name: "x", type: "number" },
            { name: "y", type: "number" },
            { name: "script", type: "array" },
            { name: "condition", type: "string" }
        ], "Root/System/Events");
    }
    async run(eventId) {
        const ev = this.events.Values.find(v => v[0] === eventId);
        if (!ev)
            return;
        if (ev[5] && !this._checkCondition(ev[5]))
            return;
        for (const cmd of ev[4])
            await this._execute(cmd);
    }
    _checkCondition(c) {
        if (c.startsWith("flag:"))
            return this.stateManager.state[c.split(":")[1]] === true;
        return true;
    }
    async _execute(cmd) {
        const [action, ...args] = cmd;
        if (action === "SET_FLAG")
            this.stateManager.state[args[0]] = args[1];
    }
}
