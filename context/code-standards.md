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

## File & Directory Organization

- `src/` — Server entry point, route definitions, and route handlers.
- `src/repository/` — Database access layer & connection initialization.
- `src/middleware/` — Auth token verification middleware.
- `scraper/` — Scraper pipeline scripts (`fetcher`, `parser`, `validator`).
- `scraper/cache/` — Saved raw HTML page snapshots.
- `scraper/output/` — Output data files (`books.json`, `errors.json`, `run-report.json`).
