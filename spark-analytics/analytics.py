"""Baseline drive diagnostics: overheating warnings, not a seizure classifier."""
import os
os.environ.setdefault("PYSPARK_SUBMIT_ARGS",
    "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 pyspark-shell")
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit, array, struct, explode, to_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

MOTORS = ("front_left", "front_right", "rear_left", "rear_right")
motor_schema = StructType([StructField("speed_rpm", DoubleType()), StructField("temp_C", DoubleType())])
schema = StructType([
    StructField("timestamp", DoubleType()), StructField("agv_id", StringType()),
    StructField("session_id", StringType()), StructField("sequence", LongType()),
    StructField("telemetry", StructType([StructField("motors", StructType([
        StructField(name, motor_schema) for name in MOTORS]))]))
])

def main():
    broker = os.getenv("KAFKA_SERVER", "kafka:9092")
    spark = (SparkSession.builder.master(os.getenv("SPARK_MASTER", "local[2]"))
             .appName("AGV_Drive_Diagnostics").config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    try:
        raw = (spark.readStream.format("kafka").option("kafka.bootstrap.servers", broker)
               .option("subscribe", "telemetry_topic").option("startingOffsets", "earliest").load())
        data = raw.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
        motors = data.select("timestamp", "agv_id", "session_id", "sequence", explode(array(*[
            struct(lit(name).alias("name"), col(f"telemetry.motors.{name}.temp_C").alias("temperature"))
            for name in MOTORS])).alias("motor"))
        alerts = (motors.filter(col("motor.temperature") > float(os.getenv("ALERT_TEMP_C", "50")))
                  .withColumn("ALERT_MSG", lit("Podwyższona temperatura silnika — sprawdź napęd"))
                  .withColumn("schema_version", lit(1)))
        query = (alerts.select(col("agv_id").alias("key"), to_json(struct("*")).alias("value"))
                 .writeStream.format("kafka").option("kafka.bootstrap.servers", broker)
                 .option("topic", "alerts_topic")
                 .option("checkpointLocation", os.getenv("SPARK_CHECKPOINT", "/checkpoints/drive-temperature-v1"))
                 .trigger(processingTime="1 second").start())
        query.awaitTermination()
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
