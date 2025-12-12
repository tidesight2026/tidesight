# 📝 دليل إعداد Frontend خطوة بخطوة

هذا الدليل يوضح كيفية إعداد Frontend من الصفر.

---

## الخطوة 1: إنشاء المشروع

```bash
cd D:\AquaERP
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

## الخطوة 2: تثبيت المكتبات

```bash
# المكتبات الأساسية
npm install axios react-router-dom zustand

# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# إعداد Tailwind
npx tailwindcss init -p

# مكتبات إضافية
npm install react-hook-form zod @hookform/resolvers
npm install date-fns
```

## الخطوة 3: نسخ ملفات التكوين

انسخ الملفات التالية من `frontend_configs/` إلى `frontend/`:
- `tailwind.config.js`
- `vite.config.ts` (تعديل)
- `src/index.css`
- `src/types/index.ts`

## الخطوة 4: إنشاء الملفات

اتبع الهيكل المذكور في `FRONTEND_SETUP.md`

## الخطوة 5: الاختبار

```bash
npm run dev
```

افتح المتصفح على: `http://localhost:5173`

---

**ملاحظة:** الملفات المطلوبة ستُنشأ في الخطوات التالية.

