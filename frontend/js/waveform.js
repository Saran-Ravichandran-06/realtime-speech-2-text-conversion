export class Waveform {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
    }

    draw(data) {
        const ctx = this.ctx;
        const { width, height } = this.canvas;

        ctx.fillStyle = "#111";
        ctx.fillRect(0, 0, width, height);

        ctx.strokeStyle = "#00e1ff";
        ctx.beginPath();

        const step = Math.ceil(data.length / width);

        for (let i = 0; i < width; i++) {
            const min = data[i * step] || 0;
            const y = (1 - min) * height;
            if (i === 0) ctx.moveTo(i, y);
            else ctx.lineTo(i, y);
        }

        ctx.stroke();
    }
}
