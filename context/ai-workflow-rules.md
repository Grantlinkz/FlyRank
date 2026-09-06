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
6. **Milestone A6 (LLM Task Triage)**:
   - Run evaluation suite `python evals/run_evals.py`; achieve $\ge 80\%$ benchmark passing rate.
   - Test prompt injection defense: ensure JSON payloads prevent prompt override.
   - Verify repair retry: malformed JSON triggers exactly one repair round before falling back to `logs/quarantine.jsonl` (HTTP 422).
   - Test stub mode (`LLM_STUB=1`) and kill switch (`LLM_ENABLED=false` -> HTTP 503).
7. **Milestone A7 / W7 (Your First Background Job)**:
   - Run API (`:8000`) and Inngest Dev Server (`npx inngest-cli@latest dev -u http://localhost:8000/api/inngest`).
   - Invoke `say-hello` via Dev Server dashboard (`:8288`); verify 5-second sleep step completes.
   - Send `POST /reports` with `{"topic": "cats"}`; verify immediate HTTP 202 response in <1s.
   - Poll `GET /reports/:id`; verify status flips from `pending` to `done` with output result.
   - Send `POST /reports` with `{"topic": "fail"}`; verify 3 execution attempts with backoff in dashboard and final status `Failed`.
   - Send `POST /reports` without `topic`; verify HTTP 400 Bad Request and zero Inngest jobs created.
   - Observe dashboard for 2 minutes; verify `heartbeat` cron function triggers once per minute logging counts.
8. **Milestone A8 / W7b (PDF Report Generator)**:
   - Verify Playwright Chromium installation (`playwright install chromium`).
   - Run database seed script twice; verify row count does not double (`COUNT(*)` remains consistent).
   - Verify SQL aggregation script outputs 4-section summary JSON (`COUNT`, `SUM`, `AVG`, `GROUP BY`).
   - Inspect rendered PDF: verify $\ge 2$ pages, table rows not cut across page breaks, and table headers repeated.
   - Send `POST /reports`; verify HTTP 201 + file link. Download via `GET /reports/:id/file` and verify PDF opens cleanly.
   - Send two rapid `POST /reports` on the same day; verify second request returns HTTP 200 with identical ID and no duplicate file created. Verify `{ "force": true }` generates a new file.

## The AI Rematch Protocol (Bonus Stage)

Every major task assignment features a bonus "AI Rematch" exercise:

1. **Quarantine Generation**: Prompt an AI assistant to build the target module in a separate directory (`ai-version/`) or isolated branch (e.g., `ai-version/jobs/` for A7, `ai-version/reports/` for A8). Do not overwrite hand-built implementation code.
2. **Verification & Diffing**: Run checkpoint tests against the AI-generated code. Compare hand-built code with AI code using `git diff --no-index`.
3. **Documentation ("AI vs Me")**: Document findings in the assignment README addressing:
   - What did the AI do better (e.g., transaction handling, concise helper)?
   - What did it get wrong or ignore (e.g., missing 400 validation, unparameterized query, unthrottled scraper, leaked service key, sliced PDF rows, missing retry limits)?
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
