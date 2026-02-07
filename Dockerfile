FROM python:3.14-slim-bookworm

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies (including pg_dump/pg_restore)
# We need to add the official Postgres repo to get version 18
RUN apt-get update && apt-get install -y curl gnupg2 lsb-release \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y postgresql-client-18 \
    && rm -rf /var/lib/apt/lists/*

# Add PostgreSQL tools to PATH
ENV PATH="/usr/lib/postgresql/18/bin:${PATH}"

# Copy requirements first for better Docker layer caching
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the source code
COPY . .

ENTRYPOINT ["python3", "main.py"]