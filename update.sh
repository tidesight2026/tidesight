#!/bin/bash
# TideSight Update Script
# يستخدم Git لسحب التحديثات وإعادة نشر التطبيق

set -e

echo "=========================================="
echo "TideSight Update Script"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="/opt/tidesight"

# التحقق من وجود المجلد
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ مجلد المشروع غير موجود: $PROJECT_DIR${NC}"
    exit 1
fi

cd $PROJECT_DIR

# التحقق من Git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ هذا ليس Git repository${NC}"
    exit 1
fi

echo -e "${GREEN}🔄 سحب التحديثات من Git...${NC}"
git fetch origin
git pull origin main || git pull origin master

echo -e "${GREEN}🔨 إعادة بناء الصور...${NC}"
docker-compose -f docker-compose.prod.yml build

echo -e "${GREEN}🚀 إعادة تشغيل الخدمات...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${GREEN}⏳ انتظار 10 ثواني...${NC}"
sleep 10

echo -e "${GREEN}📊 تشغيل Migrations...${NC}"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate_schemas --shared || true
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate_schemas --tenant || true

echo -e "${GREEN}📦 جمع Static Files...${NC}"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput || true

echo -e "${GREEN}✅ تم التحديث بنجاح!${NC}"
echo ""
echo "📊 حالة الخدمات:"
docker-compose -f docker-compose.prod.yml ps
