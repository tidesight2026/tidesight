"""
Migration لإضافة Indexes لتحسين الأداء
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        # Indexes على JournalEntry
        migrations.AddIndex(
            model_name='journalentry',
            index=models.Index(fields=['entry_date', 'is_posted'], name='accounting_j_entry_d_7a8f1d_idx'),
        ),
        migrations.AddIndex(
            model_name='journalentry',
            index=models.Index(fields=['reference_type', 'reference_id'], name='accounting_j_referen_idx'),
        ),
        
        # Indexes على JournalEntryLine
        migrations.AddIndex(
            model_name='journalentryline',
            index=models.Index(fields=['account', 'type'], name='accounting_j_account_idx'),
        ),
        migrations.AddIndex(
            model_name='journalentryline',
            index=models.Index(fields=['journal_entry', 'type'], name='accounting_j_journal__idx'),
        ),
        
        # Indexes على Account
        migrations.AddIndex(
            model_name='account',
            index=models.Index(fields=['account_type', 'is_active'], name='accounting_a_account__idx'),
        ),
        
        # ملاحظة: BiologicalAssetRevaluation indexes تم إضافتها في migration لاحق بعد إنشاء النموذج
    ]

