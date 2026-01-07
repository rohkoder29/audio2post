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
        response = client.chat_completion(messages, model=model, max_tokens=2000)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Generation failed: {e}")
        return None

def create_sermon_prompt(transcript_text, scripture_reference=""):
    scripture_note = f"\nEscritura del día: {scripture_reference}" if scripture_reference else ""
    
    return f"""
    Eres un administrador de redes sociales para una iglesia cristiana en Argentina. El pastor es **Leonardo D. Félix**.
    
    Analiza la siguiente transcripción de sermón y genera contenido para redes sociales:{scripture_note}
    
    1. **Resumen** (2-3 oraciones) en español rioplatense (neutro pero natural).
    
    2. **Puntos clave** (5-7 bullet points) con las enseñanzas principales.
    
    3. **Contenido para postear** (genera todos los que consideres relevantes):
       - Frases impactantes del pastor (atribuidas a "Ptr. Leonardo D. Félix")
       - Versículos bíblicos citados (atribuidos correctamente, ej: "Juan 3:16 RVR1960")
       - Pensamientos de reflexión basados en el mensaje
       - Palabras de aliento relacionadas con la enseñanza
       
       Cada item debe ser corto (máximo 25 palabras), impactante y útil para un gráfico de redes sociales.
       Formato: "Texto de la frase" — Atribución
    
    4. **Caption para Instagram/Facebook** promocionando este mensaje (atrapante, usa emojis, tono cercano y argentino).

    Transcripción:
    {transcript_text[:15000]} 
    """

def create_debate_prompt(transcript_text, topic=""):
    topic_note = f"\nTema del debate: {topic}" if topic else ""
    
    return f"""
    Eres un creador de contenido analizando un debate teológico en una iglesia en Argentina.{topic_note}
    
    Analiza la siguiente transcripción y genera:
    
    1. **Resumen** del tema central y las posiciones presentadas.
    
    2. **Análisis "Punto vs Contrapunto"** (3-5 argumentos clave de cada lado).
    
    3. **Contenido para postear** (genera todos los que consideres relevantes):
       - Citas destacadas de cada participante (con atribución)
       - Versículos bíblicos citados (atribuidos correctamente)
       - Preguntas para reflexión
       - Puntos de acuerdo entre las partes
       
       Cada item debe ser corto (máximo 25 palabras) y útil para un gráfico de redes sociales.
       Formato: "Texto de la frase" — Atribución
    
    4. **Post para redes** neutral y atractivo preguntando a la audiencia su opinión.

    Transcripción:
    {transcript_text[:15000]}
    """

def process_content_generation(transcript_data, hf_token, content_type="sermon", scripture_reference=""):
    """
    Orchestrates content generation.
    transcript_data: list of segments [{'text':..., 'speaker':...}, ...]
    scripture_reference: Optional scripture for the day (for sermons)
    """
    client = get_inference_client(hf_token)
    
    # Combine text
    full_text = " ".join([f"{seg['speaker']}: {seg['text']}" for seg in transcript_data])
    
    if content_type == "debate":
        prompt = create_debate_prompt(full_text)
    else:
        prompt = create_sermon_prompt(full_text, scripture_reference)
        
    print(f"Generating {content_type} content...")
    result = generate_text(client, prompt)
    
    return result
