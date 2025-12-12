# Generated manually for Phase 4 - IoT Preparation

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('biological', '0003_batch_current_weight_batch_is_active_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_type', models.CharField(choices=[('temperature', 'درجة الحرارة'), ('oxygen', 'الأكسجين المذاب'), ('ph', 'درجة الحموضة (pH)'), ('ammonia', 'الأمونيا'), ('nitrite', 'النتريت'), ('nitrate', 'النتريت'), ('turbidity', 'العكارة'), ('salinity', 'الملوحة'), ('other', 'أخرى')], max_length=20, verbose_name='نوع المستشعر')),
                ('reading_value', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='قيمة القراءة')),
                ('unit', models.CharField(default='', max_length=20, verbose_name='الوحدة')),
                ('reading_date', models.DateTimeField(verbose_name='تاريخ ووقت القراءة')),
                ('is_alert', models.BooleanField(default=False, verbose_name='تنبيه')),
                ('alert_message', models.TextField(blank=True, null=True, verbose_name='رسالة التنبيه')),
                ('sensor_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='معرف المستشعر')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('pond', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensor_readings', to='biological.pond', verbose_name='الحوض')),
            ],
            options={
                'verbose_name': 'قراءة مستشعر',
                'verbose_name_plural': 'قراءات المستشعرات',
                'ordering': ['-reading_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['pond', 'sensor_type', 'reading_date'], name='biological_s_pond_i_123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['reading_date'], name='biological_s_readin_idx'),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['sensor_type'], name='biological_s_sensor_idx'),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['is_alert'], name='biological_s_is_ale_idx'),
        ),
    ]
