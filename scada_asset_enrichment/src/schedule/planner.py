"""Deterministic maintenance schedule generator."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from sqlalchemy import delete, select

from src.config import DEFAULT_SERVICE_RULES
from src.database import SessionLocal
from src.models.tables import AssetInstance, MaintenanceSchedule, ProductMaster, ReviewQueue


def _parse_date(value):
    if not value:
        return None
    try:
        return pd.to_datetime(value).date()
    except Exception:  # noqa: BLE001
        return None


def calculate_next_due(last_service_date, install_date, interval_days: int):
    last = _parse_date(last_service_date)
    install = _parse_date(install_date)
    base = last or install
    if base is None:
        return None
    return base + timedelta(days=int(interval_days))


def generate_maintenance_schedule() -> None:
    with SessionLocal() as session:
        assets = pd.read_sql(select(AssetInstance), session.bind)
        products = pd.read_sql(select(ProductMaster), session.bind)
        product_lookup = {row["product_key"]: row for _, row in products.iterrows()}

        session.execute(delete(MaintenanceSchedule))

        for _, asset in assets.iterrows():
            pk = asset.get("product_key")
            prod = product_lookup.get(pk, {})
            ctype = (asset.get("component_type_normalized") or "").lower()
            interval = prod.get("service_interval_days")
            if pd.isna(interval) or interval is None:
                interval = DEFAULT_SERVICE_RULES.get(ctype, {}).get("service_interval_days")

            if not interval:
                session.add(
                    ReviewQueue(
                        record_type="asset_instances",
                        record_ref=str(asset["id"]),
                        issue_type="missing_service_interval",
                        issue_details="No product or component fallback interval available",
                        severity="medium",
                    )
                )
                continue

            due = calculate_next_due(asset.get("last_service_date"), asset.get("install_date"), int(interval))
            if due is None:
                session.add(
                    ReviewQueue(
                        record_type="asset_instances",
                        record_ref=str(asset["id"]),
                        issue_type="missing_service_anchor_date",
                        issue_details="Need install_date or last_service_date to compute due date",
                        severity="medium",
                    )
                )
                continue

            priority = "normal"
            if bool(prod.get("legacy_flag")) or bool(prod.get("end_of_life_flag")):
                priority = "high"

            session.add(
                MaintenanceSchedule(
                    asset_instance_id=int(asset["id"]),
                    product_key=pk,
                    due_date=due,
                    priority=priority,
                    status="overdue" if due < date.today() else "due",
                    reason=f"Interval {interval} days from baseline date",
                )
            )

        session.commit()


def maintenance_calendar_monthly() -> pd.DataFrame:
    with SessionLocal() as session:
        sched = pd.read_sql(select(MaintenanceSchedule), session.bind)
    if sched.empty:
        return sched
    sched["due_date"] = pd.to_datetime(sched["due_date"])
    sched["month"] = sched["due_date"].dt.to_period("M").astype(str)
    return sched.groupby(["month", "priority", "status"], as_index=False).size().rename(columns={"size": "count"})
