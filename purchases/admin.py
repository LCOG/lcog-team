from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    Expense, ExpenseCard, ExpenseGL, ExpenseMonth, ExpenseMonthLock,
    ExpenseStatement, ExpenseStatementItem, PurchaseCategory, PurchaseObject,
    PurchaseRequest, Role
)


class ExpenseSubmitterFilter(admin.SimpleListFilter):
    title = 'Expense Submitter'
    parameter_name = 'expense_submitter'
    field_name = 'purchaser'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        # If we're in ExpenseAdmin, we need to filter through month__purchaser
        if model == Expense:
            self.field_name = 'month__purchaser'

    def lookups(self, request, model_admin):
        expense_submitters = Group.objects.get(name='Expense Submitter')\
            .user_set.all()
        return [
            (str(user.employee.id), user.employee.name) for user in
                expense_submitters if hasattr(user, 'employee')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{f'{self.field_name}_id': self.value()})
        return queryset


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ("members",)


@admin.register(PurchaseCategory)
class PurchaseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(PurchaseObject)
class PurchaseObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'request_for', 'purchase_object', 'name', 'quantity', 'status'
    )


class ExpenseGLInline(admin.TabularInline):
    model = ExpenseGL
    extra = 0


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    fields = ('id', 'name', 'date', 'vendor', 'amount')
    readonly_fields = ('id', 'name', 'date', 'vendor', 'amount')
    # No delete
    can_delete = False


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_purchaser', 'date', 'name', 'amount', 'status'
    )
    inlines = (ExpenseGLInline,)
    list_filter = ('status', 'month__year', 'month__month', ExpenseSubmitterFilter)

    @admin.display(ordering='month__purchaser', description='Purchaser')
    def get_purchaser(self, expense):
        return expense.month.purchaser


@admin.register(ExpenseMonth)
class ExpenseMonthAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'purchaser', 'year', 'month', 'card', 'status'
    )
    list_filter = ('status', 'year', 'month', ExpenseSubmitterFilter)
    inlines = (ExpenseInline,)
    

@admin.register(ExpenseCard)
class ExpenseCardAdmin(admin.ModelAdmin):
    list_display = (
        'last4', 'assignee', 'shared'
    )


class ExpenseStatementItemInline(admin.TabularInline):
    model = ExpenseStatementItem
    extra = 0


@admin.register(ExpenseStatement)
class ExpenseStatementAdmin(admin.ModelAdmin):
    list_display = ('id', 'card', 'month', 'year')
    list_filter = ('card', 'year', 'month')
    inlines = (ExpenseStatementItemInline,)


@admin.register(ExpenseMonthLock)
class ExpenseMonthLockAdmin(admin.ModelAdmin):
    list_display = ('pk', 'year', 'month', 'locked_by')
    list_filter = ('year',)