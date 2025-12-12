# 📦 إعداد Git Repository - TideSight

## 🎯 الخطوات السريعة

### 1. إنشاء Repository على GitHub/GitLab

1. اذهب إلى GitHub/GitLab
2. أنشئ repository جديد باسم `tidesight`
3. **لا** تضع README أو .gitignore (لدينا بالفعل)

---

## 🔧 الخطوة 2: إعداد Git محلياً

### 2.1 في مجلد المشروع

```bash
cd d:\AquaERP

# إذا لم يكن Git مهيأ
git init

# إضافة Remote
git remote add origin https://github.com/yourusername/tidesight.git
# أو SSH:
git remote add origin git@github.com:yourusername/tidesight.git

# التحقق من Remote
git remote -v
```

### 2.2 إضافة الملفات

```bash
# إضافة جميع الملفات
git add .

# Commit
git commit -m "Initial commit - TideSight deployment ready"

# Push
git push -u origin main
```

---

## ✅ التحقق من .gitignore

تأكد من أن `.gitignore` يحتوي على:

```
.env
.env.prod
.env.local
node_modules/
__pycache__/
*.pyc
venv/
.venv/
```

---

## 🚀 بعد Push

الآن يمكنك Clone على الخادم:

```bash
ssh root@72.60.187.58
cd /opt
git clone https://github.com/yourusername/tidesight.git tidesight
```

---

**جاهز! 🎉**
