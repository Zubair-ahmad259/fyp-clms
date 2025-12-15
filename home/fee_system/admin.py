from django.contrib import admin
from .models import UploadFee, ClearFee



@admin.register(UploadFee)
class UploadFeeAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'batch', 'semester', 'section',
        'semester_option', 'amount', 'fine', 'total_fee', 'upload_date'
    )
    list_filter = ('batch', 'semester', 'section', 'semester_option')
    search_fields = ('student__first_name', 'student__last_name', 'student__student_id')
    ordering = ('batch', 'semester', 'section', 'student')
    readonly_fields = ('upload_date',)

    def total_fee(self, obj):
        return obj.amount + obj.fine
    total_fee.short_description = "Total Fee"


@admin.register(ClearFee)
class ClearFeeAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', 'upload_fee', 'cleared_amount',
        'payment_method', 'collector_name', 'cleared_date'
    )
    list_filter = ('payment_method', 'cleared_date')
    search_fields = (
        'receipt_number',
        'collector_name',
        'upload_fee__student__first_name',
        'upload_fee__student__last_name',
        'upload_fee__student__student_id',
    )
    ordering = ('-cleared_date',)
    readonly_fields = ('cleared_date',)
