# LLM Bot Build Plan for Codex

> **Revision note (2026-08-09):** This version is reset for a **new/different repository** — it is not a continuation of the previously audited nanoGPT-based project. Phases 1 and 2 have been reset to not-started and stripped of the prior repo's completion notes, so Codex will actually perform a real audit and build a real backend for this repository instead of skipping ahead on stale checkboxes. From Phase 3 onward, the plan was restructured to close four gaps found in the original: (1) no explicit decision phase for frontend stack / identity / storage / deployment, so downstream phases were guessing; (2) the "AI-native feel" work was scheduled after the UI was already built instead of before; (3) the persistence schema couldn't support edit/regenerate without a later migration; (4) "production-quality" had no containerization, CI/CD, or cost/rate governance anywhere in the plan.

## How to use this file

Run Codex from the project root and give it only this command:

```text
Read LLM_BOT_BUILD_PLAN.md and execute the next incomplete phase only.
Follow every instruction in the file.
Inspect the existing repository first, preserve working behavior, implement the phase completely, run relevant tests, update this file by marking completed items, and stop after finishing one phase.
```

For continuous execution across multiple phases, use:

```text
Read LLM_BOT_BUILD_PLAN.md and continue sequentially from the first incomplete phase.
Complete one phase at a time, test and verify it, update the checklist, then continue to the next phase.
Stop only if blocked, if a destructive architectural decision requires approval, or when all phases are complete.
```

---

# Permanent Execution Rules

These rules apply to every phase.

1. Inspect the existing repository before modifying code.
2. Do not assume the framework, filenames, database, frontend stack, or architecture.
3. Preserve working functionality.
4. Reuse existing abstractions instead of duplicating them.
5. Do not rebuild the application from scratch unless the repository is genuinely empty.
6. Do not introduce React, Vue, Angular, Next.js, or another large frontend framework unless already present or strongly justified — this decision is made explicitly in Phase 3, not improvised mid-build.
7. Keep LLM provider credentials on the backend only.
8. Never commit secrets.
9. Never expose hidden chain-of-thought.
10. Never fabricate model confidence, tool output, citations, progress percentages, backend data, or product statistics.
11. AI-generated critical data should use structured schemas when possible.
12. Never execute arbitrary model-generated shell commands.
13. Validate all tool calls server-side.
14. Preserve user work when AI operations fail.
15. Every asynchronous operation needs loading, success, failure, and retry behavior where appropriate.
16. Add automated tests for critical backend behavior.
17. Mock LLM providers and external integrations in normal unit tests.
18. Run relevant tests after every meaningful implementation.
19. If the UI changes and browser automation is available, render and visually inspect the result.
20. Do not claim something works unless it was actually tested.
21. Update this file after every completed phase.
22. Stop after one phase when using the "next incomplete phase only" command.
23. Treat LLM API cost as a first-class production risk. Do not enable any feature that calls the model repeatedly (agent mode, RAG, evaluations) without the budget/rate-limit path from Phase 19 already in place.
24. If message editing or regeneration is planned anywhere in the roadmap, design the persistence schema to support branching from the start. Do not ship a flat message table and migrate later.

---

# Product Goal

Build a production-quality LLM chatbot that evolves through this architecture:

```text
User
  ↓
Chat UI  (built against an explicit AI-native design system)
  ↓
Chat API
  ↓
Identity / Access boundary  (decided in Phase 3, not assumed)
  ↓
Conversation Service
  ↓
Context Builder
  ↓
LLM Provider  (with fallback)
  ↓
Streaming Response
  ↓
Conversation Persistence  (branch-capable schema)
  ↓
RAG / Tools / Memory / Agent Mode
  ↓
Rate & Cost Governance  (wraps every model-calling path)
  ↓
Containerized Deployment
```

The final product should support:

- modern, AI-native chat UI
- multiple conversations, with branching/edit-and-resend supported at the schema level
- persistent history
- streaming responses
- markdown and code rendering
- model abstraction with fallback
- prompt management
- context-window management
- file attachments
- RAG
- tool calling
- optional web search
- controlled memory
- optional agent mode
- rate limiting and cost budgets
- security controls
- observability
- AI evaluations
- containerized, CI-tested deployment
- production hardening

---

# Progress

