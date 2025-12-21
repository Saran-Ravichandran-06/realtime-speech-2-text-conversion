# scripts/test_ws_client.py
import asyncio
import soundfile as sf
import numpy as np
import websockets
from config import SAMPLE_RATE, FRAME_DURATION_MS

SERVER_WS = "ws://localhost:8000/ws/stream"

def chunk_pcm16_bytes(samples: np.ndarray, frame_samples: int):
    """Yield PCM16LE bytes frames from int16 numpy samples"""
    i = 0
    total = len(samples)
    while i + frame_samples <= total:
        frame = samples[i:i+frame_samples]
        yield frame.tobytes()
        i += frame_samples

async def send_wav(path):
    data, sr = sf.read(path, dtype='int16')
    # if stereo, convert to mono by averaging
    if len(data.shape) == 2:
        data = data.mean(axis=1).astype(np.int16)

    # if sample rate mismatches, user should pre-resample
    if sr != SAMPLE_RATE:
        raise RuntimeError(f"Test client expects {SAMPLE_RATE} Hz WAV. Found {sr} Hz.")

    frame_samples = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
    async with websockets.connect(SERVER_WS) as ws:
        for fb in chunk_pcm16_bytes(data, frame_samples):
            await ws.send(fb)
            # wait to receive any transcription messages (if any)
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
                print(">>", msg)
            except asyncio.TimeoutError:
                pass
        # close connection
        await ws.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_ws_client.py path_to_16k_mono_pcm16.wav")
        sys.exit(1)
    wav = sys.argv[1]
    asyncio.run(send_wav(wav))
