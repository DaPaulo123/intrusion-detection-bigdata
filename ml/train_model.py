"""
train_model.py
--------------
Module xay dung va huan luyen mo hinh PySpark MLlib.
Tach biet logic training khoi rf_model.py de de tai su dung
va thu nghiem voi cac thuat toan khac nhau.
"""

from pyspark.sql import DataFrame
import pyspark.sql.functions as F
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
    label_is_string = dict(train_df.dtypes).get(label_col) == 'string'
    
    # Tim cac cot kieu chuoi can encode (tru label)
    categorical_cols = [c for c, t in train_df.dtypes if t == 'string' and c != label_col]

    # StringIndexer cho tung cot categorical
    indexers = [
        StringIndexer(inputCol=c, outputCol=c + '_index', handleInvalid='keep')
        for c in categorical_cols
    ]
    
    final_label_col = label_col
    if label_is_string:
        final_label_col = label_col + '_index'
        indexers.append(StringIndexer(inputCol=label_col, outputCol=final_label_col, handleInvalid='keep'))

    pipeline = Pipeline(stages=indexers) # type: ignore
    fitted_pipeline = pipeline.fit(train_df)

    # Transform va xoa cot goc
    df_indexed = fitted_pipeline.transform(train_df).drop(*categorical_cols)
    if label_is_string:
        df_indexed = df_indexed.drop(label_col)

    # Lay danh sach feature (tat ca tru label)
    feature_cols = [c for c in df_indexed.columns if c != final_label_col]

    # VectorAssembler gom cac feature thanh 1 vector
    assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')
    train_transformed = assembler.transform(df_indexed).select('features', final_label_col)

    return feature_cols, fitted_pipeline, assembler, train_transformed, final_label_col



def apply_pipeline(df: DataFrame, fitted_pipeline: PipelineModel,
                   assembler: VectorAssembler, categorical_cols: list,
                   label_col: str, final_label_col: str) -> DataFrame:
    """
    Ap dung Pipeline da fit len mot DataFrame moi (thay la tap test).
    """
    df_indexed = fitted_pipeline.transform(df).drop(*categorical_cols)
    if label_col != final_label_col:
        df_indexed = df_indexed.drop(label_col)
    return assembler.transform(df_indexed).select('features', final_label_col)


def add_class_weights(df: DataFrame, label_col: str, weight_col: str = 'class_weight') -> DataFrame:
    """
    Tinh toan va them cot trong so de xu ly Mat can bang du lieu (Class Imbalance).
    Nhan hiem -> trong so cao; Nhan pho bien -> trong so thap.
    """
    total_count = df.count()
    num_classes = df.select(label_col).distinct().count()
    
    # Tinh so luong cua moi class
    class_counts = df.groupBy(label_col).count().collect()
    
    # Tao bieu thuc F.when de map label -> weight
    # Cong thuc: weight = total_count / (num_classes * class_count)
    weight_expr = None
    for row in class_counts:
        label_val = row[label_col]
        count_val = row['count']
        weight_val = total_count / (num_classes * count_val)
        
        if weight_expr is None:
            weight_expr = F.when(F.col(label_col) == label_val, weight_val)
        else:
            weight_expr = weight_expr.when(F.col(label_col) == label_val, weight_val)
            
    # Neu khong khop nao (khong xay ra), cho weight = 1.0
    if weight_expr is not None:
        weight_expr = weight_expr.otherwise(1.0)
    else:
        weight_expr = F.lit(1.0)
    
    return df.withColumn(weight_col, weight_expr)


def train_random_forest(train_data: DataFrame,
                        label_col: str = 'label',
                        weight_col: str | None = None,
                        num_trees: int = 50,
                        max_bins: int = 256,
                        seed: int = 42):
    """
    Huan luyen mo hinh Random Forest voi PySpark MLlib.
    Ho tro weight_col de tri Class Imbalance.
    """
    rf = RandomForestClassifier(
        labelCol=label_col,
        featuresCol='features',
        numTrees=num_trees,
        maxBins=max_bins,
        seed=seed
    )
    
    if weight_col:
        rf.setWeightCol(weight_col)
        
    return rf.fit(train_data)
