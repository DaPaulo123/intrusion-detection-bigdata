"""
feature_engineering.py
-----------------------
Module tao them cac dac trung moi (Feature Engineering) tu du lieu mang UNSW-NB15.
Cac feature moi giup mo hinh ML hoc duoc nhieu goc do hon tchu khong chi dua vao
cac cot go san trong dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, log1p


def add_network_features(df: DataFrame) -> DataFrame:
    """
    Tao cac dac trung moi tu cac cot co san trong UNSW-NB15.

    Feature moi:
      - total_bytes    : Tong byte trao doi ca 2 chieu (sbytes + dbytes)
      - byte_ratio     : Ti le byte chieu len / tong byte (sbytes / total_bytes)
      - pkt_ratio      : Ti le goi tin chieu len / tong goi (spkts / (spkts+dpkts))
      - log_duration   : Log1p cua thoi gian ket noi (xu ly gia tri skewed)
      - is_bidirection : Co 1 neu co du lieu ca 2 chieu (sbytes>0 va dbytes>0)

    Args:
        df: PySpark DataFrame da qua buoc preprocessing

    Returns:
        PySpark DataFrame voi cac cot feature moi duoc them vao
    """
    # total_bytes: tong luong byte trao doi 2 chieu
    if 'sbytes' in df.columns and 'dbytes' in df.columns:
        df = df.withColumn('total_bytes', col('sbytes') + col('dbytes'))

        # byte_ratio: ty le byte gui di so voi tong (tranh chia 0)
        df = df.withColumn(
            'byte_ratio',
            when(col('total_bytes') > 0, col('sbytes') / col('total_bytes')).otherwise(0.0)
        )

    # pkt_ratio: ty le goi tin gui di so voi tong goi
    if 'spkts' in df.columns and 'dpkts' in df.columns:
        total_pkts = col('spkts') + col('dpkts')
        df = df.withColumn(
            'pkt_ratio',
            when(total_pkts > 0, col('spkts') / total_pkts).otherwise(0.0)
        )

    # log_duration: log1p de xu ly phan phoi lech (highly skewed duration)
    if 'dur' in df.columns:
        df = df.withColumn('log_duration', log1p(col('dur')))

    # is_bidirectional: ket noi co du lieu 2 chieu hay khong
    if 'sbytes' in df.columns and 'dbytes' in df.columns:
        df = df.withColumn(
            'is_bidirectional',
            when((col('sbytes') > 0) & (col('dbytes') > 0), 1).otherwise(0)
        )

    return df
