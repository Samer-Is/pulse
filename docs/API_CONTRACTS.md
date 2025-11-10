# API Contracts

> Complete API specification with request/response schemas, headers, and error codes

---

## Table of Contents

1. [General Conventions](#general-conventions)
2. [Authentication](#authentication)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [AI Gateway Endpoints](#ai-gateway-endpoints)
5. [Error Responses](#error-responses)
6. [Rate Limiting](#rate-limiting)

---

## General Conventions

### Base URLs

- **Backend API:** `https://api.your-domain.tld/v1` or `https://alb-domain/api/v1`
- **AI Gateway:** `https://gateway.your-domain.tld/v1` or `https://alb-domain/gateway/v1`

### Request Headers

```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>                    # Optional, for tracing
Cookie: session=<jwt-token>             # For authenticated requests
X-CSRF-Token: <token>                   # For state-changing requests
Accept-Language: ar, en                 # Preferred language
```

### Response Headers

```http
Content-Type: application/json
X-Trace-ID: <uuid>                      # For debugging
X-RateLimit-Limit: 60                   # Requests allowed per window
X-RateLimit-Remaining: 45               # Requests remaining
X-RateLimit-Reset: 1699123456           # Unix timestamp
X-Usage-Tokens: 1234/150000            # Current usage (if applicable)
X-Usage-Images: 5/10
X-Usage-Videos: 1/2
```

### Common Response Structure

**Success (2xx):**
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-10T18:00:00Z",
    "trace_id": "abc-123-def"
  }
}
```

**Error (4xx, 5xx):**
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly token limit reached",
    "details": {
      "current": 150000,
      "limit": 150000,
      "reset_at": "2025-12-01T00:00:00Z"
    }
  },
  "meta": {
    "timestamp": "2025-11-10T18:00:00Z",
    "trace_id": "abc-123-def"
  }
}
```

---

## Authentication

### Magic Link Request

**Endpoint:** `POST /v1/auth/magic-link`

**Request:**
```json
{
  "email": "user@example.com",
  "locale": "ar"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "message": "Magic link sent to user@example.com",
    "expires_in": 600
  },
  "meta": {
    "timestamp": "2025-11-10T18:00:00Z"
  }
}
```

**Notes:**
- Email must be verified in SES (if in sandbox mode)
- Link expires in 10 minutes
- Format: `https://app.domain.tld/verify?token=<jwt>`

---

### Magic Link Verification

**Endpoint:** `POST /v1/auth/magic-link/verify`

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "data": {
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "locale": "ar",
      "created_at": "2025-11-01T10:00:00Z"
    },
    "subscription": {
      "plan_name": "Pro",
      "status": "active",
      "renews_at": "2025-12-10T00:00:00Z"
    },
    "redirect_url": "/app/chat"
  },
  "meta": {
    "timestamp": "2025-11-10T18:00:00Z"
  }
}
```

**Side Effect:** Sets httpOnly cookie `session=<jwt>` with 30-day expiry

**Errors:**
- `400` Invalid or expired token
- `404` User not found

---

## Backend API Endpoints

### Get Plans

**Endpoint:** `GET /v1/plans`

**Request:** No body

**Response (200 OK):**
```json
{
  "data": {
    "plans": [
      {
        "id": "plan-starter",
        "name": "Starter",
        "price_jod": 3.00,
        "token_limit": 150000,
        "image_limit": 10,
        "video_limit": 2,
        "features": {
          "cv_maker": true,
          "slide_maker": false,
          "pdf_summary": false,
          "advanced_editors": false
        }
      },
      {
        "id": "plan-pro",
        "name": "Pro",
        "price_jod": 5.00,
        "token_limit": 400000,
        "image_limit": 30,
        "video_limit": 5,
        "features": {
          "cv_maker": true,
          "slide_maker": true,
          "pdf_summary": true,
          "advanced_editors": false
        }
      },
      {
        "id": "plan-creator",
        "name": "Creator",
        "price_jod": 7.00,
        "token_limit": 1000000,
        "image_limit": 60,
        "video_limit": 10,
        "features": {
          "cv_maker": true,
          "slide_maker": true,
          "pdf_summary": true,
          "advanced_editors": true
        }
      }
    ],
    "addons": [
      {
        "type": "tokens",
        "amount": 200000,
        "price_jod": 1.00
      },
      {
        "type": "images",
        "amount": 10,
        "price_jod": 1.00
      },
      {
        "type": "video",
        "amount": 1,
        "price_jod": 1.00
      }
    ]
  }
}
```

---

### Create Payment Session

**Endpoint:** `POST /v1/payments/session`

**Request:**
```json
{
  "plan_id": "plan-pro",
  "provider": "hyperpay"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "session_id": "8a8294175d0595bb015d05a8c7ea008a",
    "redirect_url": "https://test.oppwa.com/v1/paymentWidgets.js?checkoutId=...",
    "expires_at": "2025-11-10T19:00:00Z"
  }
}
```

**Notes:**
- Frontend redirects user to `redirect_url`
- HyperPay handles payment collection
- Webhook updates subscription status

---

### Payment Webhook (HyperPay)

**Endpoint:** `POST /v1/payments/webhook/hyperpay`

**Request (from HyperPay):**
```json
{
  "id": "8a8294175d0595bb015d05a8c7ea008a",
  "paymentType": "PA",
  "amount": "5.00",
  "currency": "JOD",
  "result": {
    "code": "000.100.110",
    "description": "Request successfully processed"
  },
  "merchantTransactionId": "user-123-plan-pro-1699123456",
  "timestamp": "2025-11-10 18:00:00+0000"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "status": "processed"
  }
}
```

**Side Effects:**
- Updates `payments` table (status = completed)
- Updates `subscriptions` table (status = active, renews_at = +30 days)
- (Optional) Sends email confirmation

---

### Get User Usage

**Endpoint:** `GET /v1/usage/me`

**Headers:** Requires authentication (JWT cookie)

**Response (200 OK):**
```json
{
  "data": {
    "period": {
      "start": "2025-11-01T00:00:00Z",
      "end": "2025-11-30T23:59:59Z"
    },
    "plan": {
      "name": "Pro",
      "limits": {
        "tokens": 400000,
        "images": 30,
        "videos": 5
      }
    },
    "usage": {
      "tokens": {
        "used": 125000,
        "remaining": 275000,
        "percentage": 31.25
      },
      "images": {
        "used": 12,
        "remaining": 18,
        "percentage": 40.0
      },
      "videos": {
        "used": 2,
        "remaining": 3,
        "percentage": 40.0
      }
    },
    "warnings": {
      "tokens": false,
      "images": false,
      "videos": false
    }
  }
}
```

**Notes:**
- `warnings` set to `true` if usage > 80%
- Cached in Redis (5-minute TTL)

---

### Generate CV

**Endpoint:** `POST /v1/cv/generate`

**Headers:** Requires authentication

**Request:**
```json
{
  "personal_info": {
    "full_name": "Ahmed Hassan",
    "email": "ahmed@example.com",
    "phone": "+962791234567",
    "location": "Amman, Jordan",
    "linkedin": "linkedin.com/in/ahmed",
    "summary": "Experienced software engineer..."
  },
  "experience": [
    {
      "title": "Senior Developer",
      "company": "Tech Corp",
      "location": "Amman",
      "start_date": "2020-01",
      "end_date": "2025-11",
      "description": "Led team of 5 developers..."
    }
  ],
  "education": [
    {
      "degree": "B.Sc. Computer Science",
      "institution": "University of Jordan",
      "graduation_year": 2019
    }
  ],
  "skills": ["Python", "JavaScript", "AWS", "Docker"],
  "languages": ["Arabic (Native)", "English (Fluent)"],
  "format": "docx",
  "language": "en",
  "ats_friendly": true
}
```

**Response (200 OK):**
```json
{
  "data": {
    "file_id": "file-123",
    "download_url": "https://s3.region.amazonaws.com/bucket/cv.docx?X-Amz-Signature=...",
    "expires_at": "2025-11-10T18:05:00Z",
    "format": "docx",
    "size_bytes": 45678
  }
}
```

**Notes:**
- Supports `format`: "docx" or "pdf"
- ATS-friendly removes images/colors for better parsing
- Download URL valid for 5 minutes

---

### Generate Slides

**Endpoint:** `POST /v1/slides/generate`

**Headers:** Requires authentication + Pro plan or higher

**Request:**
```json
{
  "topic": "Digital Marketing Strategy for Coffee Shops",
  "audience": "Small business owners",
  "slide_count": 10,
  "language": "ar",
  "include_images": true
}
```

**Response (200 OK):**
```json
{
  "data": {
    "file_id": "file-456",
    "download_url": "https://s3.region.amazonaws.com/bucket/slides.pptx?...",
    "expires_at": "2025-11-10T18:05:00Z",
    "format": "pptx",
    "slides": [
      {
        "number": 1,
        "title": "استراتيجية التسويق الرقمي",
        "type": "title_slide"
      },
      {
        "number": 2,
        "title": "لماذا التسويق الرقمي؟",
        "type": "content"
      }
    ]
  }
}
```

**Errors:**
- `402` If user is on Starter plan (requires Pro)

---

### Get File Signed URL

**Endpoint:** `GET /v1/files/{file_id}/signed-url`

**Headers:** Requires authentication

**Response (200 OK):**
```json
{
  "data": {
    "file_id": "file-123",
    "download_url": "https://s3.region.amazonaws.com/bucket/file.pdf?...",
    "expires_at": "2025-11-10T18:05:00Z",
    "filename": "ahmed_hassan_cv.pdf",
    "size_bytes": 45678
  }
}
```

**Errors:**
- `403` If file doesn't belong to authenticated user
- `404` If file not found

---

## AI Gateway Endpoints

### Chat Completion

**Endpoint:** `POST /v1/chat/complete`

**Headers:** Requires authentication

**Request:**
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is the capital of Jordan?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": false
}
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "chatcmpl-abc123",
    "model": "gpt-4o",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "The capital of Jordan is Amman."
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 10,
      "total_tokens": 35
    }
  },
  "meta": {
    "trace_id": "abc-123",
    "latency_ms": 1250
  }
}
```

