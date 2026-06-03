import { AudioCapture } from "./audio_capture.js";
import { Waveform } from "./waveform.js";
import { WebSocketClient } from "./websocket_client.js";

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const clearBtn = document.getElementById("clearBtn");
const canvas = document.getElementById("waveform");

const statusBadge = document.getElementById("statusBadge");
const activityText = document.getElementById("activityText");
const transcriptContainer = document.getElementById("transcriptContainer");
const finalTextElement = document.getElementById("finalText");
const partialTextElement = document.getElementById("partialText");
const statDuration = document.getElementById("statDuration");
const statWords = document.getElementById("statWords");

const waveform = canvas ? new Waveform(canvas) : null;

let audio = null;
let ws = null;
let sessionTimer = null;
let sessionSeconds = 0;
let isIntentionalStop = false;

function setStatus(status) {
    if (!statusBadge || !activityText || !startBtn || !stopBtn) return;
    
    // Do not override if user intentionally stopped
    if (isIntentionalStop && status === 'Disconnected') {
        return;
    }

    statusBadge.className = `badge ${status.toLowerCase()}`;
    statusBadge.textContent = status;
    
    if (status === 'Listening') {
        activityText.textContent = "Listening...";
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else if (status === 'Ready' || status === 'Disconnected') {
        activityText.textContent = status === 'Ready' ? "Waiting for speech..." : "Disconnected from server.";
        startBtn.disabled = false;
        stopBtn.disabled = true;
    } else if (status === 'Processing') {
        activityText.textContent = "Processing audio...";
    }
}

function updateStats() {
    if (!statDuration || !statWords || !finalTextElement) return;

    // Format duration
    const mins = Math.floor(sessionSeconds / 60).toString().padStart(2, '0');
    const secs = (sessionSeconds % 60).toString().padStart(2, '0');
    statDuration.textContent = `${mins}:${secs}`;
    
    // Calculate word count
    const text = finalTextElement.textContent.trim();
    statWords.textContent = text ? text.split(/\s+/).length : 0;
}

if (startBtn) {
    startBtn.onclick = async () => {
        isIntentionalStop = false;
        setStatus('Ready');
        
        ws = new WebSocketClient(onTextReceived, (status) => setStatus(status));
        ws.connect();

        audio = new AudioCapture((pcm) => {
            if (ws && ws.isConnected()) {
                ws.sendAudio(pcm);
            }
            if (waveform) waveform.draw(pcm);
        });

        await audio.start();
        
        // Start session timer
        sessionSeconds = 0;
        updateStats();
        sessionTimer = setInterval(() => {
            sessionSeconds++;
            updateStats();
        }, 1000);
        
        setStatus('Listening');
    };
}

if (stopBtn) {
    stopBtn.onclick = () => {
        isIntentionalStop = true;
        
        if (audio) {
            audio.stop();
            audio = null;
        }
        if (ws) {
            ws.close();
            ws = null;
        }
        
        if (sessionTimer) {
            clearInterval(sessionTimer);
            sessionTimer = null;
        }
        
        setStatus('Ready');
    };
}

function onTextReceived(data) {
    if (!data) return;
    
    if (data.text && finalTextElement) {
        // Finalized text
        finalTextElement.textContent += (finalTextElement.textContent ? " " : "") + data.text;
        if (partialTextElement) partialTextElement.textContent = ""; // Clear partial text since it's finalized
    } else if (data.partial && partialTextElement) {
        // Partial text
        partialTextElement.textContent = " " + data.partial;
    }
    
    updateStats();
    
    // Auto-scroll
    if (transcriptContainer) {
        transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
    }
}

if (copyBtn) {
    copyBtn.onclick = () => {
        const finalText = finalTextElement ? finalTextElement.textContent : "";
        const partialText = partialTextElement ? partialTextElement.textContent : "";
        const text = finalText + partialText;
        navigator.clipboard.writeText(text.trim()).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = "✅ Copied!";
            setTimeout(() => copyBtn.textContent = originalText, 2000);
        });
    };
}

if (downloadBtn) {
    downloadBtn.onclick = () => {
        const finalText = finalTextElement ? finalTextElement.textContent : "";
        const partialText = partialTextElement ? partialTextElement.textContent : "";
        const text = finalText + partialText;
        const blob = new Blob([text.trim()], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `transcript_${new Date().getTime()}.txt`;
        a.click();
    };
}

if (clearBtn) {
    clearBtn.onclick = () => {
        if (finalTextElement) finalTextElement.textContent = "";
        if (partialTextElement) partialTextElement.textContent = "";
        updateStats();
    };
}
