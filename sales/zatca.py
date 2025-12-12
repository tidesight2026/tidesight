"""
ZATCA Integration - Phase 2
توليد QR Code و XML للفواتير الضريبية السعودية
"""
import base64
import qrcode
import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

from sales.models import Invoice, SalesOrder


class ZATCAIntegration:
    """
    كلاس للتعامل مع ZATCA Phase 2
    """
    
    def __init__(self, seller_name: str, seller_vat_number: str, seller_address: str = ""):
        self.seller_name = seller_name
        self.seller_vat_number = seller_vat_number
        self.seller_address = seller_address
    
    def generate_qr_code(self, invoice: Invoice) -> str:
        """
        توليد QR Code بتنسيق TLV (Tag-Length-Value) Base64
        
        Tags المطلوبة:
        - Tag 1: Seller Name
        - Tag 2: VAT Registration Number
        - Tag 3: Invoice Date
        - Tag 4: Invoice Total (including VAT)
        - Tag 5: VAT Total
        """
        try:
            # الحصول على بيانات الفاتورة
            sales_order = invoice.sales_order
            
            # تحويل التاريخ إلى timestamp
            invoice_date = datetime.combine(invoice.invoice_date, datetime.min.time())
            invoice_timestamp = int(invoice_date.timestamp())
            
            # تحويل المبالغ إلى String (بدون فاصلة عشرية)
            total_amount = str(int(invoice.total_amount * 100))  # بالهللة
            vat_amount = str(int(invoice.vat_amount * 100))  # بالهللة
            
            # بناء TLV
            tlv_data = []
            
            # Tag 1: Seller Name
            seller_name_bytes = self.seller_name.encode('utf-8')
            tlv_data.append(b'\x01' + bytes([len(seller_name_bytes)]) + seller_name_bytes)
            
            # Tag 2: VAT Registration Number
            vat_number_bytes = self.seller_vat_number.encode('utf-8')
            tlv_data.append(b'\x02' + bytes([len(vat_number_bytes)]) + vat_number_bytes)
            
            # Tag 3: Invoice Date (Unix timestamp)
            timestamp_str = str(invoice_timestamp)
            timestamp_bytes = timestamp_str.encode('utf-8')
            tlv_data.append(b'\x03' + bytes([len(timestamp_bytes)]) + timestamp_bytes)
            
            # Tag 4: Invoice Total
            total_bytes = total_amount.encode('utf-8')
            tlv_data.append(b'\x04' + bytes([len(total_bytes)]) + total_bytes)
            
            # Tag 5: VAT Total
            vat_bytes = vat_amount.encode('utf-8')
            tlv_data.append(b'\x05' + bytes([len(vat_bytes)]) + vat_bytes)
            
            # دمج TLV
            tlv_bytes = b''.join(tlv_data)
            
            # تحويل إلى Base64
            qr_base64 = base64.b64encode(tlv_bytes).decode('utf-8')
            
            return qr_base64
            
        except Exception as e:
            raise Exception(f"خطأ في توليد QR Code: {str(e)}")
    
    def generate_qr_code_image(self, qr_base64: str) -> bytes:
        """
        توليد صورة QR Code من Base64 TLV
        """
        try:
            # فك Base64
            tlv_bytes = base64.b64decode(qr_base64)
            
            # إنشاء QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_base64)
            qr.make(fit=True)
            
            # إنشاء الصورة
            img = qr.make_image(fill_color="black", back_color="white")
            
            # تحويل إلى bytes
            from io import BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"خطأ في توليد صورة QR Code: {str(e)}")
    
    def generate_ubl_xml(self, invoice: Invoice) -> str:
        """
        توليد ملف XML بتنسيق UBL 2.1 للفاتورة الضريبية
        
        UBL 2.1 Invoice Structure
        """
        try:
            sales_order = invoice.sales_order
            
            # إنشاء XML Root
            ns = {
                '': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            }
            
            root = ET.Element('Invoice', nsmap=ns)
            
            # Invoice ID
            invoice_id = ET.SubElement(root, 'cbc:ID')
            invoice_id.text = invoice.invoice_number
            
            # Issue Date
            issue_date = ET.SubElement(root, 'cbc:IssueDate')
            issue_date.text = invoice.invoice_date.isoformat()
            
            # Issue Time
            issue_time = ET.SubElement(root, 'cbc:IssueTime')
            issue_time.text = datetime.now().strftime('%H:%M:%S')
            
            # Invoice Type Code
            invoice_type = ET.SubElement(root, 'cbc:InvoiceTypeCode')
            invoice_type.set('listID', 'UN/ECE 1001')
            invoice_type.set('listAgencyID', '6')
            invoice_type.text = '388'  # Tax Invoice
            
            # Document Currency Code
            currency_code = ET.SubElement(root, 'cbc:DocumentCurrencyCode')
            currency_code.text = 'SAR'
            
            # Accounting Supplier Party
            supplier_party = ET.SubElement(root, 'cac:AccountingSupplierParty')
            supplier_party_legal = ET.SubElement(supplier_party, 'cac:Party')
            
            # Supplier Name
            supplier_name = ET.SubElement(supplier_party_legal, 'cac:PartyLegalEntity')
            supplier_name_cbc = ET.SubElement(supplier_name, 'cbc:RegistrationName')
            supplier_name_cbc.text = self.seller_name
            
            # Supplier VAT Number
            supplier_tax = ET.SubElement(supplier_party_legal, 'cac:PartyTaxScheme')
            supplier_tax_id = ET.SubElement(supplier_tax, 'cbc:CompanyID')
            supplier_tax_id.text = self.seller_vat_number
            
            # Accounting Customer Party
            customer_party = ET.SubElement(root, 'cac:AccountingCustomerParty')
            customer_party_legal = ET.SubElement(customer_party, 'cac:Party')
            customer_name = ET.SubElement(customer_party_legal, 'cac:PartyLegalEntity')
            customer_name_cbc = ET.SubElement(customer_name, 'cbc:RegistrationName')
            customer_name_cbc.text = sales_order.customer_name
            
            # Invoice Lines
            for idx, line in enumerate(sales_order.lines.all(), 1):
                invoice_line = ET.SubElement(root, 'cac:InvoiceLine')
                
                # Line ID
                line_id = ET.SubElement(invoice_line, 'cbc:ID')
                line_id.text = str(idx)
                
                # Invoiced Quantity
                quantity = ET.SubElement(invoice_line, 'cbc:InvoicedQuantity')
                quantity.set('unitCode', 'KGM')  # Kilogram
                quantity.text = str(line.quantity_kg)
                
                # Line Extension Amount
                line_amount = ET.SubElement(invoice_line, 'cbc:LineExtensionAmount')
                line_amount.set('currencyID', 'SAR')
                line_amount.text = str(line.line_total)
                
                # Item
                item = ET.SubElement(invoice_line, 'cac:Item')
                item_name = ET.SubElement(item, 'cbc:Name')
                item_name.text = f"سمك - حصاد {line.harvest.batch.batch_number}"
                
                # Price
                price = ET.SubElement(invoice_line, 'cac:Price')
                price_amount = ET.SubElement(price, 'cbc:PriceAmount')
                price_amount.set('currencyID', 'SAR')
                price_amount.text = str(line.unit_price)
            
            # Tax Total
            tax_total = ET.SubElement(root, 'cac:TaxTotal')
            tax_amount = ET.SubElement(tax_total, 'cbc:TaxAmount')
            tax_amount.set('currencyID', 'SAR')
            tax_amount.text = str(invoice.vat_amount)
            
            # Tax Subtotal
            tax_subtotal = ET.SubElement(tax_total, 'cac:TaxSubtotal')
            taxable_amount = ET.SubElement(tax_subtotal, 'cbc:TaxableAmount')
            taxable_amount.set('currencyID', 'SAR')
            taxable_amount.text = str(invoice.subtotal)
            
            tax_amount_sub = ET.SubElement(tax_subtotal, 'cbc:TaxAmount')
            tax_amount_sub.set('currencyID', 'SAR')
            tax_amount_sub.text = str(invoice.vat_amount)
            
            tax_category = ET.SubElement(tax_subtotal, 'cac:TaxCategory')
            tax_scheme = ET.SubElement(tax_category, 'cac:TaxScheme')
            tax_id = ET.SubElement(tax_scheme, 'cbc:ID')
            tax_id.set('schemeID', 'VAT')
            tax_id.text = 'VAT'
            
            # Legal Monetary Total
            legal_monetary_total = ET.SubElement(root, 'cac:LegalMonetaryTotal')
            
            line_extension_amount = ET.SubElement(legal_monetary_total, 'cbc:LineExtensionAmount')
            line_extension_amount.set('currencyID', 'SAR')
            line_extension_amount.text = str(invoice.subtotal)
            
            tax_exclusive_amount = ET.SubElement(legal_monetary_total, 'cbc:TaxExclusiveAmount')
            tax_exclusive_amount.set('currencyID', 'SAR')
            tax_exclusive_amount.text = str(invoice.subtotal)
            
            tax_inclusive_amount = ET.SubElement(legal_monetary_total, 'cbc:TaxInclusiveAmount')
            tax_inclusive_amount.set('currencyID', 'SAR')
            tax_inclusive_amount.text = str(invoice.total_amount)
            
            payable_amount = ET.SubElement(legal_monetary_total, 'cbc:PayableAmount')
            payable_amount.set('currencyID', 'SAR')
            payable_amount.text = str(invoice.total_amount)
            
            # تحويل XML إلى String
            xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            
            # Format XML
            dom = minidom.parseString(xml_string)
            formatted_xml = dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
            
            return formatted_xml
            
        except Exception as e:
            raise Exception(f"خطأ في توليد XML: {str(e)}")
    
    def sign_xml(self, xml_string: str, private_key_path: str, certificate_path: str) -> str:
        """
        توقيع XML باستخدام ECDSA
        
        ملاحظة: هذه دالة أساسية - يجب تطويرها بشكل كامل للتوافق مع ZATCA
        """
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.backends import default_backend
            
            # قراءة المفتاح الخاص
            with open(private_key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # حساب Hash للـ XML
            xml_hash = hashlib.sha256(xml_string.encode('utf-8')).digest()
            
            # التوقيع
            signature = private_key.sign(
                xml_hash,
                ec.ECDSA(hashes.SHA256())
            )
            
            # تحويل التوقيع إلى Base64
            signature_base64 = base64.b64encode(signature).decode('utf-8')
            
            # TODO: إضافة التوقيع إلى XML في العنصر المطلوب
            # هذا يتطلب تحليل XML وإضافة عنصر Signature
            
            return signature_base64
            
        except Exception as e:
            raise Exception(f"خطأ في توقيع XML: {str(e)}")


def generate_invoice_qr_code(invoice: Invoice, seller_name: str, seller_vat_number: str) -> str:
    """
    دالة مساعدة لتوليد QR Code للفاتورة
    """
    zatca = ZATCAIntegration(seller_name, seller_vat_number)
    return zatca.generate_qr_code(invoice)


def generate_invoice_xml(invoice: Invoice, seller_name: str, seller_vat_number: str) -> str:
    """
    دالة مساعدة لتوليد XML للفاتورة
    """
    zatca = ZATCAIntegration(seller_name, seller_vat_number)
    return zatca.generate_ubl_xml(invoice)

