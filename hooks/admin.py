# -*- coding: utf-8 -*-
"""
Register Hooks models for django admin.
"""

from django.contrib import admin

from hooks import models


class HookAdmin(admin.ModelAdmin):
    """
    Hook Admin Class
    """
    list_display = ['name', 'user', 'error_report_email', 'product_class']


class HookEventAdmin(admin.ModelAdmin):
    """
    HookEvent Admin Class
    """
    list_display = ['signal_type', 'hook', 'URL']


class HookLogAdmin(admin.ModelAdmin):
    """
    HookLog Admin Class
    """
    pass


class HookSignalTypeAdmin(admin.ModelAdmin):
    """
    HookSignalType Admin Class
    """
    list_display = ['id', 'name']


admin.site.register(models.Hook, HookAdmin)
admin.site.register(models.HookEvent, HookEventAdmin)
admin.site.register(models.HookLog, HookLogAdmin)
admin.site.register(models.HookSignalType, HookSignalTypeAdmin)
