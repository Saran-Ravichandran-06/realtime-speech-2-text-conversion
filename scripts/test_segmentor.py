import soundfile as sf
from asr.segmenter import Segmenter
from asr.audio_utils import float32_to_int16
from asr.vad import WebRTCVAD

vad = WebRTCVAD()
segmenter = Segmenter()

audio, sr = sf.read("sample.wav")

pcm16 = float32_to_int16(audio)

frame_length = sr // 100

segments = []

for i in range(0, len(pcm16), frame_length):
    frame = pcm16[i:i+frame_length]
    if len(frame) < frame_length:
        break

    is_speech = vad.is_speech(frame.tobytes())
    seg = segmenter.append_frame(frame, is_speech)

    if seg is not None and seg.size > 0:
        segments.append(seg)

print(f"Generated {len(segments)} segments")
