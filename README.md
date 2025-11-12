# 🚀 Pulse AI Studio

> Enterprise-grade multi-feature AI platform with Chat, Image Generation, Video Creation, CV Maker, and Slide Maker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![GitHub](https://img.shields.io/badge/github-Samer--Is%2Fpulse-blue)](https://github.com/Samer-Is/pulse)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [License](#license)

## 🎯 Overview

Pulse AI Studio is a comprehensive, **production-ready** AI-powered SaaS platform providing:

✨ **Multi-Provider AI Chat**: OpenAI GPT-4/5, Anthropic Claude 3.5/4, Google Gemini  
🖼️ **Image Generation**: Text-to-image with Google Vertex AI Imagen  
🎥 **Video Generation**: Async video creation with Runway and Pika (mock ready)  
📄 **CV Builder**: Professional resume creation with DOCX/PDF export  
📊 **Slide Maker**: AI-powered presentation generation with PPTX/PDF export  
💳 **Subscription Management**: Stripe-powered billing with quota enforcement  
📈 **Admin Dashboard**: Complete platform analytics and user management  
🔒 **Enterprise Security**: OAuth 2.0, JWT, rate limiting, CORS, CSP, HSTS  

**Built with modern, scalable architecture:**
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python 3.11), SQLAlchemy (async), Alembic migrations
- **Workers**: Node.js async job processing with SQS
- **Infrastructure**: AWS managed services (EC2, RDS, S3, SQS) via Terraform
- **Payments**: Stripe subscriptions with webhook integration

## ✨ Features

### 💬 Multi-Provider Chat
- Support for **OpenAI** (GPT-4, GPT-3.5-turbo), **Anthropic** (Claude 3), **Google** (Gemini)
- **Streaming responses** with Server-Sent Events (SSE)
- Token counting and usage tracking
- Model switching with unified interface
- **Frontend**: Real-time chat UI with message history

### 🖼️ Image Generation
- **Google Vertex AI Imagen** integration
- Batch generation (1-4 images per request)
- S3 storage with presigned URLs
- **Frontend**: Image gallery with download functionality

### 🎥 Video Generation
- **Async processing** with SQS queue
- Node.js worker service for long-running jobs
- Real-time progress tracking with SSE
- Mock providers ready for Runway/Pika integration
- **Frontend**: Progress bar and video preview

### 📄 CV Maker
- Comprehensive resume builder form (personal info, experience, education, skills)
- Professional templates with **python-docx**
- PDF generation with **Playwright** headless browser
- DOCX and PDF export formats
- **Frontend**: Multi-section form with dynamic entries

### 📊 Slide Maker
- **AI-powered outline generation** (OpenAI/Anthropic)
- Manual slide editing mode with full control
- PPTX generation with **python-pptx**
- PDF export with custom styling
- **Frontend**: Dual-mode UI (AI generate + manual entry)

### 💳 Subscription Management
- **Stripe Checkout** integration for plan purchases
- **Customer Portal** for self-service subscription management
- Webhook-driven subscription synchronization
- **Three tiers**: Starter ($9), Plus ($29), Pro ($99)
- Quota enforcement per feature (tokens, images, videos, CVs, slides)

### 📈 Admin Dashboard
- **User management**: Activate/deactivate users, assign admin roles
- **Subscription overview**: Filter by plan and status
- **Usage analytics**: Platform metrics, revenue tracking
- **Job statistics**: Monitor async jobs by type and status
- **Frontend**: Clean, responsive admin UI with tabs

### 🔒 Security & Compliance
- **Google OAuth 2.0** authentication
- **JWT-based** session management
- **Rate limiting** (per IP and per user)
- **Quota enforcement** per subscription tier
- **Security headers**: CSP, HSTS, X-Frame-Options, Permissions-Policy
- **Input validation** and sanitization
- **Structured JSON logging** for audit trails
- **Global error handling** with context

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
       ┌───────▼────────┐        ┌────────▼─────────┐
       │   Next.js Web  │        │  Stripe Checkout │
       │   (Port 3000)  │        │   & Portal       │
       └───────┬────────┘        └──────────────────┘
               │
       ┌───────▼────────────────────────────────────┐
       │         FastAPI Backend (Port 8000)        │
       │  ┌──────────────────────────────────────┐  │
       │  │  Routes: /auth, /chat, /images,      │  │
       │  │  /videos, /cv, /slides, /admin       │  │
       │  └──────────────────────────────────────┘  │
       │  ┌──────────────────────────────────────┐  │
       │  │  Middleware: Security, Rate Limit,   │  │
       │  │  CORS, Request Validation            │  │
       │  └──────────────────────────────────────┘  │
       └───┬────────┬────────┬────────┬────────────┘
           │        │        │        │
    ┌──────▼──┐  ┌─▼───┐  ┌─▼──┐  ┌─▼─────────┐
    │PostgreSQL│  │ S3  │  │SQS │  │ AI APIs   │
    │  (RDS)   │  │     │  │    │  │ (External)│
    └──────────┘  └─────┘  └─┬──┘  └───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Node.js Workers   │
                    │  (Async Jobs)      │
                    └────────────────────┘
