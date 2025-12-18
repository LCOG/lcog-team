from django.contrib import admin

from .models import PhishReport

@admin.register(PhishReport)
class PhishReportAdmin(admin.ModelAdmin):
    list_display = ('employee', 'timestamp', 'organic')
    # readonly_fields = ('employee', 'timestamp', 'message', 'organic')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__email')
    list_filter = ('organic', 'timestamp')
