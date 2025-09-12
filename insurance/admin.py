from django.contrib import admin
from .models import Insurance



@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('insurance_id','insurance_company','payment_mode','amount', 'vehicle')


