# Base image
FROM python:latest

# Set work dir
WORKDIR /app

# Install system deps (for psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install requests

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Run server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
