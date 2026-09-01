from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import ReportSitemap, StaticSitemap

sitemaps = {"static": StaticSitemap, "reports": ReportSitemap}

urlpatterns = [
    path("", views.home, name="home"),
    path("price/", views.price, name="price"),
    path("chart/", views.chart, name="chart"),
    path("reports/", views.reports, name="reports"),
    path("reports/<slug:slug>/", views.report_detail, name="report_detail"),
    path("predictions/", views.predictions, name="predictions"),
    path("about/", views.about, name="about"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("api/v1/market/latest", views.api_latest, name="api_latest"),
    path("api/v1/market/sources", views.api_sources, name="api_sources"),
    path("api/v1/market/summary", views.api_summary, name="api_summary"),
    path("api/v1/market/history", views.api_history, name="api_history"),
    path("api/v1/reports", views.api_reports, name="api_reports"),
    path("api/v1/reports/<slug:slug>", views.api_report_detail, name="api_report_detail"),
    path("api/v1/predictions", views.api_predictions, name="api_predictions"),
    path("api/v1/predictions/latest", views.api_latest_prediction, name="api_latest_prediction"),
    path("api/v1/health", views.api_health, name="api_health"),
]
