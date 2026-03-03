# DevPulse Backend

Production-grade FastAPI backend for DevPulse developer tool.

## Requirements

- Python 3.11+
- FastAPI
- httpx
- uvicorn

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check → `{"status": "ok"}` |
| GET | `/api/dashboard` | Health data placeholder → `{}` |
| GET | `/api/api-details` | List of 15 API objects |
| POST | `/api/compatibility` | API compatibility check |
| POST | `/api/generate` | Code generation |
| POST | `/api/docs` | Documentation search |

## Request/Response Examples

### POST /api/compatibility
```json
// Request
{"api1": "GitHub API", "api2": "Stripe API"}

// Response
{"score": 0, "path": [], "reason": ""}
```

### POST /api/generate
```json
// Request
{"use_case": "Build a payment integration"}

// Response
{"code": "", "apis_used": [], "status": "success"}
```

### POST /api/docs
```json
// Request
{"question": "How to authenticate with OAuth?"}

// Response
{"summary": "", "sources": [], "status": "success"}
```

## Error Response Format

All errors return consistent JSON:
```json
{"error": "Error message", "status": "error"}
```

## Input Validation

- All string inputs must be non-empty
- Maximum 500 characters per field
