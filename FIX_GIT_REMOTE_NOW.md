# 🔧 تصحيح Git Remote URL - الآن

## ⚠️ المشكلة الحالية

```
origin  https://github.com/tidesight2026/tidesight/tidesight.git (fetch)
origin  https://github.com/tidesight2026/tidesight/tidesight.git (push)
```

**URL خاطئ:** يحتوي على `tidesight` مرتين.

---

## ✅ الحل السريع

```bash
# تصحيح URL
git remote set-url origin https://github.com/tidesight2026/tidesight.git

# التحقق
git remote -v

# يجب أن ترى:
# origin  https://github.com/tidesight2026/tidesight.git (fetch)
# origin  https://github.com/tidesight2026/tidesight.git (push)
```

---

## 🚀 ثم Push

```bash
git push -u origin main
```

---

## 📝 الأوامر الكاملة

```bash
# 1. تصحيح Remote URL
git remote set-url origin https://github.com/tidesight2026/tidesight.git

# 2. التحقق
git remote -v

# 3. Push
git push -u origin main
```

---

**ملاحظة:** تأكد من كتابة `git` وليس `it` 😊

---

**جاهز! 🎉**
