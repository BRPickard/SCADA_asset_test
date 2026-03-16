"""High-level workflow functions used by Streamlit app."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.database import init_db
from src.enrich.pipeline import run_enrichment
from src.ingest.workbook_ingest import build_canonical_assets, build_product_master, load_and_flatten_inventory
from src.models.repository import replace_asset_instances, replace_product_master
from src.schedule.planner import generate_maintenance_schedule
from src.utils.exports import export_all_outputs


def process_inventory_workbook(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    init_db()
    raw = load_and_flatten_inventory(path)
    canonical = build_canonical_assets(raw)
    products = build_product_master(canonical)
    replace_asset_instances(canonical)
    replace_product_master(products)
    return canonical, products


def run_enrichment_and_schedule() -> None:
    run_enrichment()
    generate_maintenance_schedule()


def export_outputs():
    return export_all_outputs()
