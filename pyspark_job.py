from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def clean_data(df: DataFrame) -> DataFrame:
    """
    Clean the input DataFrame.

    Rules:
    - Remove rows where amount <= 0.
    - Remove rows where name is NULL.
    - Add amount_with_tax = amount * 1.20.
    """
    cleaned_df = df.filter(
        (col("amount") > 0) & col("name").isNotNull()
    )

    cleaned_df = cleaned_df.withColumn(
        "amount_with_tax",
        col("amount") * 1.20
    )

    return cleaned_df