```

### Component Responsibilities

- **Next.js Frontend**: User interface, forms, real-time updates (SSE)
- **FastAPI Backend**: REST API, authentication, business logic, AI integrations
- **PostgreSQL (RDS)**: User data, subscriptions, jobs, usage events
- **S3**: File storage for exports (CVs, slides, images, videos)
- **SQS**: Job queue for async processing (video generation)
- **Node.js Workers**: Async job processing, video generation with mock providers
- **Stripe**: Payment processing and subscription lifecycle management
- **AI Providers**: OpenAI (chat), Anthropic (chat), Google Vertex AI (chat + images)

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router), React 18
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.4, shadcn/ui components
- **State Management**: React Hooks, Server-Sent Events for real-time
- **HTTP Client**: Fetch API with custom hooks

### Backend
- **Framework**: FastAPI 0.109 (async)
- **Language**: Python 3.11
- **ORM**: SQLAlchemy 2.0 (async with asyncpg)
- **Migrations**: Alembic 1.13
- **Validation**: Pydantic 2.6 with strict type checking
- **Logging**: python-json-logger for structured logs

### Workers
- **Runtime**: Node.js 20+ (TypeScript 5.3)
- **Queue**: AWS SQS with long polling
- **Database**: pg (PostgreSQL client for job updates)
- **HTTP**: axios for API callbacks

### Infrastructure
- **IaC**: Terraform 1.6+ with modular architecture
- **Cloud**: AWS (EC2 t3.micro, RDS db.t4g.micro, S3, SQS, ECR, Secrets Manager)
- **Containers**: Docker, Docker Compose (dev + prod)
- **CI/CD**: GitHub Actions (lint, test, build, deploy)

### AI & External Services
- **Chat**: OpenAI (GPT-4, GPT-3.5-turbo), Anthropic (Claude 3), Google Vertex AI (Gemini)
- **Images**: Google Vertex AI Imagen
- **Videos**: Runway, Pika (mock implementation with placeholder URLs)
- **Documents**: python-docx (DOCX), python-pptx (PPTX), Playwright (PDF)
- **Payments**: Stripe Checkout + Customer Portal + Webhooks

### Code Quality & Tools
- **Linting**: ESLint (JS/TS), Ruff (Python)
- **Formatting**: Prettier, Black
- **Type Checking**: TypeScript strict, mypy
- **Git Hooks**: Husky + lint-staged
- **Commit Format**: Conventional Commits
- **Monorepo**: pnpm workspaces + Turborepo

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ and **pnpm** 8+
- **Python** 3.11+
- **Docker** and **Docker Compose**
- AWS Account (for deployment)
- **API Keys**: OpenAI, Anthropic, Google Cloud (Vertex AI), Stripe

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Samer-Is/pulse.git
cd pulse

# 2. Install Node.js dependencies
pnpm install

# 3. Set up Python environment (for API development)
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ../..

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Local Development

```bash
# Start PostgreSQL and LocalStack (S3, SQS)
docker-compose -f docker-compose.dev.yml up -d postgres localstack

# Run database migrations
cd apps/api
alembic upgrade head
cd ../..

# Start all services in development mode
pnpm dev

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Full Docker Stack

```bash
# Start all services with Docker Compose
docker-compose -f docker-compose.dev.yml up --build

# This starts:
# - PostgreSQL (port 5432)
# - LocalStack (S3, SQS on port 4566)
# - FastAPI backend (port 8000)
# - Next.js frontend (port 3000)
# - Node.js workers
# - Nginx reverse proxy (port 80)
```

## 📁 Project Structure

