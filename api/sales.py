"""
API Endpoints للمبيعات والحصاد
"""
import logging
from ninja import Router
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal
from django.utils import timezone

from .auth import TokenAuth, ErrorResponse
from .permissions import require_feature
from sales.models import Harvest, SalesOrder, SalesOrderLine, Invoice
from biological.models import Batch
from sales.pdf_generator import InvoicePDFGenerator

router = Router()
logger = logging.getLogger('sales')


# ==================== Schemas ====================

class HarvestSchema(BaseModel):
    """Schema لعرض الحصاد"""
    id: int
    batch_id: int
    batch_number: str
    harvest_date: str
    quantity_kg: float
    count: int
    average_weight: float
    fair_value: float
    cost_per_kg: float
    status: str
    notes: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


class HarvestCreateSchema(BaseModel):
    """Schema لإنشاء حصاد"""
    batch_id: int
    harvest_date: date
    quantity_kg: float
    count: int
    average_weight: Optional[float] = None
    fair_value: Optional[float] = None
    cost_per_kg: Optional[float] = None
    status: str = 'pending'
    notes: Optional[str] = None


class SalesOrderLineSchema(BaseModel):
    """Schema لعرض بند طلب البيع"""
    id: int
    harvest_id: int
    quantity_kg: float
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True


class SalesOrderSchema(BaseModel):
    """Schema لعرض طلب البيع"""
    id: int
    order_number: str
    order_date: str
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    subtotal: float
    vat_rate: float
    vat_amount: float
    total_amount: float
    status: str
    notes: Optional[str] = None
    lines: List[SalesOrderLineSchema]
    created_by_id: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


class SalesOrderCreateSchema(BaseModel):
    """Schema لإنشاء طلب بيع"""
    order_date: date
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    vat_rate: float = 15.0
    lines: List[dict]  # [{'harvest_id': int, 'quantity_kg': float, 'unit_price': float}]
    notes: Optional[str] = None


class InvoiceSchema(BaseModel):
    """Schema لعرض الفاتورة"""
    id: int
    invoice_number: str
    sales_order_id: int
    invoice_date: str
    subtotal: float
    vat_amount: float
    total_amount: float
    status: str
    qr_code: Optional[str] = None
    uuid: Optional[str] = None
    zatca_status: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


# ==================== Harvest Endpoints ====================

@router.get('/harvests', response={200: List[HarvestSchema]}, auth=TokenAuth())
def list_harvests(request, batch_id: Optional[int] = None, status: Optional[str] = None):
    """قائمة الحصاد - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    queryset = Harvest.objects.select_related('batch', 'created_by').all()
    
    if batch_id:
        queryset = queryset.filter(batch_id=batch_id)
    if status:
        queryset = queryset.filter(status=status)
    
    harvests = queryset.order_by('-harvest_date', '-created_at')
    
    return [
        HarvestSchema(
            id=h.id,
            batch_id=h.batch.id,
            batch_number=h.batch.batch_number,
            harvest_date=h.harvest_date.isoformat(),
            quantity_kg=float(h.quantity_kg),
            count=h.count,
            average_weight=float(h.average_weight),
            fair_value=float(h.fair_value),
            cost_per_kg=float(h.cost_per_kg),
            status=h.status,
            notes=h.notes,
            created_by_id=h.created_by.id if h.created_by else None,
            created_at=h.created_at.isoformat(),
        )
        for h in harvests
    ]


@router.post('/harvests', response={201: HarvestSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_harvest(request, data: HarvestCreateSchema):
    """إنشاء حصاد جديد - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        batch = Batch.objects.select_related('pond', 'species').get(id=data.batch_id, is_active=True)
        
        # حساب التكلفة لكل كيلوجرام إذا لم يتم تحديدها
        cost_per_kg = data.cost_per_kg
        if not cost_per_kg or cost_per_kg == 0:
            # حساب التكلفة التراكمية للدفعة
            from daily_operations.models import FeedingLog
            from django.db.models import Sum
            
            total_feed_cost = FeedingLog.objects.filter(
                batch=batch,
                is_active=True
            ).aggregate(total=Sum('total_cost'))['total'] or Decimal('0.00')
            
            total_cost = batch.initial_cost + total_feed_cost
            
            if batch.current_weight > 0:
                cost_per_kg = total_cost / batch.current_weight
            else:
                cost_per_kg = Decimal('0.00')
        
        # حساب القيمة العادلة إذا لم يتم تحديدها
        fair_value = data.fair_value
        if not fair_value or fair_value == 0:
            fair_value = float(cost_per_kg * Decimal(str(data.quantity_kg)))
        
        harvest = Harvest.objects.create(
            batch=batch,
            harvest_date=data.harvest_date,
            quantity_kg=Decimal(str(data.quantity_kg)),
            count=data.count,
            average_weight=Decimal(str(data.average_weight)) if data.average_weight else None,
            fair_value=Decimal(str(fair_value)),
            cost_per_kg=Decimal(str(cost_per_kg)),
            status=data.status,
            notes=data.notes,
            created_by=request.auth if hasattr(request, 'auth') else None,
        )
        
        return 201, HarvestSchema(
            id=harvest.id,
            batch_id=harvest.batch.id,
            batch_number=harvest.batch.batch_number,
            harvest_date=harvest.harvest_date.isoformat(),
            quantity_kg=float(harvest.quantity_kg),
            count=harvest.count,
            average_weight=float(harvest.average_weight),
            fair_value=float(harvest.fair_value),
            cost_per_kg=float(harvest.cost_per_kg),
            status=harvest.status,
            notes=harvest.notes,
            created_by_id=harvest.created_by.id if harvest.created_by else None,
            created_at=harvest.created_at.isoformat(),
        )
    except Batch.DoesNotExist:
        logger.warning(f"محاولة إنشاء حصاد لدفعة غير موجودة: batch_id={data.batch_id}, user_id={getattr(request.auth, 'id', None)}")
        return 400, ErrorResponse(detail="الدفعة غير موجودة أو غير نشطة")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إنشاء الحصاد: batch_id={data.batch_id}, error={str(e)}", exc_info=True)
        return 400, ErrorResponse(detail=f"خطأ في إنشاء الحصاد: {str(e)}")


