"""
preprocessing.py
-----------------
Module tien xu ly du lieu chung cho ca Batch Processing (Phan 2) va ML (Phan 4).
Cac ham nay duoc goi lai tu spark_sample.py va xgb_model.py de dam bao
nhat quan trong quy trinh xu ly du lieu.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, regexp_replace, when

def clean_dataframe(df: DataFrame) -> DataFrame:
    """
    Thuc hien cac buoc tien xu ly co ban tren PySpark DataFrame giong voi notebook.
    """
    # 1. Lam sach cot attack_cat va cac cot string khac
    string_cols = [c for c, t in df.dtypes if t == 'string']
    
    # Dien gia tri cho attack_cat (null hoac rong -> 'Normal')
    if 'attack_cat' in df.columns:
        df = df.fillna({'attack_cat': 'Normal'})
        df = df.withColumn('attack_cat', trim(col('attack_cat')))
        df = df.withColumn('attack_cat', regexp_replace(col('attack_cat'), 'Backdoors', 'Backdoor'))
        df = df.withColumn('attack_cat', when(col('attack_cat') == '', 'Normal').otherwise(col('attack_cat')))
    
    # Dien gia tri mac dinh cho cac cot string khac de khong bi drop boi StringIndexer
    fill_dict = {c: 'Unknown' for c in string_cols if c != 'attack_cat'}
    if fill_dict:
        df = df.fillna(fill_dict)  # type: ignore

    # 2. Ep kieu cho cac cot so thuc
    numeric_cols = ["sbytes", "dbytes", "dur", "sttl", "dttl", "sloss", "dloss"]
    for c in numeric_cols:
        if c in df.columns:
            df = df.withColumn(c, col(c).cast("double"))

    # 3. Dien gia tri 0 cho TẤT CẢ cac cot so (int, double, bigint) de tranh loi NULL khi dua vao VectorAssembler
    numeric_cols_all = [c for c, t in df.dtypes if t in ('int', 'double', 'bigint')]
    if numeric_cols_all:
        df = df.fillna(0, subset=numeric_cols_all)

    # 4. Xoa cot thua khong mang thong tin hoac khong can thiet cho ML
    cols_to_drop = ['srcip', 'dstip', 'sport', 'dsport', 'stcpb', 'dtcpb', 'stime', 'ltime', 'label']
    for c in cols_to_drop:
        if c in df.columns:
            df = df.drop(c)

    return df
