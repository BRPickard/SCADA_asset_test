"""SQLAlchemy table definitions for MVP schema."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AssetInstance(Base):
    __tablename__ = "asset_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_sheet: Mapped[str] = mapped_column(String(255), nullable=False)
    row_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    raw_json: Mapped[str] = mapped_column(Text, nullable=False)

    call_sign: Mapped[str | None] = mapped_column(String(255))
    asset_number: Mapped[str | None] = mapped_column(String(64))
    site_name_raw: Mapped[str | None] = mapped_column(String(255))
    site_name_normalized: Mapped[str | None] = mapped_column(String(255))
    component_type_raw: Mapped[str | None] = mapped_column(String(255))
    component_type_normalized: Mapped[str | None] = mapped_column(String(255))
    manufacturer_raw: Mapped[str | None] = mapped_column(String(255))
    manufacturer_normalized: Mapped[str | None] = mapped_column(String(255))
    model_raw: Mapped[str | None] = mapped_column(String(255))
    model_normalized: Mapped[str | None] = mapped_column(String(255))
    firmware_version: Mapped[str | None] = mapped_column(String(255))
    protocol: Mapped[str | None] = mapped_column(String(255))
    network_speed: Mapped[str | None] = mapped_column(String(255))
    scada_notes: Mapped[str | None] = mapped_column(Text)
    other_notes: Mapped[str | None] = mapped_column(Text)

    product_key: Mapped[str | None] = mapped_column(String(512), index=True)
    install_date: Mapped[date | None] = mapped_column(Date)
    last_service_date: Mapped[date | None] = mapped_column(Date)
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProductMaster(Base):
    __tablename__ = "product_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    manufacturer_normalized: Mapped[str | None] = mapped_column(String(255))
    model_normalized: Mapped[str | None] = mapped_column(String(255))
    component_type_normalized: Mapped[str | None] = mapped_column(String(255))

    product_family: Mapped[str | None] = mapped_column(String(255))
    asset_class: Mapped[str | None] = mapped_column(String(255))
    category_tags: Mapped[str | None] = mapped_column(Text)

    lifecycle_status: Mapped[str | None] = mapped_column(String(255))
    support_status: Mapped[str | None] = mapped_column(String(255))
    discontinued_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    end_of_life_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    end_of_support_date: Mapped[date | None] = mapped_column(Date)
    legacy_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    replacement_family: Mapped[str | None] = mapped_column(String(255))
    replacement_notes: Mapped[str | None] = mapped_column(Text)

    service_interval_days: Mapped[int | None] = mapped_column(Integer)
    service_interval_months: Mapped[int | None] = mapped_column(Integer)
    maintenance_basis: Mapped[str | None] = mapped_column(String(255))
    maintenance_tasks: Mapped[str | None] = mapped_column(Text)
    inspection_frequency: Mapped[str | None] = mapped_column(String(255))
    calibration_frequency: Mapped[str | None] = mapped_column(String(255))
    consumables: Mapped[str | None] = mapped_column(Text)
    spare_parts: Mapped[str | None] = mapped_column(Text)
    technician_type: Mapped[str | None] = mapped_column(String(255))
    downtime_required: Mapped[bool] = mapped_column(Boolean, default=False)

    enrichment_confidence: Mapped[float | None] = mapped_column(Float)
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    last_verified_date: Mapped[date | None] = mapped_column(Date)
    evidence_summary: Mapped[str | None] = mapped_column(Text)


class EnrichmentEvidence(Base):
    __tablename__ = "enrichment_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_key: Mapped[str] = mapped_column(String(512), ForeignKey("product_master.product_key"), index=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_value: Mapped[str | None] = mapped_column(Text)
    source_provider: Mapped[str] = mapped_column(String(255), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    extraction_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_instance_id: Mapped[int] = mapped_column(Integer, ForeignKey("asset_instances.id"), index=True)
    product_key: Mapped[str | None] = mapped_column(String(512), index=True)
    due_date: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(32), default="normal")
    status: Mapped[str] = mapped_column(String(32), default="due")
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReviewQueue(Base):
    __tablename__ = "review_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_type: Mapped[str] = mapped_column(String(64), nullable=False)
    record_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    issue_type: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_details: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
