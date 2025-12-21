import { AudioCapture } from "./audio_capture.js";
import { Waveform } from "./waveform.js";
import { WebSocketClient } from "./websocket_client.js";

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const transcriptBox = document.getElementById("transcript");
const downloadBtn = document.getElementById("downloadBtn");
const canvas = document.getElementById("waveform");

const waveform = new Waveform(canvas);

let audio = null;
let ws = null;

startBtn.onclick = async () => {
    ws = new WebSocketClient(onTextReceived);
    ws.connect();

    audio = new AudioCapture((pcm) => {
        ws.sendAudio(pcm);
        waveform.draw(pcm);
    });

    await audio.start();
};

stopBtn.onclick = () => {
    if (audio) audio.stop();
    if (ws) ws.close();
};

function onTextReceived(text) {
    transcriptBox.value += text + " ";
}

downloadBtn.onclick = () => {
    const blob = new Blob([transcriptBox.value], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "transcript.txt";
    a.click();
};
