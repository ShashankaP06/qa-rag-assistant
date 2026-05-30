"""Export test suite DataFrames to QA tool import formats."""

from __future__ import annotations

import pandas as pd


def _find_column(df: pd.DataFrame, *candidates: str) -> str | None:
    lower_map = {col.strip().lower(): col for col in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def _series(df: pd.DataFrame, *candidates: str, default: str = "") -> pd.Series:
    col = _find_column(df, *candidates)
    if col is None:
        return pd.Series([default] * len(df))
    return df[col].fillna(default).astype(str)


def to_jira_csv(df: pd.DataFrame) -> str:
    """Jira Cloud CSV import — Summary + Description per test case."""
    export = pd.DataFrame(
        {
            "Summary": _series(df, "Test Scenario", "Test scenario"),
            "Issue Type": "Test",
            "Description": (
                "**Component:** "
                + _series(df, "Component/Feature", "Component")
                + "\n\n**Pre-conditions:** "
                + _series(df, "Pre-conditions", "Preconditions")
                + "\n\n**Steps:** "
                + _series(df, "Execution Steps", "Steps")
                + "\n\n**Expected:** "
                + _series(df, "Expected Result", "Expected")
                + "\n\n**Type:** "
                + _series(df, "Test Type (Positive/Negative)", "Test Type")
                + "\n\n**Source:** "
                + _series(df, "Source Reference", "Source")
            ),
            "Labels": _series(df, "Component/Feature", "Component"),
            "Test ID": _series(df, "Test ID", "ID"),
        }
    )
    return export.to_csv(index=False)


def to_testrail_csv(df: pd.DataFrame) -> str:
    """TestRail bulk import compatible CSV."""
    export = pd.DataFrame(
        {
            "Title": _series(df, "Test Scenario", "Test scenario"),
            "Section": _series(df, "Component/Feature", "Component"),
            "Preconditions": _series(df, "Pre-conditions", "Preconditions"),
            "Steps": _series(df, "Execution Steps", "Steps"),
            "Expected Result": _series(df, "Expected Result", "Expected"),
            "Type": _series(df, "Test Type (Positive/Negative)", "Test Type"),
            "References": _series(df, "Source Reference", "Source"),
            "Case ID": _series(df, "Test ID", "ID"),
        }
    )
    return export.to_csv(index=False)


def to_azure_devops_csv(df: pd.DataFrame) -> str:
    """Azure DevOps test case import CSV."""
    steps = _series(df, "Execution Steps", "Steps")
    expected = _series(df, "Expected Result", "Expected")
    export = pd.DataFrame(
        {
            "Work Item Type": "Test Case",
            "Title": _series(df, "Test Scenario", "Test scenario"),
            "Area Path": _series(df, "Component/Feature", "Component"),
            "Steps": steps + " || Expected: " + expected,
            "Priority": "2",
            "Tags": _series(df, "Test Type (Positive/Negative)", "Test Type"),
            "Reference": _series(df, "Source Reference", "Source"),
            "Test Case ID": _series(df, "Test ID", "ID"),
        }
    )
    return export.to_csv(index=False)


EXPORT_FORMATS = {
    "Jira CSV": to_jira_csv,
    "TestRail CSV": to_testrail_csv,
    "Azure DevOps CSV": to_azure_devops_csv,
}


def export_test_suite(df: pd.DataFrame, format_name: str) -> str | None:
    if df is None or df.empty:
        return None
    exporter = EXPORT_FORMATS.get(format_name)
    if exporter is None:
        return None
    return exporter(df)
