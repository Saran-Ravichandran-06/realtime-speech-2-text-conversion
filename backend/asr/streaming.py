import asyncio
import contextlib
import logging
from typing import Optional

from asr.audio_buffer import BufferedAudioQueue, BufferStats
from asr.audio_utils import int16_to_float32, pcm16_bytes_to_np_int16
from asr.faster_whisper_asr import FasterWhisperTranscriber
from asr.noise_suppression import NoiseSuppressor, create_noise_suppressor
from asr.segmenter import Segmenter
from asr.vad import WebRTCVAD
from config import RESULT_QUEUE_MAXSIZE, SAMPLE_RATE

logger = logging.getLogger(__name__)


class TranscriptionWorker:
    """
    Per-connection producer-consumer pipeline.

    The WebSocket receiver only enqueues frames. This worker owns preprocessing,
    VAD, speech chunking, and model calls, then publishes transcript messages to
    the result queue for the sender task.
    """

    def __init__(
        self,
        transcriber: FasterWhisperTranscriber,
        audio_queue: Optional[BufferedAudioQueue] = None,
        result_queue_maxsize: int = RESULT_QUEUE_MAXSIZE,
        noise_suppressor: Optional[NoiseSuppressor] = None,
    ):
        self.transcriber = transcriber
        self.audio_queue = audio_queue or BufferedAudioQueue()
        self.result_queue: asyncio.Queue[Optional[dict]] = asyncio.Queue(maxsize=result_queue_maxsize)
        self.noise_suppressor = noise_suppressor or create_noise_suppressor()
        self.vad = WebRTCVAD()
        self.segmenter = Segmenter()
        self._task: Optional[asyncio.Task] = None
        self._closed = False

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="transcription-worker")

    def enqueue_audio(self, pcm_bytes: bytes) -> None:
        if self._closed:
            return
        self.audio_queue.put_nowait(pcm_bytes)

    async def stop(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.audio_queue.put_stop_nowait()

        if self._task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        await self._publish_stop()

    def buffer_stats(self) -> BufferStats:
        return self.audio_queue.stats()

    async def _run(self) -> None:
        try:
            while True:
                pcm_bytes = await self.audio_queue.get()
                try:
                    if pcm_bytes is None:
                        await self._flush_segment()
                        return

                    processed = self.noise_suppressor.process_frame(pcm_bytes)
                    is_speech = self.vad.is_speech(processed)
                    frame = pcm16_bytes_to_np_int16(processed)
                    segment = self.segmenter.append_frame(frame, is_speech=is_speech)

                    if segment is not None and segment.size > 0:
                        await self._transcribe_segment(segment)
                finally:
                    self.audio_queue.task_done()
        except Exception:
            logger.exception("Transcription worker failed")
            await self._publish({"error": "Transcription worker failed"})
            await self._publish_stop()

    async def _flush_segment(self) -> None:
        segment = self.segmenter.force_flush()
        if segment is not None and segment.size > 0:
            await self._transcribe_segment(segment)

    async def _transcribe_segment(self, segment) -> None:
        import time
        duration = len(segment) / SAMPLE_RATE
        logger.info("Processing speech segment of duration %.2fs", duration)
        
        audio = int16_to_float32(segment)
        start_time = time.time()
        text = await asyncio.to_thread(self.transcriber.transcribe, audio, SAMPLE_RATE)
        latency = time.time() - start_time
        
        if text:
            rtf = latency / duration if duration > 0 else 0
            logger.info("Transcription completed in %.2fs (RTF: %.2f)", latency, rtf)
            await self._publish({"text": text})

    async def _publish(self, message: dict) -> None:
        if self.result_queue.full():
            try:
                self.result_queue.get_nowait()
                self.result_queue.task_done()
            except asyncio.QueueEmpty:
                pass
        await self.result_queue.put(message)

    async def _publish_stop(self) -> None:
        if self.result_queue.full():
            try:
                self.result_queue.get_nowait()
                self.result_queue.task_done()
            except asyncio.QueueEmpty:
                pass
        await self.result_queue.put(None)