**Model Options:**
- `gpt-4o`, `gpt-4-turbo`, `gpt-5` (OpenAI)
- `claude-4.5-sonnet` (Anthropic)
- `gemini-1.5-pro`, `gemini-1.5-flash` (Google)

**Headers (Response):**
```
X-Usage-Tokens: 12535/400000
X-Usage-Warning: false
```

**Errors:**
- `402` Quota exceeded (with upgrade URL)
- `429` Rate limit exceeded
- `400` Invalid model or parameters
- `504` Provider timeout

---

### Generate Images

**Endpoint:** `POST /v1/images/generate`

**Headers:** Requires authentication

**Request:**
```json
{
  "model": "nano-banana",
  "prompt": "Modern coffee shop in Amman, warm lighting, customers working on laptops",
  "count": 4,
  "size": "1024x1024",
  "negative_prompt": "blurry, low quality"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "images": [
      {
        "id": "img-001",
        "url": "https://s3.../image1.png?...",
        "thumbnail_url": "https://s3.../thumb1.png?...",
        "size_bytes": 234567
      },
      {
        "id": "img-002",
        "url": "https://s3.../image2.png?...",
        "thumbnail_url": "https://s3.../thumb2.png?...",
        "size_bytes": 245678
      }
    ],
    "usage": {
      "images_generated": 4,
      "images_remaining": 26
    }
  },
  "meta": {
    "model_used": "nano-banana",
    "latency_ms": 3500
  }
}
```

