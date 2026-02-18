from django.contrib import admin

from .models import Screencap, Title


class ScreencapInline(admin.TabularInline):
    model = Screencap
    fields = ["image", "tags", "thumbnail_preview"]
    readonly_fields = ["thumbnail_preview"]


@admin.register(Screencap)
class ScreencapAdmin(admin.ModelAdmin):
    model = Screencap
    list_display = ["id", "title", "thumbnail_preview"]
    list_filter = ["title", "tags"]


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    inlines = [ScreencapInline]
    list_display = ["name", "type", "release_year"]
    list_filter = ["type"]
    search_fields = ["name"]
