# 🔧 حل مشكلة Nginx Restarting

## ⚠️ المشكلة

```
State: Restarting
```

**السبب:** خطأ في ملف تكوين Nginx.

---

## ✅ الحل: فحص Logs

```bash
cd /opt/tidesight

# فحص Logs Nginx
docker-compose -f docker-compose.prod.yml logs nginx --tail=50
```

---

## 🔍 الأخطاء الشائعة:

1. **خطأ في syntax** - تحقق من ملف `tidesight.conf`
2. **SSL certificates غير موجودة** - يجب تعطيل HTTPS مؤقتاً
3. **خطأ في المسارات** - تحقق من volumes

---

**أرسل الـ logs لتحديد المشكلة بدقة.**

---

**جاهز! 🎉**
