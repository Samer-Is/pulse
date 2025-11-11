# Pulse AI Studio - API Documentation

**Base URL (Backend):** `https://api.yourdomain.com/v1`  
**Base URL (Gateway):** `https://gateway.yourdomain.com/v1`

---

## Authentication

All authenticated endpoints require a JWT token in an httpOnly cookie named `session`.

### POST /auth/magic-link

Request magic link for email authentication.

**Request:**
```json
{
  "email": "user@example.com",
  "locale": "ar"
}
```

**Response:**
```json
{
  "data": {
    "message": "Magic link sent",
    "email": "user@example.com"
  }
}
```

### POST /auth/magic-link/verify

Verify magic link token.

**Request:**
```json
{
  "token": "abc123..."
}
```

**Response:**
```json
{
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "locale": "ar"
    }
  }
}
```

Sets httpOnly cookie `session=<jwt_token>`.

---

## Plans

### GET /plans

List all subscription plans.

**Response:**
```json
{
  "data": {
    "plans": [
      {
        "id": "uuid",
        "name": "Starter",
        "price_jod": "3.00",
        "token_limit": 150000,
        "image_limit": 10,
        "video_limit": 2,
        "features_json": {
          "chat": true,
          "cv_maker": true
        }
      }
    ]
  }
}
```

---

## Payments

### POST /payments/checkout

Create HyperPay checkout session.

**Request:**
```json
{
  "plan_id": "uuid",
  "provider": "hyperpay"
}
```

**Response:**
```json
{
  "data": {
    "session_id": "checkout_123",
    "redirect_url": "https://hyperpay.com/...",
    "amount": "5.00",
    "currency": "JOD"
  }
}
```

### POST /payments/webhook/hyperpay

HyperPay webhook handler (called by HyperPay, not by client).

---

## Usage

### GET /usage/me

Get current user's usage and quotas.

**Response:**
```json
{
  "data": {
    "user_id": "uuid",
    "plan_name": "Starter",
    "token_limit": 150000,
    "tokens_used": 50000,
    "token_percentage": 33.3,
    "image_limit": 10,
    "images_used": 5,
    "image_percentage": 50.0,
    "video_limit": 2,
    "videos_used": 1,
    "video_percentage": 50.0,
    "quota_warnings": ["Images at 50%"]
  }
}
```

---

## Files

### POST /files/presigned-upload

Get presigned URL for file upload.

**Request:**
```json
{
  "filename": "image.png",
  "content_type": "image/png"
}
```

**Response:**
```json
{
  "data": {
    "upload_url": "https://s3.amazonaws.com/...",
    "download_url": "https://s3.amazonaws.com/...",
    "file_id": "uuid",
    "expires_in": 3600
  }
}
```

---

## CV Generation

### POST /cv/generate

Generate CV from form data.

**Request:**
```json
{
  "full_name": "أحمد محمد",
  "email": "ahmed@example.com",
  "phone": "+962 79 123 4567",
  "title": "مطور برمجيات",
  "summary": "مطور برمجيات خبرة 5 سنوات...",
  "skills": ["Python", "JavaScript", "React"],
  "education": [
    {
      "degree": "بكالوريوس علوم الحاسوب",
      "institution": "الجامعة الأردنية",
      "location": "عمان، الأردن",
      "start_date": "2015-09",
      "end_date": "2019-06"
    }
  ],
  "experience": [
    {
      "title": "مطور Full Stack",
      "company": "شركة التقنية",
      "location": "عمان، الأردن",
      "start_date": "2019-07",
      "end_date": null,
      "description": "تطوير تطبيقات ويب..."
    }
  ],
  "locale": "ar",
  "ats_friendly": true,
  "export_format": "pdf"
}
```

**Response:**
```json
{
  "data": {
    "cv_id": "uuid",
    "status": "completed",
    "download_url": "https://s3.amazonaws.com/.../cv.pdf",
    "format": "pdf"
  }
}
```

---

## Slides Generation

### POST /slides/generate

Generate presentation slides.

**Request:**
```json
{
  "presentation_title": "الذكاء الاصطناعي في 2025",
  "author": "أحمد محمد",
  "topic": "نظرة عامة على تطورات الذكاء الاصطناعي",
  "audience": "مدراء الشركات",
  "num_slides": 10,
  "slides": [
    {
      "title": "المقدمة",
      "content": "الذكاء الاصطناعي يغير العالم...",
      "layout": "title-content",
      "order": 1
    }
  ],
  "theme": "professional",
  "locale": "ar",
  "export_format": "pptx"
}
```

**Response:**
```json
{
  "data": {
    "slides_id": "uuid",
    "status": "completed",
    "download_url": "https://s3.amazonaws.com/.../slides.pptx",
    "format": "pptx",
    "slide_count": 10
  }
}
```

---

## Gateway API - Chat

### POST /chat/complete

Send chat completion request.

**Request:**
```json
{
  "model": "openai:gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "ما هو الذكاء الاصطناعي؟"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response:**
```json
{
  "data": {
    "id": "chatcmpl-123",
    "model": "gpt-4o",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "الذكاء الاصطناعي هو..."
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 150,
      "total_tokens": 165
    }
  }
}
```

**Supported Models:**
- `openai:gpt-4o`
- `openai:gpt-5`
- `anthropic:claude-4.5`
- `google:gemini-1.5-pro`

---

## Gateway API - Images

### POST /images/generate

Generate images using AI.

**Request:**
```json
{
  "model": "nano-banana:default",
  "prompt": "قط أبيض في حديقة",
  "negative_prompt": "ضبابي، سيء الجودة",
  "width": 1024,
  "height": 1024,
  "count": 4
}
```

**Response:**
```json
{
  "data": {
    "id": "img-123",
    "model": "nano-banana",
    "images": [
      {
        "url": "https://s3.amazonaws.com/.../img1.png",
        "width": 1024,
        "height": 1024
      }
    ],
    "prompt": "قط أبيض في حديقة",
    "status": "completed"
  }
}
```

**Supported Models:**
- `nano-banana:default`
- `replicate:stable-diffusion-xl`

---

## Gateway API - Video

### POST /video/generate

Generate video using AI.

**Request:**
```json
{
  "model": "veo3:default",
  "prompt": "شروق الشمس فوق جبال الأردن",
  "duration_s": 5,
  "width": 1280,
  "height": 720,
  "fps": 30
}
```

**Response:**
```json
{
  "data": {
    "id": "vid-123",
    "model": "veo3",
    "video_url": "https://s3.amazonaws.com/.../video.mp4",
    "thumbnail_url": "https://s3.amazonaws.com/.../thumb.jpg",
    "prompt": "شروق الشمس فوق جبال الأردن",
    "duration": 5,
    "width": 1280,
    "height": 720,
    "fps": 30,
    "status": "processing"
  }
}
```

**Status Values:**
- `queued`: Job queued
- `processing`: Video being generated
- `completed`: Video ready
- `failed`: Generation failed

**Supported Models:**
- `veo3:default`
- `pika:1.0`
- `runway:gen-2`

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "You have reached your monthly token limit",
    "details": {
      "used": 150000,
      "limit": 150000
    }
  }
}
```

**Common Error Codes:**
- `UNAUTHORIZED` (401): Invalid or missing JWT
- `QUOTA_EXCEEDED` (402): Usage limit reached
- `NOT_FOUND` (404): Resource not found
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

---

## Rate Limits

- **60 requests per minute** per user
- **1000 requests per hour** per user

Rate limit info in response headers:
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 950
```

---

**Last Updated:** 2025-11-11

