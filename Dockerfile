FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .

# Install CPU-only PyTorch first (latest compatible version) and then other dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Run migrations, create superuser, collect static files, and start Gunicorn
CMD python manage.py migrate --noinput && \
    python create_superuser.py && \
    python manage.py collectstatic --noinput && \
    gunicorn DjangoModels.wsgi:application --bind 0.0.0.0:8000