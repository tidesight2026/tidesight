#!/bin/bash

# سكربت النسخ الاحتياطي لقاعدة البيانات والملفات
# يجب تشغيله يومياً باستخدام cron

set -e

# إعدادات
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="${POSTGRES_DB:-aqua_erp_db}"
DB_USER="${POSTGRES_USER:-aqua_admin}"
DB_HOST="${POSTGRES_HOST:-db}"
MEDIA_DIR="/app/media"
RETENTION_DAYS=30

# إنشاء مجلد النسخ الاحتياطي
mkdir -p "$BACKUP_DIR"

# نسخ احتياطي لقاعدة البيانات
echo "Creating database backup..."
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dumpall -h "$DB_HOST" -U "$DB_USER" | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# نسخ احتياطي للملفات الوسائط
echo "Creating media files backup..."
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C "$(dirname $MEDIA_DIR)" "$(basename $MEDIA_DIR)" 2>/dev/null || echo "Media directory not found, skipping..."

# حذف النسخ الاحتياطية القديمة (أكثر من 30 يوم)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"

# (اختياري) رفع النسخ الاحتياطية إلى S3 أو Google Drive
# aws s3 sync "$BACKUP_DIR" s3://your-bucket/backups/ --delete
# أو استخدام rclone للـ Google Drive

