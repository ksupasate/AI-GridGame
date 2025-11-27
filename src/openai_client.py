from openai import OpenAI
import base64

def analyze_image(image_bytes: bytes, prompt: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)

    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }],
        temperature=0.4,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

def generate_speech(text: str, api_key: str) -> bytes:
    client = OpenAI(api_key=api_key)

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    return response.content
