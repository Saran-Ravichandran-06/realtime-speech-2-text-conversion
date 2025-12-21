# scripts/convert_audio.py

import os
import argparse
import numpy as np
import soundfile as sf
import librosa

def convert_audio(input_path, output_path, sample_rate=16000):
    """
    Convert audio file to PCM16 WAV, mono, specified sample rate.
    """
    # Load audio with librosa
    y, sr = librosa.load(input_path, sr=sample_rate, mono=True)

    # Convert float32 in [-1,1] to int16
    y_int16 = np.int16(y * 32767)

    # Write PCM16 WAV
    sf.write(output_path, y_int16, sample_rate, subtype='PCM_16')
    print(f"Converted {input_path} -> {output_path} at {sample_rate} Hz, mono PCM16")

def main():
    parser = argparse.ArgumentParser(description="Convert audio to PCM16 WAV")
    parser.add_argument("input", help="Input audio file path")
    parser.add_argument("output", help="Output audio file path")
    parser.add_argument("--sr", type=int, default=16000, help="Target sample rate (default: 16000 Hz)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file {args.input} does not exist.")
        return

    convert_audio(args.input, args.output, args.sr)

if __name__ == "__main__":
    main()
