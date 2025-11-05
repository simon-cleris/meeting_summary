# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY docker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config.yaml .
COPY docker/entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Create necessary directories
RUN mkdir -p input output

# Default command - runs both transcription and summary
CMD ["./entrypoint.sh"]
