# 🔧 حل مشكلة إنشاء .env.prod

## ⚠️ المشكلة

```
ModuleNotFoundError: No module named 'django'
```

**السبب:** Django غير مثبت على النظام (وهذا طبيعي - سيعمل داخل Docker).

---

## ✅ الحل: استخدام طريقة بديلة

### الطريقة 1: استخدام Python secrets (موصى به)

```bash
cd /opt/tidesight

# إنشاء SECRET_KEY بدون Django
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
POSTGRES_PASS=$(openssl rand -base64 32)
REDIS_PASS=$(openssl rand -base64 32)

cat > .env.prod << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=${POSTGRES_PASS}
REDIS_PASSWORD=${REDIS_PASS}
CELERY_BROKER_URL=redis://:${REDIS_PASS}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASS}@redis:6379/0
ENVIRONMENT=production
EOF
```

### الطريقة 2: استخدام openssl فقط

```bash
cd /opt/tidesight

SECRET_KEY=$(openssl rand -hex 50)
POSTGRES_PASS=$(openssl rand -base64 32)
REDIS_PASS=$(openssl rand -base64 32)

cat > .env.prod << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=${POSTGRES_PASS}
REDIS_PASSWORD=${REDIS_PASS}
CELERY_BROKER_URL=redis://:${REDIS_PASS}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASS}@redis:6379/0
ENVIRONMENT=production
EOF
```

---

## ✅ التحقق

```bash
# عرض الملف
cat .env.prod

# التحقق من أن SECRET_KEY موجود
grep SECRET_KEY .env.prod
```

---

## 📝 ملاحظات

- Docker يعمل بالفعل (تم تشغيله بنجاح)
- Repository موجود في `/opt/tidesight`
- الآن فقط تحتاج لإنشاء `.env.prod` ثم المتابعة

---

**جاهز! 🎉**
