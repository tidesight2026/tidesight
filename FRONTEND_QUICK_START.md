# ⚡ بدء سريع - Frontend

دليل سريع لإنشاء Frontend في 10 دقائق.

---

## الخطوة 1: إنشاء المشروع (2 دقيقة)

```bash
cd D:\AquaERP
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

## الخطوة 2: تثبيت المكتبات (3 دقائق)

```bash
npm install axios react-router-dom zustand react-hook-form zod @hookform/resolvers date-fns
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## الخطوة 3: نسخ ملفات التكوين (2 دقيقة)

انسخ من `frontend_configs/`:
- `tailwind.config.js` → `frontend/tailwind.config.js`
- `index.css` → `frontend/src/index.css`

## الخطوة 4: إنشاء الملفات الأساسية (3 دقائق)

راجع `FRONTEND_FILES.md` لجميع الملفات المطلوبة.

---

## ✅ التحقق

```bash
npm run dev
```

إذا فتح المتصفح على `http://localhost:5173` بدون أخطاء = نجح! ✅

---

**الخطوة التالية:** ابدأ بإنشاء الملفات المذكورة في `FRONTEND_FILES.md`

