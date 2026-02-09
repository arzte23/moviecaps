from django.contrib import admin

from .models import Screencap, Title


class ScreencapInline(admin.TabularInline):
    model = Screencap


class TitleAdmin(admin.ModelAdmin):
    inlines = [ScreencapInline]


admin.site.register(Title, TitleAdmin)
