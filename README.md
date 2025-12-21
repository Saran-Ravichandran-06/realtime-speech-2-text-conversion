# 🎙️ Real-Time Speech-to-Text Conversion

A full-stack **real-time speech-to-text (STT) web application** built using **FastAPI, WebSockets, and Wav2Vec2**.  
The system captures microphone audio from the browser, streams it to a backend server, and returns **live transcriptions** with low latency.

---

## 🚀 Features

- 🎧 Real-time microphone audio capture (browser)
- 🔁 Audio streaming using WebSockets
- 🧠 Speech recognition using **Wav2Vec2**
- 🔇 Voice Activity Detection (WebRTC VAD)
- ⚡ Low-latency streaming transcription
- 🌙 Modern dark-themed frontend UI
- 📄 Transcript download support

---

## 🏗️ Tech Stack

### Frontend
- HTML5
- CSS3 (Dark theme)
- JavaScript (AudioWorklet, WebSocket API)

### Backend
- Python 3.10+
- FastAPI
- WebSockets
- Wav2Vec2 (Hugging Face)
- WebRTC VAD
- NumPy, Torch

## 🔌 How It Works

1. Browser captures microphone audio using `AudioWorklet`
2. Audio is converted to **PCM16**
3. Audio frames are streamed to backend via **WebSocket**
4. Backend applies:
   - Voice Activity Detection
   - Audio segmentation
   - Wav2Vec2 transcription
5. Transcribed text is streamed back to frontend in real-time

---

## 🧪 Example Use Cases

- Live meeting transcription
- Interview recording
- Voice-controlled applications
- Accessibility tools
- Research & ML demos

---

## 📌 Limitations

- No speaker diarization
- Background noise may affect accuracy
- Requires stable microphone input