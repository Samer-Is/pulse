# Architecture Documentation

> System design, component interactions, and dataflow for Pulse AI Studio

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Scalability Considerations](#scalability-considerations)
7. [Deployment Architecture](#deployment-architecture)

---

## Overview

Pulse AI Studio is a multi-tenant, Arabic-first AI platform built on AWS with a microservices architecture. The system is designed for:

- **Scalability:** Serverless databases, auto-scaling ECS services, CloudFront CDN
- **Security:** Private subnets, Secrets Manager, IAM roles, HTTPS/TLS
- **Observability:** CloudWatch logs, X-Ray tracing, structured JSON logging
- **Zero-touch deployment:** Terraform + GitHub Actions OIDC

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Devices                                    │
│                    (Web Browser - Arabic/English UI)                        │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CloudFront (CDN)                                     │
│                  (Static Assets + Frontend Caching)                          │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Application Load Balancer (ALB)                           │
│                  (Path-based routing, SSL termination)                       │
└────────────┬─────────────┬──────────────┬────────────────────────────────────┘
             │             │              │
             ▼             ▼              ▼
    ┌────────────┐  ┌────────────┐  ┌───────────┐
    │  Frontend  │  │  Backend   │  │  Gateway  │
    │   (ECS)    │  │   (ECS)    │  │   (ECS)   │
    │  Next.js   │  │  FastAPI   │  │  FastAPI  │
    │  Public    │  │  Private   │  │  Private  │
    └────────────┘  └─────┬──────┘  └─────┬─────┘
                          │                │
                          │                │
                    ┌─────▼────────────────▼─────┐
                    │    ElastiCache Redis       │
                    │  (Usage, Rate Limiting)    │
                    └────────────────────────────┘
                          │
                          ▼
                 ┌────────────────────┐
                 │  Aurora PostgreSQL │
                 │   Serverless v2    │
                 │    (Private)       │
                 └────────────────────┘
                          │
                          │
    ┌─────────────────────┴──────────────────────┐
    │                                             │
    ▼                                             ▼
┌──────────┐                                  ┌──────────┐
│  Worker  │                                  │    S3    │
│  (ECS)   │◄─────────────────────────────────│  Assets  │
│ Private  │                                  │Quarantine│
└──────────┘                                  └──────────┘
    │
    │ (Async Jobs: Webhooks, Video, Analytics)
    │
    ▼
┌────────────────────────────────────────┐
│       External Services                │
│  - OpenAI (GPT-4/5)                    │
│  - Anthropic (Claude 4.5)              │
│  - Google (Gemini Pro)                 │
│  - Nano Banana (Images)                │
│  - Veo3 (Video)                        │
│  - Replicate/Stability (Fallbacks)     │
│  - HyperPay (Payments)                 │
│  - AWS SES (Email)                     │
└────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (Next.js 15)

**Technology:** Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui, React Query

**Responsibilities:**
- Server-side rendering (SSR) for landing page
- Client-side routing for authenticated app pages
- Model selection UI (dropdown for chat/image/video models)
- Usage meters and quota warnings
- Form-based tools (CV Maker, Slide Maker)
- File uploads and downloads (presigned URLs)
- Arabic/English localization

**Routes:**
- `/` - Landing page (public)
- `/app/chat` - AI chat interface
- `/app/cv` - CV maker form
- `/app/slides` - Slide maker form
- `/app/image` - Image generator + editor
- `/app/video` - Video generator + editor
- `/app/account` - User account, usage, billing

**Deployment:** ECS Fargate (public subnet) behind ALB

---

### 2. Backend API (FastAPI)

**Technology:** Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic

**Responsibilities:**
- User authentication (magic link via SES)
- JWT token generation and validation
- Plan management and subscription logic
- Payment session creation and webhook handling
- Usage tracking and quota enforcement
- File storage orchestration (S3 presigned URLs)
- CV generation (python-docx, weasyprint)
- Slide generation (python-pptx, unoconv)

**Key Endpoints:**
- `POST /v1/auth/magic-link` - Request magic link
- `POST /v1/auth/magic-link/verify` - Verify token, issue JWT
- `GET /v1/plans` - List available plans
- `POST /v1/payments/session` - Create HyperPay checkout
- `POST /v1/payments/webhook/hyperpay` - Handle payment webhooks
- `GET /v1/usage/me` - Get current user usage
- `POST /v1/cv/generate` - Generate CV file
- `POST /v1/slides/generate` - Generate slides file
- `GET /v1/files/{id}/signed-url` - Get download URL

**Deployment:** ECS Fargate (private subnet) behind ALB

---

### 3. AI Gateway (FastAPI)

**Technology:** Python 3.11, FastAPI, Redis, Async HTTP clients

**Responsibilities:**
- Multi-model AI provider routing
- Token/image/video usage metering
- Rate limiting (60 req/60s per user)
- Content moderation hooks
- Provider error handling and retries
- Logging with trace_id for observability

**Key Endpoints:**
- `POST /v1/chat/complete` - Chat completions (OpenAI/Anthropic/Google)
- `POST /v1/images/generate` - Image generation (Nano Banana/fallbacks)
- `POST /v1/video/generate` - Video generation (Veo3/fallbacks)

**Provider Routing Logic:**
```python
if model.startswith("gpt-") or model.startswith("openai:"):
    provider = openai_client
elif model.startswith("claude") or model.startswith("anthropic:"):
    provider = anthropic_client
elif model.startswith("gemini") or model.startswith("google:"):
    provider = google_client
elif model.startswith("nano-banana"):
    provider = nano_banana_client
elif model.startswith("veo3"):
    provider = veo3_client
else:
    provider = default_fallback
```

**Deployment:** ECS Fargate (private subnet) behind ALB

---

### 4. Async Worker (Python)

**Technology:** Python 3.11, Celery/RQ/Custom queue, Boto3

**Responsibilities:**
- Process payment webhooks (HyperPay, PayTabs, ZainCash)
- Video generation job handling (async queue)
- Video finalization (encoding, thumbnailing)
- Analytics aggregation (daily usage reports)
- File cleanup (delete old files, quarantine)

**Job Types:**
- `payment_webhook` - Process successful payments
- `video_generate` - Call Veo3/fallback, upload to S3
- `video_finalize` - Encode, thumbnail, update DB
- `analytics_daily` - Aggregate usage stats
- `cleanup_files` - Delete files older than retention policy

**Deployment:** ECS Fargate (private subnet, no ALB)

---

### 5. Database (Aurora PostgreSQL Serverless v2)

**Schema:**

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    locale VARCHAR(10) DEFAULT 'ar',
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Plans
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    price_jod DECIMAL(10,2) NOT NULL,
    token_limit INT NOT NULL,
    image_limit INT NOT NULL,
    video_limit INT NOT NULL,
    features_json JSONB
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_id UUID REFERENCES plans(id),
    status VARCHAR(50) NOT NULL, -- active, cancelled, expired
    renews_at TIMESTAMP,
    provider VARCHAR(50), -- hyperpay, paytabs, zaincash
    external_ref VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_id UUID REFERENCES plans(id),
    amount_jod DECIMAL(10,2) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, completed, failed
    external_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    meta_json JSONB
);

-- Usage Logs
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    kind VARCHAR(50) NOT NULL, -- tokens, images, video
    amount INT NOT NULL,
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    meta_json JSONB
);
CREATE INDEX idx_usage_user_date ON usage_logs(user_id, created_at);
CREATE INDEX idx_usage_kind ON usage_logs(kind, created_at);