**Model Options:**
- `nano-banana` (default)
- `replicate-sdxl` (fallback)
- `stability-xl` (fallback)

**Headers (Response):**
```
X-Usage-Images: 14/30
X-Usage-Warning: false
```

**Errors:**
- `402` Image quota exceeded
- `400` Content moderation flagged prompt
- `429` Rate limit

---

### Generate Video

**Endpoint:** `POST /v1/video/generate`

**Headers:** Requires authentication

**Request:**
```json
{
  "model": "veo3",
  "prompt": "Sunset over Petra, golden hour, cinematic",
  "duration_s": 15,
  "aspect_ratio": "9:16"
}
```

**Response (202 Accepted):**
```json
{
  "data": {
    "job_id": "job-789",
    "status": "pending",
    "estimated_completion_s": 120,
    "poll_url": "/v1/jobs/job-789"
  }
}
```

**Job Status Endpoint:** `GET /v1/jobs/{job_id}`

**Response (200 OK - Processing):**
```json
{
  "data": {
    "job_id": "job-789",
    "status": "processing",
    "progress": 45,
    "created_at": "2025-11-10T18:00:00Z",
    "updated_at": "2025-11-10T18:01:30Z"
  }
}
```

**Response (200 OK - Completed):**
```json
{
  "data": {
    "job_id": "job-789",
    "status": "completed",
    "video": {
      "file_id": "video-001",
      "url": "https://s3.../video.mp4?...",
      "thumbnail_url": "https://s3.../thumb.jpg?...",
      "duration_s": 15,
      "size_bytes": 5678901
    },
    "usage": {
      "videos_generated": 1,
      "videos_remaining": 4
    }
  }
}
```

