from django.contrib import admin
from .models import UploadFee, ClearFee

@admin.register(UploadFee)
class UploadFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester_option', 'amount', 'fine', 'due_date', 'is_fully_paid')
    list_filter = ('batch', 'semester', 'section', 'semester_option')
    search_fields = ('student__name',)

@admin.register(ClearFee)
class ClearFeeAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'upload_fee', 'cleared_amount', 'payment_method', 'cleared_date')
    list_filter = ('payment_method', 'collector_name')
    search_fields = ('receipt_number', 'upload_fee__student__name')