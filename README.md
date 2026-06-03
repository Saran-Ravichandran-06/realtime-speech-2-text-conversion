# Real-Time Speech-to-Text Conversion

A full-stack real-time speech-to-text web application built with FastAPI,
WebSockets, WebRTC VAD, and Faster-Whisper. The browser captures microphone
audio, streams PCM16 frames to the backend, and receives live transcript updates
without changing the existing frontend WebSocket protocol.

## Features

- Real-time microphone audio capture with AudioWorklet
- PCM16 audio streaming over WebSockets
- Producer-consumer backend using asyncio queues
- Configurable audio ring buffer to reduce frame loss during inference delays
- Optional DeepFilterNet noise suppression before VAD and transcription
- WebRTC VAD speech detection
- Faster-Whisper transcription with CUDA when available and CPU fallback
- File upload transcription endpoint

## Backend Flow

```text
WebSocket Receiver
-> Audio Queue / Ring Buffer
-> Noise Suppression
-> WebRTC VAD
-> Chunk Manager
-> Faster-Whisper
-> Result Queue
-> WebSocket Sender
```

## Configuration

Settings are read from environment variables:

- `WHISPER_MODEL_SIZE`: Faster-Whisper model name or local path. Default: `base`
- `WHISPER_DEVICE`: `auto`, `cuda`, or `cpu`. Default: `auto`
- `WHISPER_COMPUTE_TYPE`: `auto`, `float16`, `int8`, etc. Default: `auto`
- `WHISPER_LANGUAGE`: language hint. Default: `en`
- `WHISPER_BEAM_SIZE`: decoding beam size. Default: `1`
- `AUDIO_BUFFER_MAX_SECONDS`: ring buffer capacity per socket. Default: `8`
- `AUDIO_QUEUE_MAXSIZE`: inbound frame queue size per socket. Default: `256`
- `RESULT_QUEUE_MAXSIZE`: outbound result queue size per socket. Default: `32`
- `NOISE_SUPPRESSION_ENABLED`: enable optional suppressor. Default: `false`
- `NOISE_SUPPRESSION_PROVIDER`: currently `deepfilternet`. Default: `deepfilternet`

## Running

Install dependencies, then start the backend from the `backend` directory:

```bash
pip install -r requirements.txt
cd backend
python main.py
```

Open `frontend/index.html` with a local static server and connect to
`ws://127.0.0.1:8000/ws/audio`.
