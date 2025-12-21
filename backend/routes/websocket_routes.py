import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from asr.vad import WebRTCVAD
from asr.segmenter import Segmenter
from asr.audio_utils import pcm16_bytes_to_np_int16, int16_to_float32
from asr.wav2vec_asr import Wav2VecASR
from config import SAMPLE_RATE

router = APIRouter()

# Initialize singletons
_vad = WebRTCVAD()
_segmenter = Segmenter()
_asr = Wav2VecASR()

@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected")

    try:
        while True:
            message = await websocket.receive()

            # Handle disconnect
            if message["type"] == "websocket.disconnect":
                break

            # Must read binary audio frames here
            data = message.get("bytes", None)
            if data is None:
                continue

            # Convert PCM16 bytes → int16 numpy
            int16 = pcm16_bytes_to_np_int16(data)

            # VAD
            is_speech = _vad.is_speech(data)

            # Segmenter
            segment = _segmenter.append_frame(int16, is_speech=is_speech)

            if segment is not None and segment.size > 0:
                float32 = int16_to_float32(segment)

                transcription = await asyncio.to_thread(
                    _asr.transcribe, float32, SAMPLE_RATE
                )

                await websocket.send_json({"text": transcription})

    except WebSocketDisconnect:
        print("WebSocket client disconnected")

        seg = _segmenter.force_flush()
        if seg is not None and seg.size > 0:
            float32 = int16_to_float32(seg)
            transcription = await asyncio.to_thread(
                _asr.transcribe, float32, SAMPLE_RATE
            )
            print("Final transcription:", transcription)

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        await websocket.close()
        print("Connection closed")
