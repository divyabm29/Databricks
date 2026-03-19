from pyspark.sql.functions import *
raw_df = spark.read \
    .option("header", "true") \
    .option("inferschema", "true") \
    .csv("/Volumes/workspace/default/datafiles/taxi_tripdata.csv")

raw_df.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/Volumes/workspace/default/datafiles/bronze_taxi_data_delta")
print("Bronze layer created")

spark.read.format("delta").load("/Volumes/workspace/default/datafiles/bronze_taxi_data_delta").display()