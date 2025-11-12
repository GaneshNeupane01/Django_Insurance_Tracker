FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add crontab and make sure cron service runs
RUN python manage.py crontab add

EXPOSE 8000

# Start both cron and Gunicorn
CMD service cron start && \
    python manage.py migrate --noinput && \
    python create_superuser.py && \
    python manage.py collectstatic --noinput && \
    gunicorn DjangoModels.wsgi:application --bind 0.0.0.0:8000