## Phase 1 — Repository Audit and Architecture
- [x] Complete

Completed: 2026-08-09
Summary: Audited the FastAPI/vanilla-JS bot, ran its automated tests, verified the running health and UI endpoints, and documented the current and proposed architecture in `docs/architecture/LLM_BOT_ARCHITECTURE.md`.

### Known Limitations

Browser-based visual inspection was unavailable in this environment because no browser session was available.

### Objective

Understand the current repository before implementing the LLM bot.

### Tasks

- Inspect the complete repository tree.
- Identify backend framework.
- Identify frontend architecture.
- Identify application entrypoint.
- Identify authentication.
- Identify database/storage.
- Identify API conventions.
- Identify existing AI/LLM code.
- Identify environment/config handling.
- Identify test framework.
- Run existing tests.
- Run the application if possible.
- Record current problems and constraints.

Create or update:

```text
docs/architecture/LLM_BOT_ARCHITECTURE.md
```

Document:

- current stack
- repository structure
- proposed chat architecture
- conversation model
- streaming strategy
- security considerations
- implementation sequence

### Acceptance Criteria

- Repository architecture is documented from actual inspection.
- Existing tests have been run.
- No application functionality is unnecessarily changed.
- The next implementation phase has a clear architecture.

---

## Phase 2 — Core LLM Backend
- [x] Complete

Completed: 2026-08-09
Summary: Implemented and tested the route → service → provider backend, environment-based model configuration, message validation, timeout/provider/rate-limit error mapping, and mocked provider responses.

### Objective

Create the first reliable backend chat capability.

### Architecture

```text
Route
→ Chat Service
→ LLM Provider
→ Model API
```

### Tasks

- Create or improve a centralized LLM provider abstraction.
- Read API key/model configuration from environment variables.
- Create a chat service.
- Create a backend chat endpoint.
- Validate incoming user messages.
- Send user input to the configured model.
- Return assistant output.
- Add timeout handling.
- Add rate-limit handling.
- Add provider-failure handling.
- Return clean application errors.
- Keep provider-specific code out of route handlers.
- Add mocked tests.

### Acceptance Criteria

- A user message can produce a real model response.
- Secrets remain backend-only.
- Provider failures do not crash the app.
- Unit tests do not require a live model API.
- Relevant tests pass.

---

## Phase 3 — Architecture Decision: Stack, Identity, Storage, Deployment Target
- [x] Complete

Completed: 2026-08-09
Summary: Chose the existing vanilla browser client, single-user local operation, SQLite persistence with local vector storage later if needed, and local-machine deployment. The justifications are recorded in `docs/architecture/LLM_BOT_ARCHITECTURE.md`.

### Objective

Phase 1 audited an existing repository. If that repository has no web application, no frontend, and no auth — which is the case for a bare model-training repo like nanoGPT — every later phase that says "use the existing stack" or "if authentication exists" has nothing to attach to. This phase forces the decisions Phase 1 could only observe, not make. Nothing downstream should have to guess.

### Decisions Required

Write each into `docs/architecture/LLM_BOT_ARCHITECTURE.md` with a one-paragraph justification.

1. **Frontend stack**
   - If a frontend already exists and is actively used, keep it.
   - If none exists, default to server-rendered templates plus minimal vanilla JS/HTML/CSS for a chat UI this size, unless there's a specific reason to want a component framework. Do not introduce React/Vue/Next.js by default just because it's common — justify it against Permanent Execution Rule 6.
   - Record the decision and the reason.

2. **Identity & multi-tenancy**
   - Decide explicitly: single-user local tool, or multi-user with accounts.
   - If multi-user, choose an auth approach (session-based, JWT, OAuth) proportional to actual need — do not build enterprise SSO for a personal project.
   - This decision is a hard dependency for Phase 7 (persistence/ownership), Phase 13 (RAG isolation), and Phase 16 (memory isolation). Do not defer it into those phases.

3. **Storage**
   - Pick the simplest datastore that satisfies Phases 7–13 (e.g., SQLite for single-user/local, Postgres for multi-user/deployed).
   - Pick a vector storage approach for Phase 13 consistent with the above (e.g., pgvector alongside Postgres, or a lightweight embedded vector store for local/SQLite).

