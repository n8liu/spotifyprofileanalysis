from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc

def analyze_tracks(features_path):
    spark = SparkSession.builder.appName('SpotifyAnalysis').getOrCreate()
    df = spark.read.csv(features_path, header=True, inferSchema=True)
    df.select('id', 'name', 'duration_ms', 'energy') \
      .orderBy(desc('duration_ms')) \
      .show(10)
    df.select('id', 'name', 'energy') \
      .orderBy(desc('energy')) \
      .show(10)
    spark.stop()

if __name__ == "__main__":
    import sys
    features_path = sys.argv[1] if len(sys.argv) > 1 else 'features.csv'
    analyze_tracks(features_path)
