import dlt
from pyspark.sql.functions import col

@dlt.table(
    name="bronze_users",
    comment="Raw users data"
)
def bronze_users():
    return spark.read.format("delta") \
        .load("/Volumes/workspace/default/datafiles/tmp/dlt_lab/raw_users")

@dlt.table(
    name="silver_users",
    comment="Cleaned users data"
)
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
@dlt.expect_or_drop("valid_name", "name IS NOT NULL")

def silver_users():
    return (
        dlt.read("bronze_users")
        .filter(col("age").isNull())
    )