# ==================== Sales Order Endpoints ====================

@router.get('/sales-orders', response={200: List[SalesOrderSchema]}, auth=TokenAuth())
def list_sales_orders(request, status: Optional[str] = None):
    """قائمة طلبات البيع - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    queryset = SalesOrder.objects.select_related('created_by').prefetch_related('lines__harvest').all()
    
    if status:
        queryset = queryset.filter(status=status)
    
    orders = queryset.order_by('-order_date', '-created_at')
    
    result = []
    for order in orders:
        lines = [
            SalesOrderLineSchema(
                id=line.id,
                harvest_id=line.harvest.id,
                quantity_kg=float(line.quantity_kg),
                unit_price=float(line.unit_price),
                line_total=float(line.line_total),
            )
            for line in order.lines.all()
        ]
        
        result.append(SalesOrderSchema(
            id=order.id,
            order_number=order.order_number,
            order_date=order.order_date.isoformat(),
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            subtotal=float(order.subtotal),
            vat_rate=float(order.vat_rate),
            vat_amount=float(order.vat_amount),
            total_amount=float(order.total_amount),
            status=order.status,
            notes=order.notes,
            lines=lines,
            created_by_id=order.created_by.id if order.created_by else None,
            created_at=order.created_at.isoformat(),
        ))
    
    return result


@router.post('/sales-orders', response={201: SalesOrderSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_sales_order(request, data: SalesOrderCreateSchema):
    """إنشاء طلب بيع جديد - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        # توليد رقم الطلب
        from datetime import datetime
        order_count = SalesOrder.objects.filter(order_date=data.order_date).count()
        order_number = f"SO-{data.order_date.strftime('%Y%m%d')}-{order_count + 1:04d}"
        
        # حساب المجموع الفرعي
        subtotal = Decimal('0.00')
        for line_data in data.lines:
            line_total = Decimal(str(line_data['quantity_kg'])) * Decimal(str(line_data['unit_price']))
            subtotal += line_total
        
        # إنشاء طلب البيع
        order = SalesOrder.objects.create(
            order_number=order_number,
            order_date=data.order_date,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            customer_address=data.customer_address,
            subtotal=subtotal,
            vat_rate=Decimal(str(data.vat_rate)),
            notes=data.notes,
            created_by=request.auth if hasattr(request, 'auth') else None,
        )
        
        # إنشاء بنود الطلب
        lines_data = []
        for line_data in data.lines:
            harvest = Harvest.objects.select_related('batch').get(id=line_data['harvest_id'], status='completed')
            line = SalesOrderLine.objects.create(
                sales_order=order,
                harvest=harvest,
                quantity_kg=Decimal(str(line_data['quantity_kg'])),
                unit_price=Decimal(str(line_data['unit_price'])),
            )
            lines_data.append(SalesOrderLineSchema(
                id=line.id,
                harvest_id=line.harvest.id,
                quantity_kg=float(line.quantity_kg),
                unit_price=float(line.unit_price),
                line_total=float(line.line_total),
            ))
        
        order.refresh_from_db()
        
        return 201, SalesOrderSchema(
            id=order.id,
            order_number=order.order_number,
            order_date=order.order_date.isoformat(),
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            subtotal=float(order.subtotal),
            vat_rate=float(order.vat_rate),
            vat_amount=float(order.vat_amount),
            total_amount=float(order.total_amount),
            status=order.status,
            notes=order.notes,
            lines=lines_data,
            created_by_id=order.created_by.id if order.created_by else None,
            created_at=order.created_at.isoformat(),
        )
    except Harvest.DoesNotExist:
        return 400, ErrorResponse(detail="الحصاد غير موجود")
    except Exception as e:
        return 400, ErrorResponse(detail=f"خطأ في إنشاء طلب البيع: {str(e)}")


