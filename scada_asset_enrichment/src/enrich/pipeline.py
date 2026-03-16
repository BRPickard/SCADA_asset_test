"""Run enrichment providers and persist product/evidence/review artifacts."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import delete, select

from src.config import UPLOAD_DIR
from src.database import SessionLocal
from src.enrich.providers import ExistingNotesProvider, ManualUploadProvider, MockVendorProvider
from src.models.tables import AssetInstance, EnrichmentEvidence, ProductMaster, ReviewQueue


def run_enrichment() -> None:
    providers = [ManualUploadProvider(UPLOAD_DIR), ExistingNotesProvider(), MockVendorProvider()]

    with SessionLocal() as session:
        assets_df = pd.read_sql(select(AssetInstance), session.bind)
        products_df = pd.read_sql(select(ProductMaster), session.bind)
        session.execute(delete(EnrichmentEvidence))
        session.execute(delete(ReviewQueue))

        for _, product in products_df.iterrows():
            key = product["product_key"]
            subset = assets_df[assets_df["product_key"] == key]
            updates: dict[str, object] = {}
            confidences: list[float] = []
            evidence_rows = []

            for provider in providers:
                recs = provider.enrich(product, subset)
                for rec in recs:
                    evidence_rows.append(
                        EnrichmentEvidence(
                            product_key=key,
                            field_name=rec.field_name,
                            field_value=rec.value,
                            source_provider=rec.source_provider,
                            source_reference=rec.source_reference,
                            confidence=rec.confidence,
                            extraction_notes=rec.extraction_notes,
                        )
                    )
                    updates.setdefault(rec.field_name, rec.value)
                    confidences.append(rec.confidence)

            if evidence_rows:
                session.add_all(evidence_rows)

            pm = session.scalar(select(ProductMaster).where(ProductMaster.product_key == key))
            if pm:
                for field, value in updates.items():
                    if hasattr(pm, field):
                        if field in {"service_interval_days"}:
                            value = int(value)
                        if field in {"enrichment_confidence"}:
                            value = float(value)
                        setattr(pm, field, value)
                pm.last_verified_date = date.today()
                pm.source_count = len(evidence_rows)
                pm.enrichment_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
                pm.review_required = pm.model_normalized is None or pm.manufacturer_normalized is None
                if pm.review_required:
                    session.add(
                        ReviewQueue(
                            record_type="product_master",
                            record_ref=key,
                            issue_type="missing_core_identity",
                            issue_details="Manufacturer/model unresolved after enrichment",
                            severity="high",
                        )
                    )

        unresolved_assets = session.scalars(select(AssetInstance).where(AssetInstance.review_required.is_(True))).all()
        for asset in unresolved_assets:
            session.add(
                ReviewQueue(
                    record_type="asset_instances",
                    record_ref=str(asset.id),
                    issue_type="normalization_missing",
                    issue_details="Could not normalize one or more core fields",
                    severity="medium",
                )
            )

        session.commit()
