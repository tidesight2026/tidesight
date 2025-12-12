"""
API Endpoints لـ ZATCA Integration
"""
from ninja import Router
from django.http import HttpResponse
from .auth import TokenAuth, ErrorResponse
from sales.models import Invoice
from sales.zatca import ZATCAIntegration

router = Router()


@router.get('/invoices/{invoice_id}/qr-code', response={200: dict, 404: ErrorResponse}, auth=TokenAuth())
def get_invoice_qr_code(request, invoice_id: int):
    """الحصول على QR Code للفاتورة - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        if not invoice.qr_code:
            return 400, ErrorResponse(detail="QR Code غير متوفر لهذه الفاتورة")
        
        return {
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'qr_code': invoice.qr_code,
        }
    except Invoice.DoesNotExist:
        return 404, ErrorResponse(detail="الفاتورة غير موجودة")


@router.get('/invoices/{invoice_id}/qr-image', response={200: bytes, 404: ErrorResponse}, auth=TokenAuth())
def get_invoice_qr_image(request, invoice_id: int):
    """الحصول على صورة QR Code للفاتورة - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        if not invoice.qr_code:
            return 400, ErrorResponse(detail="QR Code غير متوفر لهذه الفاتورة")
        
        # TODO: جلب بيانات البائع من إعدادات Tenant
        seller_name = "AquaERP Farm"
        seller_vat_number = "123456789012345"
        
        zatca = ZATCAIntegration(seller_name, seller_vat_number)
        qr_image = zatca.generate_qr_code_image(invoice.qr_code)
        
        response = HttpResponse(qr_image, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="qr_{invoice.invoice_number}.png"'
        return response
        
    except Invoice.DoesNotExist:
        return 404, ErrorResponse(detail="الفاتورة غير موجودة")
    except Exception as e:
        return 400, ErrorResponse(detail=f"خطأ في توليد صورة QR Code: {str(e)}")


@router.get('/invoices/{invoice_id}/xml', response={200: dict, 404: ErrorResponse}, auth=TokenAuth())
def get_invoice_xml(request, invoice_id: int):
    """الحصول على XML للفاتورة - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        # TODO: جلب بيانات البائع من إعدادات Tenant
        seller_name = "AquaERP Farm"
        seller_vat_number = "123456789012345"
        
        zatca = ZATCAIntegration(seller_name, seller_vat_number)
        xml_string = zatca.generate_ubl_xml(invoice)
        
        return {
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'xml': xml_string,
        }
    except Invoice.DoesNotExist:
        return 404, ErrorResponse(detail="الفاتورة غير موجودة")
    except Exception as e:
        return 400, ErrorResponse(detail=f"خطأ في توليد XML: {str(e)}")


@router.get('/invoices/{invoice_id}/xml-download', response={200: bytes, 404: ErrorResponse}, auth=TokenAuth())
def download_invoice_xml(request, invoice_id: int):
    """تحميل ملف XML للفاتورة - يتطلب صلاحية sales"""
    from .permissions import check_feature_permission
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    user_role = getattr(request.auth, 'role', None)
    if not check_feature_permission(user_role, 'sales'):
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى المبيعات")
    
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        # TODO: جلب بيانات البائع من إعدادات Tenant
        seller_name = "AquaERP Farm"
        seller_vat_number = "123456789012345"
        
        zatca = ZATCAIntegration(seller_name, seller_vat_number)
        xml_string = zatca.generate_ubl_xml(invoice)
        
        response = HttpResponse(xml_string, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.xml"'
        return response
        
    except Invoice.DoesNotExist:
        return 404, ErrorResponse(detail="الفاتورة غير موجودة")
    except Exception as e:
        return 400, ErrorResponse(detail=f"خطأ في توليد XML: {str(e)}")

