// bejson_renderer.ts
export class BEJSONRenderer {
    canvas;
    ctx;
    dpr;
    camera;
    constructor(canvasId) {
        if (typeof document === 'undefined') {
            this.canvas = null;
            this.ctx = null;
            this.dpr = 1;
            this.camera = { x: 0, y: 0, zoom: 1 };
            return;
        }
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`BEJSON.Renderer: Canvas #${canvasId} not found.`);
            this.ctx = null;
            this.dpr = 1;
            this.camera = { x: 0, y: 0, zoom: 1 };
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        this.dpr = window.devicePixelRatio || 1;
        this.camera = { x: 0, y: 0, zoom: 1 };
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }
    resize() {
        if (!this.canvas || !this.ctx)
            return;
        const rect = this.canvas.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0)
            return;
        this.canvas.width = rect.width * this.dpr;
        this.canvas.height = rect.height * this.dpr;
        this.ctx.setTransform(this.dpr * this.camera.zoom, 0, 0, this.dpr * this.camera.zoom, 0, 0);
    }
    clear(color = "#000") {
        if (!this.ctx || !this.canvas)
            return;
        this.ctx.save();
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.fillStyle = color;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.restore();
    }
    drawRect(x, y, w, h, color, isHUD = false) {
        if (!this.ctx)
            return;
        this.ctx.fillStyle = color;
        const tx = isHUD ? x : x - this.camera.x;
        const ty = isHUD ? y : y - this.camera.y;
        this.ctx.fillRect(tx, ty, w, h);
    }
    drawCircle(x, y, radius, color, isHUD = false) {
        if (!this.ctx)
            return;
        this.ctx.fillStyle = color;
        const tx = isHUD ? x : x - this.camera.x;
        const ty = isHUD ? y : y - this.camera.y;
        this.ctx.beginPath();
        this.ctx.arc(tx, ty, radius, 0, Math.PI * 2);
        this.ctx.fill();
    }
    drawText(text, x, y, options = {}) {
        if (!this.ctx)
            return;
        this.ctx.fillStyle = options.color || "#fff";
        this.ctx.font = options.font || "16px sans-serif";
        const tx = options.isHUD ? x : x - this.camera.x;
        const ty = options.isHUD ? y : y - this.camera.y;
        this.ctx.fillText(text, tx, ty);
    }
    drawTileLayer(grid, tileset, tileSize) {
        if (!this.ctx || !grid || !tileset || !this.canvas)
            return;
        const width = this.canvas.width / (this.dpr * this.camera.zoom);
        const height = this.canvas.height / (this.dpr * this.camera.zoom);
        const startCol = Math.max(0, Math.floor(this.camera.x / tileSize));
        const endCol = Math.min(grid.width, Math.ceil((this.camera.x + width) / tileSize));
        const startRow = Math.max(0, Math.floor(this.camera.y / tileSize));
        const endRow = Math.min(grid.height, Math.ceil((this.camera.y + height) / tileSize));
        for (let r = startRow; r < endRow; r++) {
            for (let c = startCol; c < endCol; c++) {
                const tile = grid.data[r * grid.width + c];
                if (tile === 0)
                    continue;
                const sx = (tile % 16) * tileSize;
                const sy = Math.floor(tile / 16) * tileSize;
                this.ctx.drawImage(tileset, sx, sy, tileSize, tileSize, c * tileSize - this.camera.x, r * tileSize - this.camera.y, tileSize, tileSize);
            }
        }
    }
}
