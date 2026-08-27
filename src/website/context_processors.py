from django.conf import settings


def site_context(request):
    return {"site_url": settings.SITE_URL, "bale_channel_url": settings.BALE_CHANNEL_URL, "site_name": "نقره تایم"}
