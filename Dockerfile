FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy server-only requirements first for better caching
COPY requirements-server.txt requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will override this)
EXPOSE 8080

# Set environment variables for production
ENV HOST=0.0.0.0
ENV PORT=8080
ENV ENVIRONMENT=production
ENV ENABLE_GATEWAY=true
ENV API_PREFIX=

# Start the server
CMD ["python", "app.py"]
