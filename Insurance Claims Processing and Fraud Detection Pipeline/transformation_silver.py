from pyspark.sql.functions import col

claims = spark.table("bronze_claims")
policies = spark.table("bronze_policies")
customers = spark.table("bronze_customers")

#clean claims
claims.clean = claims.dropDuplicates(['claim_id']).filter(col("claim_amount").isNotNull())

#join datasets
silver_df = claims_clean.join(policies, "policy_id", "left").join(customers, "customer_id", "left")
silver_df.write.format("delta").mode("overwrite").saveAsTable("silver_insurance")