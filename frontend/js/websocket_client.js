export class WebSocketClient {
    constructor(onTextReceived, onStatusChange) {
        this.socket = null;
        this.onTextReceived = onTextReceived;
        this.onStatusChange = onStatusChange;
    }

    connect() {
        this.socket = new WebSocket("ws://127.0.0.1:8000/ws/audio");
        this.socket.binaryType = "arraybuffer";

        this.socket.onopen = () => {
            console.log("WebSocket connected");
            if (this.onStatusChange) this.onStatusChange("Listening");
        };

        this.socket.onmessage = (event) => {
            try {
                if (!event.data) return;
                const data = JSON.parse(event.data);
                // Pass the whole data object to distinguish partial vs text
                if (data && typeof data === 'object') {
                    this.onTextReceived(data);
                }
            } catch (e) {
                console.error("Invalid JSON or data structure", e);
            }
        };

        this.socket.onclose = () => {
            console.warn("WebSocket closed");
            if (this.onStatusChange) this.onStatusChange("Disconnected");
        };
    }

    sendAudio(float32Frame) {
        if (!this.isConnected()) return;

        // Convert Float32 → PCM16 bytes
        const pcm16 = new Int16Array(float32Frame.length);
        for (let i = 0; i < float32Frame.length; i++) {
            pcm16[i] = Math.max(-1, Math.min(1, float32Frame[i])) * 32767;
        }

        // SEND RAW BYTES (Important)
        this.socket.send(pcm16.buffer);
    }
    
    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN;
    }

    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
}
