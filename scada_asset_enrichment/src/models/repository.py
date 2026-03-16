"""Repository helpers for writing/reading dataframes to SQLite."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import delete

from src.database import SessionLocal
from src.models.tables import AssetInstance, ProductMaster, ReviewQueue


def replace_asset_instances(canonical_df: pd.DataFrame) -> None:
    with SessionLocal() as session:
        session.execute(delete(AssetInstance))
        records: list[dict[str, Any]] = []
        for row in canonical_df.to_dict(orient="records"):
            records.append(
                {
                    "source_sheet": row.get("source_sheet", ""),
                    "row_hash": row.get("row_hash"),
                    "raw_json": row.get("raw_json", "{}"),
                    "call_sign": row.get("Call Sign"),
                    "asset_number": row.get("#"),
                    "site_name_raw": row.get("site_name_raw"),
                    "site_name_normalized": row.get("site_name_normalized"),
                    "component_type_raw": row.get("component_type_raw"),
                    "component_type_normalized": row.get("component_type_normalized"),
                    "manufacturer_raw": row.get("manufacturer_raw"),
                    "manufacturer_normalized": row.get("manufacturer_normalized"),
                    "model_raw": row.get("model_raw"),
                    "model_normalized": row.get("model_normalized"),
                    "firmware_version": row.get("Firmware Version"),
                    "protocol": row.get("Protocol"),
                    "network_speed": row.get("Network Switch Speed"),
                    "scada_notes": row.get("SCADA Notes"),
                    "other_notes": row.get("Other Notes"),
                    "product_key": row.get("product_key"),
                    "install_date": row.get("install_date"),
                    "last_service_date": row.get("last_service_date"),
                    "review_required": bool(row.get("review_required", False)), 
                }
            )
        session.bulk_insert_mappings(AssetInstance, records)
        session.commit()


def replace_product_master(product_df: pd.DataFrame) -> None:
    with SessionLocal() as session:
        session.execute(delete(ProductMaster))
        records = product_df.to_dict(orient="records")
        session.bulk_insert_mappings(ProductMaster, records)
        session.commit()


def upsert_review_item(record_type: str, record_ref: str, issue_type: str, issue_details: str, severity: str = "medium") -> None:
    with SessionLocal() as session:
        rq = ReviewQueue(
            record_type=record_type,
            record_ref=record_ref,
            issue_type=issue_type,
            issue_details=issue_details,
            severity=severity,
        )
        session.add(rq)
        session.commit()
