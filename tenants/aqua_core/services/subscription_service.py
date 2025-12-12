"""
خدمات إدارة الاشتراكات (Subscription Management Service)
توحيد منطق إدارة دورة حياة الاشتراك
"""
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Tuple
import logging

from tenants.models import Client, Subscription, Plan, PlatformInvoice

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    خدمة إدارة الاشتراكات
    توحيد منطق تغيير حالة الاشتراك بين Client, Subscription, PlatformInvoice
    """
    
    @staticmethod
    def activate_subscription(
        client: Client,
        plan: Plan,
        billing_cycle: str = 'monthly',
        payment_method: str = 'stripe',
        trial_days: int = 14,
        stripe_subscription_id: str = None,
        stripe_customer_id: str = None,
    ) -> Subscription:
        """
        تفعيل اشتراك جديد أو تجديد اشتراك موجود
        
        **Parameters:**
        - client: العميل (Tenant)
        - plan: الباقة المختارة
        - billing_cycle: دورة الفوترة ('monthly' أو 'yearly')
        - payment_method: طريقة الدفع
        - trial_days: عدد أيام التجربة (افتراضي: 14)
        - stripe_subscription_id: معرف الاشتراك في Stripe (اختياري)
        - stripe_customer_id: معرف العميل في Stripe (اختياري)
        
        **Returns:**
        - Subscription: الاشتراك المُنشأ أو المُحدّث
        """
        now = timezone.now()
        
        # حساب تواريخ الفترة
        if billing_cycle == 'yearly':
            period_days = 365
        else:
            period_days = 30
        
        trial_ends_at = now + timedelta(days=trial_days)
        current_period_start = now
        current_period_end = now + timedelta(days=period_days)
        
        # الحصول على الاشتراك الحالي أو إنشاء جديد
        subscription, created = Subscription.objects.get_or_create(
            client=client,
            defaults={
                'plan': plan,
                'status': 'trial',
                'trial_ends_at': trial_ends_at,
                'current_period_start': current_period_start,
                'current_period_end': current_period_end,
                'billing_cycle': billing_cycle,
                'payment_method': payment_method,
                'stripe_subscription_id': stripe_subscription_id or '',
                'stripe_customer_id': stripe_customer_id or '',
            }
        )
        
        if not created:
            # تحديث اشتراك موجود
            subscription.plan = plan
            subscription.status = 'active'
            subscription.trial_ends_at = trial_ends_at
            subscription.current_period_start = current_period_start
            subscription.current_period_end = current_period_end
            subscription.billing_cycle = billing_cycle
            subscription.payment_method = payment_method
            if stripe_subscription_id:
                subscription.stripe_subscription_id = stripe_subscription_id
            if stripe_customer_id:
                subscription.stripe_customer_id = stripe_customer_id
            subscription.save()
        
        # تحديث حالة العميل
        client.is_active_subscription = True
        client.subscription_type = plan.name
        client.subscription_start = now.date()
        client.subscription_end = current_period_end.date()
        client.save()
        
        logger.info(
            f"تم تفعيل/تجديد الاشتراك للعميل {client.name} "
            f"بالباقة {plan.name_ar} ({billing_cycle})"
        )
        
        return subscription
    
    @staticmethod
    def cancel_subscription(
        subscription: Subscription,
        reason: str = None,
        immediately: bool = False,
    ) -> Subscription:
        """
        إلغاء اشتراك
        
        **Parameters:**
        - subscription: الاشتراك المراد إلغاؤه
        - reason: سبب الإلغاء (اختياري)
        - immediately: إذا كان True، يتم الإلغاء فوراً. إذا كان False، يستمر حتى نهاية الفترة الحالية
        
        **Returns:**
        - Subscription: الاشتراك المُحدّث
        """
        now = timezone.now()
        
        subscription.auto_renew = False
        subscription.cancelled_at = now
        
        if immediately:
            subscription.status = 'cancelled'
            subscription.current_period_end = now
            
            # تحديث حالة العميل فوراً
            subscription.client.is_active_subscription = False
            subscription.client.save()
            
            logger.info(
                f"تم إلغاء الاشتراك فوراً للعميل {subscription.client.name}"
            )
        else:
            # الإلغاء في نهاية الفترة الحالية
            subscription.status = 'cancelled'
            logger.info(
                f"تم جدولة إلغاء الاشتراك للعميل {subscription.client.name} "
                f"في نهاية الفترة الحالية ({subscription.current_period_end})"
            )
        
        subscription.save()
        
        return subscription
    
    @staticmethod
    def mark_subscription_past_due(
        subscription: Subscription,
        reason: str = None,
    ) -> Subscription:
        """
        تعليم الاشتراك كمتأخر (Past Due)
        
        **Parameters:**
        - subscription: الاشتراك
        - reason: سبب التأخير (اختياري)
        
        **Returns:**
        - Subscription: الاشتراك المُحدّث
        """
        subscription.status = 'past_due'
        subscription.save()
        
        # تحديث حالة العميل
        subscription.client.is_active_subscription = False
        subscription.client.save()
        
        logger.warning(
            f"تم تعليم الاشتراك كمتأخر للعميل {subscription.client.name}"
            + (f" - السبب: {reason}" if reason else "")
        )
        
        return subscription
    
    @staticmethod
    def suspend_subscription(
        subscription: Subscription,
        reason: str = None,
    ) -> Subscription:
        """
        تعليق الاشتراك
        
        **Parameters:**
        - subscription: الاشتراك
        - reason: سبب التعليق (اختياري)
        
        **Returns:**
        - Subscription: الاشتراك المُحدّث
        """
        subscription.status = 'suspended'
        subscription.save()
        
        # تحديث حالة العميل
        subscription.client.is_active_subscription = False
        subscription.client.save()
        
        logger.warning(
            f"تم تعليق الاشتراك للعميل {subscription.client.name}"
            + (f" - السبب: {reason}" if reason else "")
        )
        
        return subscription
    
    @staticmethod
    def renew_subscription(
        subscription: Subscription,
        payment_amount: Decimal = None,
        payment_reference: str = None,
    ) -> tuple[Subscription, PlatformInvoice]:
        """
        تجديد اشتراك (عند استلام الدفع)
        
        **Parameters:**
        - subscription: الاشتراك
        - payment_amount: مبلغ الدفع (اختياري - يُؤخذ من الباقة إذا لم يُحدد)
        - payment_reference: مرجع الدفع (اختياري)
        
        **Returns:**
        - Tuple[Subscription, PlatformInvoice]: الاشتراك المُحدّث والفاتورة
        """
        now = timezone.now()
        
        # حساب مدة الفترة الجديدة
        if subscription.billing_cycle == 'yearly':
            period_days = 365
        else:
            period_days = 30
        
        # تحديث الاشتراك
        subscription.status = 'active'
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=period_days)
        subscription.last_payment_date = now
        if payment_amount:
            subscription.total_paid += payment_amount
        
        subscription.save()
        
        # تحديث حالة العميل
        subscription.client.is_active_subscription = True
        subscription.client.subscription_end = subscription.current_period_end.date()
        subscription.client.save()
        
        # إنشاء فاتورة
        invoice_amount = payment_amount or subscription.plan.price_monthly
        if subscription.billing_cycle == 'yearly':
            invoice_amount = subscription.plan.price_yearly
        
        invoice = PlatformInvoice.objects.create(
            subscription=subscription,
            invoice_number=SubscriptionService._generate_invoice_number(),
            invoice_date=now.date(),
            due_date=now.date() + timedelta(days=30),
            subtotal=invoice_amount,
            vat_amount=invoice_amount * Decimal('0.15'),  # 15% VAT
            total_amount=invoice_amount * Decimal('1.15'),
            status='paid',
            payment_method=subscription.payment_method,
            payment_date=now,
            payment_reference=payment_reference or '',
        )
        
        logger.info(
            f"تم تجديد الاشتراك للعميل {subscription.client.name} "
            f"حتى {subscription.current_period_end.date()}"
        )
        
        return (subscription, invoice)
    
    @staticmethod
    def _generate_invoice_number() -> str:
        """توليد رقم فاتورة فريد"""
        from datetime import datetime
        now = datetime.now()
        count = PlatformInvoice.objects.filter(
            invoice_date=now.date()
        ).count()
        return f"INV-{now.strftime('%Y%m%d')}-{count + 1:04d}"

