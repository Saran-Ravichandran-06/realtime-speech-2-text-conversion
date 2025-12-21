export class AudioCapture {
    // onAudioFrame: callback(float32Frame)
    // options: { micGain: number (0.0-1.0), constraints: getUserMedia audio constraints }
    constructor(onAudioFrame, options = {}) {
        this.audioContext = null;
        this.processorNode = null;
        this.onAudioFrame = onAudioFrame;
        this.stream = null;
        this.micGain = typeof options.micGain === 'number' ? options.micGain : 0.45;
        this.constraints = Object.assign({
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: false
        }, options.constraints || {});
    }

    async start() {
        // Create 16kHz audio context
        this.audioContext = new AudioContext({ sampleRate: 16000 });

        // Load the worklet (MUST before getUserMedia)
        await this.audioContext.audioWorklet.addModule("js/pcm-processor.js");

        // Get microphone with constraints to reduce background noise
        this.stream = await navigator.mediaDevices.getUserMedia({ audio: this.constraints });
        const source = this.audioContext.createMediaStreamSource(this.stream);

        // Input gain to reduce microphone sensitivity (0.0 = silent, 1.0 = original)
        const inputGain = this.audioContext.createGain();
        inputGain.gain.value = this.micGain;

        // Create processor node
        this.processorNode = new AudioWorkletNode(this.audioContext, "pcm-processor");

        // Receive Float32 PCM frames from worklet
        this.processorNode.port.onmessage = (event) => {
            const float32Frame = event.data;
            if (float32Frame instanceof Float32Array) {
                this.onAudioFrame(float32Frame);
            }
        };

        // Connect audio pipeline: source -> inputGain -> processor -> silent output
        source.connect(inputGain);
        inputGain.connect(this.processorNode);

        // Ensure worklet is driven by connecting to destination, but keep output silent
        const silentGain = this.audioContext.createGain();
        silentGain.gain.value = 0.0;
        this.processorNode.connect(silentGain);
        silentGain.connect(this.audioContext.destination);

        console.log(`🎤 Microphone started (gain=${this.micGain})`);
    }

    stop() {
        if (this.processorNode) {
            try { this.processorNode.disconnect(); } catch(e){}
            this.processorNode = null;
        }

        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
            this.stream = null;
        }

        if (this.audioContext) {
            try { this.audioContext.close(); } catch(e){}
            this.audioContext = null;
        }

        console.log("🛑 Microphone stopped");
    }
}