# ==================== Invoice Endpoints ====================

@router.get('/invoices', response={200: List[InvoiceSchema]}, auth=TokenAuth())
def list_invoices(request, status: Optional[str] = None):
    """قائمة الفواتير - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    queryset = Invoice.objects.select_related('sales_order', 'created_by').all()
    
    if status:
        queryset = queryset.filter(status=status)
    
    invoices = queryset.order_by('-invoice_date', '-created_at')
    
    return [
        InvoiceSchema(
            id=inv.id,
            invoice_number=inv.invoice_number,
            sales_order_id=inv.sales_order.id,
            invoice_date=inv.invoice_date.isoformat(),
            subtotal=float(inv.subtotal),
            vat_amount=float(inv.vat_amount),
            total_amount=float(inv.total_amount),
            status=inv.status,
            qr_code=inv.qr_code,
            uuid=inv.uuid,
            zatca_status=inv.zatca_status,
            created_by_id=inv.created_by.id if inv.created_by else None,
            created_at=inv.created_at.isoformat(),
        )
        for inv in invoices
    ]


class InvoiceCreateSchema(BaseModel):
    """Schema لإنشاء فاتورة"""
    sales_order_id: int


@router.post('/invoices', response={201: InvoiceSchema, 400: ErrorResponse, 404: ErrorResponse}, auth=TokenAuth())
def create_invoice(request, data: InvoiceCreateSchema):
    """إنشاء فاتورة من طلب بيع - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        sales_order = SalesOrder.objects.get(id=data.sales_order_id, status__in=['confirmed', 'draft'])
        
        if hasattr(sales_order, 'invoice'):
            return 400, ErrorResponse(detail="هذا الطلب لديه فاتورة بالفعل")
        
        # توليد رقم الفاتورة
        from datetime import datetime
        invoice_count = Invoice.objects.filter(invoice_date=timezone.now().date()).count()
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{invoice_count + 1:04d}"
        
        # إنشاء الفاتورة
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            sales_order=sales_order,
            invoice_date=timezone.now().date(),
            subtotal=sales_order.subtotal,
            vat_amount=sales_order.vat_amount,
            total_amount=sales_order.total_amount,
            status='issued',
            created_by=request.auth if hasattr(request, 'auth') else None,
        )
        
        # تحديث حالة طلب البيع
        sales_order.status = 'invoiced'
        sales_order.save(update_fields=['status'])
        
        return 201, InvoiceSchema(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            sales_order_id=invoice.sales_order.id,
            invoice_date=invoice.invoice_date.isoformat(),
            subtotal=float(invoice.subtotal),
            vat_amount=float(invoice.vat_amount),
            total_amount=float(invoice.total_amount),
            status=invoice.status,
            qr_code=invoice.qr_code,
            uuid=invoice.uuid,
            zatca_status=invoice.zatca_status,
            created_by_id=invoice.created_by.id if invoice.created_by else None,
            created_at=invoice.created_at.isoformat(),
        )
    except SalesOrder.DoesNotExist:
        logger.warning(f"محاولة إنشاء فاتورة لطلب بيع غير موجود: sales_order_id={data.sales_order_id}, user_id={getattr(request.auth, 'id', None)}")
        return 400, ErrorResponse(detail="طلب البيع غير موجود أو غير مؤهل لإنشاء فاتورة")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إنشاء الفاتورة: sales_order_id={data.sales_order_id}, error={str(e)}", exc_info=True)
        return 400, ErrorResponse(detail=f"خطأ في إنشاء الفاتورة: {str(e)}")


# ==================== PDF Export ====================

@router.get('/invoices/{invoice_id}/pdf', response={200: bytes, 404: ErrorResponse}, auth=TokenAuth())
def get_invoice_pdf(request, invoice_id: int):
    """تحميل PDF للفاتورة - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        from django.http import HttpResponse
        
        invoice = Invoice.objects.select_related('sales_order').prefetch_related('sales_order__lines__harvest').get(id=invoice_id)
        
        # TODO: جلب بيانات البائع من إعدادات Tenant
        seller_name = "AquaERP Farm"
        seller_vat_number = "123456789012345"
        seller_address = ""
        
        # توليد PDF
        pdf_generator = InvoicePDFGenerator(seller_name, seller_vat_number, seller_address)
        pdf_buffer = pdf_generator.generate_pdf(invoice)
        
        # إرجاع PDF كـ response
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{invoice.invoice_number}.pdf"'
        return response
        
    except Invoice.DoesNotExist:
        return 404, ErrorResponse(detail="الفاتورة غير موجودة")
    except Exception as e:
        return 400, ErrorResponse(detail=f"خطأ في توليد PDF: {str(e)}")

