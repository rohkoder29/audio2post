import mlx_whisper
import torch
import torchaudio

# Monkey-patch torchaudio for speechbrain compatibility
if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: ["soundfile"]

from speechbrain.inference.speaker import EncoderClassifier
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import os
import tempfile
import soundfile as sf

def transcribe_audio(audio_path, model="mlx-community/whisper-large-v3-mlx"):
    """
    Transcribes audio using mlx-whisper.
    Returns segments with text and timestamps.
    """
    print(f"Transcribing {audio_path} with {model}...")
    result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=model)
    return result["segments"]

def compute_embeddings(audio_path, segments):
    """
    Computes speaker embeddings for each segment using SpeechBrain.
    """
    print("Computing speaker embeddings...")
    classifier = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        run_opts={"device": "cpu"} # Force CPU for safety, simple vector inference is fast enough
    )
    
    signal, fs = torchaudio.load(audio_path)
    
    embeddings = []
    valid_indices = []

    for i, seg in enumerate(segments):
        start = seg['start']
        end = seg['end']
        
        # Audio slicing (convert seconds to samples)
        start_sample = int(start * fs)
        end_sample = int(end * fs)
        
        # Ensure we have a valid duration
        if end_sample - start_sample < 160: # minimal samples for STFT
            continue
            
        segment_audio = signal[:, start_sample:end_sample]
        
        # Compute embedding
        # SpeechBrain expects [batch, time]
        embedding = classifier.encode_batch(segment_audio)
        # Flatten: [1, 1, 192] -> [192]
        emb_vector = embedding.squeeze().numpy()
        
        embeddings.append(emb_vector)
        valid_indices.append(i)
        
    return np.array(embeddings), valid_indices

def cluster_speakers(embeddings, n_speakers=None):
    """
    Clusters embeddings to find speakers.
    If n_speakers is None, uses a distance threshold.
    """
    print("Clustering speakers...")
    if len(embeddings) == 0:
        return []
    
    # Agglomerative Clustering is good for speaker diarization
    # threshold derived empirically for cosine distance in typical speaker spaces
    clustering = AgglomerativeClustering(
        n_clusters=n_speakers,
        metric="cosine",
        linkage="average",
        distance_threshold=0.3 if n_speakers is None else None
    )
    
    labels = clustering.fit_predict(embeddings)
    return labels

def process_transcription_pipeline(audio_path, hf_token=None, model="mlx-community/whisper-large-v3-mlx", num_speakers=None):
    """
    Runs transcription and diarization (SpeechBrain version).
    hf_token is kept for signature compatibility but not used for SB model (it's public).
    """
    # 1. Transcribe
    segments = transcribe_audio(audio_path, model=model)
    
    if not segments:
        return []
        
    # 2. Compute Embeddings
    embeddings, valid_indices = compute_embeddings(audio_path, segments)
    
    if len(embeddings) == 0:
        return segments # Return without speaker labels if embedding failed
        
    # 3. Cluster
    labels = cluster_speakers(embeddings, n_speakers=num_speakers)
    
    # 4. Assign labels back to segments
    for idx, label in zip(valid_indices, labels):
        segments[idx]['speaker'] = f"SPEAKER_{label:02d}"
        
    # Fill in missing (too short) segments with 'Unknown' or previous
    for seg in segments:
        if 'speaker' not in seg:
            seg['speaker'] = "UNKNOWN"
            
    return segments
