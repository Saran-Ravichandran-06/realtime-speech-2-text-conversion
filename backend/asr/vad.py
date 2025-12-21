import webrtcvad

class WebRTCVAD:
    def __init__(self, aggressiveness=3):
        # Use a more aggressive mode by default to reduce background/noise detection
        self.vad = webrtcvad.Vad(aggressiveness)

    def is_speech(self, pcm_bytes: bytes) -> bool:
        return self.vad.is_speech(pcm_bytes, sample_rate=16000)
