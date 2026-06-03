import webrtcvad
from config import SAMPLE_RATE, VAD_AGGRESSIVENESS

class WebRTCVAD:
    def __init__(self, aggressiveness=VAD_AGGRESSIVENESS, sample_rate=SAMPLE_RATE):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate

    def is_speech(self, pcm_bytes: bytes) -> bool:
        return self.vad.is_speech(pcm_bytes, sample_rate=self.sample_rate)
