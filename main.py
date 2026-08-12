from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Message(BaseModel):
    text: str
    age: int


class MessageResponse(BaseModel):
    success: bool
    received_text: str


@app.post("/message", response_model=MessageResponse)
def receive_message(message: Message):
    return {
        "success": True,
        "received_text": message.text
    }