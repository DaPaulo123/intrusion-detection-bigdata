"""
feature_engineering.py
-----------------------
Module tao them cac dac trung moi (Feature Engineering) tu du lieu mang UNSW-NB15.
Cac feature moi giup mo hinh ML hoc duoc nhieu goc do hon tchu khong chi dua vao
cac cot go san trong dataset.
"""

from typing import Optional, Tuple
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, avg, broadcast

def calculate_network_stats(df: DataFrame) -> Tuple[Optional[DataFrame], Optional[DataFrame]]:
    """
    Tinh toan cac gia tri thong ke trung binh tu tap TRAIN.
    Chong Data Leakage: Chi tinh tren tap Train, roi dung ket qua nay ep vao ca Train va Test.
    """
    proto_stats = None
    state_stat = None
    
    if 'proto' in df.columns:
        proto_stats = df.groupBy("proto").agg(
            avg("dur").alias("avg_dur_proto"),
            avg("sbytes").alias("avg_sbytes_proto"),
            avg("dbytes").alias("avg_dbytes_proto"),
            avg("sload").alias("avg_sload_proto"),
            avg("spkts").alias("avg_spkts_proto"),
            avg("dpkts").alias("avg_dpkts_proto")
        )
        
    if 'state' in df.columns:
        state_stat = df.groupBy('state').agg(
            avg('dur').alias("avg_dur_state"),
            avg('sbytes').alias('avg_sbytes_state'),
            avg('dbytes').alias('avg_dbytes_state'),
            avg('sload').alias('avg_sload_state'),
            avg('spkts').alias('avg_spkts_state'),
            avg('dpkts').alias('avg_dpkts_state'),
        )
        
    return proto_stats, state_stat


def apply_network_features(df: DataFrame, proto_stats: Optional[DataFrame] = None, state_stat: Optional[DataFrame] = None) -> DataFrame:
    """
    Ghep cac ban thong ke da hoc tu tap Train vao du lieu (Train/Test)
    va tinh toan cac dac trung 파i sinh.
    """
    # 1. Tinh bytes_ratio (chi dung du lieu dong hien tai)
    if 'sbytes' in df.columns and 'dbytes' in df.columns:
        df = df.withColumn(
            'bytes_ratio',
            when(col('dbytes') == 0, 0.0).otherwise(col('sbytes') / col('dbytes'))
        )

    # 2. Join proto_stats
    if proto_stats is not None and 'proto' in df.columns:
        df = df.join(broadcast(proto_stats), on='proto', how='left')

    # 3. Join state_stat
    if state_stat is not None and 'state' in df.columns:
        df = df.join(broadcast(state_stat), on='state', how='left')

    # 4. Tinh threat_score (can co cac cot avg da join tu proto_stats)
    if all(c in df.columns for c in ['sbytes', 'avg_sbytes_proto', 'sload', 'avg_sload_proto']):
        from pyspark.sql.functions import abs as spark_abs
        bytes_dev = spark_abs(col("sbytes") - col("avg_sbytes_proto")) / (col("avg_sbytes_proto") + 1)
        load_dev = spark_abs(col("sload") - col("avg_sload_proto")) / (col("avg_sload_proto") + 1)
        df = df.withColumn(
            "threat_score",
            when(
                col("sbytes").isNull() | col("avg_sbytes_proto").isNull() | col("sload").isNull() | col("avg_sload_proto").isNull(), 
                0.0
            ).otherwise(bytes_dev * 0.5 + load_dev * 0.5)
        )

    # Xy ly null do join (vi du Test co 1 loai giao thuc chua tung co trong Train)
    df = df.fillna(0.0)
    
    return df
