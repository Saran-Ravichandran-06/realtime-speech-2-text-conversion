import os
from fastapi import APIRouter, UploadFile, File
from asr.wav2vec_asr import Wav2VecASR
from asr.audio_utils import int16_to_float32, resample_audio
import soundfile as sf
import numpy as np
from config import SAMPLE_RATE

router = APIRouter()
_asr = Wav2VecASR()

@router.post("/api/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    contents = await file.read()
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    # Load audio as float32
    audio, sr = sf.read(temp_path, dtype='float32')
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)  # Convert to mono

    audio_resampled = resample_audio(audio, sr, SAMPLE_RATE)
    transcription = _asr.transcribe(audio_resampled, SAMPLE_RATE)

    os.remove(temp_path)
    return {"text": transcription}
