"""
Migration لإضافة Indexes لتحسين الأداء
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daily_operations', '0001_initial'),
    ]

    operations = [
        # Indexes على FeedingLog
        migrations.AddIndex(
            model_name='feedinglog',
            index=models.Index(fields=['batch', 'feeding_date'], name='daily_operat_batch_f_idx'),
        ),
        migrations.AddIndex(
            model_name='feedinglog',
            index=models.Index(fields=['feeding_date'], name='daily_operat_feeding_idx'),
        ),
        migrations.AddIndex(
            model_name='feedinglog',
            index=models.Index(fields=['feed_type', 'batch'], name='daily_operat_feed_ty_idx'),
        ),
        
        # Indexes على MortalityLog
        migrations.AddIndex(
            model_name='mortalitylog',
            index=models.Index(fields=['batch', 'mortality_date'], name='daily_operat_batch_m_idx'),
        ),
        migrations.AddIndex(
            model_name='mortalitylog',
            index=models.Index(fields=['mortality_date'], name='daily_operat_mortalit_idx'),
        ),
    ]

