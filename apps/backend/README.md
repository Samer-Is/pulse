# Pulse AI Studio - Backend API

FastAPI-based backend API for authentication, payments, usage tracking, and file generation.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (or AWS Aurora)
- Redis

### Installation

```bash
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Running Locally

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload --port 8080

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Project Structure

```
apps/backend/
├── src/
│   ├── main.py                  # FastAPI app
│   ├── core/                    # Core modules
│   │   ├── config.py           # Settings & secrets
│   │   ├── db.py               # Database connection
│   │   ├── logging.py          # Structured logging
│   │   ├── security.py         # JWT & auth
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py
│   │   ├── plan.py
│   │   ├── usage.py
│   │   ├── payment.py
│   │   ├── file.py
│   │   └── job.py
│   ├── schemas/                 # Pydantic schemas
│   ├── api/v1/                  # API routes
│   │   ├── auth.py
│   │   ├── plans.py
│   │   ├── payments.py
│   │   ├── usage.py
│   │   ├── files.py
│   │   ├── cv.py
│   │   └── slides.py
│   ├── services/                # Business logic
│   │   ├── emails.py
│   │   ├── files.py
│   │   ├── cv_docx.py
│   │   ├── slides_pptx.py
│   │   └── payments/
│   │       ├── base.py
│   │       ├── hyperpay.py
│   │       ├── paytabs.py
│   │       └── zaincash.py
│   └── migrations/              # Alembic migrations
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## Environment Variables

See `.env.example` for all required configuration.

### AWS Secrets Manager Integration

You can reference secrets directly in `.env`:

```bash
DATABASE_URL=aws:secretsmanager:AI_STUDIO_DATABASE_URL
JWT_SECRET=aws:secretsmanager:AI_STUDIO_JWT_SECRET
```

The app will automatically fetch these from Secrets Manager on startup.

## Development

### Code Style

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## Deployment

Built as Docker image and deployed to AWS ECS Fargate. See `/docker/backend.Dockerfile`.

## API Endpoints

### Authentication
- `POST /v1/auth/magic-link` - Request magic link
- `POST /v1/auth/magic-link/verify` - Verify and login

### Plans
- `GET /v1/plans` - List plans

### Payments
- `POST /v1/payments/session` - Create payment session
- `POST /v1/payments/webhook/hyperpay` - Payment webhook

### Usage
- `GET /v1/usage/me` - Get current usage

### Files
- `GET /v1/files/{id}/signed-url` - Get download URL

### CV Maker
- `POST /v1/cv/generate` - Generate CV

### Slides
- `POST /v1/slides/generate` - Generate slides

See full API contracts in `/docs/API_CONTRACTS.md`.