**Model Options:**
- `veo3` (default, if available)
- `pika` (fallback stub)
- `runway` (fallback stub)

**Status Values:**
- `pending` - Queued
- `processing` - In progress
- `completed` - Ready for download
- `failed` - Error occurred

---

## Error Responses

### Error Codes

| Code | HTTP Status | Description | Retry? |
|------|-------------|-------------|--------|
| `INVALID_REQUEST` | 400 | Malformed request body | No |
| `UNAUTHORIZED` | 401 | Missing or invalid JWT | No |
| `PAYMENT_REQUIRED` | 402 | Quota exceeded, upgrade needed | No |
| `FORBIDDEN` | 403 | Insufficient permissions | No |
| `NOT_FOUND` | 404 | Resource doesn't exist | No |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Yes (after reset) |
| `INTERNAL_ERROR` | 500 | Server error | Yes (exponential backoff) |
| `PROVIDER_UNAVAILABLE` | 503 | AI provider down | Yes |
| `GATEWAY_TIMEOUT` | 504 | Provider timeout | Yes |

### Example Error Response

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly token limit reached",
    "details": {
      "resource": "tokens",
      "current": 400000,
      "limit": 400000,
      "reset_at": "2025-12-01T00:00:00Z",
      "upgrade_url": "/app/account/upgrade"
    }
  },
  "meta": {
    "timestamp": "2025-11-10T18:00:00Z",
    "trace_id": "abc-123-def"
  }
}
```

---

## Rate Limiting

### Strategy

**Sliding Window:** 60 requests per 60 seconds per user (Redis-backed)

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699123456
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests, please slow down",
    "details": {
      "limit": 60,
      "window_seconds": 60,
      "reset_at": "2025-11-10T18:01:00Z"
    }
  }
}
```

**HTTP Status:** `429 Too Many Requests`

**Retry-After Header:** `Retry-After: 15` (seconds until reset)

---

## Content Moderation

All text prompts and image generation requests pass through moderation hooks before reaching AI providers.

**Flagged Content Response:**
```json
{
  "error": {
    "code": "CONTENT_FLAGGED",
    "message": "Content violates usage policy",
    "details": {
      "reason": "inappropriate_content",
      "policy_url": "https://app.domain.tld/terms#content-policy"
    }
  }
}
```

**HTTP Status:** `400 Bad Request`

---

## Pagination (Future)

For list endpoints (e.g., usage history, file list):

**Request:**
```
GET /v1/usage/logs?page=2&per_page=50
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total_pages": 10,
    "total_items": 487
  }
}
```

---

## Versioning

API version is in the URL path (`/v1/`). Breaking changes will bump the version (`/v2/`).

**Deprecation Policy:** v1 supported for 12 months after v2 release.

---

*All endpoints documented here are implemented in OpenAPI/Swagger format at `/docs` on each service.*
