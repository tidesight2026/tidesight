# Multi-stage build للـ Frontend
# المرحلة 1: بناء React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Build argument for API URL
ARG VITE_API_BASE_URL=https://tidesight.cloud

# نسخ ملفات package
COPY package*.json ./

# تثبيت المكتبات
RUN npm ci --only=production=false

# نسخ الكود المصدري
COPY . .

# تعيين متغير البيئة للبناء
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# بناء التطبيق للإنتاج
RUN npm run build

# المرحلة 2: تقديم الملفات الثابتة باستخدام Nginx
FROM nginx:alpine

# نسخ ملفات البناء من المرحلة السابقة
COPY --from=builder /app/dist /usr/share/nginx/html

# نسخ إعدادات Nginx المخصصة
COPY nginx.conf /etc/nginx/conf.d/default.conf

# فتح المنفذ 80
EXPOSE 80

# تشغيل Nginx
CMD ["nginx", "-g", "daemon off;"]

