from huggingface_hub import InferenceClient
import os
import json

def get_inference_client(api_key):
    return InferenceClient(token=api_key)

def generate_text(client, prompt, model="Qwen/Qwen2.5-72B-Instruct"):
    """
    Generates text using HF Inference API.
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(messages, model=model, max_tokens=1000)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Generation failed: {e}")
        return None

def create_sermon_prompt(transcript_text):
    return f"""
    You are a social media manager for a church. Analyze the following sermon transcript and generate:
    1. A concise summary (2 sentences).
    2. A list of 5 key takeaways (bullet points).
    3. Three "Quote Card" candidates. Each must be a powerful, standalone quote from the text, less than 20 words, attributed to the speaker.
    4. A Facebook post caption promoting this sermon (engaging, using emojis).

    Transcript:
    {transcript_text[:15000]} 
    """ # Truncate to avoid context limit issues on free tier

def create_debate_prompt(transcript_text):
    return f"""
    You are a content creator analyzing a theological debate. Analyze the following transcript and generate:
    1. A summary of the central conflict/topic.
    2. "Point vs Counter-point" analysis (3 key arguments).
    3. Three "Quote Card" candidates (one from each side if possible).
    4. A neutral, engaging social media post asking the audience for their thoughts.

    Transcript:
    {transcript_text[:15000]}
    """

def process_content_generation(transcript_data, hf_token, content_type="sermon"):
    """
    Orchestrates content generation.
    transcript_data: list of segments [{'text':..., 'speaker':...}, ...]
    """
    client = get_inference_client(hf_token)
    
    # Combine text
    full_text = " ".join([f"{seg['speaker']}: {seg['text']}" for seg in transcript_data])
    
    if content_type == "debate":
        prompt = create_debate_prompt(full_text)
    else:
        prompt = create_sermon_prompt(full_text)
        
    print(f"Generating {content_type} content...")
    result = generate_text(client, prompt)
    
    return result
