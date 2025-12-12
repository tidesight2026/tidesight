#!/bin/sh

# Entrypoint script للتأكد من جاهزية قاعدة البيانات قبل تشغيل Gunicorn

set -e

if [ "$DATABASE" = "postgres" ] || [ -z "$DATABASE" ]; then
    echo "Waiting for postgres..."
    
    # استخدام متغيرات البيئة أو القيم الافتراضية
    SQL_HOST=${POSTGRES_HOST:-db}
    SQL_PORT=${POSTGRES_PORT:-5432}
    
    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done
    
    echo "PostgreSQL started"
fi

# تشغيل الترحيلات للمخططات المشتركة
echo "Running shared migrations..."
python manage.py migrate_schemas --shared --noinput || echo "Migrations may have already been applied, continuing..."

# جمع الملفات الثابتة
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# تنفيذ الأمر الممرر (عادة Gunicorn)
exec "$@"

