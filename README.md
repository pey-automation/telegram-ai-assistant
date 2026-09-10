# Telegram AI Assistant

A backend AI assistant built with **FastAPI, PostgreSQL, SQLAlchemy, Alembic, Telegram Bot API, and Groq**.

This project was built as a practical backend project to learn how to connect an AI agent with a real database, Telegram, conversation memory, and tool calling.

## Features

* FastAPI REST API
* PostgreSQL database
* SQLAlchemy ORM
* Alembic database migrations
* Telegram bot integration
* Persistent users and conversations
* Conversation history / memory
* AI responses using Groq
* AI tool calling
* Action Registry for tool execution
* Docker & Docker Compose
* Error handling and logging

## Architecture

```text
Telegram User
      ↓
Telegram Bot
      ↓
FastAPI / Services
      ↓
PostgreSQL
      ↓
Conversation History
      ↓
AI Agent
      ↓
Tool Calling / Action Registry
      ↓
AI Response
      ↓
Telegram User
```

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* python-telegram-bot
* Groq
* Docker
* Docker Compose

## Project Structure

```text
telegram-ai-assistant/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── telegram.py
│   │   └── users.py
│   │
│   └── services/
│       ├── ai_service.py
│       ├── conversation_service.py
│       ├── message_service.py
│       └── user_service.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_bot.py
└── test_ai.py
```

## Environment Variables

Create a `.env` file and configure:

```env
DATABASE_URL=your_database_url
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
POSTGRES_PASSWORD=your_postgres_password
```

Never commit the `.env` file to Git.

## Running with Docker

```bash
docker compose up --build
```

The application consists of:

* PostgreSQL database
* FastAPI API
* Telegram bot

## AI Agent & Tools

The AI assistant can use tools when necessary.

Currently, the project includes a user information tool that retrieves stored user data from PostgreSQL.

Tool execution is handled through an **Action Registry**, keeping AI tool definitions separate from their execution logic.

## Database

The database stores:

* Users
* Telegram user identity
* Conversations
* Messages
* Message roles (`user` / `assistant`)

Alembic is used to manage database migrations.

## Purpose

This project is part of my journey toward building **AI-powered automation systems and backend applications**.

The focus was on building a real working system rather than a collection of isolated tutorials.
