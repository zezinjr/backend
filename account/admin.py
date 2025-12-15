from django.contrib import admin

from account import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'name',
        'is_superuser',
        'is_staff',
        'is_active',
    )


@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'description',
        'icon',
        'is_active',
    )
    ordering = ('description',)


@admin.register(models.Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'description',
        'icon',
        'route',
    )


@admin.register(models.ModuleMenu)
class ModuleMenuAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'module',
        'menu',
        'root',
        'order',
        'has_divider',
        'is_active',
    )
    ordering = ('-order',)
