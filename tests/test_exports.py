import pandas as pd

from exports import EXPORT_FORMATS, export_test_suite, to_azure_devops_csv, to_jira_csv, to_testrail_csv


def sample_test_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Test ID": "TC-001",
                "Component/Feature": "Login",
                "Test Scenario": "Valid login with credentials",
                "Pre-conditions": "User registered",
                "Execution Steps": "Enter email and password",
                "Expected Result": "Dashboard loads",
                "Test Type (Positive/Negative)": "Positive",
                "Source Reference": "Section 1",
            }
        ]
    )


class TestToolExports:
    def test_jira_csv_contains_summary_and_description(self):
        csv_data = to_jira_csv(sample_test_df())
        assert "Summary" in csv_data
        assert "Valid login with credentials" in csv_data
        assert "Issue Type" in csv_data

    def test_testrail_csv_contains_title_and_steps(self):
        csv_data = to_testrail_csv(sample_test_df())
        assert "Title" in csv_data
        assert "Steps" in csv_data
        assert "Valid login" in csv_data

    def test_azure_devops_csv_contains_work_item_type(self):
        csv_data = to_azure_devops_csv(sample_test_df())
        assert "Work Item Type" in csv_data
        assert "Test Case" in csv_data

    def test_export_test_suite_dispatches_by_format(self):
        df = sample_test_df()
        for format_name in EXPORT_FORMATS:
            result = export_test_suite(df, format_name)
            assert result is not None
            assert len(result) > 0

    def test_export_returns_none_for_empty_dataframe(self):
        assert export_test_suite(pd.DataFrame(), "Jira CSV") is None
