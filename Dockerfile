FROM python:3.10-slim

WORKDIR /app

# Install dependencies required by OpenCV + cryptography
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir pip==24.0
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE 8000

CMD python manage.py migrate --noinput && \
    python create_superuser.py && \
    python manage.py collectstatic --noinput && \
    gunicorn DjangoModels.wsgi:application --bind 0.0.0.0:8000

