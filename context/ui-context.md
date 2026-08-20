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

### Error Response Contract

All errors must return a JSON object containing a top-level `error` key with a human-readable explanation:
```json
{ "error": "Descriptive error message" }
```

## HTTP Status Code Conventions

| Status Code | Meaning | Usage Context |
| ----------- | ------- | ------------- |
| `200 OK` | Request succeeded | `GET` requests, `PUT` updates, `POST /auth/login` |
| `201 Created` | Resource created | `POST /tasks`, `POST /auth/signup` |
| `204 No Content` | Succeeded with empty body | `DELETE /tasks/:id`, `POST /auth/logout` |
| `400 Bad Request` | Client payload validation failed | Missing or empty `title`, missing credentials |
| `401 Unauthorized` | Authentication failed or missing | Missing, malformed, or expired JWT Bearer token |
| `403 Forbidden` | Authenticated user unauthorized | Authenticated user lacks permission for target resource |
| `404 Not Found` | Resource or endpoint missing | Requesting non-existent task ID or unknown route |
| `429 Too Many Requests` | Rate limit exceeded | Excessive login attempts or rapid requests |

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
