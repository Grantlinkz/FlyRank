# Code Standards — FlyRank Platform

## General Principles

- **Single Responsibility Principle**: Keep route handlers, repository accessors, auth guards, and scraper parsers in separate modules.
- **Root Cause Fixes**: Never mask underlying errors with empty fallbacks, swallowed exceptions, or commented-out assertions.
- **Fail-Safe Defaults**: Reject invalid external input at system boundaries before processing.

## Language Standards (TypeScript/JavaScript & Python)
### Chosen Lane (Python)

- **TypeScript / Node.js**:
  - Enforce strict typing. Avoid `any` — use explicit interfaces, types, or Zod schemas.
  - Validate unknown request bodies or external scraped HTML at the boundary.
- **Python**:
  - Use Python 3.10+ type hints across functions and classes.
  - Leverage Pydantic models for data validation and parsing.

## Database & Repository Standards

- **Parameterized Queries Mandatory**: Always pass values via query placeholders (`?` for SQLite, `$1` for `pg`, `%s` for `psycopg`). Never interpolate strings into SQL.
  ```js
  // Correct
  db.prepare('SELECT * FROM tasks WHERE id = ?').get(id);
  // Incorrect - FORBIDDEN
  db.prepare(`SELECT * FROM tasks WHERE id = ${id}`).get();
  ```
- **Auto-Initialization & Seed-Once Rule**:
  - Check for and create required tables (`CREATE TABLE IF NOT EXISTS tasks ...`) on application startup.
  - Seed default data **only when the table row count is zero**. Seed logic must be idempotent across server restarts.
- **Repository Isolation**: All database operations must live inside `src/repository/`. Route handlers call repository methods rather than managing SQL or connections.

## Secrets & Environment Configuration

- **Zero Credential Leaks**: Never hardcode database passwords, JWT secrets, or API keys in code or commits.
- **`.env` Workflow**:
  - Store local secrets in `.env`.
  - Maintain a git-tracked `.env.example` with dummy placeholder values.
  - Ensure `.env` is listed in `.gitignore`.

## Auth & Security Standards

- **Delegated Authentication**: Do not write custom password hashing or password storage logic. Forward credentials to Supabase Auth.
- **Bearer Token Extraction**: Extract token cleanly from `Authorization: Bearer <token>`. Handle missing or malformed headers gracefully by returning HTTP `401` with `{ "error": "Access token required" }`.
- **Token Verification**: Verify tokens against Supabase Auth (`supabase.auth.getUser(token)`). Reject invalid/expired tokens with HTTP `401`.

## Scraping & Data Pipeline Standards

- **Politeness Rules**:
  - Identify the bot via an explicit `User-Agent` header (e.g. `FlyRankInternship/1.0`).
  - Set request timeouts (e.g. 5–10 seconds).
  - Enforce a minimum delay (>=500ms) between consecutive live network requests.
- **Caching**: Save downloaded target HTML to `scraper/cache/`. Read from local cache during development to avoid redundant external network calls.
- **URL Handling**: Use standard URL resolution tools (`new URL(relative, base)` in JS, `urljoin` in Python) to resolve relative links. Never perform manual string concatenation on URLs.
- **Validation & Output**: Validate extracted fields against a Zod/Pydantic schema before writing to `output/books.json`. Direct failing records to `errors.json` with reason details.
- **Failure Resilience**: Log and skip broken individual detail pages (404s, parser errors) without throwing an uncaught exception that halts the entire job. End runs with a summary report (`output/run-report.json`).

## LLM Integration & Prompt Engineering Standards

- **Untrusted Input Isolation**: Never concatenate raw user input into system instructions. User input must always be passed inside the `user` message role as a JSON payload to prevent prompt injection.
- **Closed Output Contracts**: Every categorical field returned by an LLM decision endpoint must belong to a predefined enum list (`TaskCategory`, `TaskUrgency`, `TaskEffort`). Freeform categories are strictly forbidden.
- **Pre-Model Input Validation**: Validate inbound fields (e.g. non-empty string, character limits) before invoking model logic; return `400 Bad Request` to avoid consuming API quota on malformed requests.
- **Explicit Timeouts & Retry Policy**: Client requests must have an explicit timeout (e.g. 30s). Retries with exponential backoff and jitter are permitted only for transient errors (429, 5xx); client errors (400, 401, 403) must fail fast.
- **Single Repair Retry & Quarantine**: If initial model output fails JSON or Pydantic validation, trigger exactly one repair request containing the original prompt, malformed output, and validation error. Persistent failures must be appended to `logs/quarantine.jsonl` and return HTTP `422 Unprocessable Entity`.
- **Zero Quota Bleed & Observability**: Support `LLM_STUB=1` returning fixture responses for offline development and testing. Emit single-line structured JSON telemetry logs (`prompt_version`, `model`, tokens, `duration_ms`, `repaired`) to `stdout`.

## Git Commit Conventions

All Git commits across the platform must adhere to the Conventional Commits standard:
- `feat:` for new features (e.g., `feat: Implement root and health endpoints`)
- `fix:` for bug fixes (e.g., `fix: Handle missing title in task validation`)
- `refactor:` for code refactoring without behavior change
- `docs:` for documentation updates (e.g., `docs: Add README run instructions and endpoint table`)
- `test:` for adding or updating tests
- `chore:` for maintenance tasks (e.g., `chore: Initialize FastAPI server setup`)

Use the `-m` git flag for concise or multi-line commit messages (e.g., `git commit -m "feat: Implement POST /tasks with input validation"`).


## File & Directory Organization

- `src/` — Server entry point, route definitions, and route handlers.
- `src/repository/` — Database access layer & connection initialization.
- `src/middleware/` — Auth token verification middleware.
- `src/llm/` — LLM client provider, schema definitions, repair retry loop, and telemetry.
- `prompts/` — Version-controlled prompt engineering specifications (`task-triage-v1.md`).
- `evals/` — Benchmark evaluation test cases (`cases.json`) and evaluation runner (`run_evals.py`).
- `logs/` — Runtime failure logs (`quarantine.jsonl`).
- `scraper/` — Scraper pipeline scripts (`fetcher`, `parser`, `validator`).
- `scraper/cache/` — Saved raw HTML page snapshots.
- `scraper/output/` — Output data files (`books.json`, `errors.json`, `run-report.json`).
- `ai-version/` — Quarantined reference implementations for AI rematch evaluations.
