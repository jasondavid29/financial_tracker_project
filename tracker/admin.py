from django.contrib import admin
from .models import Transaction
# Register your models here.


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'category', 'amount', 'created_at')  # Replace 'date' with 'created_at'
    list_filter = ('type', 'created_at')  # Replace 'date' with 'created_at'
    search_fields = ('category', 'amount')


admin.site.register(Transaction, TransactionAdmin)