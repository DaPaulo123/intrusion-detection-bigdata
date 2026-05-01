"""
evaluate.py
-----------
Module danh gia mo hinh Machine Learning toan dien.
Cung cap cac ham tinh toan va in ra:
  - Accuracy, Precision, Recall, F1, AUC-ROC
  - Confusion Matrix
  - Feature Importances (Top N)
  - Chuan doan Overfit (Train vs Test gap)
"""

from pyspark.sql import DataFrame
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator


def compute_metrics(predictions: DataFrame, label_col: str = 'label') -> dict:
    """
    Tinh toan cac chi so danh gia mo hinh phan loai nhi phan.

    Args:
        predictions: DataFrame chua cot 'label', 'prediction', 'rawPrediction'
        label_col  : Ten cot nhan

    Returns:
        Dict chua cac chi so: accuracy, precision, recall, f1, auc_roc
    """
    mc = MulticlassClassificationEvaluator(labelCol=label_col, predictionCol='prediction')
    bc = BinaryClassificationEvaluator(labelCol=label_col, rawPredictionCol='rawPrediction')

    return {
        'accuracy' : mc.setMetricName('accuracy').evaluate(predictions),
        'precision': mc.setMetricName('weightedPrecision').evaluate(predictions),
        'recall'   : mc.setMetricName('weightedRecall').evaluate(predictions),
        'f1'       : mc.setMetricName('f1').evaluate(predictions),
        'auc_roc'  : bc.setMetricName('areaUnderROC').evaluate(predictions),
    }


def print_report(train_metrics: dict, test_metrics: dict,
                 model: RandomForestClassificationModel,
                 feature_cols: list,
                 predictions_test: DataFrame,
                 top_n: int = 10):
    """
    In bao cao danh gia day du ra console.

    Args:
        train_metrics    : Dict metrics tren tap train
        test_metrics     : Dict metrics tren tap test
        model            : Mo hinh RandomForest da train
        feature_cols     : Danh sach ten cac feature
        predictions_test : DataFrame ket qua du doan tren tap test
        top_n            : So luong feature quan trong nhat can hien thi
    """
    gap_acc = train_metrics['accuracy'] - test_metrics['accuracy']
    gap_f1  = train_metrics['f1']       - test_metrics['f1']

    print('\n=======================================================')
    print('           MODEL EVALUATION REPORT')
    print('=======================================================')
    print(f"  {'Metric':<15} {'Train':>10} {'Test':>10} {'Gap':>10}")
    print(f"  {'-'*47}")
    print(f"  {'Accuracy':<15} {train_metrics['accuracy']*100:>9.2f}% "
          f"{test_metrics['accuracy']*100:>9.2f}% {gap_acc*100:>+9.2f}%")
    print(f"  {'F1-Score':<15} {train_metrics['f1']*100:>9.2f}% "
          f"{test_metrics['f1']*100:>9.2f}% {gap_f1*100:>+9.2f}%")
    print('-------------------------------------------------------')
    print(f"  Precision (Test) : {test_metrics['precision'] * 100:.2f}%")
    print(f"  Recall    (Test) : {test_metrics['recall']    * 100:.2f}%")
    print(f"  AUC-ROC   (Test) : {test_metrics['auc_roc']   * 100:.2f}%")
    print('-------------------------------------------------------')

    # Chuan doan Overfit
    print('  Overfit Diagnosis:')
    if gap_acc > 0.05:
        print(f'  [WARNING] Gap = {gap_acc*100:.2f}% -> OVERFIT! Can giam complexity mo hinh')
    elif gap_acc > 0.02:
        print(f'  [CAUTION] Gap = {gap_acc*100:.2f}% -> Overfit nhe, nen theo doi them')
    else:
        print(f'  [OK]      Gap = {gap_acc*100:.2f}% -> Mo hinh on dinh, khong overfit')
    print('-------------------------------------------------------')

    # Confusion Matrix
    print('  Confusion Matrix (Test Set):')
    predictions_test.groupBy('label', 'prediction') \
        .count().orderBy('label', 'prediction').show()

    # Feature Importances
    print(f'  Top {top_n} Important Features:')
    pairs = sorted(
        zip(feature_cols, model.featureImportances.toArray()),
        key=lambda x: x[1], reverse=True
    )[:top_n]
    for i, (name, score) in enumerate(pairs, 1):
        print(f'    {i:2}. {name:<30} -> {score:.4f}')
    print('=======================================================')
