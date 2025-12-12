# 🔧 حل مشكلة Port 80 - Docker Containers

## ⚠️ المشكلة

Nginx متوقف لكن المنفذ 80 لا يزال مستخدم - قد تكون حاوية Docker سابقة لا تزال تعمل.

---

## ✅ الحل: إيقاف جميع حاويات Docker وإعادة التشغيل

```bash
cd /opt/tidesight

# إيقاف جميع الحاويات
docker-compose -f docker-compose.prod.yml down

# التحقق من الحاويات المتبقية
docker ps -a

# إيقاف أي حاويات متبقية
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# التحقق من المنفذ 80
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# إذا كان هناك عملية تستخدم المنفذ 80، أوقفها
# ثم إعادة التشغيل
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🚀 الحل السريع

```bash
cd /opt/tidesight

# إيقاف جميع الحاويات
docker-compose -f docker-compose.prod.yml down

# التحقق من المنفذ
sudo lsof -i :80

# إذا كان هناك عملية، أوقفها باستخدام PID
# sudo kill -9 <PID>

# إعادة التشغيل
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ التحقق

```bash
# التحقق من الحاويات
docker-compose -f docker-compose.prod.yml ps

# التحقق من المنفذ
sudo netstat -tulpn | grep :80
```

---

**جاهز! 🎉**
