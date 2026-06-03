# Installation & Setup Guide

This guide explains how to run the real-time speech-to-text project locally.

## Prerequisites

- Python 3.10+
- Microphone access
- Windows, Linux, or macOS
- Optional: CUDA-capable GPU for faster inference

## Backend Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Faster-Whisper downloads the configured model automatically on first use. You
can choose a model with `WHISPER_MODEL_SIZE`, for example:

```bash
set WHISPER_MODEL_SIZE=small
```

Run the backend:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://127.0.0.1:8000`.

## Optional Noise Suppression

Noise suppression is disabled by default. To enable DeepFilterNet:

```bash
set NOISE_SUPPRESSION_ENABLED=true
set NOISE_SUPPRESSION_PROVIDER=deepfilternet
```

## Frontend Setup

Serve the frontend files:

```bash
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500` and allow microphone access when prompted.
