# 🔧 إعداد Git محلياً - TideSight

## ⚠️ المشكلة

عند محاولة عمل commit، Git يطلب إعداد الهوية:

```
Author identity unknown
*** Please tell me who you are.
```

---

## ✅ الحل

### الطريقة 1: إعداد عام (موصى به)

```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

**مثال:**
```bash
git config --global user.email "admin@tidesight.cloud"
git config --global user.name "TideSight Developer"
```

### الطريقة 2: إعداد محلي فقط (لهذا المشروع)

```bash
cd d:\AquaERP
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

---

## 🔍 التحقق من الإعدادات

```bash
# عرض الإعدادات العامة
git config --global --list

# عرض الإعدادات المحلية
git config --list
```

---

## 📝 بعد الإعداد

الآن يمكنك عمل commit:

```bash
git add .
git commit -m "Initial commit - TideSight"
git push -u origin main
```

---

**جاهز! 🎉**
