# 📝 أوامر Git المفيدة - TideSight

## 🔧 على جهازك المحلي

### إعداد Git لأول مرة

```bash
cd d:\AquaERP

# تهيئة Git
git init

# إضافة Remote
git remote add origin https://github.com/yourusername/tidesight.git

# إضافة الملفات
git add .

# Commit
git commit -m "Initial commit - TideSight"

# Push
git push -u origin main
```

### تحديث الكود

```bash
# إضافة التغييرات
git add .

# Commit
git commit -m "Update: description of changes"

# Push
git push origin main
```

---

## 🖥️ على الخادم

### Clone لأول مرة

```bash
cd /opt
git clone https://github.com/yourusername/tidesight.git tidesight
cd tidesight
```

### تحديث الكود

```bash
cd /opt/tidesight
git pull origin main
```

### استخدام Script التحديث

```bash
/opt/tidesight/update.sh
```

---

## 🔐 إعداد SSH Keys (اختياري)

### على جهازك المحلي

```bash
# إنشاء SSH Key (إذا لم يكن موجوداً)
ssh-keygen -t ed25519 -C "your-email@example.com"

# عرض المفتاح
cat ~/.ssh/id_ed25519.pub
```

### إضافة إلى GitHub/GitLab

1. انسخ محتوى `~/.ssh/id_ed25519.pub`
2. اذهب إلى GitHub → Settings → SSH Keys
3. أضف المفتاح الجديد

### اختبار

```bash
ssh -T git@github.com
```

---

## 📋 Branch Strategy (موصى به)

### إنشاء Branch للإنتاج

```bash
# على جهازك المحلي
git checkout -b production
git push origin production

# على الخادم
git clone -b production https://github.com/yourusername/tidesight.git .
```

---

## 🔄 Workflow نموذجي

### 1. تطوير محلي

```bash
git checkout -b feature/new-feature
# ... عمل التغييرات ...
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### 2. Merge إلى Main

```bash
git checkout main
git merge feature/new-feature
git push origin main
```

### 3. نشر على الخادم

```bash
# على الخادم
cd /opt/tidesight
git pull origin main
./update.sh
```

---

**جاهز! 🎉**
