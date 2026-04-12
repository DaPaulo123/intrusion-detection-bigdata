from pyspark.sql import SparkSession

def main():
    # Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName("UNSW-NB15-Data-Exploration") \
        .master("local[*]") \
        .getOrCreate()

    # Tắt log quá nhiều của Spark
    spark.sparkContext.setLogLevel("ERROR")

    print("\n--- Reading data UNSW-NB15 ---")
    file_path = "../data/UNSW_NB15_testing-set.csv"
    
    try:
        df = spark.read.csv(file_path, header=True, inferSchema=True)
        print(f"Total Rows: {df.count()}")
        
        print("\n--- Columns in Dataset ---")
        for col in df.columns:
            print(f"- {col}")
            
        print("\n--- First 5 rows ---")
        df.show(5, truncate=False)
        
    except Exception as e:
        print(f"Error reading file: {e}")
        
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
