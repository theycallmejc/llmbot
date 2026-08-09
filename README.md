# Chat Bot

A small, standalone web chat bot. It has no training code, datasets, or model weights.

## Run it

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Set `OPENAI_API_KEY`.
4. Start it: `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000`.

The bot calls an OpenAI-compatible `/chat/completions` endpoint. Configure it with these optional environment variables: `BOT_MODEL`, `OPENAI_BASE_URL`, `BOT_SYSTEM_PROMPT`, `BOT_TIMEOUT_SECONDS`, and `BOT_MAX_HISTORY_MESSAGES`.

## Design

Each request receives a conversation ID. The server stores a bounded history in memory, adds the system prompt, sends the messages to the configured provider, and then stores the completed turn. Restarting the server clears stored conversations; use a database before deploying to multiple instances or needing durable history.

## Test

Run `pytest`.

## Docker

From a clean checkout, set `OPENAI_API_KEY` in your shell and run `docker compose up --build`. The app is available only on `127.0.0.1:8000` and stores local data in the named `chatbot-data` volume. GitHub Actions runs the test suite for every push and pull request.
