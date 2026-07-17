from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression

df = spark.table("gold_claims")

#feature engineering
assembler = VectorAssembler(inputCols=["claim_amount"], outputCol = "features")

data = assembler.tranform(df)

#train the model
lr = LogisticRegression(lableCol="fraud_flag", featuresCol="features")
model = lr.fit(data)
