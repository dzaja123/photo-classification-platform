# API Documentation

## Base URLs

| Service | URL | Description |
|---------|-----|-------------|
| Auth | `http://localhost:8001` | Authentication & user management |
| Application | `http://localhost:8002` | Photo upload & classification |
| Admin | `http://localhost:8003` | Admin panel, analytics, audit |

---

## Auth Service (`/api/v1/auth`)

### POST `/api/v1/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": { "id": "uuid", "email": "...", "username": "...", "role": "USER" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Rate Limit:** 3 requests/minute per IP

---

### POST `/api/v1/auth/login`
Authenticate with username/email and password.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Rate Limit:** 5 requests/minute per IP

---

### POST `/api/v1/auth/refresh`
Refresh an expired access token.

**Request Body:**
```json
{ "refresh_token": "eyJ..." }
```

---

### POST `/api/v1/auth/logout`
Revoke tokens. Requires `Authorization: Bearer <access_token>`.

**Request Body:**
```json
{ "refresh_token": "eyJ..." }
```

---

## User Service (`/api/v1/users`)

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update profile (full_name) |
| POST | `/api/v1/users/change-password` | Change password |

---

## Application Service (`/api/v1/submissions`)

All endpoints require `Authorization: Bearer <access_token>`.

### POST `/api/v1/submissions/upload`
Upload a photo for ML classification. Uses `multipart/form-data`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Submitter name |
| age | int | yes | Age (1-150) |
| gender | string | yes | Gender |
| location | string | yes | City/location |
| country | string | yes | Country |
| description | string | no | Optional description |
| photo | file | yes | Image (jpg, png, gif, webp; max 10 MB) |

**Response (201):** Submission object with `classification_status: "pending"`.

### GET `/api/v1/submissions/`
List current user's submissions (paginated).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| page_size | int | 20 | Items per page (max 100) |
| status | string | — | Filter by classification status |

### GET `/api/v1/submissions/{id}`
Get a specific submission by ID (owner only).

### DELETE `/api/v1/submissions/{id}`
Soft-delete a submission (owner only). Returns 204.

### GET `/api/v1/submissions/{id}/photo`
Serve the submission's photo directly. Accepts JWT via `?token=` query parameter to support `<img>` tags. Returns the image bytes with the original MIME type. Cached for 1 hour.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | yes | JWT access token (query parameter) |

---

## Admin Service (`/api/v1/admin`)

All endpoints require `Authorization: Bearer <access_token>` with **ADMIN** role.

### GET `/api/v1/admin/submissions`
List all submissions with advanced filtering and sorting.

| Param | Type | Description |
|-------|------|-------------|
| age_min / age_max | int | Age range |
| gender | list[str] | Filter by gender |
| country | list[str] | Filter by country |
| location | string | Partial match |
| classification_status | string | pending/processing/completed/failed |
| classification_result | string | Filter by class label |
| date_from / date_to | datetime | Date range (ISO 8601) |
| search | string | Search name, location, country |
| sort_by | string | Column to sort (default: created_at) |
| sort_order | string | asc / desc |
| page / page_size | int | Pagination |

### GET `/api/v1/admin/analytics`
Aggregated dashboard statistics.

### GET `/api/v1/admin/audit-logs`
Paginated audit log entries with filters.

### GET `/api/v1/admin/audit-logs/user/{user_id}`
Activity timeline for a specific user.

### GET `/api/v1/admin/audit-logs/security`
Security event summary (failed logins, rate limits, etc.).

### GET `/api/v1/admin/export/submissions/csv`
Export filtered submissions as CSV download.

### GET `/api/v1/admin/export/submissions/json`
Export filtered submissions as JSON download.
