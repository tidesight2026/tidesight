# 🎨 Frontend - AquaERP

**الحالة:** جاهز للإنشاء  
**التاريخ:** ديسمبر 2025

---

## 📋 نظرة عامة

واجهة مستخدم حديثة لـ AquaERP باستخدام:

- ⚛️ React 18 + TypeScript
- ⚡ Vite
- 🎨 Tailwind CSS (مع RTL)
- 🛣️ React Router
- 🐻 Zustand (State Management)
- 📡 Axios

---

## 🚀 البدء السريع

### الخطوة 1: إنشاء المشروع

```bash
cd D:\AquaERP
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### الخطوة 2: تثبيت المكتبات

```bash
# المكتبات الأساسية
npm install axios react-router-dom zustand react-hook-form zod @hookform/resolvers date-fns

# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### الخطوة 3: إعداد الملفات

انسخ ملفات التكوين من `frontend_configs/`:

- `tailwind.config.js`
- `index.css`

### الخطوة 4: إنشاء الملفات

اتبع `FRONTEND_FILES_GUIDE.md` لإنشاء جميع الملفات المطلوبة.

---

## 📚 الأدلة المتاحة

1. **[FRONTEND_QUICK_START.md](FRONTEND_QUICK_START.md)** - بدء سريع في 10 دقائق
2. **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - دليل الإعداد الشامل
3. **[FRONTEND_FILES_GUIDE.md](FRONTEND_FILES_GUIDE.md)** - جميع الملفات المطلوبة مع محتواها
4. **[CREATE_FRONTEND.md](CREATE_FRONTEND.md)** - دليل إنشاء المشروع خطوة بخطوة

---

## 📁 الهيكل

```
frontend/
├── src/
│   ├── components/     # المكونات
│   ├── pages/          # الصفحات
│   ├── services/       # خدمات API
│   ├── store/          # State Management
│   ├── utils/          # Utilities
│   └── types/          # TypeScript Types
└── ...
```

---

## 🎯 الميزات

- ✅ RTL Support (دعم العربية الكامل)
- ✅ Cairo Font
- ✅ Responsive Design
- ✅ Form Validation
- ✅ JWT Authentication
- ✅ Protected Routes
- ✅ API Integration

---

## 🔗 الربط مع Backend

- **API Base URL:** `http://localhost:8000/api`
- **Swagger UI:** `http://farm1.localhost:8000/api/docs`

---

## 🧪 الاختبار

```bash
npm run dev
```

افتح: `http://localhost:5173`

---

## 📝 ملاحظات

- تأكد من تشغيل Backend قبل اختبار Frontend
- استخدم Proxy في `vite.config.ts` لتجنب مشاكل CORS
- جميع الملفات المطلوبة موجودة في الأدلة

---

**جاهز للبدء! 🚀**
