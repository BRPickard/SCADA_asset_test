"""Streamlit app for SCADA asset enrichment and maintenance planning MVP."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import select

from src.config import OUTPUT_DIR, UPLOAD_DIR
from src.database import SessionLocal, init_db
from src.models.tables import AssetInstance, MaintenanceSchedule, ProductMaster, ReviewQueue
from src.ui.workflow import export_outputs, process_inventory_workbook, run_enrichment_and_schedule

st.set_page_config(page_title="SCADA Asset Enrichment MVP", layout="wide")
init_db()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Pages",
    [
        "Upload Inventory",
        "Review Canonical Assets",
        "Product Master",
        "Upload Datasheets / Manuals",
        "Review Queue",
        "Maintenance Calendar / Due Work",
        "Export Outputs",
    ],
)


def _load_df(model):
    with SessionLocal() as session:
        return pd.read_sql(select(model), session.bind)


assets_df = _load_df(AssetInstance)
products_df = _load_df(ProductMaster)
review_df = _load_df(ReviewQueue)
schedule_df = _load_df(MaintenanceSchedule)

st.sidebar.markdown("### KPI Snapshot")
st.sidebar.metric("Total Assets", len(assets_df))
st.sidebar.metric("Unique Products", len(products_df))
st.sidebar.metric("Unresolved Products", int(products_df["review_required"].sum()) if not products_df.empty else 0)
st.sidebar.metric("Overdue Items", int((schedule_df["status"] == "overdue").sum()) if not schedule_df.empty else 0)

if page == "Upload Inventory":
    st.header("Upload Inventory")
    wb = st.file_uploader("Upload .xlsx workbook", type=["xlsx"])
    if wb is not None:
        target = UPLOAD_DIR / wb.name
        target.write_bytes(wb.getvalue())
        canonical, products = process_inventory_workbook(target)
        st.success(f"Processed {len(canonical)} rows across workbook sheets.")
        st.write("Canonical preview", canonical.head())
        st.write("Product master preview", products.head())

elif page == "Review Canonical Assets":
    st.header("Review Canonical Assets")
    if assets_df.empty:
        st.info("No assets loaded yet.")
    else:
        site = st.selectbox("Site", ["All"] + sorted([x for x in assets_df["site_name_normalized"].dropna().unique().tolist()]))
        ctype = st.selectbox("Component Type", ["All"] + sorted([x for x in assets_df["component_type_normalized"].dropna().unique().tolist()]))
        mfr = st.selectbox("Manufacturer", ["All"] + sorted([x for x in assets_df["manufacturer_normalized"].dropna().unique().tolist()]))
        filtered = assets_df.copy()
        if site != "All":
            filtered = filtered[filtered["site_name_normalized"] == site]
        if ctype != "All":
            filtered = filtered[filtered["component_type_normalized"] == ctype]
        if mfr != "All":
            filtered = filtered[filtered["manufacturer_normalized"] == mfr]
        st.dataframe(filtered)

elif page == "Product Master":
    st.header("Product Master")
    if products_df.empty:
        st.info("No products yet.")
    else:
        show_review = st.checkbox("Show review-required only")
        p = products_df[products_df["review_required"] == True] if show_review else products_df
        st.dataframe(p)

elif page == "Upload Datasheets / Manuals":
    st.header("Upload Datasheets / Manuals")
    files = st.file_uploader("Upload PDFs / manuals / text", accept_multiple_files=True)
    if files:
        for f in files:
            (UPLOAD_DIR / f.name).write_bytes(f.getvalue())
        st.success(f"Stored {len(files)} files to {UPLOAD_DIR}.")
    if st.button("Run Enrichment + Schedule"):
        run_enrichment_and_schedule()
        st.success("Enrichment and scheduling completed.")

elif page == "Review Queue":
    st.header("Review Queue")
    st.dataframe(review_df)

elif page == "Maintenance Calendar / Due Work":
    st.header("Maintenance Calendar / Due Work")
    if schedule_df.empty:
        st.info("No maintenance items yet. Run enrichment/schedule first.")
    else:
        st.dataframe(schedule_df)
        monthly = schedule_df.copy()
        monthly["due_date"] = pd.to_datetime(monthly["due_date"])
        monthly["month"] = monthly["due_date"].dt.to_period("M").astype(str)
        st.write(monthly.groupby(["month", "priority", "status"], as_index=False).size())

elif page == "Export Outputs":
    st.header("Export Outputs")
    if st.button("Generate output files"):
        paths = export_outputs()
        st.success("Outputs generated")
        for name, path in paths.items():
            st.write(f"{name}: {Path(path).resolve()}")
    st.write(f"Output directory: {OUTPUT_DIR.resolve()}")
