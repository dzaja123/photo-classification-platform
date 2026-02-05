# Development Dockerfile for Admin Service
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
COPY services/admin/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set Python path to include workspace (for shared module)
ENV PYTHONPATH=/workspace

# Change to service directory
WORKDIR /workspace/services/admin

# Expose port
EXPOSE 8003

# Run application with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
