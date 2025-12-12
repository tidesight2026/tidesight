# استخدام Python 3.11 slim للإنتاج (أخف وأسرع)
FROM python:3.11-slim

# إعداد متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# مجلد العمل
WORKDIR /app

# تثبيت netcat للتحقق من قاعدة البيانات
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# تثبيت المتطلبات
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ المشروع
COPY . /app/

# إنشاء مجلدات للـ staticfiles و media
RUN mkdir -p /app/staticfiles /app/media

# نسخ entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# الأمر الافتراضي (سيتم تجاوزه في docker-compose.prod.yml)
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "tenants.aqua_core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]