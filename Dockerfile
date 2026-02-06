FROM python:3.14-slim-bookworm

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies (including pg_dump/pg_restore)
# We need postgresql-client-15 or similar depending on your server version
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the source code
COPY . .

ENTRYPOINT ["python3", "main.py"]