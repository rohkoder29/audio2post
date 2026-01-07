import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Sermon/Debate Content Generator")
    parser.add_argument("--process", action="store_true", help="Process all files in recordings/")
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
        # TODO: Implement processing loop
        # 1. Scan recordings/
        # 2. For each file:
        #    - Audio Clean
        #    - Transcribe & Diarize
        #    - Generate Content
        #    - Render Visuals
        #    - Archive
        pass
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
