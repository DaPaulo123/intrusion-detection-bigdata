"""
graphframes_analysis.py
------------------------
Phan tich do thi quan he giua cac dia chi IP trong luu luong mang
su dung GraphFrames cua PySpark.

Phan tich nay giup xac dinh:
  - Cac IP co do ket noi cao bat thuong (Hub nodes) - dau hieu scan/DDoS
  - Cac doan duyet ngan nhat giua cac IP (BFS - dau hieu lateral movement)
  - Cac thanh phan lien thong (Connected components) trong luong mang

NOTE: GraphFrames can cai them:
  pip install graphframes
  Spark submit voi --packages graphframes:graphframes:0.8.2-spark3.2-s_2.12
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, desc


def build_ip_graph(spark: SparkSession, df: DataFrame):
    """
    Xay dung do thi IP tu DataFrame luu luong mang.
    Moi ket noi mang (row) la 1 canh (edge) Source IP -> Destination IP.

    Args:
        spark: SparkSession
        df   : DataFrame da qua tien xu ly, can co cot 'srcip' va 'dstip'

    Returns:
        Tuple (vertices, edges) la 2 DataFrame cho GraphFrames
    """
    try:
        # Tap dinh: tat ca cac IP duy nhat
        src_ips = df.select(col('srcip').alias('id'))
        dst_ips = df.select(col('dstip').alias('id'))
        vertices = src_ips.union(dst_ips).distinct()

        # Tap canh: moi ban ghi la 1 ket noi
        edges = df.select(
            col('srcip').alias('src'),
            col('dstip').alias('dst'),
            col('label')
        )

        print(f'[GraphFrames] Do thi: {vertices.count()} dinh, {edges.count()} canh')
        return vertices, edges

    except Exception as e:
        print(f'[GraphFrames] Loi khi xay dung do thi: {e}')
        return None, None


def analyze_top_talkers(df: DataFrame, top_n: int = 10):
    """
    Tim cac IP "noi nhieu nhat" (Top Talkers) - nhung IP co so ket noi cao nhat.
    IP co so ket noi bat thuong cao la dau hieu cua Network Scan hoac DDoS source.

    Args:
        df   : DataFrame luu luong mang (can co cot 'srcip')
        top_n: So luong IP top can hien thi

    Returns:
        DataFrame chua top N IP nguon theo so ket noi
    """
    if 'srcip' not in df.columns:
        print('[GraphFrames] Khong tim thay cot srcip')
        return None

    print(f'\n[GraphFrames] Top {top_n} Source IP co nhieu ket noi nhat (Top Talkers):')
    result = df.groupBy('srcip') \
               .agg(count('*').alias('connection_count')) \
               .orderBy(desc('connection_count')) \
               .limit(top_n)
    result.show(truncate=False)
    return result


def analyze_attack_sources(df: DataFrame, top_n: int = 10):
    """
    Tim cac IP nguon cua cac ket noi duoc ghan nhan la tan cong (label=1).

    Args:
        df   : DataFrame luu luong mang (can co cot 'srcip' va 'label')
        top_n: So luong IP can hien thi

    Returns:
        DataFrame chua top N IP nguon tan cong
    """
    if 'srcip' not in df.columns or 'label' not in df.columns:
        print('[GraphFrames] Thieu cot srcip hoac label')
        return None

    print(f'\n[GraphFrames] Top {top_n} IP nguon cua cac ket noi tan cong (label=1):')
    result = df.filter(col('label') == 1) \
               .groupBy('srcip') \
               .agg(count('*').alias('attack_count')) \
               .orderBy(desc('attack_count')) \
               .limit(top_n)
    result.show(truncate=False)
    return result


if __name__ == '__main__':
    """
    Chay phan tich do thi tren du lieu UNSW-NB15.
    Can co file CSV goc de co cot srcip va dstip.
    """
    spark = SparkSession.builder \
        .appName('UNSW-NB15-GraphAnalysis') \
        .master('local[*]') \
        .getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')

    csv_path = '../data/UNSW_NB15_testing-set.csv'
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    df = df.dropna()

    print('=== IP Graph Analysis - UNSW-NB15 ===')
    analyze_top_talkers(df, top_n=10)
    analyze_attack_sources(df, top_n=10)
    build_ip_graph(spark, df)

    spark.stop()
