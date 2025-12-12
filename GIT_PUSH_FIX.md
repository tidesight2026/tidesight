# 🔧 حل مشكلة Git Push - TideSight

## ⚠️ المشكلة

```
error: src refspec main does not match any
error: failed to push some refs
```

**السبب:** Branch `main` غير موجود محلياً أو لم يتم عمل commit بعد.

---

## ✅ الحل

### الطريقة 1: التحقق من Branch الحالي

```bash
# عرض جميع الفروع
git branch

# عرض آخر commit
git log --oneline
```

### الطريقة 2: إنشاء Branch main

إذا كان Branch الحالي هو `master`:

```bash
# إعادة تسمية master إلى main
git branch -M main

# أو إنشاء branch جديد
git checkout -b main
```

### الطريقة 3: التحقق من وجود Commits

```bash
# التحقق من حالة Git
git status

# إذا لم يكن هناك commits، قم بعمل commit أولاً
git add .
git commit -m "Initial commit - TideSight"
```

---

## 🚀 الحل الكامل

### الخطوة 1: التحقق من الحالة

```bash
cd d:\AquaERP

# التحقق من Branch
git branch

# التحقق من Commits
git log --oneline
```

### الخطوة 2: إعداد الهوية (إذا لم يكن موجوداً)

```bash
git config user.email "admin@tidesight.cloud"
git config user.name "TideSight Developer"
```

### الخطوة 3: إضافة و Commit

```bash
# إضافة الملفات
git add .

# Commit
git commit -m "Initial commit - TideSight"
```

### الخطوة 4: إنشاء/تغيير Branch إلى main

```bash
# إذا كان Branch الحالي master
git branch -M main

# أو إنشاء branch جديد
git checkout -b main
```

### الخطوة 5: Push

```bash
# Push إلى main
git push -u origin main

# أو إذا كان اسم Branch مختلف
git push -u origin HEAD
```

---

## 🔍 حلول بديلة

### إذا كان Repository يستخدم `master`

```bash
# Push إلى master
git push -u origin master
```

### إذا كان Repository فارغاً

```bash
# إنشاء branch main
git checkout -b main

# إضافة و commit
git add .
git commit -m "Initial commit - TideSight"

# Push
git push -u origin main
```

---

## 📝 أوامر سريعة

```bash
cd d:\AquaERP

# 1. إعداد الهوية
git config user.email "admin@tidesight.cloud"
git config user.name "TideSight Developer"

# 2. إضافة الملفات
git add .

# 3. Commit
git commit -m "Initial commit - TideSight"

# 4. إنشاء/تغيير Branch إلى main
git branch -M main

# 5. Push
git push -u origin main
```

---

**جاهز! 🎉**
