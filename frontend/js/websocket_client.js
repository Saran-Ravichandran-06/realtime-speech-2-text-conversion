export class WebSocketClient {
    constructor(onTextReceived) {
        this.socket = null;
        this.onTextReceived = onTextReceived;
    }

    connect() {
        this.socket = new WebSocket("ws://127.0.0.1:8000/ws/audio");
        this.socket.binaryType = "arraybuffer";

        this.socket.onopen = () => {
            console.log("WebSocket connected");
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.text) {
                    this.onTextReceived(data.text);
                }
            } catch (e) {
                console.error("Invalid JSON", e);
            }
        };

        this.socket.onclose = () => {
            console.warn("WebSocket closed");
        };
    }

    sendAudio(float32Frame) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;

        // Convert Float32 → PCM16 bytes
        const pcm16 = new Int16Array(float32Frame.length);
        for (let i = 0; i < float32Frame.length; i++) {
            pcm16[i] = Math.max(-1, Math.min(1, float32Frame[i])) * 32767;
        }

        // SEND RAW BYTES (Important)
        this.socket.send(pcm16.buffer);
    }

    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
}
