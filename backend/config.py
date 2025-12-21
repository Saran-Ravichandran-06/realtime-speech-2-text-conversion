import os

# Server host and port
HOST = "127.0.0.1"
PORT = 8000

# Audio settings
SAMPLE_RATE = 16000          # Sample rate expected by Wav2Vec2
FRAME_DURATION_MS = 30       # Audio frame duration for VAD

# Model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WAV2VEC_MODEL_DIR = os.path.join(BASE_DIR, "models/wav2vec")
