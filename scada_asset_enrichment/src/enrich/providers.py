"""Provider-based enrichment architecture for MVP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd


@dataclass
class EnrichmentRecord:
    field_name: str
    value: str
    source_provider: str
    source_reference: str
    confidence: float
    extraction_notes: str


class EnrichmentProvider(Protocol):
    name: str

    def enrich(self, product_row: pd.Series, asset_rows: pd.DataFrame) -> list[EnrichmentRecord]:
        """Return candidate enrichments for a product."""


class ExistingNotesProvider:
    name = "existing_notes_provider"

    def enrich(self, product_row: pd.Series, asset_rows: pd.DataFrame) -> list[EnrichmentRecord]:
        notes = " ".join(asset_rows["SCADA Notes"].fillna("").astype(str).tolist() + asset_rows["Other Notes"].fillna("").astype(str).tolist()).lower()
        tags = []
        if "battery" in notes:
            tags.append("battery")
        if "firmware" in notes:
            tags.append("firmware")
        if "critical" in notes:
            tags.append("critical")
        if not tags:
            return []
        return [
            EnrichmentRecord(
                field_name="category_tags",
                value=",".join(sorted(set(tags))),
                source_provider=self.name,
                source_reference="SCADA Notes + Other Notes",
                confidence=0.65,
                extraction_notes="Keyword extraction from inventory notes.",
            )
        ]


class ManualUploadProvider:
    name = "manual_upload_provider"

    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir

    def enrich(self, product_row: pd.Series, asset_rows: pd.DataFrame) -> list[EnrichmentRecord]:
        refs = [p.name for p in self.upload_dir.glob("**/*") if p.is_file()]
        if not refs:
            return []
        return [
            EnrichmentRecord(
                field_name="evidence_summary",
                value=f"{len(refs)} manual/datasheet files available for lookup",
                source_provider=self.name,
                source_reference=";".join(refs[:10]),
                confidence=0.5,
                extraction_notes="Manual files uploaded; text parsing not yet enabled for binary PDFs.",
            )
        ]


class MockVendorProvider:
    name = "mock_vendor_provider"

    def enrich(self, product_row: pd.Series, asset_rows: pd.DataFrame) -> list[EnrichmentRecord]:
        component = (product_row.get("component_type_normalized") or "").lower()
        interval = 180
        if "ups" in component:
            interval = 90
        elif "server" in component:
            interval = 90
        elif "flow" in component:
            interval = 365
        return [
            EnrichmentRecord("lifecycle_status", "Active (MOCK)", self.name, "mock-rule-v1", 0.4, "Deterministic placeholder."),
            EnrichmentRecord("support_status", "Supported (MOCK)", self.name, "mock-rule-v1", 0.4, "Deterministic placeholder."),
            EnrichmentRecord("service_interval_days", str(interval), self.name, "mock-rule-v1", 0.5, "Interval seeded by component type."),
            EnrichmentRecord("maintenance_basis", "time-based (MOCK)", self.name, "mock-rule-v1", 0.4, "Deterministic placeholder."),
            EnrichmentRecord("enrichment_confidence", "0.45", self.name, "mock-rule-v1", 0.45, "Aggregate mock confidence."),
        ]
