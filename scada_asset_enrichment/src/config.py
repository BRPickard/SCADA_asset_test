"""Application configuration and defaults for SCADA asset enrichment MVP."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
DB_PATH = DATA_DIR / "scada_assets.db"

DEFAULT_SERVICE_RULES = {
    "plc": {"service_interval_days": 180, "maintenance_basis": "time-based"},
    "ups": {"service_interval_days": 90, "maintenance_basis": "inspection+replacement"},
    "radio": {"service_interval_days": 180, "maintenance_basis": "performance-check"},
    "router": {"service_interval_days": 180, "maintenance_basis": "firmware+health"},
    "network switch": {"service_interval_days": 180, "maintenance_basis": "firmware+inspection"},
    "server": {"service_interval_days": 90, "maintenance_basis": "patching+hardware-check"},
    "flow monitor": {"service_interval_days": 365, "maintenance_basis": "calibration"},
    "pressure recorder": {"service_interval_days": 180, "maintenance_basis": "calibration"},
    "chart recorder": {"service_interval_days": 180, "maintenance_basis": "inspection+calibration"},
    "dac module": {"service_interval_days": 365, "maintenance_basis": "functional-test"},
}

UNKNOWN_TOKENS = {"", "unknown", "n/a", "na", "none", "null", "-", "--"}

for directory in (DATA_DIR, UPLOAD_DIR, OUTPUT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
