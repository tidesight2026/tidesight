# 🔧 إصلاح المشاكل في Settings و Nginx

## ✅ تم إصلاح المشاكل التالية:

1. **`NameError: name 'STATIC_ROOT' is not defined`**
   - ✅ تم حذف الكود الذي يحاول استخدام `STATIC_ROOT` قبل تعريفه

2. **`duplicate upstream "backend"` في Nginx**
   - ✅ تم حذف ملف `aquaerp.conf` القديم

3. **`host not found in upstream "web:8000"`**
   - ✅ سيتم حله بعد إصلاح خطأ settings.py

---

## 🚀 الخطوات التالية

### 1. Commit و Push التغييرات:

```bash
git add .
git commit -m "Fix STATIC_ROOT error and remove old nginx config"
git push origin main
```

### 2. على الخادم - Pull و Rebuild:

```bash
cd /opt/tidesight
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ التحقق

```bash
# التحقق من الحاويات
docker-compose -f docker-compose.prod.yml ps

# يجب أن تكون جميع الحاويات في حالة "Up" أو "healthy"
```

---

**جاهز! 🎉**
