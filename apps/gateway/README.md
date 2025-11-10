# Pulse AI Studio - AI Gateway

AI Gateway for multi-model routing, usage metering, rate limiting, and content moderation.

## Features

- **Multi-Model Routing:** OpenAI (GPT-4/5), Anthropic (Claude 4.5), Google (Gemini Pro), Nano Banana, Veo3
- **Usage Metering:** Track tokens, images, videos per user
- **Rate Limiting:** 60 requests per 60 seconds per user (configurable)
- **Content Moderation:** Pre-provider moderation hooks
- **Fallback Logic:** Automatic fallback to alternative providers

## Setup

```bash
cd apps/gateway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with API keys
```

## Running

```bash
# Development
uvicorn src.main:app --reload --port 8081

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8081 --workers 4
```

## API Endpoints

### Chat Completion
```http
POST /v1/chat/complete
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "Hello"}]
}
```

### Image Generation
```http
POST /v1/images/generate
{
  "model": "nano-banana",
  "prompt": "Beautiful sunset",
  "count": 4
}
```

### Video Generation
```http
POST /v1/video/generate
{
  "model": "veo3",
  "prompt": "Ocean waves",
  "duration_s": 15
}
```

## Project Structure

```
apps/gateway/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── rate_limit.py
│   │   ├── provider_router.py
│   │   ├── usage_meter.py
│   │   └── moderation.py
│   ├── providers/
│   │   ├── openai_client.py
│   │   ├── anthropic_client.py
│   │   ├── google_client.py
│   │   ├── nano_banana_client.py
│   │   ├── veo3_client.py
│   │   └── replicate_client.py
│   ├── routes/
│   │   ├── chat.py
│   │   ├── images.py
│   │   └── video.py
│   └── schemas/
├── requirements.txt
└── .env.example
```

## Provider Routing

Model names determine routing:
- `gpt-*`, `openai:*` → OpenAI
- `claude*`, `anthropic:*` → Anthropic
- `gemini*`, `google:*` → Google Gemini
- `nano-banana*` → Nano Banana (images)
- `veo3*` → Veo3 (video)

## Deployment

Deployed as Docker container to AWS ECS Fargate. See `/docker/gateway.Dockerfile`.