```
pulse/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── auth/          # OAuth, JWT authentication
│   │   │   ├── middleware/    # Security, rate limiting, errors
│   │   │   ├── models/        # SQLAlchemy models (User, Subscription, Job, etc.)
│   │   │   ├── providers/     # AI provider integrations (OpenAI, Anthropic, Google)
│   │   │   ├── routers/       # API endpoints (auth, chat, images, videos, cv, slides, admin)
│   │   │   ├── schemas/       # Pydantic request/response schemas
│   │   │   ├── services/      # Business logic (CV, Slide, Stripe services)
│   │   │   └── utils/         # Utilities (S3, SQS, secrets, quota, validation, logging)
│   │   ├── alembic/           # Database migrations
│   │   ├── tests/             # Pytest test suite
│   │   └── requirements.txt
│   │
│   ├── web/                   # Next.js frontend
│   │   ├── src/app/
│   │   │   ├── page.tsx       # Homepage with feature cards
│   │   │   ├── chat/          # Chat interface
│   │   │   ├── images/        # Image generation UI
│   │   │   ├── videos/        # Video generation UI with progress
│   │   │   ├── cv/            # CV builder form
│   │   │   ├── slides/        # Slide maker (AI + manual modes)
│   │   │   └── admin/         # Admin dashboard
│   │   └── package.json
│   │
│   └── workers/               # Node.js async workers
│       ├── src/
│       │   ├── processors/    # Video processor (mock)
│       │   ├── services/      # SQS worker, database
│       │   └── index.ts       # Worker entry point
│       └── package.json
│
├── packages/
│   └── shared/                # Shared TypeScript types
│       └── src/
│           ├── types.ts       # User, Plan, Subscription interfaces
│           └── plans.ts       # Plan definitions
│
├── infra/
│   ├── terraform/             # Infrastructure as Code
│   │   ├── modules/           # Terraform modules
│   │   │   ├── vpc/           # VPC, subnets, IGW
│   │   │   ├── ec2/           # EC2 instance + IAM
│   │   │   ├── rds/           # PostgreSQL RDS
│   │   │   ├── s3/            # S3 bucket
│   │   │   ├── sqs/           # SQS queue + DLQ
│   │   │   ├── ecr/           # ECR repositories
│   │   │   └── secrets/       # Secrets Manager
│   │   └── environments/dev/
│   └── nginx/                 # Nginx reverse proxy configs
│
├── docs/
│   ├── ACTIVITY.md           # Development activity log (all 9 phases)
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── API.md                # API documentation
│
├── .github/workflows/        # GitHub Actions CI/CD
│   ├── ci.yml                # Linting, type-checking, building
│   └── deploy.yml            # ECR push and EC2 deployment
│
├── docker-compose.dev.yml    # Local development stack
├── Makefile                  # Convenience commands
├── turbo.json               # Turborepo config
├── pnpm-workspace.yaml      # pnpm monorepo config
└── build_checklist.json     # Build progress tracker (9/10 phases complete)
```

## 💻 Development

### Available Scripts

```bash
# Development
pnpm dev              # Start all services in dev mode
pnpm build            # Build all packages
pnpm lint             # Run all linters
pnpm lint:fix         # Fix linting issues
pnpm format           # Format code with Prettier
pnpm clean            # Clean build artifacts

# Database
cd apps/api && alembic upgrade head    # Run migrations
cd apps/api && alembic revision -m ""  # Create new migration

# Docker
pnpm docker-up        # Start Docker services
pnpm docker-down      # Stop Docker services

# Testing
cd apps/api && pytest                  # Run API tests
cd apps/web && pnpm test              # Run frontend tests
```

### Code Quality

The project enforces code quality through:
- ✅ **Pre-commit hooks** (Husky + lint-staged)
- ✅ **Conventional Commits** specification
- ✅ **ESLint** for TypeScript/JavaScript
- ✅ **Ruff + Black** for Python formatting
- ✅ **Prettier** for consistent code style
- ✅ **TypeScript strict mode** + **mypy** for type safety
- ✅ **Pydantic** validation for all API inputs

### Key Environment Variables

See `.env.example` for the complete list. Key variables:

```bash
# API
ENVIRONMENT=development
LOG_LEVEL=INFO
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://pulse:pulse@localhost:5432/pulse

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GCP_VERTEX_PROJECT_ID=your-project
GCP_VERTEX_LOCATION=us-central-1
GCP_VERTEX_SA_JSON=base64-encoded-service-account-json

# AWS
AWS_REGION=eu-central-1
S3_BUCKET_NAME=pulse-dev-exports
SQS_QUEUE_URL=http://localstack:4566/000000000000/pulse-jobs

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PLUS=price_...
STRIPE_PRICE_PRO=price_...

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

## 🌐 Deployment

### AWS Infrastructure

The project includes complete Terraform configuration for AWS deployment:

```bash
# 1. Configure AWS credentials
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=eu-central-1

