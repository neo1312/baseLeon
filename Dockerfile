# 
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
   gcc \
   python3-dev \
   libpq-dev \
   pkg-config \
   libcairo2-dev \
   libjpeg-dev \
   zlib1g-dev \
   libfreetype6-dev \
   liblcms2-dev \
   libopenjp2-7-dev \
   libtiff5-dev \
   libwebp-dev \
   build-essential \
   && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

EXPOSE 8000

# migrate + collectstatic + gunicorn are handled by docker-compose
# so this CMD is only a fallback / for direct docker run
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
