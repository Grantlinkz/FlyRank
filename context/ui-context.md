# UI & Developer Experience Context — FlyRank Platform

## Visual Theme & API Environment

As a backend-focused platform, the user interface centers on the interactive API documentation console served at `/docs` (Swagger UI), alongside consistent JSON error/success formatting in terminal outputs (curl) and API client interfaces (Postman, Hoppscotch).

- **Swagger UI Theme**: Dark technical workspace layout with dark slate background (`#1a1d24`), layered card surfaces, high-contrast typography, and vivid status indicators.
- **Interactive OpenAPI Console**: Served at `/docs` with a visible "Authorize" padlock button allowing developers to input Bearer JWT tokens and test protected endpoints directly from the browser.

## API Response Formatting & Standard Contracts

All server responses must follow a strict, predictable JSON shape.

### Success Response Shapes

- **Root Info (`GET /`)**:
  ```json
  { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }
  ```
- **Health Check (`GET /health`)**:
  ```json
  { "status": "ok" }
  ```
- **Resource Representation (`GET /tasks/:id`, `POST /tasks`, `PUT /tasks/:id`)**:
  ```json
  { "id": 1, "title": "Buy milk", "done": false }
  ```
- **Resource Collection (`GET /tasks`)**:
  ```json
  [
    { "id": 1, "title": "Buy milk", "done": false },
    { "id": 2, "title": "Review PR", "done": true }
  ]
  ```

- **Task Triage Representation (`POST /tasks/triage`)**:
  ```json
  {
    "category": "bug",
    "urgency": "high",
    "estimated_effort": "medium_task",
    "confidence": 0.95,
    "reason": "Direct failure in resource deletion degrades system reliability."
  }
  ```

- **Background Job Accepted (`POST /reports` - Fast Door)**:
  ```json
  {
    "id": "rep_a1b2c3d4",
    "status": "pending"
  }
  ```

- **Background Job Status Polling (`GET /reports/:id`)**:
  ```json
  {
    "id": "rep_a1b2c3d4",
    "topic": "cats",
    "status": "done",
    "result": "Report completed successfully"
  }
  ```

- **PDF Report Generation / Link (`POST /reports`, `GET /reports/:id`)**:
  ```json
  {
    "id": 1,
    "file": "/reports/1/file",
    "created_at": "2026-09-06T12:00:00"
  }
  ```

- **File Download Stream (`GET /reports/:id/file`)**:
  - `Content-Type: application/pdf`
  - Returns raw binary PDF bytes directly from disk storage via `FileResponse`.

### Error Response Contract

All errors must return a JSON object containing a top-level `error` key with a human-readable explanation:
```json
{ "error": "Descriptive error message" }
```

## HTTP Status Code Conventions

| Status Code | Meaning | Usage Context |
| ----------- | ------- | ------------- |
| `200 OK` | Request succeeded / Idempotent Hit | `GET` requests, `PUT` updates, `POST /auth/login`, `POST /tasks/triage`, duplicate `POST /reports` (cached report) |
| `201 Created` | Resource created | `POST /tasks`, `POST /auth/signup`, fresh `POST /reports` (new PDF generated) |
| `202 Accepted` | Accepted for background execution | `POST /reports` (fast-door background job dispatched to Inngest) |
| `204 No Content` | Succeeded with empty body | `DELETE /tasks/:id`, `POST /auth/logout` |
| `400 Bad Request` | Client payload validation failed | Missing or empty `title`, missing `topic` on reports, invalid credentials |
| `401 Unauthorized` | Authentication failed or missing | Missing, malformed, or expired JWT Bearer token |
| `403 Forbidden` | Authenticated user unauthorized | Authenticated user lacks permission for target resource |
| `404 Not Found` | Resource or endpoint missing | Requesting non-existent task ID, report ID, or unknown route |
| `422 Unprocessable` | Unrepairable model schema failure | Model output failed validation after repair retry (quarantined) |
| `429 Too Many Requests` | Rate limit exceeded | Excessive requests or provider rate limit |
| `502 Bad Gateway` | Upstream provider error | LLM provider failure or network disruption |
| `503 Service Unavailable` | Service feature disabled | LLM triage disabled via `LLM_ENABLED=false` kill switch |
| `504 Gateway Timeout` | Request timeout exceeded | LLM call exceeded explicit 30s timeout |

## Swagger UI Configuration

- **Spec Location**: Served at `/docs` via `swagger-ui-express` (Node) or FastAPI's automatic docs engine.
- **Security Scheme**: OpenAPI 3.0 `securitySchemes` configuration:
  ```json
  {
    "BearerAuth": {
      "type": "http",
      "scheme": "bearer",
      "bearerFormat": "JWT"
    }
  }
  ```
- **Endpoint Protection**: Protected routes (`/protected/profile`, `/auth/logout`, `/tasks/*`) must display the lock icon in Swagger UI and require authorization before execution.
