# SCADA Asset Enrichment MVP

Production-leaning Python MVP for ingesting SCADA/industrial asset inventories, normalizing messy spreadsheet data, enriching product-level metadata through provider interfaces, and generating deterministic maintenance schedules.

## What this MVP does

- Ingests multi-sheet `.xlsx` inventory workbooks and flattens to one canonical asset dataset.
- Preserves **all raw source columns** and adds normalized columns.
- Builds a `product_master` keyed by normalized manufacturer + model + component type.
- Runs provider-based enrichment pipeline:
  - `manual_upload_provider`
  - `existing_notes_provider`
  - `mock_vendor_provider` (explicitly mock/demo)
- Persists all core tables to SQLite.
- Produces deterministic maintenance schedule and monthly calendar summary.
- Exports:
  - `enriched_inventory.csv` and `enriched_inventory.xlsx`
  - `product_master.csv`
  - `review_queue.csv`
  - `maintenance_schedule.csv`
  - `maintenance_calendar_monthly.csv`
- Provides a minimal Streamlit UI for upload, review, enrichment/scheduling, and exports.

## Architecture (MVP)

- `src/ingest`: workbook ingestion and canonical flattening
- `src/normalize`: string/value normalizers
- `src/models`: SQLAlchemy table models + repository persistence
- `src/enrich`: provider interfaces + enrichment pipeline
- `src/schedule`: deterministic maintenance planning logic
- `src/ui`: workflow orchestration used by Streamlit app
- `src/utils`: export helpers

SQLite is used now; swap to Postgres later by changing SQLAlchemy engine config.

## Project structure

```text
scada_asset_enrichment/
  app.py
  requirements.txt
  README.md
  /data
  /uploads
  /outputs
  /src
    /ingest
    /normalize
    /models
    /enrich
    /schedule
    /ui
    /utils
    config.py
    database.py
  /tests
```

## Setup

```bash
cd scada_asset_enrichment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Streamlit app

```bash
streamlit run app.py
```

## How to use

1. Open **Upload Inventory** and upload the multi-sheet workbook.
2. Review normalized records in **Review Canonical Assets**.
3. Optionally upload datasheets/manuals in **Upload Datasheets / Manuals**.
4. Run **Enrichment + Schedule** from that page.
5. Inspect unresolved records in **Review Queue**.
6. Review due work in **Maintenance Calendar / Due Work**.
7. Generate output files from **Export Outputs**.

## Where to add real LLM/vendor enrichment later

Add a new provider in `src/enrich/providers.py` implementing:

```python
class EnrichmentProvider(Protocol):
    name: str
    def enrich(self, product_row: pd.Series, asset_rows: pd.DataFrame) -> list[EnrichmentRecord]:
        ...
```

Then register it in `run_enrichment()` (`src/enrich/pipeline.py`).

## Mock vs production-ready

### Production-leaning now
- Ingestion/flattening across all sheets
- normalization layer with raw-preserving design
- SQLite persistence with clear schema
- deterministic schedule computation logic
- Streamlit workflow + exports

### Mock/demo now
- `mock_vendor_provider` lifecycle/support outputs are placeholders and labeled `(MOCK)`
- manual upload provider currently registers evidence and file references; binary PDF extraction/parsing remains to be implemented
- date anchors (`install_date`, `last_service_date`) exist in schema but require user/system population for due-date computation

## Tests

```bash
pytest -q
```

Covers normalization and deterministic scheduling helper behavior.
