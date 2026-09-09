import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.database import SessionLocal
from app.services.user_service import get_user_info


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
- When the user asks about their own stored information, use the available tools instead of guessing.
"""


def format_conversation_history(messages):
    return [
        {
            "role": message.role,
            "content": message.text,
        }
        for message in messages
    ]


# =========================
# Tools
# =========================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": (
                "Get the current Telegram user's stored information "
                "from the database."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]


def execute_get_user_info(user_id: int):
    db = SessionLocal()

    try:
        user = get_user_info(
            db=db,
            user_id=user_id,
        )

        if user is None:
            return {
                "found": False,
                "message": "User was not found.",
            }

        return {
            "found": True,
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "username": user.username,
            "telegram_user_id": user.telegram_user_id,
        }

    finally:
        db.close()


# =========================
# Action Registry
# =========================

ACTION_HANDLERS = {
    "get_user_info": execute_get_user_info,
}


def execute_tool(
    function_name: str,
    user_id: int,
    arguments: dict,
):
    handler = ACTION_HANDLERS.get(function_name)

    if handler is None:
        return {
            "error": f"Unknown tool: {function_name}"
        }

    return handler(
        user_id=user_id,
    )


# =========================
# AI Response
# =========================

def generate_ai_response(
    history,
    user_id: int,
):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *history,
    ]

    for _ in range(3):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        response_message = response.choices[0].message

        if not response_message.tool_calls:
            return response_message.content

        messages.append(
            response_message.model_dump()
        )

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )
            except json.JSONDecodeError:
                arguments = {}

            tool_result = execute_tool(
                function_name=function_name,
                user_id=user_id,
                arguments=arguments,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                    ),
                }
            )

    raise RuntimeError(
        "Maximum tool-calling iterations exceeded."
    )
