# 🔧 حل مشكلة Git Repository

## ⚠️ المشكلة

```
fatal: not a git repository (or any of the parent directories): .git
```

**السبب:** المجلد `/opt/tidesight` موجود لكنه ليس Git repository.

---

## ✅ الحل: إعادة Clone

### الطريقة 1: حذف المجلد والـ Clone من جديد (موصى به)

```bash
# الانتقال للمجلد الأب
cd /opt

# حذف المجلد القديم (⚠️ احفظ .env.prod أولاً!)
cp tidesight/.env.prod /tmp/.env.prod.backup

# حذف المجلد
rm -rf tidesight

# Clone من جديد
git clone https://github.com/tidesight2026/tidesight.git tidesight

# استعادة .env.prod
cp /tmp/.env.prod.backup tidesight/.env.prod

# التحقق
cd tidesight
git status
cat .env.prod
```

### الطريقة 2: تهيئة Git في المجلد الحالي

```bash
cd /opt/tidesight

# تهيئة Git
git init

# إضافة Remote
git remote add origin https://github.com/tidesight2026/tidesight.git

# Fetch
git fetch origin

# Merge
git merge origin/main --allow-unrelated-histories
```

---

## 🚀 الأوامر السريعة (الطريقة 1 - موصى به)

```bash
cd /opt
cp tidesight/.env.prod /tmp/.env.prod.backup
rm -rf tidesight
git clone https://github.com/tidesight2026/tidesight.git tidesight
cp /tmp/.env.prod.backup tidesight/.env.prod
cd tidesight
cat .env.prod
```

---

**جاهز! 🎉**
