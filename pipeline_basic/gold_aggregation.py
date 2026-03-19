from pyspark.sql.functions import *

silver_df=spark.read.format("delta").load("/Volumes/workspace/default/datafiles/silver_taxi")
daily_revenue=silver_df.groupBy("lpep_pickup_datetime") \
    .agg(sum("total_amount").alias("revenue"))

daily_revenue.write.mode("overwrite").format("delta") \
    .save("/Volumes/workspace/default/datafiles/gold_daily_revenue")

daily_revenue.display()