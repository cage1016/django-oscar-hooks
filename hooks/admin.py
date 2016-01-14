from django.contrib import admin

from hooks import models

class HookAdmin(admin.ModelAdmin):
  list_display = ['name']

class HookClassAdmin(admin.ModelAdmin):
  list_display = ('name', 'email')


admin.site.register(models.Hook, HookAdmin)
admin.site.register(models.HookClass, HookClassAdmin)
