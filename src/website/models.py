from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Report(models.Model):
    CATEGORY_CHOICES = (
        ("iran_market", "بازار ایران"),
        ("global_xag", "اونس جهانی"),
        ("analysis", "تحلیل"),
        ("education", "آموزش"),
        ("daily_report", "گزارش روزانه"),
    )
    STATUS_CHOICES = (("draft", "پیش‌نویس"), ("published", "منتشرشده"), ("archived", "بایگانی"))
    slug = models.SlugField(max_length=180, unique=True)
    title = models.CharField(max_length=240)
    summary = models.TextField()
    content_markdown = models.TextField()
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    seo_title = models.CharField(max_length=240, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-published_at", "-id")
        indexes = [models.Index(fields=("status", "published_at"))]

    def __str__(self):
        return self.title


class Prediction(models.Model):
    DIRECTION_CHOICES = (("up", "صعودی"), ("flat", "خنثی"), ("down", "نزولی"))
    SOURCE_CHOICES = (("manual", "دستی"), ("rule_based", "قاعده‌محور"), ("llm", "مدل زبانی"), ("ml_model", "مدل آماری"))
    STATUS_CHOICES = (("draft", "پیش‌نویس"), ("published", "منتشرشده"), ("resolved", "نتیجه‌دار"), ("archived", "بایگانی"))
    RESULT_CHOICES = (("pending", "در انتظار"), ("correct", "درست"), ("partial", "نسبی"), ("incorrect", "نادرست"))
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    horizon = models.CharField(max_length=80)
    direction = models.CharField(max_length=16, choices=DIRECTION_CHOICES)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    target_low = models.PositiveBigIntegerField(null=True, blank=True)
    target_high = models.PositiveBigIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=500)
    reasoning_markdown = models.TextField(blank=True)
    underlying_inputs = models.JSONField(default=dict, blank=True)
    source_type = models.CharField(max_length=16, choices=SOURCE_CHOICES, default="manual")
    model_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft")
    actual_end_price = models.PositiveBigIntegerField(null=True, blank=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES, default="pending")

    class Meta:
        ordering = ("-published_at", "-id")
        indexes = [models.Index(fields=("status", "published_at"))]

    def __str__(self):
        return f"{self.horizon} — {self.get_direction_display()}"
