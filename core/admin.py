from django.contrib import admin

from core import models


# Register your models here.
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age')
    search_fields = ('name', 'age')
    list_filter = ('name', 'age')
    list_display_links = ('id', 'name', 'age')
    list_per_page = 2

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(models.Client, ClienteAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'registration')

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

admin.site.register(models.Employee, EmployeeAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'quantity')

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

admin.site.register(models.Product, ProductAdmin)


class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'client', 'employee', 'nrf')

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

admin.site.register(models.Sale, SaleAdmin)