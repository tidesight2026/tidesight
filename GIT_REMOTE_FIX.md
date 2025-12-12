# 🔧 حل مشكلة Git Remote URL - TideSight

## ⚠️ المشكلة

```
remote: Not Found
fatal: repository 'https://github.com/tidesight2026/tidesight/tidesight.git/' not found
```

**السبب:** URL الخاص بـ Remote غير صحيح - يحتوي على `tidesight` مرتين.

---

## ✅ الحل

### الخطوة 1: التحقق من Remote الحالي

```bash
git remote -v
```

سترى شيء مثل:
```
origin  https://github.com/tidesight2026/tidesight/tidesight.git (fetch)
origin  https://github.com/tidesight2026/tidesight/tidesight.git (push)
```

### الخطوة 2: تصحيح Remote URL

**URL الصحيح يجب أن يكون:**
```
https://github.com/tidesight2026/tidesight.git
```

**وليس:**
```
https://github.com/tidesight2026/tidesight/tidesight.git
```

### الخطوة 3: تحديث Remote

```bash
# حذف Remote الحالي
git remote remove origin

# إضافة Remote الصحيح
git remote add origin https://github.com/tidesight2026/tidesight.git

# أو تحديث URL مباشرة
git remote set-url origin https://github.com/tidesight2026/tidesight.git
```

### الخطوة 4: التحقق

```bash
git remote -v
```

يجب أن ترى:
```
origin  https://github.com/tidesight2026/tidesight.git (fetch)
origin  https://github.com/tidesight2026/tidesight.git (push)
```

### الخطوة 5: Push

```bash
git push -u origin main
```

---

## 🔍 حلول بديلة

### إذا كان Repository اسمه مختلف

```bash
# تحقق من اسم Repository الصحيح على GitHub
# ثم استخدم:
git remote set-url origin https://github.com/tidesight2026/REPOSITORY_NAME.git
```

### إذا كان Repository خاص (Private)

```bash
# قد تحتاج إلى استخدام Personal Access Token
# أو استخدام SSH:
git remote set-url origin git@github.com:tidesight2026/tidesight.git
```

---

## 📝 الأوامر الكاملة

```bash
cd d:\AquaERP

# 1. التحقق من Remote
git remote -v

# 2. تصحيح URL
git remote set-url origin https://github.com/tidesight2026/tidesight.git

# 3. التحقق مرة أخرى
git remote -v

# 4. Push
git push -u origin main
```

---

## ⚠️ ملاحظات مهمة

1. **تأكد من وجود Repository على GitHub:**
   - اذهب إلى: `https://github.com/tidesight2026/tidesight`
   - تأكد من أن Repository موجود

2. **إذا كان Repository فارغاً:**
   - GitHub قد يطلب منك إنشاء README أولاً
   - أو يمكنك Push مباشرة

3. **إذا كان Repository خاص:**
   - قد تحتاج إلى Personal Access Token
   - أو استخدام SSH Keys

---

**جاهز! 🎉**
