import logging
from abc import ABC, abstractmethod

import numpy as np

from asr.audio_utils import float32_to_int16, int16_to_float32, pcm16_bytes_to_np_int16
from config import NOISE_SUPPRESSION_ENABLED, NOISE_SUPPRESSION_PROVIDER, SAMPLE_RATE

logger = logging.getLogger(__name__)


class NoiseSuppressor(ABC):
    @abstractmethod
    def process_frame(self, pcm_bytes: bytes) -> bytes:
        raise NotImplementedError


class PassthroughNoiseSuppressor(NoiseSuppressor):
    def process_frame(self, pcm_bytes: bytes) -> bytes:
        return pcm_bytes


class DeepFilterNetNoiseSuppressor(NoiseSuppressor):
    """
    Optional DeepFilterNet adapter.

    DeepFilterNet is loaded lazily and only when explicitly enabled because it is
    heavier than the rest of the streaming path.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        try:
            import torch
            from df import enhance, init_df
        except Exception as exc:
            raise RuntimeError("DeepFilterNet is not installed or could not be imported") from exc

        self.torch = torch
        self.enhance = enhance
        self.model, self.df_state, _ = init_df()
        self.sample_rate = sample_rate

    def process_frame(self, pcm_bytes: bytes) -> bytes:
        int16 = pcm16_bytes_to_np_int16(pcm_bytes)
        audio = int16_to_float32(int16)

        with self.torch.no_grad():
            tensor = self.torch.from_numpy(audio).float().unsqueeze(0)
            enhanced = self.enhance(self.model, self.df_state, tensor)

        enhanced_np = enhanced.squeeze(0).detach().cpu().numpy().astype(np.float32)
        return float32_to_int16(enhanced_np).tobytes()


def create_noise_suppressor(
    enabled: bool = NOISE_SUPPRESSION_ENABLED,
    provider: str = NOISE_SUPPRESSION_PROVIDER,
) -> NoiseSuppressor:
    if not enabled:
        return PassthroughNoiseSuppressor()

    normalized_provider = provider.lower()
    if normalized_provider == "deepfilternet":
        try:
            return DeepFilterNetNoiseSuppressor()
        except RuntimeError:
            logger.exception("Noise suppression requested but unavailable; using passthrough")
            return PassthroughNoiseSuppressor()

    logger.warning("Unknown noise suppression provider '%s'; using passthrough", provider)
    return PassthroughNoiseSuppressor()
