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
    Heuristic to parse the content section from the LLM output.
    Extracts quotes, verses, thoughts - anything formatted as "Text" — Attribution
    """
    quotes = []
    lines = content_text.split('\n')
    capture = False
    
    for line in lines:
        # Start capturing when we see content section headers
        if any(keyword in line.lower() for keyword in ["contenido para postear", "frases destacadas", "quote cards", "contenido para"]):
            capture = True
            continue
        
        if capture:
            # Stop capturing on certain headers
            if any(keyword in line.lower() for keyword in ["caption", "post para redes", "instagram", "facebook"]):
                capture = False
                continue
            
            # Look for the format: "Text" — Attribution or - "Text" — Attribution
            # Match lines that have quotes and attribution
            match = re.search(r'["\"](.+?)["\"].*?[—\-–]\s*(.+)', line)
            if match:
                quote_text = match.group(1).strip()
                author_text = match.group(2).strip()
                if quote_text and len(quote_text) > 5:  # Filter very short matches
                    quotes.append({"text": quote_text, "author": author_text})
            else:
                # Fallback: Try simple dash separation
                cleaned = line.strip().strip('1234567890.- *')
                if cleaned and '—' in cleaned or ' - ' in cleaned:
                    parts = re.split(r'[—\-–]', cleaned)
                    if len(parts) >= 2:
                        quote_text = parts[0].strip(' "\'')
                        author_text = parts[-1].strip()
                        if quote_text and len(quote_text) > 10:
                            quotes.append({"text": quote_text, "author": author_text})
                
    return quotes  # No limit - generate all relevant visuals

def main():
    parser = argparse.ArgumentParser(description="Sermon/Debate Content Generator")
    parser.add_argument("--process", action="store_true", help="Process all files in recordings/")
    parser.add_argument("--type", choices=["sermon", "debate"], default="sermon", help="Type of content")
    parser.add_argument("--scripture", type=str, default="", help="Scripture reference for the day (e.g., 'Juan 3:16')")
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
            transcript = process_transcription_pipeline(cleaned_audio_path, hf_token)
            if not transcript:
                print("Transcription failed.")
                continue
                
            # 3. Generate Content
            content = process_content_generation(
                transcript, 
                hf_token, 
                content_type=args.type,
                scripture_reference=args.scripture
            )
            if not content:
                print("Content generation failed.")
                continue
            
            print("\nGenerated Content Preview:")
            print(content[:500] + "...\n")

            # 4. Render Visuals
            quotes = extract_quotes_from_text(content)
            print(f"Extracted {len(quotes)} items for rendering.")
            render_files = create_visual_assets(quotes, os.path.join(output_dir, "renders"))
            
            # 5. Archive
            archive_path = archive_project(
                input_path, 
                cleaned_audio_path, 
                transcript, 
                content, 
                render_files,
                content_type=args.type
            )
            print(f"Completed! Output saved to: {archive_path}")
            
            # Cleanup temp
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
