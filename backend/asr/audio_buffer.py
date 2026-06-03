import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional

from config import AUDIO_BUFFER_MAX_SECONDS, AUDIO_QUEUE_MAXSIZE, SAMPLE_RATE

BYTES_PER_SAMPLE = 2


@dataclass(frozen=True)
class BufferStats:
    bytes_buffered: int
    frames_buffered: int
    frames_dropped: int


class AudioRingBuffer:
    """Fixed-size PCM16 ring buffer used to absorb short processing delays."""

    def __init__(self, max_seconds: float = AUDIO_BUFFER_MAX_SECONDS, sample_rate: int = SAMPLE_RATE):
        self.max_bytes = max(1, int(max_seconds * sample_rate * BYTES_PER_SAMPLE))
        self._frames: Deque[bytes] = deque()
        self._bytes_buffered = 0
        self._frames_dropped = 0

    def append(self, frame: bytes) -> None:
        self._frames.append(frame)
        self._bytes_buffered += len(frame)

        while self._bytes_buffered > self.max_bytes and self._frames:
            dropped = self._frames.popleft()
            self._bytes_buffered -= len(dropped)
            self._frames_dropped += 1

    def stats(self) -> BufferStats:
        return BufferStats(
            bytes_buffered=self._bytes_buffered,
            frames_buffered=len(self._frames),
            frames_dropped=self._frames_dropped,
        )


class BufferedAudioQueue:
    """
    Non-blocking producer queue backed by a ring buffer.

    If the worker falls behind, the oldest queued frame is dropped before new
    audio is accepted so WebSocket receive stays responsive.
    """

    def __init__(
        self,
        max_seconds: float = AUDIO_BUFFER_MAX_SECONDS,
        queue_maxsize: int = AUDIO_QUEUE_MAXSIZE,
        sample_rate: int = SAMPLE_RATE,
    ):
        self.ring_buffer = AudioRingBuffer(max_seconds=max_seconds, sample_rate=sample_rate)
        self.queue: asyncio.Queue[Optional[bytes]] = asyncio.Queue(maxsize=queue_maxsize)

    def put_nowait(self, frame: bytes) -> None:
        self.ring_buffer.append(frame)

        if self.queue.full():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except asyncio.QueueEmpty:
                pass

        self.queue.put_nowait(frame)

    def put_stop_nowait(self) -> None:
        if self.queue.full():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except asyncio.QueueEmpty:
                pass
        self.queue.put_nowait(None)

    async def get(self) -> Optional[bytes]:
        return await self.queue.get()

    def task_done(self) -> None:
        self.queue.task_done()

    def stats(self) -> BufferStats:
        return self.ring_buffer.stats()
