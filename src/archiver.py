import os
import shutil
from datetime import datetime
import json
import re

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text).strip('-')

def archive_project(original_audio, cleaned_audio, transcript_data, generated_content, render_files):
    """
    Moves all assets to an archive folder.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Try to get a slug from the summary or audio filename
    slug = slugify(os.path.basename(original_audio).split('.')[0])
    
    archive_path = os.path.join(os.getcwd(), "archives", f"{date_str}_{slug}")
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        
    print(f"Archiving to {archive_path}...")
    
    # 1. Copy Audios
    shutil.copy2(original_audio, archive_path)
    if cleaned_audio and os.path.exists(cleaned_audio):
        shutil.move(cleaned_audio, os.path.join(archive_path, "cleaned_audio.wav"))
        
    # 2. Save Transcript
    with open(os.path.join(archive_path, "transcript.json"), "w") as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
    # 3. Save Content Generation Output
    with open(os.path.join(archive_path, "social_media_content.md"), "w") as f:
        f.write(generated_content if generated_content else "Generation Failed")
        
    # 4. Move Renders
    renders_dir = os.path.join(archive_path, "visuals")
    if not os.path.exists(renders_dir):
        os.makedirs(renders_dir)
        
    for render in render_files:
        shutil.move(render, renders_dir)
        
    print("Archival complete.")
    return archive_path
