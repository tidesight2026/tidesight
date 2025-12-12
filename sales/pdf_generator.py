"""
PDF Generator للفواتير الضريبية السعودية
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from io import BytesIO
import base64
from decimal import Decimal
from typing import Optional
from datetime import datetime

from .models import Invoice
from .zatca import ZATCAIntegration


class InvoicePDFGenerator:
    """
    كلاس لتوليد PDF للفواتير الضريبية السعودية
    """
    
    def __init__(self, seller_name: str, seller_vat_number: str, seller_address: str = ""):
        self.seller_name = seller_name
        self.seller_vat_number = seller_vat_number
        self.seller_address = seller_address
        self.zatca = ZATCAIntegration(seller_name, seller_vat_number, seller_address)
    
    def generate_pdf(self, invoice: Invoice) -> BytesIO:
        """
        توليد PDF للفاتورة
        
        Returns:
            BytesIO: ملف PDF في الذاكرة
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
        )
        
        # إنشاء Story (المحتوى)
        story = []
        
        # إضافة العناصر
        story.extend(self._create_header(invoice))
        story.append(Spacer(1, 10*mm))
        story.extend(self._create_invoice_info(invoice))
        story.append(Spacer(1, 5*mm))
        story.extend(self._create_customer_info(invoice))
        story.append(Spacer(1, 5*mm))
        story.extend(self._create_items_table(invoice))
        story.append(Spacer(1, 5*mm))
        story.extend(self._create_totals_table(invoice))
        story.append(Spacer(1, 10*mm))
        story.extend(self._create_qr_code(invoice))
        story.append(Spacer(1, 5*mm))
        story.extend(self._create_footer(invoice))
        
        # بناء PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_header(self, invoice: Invoice):
        """إنشاء رأس الفاتورة"""
        styles = getSampleStyleSheet()
        
        # عنوان رئيسي
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1f2937'),
            alignment=TA_CENTER,
            spaceAfter=10,
        )
        
        header_elements = [
            Paragraph('فاتورة ضريبية', title_style),
            Paragraph('Tax Invoice', styles['Normal']),
            Spacer(1, 5*mm),
        ]
        
        # معلومات البائع
        seller_info = f"""
        <b>البائع / Seller:</b><br/>
        {self.seller_name}<br/>
        الرقم الضريبي / VAT Number: {self.seller_vat_number}
        """
        if self.seller_address:
            seller_info += f"<br/>{self.seller_address}"
        
        header_elements.append(Paragraph(seller_info, styles['Normal']))
        
        return header_elements
    
    def _create_invoice_info(self, invoice: Invoice):
        """إنشاء معلومات الفاتورة"""
        styles = getSampleStyleSheet()
        
        invoice_info = f"""
        <b>رقم الفاتورة / Invoice Number:</b> {invoice.invoice_number}<br/>
        <b>تاريخ الفاتورة / Invoice Date:</b> {invoice.invoice_date.strftime('%Y-%m-%d')}
        """
        
        if invoice.uuid:
            invoice_info += f"<br/><b>UUID:</b> {invoice.uuid}"
        
        return [Paragraph(invoice_info, styles['Normal'])]
    
    def _create_customer_info(self, invoice: Invoice):
        """إنشاء معلومات العميل"""
        styles = getSampleStyleSheet()
        
        sales_order = invoice.sales_order
        
        customer_info = f"""
        <b>العميل / Customer:</b><br/>
        {sales_order.customer_name}
        """
        
        if sales_order.customer_phone:
            customer_info += f"<br/>الهاتف / Phone: {sales_order.customer_phone}"
        
        if sales_order.customer_address:
            customer_info += f"<br/>العنوان / Address: {sales_order.customer_address}"
        
        return [Paragraph(customer_info, styles['Normal'])]
    
    def _create_items_table(self, invoice: Invoice):
        """إنشاء جدول البنود"""
        sales_order = invoice.sales_order
        
        # رأس الجدول
        data = [
            ['#', 'الوصف / Description', 'الكمية / Quantity', 'السعر / Unit Price', 'الإجمالي / Total']
        ]
        
        # إضافة البنود
        for idx, line in enumerate(sales_order.lines.all(), 1):
            harvest = line.harvest
            description = f"حصاد دفعة {harvest.batch.batch_number}"
            quantity = f"{line.quantity_kg} كجم"
            unit_price = f"{line.unit_price:.2f} ريال"
            total = f"{line.line_total:.2f} ريال"
            
            data.append([str(idx), description, quantity, unit_price, total])
        
        # إنشاء الجدول
        table = Table(data, colWidths=[15*mm, 70*mm, 30*mm, 30*mm, 35*mm])
        
        # تطبيق الأنماط
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return [table]
    
    def _create_totals_table(self, invoice: Invoice):
        """إنشاء جدول الإجماليات"""
        data = [
            ['المجموع الفرعي / Subtotal:', f"{invoice.subtotal:.2f} ريال"],
            [f'ضريبة القيمة المضافة ({invoice.sales_order.vat_rate * 100:.1f}%) / VAT:', f"{invoice.vat_amount:.2f} ريال"],
            ['الإجمالي / Total:', f"{invoice.total_amount:.2f} ريال"],
        ]
        
        table = Table(data, colWidths=[100*mm, 80*mm])
        
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (-1, -1), (-1, -1), 12),
            ('TEXTCOLOR', (-1, -1), (-1, -1), HexColor('#1f2937')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return [table]
    
    def _create_qr_code(self, invoice: Invoice):
        """إنشاء QR Code"""
        try:
            # توليد QR Code image
            qr_code_data = invoice.qr_code
            if not qr_code_data:
                # محاولة توليد QR Code إذا لم يكن موجوداً
                qr_code_data = self.zatca.generate_qr_code(invoice)
                invoice.qr_code = qr_code_data
                invoice.save(update_fields=['qr_code'])
            
            # توليد صورة QR Code
            qr_image = self.zatca.generate_qr_code_image(qr_code_data)
            
            # حفظ الصورة مؤقتاً
            img_buffer = BytesIO(qr_image)
            img_buffer.seek(0)
            
            # إنشاء Image object
            img = Image(img_buffer, width=50*mm, height=50*mm)
            
            styles = getSampleStyleSheet()
            
            return [
                Paragraph('<b>QR Code:</b>', styles['Normal']),
                Spacer(1, 2*mm),
                img,
            ]
        except Exception as e:
            # في حالة الخطأ، إرجاع نص فقط
            styles = getSampleStyleSheet()
            return [Paragraph(f'<i>QR Code غير متوفر: {str(e)}</i>', styles['Normal'])]
    
    def _create_footer(self, invoice: Invoice):
        """إنشاء تذييل الفاتورة"""
        styles = getSampleStyleSheet()
        
        footer_text = """
        <i>شكراً لتعاملك معنا / Thank you for your business</i><br/>
        <br/>
        ملاحظات / Notes:<br/>
        هذه فاتورة ضريبية معتمدة / This is a certified tax invoice
        """
        
        if invoice.sales_order.notes:
            footer_text += f"<br/>{invoice.sales_order.notes}"
        
        return [Paragraph(footer_text, styles['Normal'])]

