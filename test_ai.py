import asyncio

from app.services.ai import generate_ai_response


async def main():

    messages = [
        {
            "role": "user",
            "content": "سلام، خودت رو در یک جمله معرفی کن."
        }
    ]

    response = await generate_ai_response(
        messages
    )

    print("\nAI RESPONSE:")
    print(response)


asyncio.run(main())