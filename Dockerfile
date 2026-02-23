# syntax=docker/dockerfile:1.2
FROM python:3.9-slim

WORKDIR /app

# Install required dependences of the system
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Cloud Run PORT
ENV PORT=8080

EXPOSE 8080

# Fastapi 
CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8080"]