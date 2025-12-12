# ملف المعلومات التقنية والفنية – AquaERP

## نظرة عامة

- نظام SaaS متعدد العملاء (Schema-based multi-tenancy) لإدارة المزارع السمكية، مع تكامل محاسبي (IAS 41) ودعم فواتير ZATCA.
- البنية تقسم التطبيقات لكل عميل (tenant) مع مخططات Postgres معزولة، وطبقة API موحدة عبر Django Ninja.

## المكدس التقني

- **Backend:** Python 3.11، Django 5، Django Ninja، django-tenants، PostgreSQL 16، Celery + Redis، JWT عبر simplejwt، CORS.
- **Frontend:** React 18 + TypeScript، Vite (منفذ 5175)، Tailwind CSS، React Router، Zustand، React Hook Form، Zod، i18next.
- **البنية التحتية:** Docker/Docker Compose، Gunicorn (للإنتاج)، Redis للوسائط والـ cache، Postgres.

## الخدمات (docker-compose)

- `web`: Django runserver على 8000 مع تحميل الكود الحي.
- `db`: PostgreSQL 16 مع بيانات افتراضية `aqua_erp_db / aqua_admin / secure_pass_123`.
- `redis`: Redis 7 (منفذ 6379) للتخزين المؤقت ووسيط الرسائل.
- `celery`: عامل مهام لخلفية النظام، يتصل بـ Redis.
- `celery-beat`: جدولة مهام دورية.

## البنية المنطقية للتطبيق (backend)

- **التطبيقات المشتركة (shared):** `tenants` لإدارة العملاء والمجالات، `django-tenants`، `corsheaders`، `django_celery_beat`.
- **تطبيقات العميل (tenant apps):** `accounts` (مستخدمون وصلاحيات)، `biological` (الأنواع/الأحواض/الدفعات)، `inventory` (أعلاف/أدوية)، `daily_operations` (تغذية/نفوق/FCR)، `accounting` (قيود مزدوجة)، `sales` (مبيعات وحصاد وZATCA)، `audit` (تسجيل العمليات)، `api` (نقاط نهاية REST/Ninja).
- **الميدلوير الأساسي:** `TenantMainMiddleware` لتوجيه المخططات، `SubscriptionMiddleware` للقيود، `TenantDebugMiddleware` للتتبع، `AuditLoggingMiddleware` للتدقيق، مع CORS و i18n.
- **المصادقة:** `AUTH_USER_MODEL = accounts.User`، JWT بإعمار افتراضي: وصول 1 ساعة، تحديث 7 أيام مع تدوير وتعمية HS256 بالـ `SECRET_KEY`.
- **التخزين المؤقت:** Redis (DB 1) مع `KEY_PREFIX=aquaerp` و `CACHE_VERSION=1`.
- **CORS:** منافذ Vite (5173–5175) و localhost/domains الفرعية `*.localhost`، والسماح العام عند DEBUG.
- **اللغات والتوقيت:** `LANGUAGE_CODE=ar-sa`، `TIME_ZONE=Asia/Riyadh`، مع ملفات ترجمة في `locale/`.
- **الملفات الثابتة/الإعلامية:** `STATIC_ROOT=staticfiles`، `MEDIA_ROOT=media`.

## البنية المنطقية للتطبيق (frontend)

- إعداد Vite مع React Compiler، خادم تطوير على `5175`، بروكسي تلقائي لـ `/api` إلى `http://localhost:8000`.
- الاعتماد على i18next للترجمة، Zustand للحالة العامة، React Hook Form + Zod للتحقق، Recharts للرسوم.

## المتغيرات البيئية الأساسية (`env.example`)

- Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.
- قاعدة البيانات: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.
- Redis/Celery: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.
- لغة/منطقة: `LANGUAGE_CODE`, `TIME_ZONE`.
- إعدادات الإنتاج المقترحة: `STATIC_ROOT`, `MEDIA_ROOT`, وتعطيل DEBUG مع تمكين إعدادات الأمان (CSRF/HSTS/SSL).

## أوامر التشغيل السريعة

- **Docker (مفضل للتجارب السريعة):**
  - `docker-compose up -d`
  - Migrations: `docker-compose exec web python manage.py migrate_schemas --shared && docker-compose exec web python manage.py migrate_schemas`
  - إنشاء عميل: `docker-compose exec web python manage.py create_tenant --name "<NAME>" --domain "<DOMAIN>" --email "<EMAIL>" --admin-username "<USER>" --admin-email "<EMAIL>" --admin-password "<PASS>"`
- **تشغيل محلي (بدون Docker):**
  - Backend: `pip install -r requirements.txt` ثم `python manage.py runserver 0.0.0.0:8000`
  - Celery worker: `celery -A tenants.aqua_core worker -l info`
  - Celery beat: `celery -A tenants.aqua_core beat -l info`
  - Frontend: داخل `frontend/` تشغيل `npm install` ثم `npm run dev -- --host --port 5175`

## هيكل المجلدات المختصر

- الجذر: `docker-compose.yml`, `Dockerfile`, `manage.py`, `requirements.txt`, `env.example`.
- backend: `tenants/` (إعدادات Django و multi-tenancy)، `accounts/`, `biological/`, `inventory/`, `daily_operations/`, `accounting/`, `sales/`, `audit/`, `api/`.
- frontend: `frontend/` مع إعداد Vite/React.
- اختبارات: ملفات `test_*.py` و`tests/` لوحدات مختلفة.

## الأمان وأفضل الممارسات

- عيّن `SECRET_KEY` قوية وأوقف `DEBUG` في الإنتاج، وحدد `ALLOWED_HOSTS`.
- فعّل HTTPS وقيود الكوكيز (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) في الإنتاج.
- خزن مفاتيح ZATCA وأي بيانات حساسة في Vault/بيئة مشفرة.
- راجع إعدادات CORS قبل النشر، واضبط `CORS_ALLOW_ALL_ORIGINS=False` للإنتاج.

## الاختبارات

- إطار العمل: `pytest`, `pytest-django`, تغطية عبر `pytest-cov`.
- أوامر نموذجية: `pytest -q` أو تشغيل ملفات اختبار منفصلة مثل `test_api_endpoint.py`.

## ملاحظات نشر سريعة

- للإنتاج استخدم Gunicorn خلف Nginx أو عكس-proxy، مع قاعدة بيانات و Redis مُدارة.
- نفّذ ترحيلات `migrate_schemas` لكل من المخطط المشترك ومخططات العملاء عند نشر جديد.
- تابع سجلات المهام الدورية عبر `celery-beat` وتأكد من صحة Healthchecks لـ Postgres/Redis.

---

آخر تحديث: توليد تلقائي (يرجى تحديث القيم الحساسة قبل النشر).


