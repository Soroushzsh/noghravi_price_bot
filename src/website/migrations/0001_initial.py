from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("title", models.CharField(max_length=240)),
                ("summary", models.TextField()),
                ("content_markdown", models.TextField()),
                ("category", models.CharField(choices=[("iran_market", "بازار ایران"), ("global_xag", "اونس جهانی"), ("analysis", "تحلیل"), ("education", "آموزش"), ("daily_report", "گزارش روزانه")], max_length=32)),
                ("status", models.CharField(choices=[("draft", "پیش‌نویس"), ("published", "منتشرشده"), ("archived", "بایگانی")], default="draft", max_length=16)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("seo_title", models.CharField(blank=True, max_length=240)),
                ("seo_description", models.CharField(blank=True, max_length=320)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-published_at", "-id")},
        ),
        migrations.CreateModel(
            name="Prediction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("horizon", models.CharField(max_length=80)),
                ("direction", models.CharField(choices=[("up", "صعودی"), ("flat", "خنثی"), ("down", "نزولی")], max_length=16)),
                ("confidence", models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("target_low", models.PositiveBigIntegerField(blank=True, null=True)),
                ("target_high", models.PositiveBigIntegerField(blank=True, null=True)),
                ("summary", models.CharField(max_length=500)),
                ("reasoning_markdown", models.TextField(blank=True)),
                ("underlying_inputs", models.JSONField(blank=True, default=dict)),
                ("source_type", models.CharField(choices=[("manual", "دستی"), ("rule_based", "قاعده‌محور"), ("llm", "مدل زبانی"), ("ml_model", "مدل آماری")], default="manual", max_length=16)),
                ("model_name", models.CharField(blank=True, max_length=120)),
                ("status", models.CharField(choices=[("draft", "پیش‌نویس"), ("published", "منتشرشده"), ("resolved", "نتیجه‌دار"), ("archived", "بایگانی")], default="draft", max_length=16)),
                ("actual_end_price", models.PositiveBigIntegerField(blank=True, null=True)),
                ("result", models.CharField(choices=[("pending", "در انتظار"), ("correct", "درست"), ("partial", "نسبی"), ("incorrect", "نادرست")], default="pending", max_length=16)),
            ],
            options={"ordering": ("-published_at", "-id")},
        ),
        migrations.AddIndex(model_name="report", index=models.Index(fields=["status", "published_at"], name="website_rep_status_aee3a0_idx")),
        migrations.AddIndex(model_name="prediction", index=models.Index(fields=["status", "published_at"], name="website_pre_status_830305_idx")),
    ]
