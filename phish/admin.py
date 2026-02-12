from django.contrib import admin

from .models import PhishReport, SyntheticPhish, SyntheticPhishTemplate

@admin.register(PhishReport)
class PhishReportAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at', 'processed')
    readonly_fields = ('employee', 'created_at', 'message')
    search_fields = (
        'employee__first_name', 'employee__last_name', 'employee__email'
    )
    list_filter = ('created_at', 'processed')


@admin.register(SyntheticPhishTemplate)
class SyntheticPhishTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'subject', 'active')
    search_fields = ('name', 'subject')
    list_filter = ('active',)


@admin.register(SyntheticPhish)
class SyntheticPhishAdmin(admin.ModelAdmin):
    list_display = ('employee', 'template', 'sent_at', 'clicked', 'reported')
    readonly_fields = (
        'employee', 'template', 'sent_at', 'clicked', 'reported', 'reported_at'
    )
    search_fields = (
        'employee__first_name', 'employee__last_name', 'employee__email',
        'template__name'
    )
    list_filter = ('clicked', 'reported', 'sent_at')