4. **Deployment target**
   - Decide where this actually runs (local only, single VM, containerized service, serverless) before Phase 23 starts, since it affects how config and secrets are handled from Phase 2 onward.

### Rules

- This phase produces decisions and documentation only — no speculative infrastructure.
- Every "if authentication exists" and "if the frontend stack supports X" conditional elsewhere in this document resolves against the decisions made here.

### Acceptance Criteria

- `docs/architecture/LLM_BOT_ARCHITECTURE.md` is updated with explicit, justified decisions for all four items above.
- No phase after this one needs to guess the stack, auth model, storage, or deployment target.

---

## Phase 4 — AI-Native Design System
- [x] Complete

Completed: 2026-08-09
Summary: Defined the visual language, responsive layout, safe output rules, and real interaction states in `docs/design/AI_NATIVE_DESIGN_SYSTEM.md`; the refreshed UI implements those decisions.

### Known Limitations

Browser automation is not available in this environment, so visual verification relies on the user-provided browser capture and route-level checks.

### Objective

Define the visual and interaction language before building any screen, so the "AI feel" is structural, not a coat of paint applied near the end. Retrofitting this after a dozen phases of features already exist means rewriting CSS and markup across the whole app.

### Deliverable

A short design reference (e.g., `docs/design/AI_NATIVE_DESIGN_SYSTEM.md`) covering:

**Visual language**

- Typography-led hierarchy over decoration: one primary typeface, a restrained weight/size scale.
- No cartoon bot avatars, no default purple-to-blue gradient backgrounds, no glowing neon borders — these read as generic "AI template," not as a real product.
- A small neutral color palette (background / surface / text / border) plus one accent color used sparingly, only for interactive elements.
- Generous whitespace and a line length tuned for reading, not for filling the viewport.

**Motion & state — this is where "AI feel" actually lives**

- Streaming text: a subtle blinking cursor or fade-in per chunk, not a spinner that hides content until generation finishes.
- Tool/RAG/agent activity: short, literal status text tied to real backend state ("Searching your documents…", "Running calculator…"). Never decorative fake-thinking animation, per Permanent Execution Rule 10.
- Loading states are purposeful skeletons shaped like the content that will appear, not generic spinners.
- Message actions (copy, regenerate, edit) appear on hover/focus rather than sitting as permanent visual clutter.
- Transitions are fast (roughly 120–200ms) and reserved for state changes that matter (new message, stream start/stop) — never applied to static content.

**Interaction model**

- Keyboard-first: Enter to send, Shift+Enter for a newline, Cmd/Ctrl+K for a command palette if one is built.
- The empty state guides the user with a few real, clickable example prompts, not a blank box.
- Errors are stated plainly inside the conversation ("The model didn't respond — retry?") rather than a generic toast disconnected from context.

### Rules

- Every visual or motion decision must be traceable to making the AI's current state legible — not decoration for its own sake.
- This system is a hard dependency for Phase 5 (Chat UI) and Phase 18 (Interaction Polish). Both must implement against it, not invent their own styling ad hoc.

### Acceptance Criteria

- The design reference exists and is specific enough that Phase 5 can be built directly from it without further design decisions.
- No component built from Phase 5 onward contradicts it without a documented reason.

---

## Phase 5 — Chat UI
- [ ] Complete

### Objective

Build a clean, Claude/ChatGPT-style conversational interface using the frontend stack decided in Phase 3, implemented directly against the design system from Phase 4.

### Required UI

- sidebar
- New Chat
- conversation area
- user message bubbles/blocks
- assistant message blocks
- input composer
- Send
- loading state
- error state
- empty state
- responsive layout

### Rendering

Support:

- Markdown
- code blocks
- copy code
- copy response

### Design Direction

This section summarizes Phase 4 — Phase 4 is the source of truth if anything conflicts.

Prefer:

- clean
- restrained
- readable
- AI-native (see Phase 4 for what that means concretely)
- strong light theme
- good dark theme if supported

Avoid:

- excessive gradients
- neon AI styling
- generic admin dashboard
- giant cards
- dead controls

### Acceptance Criteria

- User can send a message from the UI.
- Assistant response renders correctly.
- Markdown/code render safely.
- UI works on desktop and mobile.
- Implementation matches the Phase 4 design system; any deviation is documented with a reason.
- No relevant browser-console errors.

