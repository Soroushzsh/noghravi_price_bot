from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Report


class StaticSitemap(Sitemap):
    priority = 0.7

    def items(self):
        return ("home", "price", "chart", "reports", "predictions", "about")

    def location(self, item):
        return reverse(item)


class ReportSitemap(Sitemap):
    priority = 0.6

    def items(self):
        return Report.objects.filter(status="published")

    def lastmod(self, item):
        return item.updated_at

    def location(self, item):
        return reverse("report_detail", args=(item.slug,))
