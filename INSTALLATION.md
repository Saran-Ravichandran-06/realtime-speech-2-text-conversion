# ⚙️ Installation & Setup Guide

This guide explains how to set up and run the **Real-Time Speech-to-Text Conversion** project locally.

---

## ✅ Prerequisites

- Python **3.10+**
- Node-free (pure JS frontend)
- Microphone access
- Windows / Linux / macOS

---

## 📥 Clone Repository

git clone https://github.com/Saran-Ravichandran-06/realtime-speech-2-text-conversion.git
cd realtime-speech-2-text-conversion

---

## 🐍 Backend Setup

1. Create Virtual Environment
- python -m venv venv
- venv\Scripts\activate


2. Install Dependencies
- pip install -r requirements.txt

3. Download Wav2Vec2 Model
Download from Hugging Face and place inside:
- backend/models/wav2vec/

Recommended model:
- facebook/wav2vec2-base-960h

4. Run Backend Server
- cd backend
- uvicorn main:app --reload --host 0.0.0.0 --port 8000


Backend will be available at:
- http://127.0.0.1:8000

---

## 🌐 Frontend Setup
1. Serve Frontend Files
- cd frontend
- python -m http.server 5500

2. Open in Browser
- http://127.0.0.1:5500

Allow microphone access when prompted.