---

## Phase 6 — Streaming Responses
- [ ] Complete

### Objective

Stream real model output progressively, rendered per the Phase 4 motion/state guidance (cursor/fade-in, not a spinner).

### Preferred Approach

Use Server-Sent Events if compatible with the current backend.

### Tasks

- Enable provider streaming.
- Stream real chunks to the browser.
- Render content progressively.
- Add Stop Generation.
- Prevent duplicate sends.
- Handle browser disconnect.
- Handle provider disconnect.
- Preserve partial response where appropriate.
- Display clean stream errors.

### Rules

Do not simulate typing with artificial delays.

### Acceptance Criteria

- Responses appear progressively.
- Stop Generation works.
- Failed streams leave the application usable.
- Relevant tests pass.

---

## Phase 7 — Conversation Persistence
- [ ] Complete

### Objective

Store and reload chats, with a schema that supports edit/regenerate from day one — see Permanent Execution Rule 24.

### Data Model

Conversation should include conceptually:

- id
- user_id, if the Phase 3 identity decision includes multi-user auth
- title
- created_at
- updated_at

Message should include:

- id
- conversation_id
- parent_message_id (nullable — lets edit/regenerate create a new branch instead of mutating or deleting history)
- role
- content
- model
- created_at
- an indicator of which branch is currently active/displayed per parent

### Features

- create conversation
- list conversations
- load conversation
- save user messages
- save assistant messages
- rename conversation
- delete conversation
- preserve message ordering
- resolve which branch to display when a message has multiple children

### Rules

- Do not store hidden reasoning.
- Build the branch-capable schema now even if the UI only ever shows one linear branch until Phase 18 — this avoids a migration later.

### Acceptance Criteria

- Conversations survive reload/restart as appropriate for the storage layer.
- Sidebar shows real conversations.
- Conversation ownership is enforced if the Phase 3 decision includes multi-user auth.
- Schema supports branching even before the UI exposes it.
- Tests cover persistence behavior, including branch creation.

---

## Phase 8 — Automatic Conversation Titles
- [ ] Complete

### Objective

Generate concise useful conversation titles.

### Rules

- Generate after first meaningful user message.
- Target roughly 5–8 words.
- Do not block the main response.
- Fall back safely if title generation fails.
- Allow manual rename.
- Never overwrite a manually renamed title.

### Acceptance Criteria

- New conversations get useful titles.
- Title failure does not affect chat.
- Manual rename remains authoritative.

---

## Phase 9 — Model and Provider Abstraction
- [ ] Complete

### Objective

Avoid tight coupling to one provider/model, and avoid a single provider outage taking the whole bot down.

### Interface

Support conceptually:

```text
generate()
stream()
generate_structured()
```

### Tasks

- Introduce or improve provider interface.
- Keep business logic provider-independent.
- Load provider/model choice from configuration.
- Support an optional configured fallback provider/model so a single outage degrades gracefully instead of failing every request.
- Preserve existing chat behavior.
- Add tests around provider selection and fallback behavior.

### Acceptance Criteria

- Chat service is not directly coupled to a provider SDK.
- Existing functionality still works.
- Provider abstraction is simple, not speculative overengineering.
- Configured fallback activates on primary provider failure; behavior without a configured fallback is a clean error.

---

## Phase 10 — Prompt Management
- [ ] Complete

### Objective

Centralize and version prompts.

### Tasks

- Create prompt registry or equivalent.
- Add base system prompt.
- Add prompt name/version.
- Support optional domain-specific instructions.
- Keep large prompt strings out of route handlers.
- Record prompt version where useful.

### Rules

Do not expose hidden system prompts to the frontend.

### Acceptance Criteria

- Prompt definitions are centralized.
- Prompt versions are traceable.
- Prompt assembly has tests.

---

## Phase 11 — Context Window Management
- [ ] Complete

### Objective

Prevent long conversations from blindly exceeding model limits.

### Tasks

Create a Context Builder or equivalent.

Support:

- context/token estimation
- recent-message prioritization
- maximum context budget
- conversation summarization when necessary
- latest user request always preserved
- optional stored conversation summary
- correct handling of the active branch when the conversation has diverged (Phase 7)

### Rules

Do not send entire histories indefinitely.

### Acceptance Criteria

