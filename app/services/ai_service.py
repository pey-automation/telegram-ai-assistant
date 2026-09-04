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


SYSTEM_PROMPT = """
You are a helpful AI assistant.

Rules:
- Answer the user's request directly.
- Do not add unrelated information.
- Keep simple requests concise.
- If the user asks for a translation, provide only the translation unless they ask for an explanation.
- If the user asks for code, provide the code and a brief explanation when useful.
- Use the conversation history to understand context.
- Do not invent previous conversation details.
- Respond in the same language as the user unless the user asks for another language.
"""


def format_conversation_history(messages):
    return [
        {
            "role": message.role,
            "content": message.text,
        }
        for message in messages
    ]


def generate_ai_response(history):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *history,
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )

    return response.choices[0].message.content