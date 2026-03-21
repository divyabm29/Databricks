from pyspark.sql.functions import *

bronze_df=spark.read.format("delta").load("/Volumes/workspace/default/datafiles/bronze_taxi_data_delta")

silver_df=bronze_df \
    .filter(col("fare_amount").isNotNull()) \
    .filter(col("trip_distance")>0) \
    .withColumn("pickup_datetime", to_timestamp(col("lpep_pickup_datetime"))) \
    .withColumn("dropoff_datetime", to_timestamp(col("lpep_dropoff_datetime"))) \
    .withColumn("pickup_year", year(col("pickup_datetime"))) \
    .withColumn("pickup_month", month(col("pickup_datetime")))

silver_df.write.mode("overwrite").format("delta").save("/Volumes/workspace/default/datafiles/silver_taxi")
    