"""
Admin interface للمحاسبة
"""
from django.contrib import admin
from .models import Account, JournalEntry, JournalEntryLine, BiologicalAssetRevaluation


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface للحسابات"""
    list_display = ['code', 'arabic_name', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['code', 'name', 'arabic_name']
    ordering = ['code']


class JournalEntryLineInline(admin.TabularInline):
    """Inline editor لبنود القيد"""
    model = JournalEntryLine
    extra = 2
    fields = ['account', 'type', 'amount', 'description']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin interface للقيود المحاسبية"""
    list_display = ['entry_number', 'entry_date', 'description', 'is_posted', 'created_at']
    list_filter = ['entry_date', 'is_posted', 'reference_type']
    search_fields = ['entry_number', 'description']
    date_hierarchy = 'entry_date'
    inlines = [JournalEntryLineInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BiologicalAssetRevaluation)
class BiologicalAssetRevaluationAdmin(admin.ModelAdmin):
    """Admin interface لإعادة تقييم الأصول البيولوجية"""
    list_display = [
        'id',
        'batch',
        'revaluation_date',
        'carrying_amount',
        'fair_value',
        'unrealized_gain_loss',
        'market_price_per_kg',
        'created_at',
    ]
    list_filter = ['revaluation_date', 'batch']
    search_fields = ['batch__batch_number']
    date_hierarchy = 'revaluation_date'
    readonly_fields = [
        'carrying_amount',
        'fair_value',
        'unrealized_gain_loss',
        'current_weight_kg',
        'current_count',
        'created_at',
    ]
