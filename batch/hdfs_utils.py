"""
hdfs_utils.py
--------------
Module tien ich doc/ghi du lieu giua he thong file cuc bo (local) va HDFS.
Cung cap giao dien thong nhat de spark_sample.py co the luu Parquet
ma khong can quan tam den moi truong dang chay (local hay Docker cluster).
"""

import os
from typing import Optional
from pyspark.sql import DataFrame, SparkSession


def save_parquet(df: DataFrame, path: str, overwrite: bool = True) -> bool:
    """
    Luu PySpark DataFrame ra dinh dang Parquet.
    Tu dong tao thu muc cha neu chua ton tai (voi duong dan local).

    Args:
        df       : PySpark DataFrame can luu
        path     : Duong dan dich (local path hoac hdfs://...)
        overwrite: Ghi de neu da ton tai (mac dinh True)

    Returns:
        True neu luu thanh cong, False neu that bai
    """
    try:
        # Neu la local path, tao thu muc parent truoc
        if not path.startswith('hdfs://'):
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

        mode = 'overwrite' if overwrite else 'error'
        df.write.mode(mode).parquet(path)
        print(f"[hdfs_utils] Da luu Parquet thanh cong: {path}")
        return True

    except Exception as e:
        print(f"[hdfs_utils] Loi khi luu Parquet: {e}")
        return False


def load_parquet(spark: SparkSession, path: str) -> Optional[DataFrame]:
    """
    Doc du lieu Parquet tu duong dan (local hoac HDFS).

    Args:
        spark: SparkSession hien tai
        path : Duong dan Parquet

    Returns:
        PySpark DataFrame, hoac None neu khong doc duoc
    """
    try:
        df = spark.read.parquet(path)
        print(f"[hdfs_utils] Da doc Parquet: {path} ({df.count()} dong)")
        return df
    except Exception as e:
        print(f"[hdfs_utils] Loi khi doc Parquet {path}: {e}")
        return None


def load_csv(spark: SparkSession, path: str) -> Optional[DataFrame]:
    """
    Doc file CSV voi header va tu dong suy kieu du lieu (inferSchema).

    Args:
        spark: SparkSession hien tai
        path : Duong dan file CSV

    Returns:
        PySpark DataFrame
    """
    try:
        df = spark.read.csv(path, header=True, inferSchema=True)
        print(f"[hdfs_utils] Da doc CSV: {path} ({df.count()} dong)")
        return df
    except Exception as e:
        print(f"[hdfs_utils] Loi khi doc CSV {path}: {e}")
        return None
