import re
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from config import WAV2VEC_MODEL_DIR, SAMPLE_RATE
import numpy as np
from spellchecker import SpellChecker

class Wav2VecASR:
    def __init__(self):
        # Load processor and model locally
        self.processor = Wav2Vec2Processor.from_pretrained(WAV2VEC_MODEL_DIR)
        self.model = Wav2Vec2ForCTC.from_pretrained(WAV2VEC_MODEL_DIR)
        self.model.eval()
        # Initialize a spell checker for lightweight postprocessing
        try:
            self.spell = SpellChecker()
        except Exception:
            self.spell = None

    def transcribe(self, float32_audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> str:
        """
        Transcribe a float32 numpy array audio segment into text.
        """
        # Convert float32 numpy array to torch tensor
        input_values = self.processor(float32_audio, sampling_rate=sample_rate, return_tensors="pt").input_values
        with torch.no_grad():
            logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0]
        transcription = transcription.lower()

        # Apply lightweight spell correction to reduce common ASR spelling errors
        if self.spell is not None:
            def _replace(match: re.Match) -> str:
                word = match.group(0)
                if word.isdigit():
                    return word
                # If word is already known, keep it
                if self.spell.known([word]):
                    return word
                corrected = self.spell.correction(word)
                return corrected if corrected is not None else word

            corrected_text = re.sub(r"\w+", _replace, transcription)
            return corrected_text

        return transcription
