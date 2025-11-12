# Pulse AI Studio

> Multi-feature AI platform with Chat, Image Generation, Video Creation, CV Maker, and Slide Maker

## Overview

Pulse AI Studio is a production-ready AI platform built with:
- **Frontend**: Next.js 14 (TypeScript, Tailwind CSS, shadcn/ui)
- **Backend**: FastAPI (Python)
- **Workers**: Node.js/Python async job processors
- **Infrastructure**: AWS (Terraform IaC)
- **Auth**: Google OAuth
- **Payment**: Manual verification → PayPal/HyperPay adapters

### Features

1. **Chat** - Multi-provider LLM chat (OpenAI GPT-4/5, Anthropic Claude, Google Gemini)
2. **Images** - Text-to-image via Google Vertex AI Imagen
3. **Videos** - Async video generation (Runway/Pika) with SQS queue
4. **CV Maker** - Export professional CVs as DOCX/PDF
5. **Slide Maker** - Generate presentation slides (PPTX/PDF)

### Pricing Tiers (JOD/month)

- **Starter** (3 JOD): 50k chat tokens, 20 images, 30 video seconds, 1 CV, 1 Slide
- **Plus** (4 JOD): Higher limits
- **Pro** (5 JOD): Highest limits

## Architecture

```
/apps
  /web          # Next.js frontend
  /api          # FastAPI backend
  /workers      # Async job processors
/infra
  /terraform    # AWS infrastructure as code
/packages
  /shared       # Shared types & utilities
/docs           # Documentation & activity logs
```

## Local Development Quickstart

### Prerequisites

- Node.js 18+ & pnpm
- Python 3.11+
- Docker & Docker Compose
- AWS CLI configured

### Setup

```bash
# 1) Install dependencies
pnpm install --frozen-lockfile

# Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r apps/api/requirements.txt

# 2) Configure environment
cp .env.example .env
# Edit .env with your local values

# 3) Start development stack
docker compose -f docker-compose.dev.yml up --build

# 4) Run database migrations
cd apps/api
alembic upgrade head
python scripts/seed_plans.py

# 5) Open in browser
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

### Development Workflow

```bash
# Web development
cd apps/web
pnpm dev

# API development
cd apps/api
uvicorn app.main:app --reload --port 8000

# Run tests
pnpm test          # Frontend tests
pytest             # Backend tests

# Lint & format
pnpm lint:fix      # TypeScript
ruff check --fix . # Python
```

## Infrastructure

All infrastructure is managed via Terraform in `/infra/terraform/`.

### AWS Resources

- **VPC** with 2 subnets
- **EC2** t3.micro (Docker host)
- **RDS** Postgres db.t4g.micro
- **S3** for exports & generated content
- **SQS** for async video jobs
- **ECR** for container images
- **Secrets Manager** for API keys

### Deploy to AWS

```bash
cd infra/terraform/environments/dev
terraform init
terraform plan
terraform apply

# Deploy application
git tag v0.1.0
git push origin v0.1.0
# GitHub Actions will build & deploy
```

## Security

- All secrets stored in AWS Secrets Manager (never in Git)
- Google OAuth for authentication
- Rate limiting (per-IP & per-user)
- Input validation (Pydantic + Zod)
- HTTPS only in production
- CSRF protection, secure cookies

## Monitoring & Logs

- Structured JSON logs to stdout
- Activity log: `docs/ACTIVITY.md`
- Build progress: `build_checklist.json`
- OpenTelemetry tracing (web ↔ api ↔ worker)

## Cost Optimization

- t3.micro/t4g.micro instances
- Minimal always-on resources
- Presigned S3 URLs (no data transfer)
- SQS polling (no idle costs)
- Target: <$50/month on AWS

## Documentation

- [Activity Log](docs/ACTIVITY.md) - Development timeline
- [Technical Specs](docs/technical.md) - API contracts & patterns
- [Architecture Diagram](docs/architecture.mermaid) - System design

## Contributing

1. Follow [Conventional Commits](https://www.conventionalcommits.org/)
2. Run linters before commit (Husky hooks)
3. Update `docs/ACTIVITY.md` for significant changes
4. All PRs require tests

## License

MIT License - see [LICENSE](LICENSE)

## Support

For issues or questions, open a GitHub issue or contact the team.

