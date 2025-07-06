FROM python:3.10-slim

WORKDIR /code

# 1. Install system dependencies including specific versions for reportlab
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libtiff-dev \
    libwebp-dev \
    libpython3.11-dev \
    libgirepository1.0-dev \
    libffi-dev \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libfribidi-dev \
    libharfbuzz-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Use compatible pip version
RUN pip install --no-cache-dir pip==24.0

COPY requirements.txt .

# 3. Install reportlab using pre-built wheel with specific version
RUN pip install --no-cache-dir --only-binary=reportlab reportlab==3.6.12

# 4. Install other problematic packages
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.3 \
    arabic-reshaper==2.1.4 \
    Pillow==9.0.0

# 5. Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
