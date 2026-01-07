import os
import shutil
import argparse
import re
from dotenv import load_dotenv
from src.audio_processor import process_audio_pipeline
from src.transcriber import process_transcription_pipeline
from src.content_generator import process_content_generation
from src.renderer import create_visual_assets
from src.archiver import archive_project

# Load environment variables
load_dotenv()

def extract_quotes_from_text(content_text):
    """
    Heuristic to parse the "Quote Card" section from the LLM output.
    Looks for lines starting with "- " or numbers in a "Quote Card" section.
    """
    quotes = []
    lines = content_text.split('\n')
    capture = False
    
    for line in lines:
        if "candidatos" in line.lower() or "frases destacadas" in line.lower() or "quote cards" in line.lower():
            capture = True
            continue
        
        if capture:
            if line.strip() == "" or "caption" in line.lower() or "post" in line.lower():
                capture = False
                continue
            
            # Simple regex to extract quote content
            # Matches: 1. "Quote" - Author OR - "Quote" - Author
            cleaned = line.strip().strip('1234567890.- ')
            if cleaned:
                # Naive split for author if present (usually separated by - or —)
                parts = re.split(r'[-—]', cleaned)
                if len(parts) >= 2:
                    quote_text = parts[0].strip(' "')
                    author_text = parts[-1].strip()
                else:
                    quote_text = cleaned.strip(' "')
                    author_text = "IEMA" # Default author
                
                quotes.append({"text": quote_text, "author": author_text})
                
    return quotes[:3] # Limit to 3

def main():
    parser = argparse.ArgumentParser(description="Sermon/Debate Content Generator")
    parser.add_argument("--process", action="store_true", help="Process all files in recordings/")
    parser.add_argument("--type", choices=["sermon", "debate"], default="sermon", help="Type of content")
    args = parser.parse_args()

    # Check for HF Token
    hf_token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    if not hf_token:
        print("Error: HUGGINGFACE_API_KEY or HF_TOKEN not found in environment variables.")
        return

    # Check directories
    recordings_dir = os.path.join(os.getcwd(), "recordings")
    if not os.path.exists(recordings_dir):
        print(f"Error: Recordings directory not found at {recordings_dir}")
        return

    if args.process:
        print("Starting processing pipeline...")
        files = [f for f in os.listdir(recordings_dir) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        
        if not files:
            print("No audio files found in recordings/")
            return

        for filename in files:
            input_path = os.path.join(recordings_dir, filename)
            print(f"\nProcessing {filename}...")
            
            # 1. Clean Audio
            output_dir = os.path.join(os.getcwd(), "processed_temp")
            cleaned_audio_path = process_audio_pipeline(input_path, output_dir)
            if not cleaned_audio_path:
                print("Audio processing failed.")
                continue

            # 2. Transcribe & Diarize
            # Note: We use the cleaned audio for transcription
            transcript = process_transcription_pipeline(cleaned_audio_path, hf_token)
            if not transcript:
                print("Transcription failed.")
                continue
                
            # 3. Generate Content
            content = process_content_generation(transcript, hf_token, content_type=args.type)
            if not content:
                print("Content generation failed.")
                continue
            
            print("\nGenerated Content Preview:")
            print(content[:500] + "...\n")

            # 4. Render Visuals
            quotes = extract_quotes_from_text(content)
            print(f"Extracted {len(quotes)} quotes for rendering.")
            render_files = create_visual_assets(quotes, os.path.join(output_dir, "renders"))
            
            # 5. Archive
            archive_path = archive_project(input_path, cleaned_audio_path, transcript, content, render_files)
            print(f"Completed! Output saved to: {archive_path}")
            
            # Cleanup temp
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
