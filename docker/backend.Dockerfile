# SEO Monster - Backend Dockerfile
# Python FastAPI application

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Create data directories
RUN mkdir -p /app/data/sites \
    /app/data/platforms \
    /app/data/content \
    /app/data/tasks \
    /app/data/sessions \
    /app/data/indexing \
    /app/data/ai \
    /app/data/tds \
    /app/data/ads \
    /app/data/tracker \
    /app/data/ses \
    /app/data/diagnostics \
    /app/data/keys \
    /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 seomonster && \
    chown -R seomonster:seomonster /app
USER seomonster

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
