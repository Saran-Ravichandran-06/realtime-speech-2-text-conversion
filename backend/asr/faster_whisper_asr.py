import logging
from typing import Optional

import ctranslate2
import numpy as np
from faster_whisper import WhisperModel

from config import (
    SAMPLE_RATE,
    WHISPER_BEAM_SIZE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_LANGUAGE,
    WHISPER_MODEL_SIZE,
)

logger = logging.getLogger(__name__)


class FasterWhisperTranscriber:
    """
    Reusable Faster-Whisper transcription service.

    The model is intentionally loaded once and shared by request handlers. Per-user
    streaming state lives outside this class.
    """

    def __init__(
        self,
        model_size: str = WHISPER_MODEL_SIZE,
        device: str = WHISPER_DEVICE,
        compute_type: str = WHISPER_COMPUTE_TYPE,
        language: Optional[str] = WHISPER_LANGUAGE,
        beam_size: int = WHISPER_BEAM_SIZE,
    ):
        self.device = self._resolve_device(device)
        self.compute_type = self._resolve_compute_type(compute_type, self.device)
        self.language = language or None
        self.beam_size = beam_size

        logger.info(
            "Loading Faster-Whisper model '%s' on %s with compute_type=%s",
            model_size,
            self.device,
            self.compute_type,
        )
        self.model = WhisperModel(
            model_size,
            device=self.device,
            compute_type=self.compute_type,
        )

    def transcribe(self, float32_audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> str:
        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"Expected {SAMPLE_RATE} Hz audio, got {sample_rate} Hz")

        if float32_audio.size == 0:
            return ""

        audio = np.asarray(float32_audio, dtype=np.float32)
        segments, _ = self.model.transcribe(
            audio,
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=False,
            condition_on_previous_text=False,
        )
        return " ".join(segment.text.strip() for segment in segments).strip()

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device != "auto":
            return device

        try:
            return "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            logger.exception("Unable to inspect CUDA availability; falling back to CPU")
            return "cpu"

    @staticmethod
    def _resolve_compute_type(compute_type: str, device: str) -> str:
        if compute_type != "auto":
            return compute_type
        return "float16" if device == "cuda" else "int8"
