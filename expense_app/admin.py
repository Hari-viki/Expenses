from django.contrib import admin
from django.utils.html import format_html
from .models import CustomUser, ExpensesList, Bank, BikeExpensesList, BikeTrip


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

@admin.register(BikeExpensesList)
class BikeExpensesAdmin(admin.ModelAdmin):

    list_display = ('user', 'date', 'petrol_amount', 'start_trip', 'end_trip', 'mileage', 'licence_view', 'rc_view', 'insurance_view')
    search_fields = ('user__username',)
    list_filter = ('date', 'user')
    ordering = ('-date',)
    readonly_fields = ('licence_preview', 'rc_preview', 'insurance_preview')

    # OPEN BUTTONS

    def licence_view(self, obj):
        if obj.licence_image:
            return format_html(
                '<a target="_blank" href="{}">Open</a>',
                obj.licence_image.url
            )
        return '-'

    def rc_view(self, obj):
        if obj.rc_image:
            return format_html(
                '<a target="_blank" href="{}">Open</a>',
                obj.rc_image.url
            )
        return '-'

    def insurance_view(self, obj):
        if obj.insurance_image:
            return format_html(
                '<a target="_blank" href="{}">Open</a>',
                obj.insurance_image.url
            )
        return '-'

    # IMAGE PREVIEW

    def licence_preview(self, obj):
        if obj.licence_image:
            return format_html(
                '<img src="{}" width="120"/>',
                obj.licence_image.url
            )
        return '-'

    def rc_preview(self, obj):
        if obj.rc_image:
            return format_html(
                '<img src="{}" width="120"/>',
                obj.rc_image.url
            )
        return '-'

    def insurance_preview(self, obj):
        if obj.insurance_image:
            return format_html(
                '<img src="{}" width="120"/>',
                obj.insurance_image.url
            )
        return '-'

@admin.register(BikeTrip)
class BikeTripAdmin(admin.ModelAdmin):

    list_display = ('user', 'date', 'petrol_amount', 'start_trip', 'end_trip', 'km_travelled_display', 'mileage', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('date', 'user', 'created_at')
    ordering = ('-date', '-created_at')
    list_per_page = 20
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
    fieldsets = (('Trip Details', {'fields': ('user', 'date', 'petrol_amount', 'start_trip', 'end_trip', 'mileage', 'created_at')}),)

    def km_travelled_display(self, obj):

        return obj.km_travelled

    km_travelled_display.short_description = "KM Travelled"
