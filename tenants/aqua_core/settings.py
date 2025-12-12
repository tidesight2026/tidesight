# aqua_core/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# إعدادات Django الأساسية - من Environment Variables
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-later-dev-only')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
# ALLOWED_HOSTS - دمج من .env مع القيم الافتراضية
# ملاحظة: Django لا يدعم wildcards في ALLOWED_HOSTS، لذلك يجب إضافة كل domain بشكل صريح
default_allowed_hosts = [
    'localhost', 
    '127.0.0.1', 
    'farm1.localhost', 
    'tmco.localhost',
    'tidesight.cloud',
    'www.tidesight.cloud',
    'tidesight.doud',
    'www.tidesight.doud',
]
env_allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
if env_allowed_hosts:
    # دمج hosts من .env مع tenant domains
    all_hosts = set(env_allowed_hosts.split(','))
    all_hosts.update([
        'farm1.localhost', 
        'tmco.localhost',
        'tidesight.cloud',
        'www.tidesight.cloud',
        'tidesight.doud',
        'www.tidesight.doud',
    ])  # إضافة tenant domains
    # إضافة أي domain يحتوي على .localhost (للتطوير)
    all_hosts.add('*.localhost')  # للتوثيق فقط - Django لا يدعم wildcards
    ALLOWED_HOSTS = list(all_hosts)
else:
    ALLOWED_HOSTS = default_allowed_hosts

# للتطوير: السماح بجميع .localhost domains
# في الإنتاج، يجب إضافة كل domain بشكل صريح
# ملاحظة: لا يمكن الوصول إلى قاعدة البيانات هنا لأن Django لم يتم تهيئته بعد
# سيتم إضافة domains ديناميكياً في middleware إذا لزم الأمر

# =================================================
# PRODUCTION SECURITY CHECKS (حماية من سوء الإعداد)
# =================================================
# التحقق من الإعدادات الخطيرة في بيئة الإنتاج
if not DEBUG:
    import sys
    
    # التحقق من SECRET_KEY
    default_secret_keys = [
        'django-insecure-change-me-later-dev-only',
        'django-insecure-change-me-later-in-production-use-strong-random-key',
        'your-super-secret-key-change-this-in-production-minimum-50-characters-long',
    ]
    if SECRET_KEY in default_secret_keys or len(SECRET_KEY) < 50:
        print(
            "\n" + "="*80 + "\n"
            "⚠️  خطأ أمني خطير: SECRET_KEY غير آمن!\n"
            "⚠️  في بيئة الإنتاج، يجب استخدام SECRET_KEY قوي وعشوائي (50+ حرف).\n"
            "⚠️  توليد مفتاح جديد:\n"
            "   python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"\n"
            "="*80 + "\n",
            file=sys.stderr
        )
        raise ValueError(
            "SECRET_KEY غير آمن في بيئة الإنتاج. "
            "يرجى تعيين SECRET_KEY قوي في متغيرات البيئة."
        )
    
    # التحقق من ALLOWED_HOSTS
    if not ALLOWED_HOSTS or all(host in ['localhost', '127.0.0.1', '0.0.0.0'] for host in ALLOWED_HOSTS):
        print(
            "\n" + "="*80 + "\n"
            "⚠️  تحذير أمني: ALLOWED_HOSTS غير محددة بشكل صحيح للإنتاج!\n"
            "⚠️  يجب تعيين ALLOWED_HOSTS بنطاقات الإنتاج الفعلية.\n"
            "="*80 + "\n",
            file=sys.stderr
        )
        # في الإنتاج، نرفع استثناء. في التطوير، نكتفي بتحذير
        if os.getenv('ENVIRONMENT') == 'production':
            raise ValueError(
                "ALLOWED_HOSTS غير محددة بشكل صحيح في بيئة الإنتاج. "
                "يرجى تعيين ALLOWED_HOSTS بنطاقات الإنتاج الفعلية."
            )
    
    # التحقق من قاعدة البيانات (قيم افتراضية خطيرة)
    default_db_password = 'secure_pass_123'
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    if db_password == default_db_password:
        print(
            "\n" + "="*80 + "\n"
            "⚠️  تحذير أمني: كلمة مرور قاعدة البيانات هي القيمة الافتراضية!\n"
            "⚠️  يجب تغيير POSTGRES_PASSWORD في بيئة الإنتاج.\n"
            "="*80 + "\n",
            file=sys.stderr
        )
        if os.getenv('ENVIRONMENT') == 'production':
            raise ValueError(
                "كلمة مرور قاعدة البيانات هي القيمة الافتراضية في بيئة الإنتاج. "
                "يرجى تعيين POSTGRES_PASSWORD قوي في متغيرات البيئة."
            )
    
    # التحقق من Redis (إذا كان يستخدم كلمة مرور في الإنتاج)
    redis_url = os.getenv('REDIS_URL', '')
    if redis_url and 'redis://redis:6379' in redis_url and not redis_url.startswith('redis://:'):
        # Redis بدون كلمة مرور في الإنتاج
        if os.getenv('ENVIRONMENT') == 'production':
            print(
                "\n" + "="*80 + "\n"
                "⚠️  تحذير أمني: Redis بدون كلمة مرور في بيئة الإنتاج!\n"
                "⚠️  يجب تفعيل requirepass في Redis وتعيين REDIS_URL مع كلمة المرور.\n"
                "="*80 + "\n",
                file=sys.stderr
            )
    