# 2. Initialize Terraform
cd infra/terraform/environments/dev
terraform init

# 3. Review planned changes
terraform plan

# 4. Deploy infrastructure
terraform apply

# Terraform will provision:
# - VPC with public subnets
# - EC2 t3.micro instance
# - RDS PostgreSQL db.t4g.micro
# - S3 bucket for exports
# - SQS queue with DLQ
# - ECR repositories for Docker images
# - Secrets Manager for API keys
```

### Deployed Resources

After `terraform apply`, you'll have:
- **EC2**: Public IP for SSH access and application hosting
- **RDS**: PostgreSQL endpoint for database connection
- **S3**: Bucket for storing generated files (CVs, slides, images, videos)
- **SQS**: Queue URL for async job processing
- **ECR**: Docker registries for API, Web, Workers images

### CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/deploy.yml`):
1. Triggered on git tag push (e.g., `v0.1.0`)
2. Builds Docker images for API, Web, Workers
3. Pushes images to AWS ECR
4. SSHs to EC2 instance
5. Pulls new images and restarts containers

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/google` - Google OAuth callback
- `POST /api/v1/auth/refresh` - Refresh JWT token

**Chat**
- `GET /api/v1/chat/models` - List available models
- `POST /api/v1/chat/complete` - Chat completion
- `POST /api/v1/chat/stream` - Streaming chat (SSE)

**Images**
- `POST /api/v1/images/generate` - Generate 1-4 images
- `GET /api/v1/images/{id}` - Get image details

**Videos**
- `POST /api/v1/videos/generate` - Enqueue video job
- `GET /api/v1/videos/status/{job_id}` - Check status
- `GET /api/v1/videos/stream/{job_id}` - Stream updates (SSE)

**CV & Slides**
- `POST /api/v1/cv/generate` - Generate CV (DOCX/PDF)
- `POST /api/v1/slides/generate-outline` - AI outline generation
- `POST /api/v1/slides/generate` - Generate presentation

**Admin**
- `GET /api/v1/admin/users` - List users (admin only)
- `GET /api/v1/admin/analytics` - Platform metrics
- `PATCH /api/v1/admin/subscriptions/{id}` - Update subscription

**Payments**
- `POST /api/v1/stripe/create-checkout-session` - Stripe checkout
- `POST /api/v1/stripe/create-portal-session` - Customer portal
- `POST /api/v1/stripe/webhook` - Stripe webhooks

**Health**
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness probe (K8s compatible)
- `GET /health/live` - Liveness probe

## 📊 Project Status

**Build Progress**: 9/10 Phases Complete

✅ **Phase 0**: Repo Bootstrap (monorepo, tooling, Docker, CI/CD)  
✅ **Phase 1**: AWS Infrastructure (Terraform, VPC, EC2, RDS, S3, SQS, ECR)  
✅ **Phase 2**: Database & Backend API (SQLAlchemy, Alembic, Auth, Users)  
✅ **Phase 3**: Multi-Provider Chat (OpenAI, Anthropic, Google, streaming)  
✅ **Phase 4**: Image Generation (Vertex AI Imagen, S3 integration)  
✅ **Phase 5**: Video Generation (Async with SQS, Node.js workers, SSE)  
✅ **Phase 6**: CV Maker (DOCX/PDF export, python-docx, Playwright)  
✅ **Phase 7**: Slide Maker (AI outlines, PPTX/PDF, dual-mode UI)  
✅ **Phase 8**: Payments & Admin (Stripe, quotas, analytics dashboard)  
✅ **Phase 9**: Observability & Security (logging, health checks, validation)  
🚧 **Phase 10**: Production Readiness (final docs, testing, optimization)

See `build_checklist.json` and `docs/ACTIVITY.md` for detailed progress.

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow [Conventional Commits](https://www.conventionalcommits.org/)
2. Run linters before commit (enforced by Husky hooks)
3. Add tests for new features
4. Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern frameworks: FastAPI, Next.js, Terraform
- AI providers: OpenAI, Anthropic, Google
- UI components: shadcn/ui, Tailwind CSS, Lucide icons
- Infrastructure: AWS managed services
- Payments: Stripe

---

**Built with ❤️ by Samer Ismail**  
📧 Email: s.ismail@qoad.com  
🔗 GitHub: [@Samer-Is](https://github.com/Samer-Is)
