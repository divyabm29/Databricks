from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("InsuranceIngestion").getOrCreate()

#load raw csv file
claims_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/FileStore/tables/insurance.csv")

policies_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/FileStore/tables/policies.csv")

customers_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/FileStore/tables/customers.csv")

#null checks
df.filter(col("claim_id").isNull()).count()

#duplicate check
df.groupBy("claim_id").count().filter("count > 1").show()

#write  data to delta table
claims_df.write.mode("overwrite").format("delta").saveAsTable("bronze_claims")
policies_df.write.mode("overwrite").format("delta").saveAsTable("bronze_policies")
customers_df.write.mode("overwrite").format("delta").saveAsTable("bronze_customers")