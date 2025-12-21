import soundfile as sf
from asr.wav2vec_asr import Wav2VecASR
from asr.audio_utils import int16_to_float32, float32_to_int16

print("Loading model…")
asr = Wav2VecASR()

path = "long_audio.wav"
audio, sr = sf.read(path)

pcm16 = float32_to_int16(audio)
audio_float = int16_to_float32(pcm16)

print("Transcribing…")
text = asr.transcribe(audio_float, sr)

print("\n=== TRANSCRIPTION ===\n")
print(text)
