import pandas as pd
import pytest

from report_tool.fetcher import fetch_data
from report_tool.pdf_builder import build_pdf
from report_tool.processor import summarize


def test_summarize_totals():
    df = pd.DataFrame({"category": ["a", "a", "b"], "amount": [10, 20, "x"]})
    s = summarize(df)
    assert s["records"] == 2          # invalid amount dropped
    assert s["total"] == 30
    assert s["top_category"] == "a"


def test_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("foo,bar\n1,2\n")
    with pytest.raises(ValueError):
        fetch_data(str(p))


def test_pdf_created(tmp_path):
    df = fetch_data("sample_data/sales.csv")
    out = build_pdf(summarize(df), str(tmp_path / "r.pdf"))
    assert (tmp_path / "r.pdf").stat().st_size > 1000
    assert out.endswith("r.pdf")
