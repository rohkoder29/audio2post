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
    Eres un administrador de redes sociales para una iglesia en Argentina. Analiza la siguiente transcripción de sermón y genera:
    1. Un resumen conciso (2 oraciones) en español rioplatense (neutro pero natural).
    2. Una lista de 5 puntos clave (bullet points).
    3. Tres candidatos para "Frases destacadas" (Quote Cards). Cada una debe ser una cita impactante y autónoma del texto, de menos de 20 palabras, atribuida al orador.
    4. Un caption para Instagram/Facebook promocionando este mensaje (atrapante, usa emojis, tono cercano y argentino).

    Transcripción:
    {transcript_text[:15000]} 
    """ # Truncate to avoid context limit issues on free tier

def create_debate_prompt(transcript_text):
    return f"""
    Eres un creador de contenido analizando un debate teológico en Argentina. Analiza la siguiente transcripción y genera:
    1. Un resumen del conflicto central/tema.
    2. Análisis "Punto vs Contrapunto" (3 argumentos clave).
    3. Tres candidatos para "Frases destacadas" (una de cada lado si es posible).
    4. Un post de redes sociales neutral y atractivo preguntando a la audiencia su opinión.

    Transcripción:
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
