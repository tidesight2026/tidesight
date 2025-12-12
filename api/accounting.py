"""
API Endpoints للمحاسبة
"""
from ninja import Router
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal
from django.db.models import Sum, Q

from .auth import TokenAuth, ErrorResponse
from .permissions import require_feature
from accounting.models import Account, JournalEntry, JournalEntryLine, AccountType, BiologicalAssetRevaluation

router = Router()


# ==================== Schemas ====================

class AccountSchema(BaseModel):
    """Schema للحساب"""
    id: int
    code: str
    name: str
    arabic_name: str
    account_type: str
    account_type_display: str
    balance: float
    is_active: bool

    class Config:
        from_attributes = True


class JournalEntryLineSchema(BaseModel):
    """Schema لبند القيد"""
    id: int
    account_id: int
    account_code: str
    account_name: str
    type: str
    type_display: str
    amount: float
    description: Optional[str]

    class Config:
        from_attributes = True


class JournalEntrySchema(BaseModel):
    """Schema للقيد المحاسبي"""
    id: int
    entry_number: str
    entry_date: str
    description: str
    reference_type: Optional[str]
    reference_id: Optional[int]
    is_posted: bool
    total_debit: float
    total_credit: float
    created_by_id: Optional[int]
    created_by_name: Optional[str]
    created_at: str
    lines: List[JournalEntryLineSchema]

    class Config:
        from_attributes = True


class CreateJournalEntrySchema(BaseModel):
    """Schema لإنشاء قيد محاسبي"""
    entry_date: str
    description: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    lines: List[dict]  # [{"account_id": 1, "type": "debit", "amount": 100.00, "description": "..."}]


class TrialBalanceItem(BaseModel):
    """Schema لـ Trial Balance"""
    account_id: int
    account_code: str
    account_name: str
    debit: float
    credit: float
    balance: float


class BalanceSheetItem(BaseModel):
    """Schema لـ Balance Sheet"""
    category: str
    items: List[dict]
    total: float


class BiologicalAssetRevaluationSchema(BaseModel):
    """Schema لإعادة تقييم الأصل البيولوجي"""
    id: int
    batch_id: int
    batch_number: str
    revaluation_date: str
    carrying_amount: float
    fair_value: float
    market_price_per_kg: float
    current_weight_kg: float
    current_count: int
    unrealized_gain_loss: float
    journal_entry_id: Optional[int]
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# ==================== Account Endpoints ====================

@router.get('/accounts', response={200: List[AccountSchema]}, auth=TokenAuth())
@require_feature('accounting')
def list_accounts(request, account_type: Optional[str] = None):
    """
    قائمة الحسابات
    
    **Parameters:**
    - account_type: تصفية حسب نوع الحساب (asset, liability, etc.)
    """
    queryset = Account.objects.filter(is_active=True)
    
    if account_type:
        queryset = queryset.filter(account_type=account_type)
    
    accounts = queryset.order_by('code')
    
    return [
        AccountSchema(
            id=acc.id,
            code=acc.code,
            name=acc.name,
            arabic_name=acc.arabic_name,
            account_type=acc.account_type,
            account_type_display=acc.get_account_type_display(),
            balance=float(acc.balance),
            is_active=acc.is_active,
        )
        for acc in accounts
    ]


@router.get('/accounts/{account_id}', response={200: AccountSchema, 404: ErrorResponse}, auth=TokenAuth())
@require_feature('accounting')
def get_account(request, account_id: int):
    """الحصول على حساب محدد"""
    try:
        account = Account.objects.get(id=account_id)
        return AccountSchema(
            id=account.id,
            code=account.code,
            name=account.name,
            arabic_name=account.arabic_name,
            account_type=account.account_type,
            account_type_display=account.get_account_type_display(),
            balance=float(account.balance),
            is_active=account.is_active,
        )
    except Account.DoesNotExist:
        return 404, ErrorResponse(detail="الحساب غير موجود")


@router.post('/accounts', response={200: AccountSchema, 400: ErrorResponse}, auth=TokenAuth())
@require_feature('accounting')
def create_account(request, account_data: dict):
    """إنشاء حساب جديد"""
    try:
        account = Account.objects.create(**account_data)
        return AccountSchema(
            id=account.id,
            code=account.code,
            name=account.name,
            arabic_name=account.arabic_name,
            account_type=account.account_type,
            account_type_display=account.get_account_type_display(),
            balance=float(account.balance),
            is_active=account.is_active,
        )
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))


