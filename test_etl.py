import pytest
import pandas as pd
from etl_script import extract, transform


# ── Extract Tests ─────────────────────────────────────────────────────────────
def test_extract_returns_dataframe(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text("name,age,salary\nAlice,30,50000\nBob,25,40000\n")
    df = extract(str(csv))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_extract_correct_columns(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text("name,age,salary\nAlice,30,50000\n")
    df = extract(str(csv))
    assert list(df.columns) == ["name", "age", "salary"]


# ── Transform Tests ───────────────────────────────────────────────────────────
def test_transform_removes_all_null_rows():
    df = pd.DataFrame({
        "name": ["Alice", None],
        "age": [30, None],
        "salary": [50000, None]
    })
    result = transform(df)
    assert len(result) == 1


def test_transform_fills_numeric_nulls_with_mean():
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [30, None, 40]
    })
    result = transform(df)
    assert result["age"].isnull().sum() == 0
    assert result["age"].iloc[1] == 35.0  # mean of 30 and 40


def test_transform_fills_string_nulls_with_unknown():
    df = pd.DataFrame({
        "name": ["Alice", None, "Charlie"],
        "city": ["NY", "LA", None]
    })
    result = transform(df)
    assert "Unknown" in result["name"].values
    assert "Unknown" in result["city"].values


def test_transform_strips_column_whitespace():
    df = pd.DataFrame({" name ": ["Alice"], " age ": [30]})
    result = transform(df)
    assert "name" in result.columns
    assert "age" in result.columns


def test_transform_no_nulls_after_clean():
    df = pd.DataFrame({
        "name": ["Alice", None, "Charlie"],
        "age": [30, None, 25],
        "salary": [50000, 60000, None]
    })
    result = transform(df)
    assert result.isnull().sum().sum() == 0
