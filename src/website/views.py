import math

import markdown
import nh3
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from .market import RANGES, history, latest_run, latest_sources, market_latest, summary
from .models import Prediction, Report


def clean_markdown(value):
    html = markdown.markdown(value or "", extensions=["extra", "sane_lists"])
    return nh3.clean(html)


def _report_json(report):
    return {"slug": report.slug, "title": report.title, "summary": report.summary, "content": clean_markdown(report.content_markdown), "category": report.category, "category_label": report.get_category_display(), "published_at": report.published_at.isoformat() if report.published_at else None, "updated_at": report.updated_at.isoformat(), "seo_title": report.seo_title or report.title, "seo_description": report.seo_description or report.summary}


def _prediction_json(prediction):
    return {"id": prediction.id, "horizon": prediction.horizon, "direction": prediction.direction, "direction_label": prediction.get_direction_display(), "confidence": float(prediction.confidence), "target_low": prediction.target_low, "target_high": prediction.target_high, "summary": prediction.summary, "reasoning": clean_markdown(prediction.reasoning_markdown), "underlying_inputs": prediction.underlying_inputs, "source_type": prediction.source_type, "model_name": prediction.model_name, "status": prediction.status, "published_at": prediction.published_at.isoformat() if prediction.published_at else None, "actual_end_price": prediction.actual_end_price, "result": prediction.result}


def _reading_minutes(text):
    return max(1, math.ceil(len((text or "").split()) / 200))


def home(request):
    latest = market_latest()
    reports = list(Report.objects.filter(status="published")[:4])
    prediction = Prediction.objects.filter(status__in=("published", "resolved")).first()
    return render(request, "website/home.html", {"market": latest["data"], "freshness": latest["freshness"], "market_summary": summary(), "sources": latest_sources(), "reports": reports, "prediction": prediction, "reading_minutes": _reading_minutes})


def price(request):
    latest = market_latest()
    return render(request, "website/price.html", {"market": latest["data"], "freshness": latest["freshness"], "market_summary": summary(), "sources": latest_sources()})


def chart(request):
    return render(request, "website/chart.html", {"market": latest_run(), "default_range": "7d"})


def reports(request):
    category = request.GET.get("category", "")
    queryset = Report.objects.filter(status="published")
    if category in dict(Report.CATEGORY_CHOICES):
        queryset = queryset.filter(category=category)
    return render(request, "website/reports.html", {"reports": queryset[:30], "active_category": category, "categories": Report.CATEGORY_CHOICES, "reading_minutes": _reading_minutes})


def report_detail(request, slug):
    report = get_object_or_404(Report, slug=slug, status="published")
    related = Report.objects.filter(status="published").exclude(pk=report.pk)[:3]
    return render(request, "website/report_detail.html", {"report": report, "report_html": clean_markdown(report.content_markdown), "related": related})


def predictions(request):
    records = Prediction.objects.filter(status__in=("published", "resolved"))[:30]
    return render(request, "website/predictions.html", {"predictions": records})


def about(request):
    return render(request, "website/about.html")


def robots(request):
    return HttpResponse(f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {request.build_absolute_uri('/sitemap.xml')}\n", content_type="text/plain")


@require_GET
def api_latest(request):
    return JsonResponse(market_latest())


@require_GET
def api_sources(request):
    return JsonResponse({"sources": latest_sources()})


@require_GET
def api_summary(request):
    return JsonResponse(summary())


@require_GET
def api_history(request):
    range_name = request.GET.get("range", "7d")
    if range_name not in RANGES:
        return JsonResponse({"error": "range must be one of 24h, 7d, 30d, 90d, 1y"}, status=400)
    return JsonResponse({"range": range_name, "points": history(range_name)})


@require_GET
def api_reports(request):
    category = request.GET.get("category", "")
    try:
        page = max(1, int(request.GET.get("page", "1")))
        limit = min(50, max(1, int(request.GET.get("limit", "12"))))
    except ValueError:
        return JsonResponse({"error": "page and limit must be integers"}, status=400)
    queryset = Report.objects.filter(status="published")
    if category:
        if category not in dict(Report.CATEGORY_CHOICES):
            return JsonResponse({"error": "unknown category"}, status=400)
        queryset = queryset.filter(category=category)
    total = queryset.count()
    records = queryset[(page - 1) * limit : page * limit]
    return JsonResponse({"page": page, "limit": limit, "total": total, "reports": [_report_json(report) for report in records]})


@require_GET
def api_report_detail(request, slug):
    return JsonResponse(_report_json(get_object_or_404(Report, slug=slug, status="published")))


@require_GET
def api_predictions(request):
    try:
        page = max(1, int(request.GET.get("page", "1")))
        limit = min(50, max(1, int(request.GET.get("limit", "12"))))
    except ValueError:
        return JsonResponse({"error": "page and limit must be integers"}, status=400)
    queryset = Prediction.objects.filter(status__in=("published", "resolved"))
    total = queryset.count()
    records = queryset[(page - 1) * limit : page * limit]
    return JsonResponse({"page": page, "limit": limit, "total": total, "predictions": [_prediction_json(prediction) for prediction in records]})


@require_GET
def api_latest_prediction(request):
    prediction = Prediction.objects.filter(status__in=("published", "resolved")).first()
    return JsonResponse({"prediction": _prediction_json(prediction) if prediction else None})


@require_GET
def api_health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        latest = market_latest()
        return JsonResponse({"status": latest["freshness"]["state"], "updated_at": latest["data"]["updated_at"] if latest["data"] else None})
    except Exception:
        return JsonResponse({"status": "database_unavailable"}, status=503)