- Long conversations remain usable.
- Context selection is deterministic/testable where possible.
- Latest user intent is preserved.
- Tests cover long-history behavior.

---

## Phase 12 — File Attachments
- [ ] Complete

### Objective

Allow users to attach useful files safely.

### Start With

- txt
- md
- json
- csv
- log
- yaml
- yml
- py
- js
- html
- css

Add PDF only if safe extraction is supported by the current architecture.

### Tasks

- file-size validation
- type validation
- secure filenames
- path traversal protection
- safe server-side storage
- text extraction
- attachment UI
- model context integration
- graceful extraction failure

### Acceptance Criteria

- Supported files can be uploaded and used in chat.
- Unsafe files are rejected.
- Cross-user file access is prevented where the Phase 3 decision includes multi-user auth.
- Upload tests exist.

---

## Phase 13 — Retrieval-Augmented Generation
- [ ] Complete

### Objective

Retrieve relevant document chunks instead of stuffing entire documents into prompts.

### Architecture

```text
Document
→ Extraction
→ Chunking
→ Embeddings
→ Vector Storage
→ Retrieval
→ Context Builder
→ LLM
```

### Requirements

- document ownership, following the Phase 3 identity decision
- chunk metadata
- embeddings
- similarity retrieval
- top-k retrieval
- source references
- document deletion
- no cross-user leakage

Use the vector storage approach decided in Phase 3.

### Acceptance Criteria

- Questions can retrieve relevant uploaded content.
- Responses can identify their retrieved sources.
- Retrieval tests exist.
- No unnecessary infrastructure was introduced.

---

## Phase 14 — Tool Calling
- [ ] Complete

### Objective

Allow the model to invoke controlled server-side capabilities.

### Tool Registry

Each tool defines:

- name
- description
- input schema
- permission level
- executor

### Safe Initial Tools

Examples:

- calculator
- current application-data lookup
- conversation search

### Flow

```text
User
→ LLM
→ Tool Request
→ Server Validation
→ Tool Execution
→ Tool Result
→ LLM
→ Final Response
```

### Rules

- Never provide arbitrary shell access.
- Validate model-generated tool parameters.
- Allow only registered tools.
- Log tool execution safely.

### Acceptance Criteria

- Allowed tools work.
- Unknown/unauthorized tools are rejected.
- Tool-call tests exist.
- Tool failure does not crash chat.

---

## Phase 15 — Optional Web Search
- [ ] Complete

### Objective

Provide current external information through a controlled search tool.

### Requirements

- dedicated server-side search abstraction
- query validation
- timeout
- rate limiting
- source metadata
- citation support
- graceful failure

### Rules

Do not allow the model to perform arbitrary unrestricted HTTP requests.

Clearly distinguish retrieved information from model-generated knowledge.

### Acceptance Criteria

- Search results can be used in responses.
- Sources are surfaced clearly.
- Tests use mocked search responses.

---

## Phase 16 — User Memory
- [ ] Complete

### Objective

Store useful cross-conversation preferences/context in a controlled way.

### Features

- create memory
- retrieve relevant memory
- list/manage memory
- delete memory
- clear memory

### Rules

- Do not store every chat message.
- Avoid storing sensitive information automatically.
- Respect user ownership, following the Phase 3 identity decision.
- Inject only relevant memory into context.

### Acceptance Criteria

- Memory improves relevant future chats.
- Users can see/delete saved memory.
- Memory does not leak between users.

---

## Phase 17 — Agent Mode
- [ ] Complete

### Objective

Add optional multi-step task execution without breaking normal chat.

### Agent Flow

```text
Goal
→ Plan
→ Tool Selection
→ Tool Execution
→ Observation
→ Next Step
→ Final Result
```

### Guardrails

- bounded step count
- tool allowlist
- execution timeout
- retry limits
- cancellation
- audit log
- approval before sensitive actions
- step and tool-call counts bounded against the Phase 19 rate/cost budget, not just an arbitrary limit

### UI

Show user-visible activity such as:

- Searching documents...
- Checking repository...
- Running approved tool...

Do not expose hidden chain-of-thought.

### Acceptance Criteria

- Agent mode is optional.
- Normal chat remains intact.
- Tools remain controlled.
- Agent loops cannot run indefinitely, and cannot exceed the Phase 19 cost budget.
- Users can cancel execution.

