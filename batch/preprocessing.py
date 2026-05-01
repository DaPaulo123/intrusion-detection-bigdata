"""
preprocessing.py
-----------------
Module tien xu ly du lieu chung cho ca Batch Processing (Phan 2) va ML (Phan 4).
Cac ham nay duoc goi lai tu spark_sample.py va rf_model.py de dam bao
nhat quan trong quy trinh xu ly du lieu.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def clean_dataframe(df: DataFrame) -> DataFrame:
    """
    Thuc hien cac buoc tien xu ly co ban tren PySpark DataFrame:
      1. Xoa cac dong co gia tri null (Missing values)
      2. Xoa cot thua khong mang thong tin (id, attack_cat)
      3. Loc nhieu trong cac cot chuoi (service, state)

    Args:
        df: PySpark DataFrame chua du lieu tho

    Returns:
        PySpark DataFrame da duoc lam sach
    """
    # Buoc 1: Xu ly gia tri trong (Missing values)
    df = df.dropna()

    # Buoc 2: Xoa cot thua
    # - 'id'         : Bo dem dong, khong mang y nghia ML
    # - 'attack_cat' : Nhan da lop, gay Data Leakage khi chi lam phan loai nhi phan
    for drop_col in ['id', 'attack_cat']:
        if drop_col in df.columns:
            df = df.drop(drop_col)

    # Buoc 3: Loc nhieu trong cac cot phan loai
    # Thiet bi mang thuong ghi '-' hoac 'unknown' khi khong xac dinh duoc dich vu/trang thai
    if 'service' in df.columns:
        df = df.filter(col('service') != '-').filter(col('service') != 'unknown')
    if 'state' in df.columns:
        df = df.filter(col('state') != '-').filter(col('state') != 'unknown')

    return df
