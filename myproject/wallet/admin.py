from django.contrib import admin
from .models import Transaction, Category

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'creation', 'user', 'category')
    list_filter = ('creation', 'category')
    search_fields = ('description', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


