"""
API Endpoints للتتبع (Traceability)
"""
import logging
from ninja import Router
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal

from .auth import TokenAuth, ErrorResponse
from .permissions import require_feature
from sales.models import Harvest, SalesOrder, SalesOrderLine, Invoice
from biological.models import Batch, Pond, Species
from daily_operations.models import FeedingLog, MortalityLog

router = Router()
logger = logging.getLogger('api')


# ==================== Schemas ====================

class BatchInfoSchema(BaseModel):
    """معلومات الدفعة"""
    id: int
    batch_number: str
    start_date: str
    species_name: str
    pond_name: str
    initial_count: int
    initial_weight: float
    current_count: int
    current_weight: float
    status: str

    class Config:
        from_attributes = True


class HarvestInfoSchema(BaseModel):
    """معلومات الحصاد"""
    id: int
    harvest_date: str
    quantity_kg: float
    count: int
    average_weight: float
    status: str

    class Config:
        from_attributes = True


class SalesOrderInfoSchema(BaseModel):
    """معلومات طلب البيع"""
    id: int
    order_number: str
    order_date: str
    customer_name: str
    total_amount: float
    status: str

    class Config:
        from_attributes = True


class InvoiceInfoSchema(BaseModel):
    """معلومات الفاتورة"""
    id: int
    invoice_number: str
    invoice_date: str
    total_amount: float
    status: str

    class Config:
        from_attributes = True


class FeedingLogInfoSchema(BaseModel):
    """معلومات سجل التغذية"""
    id: int
    feeding_date: str
    quantity: float
    feed_type_name: str

    class Config:
        from_attributes = True


class MortalityLogInfoSchema(BaseModel):
    """معلومات سجل النفوق"""
    id: int
    mortality_date: str
    count: int
    cause: Optional[str] = None

    class Config:
        from_attributes = True


class TraceabilityByInvoiceSchema(BaseModel):
    """سلسلة التتبع من الفاتورة إلى الدفعة"""
    invoice: InvoiceInfoSchema
    sales_order: SalesOrderInfoSchema
    harvests: List[HarvestInfoSchema]
    batches: List[BatchInfoSchema]
    feeding_logs: List[FeedingLogInfoSchema]
    mortality_logs: List[MortalityLogInfoSchema]


class TraceabilityByBatchSchema(BaseModel):
    """سلسلة التتبع من الدفعة إلى المبيعات"""
    batch: BatchInfoSchema
    harvests: List[HarvestInfoSchema]
    sales_orders: List[SalesOrderInfoSchema]
    invoices: List[InvoiceInfoSchema]
    feeding_logs: List[FeedingLogInfoSchema]
    mortality_logs: List[MortalityLogInfoSchema]


# ==================== Endpoints ====================

