# AI Workflow Rules — FlyRank Platform

## Approach

Development follows a spec-driven, stage-by-stage workflow. Context files and assignment specifications define what to build, how to structure components, and what checkpoints prove success. Always build incrementally against these specs.

## Scoping & Stage Delivery Rules

- Work on **one assignment stage at a time** (e.g., Stage 0 through Stage 6/7 per assignment).
- Prefer small, verifiable increments over large speculative code generation.
- Do not combine unrelated system boundaries (e.g., setting up Docker infrastructure and writing scraping parsers in one step).
- Each stage must terminate with an explicit verification checkpoint command.
- Commit code to Git at every checkpoint using Conventional Commits format (`feat:`, `docs:`, `chore:`, etc. with `-m`).

## Verification Checkpoints per Milestone

1. **Milestone A1 (CRUD API)**:
   - Verify `GET /`, `GET /health`, `GET /tasks`, `GET /tasks/:id`, `POST /tasks`, `PUT /tasks/:id`, `DELETE /tasks/:id`.
   - Confirm status codes: 200, 201, 204, 400, 404.
2. **Milestone A2 (SQLite Database)**:
   - Restart app 3 times; verify row count in `tasks.db` remains 3 (seed runs only once).
   - Test SQL read/write/delete operations using parameterized queries.
3. **Milestone A3 (Containerization & Postgres)**:
   - Run `docker compose up`; verify app connects to Postgres container (`db:5432`).
   - Run `docker compose down` and `docker compose up`; confirm data persists via `taskdata` volume.
4. **Milestone A4 (Auth & Supabase)**:
   - Test signup (`POST /auth/signup`) and login (`POST /auth/login`).
   - Verify protected route (`GET /protected/profile`) returns `200` with valid JWT and `401` with missing or tampered token.
5. **Milestone A5 (Polite Scraper)**:
   - Verify local cache hits on secondary run (`FETCH` vs `CACHE HIT`).
   - Confirm `output/books.json` holds 60 validated records.
   - Inject deliberate 404 URL; verify scraper logs failure in `output/run-report.json` (`failed_pages: 1`) and completes without crashing.

## The AI Rematch Protocol (Bonus Stage)

Every major task assignment features a bonus "AI Rematch" exercise:

1. **Quarantine Generation**: Prompt an AI assistant to build the target module in a separate directory (`ai-version/`) or isolated branch. Do not overwrite hand-built implementation code.
2. **Verification & Diffing**: Run checkpoint tests against the AI-generated code. Compare hand-built code with AI code using `git diff --no-index`.
3. **Documentation ("AI vs Me")**: Document findings in the assignment README addressing:
   - What did the AI do better (e.g., transaction handling, concise helper)?
   - What did it get wrong or ignore (e.g., missing 400 validation, unparameterized query, unthrottled scraper, leaked service key)?
   - What did the prompt fail to specify, and what did the AI silently decide?

## Protected Files & Boundaries

Do not modify without explicit user instruction:
- `components/ui/*` (if UI library files exist).
- Third-party library internals.
- `.env` secret values (modify `.env.example` instead for schema changes).

## Definition of Done for any Unit

1. Code executes end-to-end within defined scope.
2. Architecture invariants in `architecture.md` are respected.
3. Checkpoint verification commands pass cleanly.
4. `progress-tracker.md` is updated to reflect completed progress and session state.
