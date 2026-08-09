# LLM Bot Architecture

## Audit — 2026-08-09

The repository is a small Python web application. It uses FastAPI for the HTTP API and static HTML, CSS, and vanilla JavaScript for the browser client. `app/main.py` is the application entrypoint; `uvicorn app.main:app` starts the service. Pytest is the test framework.

The app has no authentication, database, or durable storage. It is currently a single-user local bot. Configuration comes from environment variables: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `BOT_MODEL`, `BOT_SYSTEM_PROMPT`, `BOT_TIMEOUT_SECONDS`, and `BOT_MAX_HISTORY_MESSAGES`.

## Current structure

```text
app/
  main.py       HTTP routes and static-file mounting
  service.py    conversation orchestration
  provider.py   OpenAI-compatible model adapter
  memory.py     bounded in-memory conversation store
  config.py     validated environment configuration
  static/       browser interface
tests/          provider-independent API and conversation tests
```

## Current request flow

```text
Browser → POST /api/chat → BotService → OpenAICompatibleProvider → Model API
                         ↘ ConversationStore ↗
```

The service prepends the configured system prompt, adds the conversation's remembered messages, sends the assembled request to the provider, and stores the completed user/assistant turn. Provider failures are mapped to safe API errors. The model API key stays exclusively on the server.

## Proposed evolution

Keep FastAPI and the lightweight browser client. Add streaming through Server-Sent Events, replace the in-memory store with the datastore selected in Phase 3, and introduce a context builder between `BotService` and the provider. Provider adapters remain behind a protocol so fallback and additional providers do not leak into route handlers.

## Security and constraints

- The current in-memory conversation store is erased on restart and is not suitable for multiple application instances.
- There is no identity boundary; therefore, the current application must remain local/single-user until Phase 3 makes and records an identity decision.
- The UI is deliberately text-only and uses `textContent`, so model responses are not interpreted as HTML.
- Provider calls have timeouts and clean errors, but no streaming, rate limits, budgets, observability, durable persistence, or attachment handling yet.
- Automated tests pass. The live health endpoint and static UI route were verified. Browser-based visual inspection could not run because no browser session was available in this environment.

## Implementation sequence

1. Complete and test the core backend contract.
2. Make stack, identity, storage, and deployment decisions.
3. Define the UI design system, then build streaming and persistent conversations.
4. Add advanced model capabilities only after the persistence, context, governance, and security foundations exist.
