from pyspark.sql.functions import when, col

df = spark.table("silver_insurance")
gold_df = df.withColumn("fraud_flag", when(col("claim_amount") > 10000, "HIGH_RISK")
                        .when(col("claim_status") == "REJECTED", "MEDIUM_RISK")
                        .otherwise("LOW_RISK"))

gold_df.write.format("delta").mode("overwrite").saveAsTable("gold_claims")

