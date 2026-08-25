import os

from dotenv import load_dotenv
from groq import AsyncGroq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY در فایل .env پیدا نشد."
    )


client = AsyncGroq(
    api_key=GROQ_API_KEY
)


async def generate_ai_response(
    messages: list[dict],
) -> str:

    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )

    return response.choices[0].message.content