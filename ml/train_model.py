"""
train_model.py
--------------
Module xay dung va huan luyen mo hinh PySpark MLlib.
Tach biet logic training khoi rf_model.py de de tai su dung
va thu nghiem voi cac thuat toan khac nhau.
"""

from pyspark.sql import DataFrame
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier


def build_preprocessing_pipeline(train_df: DataFrame, label_col: str = 'label'):
    """
    Xay dung va fit Pipeline tien xu ly: StringIndexer -> VectorAssembler.
    Pipeline duoc fit tren tap TRAIN, sau do ap dung len ca TRAIN va TEST
    (tranh Data Leakage tu tap test vao qua trinh fit encoder).

    Args:
        train_df  : DataFrame tap huan luyen (da qua buoc clean)
        label_col : Ten cot nhan (mac dinh 'label')

    Returns:
        Tuple (feature_cols, fitted_pipeline, train_transformed)
    """
    # Tim cac cot kieu chuoi can encode
    categorical_cols = [c for c, t in train_df.dtypes if t == 'string' and c != label_col]

    # StringIndexer cho tung cot categorical
    indexers = [
        StringIndexer(inputCol=c, outputCol=c + '_index', handleInvalid='skip')
        for c in categorical_cols
    ]

    pipeline = Pipeline(stages=indexers)
    fitted_pipeline = pipeline.fit(train_df)

    # Transform va xoa cot goc
    df_indexed = fitted_pipeline.transform(train_df).drop(*categorical_cols)

    # Lay danh sach feature (tat ca tru label)
    feature_cols = [c for c in df_indexed.columns if c != label_col]

    # VectorAssembler gom cac feature thanh 1 vector
    assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')
    train_transformed = assembler.transform(df_indexed).select('features', label_col)

    return feature_cols, fitted_pipeline, assembler, train_transformed


def apply_pipeline(df: DataFrame, fitted_pipeline: PipelineModel,
                   assembler: VectorAssembler, categorical_cols: list,
                   label_col: str = 'label') -> DataFrame:
    """
    Ap dung Pipeline da fit len mot DataFrame moi (thay la tap test).

    Args:
        df              : DataFrame can transform (tap test)
        fitted_pipeline : Pipeline da duoc fit tren tap train
        assembler       : VectorAssembler da duoc tao tu tap train
        categorical_cols: Danh sach cot categorical can drop
        label_col       : Ten cot nhan

    Returns:
        DataFrame da transform voi cot 'features' va label
    """
    df_indexed = fitted_pipeline.transform(df).drop(*categorical_cols)
    return assembler.transform(df_indexed).select('features', label_col)


def train_random_forest(train_data: DataFrame,
                        num_trees: int = 50,
                        max_bins: int = 256,
                        seed: int = 42):
    """
    Huan luyen mo hinh Random Forest voi PySpark MLlib.

    Args:
        train_data: DataFrame voi cot 'features' va 'label'
        num_trees : So cay quyet dinh (mac dinh 50)
        max_bins  : So bin toi da cho bien lien tuc (mac dinh 256)
        seed      : Random seed de tai tao ket qua

    Returns:
        Mo hinh RandomForestClassificationModel da duoc fit
    """
    rf = RandomForestClassifier(
        labelCol='label',
        featuresCol='features',
        numTrees=num_trees,
        maxBins=max_bins,
        seed=seed
    )
    return rf.fit(train_data)
