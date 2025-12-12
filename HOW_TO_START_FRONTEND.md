# كيفية تشغيل Frontend - AquaERP

## 🚀 تشغيل Frontend للتطوير

### 1. الانتقال إلى مجلد Frontend
```bash
cd frontend
```

### 2. تثبيت المكتبات (إذا لم تكن مثبتة)
```bash
npm install
```

### 3. تشغيل Frontend
```bash
npm run dev
```

Frontend سيعمل على: `http://localhost:5175`

---

## 🔧 إعداد API URL لكل Tenant

### إنشاء ملف `.env` في `frontend/`

**لـ Farm 1:**
```env
VITE_API_BASE_URL=http://farm1.localhost:8000
```

**لـ TMCO:**
```env
VITE_API_BASE_URL=http://tmco.localhost:8000
```

---

## 📱 الوصول

### صفحة تسجيل الدخول
```
http://localhost:5175/login
```

### بعد تسجيل الدخول
سيتم توجيهك تلقائياً إلى:
```
http://localhost:5175/dashboard
```

---

## ⚠️ ملاحظات مهمة

1. **يجب أن يكون Backend يعمل** على `http://localhost:8000` أو tenant domain
2. **يجب إضافة tenant domains إلى hosts file**:
   ```
   127.0.0.1    farm1.localhost
   127.0.0.1    tmco.localhost
   ```
3. **يجب تحديث `VITE_API_BASE_URL`** في `.env` لكل tenant

---

**جاهز للاستخدام! 🎉**
