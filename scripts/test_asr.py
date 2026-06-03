import soundfile as sf
from asr.faster_whisper_asr import FasterWhisperTranscriber

asr = FasterWhisperTranscriber()

path = "sample.wav"   # put any wav file here

audio, sr = sf.read(path)

print(f"Loaded audio: {audio.shape}, SR={sr}")

text = asr.transcribe(audio, sr)

print("\n=== TRANSCRIPTION ===")
print(text)
