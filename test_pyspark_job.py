import pytest
from pyspark.sql import SparkSession

from pyspark_job import clean_data


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for the tests."""
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("PySparkUnitTests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    yield spark

    spark.stop()


@pytest.fixture
def input_df(spark):
    """Create test data."""
    data = [
        ("Alice", 100.0),
        ("Bob", 50.0),
        ("Charlie", 0.0),
        ("David", -20.0),
        (None, 80.0),
    ]

    return spark.createDataFrame(
        data,
        ["name", "amount"]
    )


def test_valid_records_are_kept(input_df):
    """Valid records should remain after cleaning."""
    result = clean_data(input_df)

    names = [row["name"] for row in result.select("name").collect()]

    assert names == ["Alice", "Bob"]


def test_records_with_non_positive_amount_are_removed(input_df):
    """Rows with amount <= 0 should be removed."""
    result = clean_data(input_df)

    amounts = [
        row["amount"]
        for row in result.select("amount").collect()
    ]

    assert 0.0 not in amounts
    assert -20.0 not in amounts


def test_records_with_null_names_are_removed(input_df):
    """Rows with NULL names should be removed."""
    result = clean_data(input_df)

    null_names = result.filter(
        result["name"].isNull()
    ).count()

    assert null_names == 0


def test_amount_with_tax_is_calculated_correctly(input_df):
    """amount_with_tax should equal amount * 1.20."""
    result = clean_data(input_df)

    rows = {
        row["name"]: row["amount_with_tax"]
        for row in result.select("name", "amount_with_tax").collect()
    }

    assert rows["Alice"] == pytest.approx(120.0)
    assert rows["Bob"] == pytest.approx(60.0)