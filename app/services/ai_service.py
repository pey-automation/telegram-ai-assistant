import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found in .env"
    )


client = Groq(
    api_key=GROQ_API_KEY
)

MODEL_NAME = "openai/gpt-oss-20b"


def generate_ai_response(history):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=history,
    )

    return response.choices[0].message.content