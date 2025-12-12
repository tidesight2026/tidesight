"""
Migration لإضافة Indexes لتحسين الأداء
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        # Indexes على Invoice
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['invoice_date', 'status'], name='sales_invoi_invoice_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['invoice_number'], name='sales_invoi_invoice_n_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['sales_order', 'status'], name='sales_invoi_sales_o_idx'),
        ),
        
        # Indexes على SalesOrder
        migrations.AddIndex(
            model_name='salesorder',
            index=models.Index(fields=['order_date', 'status'], name='sales_saleso_order_d_idx'),
        ),
        migrations.AddIndex(
            model_name='salesorder',
            index=models.Index(fields=['order_number'], name='sales_saleso_order_n_idx'),
        ),
        
        # Indexes على Harvest
        migrations.AddIndex(
            model_name='harvest',
            index=models.Index(fields=['batch', 'harvest_date'], name='sales_harves_batch_h_idx'),
        ),
        migrations.AddIndex(
            model_name='harvest',
            index=models.Index(fields=['harvest_date', 'status'], name='sales_harves_harvest_idx'),
        ),
        
        # Indexes على SalesOrderLine
        migrations.AddIndex(
            model_name='salesorderline',
            index=models.Index(fields=['sales_order', 'harvest'], name='sales_saleso_sales_o_idx'),
        ),
        migrations.AddIndex(
            model_name='salesorderline',
            index=models.Index(fields=['harvest'], name='sales_saleso_harvest_idx'),
        ),
    ]

