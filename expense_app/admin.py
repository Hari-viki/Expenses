from django.contrib import admin
from .models import CustomUser, ExpensesList, Bank


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')


@admin.register(ExpensesList)
class ExpensesListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'amount', 'balance_amount', 'extra_amount', 'bank', 'description', 'date')
    list_filter = ('date',)
    search_fields = ('description',)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)