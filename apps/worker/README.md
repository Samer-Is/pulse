# Pulse AI Studio - Async Worker

Background worker for async job processing using Celery.

## Jobs

- **Payment Webhooks:** Process HyperPay/PayTabs/ZainCash webhooks
- **Video Finalization:** Encode, thumbnail, upload videos
- **Analytics:** Daily usage aggregation
- **Cleanup:** Delete old files, quarantine cleanup

## Setup

```bash
cd apps/worker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env
```

## Running

```bash
# Start Celery worker
celery -A src.main worker --loglevel=info

# With specific queues
celery -A src.main worker --loglevel=info -Q payments,videos,analytics

# Beat scheduler (for periodic tasks)
celery -A src.main beat --loglevel=info
```

## Monitoring

```bash
# Flower (web-based monitoring)
pip install flower
celery -A src.main flower
# Visit http://localhost:5555
```

## Project Structure

```
apps/worker/
├── src/
│   ├── main.py                      # Celery app
│   └── jobs/
│       ├── payments_webhooks.py     # Payment processing
│       ├── video_finalize.py        # Video jobs
│       ├── analytics.py             # Usage analytics
│       └── cleanup.py               # File cleanup
├── requirements.txt
└── .env.example
```

## Deployment

Deployed as Docker container to AWS ECS Fargate (no ALB, internal only).

