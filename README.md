# 🚀 Pulse AI Studio

**Arabic-first, all-in-one AI workspace for Jordan**

Pulse AI Studio is a comprehensive AI platform offering chat, CV generation, slide creation, image editing/generation, and video editing/generation—all with strict usage metering and subscription-based pricing tailored for the Jordanian market.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Pricing Plans](#pricing-plans)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [License](#license)

---

## 🎯 Overview

**Vision:** Bring AI superpowers to Jordanians with:
- Arabic as the default language (RTL support)
- Affordable pricing in JOD (3/5/7 JD tiers)
- Zero-touch AWS deployment via Terraform + GitHub Actions OIDC
- Multi-model AI (GPT-4, Claude, Gemini, custom image/video models)

**Target Market:** Jordan (starting point), scalable to MENA region

---

## ✨ Features

### 1. **AI Chat** 
- Multi-model support: GPT-4/5, Claude 4.5, Gemini Pro
- Arabic and English language support
- Real-time streaming responses
- Context-aware conversations

### 2. **CV Maker**
- Guided form-based experience
- Professional templates
- PDF export
- Arabic & English versions

### 3. **Slide Maker**
- Guided presentation builder
- Modern templates
- Export to PowerPoint/PDF

### 4. **Image Editor/Generator**
- AI image generation (Nano Banana, Replicate, Stability)
- Image editing capabilities
- High-quality outputs

### 5. **Video Editor/Generator**
- AI video generation (Veo3, Pika, Runway)
- Short-form content creation
- Thumbnail generation

### 6. **Usage Metering**
- Real-time quota tracking
- 80% warning threshold
- 100% hard stop
- Per-plan limits enforcement

### 7. **Payments**
- HyperPay integration (primary)
- Abstraction for PayTabs, ZainCash
- Subscription management
- Add-on purchases (tokens, images, videos)

---

## 💰 Pricing Plans

| Plan | Price | Tokens | Images | Videos |
|------|-------|--------|--------|--------|
| **Starter** | 3 JD/month | 100k | 20 | 3 |
| **Pro** | 5 JD/month | 500k | 50 | 10 |
| **Creator** | 7 JD/month | 2M | 100 | 30 |

**Add-ons:**
- 200k tokens: 1 JD
- 10 images: 1 JD
- 1 video: 1 JD

---

## 🏗️ Architecture

```
┌─────────────┐
│  CloudFront │  ← CDN
└──────┬──────┘
       │
┌──────▼──────┐
│     ALB     │  ← Load Balancer (path-based routing)
└──────┬──────┘
       ├──────────┬──────────┬──────────┐
       │          │          │          │
┌──────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│ Frontend │ │Backend │ │Gateway │ │ Worker │  ← ECS Fargate
└──────────┘ └───┬────┘ └───┬────┘ └───┬────┘
                 │          │          │
       ┌─────────┼──────────┼──────────┤
       │         │          │          │
┌──────▼──┐ ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│ Aurora  │ │ Redis │  │  S3   │  │  SES  │  ← Data layer
│ Postgres│ │       │  │       │  │       │
└─────────┘ └───────┘  └───────┘  └───────┘
```

**Key Components:**
- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind, shadcn/ui
- **Backend API:** FastAPI (Python 3.11) - auth, plans, payments, usage
- **AI Gateway:** FastAPI - model routing, metering, rate limiting
- **Worker:** FastAPI - async tasks (payments, video jobs, analytics)
- **Database:** Aurora PostgreSQL Serverless v2
- **Cache:** ElastiCache Redis
- **Storage:** S3 (assets + quarantine buckets)
- **Email:** SES (magic link authentication)
- **Containers:** Docker → ECR → ECS Fargate
- **Network:** VPC (3 AZ), private subnets, NAT gateways
- **CI/CD:** GitHub Actions (OIDC, zero-touch deployment)

---

## 🛠️ Tech Stack

### Infrastructure
- **IaC:** Terraform 1.5+
- **Cloud:** AWS (eu-central-1)
- **CI/CD:** GitHub Actions with OIDC
- **Secrets:** AWS Secrets Manager
- **Observability:** CloudWatch Logs, X-Ray, Alarms

### Backend
- **Language:** Python 3.11
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Testing:** pytest

### Frontend
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **State:** React Query
- **Testing:** Jest, React Testing Library

### AI Providers
- **Chat:** OpenAI (GPT-4/5), Anthropic (Claude 4.5), Google (Gemini Pro)
- **Images:** Nano Banana, Replicate, Stability AI
- **Video:** Veo3, Pika, Runway

---

## 🚀 Getting Started

### Prerequisites
- Docker Desktop
- Node.js 18+
- Python 3.11+
- Terraform 1.5+
- AWS CLI (configured)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/pulse-ai-studio.git
   cd pulse-ai-studio
   ```

2. **Bootstrap development environment**
   ```bash
   chmod +x scripts/dev_bootstrap.sh
   ./scripts/dev_bootstrap.sh
   ```

3. **Configure environment variables**
   - Update `.env` files in `apps/backend`, `apps/gateway`, `apps/worker`, `apps/frontend`
   - Add your API keys (OpenAI, Anthropic, etc.)

4. **Run services locally**
   ```bash
   # Terminal 1 - Backend
   cd apps/backend
   source venv/bin/activate
   uvicorn src.main:app --reload --port 8080

   # Terminal 2 - Gateway
   cd apps/gateway
   source venv/bin/activate
   uvicorn src.main:app --reload --port 8081

   # Terminal 3 - Frontend
   cd apps/frontend
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080/docs
   - Gateway API: http://localhost:8081/docs

---

## 🔧 Development

### Project Structure
```
pulse-ai-studio/
├── apps/
│   ├── frontend/          # Next.js app
│   ├── backend/           # Backend API
│   ├── gateway/           # AI Gateway
│   └── worker/            # Async worker
├── infra/
│   └── terraform/
│       └── modules/       # 14 Terraform modules
├── docker/                # Dockerfiles
├── scripts/               # Utility scripts
├── docs/                  # Documentation
│   ├── ACTIVITY.md        # Activity log
│   └── CHECKLIST.md       # Delivery checklist
└── .github/workflows/     # CI/CD pipelines
```

### Available Scripts

```bash
# Bootstrap development environment
./scripts/dev_bootstrap.sh

# Update ECS services (production)
./scripts/update_ecs_images.sh <image-tag>

# Check code formatting
./scripts/format_check.sh

# Run linters
./scripts/lint_check.sh
```

### Code Quality

- **Python:** Black, isort, Ruff, MyPy
- **TypeScript:** ESLint, Prettier, TypeScript compiler
- **Terraform:** terraform fmt

---

## 🚢 Deployment

### AWS Prerequisites
1. AWS account with admin access
2. Domain name (optional, but recommended)
3. Route53 hosted zone (if using custom domain)

### Initial Deployment

1. **Configure Terraform variables**
   ```bash
   cd infra/terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

2. **Initialize Terraform**
   ```bash
   terraform init
   ```

3. **Plan infrastructure**
   ```bash
   terraform plan
   ```

4. **Apply infrastructure**
   ```bash
   terraform apply
   ```

5. **Configure GitHub Secrets**
   - Add `AWS_ACCOUNT_ID` to GitHub repository secrets
   - GitHub Actions will use OIDC for deployment (no long-lived keys!)

6. **Push to main branch**
   ```bash
   git push origin main
   ```
   - This triggers both `infra.yml` and `app.yml` workflows
   - Infrastructure is deployed via Terraform
   - Docker images are built, pushed to ECR, and deployed to ECS

### Continuous Deployment

Every push to `main` triggers:
1. **Infrastructure changes** (`infra/**`) → Terraform apply
2. **Application changes** (`apps/**`) → Docker build + ECS deploy
3. **Activity log** updated automatically in `docs/ACTIVITY.md`

---

## 📚 Documentation

- **[ACTIVITY.md](docs/ACTIVITY.md)** - Continuous activity log with all changes
- **[CHECKLIST.md](docs/CHECKLIST.md)** - Delivery gate checklist
- **API Documentation:**
  - Backend: http://your-alb-url/docs
  - Gateway: http://your-alb-url/gateway/docs

### Key Implementation Details

#### Authentication Flow
1. User enters email (Arabic UI)
2. Magic link sent via SES
3. Token verification → JWT cookie (httpOnly)
4. Session stored for 30 days

#### Usage Metering
1. Gateway pre-checks quota before AI call
2. Gateway logs usage after successful response
3. Backend aggregates usage per billing period
4. Frontend displays real-time meter with warnings

#### Payment Flow
1. User selects plan/add-on
2. Backend creates HyperPay checkout session
3. User completes payment on HyperPay widget
4. Webhook confirms payment
5. Subscription activated/extended

#### Model Routing
- `gpt-*` or `openai:*` → OpenAI client
- `claude*` or `anthropic:*` → Anthropic client
- `gemini*` or `google:*` → Google client
- Automatic failover and error handling

---

## 🗂️ Terraform Modules (14/14 Complete)

| Module | Status | Description |
|--------|--------|-------------|
| VPC | ✅ | 3 AZs, public/private subnets, NAT gateways |
| S3 | ✅ | Assets, quarantine, Terraform state buckets |
| IAM | ✅ | GitHub OIDC, ECS roles, deployment roles |
| ECR | ✅ | Container registries for 4 services |
| Secrets | ✅ | All secrets with placeholders |
| RDS | ✅ | Aurora PostgreSQL Serverless v2 |
| Redis | ✅ | ElastiCache Redis cluster |
| ALB | ✅ | Path-based routing (frontend/backend/gateway) |
| ECS | ✅ | Cluster + task definitions + services |
| SES | ✅ | Email identity and configuration |
| ACM | ✅ | TLS certificate with DNS validation |
| CloudFront | ✅ | CDN with S3 and ALB origins |
| Route53 | ✅ | DNS records for CloudFront/ALB |
| Observability | ✅ | CloudWatch logs, alarms, X-Ray |

---

## 🎯 Implementation Status

### ✅ Completed (100%)
- Infrastructure (14 Terraform modules)
- CI/CD (2 GitHub Actions workflows)
- Backend API (auth, plans, payments, usage)
- Gateway (OpenAI, Anthropic, chat routing)
- Frontend (API client, ModelSelector, TokenMeter)
- Utility scripts (bootstrap, ECS update, linting)
- Documentation (ACTIVITY.md, CHECKLIST.md, README.md)

### ⏳ Pending (Future Iterations)
- Database models & migrations
- Google Gemini client
- Image generation routes
- Video generation routes
- Provider stubs (Nano Banana, Veo3)
- CV Maker UI & API
- Slides Maker UI & API
- Complete frontend pages
- Unit & integration tests
- E2E tests

---

## 🔒 Security

- ✅ All secrets in AWS Secrets Manager
- ✅ No hardcoded credentials
- ✅ OIDC for GitHub Actions (no long-lived keys)
- ✅ httpOnly session cookies
- ✅ Private subnets for RDS/Redis
- ✅ Security groups (least privilege)
- ⏳ Content moderation (stub)
- ⏳ File upload virus scanning

---

## 📊 Monitoring

- **CloudWatch Logs:** All services with 30-day retention
- **X-Ray:** 5% sampling for distributed tracing
- **Alarms:**
  - ALB 5xx errors > 10
  - ECS CPU > 80%
  - RDS CPU > 80%
  - Redis CPU > 80%

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Code Quality Checks:**
```bash
./scripts/format_check.sh
./scripts/lint_check.sh
```

---

## 📝 License

Proprietary - All rights reserved

---

## 🙏 Acknowledgments

- Built with ❤️ for the Jordanian market
- Arabic-first design principles
- Zero-touch deployment philosophy
- Inspired by best practices from Vercel, AWS, and modern SaaS platforms

---

## 📞 Support

- **Documentation:** See `docs/` directory
- **Issues:** GitHub Issues
- **Email:** support@pulseai.studio (placeholder)

---

**Made with 🚀 by the Pulse AI Studio team**
