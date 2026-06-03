import asyncio
import os
import tempfile

import soundfile as sf
from fastapi import APIRouter, File, Request, UploadFile

from asr.audio_utils import resample_audio
from config import SAMPLE_RATE

router = APIRouter()


@router.post("/api/transcribe")
async def transcribe_file(request: Request, file: UploadFile = File(...)):
    contents = await file.read()

    suffix = os.path.splitext(file.filename or "")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        audio, sample_rate = sf.read(temp_path, dtype="float32")
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        audio_resampled = resample_audio(audio, sample_rate, SAMPLE_RATE)
        transcription = await asyncio.to_thread(
            request.app.state.transcriber.transcribe,
            audio_resampled,
            SAMPLE_RATE,
        )
        return {"text": transcription}
    finally:
        os.remove(temp_path)
