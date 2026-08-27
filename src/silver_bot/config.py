from dataclasses import dataclass
import os
from decimal import Decimal

def _bool(name, default):
    value = os.getenv(name, str(default)).lower()
    if value not in {"true", "false"}: raise ValueError(f"{name} must be true or false")
    return value == "true"

@dataclass(frozen=True)
class Config:
    poll_interval: int; send_enabled: bool; send_interval: int; send_threshold_percent: Decimal
    token: str; channel: str; alert_chat: str; enabled: dict
    weights: dict; multipliers: dict; fields: dict; min_sources: int
    min_price: Decimal; max_price: Decimal; max_deviation: Decimal
    connect_timeout: float; read_timeout: float; retries: int; database: str
    timezone: str; breakdown: bool; log_level: str

    @classmethod
    def from_env(cls):
        names = ("digikala", "noghresea", "tokeniko", "melligold")
        enabled = {n: _bool(f"{n.upper()}_ENABLED", True) for n in names}
        weights = {n: Decimal(os.getenv(f"WEIGHT_{n.upper()}", "1")) for n in names}
        multipliers = {"digikala": Decimal(os.getenv("DIGIKALA_MULTIPLIER", "100")), "noghresea": Decimal(os.getenv("NOGHRESEA_MULTIPLIER", "1000")), "tokeniko": Decimal(os.getenv("TOKENIKO_MULTIPLIER", "0.1")), "melligold": Decimal(os.getenv("MELLIGOLD_MULTIPLIER", "1"))}
        if not any(enabled.values()): raise ValueError("at least one source must be enabled")
        interval = int(os.getenv("POLL_INTERVAL_SECONDS", "600"))
        send_enabled = _bool("SEND_CHANNEL_MESSAGE_ENABLED", True)
        send_interval = int(os.getenv("SEND_CHANNEL_MESSAGE_INTERVAL", str(interval)))
        send_threshold = Decimal(os.getenv("SEND_CHANNEL_MESSAGE_CHANGE_THRESHOLD_PERCENT", "0.5"))
        min_sources = int(os.getenv("MIN_VALID_SOURCES", "3"))
        if interval <= 0: raise ValueError("POLL_INTERVAL_SECONDS must be positive")
        if send_interval <= 0: raise ValueError("SEND_CHANNEL_MESSAGE_INTERVAL must be positive")
        if send_threshold < 0: raise ValueError("SEND_CHANNEL_MESSAGE_CHANGE_THRESHOLD_PERCENT must be non-negative")
        if min_sources < 1 or min_sources > sum(enabled.values()): raise ValueError("MIN_VALID_SOURCES exceeds enabled sources")
        if any(v < 0 for v in weights.values()) or any(v <= 0 for v in multipliers.values()): raise ValueError("weights and multipliers must be non-negative/positive")
        token, channel = os.getenv("BALE_BOT_TOKEN", ""), os.getenv("BALE_CHANNEL_ID", "")
        if send_enabled and (not token or not channel): raise ValueError("BALE_BOT_TOKEN and BALE_CHANNEL_ID are required when channel messages are enabled")
        fields = {"tokeniko": os.getenv("TOKENIKO_PRICE_FIELD", "sellPrice"), "melligold": os.getenv("MELLIGOLD_PRICE_FIELD", "price_buy"), "abantether": os.getenv("ABANTETHER_PRICE_FIELD", "buy_price")}
        if fields["abantether"] not in {"buy_price", "sell_price"}: raise ValueError("ABANTETHER_PRICE_FIELD must be buy_price or sell_price")
        return cls(interval, send_enabled, send_interval, send_threshold, token, channel, os.getenv("BALE_ALERT_CHAT_ID", ""), enabled, weights, multipliers, fields, min_sources, Decimal(os.getenv("MIN_SILVER_PRICE_TOMAN", "100000")), Decimal(os.getenv("MAX_SILVER_PRICE_TOMAN", "2000000")), Decimal(os.getenv("MAX_SOURCE_DEVIATION_PCT", "15")), float(os.getenv("HTTP_CONNECT_TIMEOUT_SECONDS", "5")), float(os.getenv("HTTP_READ_TIMEOUT_SECONDS", "5")), int(os.getenv("HTTP_MAX_RETRIES", "2")), os.getenv("DATABASE_PATH", "/data/silver_price_bot.db"), os.getenv("DISPLAY_TIMEZONE", "Asia/Tehran"), _bool("INCLUDE_SOURCE_BREAKDOWN", True), os.getenv("LOG_LEVEL", "INFO"))