# =================================================
# MULTI-TENANCY CONFIGURATION (نواة النظام)
# =================================================

SHARED_APPS = (
    'django_tenants',  # إلزامي أن يكون الأول
    'tenants',         # تطبيق إدارة العملاء
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',  # Admin للـ Public Schema (لإدارة Tenants)
    'accounts',  # تطبيق المستخدمين - موجود في public schema أيضاً (لإدارة Tenants)
    'corsheaders',      # CORS support للـ Frontend
    'django_celery_beat',  # لمهام Celery المجدولة
)

TENANT_APPS = (
    'django.contrib.admin',  # Admin لكل Tenant
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'accounts',  # تطبيق المستخدمين - معزول لكل tenant
    'biological',  # تطبيق البيانات البيولوجية (Species, Ponds, Batches)
    'inventory',  # تطبيق المخزون (Feeds, Medicines) - ✅ في TENANT_APPS
    'daily_operations',  # تطبيق العمليات اليومية (Feeding, Mortality) - Sprint 3
    'accounting',  # تطبيق المحاسبة (Double Entry) - Sprint 4
    'sales',  # تطبيق المبيعات والحصاد - Sprint 5
    'audit',  # تطبيق Audit Logging - تسجيل العمليات الحساسة
    'api',  # API endpoints - يجب أن يكون في TENANT_APPS للوصول إلى نماذج tenant
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "tenants.Client" 
TENANT_DOMAIN_MODEL = "tenants.Domain"

# إعدادات إضافية لـ django-tenants
PUBLIC_SCHEMA_URLCONF = 'tenants.aqua_core.urls'  # نفس URLs لكل من public و tenant schemas

# السماح بالوصول إلى public schema عبر localhost بدون domain
# هذا يسمح بالوصول إلى Admin من localhost:8000 لإنشاء tenants
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware - يجب أن يكون قبل TenantMiddleware
    'django_tenants.middleware.main.TenantMainMiddleware', # هذا هو المسؤول عن توجيه الطلب للـ Schema الصحيحة
    'tenants.aqua_core.middleware.SubscriptionMiddleware',  # Subscription Gatekeeper
    'tenants.aqua_core.middleware.TenantDebugMiddleware',  # Debug middleware
    'audit.middleware.AuditLoggingMiddleware',  # Audit Logging Middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend', # محرك خاص للمكتبة
        'NAME': os.getenv('POSTGRES_DB', 'aqua_erp_db'),
        'USER': os.getenv('POSTGRES_USER', 'aqua_admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'secure_pass_123'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

ROOT_URLCONF = 'tenants.aqua_core.urls'
WSGI_APPLICATION = 'tenants.aqua_core.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LANGUAGE_CODE = 'ar-sa' # التجهيز للغة العربية
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Languages supported
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# =================================================
# CACHING CONFIGURATION
# =================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),  # استخدام DB 1 للـ Cache
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'aquaerp',
        'TIMEOUT': 300,  # 5 دقائق افتراضي
    }
}

