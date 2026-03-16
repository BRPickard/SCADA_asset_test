"""Workbook inspection utility."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def inspect_workbook(path: Path) -> dict:
    xls = pd.ExcelFile(path)
    details = {"sheets": []}
    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, nrows=5)
        details["sheets"].append({"sheet": sheet, "columns": [str(c) for c in df.columns], "sample_rows": len(df)})
    return details
