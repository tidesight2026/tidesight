# 🔧 إضافة CORS إلى .env

## ✅ على الخادم

أضف إلى `.env`:

```bash
cd /opt/tidesight

# إضافة CORS_ALLOWED_ORIGINS
echo "CORS_ALLOWED_ORIGINS=https://tidesight.cloud,https://www.tidesight.cloud,http://tidesight.cloud,http://www.tidesight.cloud" >> .env
```

أو عدّل `.env` يدوياً:

```
CORS_ALLOWED_ORIGINS=https://tidesight.cloud,https://www.tidesight.cloud,http://tidesight.cloud,http://www.tidesight.cloud
```

---

## 🔄 إعادة تشغيل

```bash
docker-compose -f docker-compose.prod.yml restart web
```

---

**جاهز! 🎉**
