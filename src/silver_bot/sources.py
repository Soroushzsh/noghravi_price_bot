from dataclasses import dataclass
from decimal import Decimal
import http.cookiejar, json, time, urllib.request

URLS = {"digikala":"https://api.digikala.com/non-inventory/v1/prices/", "noghresea":"https://api.noghresea.ir/api/market/getSilverPrice", "tokeniko":"https://tokeniko.com/api/prices-with-change", "melligold":"https://melligold.com/api/v1/exchange/buy-sell-price/?symbol=XAG&format=json"}
ABANTETHER_URL = "https://api.abantether.com/api/v1/manager/otc/ticker?coin=USDT"
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
@dataclass
class Observation:
    source: str; raw: Decimal | None = None; price: Decimal | None = None; error: str = ""; raw_response: str = ""; latency_ms: int = 0; http_status: int | None = None; excluded: str = ""

def fetch(source, multiplier, field, timeout, retries):
    started = time.monotonic(); last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(URLS[source], headers={"User-Agent":"silver-price-bale-bot/1.0", "Accept":"application/json"})
            with OPENER.open(req, timeout=timeout) as response:
                body = response.read().decode(); data = json.loads(body); raw = _extract(source, data, field)
                value = Decimal(str(raw)); latency = int((time.monotonic() - started) * 1000)
                return Observation(source, value, value * multiplier, raw_response=body[:200000], latency_ms=latency, http_status=response.status)
        except Exception as exc:
            last = exc
            if attempt < retries: time.sleep(0.5 * (attempt + 1))
    return Observation(source, error=f"{type(last).__name__}: {last}", latency_ms=int((time.monotonic()-started)*1000))

def _extract(source, data, field):
    if source == "digikala": return data.get("data", data)["silver999"]["price"]
    if source == "noghresea": return data["price"]
    if source == "tokeniko": return next(x[field] for x in data["products"] if x["name"] == "Silver999")
    return data["data"][field]

def fetch_usdt(field, timeout, retries):
    last = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(ABANTETHER_URL, headers={"User-Agent":"silver-price-bale-bot/1.0", "Accept":"application/json"})
            with OPENER.open(request, timeout=timeout) as response:
                return Decimal(str(json.loads(response.read())["data"]["markets"]["USDTIRT"][field]))
        except Exception as exc:
            last = exc
            if attempt < retries: time.sleep(0.5 * (attempt + 1))
    return None
