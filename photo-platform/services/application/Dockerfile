# Development Dockerfile for Application Service
FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from service directory
COPY services/application/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set Python path to include workspace (for shared module)
ENV PYTHONPATH=/workspace

# Change to service directory
WORKDIR /workspace/services/application

# Expose port
EXPOSE 8002

# Run application with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
