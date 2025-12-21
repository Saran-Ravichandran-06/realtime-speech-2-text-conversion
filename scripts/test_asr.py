import soundfile as sf
from asr.wav2vec_asr import Wav2VecASR

asr = Wav2VecASR()

path = "sample.wav"   # put any wav file here

audio, sr = sf.read(path)

print(f"Loaded audio: {audio.shape}, SR={sr}")

text = asr.transcribe(audio, sr)

print("\n=== TRANSCRIPTION ===")
print(text)
