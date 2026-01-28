# Dockerfile for PMCC Bot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create volume for database persistence
VOLUME ["/app/data"]

# Set environment variable for database path
ENV DB_PATH=/app/data/pmcc.db

# Run the bot
CMD ["python", "main.py"]