# ==================== Journal Entry Endpoints ====================

@router.get('/journal-entries', response={200: List[JournalEntrySchema]}, auth=TokenAuth())
@require_feature('accounting')
def list_journal_entries(request, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    قائمة القيود المحاسبية
    
    **Parameters:**
    - start_date: تاريخ البداية (YYYY-MM-DD)
    - end_date: تاريخ النهاية (YYYY-MM-DD)
    """
    queryset = JournalEntry.objects.select_related('created_by').prefetch_related('lines__account').all()
    
    if start_date:
        queryset = queryset.filter(entry_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(entry_date__lte=end_date)
    
    entries = queryset.order_by('-entry_date', '-created_at')
    
    result = []
    for entry in entries:
        total_debit = sum(line.amount for line in entry.lines.filter(type='debit'))
        total_credit = sum(line.amount for line in entry.lines.filter(type='credit'))
        
        result.append(JournalEntrySchema(
            id=entry.id,
            entry_number=entry.entry_number,
            entry_date=str(entry.entry_date),
            description=entry.description,
            reference_type=entry.reference_type,
            reference_id=entry.reference_id,
            is_posted=entry.is_posted,
            total_debit=float(total_debit),
            total_credit=float(total_credit),
            created_by_id=entry.created_by.id if entry.created_by else None,
            created_by_name=entry.created_by.full_name if entry.created_by else None,
            created_at=entry.created_at.isoformat(),
            lines=[
                JournalEntryLineSchema(
                    id=line.id,
                    account_id=line.account.id,
                    account_code=line.account.code,
                    account_name=line.account.arabic_name,
                    type=line.type,
                    type_display=line.get_type_display(),
                    amount=float(line.amount),
                    description=line.description,
                )
                for line in entry.lines.all()
            ],
        ))
    
    return result


@router.get('/journal-entries/{entry_id}', response={200: JournalEntrySchema, 404: ErrorResponse}, auth=TokenAuth())
@require_feature('accounting')
def get_journal_entry(request, entry_id: int):
    """الحصول على قيد محاسبي محدد"""
    try:
        entry = JournalEntry.objects.select_related('created_by').prefetch_related('lines__account').get(id=entry_id)
        
        total_debit = sum(line.amount for line in entry.lines.filter(type='debit'))
        total_credit = sum(line.amount for line in entry.lines.filter(type='credit'))
        
        return JournalEntrySchema(
            id=entry.id,
            entry_number=entry.entry_number,
            entry_date=str(entry.entry_date),
            description=entry.description,
            reference_type=entry.reference_type,
            reference_id=entry.reference_id,
            is_posted=entry.is_posted,
            total_debit=float(total_debit),
            total_credit=float(total_credit),
            created_by_id=entry.created_by.id if entry.created_by else None,
            created_by_name=entry.created_by.full_name if entry.created_by else None,
            created_at=entry.created_at.isoformat(),
            lines=[
                JournalEntryLineSchema(
                    id=line.id,
                    account_id=line.account.id,
                    account_code=line.account.code,
                    account_name=line.account.arabic_name,
                    type=line.type,
                    type_display=line.get_type_display(),
                    amount=float(line.amount),
                    description=line.description,
                )
                for line in entry.lines.all()
            ],
        )
    except JournalEntry.DoesNotExist:
        return 404, ErrorResponse(detail="القيد المحاسبي غير موجود")


@router.post('/journal-entries', response={200: JournalEntrySchema, 400: ErrorResponse}, auth=TokenAuth())
@require_feature('accounting')
def create_journal_entry(request, entry_data: CreateJournalEntrySchema):
    """
    إنشاء قيد محاسبي جديد
    
    **Note:** يجب أن يكون مجموع المدين = مجموع الدائن
    """
    from django.db import transaction
    
    try:
        with transaction.atomic():
            # توليد رقم القيد
            from datetime import datetime
            entry_number = f"JE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # إنشاء القيد
            entry = JournalEntry.objects.create(
                entry_number=entry_number,
                entry_date=entry_data.entry_date,
                description=entry_data.description,
                reference_type=entry_data.reference_type,
                reference_id=entry_data.reference_id,
                is_posted=False,
                created_by=request.auth,
            )
            
            # إنشاء بنود القيد
            total_debit = Decimal('0.00')
            total_credit = Decimal('0.00')
            
            for line_data in entry_data.lines:
                account = Account.objects.get(id=line_data['account_id'])
                amount = Decimal(str(line_data['amount']))
                
                if line_data['type'] == 'debit':
                    total_debit += amount
                else:
                    total_credit += amount
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    type=line_data['type'],
                    amount=amount,
                    description=line_data.get('description'),
                )
            
            # التحقق من التوازن
            if total_debit != total_credit:
                raise ValueError(f"القيد غير متوازن! المدين: {total_debit}, الدائن: {total_credit}")
            
            # ترحيل القيد
            entry.is_posted = True
            entry.save()
            
            # إرجاع النتيجة
            total_debit = sum(line.amount for line in entry.lines.filter(type='debit'))
            total_credit = sum(line.amount for line in entry.lines.filter(type='credit'))
            
            return JournalEntrySchema(
                id=entry.id,
                entry_number=entry.entry_number,
                entry_date=str(entry.entry_date),
                description=entry.description,
                reference_type=entry.reference_type,
                reference_id=entry.reference_id,
                is_posted=entry.is_posted,
                total_debit=float(total_debit),
                total_credit=float(total_credit),
                created_by_id=entry.created_by.id if entry.created_by else None,
                created_by_name=entry.created_by.full_name if entry.created_by else None,
                created_at=entry.created_at.isoformat(),
                lines=[
                    JournalEntryLineSchema(
                        id=line.id,
                        account_id=line.account.id,
                        account_code=line.account.code,
                        account_name=line.account.arabic_name,
                        type=line.type,
                        type_display=line.get_type_display(),
                        amount=float(line.amount),
                        description=line.description,
                    )
                    for line in entry.lines.all()
                ],
            )
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))


# ==================== Reports Endpoints ====================

@router.get('/trial-balance', response={200: List[TrialBalanceItem]}, auth=TokenAuth())
@require_feature('accounting')
def get_trial_balance(request, as_of_date: Optional[str] = None):
    """
    ميزانية تجريبية (Trial Balance)
    
    **Parameters:**
    - as_of_date: التاريخ المحدد (YYYY-MM-DD). افتراضي: اليوم
    """
    if as_of_date:
        as_of_date_obj = date.fromisoformat(as_of_date)
    else:
        as_of_date_obj = date.today()
    
    accounts = Account.objects.filter(is_active=True).order_by('code')
    
    result = []
    for account in accounts:
        # حساب المدين والدائن حتى التاريخ المحدد
        debit_lines = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__entry_date__lte=as_of_date_obj,
            journal_entry__is_posted=True,
            type='debit'
        )
        credit_lines = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__entry_date__lte=as_of_date_obj,
            journal_entry__is_posted=True,
            type='credit'
        )
        
        total_debit = debit_lines.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_credit = credit_lines.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # حساب الرصيد حسب نوع الحساب
        if account.account_type in ['asset', 'expense', 'biological_asset']:
            balance = total_debit - total_credit
        else:
            balance = total_credit - total_debit
        
        # إضافة فقط الحسابات التي لديها رصيد
        if total_debit > 0 or total_credit > 0:
            result.append(TrialBalanceItem(
                account_id=account.id,
                account_code=account.code,
                account_name=account.arabic_name,
                debit=float(total_debit),
                credit=float(total_credit),
                balance=float(balance),
            ))
    
    return result


@router.get('/balance-sheet', response={200: BalanceSheetItem}, auth=TokenAuth())
@require_feature('accounting')
def get_balance_sheet(request, as_of_date: Optional[str] = None):
    """
    الميزانية العمومية (Balance Sheet)
    
    **Parameters:**
    - as_of_date: التاريخ المحدد (YYYY-MM-DD). افتراضي: اليوم
    """
    if as_of_date:
        as_of_date_obj = date.fromisoformat(as_of_date)
    else:
        as_of_date_obj = date.today()
    
    # حساب الأصول
    assets = []
    total_assets = Decimal('0.00')
    for account in Account.objects.filter(account_type='asset', is_active=True):
        balance = account.balance
        if balance != 0:
            assets.append({'code': account.code, 'name': account.arabic_name, 'balance': float(balance)})
            total_assets += balance
    
    # حساب الخصوم
    liabilities = []
    total_liabilities = Decimal('0.00')
    for account in Account.objects.filter(account_type='liability', is_active=True):
        balance = account.balance
        if balance != 0:
            liabilities.append({'code': account.code, 'name': account.arabic_name, 'balance': float(balance)})
            total_liabilities += balance
    
    # حساب حقوق الملكية
    equity = []
    total_equity = Decimal('0.00')
    for account in Account.objects.filter(account_type='equity', is_active=True):
        balance = account.balance
        if balance != 0:
            equity.append({'code': account.code, 'name': account.arabic_name, 'balance': float(balance)})
            total_equity += balance
    
    return BalanceSheetItem(
        category='balance_sheet',
        items=[
            {'category': 'assets', 'items': assets, 'total': float(total_assets)},
            {'category': 'liabilities', 'items': liabilities, 'total': float(total_liabilities)},
            {'category': 'equity', 'items': equity, 'total': float(total_equity)},
        ],
        total=float(total_assets),
    )


# ==================== Biological Asset Revaluation Endpoints ====================

@router.get('/biological-asset-revaluations', response={200: List[BiologicalAssetRevaluationSchema]}, auth=TokenAuth())
@require_feature('accounting')
def list_biological_asset_revaluations(
    request,
    batch_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    قائمة إعادة تقييم الأصول البيولوجية
    
    **Parameters:**
    - batch_id: تصفية حسب دفعة محددة
    - start_date: تاريخ البداية (YYYY-MM-DD)
    - end_date: تاريخ النهاية (YYYY-MM-DD)
    """
    queryset = BiologicalAssetRevaluation.objects.select_related('batch', 'journal_entry').all()
    
    if batch_id:
        queryset = queryset.filter(batch_id=batch_id)
    if start_date:
        queryset = queryset.filter(revaluation_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(revaluation_date__lte=end_date)
    
    revaluations = queryset.order_by('-revaluation_date', '-created_at')
    
    return [
        BiologicalAssetRevaluationSchema(
            id=rev.id,
            batch_id=rev.batch.id,
            batch_number=rev.batch.batch_number,
            revaluation_date=str(rev.revaluation_date),
            carrying_amount=float(rev.carrying_amount),
            fair_value=float(rev.fair_value),
            market_price_per_kg=float(rev.market_price_per_kg),
            current_weight_kg=float(rev.current_weight_kg),
            current_count=rev.current_count,
            unrealized_gain_loss=float(rev.unrealized_gain_loss),
            journal_entry_id=rev.journal_entry.id if rev.journal_entry else None,
            notes=rev.notes,
            created_at=rev.created_at.isoformat(),
        )
        for rev in revaluations
    ]


@router.get('/biological-asset-revaluations/{revaluation_id}', response={200: BiologicalAssetRevaluationSchema, 404: ErrorResponse}, auth=TokenAuth())
@require_feature('accounting')
def get_biological_asset_revaluation(request, revaluation_id: int):
    """الحصول على إعادة تقييم محددة"""
    try:
        rev = BiologicalAssetRevaluation.objects.select_related('batch', 'journal_entry').get(id=revaluation_id)
        
        return BiologicalAssetRevaluationSchema(
            id=rev.id,
            batch_id=rev.batch.id,
            batch_number=rev.batch.batch_number,
            revaluation_date=str(rev.revaluation_date),
            carrying_amount=float(rev.carrying_amount),
            fair_value=float(rev.fair_value),
            market_price_per_kg=float(rev.market_price_per_kg),
            current_weight_kg=float(rev.current_weight_kg),
            current_count=rev.current_count,
            unrealized_gain_loss=float(rev.unrealized_gain_loss),
            journal_entry_id=rev.journal_entry.id if rev.journal_entry else None,
            notes=rev.notes,
            created_at=rev.created_at.isoformat(),
        )
    except BiologicalAssetRevaluation.DoesNotExist:
        return 404, ErrorResponse(detail="إعادة التقييم غير موجودة")
