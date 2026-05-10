/*
Library:     lib_bejson_ui_screens.js
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-10
*/

/**
 * switch_ui_screens.js
 * game1 aka the BEJSON Game Engine (#1)
 * Author: Elton Boehnen: BEJSON-Native UI Screen Manager (v1.1
 * Date: 2026-05-03
 * Family: Gaming
 */

window.Switch = window.Switch || {};

class SwitchUIScreens {
    constructor(renderer) {
        this.renderer = renderer;
        this.activeScreen = null;
        this.screens = Switch.BEJSON.create104("UIScreens", [
            { name: "id", type: "string" },
            { name: "title", type: "string" },
            { name: "options", type: "array" }
        ], [
            ["START_SCREEN", "SWITCH RPG", ["Start Game", "Load Game", "Options", "Exit"]],
            ["SAVE_MENU", "SAVE GAME", ["Slot 1", "Slot 2", "Slot 3", "Back"]]
        ]);
        
        this.selectedIndex = 0;
    }

    show(id) {
        this.activeScreen = this.screens.Values.find(v => v[0] === id);
        this.selectedIndex = 0;
    }

    render() {
        if (!this.activeScreen) return;

        const [id, title, options] = this.activeScreen;
        const canvas = this.renderer.canvas;
        const dpr = this.renderer.dpr;
        const w = canvas.width / dpr;
        const h = canvas.height / dpr;

        // Dim Background
        this.renderer.drawRect(0, 0, w, h, "rgba(0,0,0,0.8)", true);

        // Title
        this.renderer.drawText(title, w / 2 - 50, h / 4, { 
            font: "bold 24px sans-serif", 
            isHUD: true,
            color: "#3b82f6"
        });

        // Options
        options.forEach((opt, i) => {
            const isSelected = i === this.selectedIndex;
            const color = isSelected ? "#fff" : "#666";
            const prefix = isSelected ? "> " : "  ";
            this.renderer.drawText(prefix + opt, w / 2 - 40, h / 2 + (i * 30), { 
                font: "18px sans-serif", 
                isHUD: true,
                color: color
            });
        });
    }

    navigate(dir) {
        if (!this.activeScreen) return;
        const options = this.activeScreen[2];
        this.selectedIndex = (this.selectedIndex + dir + options.length) % options.length;
    }

    getSelectedOption() {
        if (!this.activeScreen) return null;
        return this.activeScreen[2][this.selectedIndex];
    }
}

Switch.UIScreens = SwitchUIScreens;
export default SwitchUIScreens;