-- Files
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    kind VARCHAR(50) NOT NULL, -- image, video, doc
    s3_key VARCHAR(500) NOT NULL,
    bytes BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    meta_json JSONB
);
CREATE INDEX idx_files_user ON files(user_id, created_at);

-- Jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    kind VARCHAR(50) NOT NULL, -- video_gen, video_edit
    status VARCHAR(50) NOT NULL, -- pending, processing, completed, failed
    payload_json JSONB,
    result_file_id UUID REFERENCES files(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_jobs_status ON jobs(status, created_at);
```

**Seed Data:**
```sql
INSERT INTO plans (name, price_jod, token_limit, image_limit, video_limit, features_json) VALUES
('Starter', 3.00, 150000, 10, 2, '{"cv_maker": true, "slide_maker": false, "pdf_summary": false}'),
('Pro', 5.00, 400000, 30, 5, '{"cv_maker": true, "slide_maker": true, "pdf_summary": true}'),
('Creator', 7.00, 1000000, 60, 10, '{"cv_maker": true, "slide_maker": true, "pdf_summary": true, "advanced_editors": true}');
```

---

### 6. Cache (ElastiCache Redis)

**Purpose:**
- Real-time usage counters (monthly tokens/images/videos per user)
- Rate limiting (sliding window: 60 requests per 60 seconds)
- Session data (optional, if not using JWT-only)

**Key Patterns:**
```
usage:tokens:{user_id}:{year}-{month}  →  INT (token count)
usage:images:{user_id}:{year}-{month}  →  INT (image count)
usage:videos:{user_id}:{year}-{month}  →  INT (video count)
ratelimit:{user_id}:{timestamp_bucket} →  INT (request count)
```

**Sync Strategy:**
- Write-through: increment Redis + async DB write
- Read: check Redis first, fallback to DB if cache miss
- Reset: monthly cron job flushes old keys

---

### 7. Storage (S3)

**Buckets:**
1. `${project}-assets` - Generated files (images, videos, CVs, slides)
2. `${project}-quarantine` - User uploads (pre-scan)
3. `${project}-tfstate` - Terraform remote state

**Access Patterns:**
- **Upload:** Backend/Worker generates presigned POST URL → Client uploads
- **Download:** Backend generates presigned GET URL (time-limited) → Client downloads
- **Security:** Buckets private, no public access, CloudFront as optional CDN origin

---

### 8. CDN (CloudFront)

**Origins:**
- ALB (frontend service)
- S3 assets bucket (optional, for static media)

**Behaviors:**
- Cache static assets (images, videos, CSS, JS)
- Forward auth cookies to origin for authenticated routes
- Compress responses (gzip, brotli)

---

## Data Flow

### 1. User Authentication (Magic Link)

```
User → Frontend: Enter email
Frontend → Backend: POST /v1/auth/magic-link {email}
Backend → SES: Send email with token link
User → Email: Click magic link
Browser → Frontend: Open /verify?token=XXX
Frontend → Backend: POST /v1/auth/magic-link/verify {token}
Backend → JWT: Generate token, store in httpOnly cookie
Backend → Frontend: {user, redirect: /app/chat}
Frontend → Redirect to app
```

### 2. Payment Flow (HyperPay)

```
User → Frontend: Select plan, click "Upgrade"
Frontend → Backend: POST /v1/payments/session {plan_id}
Backend → HyperPay API: Create checkout session
HyperPay → Backend: {checkout_id, redirect_url}
Backend → Frontend: {redirect_url}
Frontend → Redirect to HyperPay
User → HyperPay: Complete payment
HyperPay → Backend: POST /v1/payments/webhook/hyperpay {checkout_id, status}
Backend → Verify signature
Backend → DB: Update payment status, activate subscription
Backend → Worker: Queue email notification (optional)
HyperPay → User: Redirect to success page
Frontend → Display success message
```

### 3. Chat Request (Multi-Model)

```
User → Frontend: Select model (GPT-4), type message
Frontend → Gateway: POST /v1/chat/complete {model: "gpt-4o", messages: [...]}
Gateway → Redis: Check rate limit (60/60s)
Gateway → Redis: Check quota (tokens used this month)
Gateway → Moderation: Check message content
Gateway → Provider Router: Route to OpenAI client
OpenAI Client → OpenAI API: Chat completion request
OpenAI API → OpenAI Client: {choices: [{message: {...}}], usage: {tokens}}
Gateway → Redis: Increment token usage
Gateway → DB (async): Log usage record
Gateway → Frontend: {response, usage_info}
Frontend → Display message + updated token meter
```

### 4. Image Generation

```
User → Frontend: Select model (Nano Banana), enter prompt
Frontend → Gateway: POST /v1/images/generate {model: "nano-banana", prompt, count: 4}
Gateway → Redis: Check image quota
Gateway → Moderation: Check prompt
Gateway → Nano Banana Client: Generate images
Nano Banana → Gateway: [image_data, ...]
Gateway → S3: Upload images to assets bucket
Gateway → DB: Insert file records
Gateway → Redis: Increment image count
Gateway → Frontend: {images: [{id, url}, ...]}
Frontend → Display image grid
```

### 5. Video Generation (Async)

```
User → Frontend: Select model (Veo3), enter prompt
Frontend → Gateway: POST /v1/video/generate {model: "veo3", prompt, duration_s: 15}
Gateway → Redis: Check video quota
Gateway → DB: Create job record (status: pending)
Gateway → Worker Queue: Enqueue video job
Gateway → Frontend: {job_id, status: "pending"}
Frontend → Poll: GET /v1/jobs/{job_id}

(Async in Worker)
Worker → Job: Dequeue video job
Worker → Veo3 Client: Generate video
Veo3 → Worker: Video data (or job_id)
Worker → Poll Veo3: Wait for completion
Worker → S3: Upload video to assets bucket
Worker → DB: Update job (status: completed, result_file_id)
Worker → Redis: Increment video count

(Client polling)
Frontend → Backend: GET /v1/jobs/{job_id}
Backend → DB: {status: "completed", file_id: "..."}
Backend → S3: Generate presigned download URL
Backend → Frontend: {status: "completed", download_url}
Frontend → Display video player with download button
```

### 6. CV/Slide Export

```
User → Frontend: Fill CV form, click "Export DOCX"
Frontend → Backend: POST /v1/cv/generate {name, contact, skills, ...}
Backend → python-docx: Generate DOCX bytes
Backend → S3: Upload to assets bucket
Backend → DB: Insert file record
Backend → S3: Generate presigned URL
Backend → Frontend: {file_id, download_url}
Frontend → Browser download
```

---

## Security Architecture

### Network Security

- **VPC:** 3 Availability Zones, public + private subnets
- **Public Subnets:** ALB, NAT Gateways
- **Private Subnets:** ECS tasks (backend, gateway, worker), RDS, Redis
- **Security Groups:**
  - ALB → Allow 80/443 from Internet
  - ECS → Allow traffic from ALB only
  - RDS → Allow 5432 from ECS security group
  - Redis → Allow 6379 from ECS security group
- **NAT Gateway:** Egress for ECS tasks (call external APIs)

### Application Security

- **Authentication:** JWT tokens in httpOnly cookies (CSRF protection)
- **Authorization:** Middleware validates JWT, extracts user_id
- **Secrets:** AWS Secrets Manager (no hardcoded keys)
- **Input Validation:** Pydantic schemas for all API requests
- **SQL Injection:** SQLAlchemy ORM (parameterized queries)
- **Rate Limiting:** 60 requests per 60 seconds per user (Redis sliding window)
- **Content Moderation:** Pre-provider hooks for text/image content

### Data Security

- **Encryption at Rest:** Aurora (AWS KMS), S3 (SSE-S3), Redis (encryption enabled)
- **Encryption in Transit:** TLS 1.2+ for all connections (ALB, API calls)
- **Presigned URLs:** Time-limited (300s default), prevent direct S3 access
- **PII Handling:** No PII in logs, email masked in analytics

---

## Scalability Considerations

### Horizontal Scaling

- **ECS Auto-Scaling:** Target tracking on CPU/memory (target: 70%)
- **Aurora Serverless:** Auto-scales ACUs (min/max configurable)
- **Redis:** Cluster mode optional (future)

### Vertical Scaling

- **Task CPU/Memory:** Adjustable per service (frontend: 512/1024, backend: 1024/2048, etc.)
- **RDS ACUs:** Min 0.5, Max 8 (configurable)

### Caching Strategy

- **CloudFront:** Cache static assets (TTL: 1 hour)
- **Redis:** Cache usage counters (TTL: 5 minutes)
- **Application:** React Query cache (stale-while-revalidate)

### Bottleneck Mitigation

- **Database:** Indexes on `user_id`, `created_at`, `kind`
- **S3:** Parallelized uploads/downloads
- **AI Gateway:** Async provider calls, connection pooling
- **Worker:** Queue-based job processing (scale worker count)

---

## Deployment Architecture

### GitHub Actions → AWS

```
GitHub Actions (OIDC)
    ↓
AWS STS (Assume Role: gha-deploy-role)
    ↓
Build Docker Images (4x)
    ↓
Push to ECR (tag: git SHA)
    ↓
Update ECS Task Definitions
    ↓
Update ECS Services (rolling update)
    ↓
Wait for Healthy (ALB target health checks)
    ↓
Append to ACTIVITY.md (bot commit)
```

### Zero Downtime Deployment

- **ECS Rolling Update:** Minimum healthy percent: 100%, Maximum: 200%
- **Health Checks:** ALB checks `/health` every 30s
- **Deregistration Delay:** 30s (allow in-flight requests to complete)
- **Rollback:** Redeploy previous task definition if new version unhealthy

### Terraform State

- **Backend:** S3 bucket + DynamoDB lock table
- **Bootstrapping:** First `terraform apply` creates state bucket if missing
- **State Locking:** Prevents concurrent applies

---

## Observability

### Logging

- **Format:** Structured JSON with `trace_id`, `user_id`, `timestamp`, `level`, `message`
- **Destinations:** CloudWatch Log Groups (per service)
- **Retention:** 30 days (configurable)

### Tracing

- **X-Ray:** Enabled on ALB and ECS tasks
- **Trace ID:** Propagated through all services (headers: `X-Amzn-Trace-Id`)
- **Segments:** ALB → Frontend → Backend → Gateway → Provider

### Metrics

- **CloudWatch Metrics:** CPU, Memory, Request Count, Latency, Error Rate
- **Custom Metrics:** Token usage, Image generations, Video jobs (per model)
- **Alarms:**
  - ALB 5xx > 10 in 5 minutes
  - ECS unhealthy tasks > 0
  - RDS CPU > 80%
  - Redis CPU > 80%

### Dashboards

- **Service Health:** ECS task count, ALB target health
- **Usage:** Tokens/Images/Videos per hour
- **Latency:** P50, P95, P99 for chat/image/video endpoints
- **Errors:** Error rate by service and endpoint

---

## Future Enhancements

1. **SMS OTP:** Integrate Twilio/SNS for phone-based auth
2. **Multi-Region:** Deploy to multiple AWS regions for DR
3. **Advanced Analytics:** User behavior tracking, A/B testing
4. **Real-Time Notifications:** WebSocket support for job status updates
5. **Mobile Apps:** Native iOS/Android apps
6. **API Marketplace:** Allow third-party integrations
7. **Custom Models:** Fine-tuned models per tenant
8. **Batch Processing:** Bulk CV/Slide generation

---

*This architecture is designed to evolve. All changes should be documented here and reflected in the codebase.*
