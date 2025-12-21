import soundfile as sf
from asr.vad import WebRTCVAD
from asr.audio_utils import float32_to_int16

vad = WebRTCVAD()

path = "sample.wav"

audio, sr = sf.read(path)

pcm16 = float32_to_int16(audio)

frame_length = 16000 // 100  # 10 ms

count = 0

for i in range(0, len(pcm16), frame_length):
    frame = pcm16[i:i+frame_length]
    if len(frame) < frame_length: break

    is_speech = vad.is_speech(frame.tobytes())
    print(f"Frame {count}: Speech={is_speech}")
    count += 1