# Cache versioning for cache invalidation
CACHE_VERSION = 1

# Static & Media Files
STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =================================================
# CELERY CONFIGURATION
# =================================================
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# =================================================
# CELERY BEAT SCHEDULE (المهام المجدولة)
# =================================================
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # تنظيف سجلات التدقيق القديمة - كل أسبوع يوم الأحد الساعة 2 صباحاً
    'cleanup-old-audit-logs': {
        'task': 'audit.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # كل أسبوع يوم الأحد
        'kwargs': {
            'retention_months': int(os.getenv('AUDIT_LOG_RETENTION_MONTHS', '12')),
            'batch_size': int(os.getenv('AUDIT_LOG_CLEANUP_BATCH_SIZE', '1000')),
        }
    },
    # التحقق من الاشتراكات المنتهية - يومياً الساعة 3 صباحاً
    'check-expired-subscriptions': {
        'task': 'tenants.check_expired_subscriptions',
        'schedule': crontab(hour=3, minute=0),  # يومياً الساعة 3 صباحاً
    },
}

# =================================================
# CORS CONFIGURATION (للتواصل مع Frontend)
# =================================================
# في الإنتاج، يجب تحديد النطاقات المسموحة فقط
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://farm1.localhost:5175",
    ]
else:
    # في الإنتاج، استخدام النطاقات من Environment Variables
    cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',') if origin.strip()] if cors_origins else []
    
    # تحذير في الإنتاج إذا لم يتم تعيين CORS_ALLOWED_ORIGINS
    if not CORS_ALLOWED_ORIGINS:
        import sys
        print(
            "\n" + "="*80 + "\n"
            "⚠️  تحذير أمني: CORS_ALLOWED_ORIGINS غير محددة في بيئة الإنتاج!\n"
            "⚠️  يجب تعيين CORS_ALLOWED_ORIGINS بنطاقات Frontend المسموحة.\n"
            "⚠️  مثال: CORS_ALLOWED_ORIGINS=https://app.aquaerp.com,https://admin.aquaerp.com\n"
            "="*80 + "\n",
            file=sys.stderr
        )

# CORS إضافية للتنمية
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # في وضع التطوير فقط
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =================================================
# LOGGING CONFIGURATION
# =================================================
# إنشاء مجلد logs إذا لم يكن موجوداً
logs_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {funcName} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '{levelname} {asctime} {module} {funcName} {pathname}:{lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'aquaerp.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'tenants.aqua_core.middleware': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'daily_operations': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'sales': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounting': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'audit': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =================================================
# AUTHENTICATION CONFIGURATION
# =================================================
AUTH_USER_MODEL = 'accounts.User'

# =================================================
# JWT CONFIGURATION
# =================================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# =================================================
# SECURITY SETTINGS (Production)
# =================================================
# ملاحظة: هذه الإعدادات للبيئة الإنتاجية فقط
# في التطوير، يجب تعطيلها لسهولة التطوير

# HTTPS Settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() == 'true'

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true'
SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False').lower() == 'true'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if os.getenv('CSRF_TRUSTED_ORIGINS') else []

# Data Leakage Prevention
# التأكد من عدم إرجاع معلومات حساسة في Error Messages
# SECRET_KEY يجب أن يكون في Environment Variables فقط
# ZATCA Keys يجب أن تكون في Vault أو Environment Variables مشفرة

# =================================================
# EMAIL CONFIGURATION
# =================================================
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@aquaerp.com')

# =================================================
# AUDIT LOG RETENTION CONFIGURATION
# =================================================
# فترة الاحتفاظ بسجلات التدقيق (بالأشهر)
# السجلات الأقدم من هذه الفترة سيتم حذفها تلقائياً
AUDIT_LOG_RETENTION_MONTHS = int(os.getenv('AUDIT_LOG_RETENTION_MONTHS', '12'))
# حجم الدفعة عند حذف السجلات القديمة
AUDIT_LOG_CLEANUP_BATCH_SIZE = int(os.getenv('AUDIT_LOG_CLEANUP_BATCH_SIZE', '1000'))