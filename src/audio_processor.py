import os
import ffmpeg
import noisereduce as nr
import soundfile as sf
import numpy as np

def convert_to_wav(input_path, output_path, target_sr=16000):
    """
    Converts audio to WAV, 16kHz, mono using ffmpeg.
    """
    try:
        print(f"Converting {input_path} to {output_path}...")
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, ac=1, ar=target_sr, format='wav')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return output_path
    except ffmpeg.Error as e:
        print(f"Error converting {input_path}: {e}")
        return None

def clean_audio(audio_path, output_path):
    """
    Loads audio, performs noise reduction, and saves.
    """
    try:
        print(f"Cleaning audio {audio_path}...")
        data, rate = sf.read(audio_path)
        
        # Noise reduction
        # prop_decrease=0.75 is a safe default for voice
        reduced_noise = nr.reduce_noise(y=data, sr=rate, stationary=True, prop_decrease=0.75)

        sf.write(output_path, reduced_noise, rate)
        print(f"Saved cleaned audio to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error cleaning audio {audio_path}: {e}")
        return None

def process_audio_pipeline(input_path, output_dir):
    """
    Orchestrates the audio processing pipeline (Convert -> Clean).
    Returns path to the final cleaned audio file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Step 1: Convert to WAV (16kHz, mono)
    temp_wav = os.path.join(output_dir, f"temp_{base_name}.wav")
    if not convert_to_wav(input_path, temp_wav):
        return None

    # Step 2: Clean Audio
    final_wav = os.path.join(output_dir, f"cleaned_{base_name}.wav")
    result = clean_audio(temp_wav, final_wav)
    
    # Cleanup temp
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
        
    return result
