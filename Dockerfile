FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir \
    torch==2.9.1+cpu torchvision==0.24.1+cpu torchaudio==2.9.1+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Add crontab and make sure cron service runs
#RUN python manage.py crontab add

EXPOSE 8000
#service cron start && \
# Start both cron and Gunicorn
#gunicorn DjangoModels.wsgi:application --bind 0.0.0.service cron start && \0:8000
CMD python manage.py migrate --noinput && \
    python create_superuser.py && \
    python manage.py collectstatic --noinput && \
    gunicorn DjangoModels.wsgi:application --bind 0.0.0.0:8000