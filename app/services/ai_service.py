import json
import os

import httpx
from dotenv import load_dotenv
from groq import Groq

from app.database import SessionLocal
from app.services.order_service import (
    create_order,
    get_order,
    get_orders,
)
from app.services.user_service import get_user_info


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found in .env"
    )

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

if not N8N_WEBHOOK_URL:
    raise RuntimeError(
        "N8N_WEBHOOK_URL not found in .env"
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
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": (
                "Create a new order for the current Telegram user."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer.",
                    },
                    "item": {
                        "type": "string",
                        "description": "Name of the ordered item.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of items ordered.",
                    },
                    "amount": {
                        "type": "integer",
                        "description": (
                            "Total order amount as an integer."
                        ),
                    },
                },
                "required": [
                    "customer_name",
                    "item",
                    "quantity",
                    "amount",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_orders",
            "description": (
                "Get the current Telegram user's orders "
                "from the database."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": (
                "Get a specific order belonging to the current "
                "Telegram user."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The ID of the order.",
                    },
                },
                "required": [
                    "order_id",
                ],
            },
        },
    },
]


# =========================
# User Actions
# =========================

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
# Order Actions
# =========================

def send_order_to_n8n(order_data: dict):
    response = httpx.post(
        N8N_WEBHOOK_URL,
        json=order_data,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def execute_create_order(
    user_id: int,
    customer_name: str,
    item: str,
    quantity: int,
    amount: int,
):
    db = SessionLocal()

    try:
        order = create_order(
            db=db,
            user_id=user_id,
            customer_name=customer_name,
            item=item,
            quantity=quantity,
            amount=amount,
        )

        order_data = {
            "success": True,
            "order_id": order.id,
            "customer_name": order.customer_name,
            "item": order.item,
            "quantity": order.quantity,
            "amount": order.amount,
            "created_at": order.created_at.isoformat(),
        }

        try:
            send_order_to_n8n(order_data)
        except Exception as exc:
            print(f"n8n automation failed: {exc}")

        return order_data

    finally:
        db.close()


def execute_get_orders(user_id: int):
    db = SessionLocal()

    try:
        orders = get_orders(
            db=db,
            user_id=user_id,
        )

        if not orders:
            return {
                "found": False,
                "orders": [],
                "message": "No orders found.",
            }

        return {
            "found": True,
            "orders": [
                {
                    "order_id": order.id,
                    "customer_name": order.customer_name,
                    "item": order.item,
                    "quantity": order.quantity,
                    "amount": order.amount,
                    "created_at": order.created_at.isoformat(),
                }
                for order in orders
            ],
        }

    finally:
        db.close()


def execute_get_order(
    user_id: int,
    order_id: int,
):
    db = SessionLocal()

    try:
        order = get_order(
            db=db,
            user_id=user_id,
            order_id=order_id,
        )

        if order is None:
            return {
                "found": False,
                "message": "Order was not found.",
            }

        return {
            "found": True,
            "order_id": order.id,
            "customer_name": order.customer_name,
            "item": order.item,
            "quantity": order.quantity,
            "amount": order.amount,
            "created_at": order.created_at.isoformat(),
        }

    finally:
        db.close()


# =========================
# Action Registry
# =========================

ACTION_HANDLERS = {
    "get_user_info": execute_get_user_info,
    "create_order": execute_create_order,
    "get_orders": execute_get_orders,
    "get_order": execute_get_order,
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

    if function_name == "create_order":
        return handler(
            user_id=user_id,
            customer_name=arguments["customer_name"],
            item=arguments["item"],
            quantity=arguments["quantity"],
            amount=arguments["amount"],
        )

    if function_name == "get_order":
        return handler(
            user_id=user_id,
            order_id=arguments["order_id"],
        )

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
            {
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in response_message.tool_calls
                ],
            }
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