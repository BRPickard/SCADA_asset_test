"""Workbook ingestion and flattening for SCADA inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.normalize.normalizers import (
    make_product_key,
    normalize_component_type,
    normalize_manufacturer,
    normalize_model,
    normalize_site_name,
)


REQUIRED_COLUMNS = [
    "Call Sign",
    "#",
    "Index",
    "Name",
    "Site Type",
    "Address",
    "Component Type",
    "Manufaturer",
    "Model",
    "Building Location",
    "Equipment Location",
    "Firmware Version",
    "PLC Memory Used",
    "Protocol",
    "Network Switch Speed",
    "SCADA Network Priority (1-4)",
    "SCADA Notes",
    "Other Notes",
    "GPS Coordinates",
]


def load_and_flatten_inventory(workbook_path: Path) -> pd.DataFrame:
    workbook_path = Path(workbook_path)
    xls = pd.ExcelFile(workbook_path)
    frames: list[pd.DataFrame] = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(workbook_path, sheet_name=sheet, dtype=str)
        df.columns = [str(c).strip() for c in df.columns]
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[REQUIRED_COLUMNS].copy()
        df["source_sheet"] = sheet
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.dropna(how="all")
    return merged


def build_canonical_assets(raw_df: pd.DataFrame) -> pd.DataFrame:
    canonical = raw_df.copy()
    canonical["manufacturer_raw"] = canonical["Manufaturer"]
    canonical["manufacturer_normalized"] = canonical["manufacturer_raw"].apply(normalize_manufacturer)
    canonical["model_raw"] = canonical["Model"]
    canonical["model_normalized"] = canonical["model_raw"].apply(normalize_model)
    canonical["component_type_raw"] = canonical["Component Type"]
    canonical["component_type_normalized"] = canonical["component_type_raw"].apply(normalize_component_type)
    canonical["site_name_raw"] = canonical["Name"]
    canonical["site_name_normalized"] = canonical["site_name_raw"].apply(normalize_site_name)
    canonical["product_key"] = canonical.apply(
        lambda row: make_product_key(
            row["manufacturer_normalized"],
            row["model_normalized"],
            row["component_type_normalized"],
        ),
        axis=1,
    )
    canonical["review_required"] = canonical[["manufacturer_normalized", "model_normalized", "component_type_normalized"]].isna().any(axis=1)
    canonical["row_hash"] = canonical.apply(lambda row: hash_row(row.to_dict()), axis=1)
    canonical["raw_json"] = canonical[REQUIRED_COLUMNS].apply(lambda row: json.dumps(row.to_dict(), default=str), axis=1)
    return canonical


def hash_row(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def build_product_master(canonical_df: pd.DataFrame) -> pd.DataFrame:
    grouped = canonical_df.dropna(subset=["product_key"]).groupby("product_key", as_index=False).agg(
        manufacturer_normalized=("manufacturer_normalized", "first"),
        model_normalized=("model_normalized", "first"),
        component_type_normalized=("component_type_normalized", "first"),
        source_count=("product_key", "count"),
    )
    grouped["review_required"] = False
    return grouped
