# Worker Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including FFmpeg for video processing)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY apps/worker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/worker/src ./src

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run Celery worker
CMD ["celery", "-A", "src.main", "worker", "--loglevel=info"]
