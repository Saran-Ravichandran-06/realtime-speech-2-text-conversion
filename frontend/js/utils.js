// frontend/js/utils.js

// Download text content as a file
export function downloadText(filename, text) {
    const element = document.createElement("a");
    const blob = new Blob([text], { type: "text/plain" });
    element.href = URL.createObjectURL(blob);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Simple sleep / delay function
export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Convert Float32Array to PCM16 ArrayBuffer (if needed globally)
export function floatTo16BitPCM(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < float32Array.length; i++, offset += 2) {
        let s = Math.max(-1, Math.min(1, float32Array[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return buffer;
}
