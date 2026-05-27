import os
import sys
import time

print("--- URUCHAMIANIE MODUŁU SPARK ---", flush=True)
print("Pobieranie sterowników Kafka z sieci... (To może potrwać od 2 do 5 minut, cierpliwości!)", flush=True)

# Magiczna linijka pobierająca sterowniki
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 pyspark-shell'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Tworzenie sesji (tutaj następuje to długie pobieranie)
spark = SparkSession.builder \
    .appName("AGV_Predictive_Maintenance") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("✅ Gotowe! Silnik Spark uruchomiony.", flush=True)
print("🔗 Łączenie z Kafką...", flush=True)

schema = StructType([
    StructField("timestamp", StringType()),
    StructField("agv_id", StringType()),
    StructField("telemetry", StructType([
        StructField("motors", StructType([
            StructField("rear_right", StructType([
                StructField("speed_rpm", DoubleType()),
                StructField("temp_C", DoubleType())
            ]))
        ]))
    ]))
])

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "telemetry_topic") \
    .option("startingOffsets", "latest") \
    .load()

parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

alerts = parsed_df.filter(
    (col("telemetry.motors.rear_right.temp_C") > 50.0) & 
    (col("telemetry.motors.rear_right.speed_rpm") < 118.0)
)

final_alerts = alerts.withColumn("ALERT_MSG", lit("🚨 KRYTYCZNE ZATARCIE: Prawy tył przegrzany! 🚨"))

print("📡 Nasłuchiwanie strumienia rozpoczęte! Szukam anomalii...", flush=True)

query = final_alerts \
    .selectExpr("CAST(agv_id AS STRING) AS key", "to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "alerts_topic") \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .trigger(processingTime='1 second') \
    .start()

query.awaitTermination()