@router.get('/by-invoice/{invoice_id}', response={200: TraceabilityByInvoiceSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_traceability_by_invoice(request, invoice_id: int):
    """
    استرجاع سلسلة التتبع من الفاتورة إلى الدفعة
    
    يعيد معلومات كاملة عن:
    - الفاتورة
    - طلب البيع المرتبط
    - الحصاد المرتبط
    - الدفعات المرتبطة
    - سجلات التغذية والنفوق
    """
    try:
        # الحصول على الفاتورة
        invoice = Invoice.objects.select_related(
            'sales_order',
            'sales_order__invoice'
        ).get(id=invoice_id)
        
        # الحصول على طلب البيع
        sales_order = invoice.sales_order
        
        # الحصول على بنود طلب البيع مع الحصاد
        sales_order_lines = SalesOrderLine.objects.select_related(
            'harvest',
            'harvest__batch',
            'harvest__batch__species',
            'harvest__batch__pond'
        ).filter(sales_order=sales_order)
        
        # جمع الحصاد والدفعات
        harvests = []
        batches = []
        batch_ids = set()
        
        for line in sales_order_lines:
            harvest = line.harvest
            if harvest:
                harvests.append(harvest)
                if harvest.batch and harvest.batch.id not in batch_ids:
                    batches.append(harvest.batch)
                    batch_ids.add(harvest.batch.id)
        
        # جمع سجلات التغذية والنفوق للدفعات
        feeding_logs = FeedingLog.objects.select_related(
            'feed_type'
        ).filter(batch_id__in=batch_ids).order_by('-feeding_date')[:50]  # آخر 50 سجل
        
        mortality_logs = MortalityLog.objects.filter(
            batch_id__in=batch_ids
        ).order_by('-mortality_date')[:50]  # آخر 50 سجل
        
        # بناء الاستجابة
        return 200, TraceabilityByInvoiceSchema(
            invoice=InvoiceInfoSchema(
                id=invoice.id,
                invoice_number=invoice.invoice_number,
                invoice_date=invoice.invoice_date.isoformat(),
                total_amount=float(invoice.total_amount),
                status=invoice.status
            ),
            sales_order=SalesOrderInfoSchema(
                id=sales_order.id,
                order_number=sales_order.order_number,
                order_date=sales_order.order_date.isoformat(),
                customer_name=sales_order.customer_name,
                total_amount=float(sales_order.total_amount),
                status=sales_order.status
            ),
            harvests=[
                HarvestInfoSchema(
                    id=h.id,
                    harvest_date=h.harvest_date.isoformat(),
                    quantity_kg=float(h.quantity_kg),
                    count=h.count,
                    average_weight=float(h.average_weight),
                    status=h.status
                ) for h in harvests
            ],
            batches=[
                BatchInfoSchema(
                    id=b.id,
                    batch_number=b.batch_number,
                    start_date=b.start_date.isoformat(),
                    species_name=b.species.arabic_name,
                    pond_name=b.pond.name,
                    initial_count=b.initial_count,
                    initial_weight=float(b.initial_weight),
                    current_count=b.current_count,
                    current_weight=float(b.current_weight),
                    status=b.status
                ) for b in batches
            ],
            feeding_logs=[
                FeedingLogInfoSchema(
                    id=fl.id,
                    feeding_date=fl.feeding_date.isoformat(),
                    quantity=float(fl.quantity),
                    feed_type_name=fl.feed_type.arabic_name if fl.feed_type else 'غير محدد'
                ) for fl in feeding_logs
            ],
            mortality_logs=[
                MortalityLogInfoSchema(
                    id=ml.id,
                    mortality_date=ml.mortality_date.isoformat(),
                    count=ml.count,
                    cause=ml.cause
                ) for ml in mortality_logs
            ]
        )
        
    except Invoice.DoesNotExist:
        logger.warning(f"محاولة استرجاع تتبع لفاتورة غير موجودة: invoice_id={invoice_id}, user_id={getattr(request.auth, 'id', None)}")
        return 404, ErrorResponse(detail=f"الفاتورة رقم {invoice_id} غير موجودة")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في استرجاع التتبع من الفاتورة: invoice_id={invoice_id}, error={str(e)}", exc_info=True)
        return 500, ErrorResponse(detail=f"خطأ في استرجاع البيانات: {str(e)}")


@router.get('/by-batch/{batch_id}', response={200: TraceabilityByBatchSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_traceability_by_batch(request, batch_id: int):
    """
    استرجاع سلسلة التتبع من الدفعة إلى المبيعات
    
    يعيد معلومات كاملة عن:
    - الدفعة
    - جميع الحصاد المرتبطة
    - جميع طلبات البيع المرتبطة
    - جميع الفواتير المرتبطة
    - سجلات التغذية والنفوق
    """
    try:
        # الحصول على الدفعة
        batch = Batch.objects.select_related(
            'species',
            'pond'
        ).get(id=batch_id)
        
        # الحصول على جميع الحصاد المرتبطة
        harvests = Harvest.objects.filter(batch=batch).order_by('-harvest_date')
        
        # الحصول على جميع بنود طلبات البيع المرتبطة بالحصاد
        harvest_ids = [h.id for h in harvests]
        sales_order_lines = SalesOrderLine.objects.select_related(
            'sales_order',
            'sales_order__invoice'
        ).filter(harvest_id__in=harvest_ids)
        
        # جمع طلبات البيع والفواتير
        sales_orders = []
        invoices = []
        sales_order_ids = set()
        invoice_ids = set()
        
        for line in sales_order_lines:
            sales_order = line.sales_order
            if sales_order and sales_order.id not in sales_order_ids:
                sales_orders.append(sales_order)
                sales_order_ids.add(sales_order.id)
            
            # الحصول على الفاتورة المرتبطة
            if hasattr(sales_order, 'invoice') and sales_order.invoice:
                invoice = sales_order.invoice
                if invoice.id not in invoice_ids:
                    invoices.append(invoice)
                    invoice_ids.add(invoice.id)
        
        # الحصول على سجلات التغذية والنفوق
        feeding_logs = FeedingLog.objects.select_related(
            'feed_type'
        ).filter(batch=batch).order_by('-feeding_date')
        
        mortality_logs = MortalityLog.objects.filter(
            batch=batch
        ).order_by('-mortality_date')
        
        # بناء الاستجابة
        return 200, TraceabilityByBatchSchema(
            batch=BatchInfoSchema(
                id=batch.id,
                batch_number=batch.batch_number,
                start_date=batch.start_date.isoformat(),
                species_name=batch.species.arabic_name,
                pond_name=batch.pond.name,
                initial_count=batch.initial_count,
                initial_weight=float(batch.initial_weight),
                current_count=batch.current_count,
                current_weight=float(batch.current_weight),
                status=batch.status
            ),
            harvests=[
                HarvestInfoSchema(
                    id=h.id,
                    harvest_date=h.harvest_date.isoformat(),
                    quantity_kg=float(h.quantity_kg),
                    count=h.count,
                    average_weight=float(h.average_weight),
                    status=h.status
                ) for h in harvests
            ],
            sales_orders=[
                SalesOrderInfoSchema(
                    id=so.id,
                    order_number=so.order_number,
                    order_date=so.order_date.isoformat(),
                    customer_name=so.customer_name,
                    total_amount=float(so.total_amount),
                    status=so.status
                ) for so in sales_orders
            ],
            invoices=[
                InvoiceInfoSchema(
                    id=inv.id,
                    invoice_number=inv.invoice_number,
                    invoice_date=inv.invoice_date.isoformat(),
                    total_amount=float(inv.total_amount),
                    status=inv.status
                ) for inv in invoices
            ],
            feeding_logs=[
                FeedingLogInfoSchema(
                    id=fl.id,
                    feeding_date=fl.feeding_date.isoformat(),
                    quantity=float(fl.quantity),
                    feed_type_name=fl.feed_type.arabic_name if fl.feed_type else 'غير محدد'
                ) for fl in feeding_logs
            ],
            mortality_logs=[
                MortalityLogInfoSchema(
                    id=ml.id,
                    mortality_date=ml.mortality_date.isoformat(),
                    count=ml.count,
                    cause=ml.cause
                ) for ml in mortality_logs
            ]
        )
        
    except Batch.DoesNotExist:
        logger.warning(f"محاولة استرجاع تتبع لدفعة غير موجودة: batch_id={batch_id}, user_id={getattr(request.auth, 'id', None)}")
        return 404, ErrorResponse(detail=f"الدفعة رقم {batch_id} غير موجودة")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في استرجاع التتبع من الدفعة: batch_id={batch_id}, error={str(e)}", exc_info=True)
        return 500, ErrorResponse(detail=f"خطأ في استرجاع البيانات: {str(e)}")
