"""Output export helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import select

from src.config import OUTPUT_DIR
from src.database import SessionLocal
from src.models.tables import AssetInstance, MaintenanceSchedule, ProductMaster, ReviewQueue
from src.schedule.planner import maintenance_calendar_monthly


def export_all_outputs(output_dir: Path | None = None) -> dict[str, Path]:
    out = output_dir or OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as session:
        assets = pd.read_sql(select(AssetInstance), session.bind)
        products = pd.read_sql(select(ProductMaster), session.bind)
        review = pd.read_sql(select(ReviewQueue), session.bind)
        schedule = pd.read_sql(select(MaintenanceSchedule), session.bind)

    enriched_csv = out / "enriched_inventory.csv"
    assets.to_csv(enriched_csv, index=False)
    enriched_xlsx = out / "enriched_inventory.xlsx"
    assets.to_excel(enriched_xlsx, index=False)

    product_csv = out / "product_master.csv"
    products.to_csv(product_csv, index=False)

    review_csv = out / "review_queue.csv"
    review.to_csv(review_csv, index=False)

    schedule_csv = out / "maintenance_schedule.csv"
    schedule.to_csv(schedule_csv, index=False)

    cal_csv = out / "maintenance_calendar_monthly.csv"
    maintenance_calendar_monthly().to_csv(cal_csv, index=False)

    return {
        "enriched_inventory.csv": enriched_csv,
        "enriched_inventory.xlsx": enriched_xlsx,
        "product_master.csv": product_csv,
        "review_queue.csv": review_csv,
        "maintenance_schedule.csv": schedule_csv,
        "maintenance_calendar_monthly.csv": cal_csv,
    }
