from openai import OpenAI
import json

def get_single_ai_response(prompt):
    """
    Simulates an AI response based on the given prompt.
    For demonstration purposes, this function returns a fixed response.
    In a real implementation, this could call an actual AI model or API.
    """
    with open("config.json", "r") as f:
        config = json.load(f)
    
    AI_API_URL = config.get("AI_API_URL", "https://api.deepseek.com")
    AI_API_KEY = config.get("AI_API_KEY", "")
    AI_API_MODEL = config.get("AI_API_MODEL", "deepseek-chat")

    client = OpenAI(api_key=AI_API_KEY, base_url=AI_API_URL)

    response = client.chat.completions.create(
        model=AI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    return response.choices[0].message.content


