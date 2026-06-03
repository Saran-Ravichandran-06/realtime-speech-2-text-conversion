import soundfile as sf

from asr.audio_utils import float32_to_int16, int16_to_float32
from asr.faster_whisper_asr import FasterWhisperTranscriber

print("Loading model...")
asr = FasterWhisperTranscriber()

path = "long_audio.wav"
audio, sr = sf.read(path, dtype="float32")

pcm16 = float32_to_int16(audio)
audio_float = int16_to_float32(pcm16)

print("Transcribing...")
text = asr.transcribe(audio_float, sr)

print("\n=== TRANSCRIPTION ===\n")
print(text)