---

## Phase 18 — AI-Native Interaction Polish
- [ ] Complete

### Objective

Wire the remaining interaction affordances on top of the Phase 4 design system and the Phase 7 branch-capable schema. This phase should mostly be wiring existing capability to UI, not new design decisions — those were made in Phase 4.

### Add Where Appropriate

- contextual suggestions
- quick prompts
- streamed generation state
- tool-execution indicators
- file-analysis state
- source citations
- regenerate
- edit and resend (using the branching schema from Phase 7)
- stop generation
- response feedback
- keyboard shortcuts

Suggested shortcuts:

- Enter = send
- Shift+Enter = newline
- Ctrl/Cmd+K = command palette if implemented

### Rules

AI feeling comes from product behavior built on the Phase 4 system, not from adding gradients here.

### Acceptance Criteria

- Important AI states are understandable.
- UI remains consistent with the Phase 4 design system.
- Mobile behavior remains usable.
- Accessibility is preserved/improved.

---

## Phase 19 — Rate Limiting & Cost Controls
- [ ] Complete

### Objective

Treat LLM spend as a first-class production risk, not scattered checklist bullets. Every feature added since Phase 9 — streaming, RAG, tools, agent mode — multiplies how many model calls a single user session can trigger.

### Tasks

- Per-user and/or per-IP request rate limiting on the chat endpoint.
- A configurable per-user/day or per-user/month token or request budget.
- A hard stop, with a clear non-technical error message, when a budget is exceeded — never silently degrade and never silently keep charging.
- Track a cost estimate per request (token count × known provider pricing) and surface it in Observability (Phase 21).
- Agent mode (Phase 17) step and tool-call counts are bounded against this same budget.

### Rules

- This is one enforced code path every chat/agent/RAG request goes through — not guidance repeated in five other phases.
- Budgets and limits are configuration, not hardcoded values.

### Acceptance Criteria

- A user cannot exceed configured request/token budgets even via agent mode or heavy RAG usage.
- Budget exhaustion produces a clear, safe failure — not a crash, not a silent free-for-all.
- Tests cover limit enforcement.

---

## Phase 20 — Security Hardening
- [ ] Complete

### Objective

Audit and fix high-impact security weaknesses.

### Review

- prompt injection
- tool injection
- XSS from model output
- unsafe Markdown
- API key exposure
- authentication
- authorization
- conversation ownership
- file upload security
- RAG isolation
- rate limiting (implementation lives in Phase 19; this audits it)
- CSRF where applicable
- CORS
- unsafe URL fetching
- arbitrary code/command execution
- secrets in logs

### Acceptance Criteria

- High-risk findings are fixed.
- Relevant regression tests exist.
- Security fixes are practical, not cosmetic.

---

## Phase 21 — Observability
- [ ] Complete

### Objective

Make the LLM application operable.

### Track Where Available

- request ID
- user/conversation ID
- provider
- model
- latency
- token usage
- cost estimate per request (from Phase 19)
- streaming failures
- tool calls
- retrieval latency
- provider errors and fallback activations (Phase 9)
- retry count

Use structured logging.

### Never Log

- API keys
- passwords
- auth tokens
- unnecessary sensitive content
- hidden reasoning

Add health/readiness endpoints if appropriate — these feed the deployment platform's health checks in Phase 23.

### Acceptance Criteria

- Important failures can be diagnosed from logs/metrics.
- Sensitive data is not logged.
- Health status is available where useful.

---

## Phase 22 — AI Evaluation Framework
- [ ] Complete

### Objective

Measure whether AI changes improve or degrade the bot.

### Evaluation Areas

- instruction following
- relevance
- context retention
- hallucination resistance
- RAG grounding
- tool selection
- structured output
- long conversations
- refusal behavior where relevant

### Record

- model
- prompt version
- evaluation case
- result/metrics
- latency
- token usage where available

Support comparisons such as:

- prompt v1 vs v2
- model A vs model B

Prefer deterministic checks wherever possible.

### Acceptance Criteria

- AI quality can be compared across versions.
- Evaluations do not rely solely on vague subjective scoring.
- Evaluation documentation exists.

---

## Phase 23 — Containerization & Deployment
- [ ] Complete

