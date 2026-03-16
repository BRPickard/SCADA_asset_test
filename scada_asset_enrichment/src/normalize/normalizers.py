"""Normalization utilities for inventory fields."""

from __future__ import annotations

import re
from typing import Any

from src.config import UNKNOWN_TOKENS

MANUFACTURER_MAP = {
    "allen bradley": "Allen-Bradley",
    "allen-bradley": "Allen-Bradley",
    "a-b": "Allen-Bradley",
    "ab": "Allen-Bradley",
    "opto 22": "OPTO 22",
    "opto-22": "OPTO 22",
    "cisco": "Cisco",
    "dell": "Dell",
    "n-tron": "N-Tron",
    "n tron": "N-Tron",
    "n-tron corp": "N-Tron",
    "microtik": "MikroTik",
    "mikrotik": "MikroTik",
}

COMPONENT_MAP = {
    "plc": "PLC",
    "radio": "Radio",
    "router": "Router",
    "switch": "Network Switch",
    "network switch": "Network Switch",
    "ups": "UPS",
    "server": "Server",
    "flow monitor": "Flow Monitor",
    "pressure recorder": "Pressure Recorder",
    "chart recorder": "Chart Recorder",
    "dac": "DAC Module",
    "dac module": "DAC Module",
}


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in UNKNOWN_TOKENS:
        return None
    return re.sub(r"\s+", " ", text)


def normalize_manufacturer(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    key = cleaned.lower().replace(".", "")
    key = re.sub(r"\s+", " ", key)
    return MANUFACTURER_MAP.get(key, cleaned.title() if cleaned.isupper() else cleaned)


def normalize_model(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    normalized = cleaned.upper().replace(" ", "")
    normalized = re.sub(r"[^A-Z0-9\-_/]", "", normalized)
    return normalized or None


def normalize_component_type(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    key = cleaned.lower()
    for pattern, label in COMPONENT_MAP.items():
        if pattern in key:
            return label
    return cleaned.title()


def normalize_site_name(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    cleaned = cleaned.replace("  ", " ")
    return cleaned.title()


def make_product_key(manufacturer: str | None, model: str | None, component_type: str | None) -> str | None:
    if not manufacturer or not model or not component_type:
        return None
    return f"{manufacturer}|{model}|{component_type}".lower()
