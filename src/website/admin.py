from django.contrib import admin

from .models import Prediction, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "published_at", "updated_at")
    list_filter = ("category", "status")
    search_fields = ("title", "summary", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("محتوا", {"fields": ("title", "slug", "category", "summary", "content_markdown")} ),
        ("انتشار و سئو", {"fields": ("status", "published_at", "seo_title", "seo_description")} ),
        ("سیستمی", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    actions = ("publish_selected", "archive_selected")

    @admin.action(description="انتشار گزارش‌های انتخاب‌شده")
    def publish_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="published", published_at=timezone.now())

    @admin.action(description="بایگانی گزارش‌های انتخاب‌شده")
    def archive_selected(self, request, queryset):
        queryset.update(status="archived")


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("horizon", "direction", "confidence", "status", "published_at", "result")
    list_filter = ("direction", "source_type", "status", "result")
    search_fields = ("horizon", "summary", "model_name")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("پیش‌بینی", {"fields": ("horizon", "direction", "confidence", "target_low", "target_high", "summary", "reasoning_markdown")} ),
        ("منبع و ورودی‌ها", {"fields": ("source_type", "model_name", "underlying_inputs")} ),
        ("انتشار و نتیجه", {"fields": ("status", "published_at", "actual_end_price", "result")} ),
        ("سیستمی", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
    actions = ("publish_selected", "archive_selected")

    @admin.action(description="انتشار پیش‌بینی‌های انتخاب‌شده")
    def publish_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="published", published_at=timezone.now())

    @admin.action(description="بایگانی پیش‌بینی‌های انتخاب‌شده")
    def archive_selected(self, request, queryset):
        queryset.update(status="archived")
