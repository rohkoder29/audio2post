import os
import shutil
from datetime import datetime
import json
import re

def parse_date_from_filename(filename):
    """
    Extracts date from filename. Last 6 chars before extension are DDMMYY.
    e.g., 'domingo040125.m4a' -> '04-01-25' -> '2025-01-04'
    """
    base = os.path.splitext(filename)[0]
    if len(base) >= 6:
        date_str = base[-6:]  # Last 6 characters
        try:
            day = int(date_str[0:2])
            month = int(date_str[2:4])
            year = int(date_str[4:6]) + 2000  # Assume 20xx
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    # Fallback to today's date
    return datetime.now().strftime("%Y-%m-%d")

def transcript_to_text(transcript_data, conversational=False):
    """
    Converts transcript data to plain text.
    If conversational=True (for debates), formats with speaker labels.
    """
    lines = []
    current_speaker = None
    
    for seg in transcript_data:
        speaker = seg.get('speaker', 'Unknown')
        text = seg.get('text', '').strip()
        
        if conversational:
            if speaker != current_speaker:
                lines.append(f"\n{speaker}:")
                current_speaker = speaker
            lines.append(f"  {text}")
        else:
            lines.append(text)
    
    return "\n".join(lines)

def archive_project(original_audio, cleaned_audio, transcript_data, generated_content, render_files, content_type="sermon"):
    """
    Moves all assets to an archive folder.
    Uses date from filename instead of current date.
    """
    filename = os.path.basename(original_audio)
    date_str = parse_date_from_filename(filename)
    
    archive_path = os.path.join(os.getcwd(), "archives", date_str)
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        
    print(f"Archiving to {archive_path}...")
    
    # 1. Copy Audios
    shutil.copy2(original_audio, archive_path)
    if cleaned_audio and os.path.exists(cleaned_audio):
        shutil.move(cleaned_audio, os.path.join(archive_path, "cleaned_audio.wav"))
        
    # 2. Save Transcript as JSON
    with open(os.path.join(archive_path, "transcript.json"), "w") as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    # 3. Save Transcript as .txt
    is_debate = content_type == "debate"
    txt_content = transcript_to_text(transcript_data, conversational=is_debate)
    txt_filename = "debate_transcript.txt" if is_debate else "sermon_transcript.txt"
    with open(os.path.join(archive_path, txt_filename), "w") as f:
        f.write(txt_content)
        
    # 4. Save Content Generation Output
    with open(os.path.join(archive_path, "social_media_content.md"), "w") as f:
        f.write(generated_content if generated_content else "Generation Failed")
        
    # 5. Move Renders
    renders_dir = os.path.join(archive_path, "visuals")
    if not os.path.exists(renders_dir):
        os.makedirs(renders_dir)
        
    for render in render_files:
        shutil.move(render, renders_dir)
        
    print("Archival complete.")
    return archive_path
