import os

# Server host and port
HOST = "127.0.0.1"
PORT = 8000

# Audio settings
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
FRAME_DURATION_MS = int(os.getenv("FRAME_DURATION_MS", "30"))
VAD_AGGRESSIVENESS = int(os.getenv("VAD_AGGRESSIVENESS", "3"))

# Faster-Whisper settings
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "1"))

# Streaming settings
AUDIO_BUFFER_MAX_SECONDS = float(os.getenv("AUDIO_BUFFER_MAX_SECONDS", "8"))
AUDIO_QUEUE_MAXSIZE = int(os.getenv("AUDIO_QUEUE_MAXSIZE", "256"))
RESULT_QUEUE_MAXSIZE = int(os.getenv("RESULT_QUEUE_MAXSIZE", "32"))

# Optional preprocessing
NOISE_SUPPRESSION_ENABLED = os.getenv("NOISE_SUPPRESSION_ENABLED", "false").lower() == "true"
NOISE_SUPPRESSION_PROVIDER = os.getenv("NOISE_SUPPRESSION_PROVIDER", "deepfilternet")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
