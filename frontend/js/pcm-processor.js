class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.buffer = [];
        this.frameSize = 320;      // 20ms @ 16kHz
    }

    process(inputs) {
        const input = inputs[0][0];
        if (!input) return true;

        for (let i = 0; i < input.length; i++) {
            this.buffer.push(input[i]);
            if (this.buffer.length >= this.frameSize) {
                const frame = new Float32Array(this.buffer.splice(0, this.frameSize));
                this.port.postMessage(frame);
            }
        }
        return true;
    }
}

registerProcessor("pcm-processor", PCMProcessor);
