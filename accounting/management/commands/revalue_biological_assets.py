"""
Management Command لإعادة تقييم الأصول البيولوجية حسب معيار IAS 41

الاستخدام:
    python manage.py revalue_biological_assets --date 2025-01-31 --market-price 25.00
    python manage.py revalue_biological_assets --all --market-price 25.00
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date
from accounting.models import (
    Account,
    JournalEntry,
    JournalEntryLine,
    BiologicalAssetRevaluation,
)
from biological.models import Batch
from daily_operations.utils import calculate_estimated_biomass
from accounts.models import User


class Command(BaseCommand):
    help = 'إعادة تقييم الأصول البيولوجية حسب معيار IAS 41'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='تاريخ إعادة التقييم (YYYY-MM-DD). افتراضي: اليوم',
        )
        parser.add_argument(
            '--market-price',
            type=float,
            required=True,
            help='سعر السوق الحالي للكيلوجرام (ريال)',
        )
        parser.add_argument(
            '--batch-id',
            type=int,
            help='معرف دفعة محددة (اختياري). إذا لم يتم تحديده، سيتم تقييم جميع الدفعات النشطة',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون حفظ (للعرض فقط)',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='معرف المستخدم الذي ينفذ العملية (اختياري)',
        )

    def handle(self, *args, **options):
        revaluation_date = options.get('date')
        if revaluation_date:
            try:
                revaluation_date = date.fromisoformat(revaluation_date)
            except ValueError:
                raise CommandError('تاريخ غير صحيح. استخدم الصيغة YYYY-MM-DD')
        else:
            revaluation_date = timezone.now().date()

        market_price = Decimal(str(options['market_price']))
        batch_id = options.get('batch_id')
        dry_run = options.get('dry_run', False)
        user_id = options.get('user_id')

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise CommandError(f'المستخدم برقم {user_id} غير موجود')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'إعادة تقييم الأصول البيولوجية (IAS 41)\n'
                f'{"="*60}\n'
                f'التاريخ: {revaluation_date}\n'
                f'سعر السوق: {market_price} ريال/كجم\n'
                f'{"="*60}\n'
            )
        )

        # جلب الدفعات
        if batch_id:
            try:
                batches = [Batch.objects.get(id=batch_id, status='active')]
            except Batch.DoesNotExist:
                raise CommandError(f'الدفعة برقم {batch_id} غير موجودة أو غير نشطة')
        else:
            batches = Batch.objects.filter(status='active')

        if not batches.exists():
            self.stdout.write(self.style.WARNING('لا توجد دفعات نشطة للتقييم'))
            return

        # حساب عدد القيود المحاسبية
        journal_entry_count = 0
        for batch in batches:
            journal_entry_count += 1

        total_unrealized_gain_loss = Decimal('0.00')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  تشغيل تجريبي - لن يتم حفظ البيانات\n'))

        try:
            with transaction.atomic():
                # جلب أو إنشاء حساب "أصول بيولوجية"
                biological_asset_account = Account.objects.filter(
                    account_type='biological_asset',
                    code__icontains='biological'
                ).first()

                if not biological_asset_account:
                    # محاولة إنشاء حساب إذا لم يكن موجوداً
                    biological_asset_account = Account.objects.filter(
                        code='1400'  # مثال
                    ).first()
                    if not biological_asset_account:
                        self.stdout.write(
                            self.style.ERROR(
                                '⚠️  لم يتم العثور على حساب الأصول البيولوجية. '
                                'يرجى إنشاء حساب برمز يحتوي على "biological" أو استخدام --create-account'
                            )
                        )
                        return

                # جلب أو إنشاء حساب "ربح/خسارة غير محققة"
                unrealized_gain_loss_account = Account.objects.filter(
                    code__icontains='unrealized'
                ).first()

                if not unrealized_gain_loss_account:
                    unrealized_gain_loss_account = Account.objects.filter(
                        code__icontains='3100'  # مثال - حقوق ملكية
                    ).first()
                    if not unrealized_gain_loss_account:
                        self.stdout.write(
                            self.style.ERROR(
                                '⚠️  لم يتم العثور على حساب الربح/الخسارة غير المحققة. '
                                'يرجى إنشاء حساب'
                            )
                        )
                        return

                revaluations_created = []

                for batch in batches:
                    # حساب القيمة الدفترية الحالية (من JournalEntries السابقة)
                    carrying_amount = self._calculate_carrying_amount(batch)

                    # حساب الوزن الحالي
                    current_weight = calculate_estimated_biomass(batch.id)
                    current_count = batch.current_count

                    # حساب القيمة العادلة
                    fair_value = Decimal(str(current_weight)) * market_price

                    # حساب الربح/الخسارة غير المحققة
                    unrealized_gain_loss = fair_value - carrying_amount
                    total_unrealized_gain_loss += unrealized_gain_loss

                    # عرض النتائج
                    self.stdout.write(
                        f'\nدفعة: {batch.batch_number}\n'
                        f'  - القيمة الدفترية: {carrying_amount:.2f} ريال\n'
                        f'  - الوزن الحالي: {current_weight:.2f} كجم\n'
                        f'  - العدد الحالي: {current_count}\n'
                        f'  - سعر السوق: {market_price:.2f} ريال/كجم\n'
                        f'  - القيمة العادلة: {fair_value:.2f} ريال\n'
                        f'  - ربح/خسارة غير محققة: {unrealized_gain_loss:.2f} ريال'
                    )

                    if not dry_run:
                        # إنشاء القيد المحاسبي
                        journal_entry = JournalEntry.objects.create(
                            entry_number=f'REV-{revaluation_date.strftime("%Y%m%d")}-{batch.id}',
                            entry_date=revaluation_date,
                            description=f'إعادة تقييم أصل بيولوجي - دفعة {batch.batch_number}',
                            reference_type='biological_revaluation',
                            reference_id=batch.id,
                            is_posted=True,
                            created_by=user,
                        )

                        # بند مدين: زيادة القيمة العادلة
                        if unrealized_gain_loss > 0:
                            JournalEntryLine.objects.create(
                                journal_entry=journal_entry,
                                account=biological_asset_account,
                                type='debit',
                                amount=unrealized_gain_loss,
                                description=f'زيادة قيمة الأصل البيولوجي - دفعة {batch.batch_number}',
                            )

                            JournalEntryLine.objects.create(
                                journal_entry=journal_entry,
                                account=unrealized_gain_loss_account,
                                type='credit',
                                amount=unrealized_gain_loss,
                                description=f'ربح غير محقق - دفعة {batch.batch_number}',
                            )
                        elif unrealized_gain_loss < 0:
                            # خسارة غير محققة
                            JournalEntryLine.objects.create(
                                journal_entry=journal_entry,
                                account=unrealized_gain_loss_account,
                                type='debit',
                                amount=abs(unrealized_gain_loss),
                                description=f'خسارة غير محققة - دفعة {batch.batch_number}',
                            )

                            JournalEntryLine.objects.create(
                                journal_entry=journal_entry,
                                account=biological_asset_account,
                                type='credit',
                                amount=abs(unrealized_gain_loss),
                                description=f'انخفاض قيمة الأصل البيولوجي - دفعة {batch.batch_number}',
                            )

                        # إنشاء سجل إعادة التقييم
                        revaluation, created = BiologicalAssetRevaluation.objects.get_or_create(
                            batch=batch,
                            revaluation_date=revaluation_date,
                            defaults={
                                'carrying_amount': carrying_amount,
                                'fair_value': fair_value,
                                'market_price_per_kg': market_price,
                                'current_weight_kg': Decimal(str(current_weight)),
                                'current_count': current_count,
                                'unrealized_gain_loss': unrealized_gain_loss,
                                'journal_entry': journal_entry,
                                'created_by': user,
                            }
                        )

                        if not created:
                            # تحديث السجل الموجود
                            revaluation.carrying_amount = carrying_amount
                            revaluation.fair_value = fair_value
                            revaluation.market_price_per_kg = market_price
                            revaluation.current_weight_kg = Decimal(str(current_weight))
                            revaluation.current_count = current_count
                            revaluation.unrealized_gain_loss = unrealized_gain_loss
                            revaluation.journal_entry = journal_entry
                            revaluation.save()

                        revaluations_created.append(revaluation)

                if dry_run:
                    # إلغاء Transaction في حالة dry-run
                    transaction.set_rollback(True)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ تمت محاكاة إعادة التقييم لـ {len(batches)} دفعة\n'
                            f'إجمالي الربح/الخسارة غير المحققة: {total_unrealized_gain_loss:.2f} ريال'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ تمت إعادة التقييم بنجاح!\n'
                            f'  - عدد الدفعات: {len(batches)}\n'
                            f'  - عدد القيود: {journal_entry_count}\n'
                            f'  - إجمالي الربح/الخسارة: {total_unrealized_gain_loss:.2f} ريال'
                        )
                    )

        except Exception as e:
            raise CommandError(f'حدث خطأ أثناء إعادة التقييم: {str(e)}')

    def _calculate_carrying_amount(self, batch):
        """حساب القيمة الدفترية الحالية للدفعة"""
        from django.db.models import Sum

        # جلب حساب الأصول البيولوجية للدفعة
        biological_accounts = Account.objects.filter(
            account_type='biological_asset'
        )

        if not biological_accounts.exists():
            # إذا لم يكن هناك حساب، نرجع التكلفة الأولية
            return batch.initial_cost or Decimal('0.00')

        # حساب الرصيد الحالي للحساب
        total_debit = JournalEntryLine.objects.filter(
            account__in=biological_accounts,
            journal_entry__reference_type__in=['batch', 'feeding_log', 'mortality_log'],
            journal_entry__reference_id=batch.id,
            type='debit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total_credit = JournalEntryLine.objects.filter(
            account__in=biological_accounts,
            journal_entry__reference_type__in=['batch', 'harvest'],
            journal_entry__reference_id=batch.id,
            type='credit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        carrying_amount = total_debit - total_credit

        # إذا كانت القيمة صفر أو سالبة، نرجع التكلفة الأولية
        if carrying_amount <= 0:
            carrying_amount = batch.initial_cost or Decimal('0.00')

        return carrying_amount