### Objective

A bot that only runs via `uvicorn app.main:app` on a laptop is not production-quality, regardless of how good the code is. This phase makes the Phase 3 deployment-target decision real.

### Tasks

- Dockerfile for the backend (and frontend build step if applicable), using a minimal base image and a non-root user.
- `docker-compose.yml` or equivalent for local dev parity: app + database + any vector store.
- Environment separation: distinct config for local/dev, staging, and production — no shared `.env` committed to source control.
- Secrets handling appropriate to the Phase 3 deployment target (e.g., environment variables injected by the platform, a secrets manager — not `.env` files in production).
- CI pipeline: run lint and tests on every push/PR before merge.
- CD or a written deployment runbook: how a change actually reaches production. Manual steps are acceptable for a small project, but they must be written down, not implied.
- Health/readiness endpoints from Phase 21 wired into the deployment platform's health checks.

### Rules

- Do not introduce Kubernetes, a service mesh, or multi-region infrastructure for a project that doesn't need it — match infra complexity to actual scale, the same discipline Permanent Execution Rule 6 applies to frontend frameworks.
- Never commit secrets or `.env` files with real credentials, per Permanent Execution Rule 8.

### Acceptance Criteria

- The application can be built and run from a clean checkout using the Dockerfile/compose setup alone.
- CI fails the build on failing tests or lint errors.
- The deployment path from a merged change to a running instance is documented and repeatable.
- Environment configuration between dev/staging/prod is clearly separated.

---

## Phase 24 — Production Readiness Audit
- [ ] Complete

### Objective

Perform a complete final engineering review.

### Audit

- frontend
- backend
- database
- LLM layer
- streaming
- conversation persistence (including branching)
- context management
- uploads
- RAG
- tools
- web search if present
- memory
- agent mode
- rate limiting and cost controls
- security
- authentication
- error handling
- performance
- observability
- accessibility
- responsiveness
- containerized deployment and CI
- tests

### Full Journey to Verify

1. Login if authentication exists.
2. Create new chat.
3. Send a message.
4. Stream response.
5. Continue conversation.
6. Create second conversation.
7. Reload and verify history.
8. Upload a supported document.
9. Ask a grounded question.
10. Run a safe tool.
11. Stop generation.
12. Trigger/handle a provider failure and verify fallback (Phase 9).
13. Edit a message and confirm it branches rather than overwrites (Phase 7/18).
14. Rename a conversation.
15. Delete a conversation.
16. Exceed a configured rate/cost budget and verify the clean failure (Phase 19).
17. Verify mobile layout.
18. Verify no relevant console/server errors.
19. Build and run the application from the Docker/compose setup alone (Phase 23).

### Cleanup

Remove:

- dead code
- debug output
- unused CSS
- unused dependencies
- fake UI
- placeholder functionality presented as real

### Acceptance Criteria

- All major user journeys work.
- Tests pass.
- Documentation reflects reality.
- No known severe regression remains.
- Application is ready for the next deployment/release step.

---

# Completion Protocol

After finishing a phase:

1. Change its checkbox from:

```text
- [ ] Complete
```

to:

```text
- [x] Complete
```

2. Add a short completion note directly below the phase heading:

```text
Completed: YYYY-MM-DD
Summary: <one or two sentences>
```

3. Record any important limitation under:

```text
### Known Limitations
```

4. Run relevant tests.

5. Do not mark a phase complete if acceptance criteria are not satisfied.

6. When using the "next incomplete phase only" command, STOP after updating this file.

---

# Final State

When every phase is complete, the checklist should show:

```text
Phase 1  ✅
Phase 2  ✅
Phase 3  ✅
Phase 4  ✅
Phase 5  ✅
Phase 6  ✅
Phase 7  ✅
Phase 8  ✅
Phase 9  ✅
Phase 10 ✅
Phase 11 ✅
Phase 12 ✅
Phase 13 ✅
Phase 14 ✅
Phase 15 ✅
Phase 16 ✅
Phase 17 ✅
Phase 18 ✅
Phase 19 ✅
Phase 20 ✅
Phase 21 ✅
Phase 22 ✅
Phase 23 ✅
Phase 24 ✅
```

At that point, perform one final repository audit and update the project README/architecture documentation to match the actual implementation.
