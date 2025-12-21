import numpy as np
import librosa

def pcm16_bytes_to_np_int16(pcm_bytes: bytes) -> np.ndarray:
    return np.frombuffer(pcm_bytes, dtype=np.int16)

def int16_to_float32(int16: np.ndarray) -> np.ndarray:
    return int16.astype(np.float32) / 32768.0

def resample_audio(float32_audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return float32_audio
    return librosa.resample(float32_audio, orig_sr=orig_sr, target_sr=target_sr)
