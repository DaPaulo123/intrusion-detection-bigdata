"""
evaluate.py
-----------
Module danh gia mo hinh Machine Learning toan dien.
Cung cap cac ham tinh toan va in ra:
  - Accuracy, Precision, Recall, F1, AUC-ROC
  - Confusion Matrix
  - Feature Importances (Top N) - Ho tro ca RandomForest va XGBoost
  - Chuan doan Overfit (Train vs Test gap)
"""

from pyspark.sql import DataFrame
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


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

    return {
        'accuracy' : mc.setMetricName('accuracy').evaluate(predictions),
        'precision': mc.setMetricName('weightedPrecision').evaluate(predictions),
        'recall'   : mc.setMetricName('weightedRecall').evaluate(predictions),
        'f1'       : mc.setMetricName('f1').evaluate(predictions),
    }


def _get_feature_importances(model, feature_cols: list, top_n: int = 10):
    """
    Lay feature importances tu mo hinh (ho tro ca RF va XGBoost).
    Tra ve danh sach [(name, score), ...] da sap xep giam dan.
    Neu khong lay duoc, tra ve None.
    """
    importances = None

    # Thu lay featureImportances tu PySpark RF model
    if hasattr(model, 'featureImportances'):
        importances = model.featureImportances.toArray()
    # Thu lay feature_importances_ tu XGBoost model (native)
    elif hasattr(model, 'get_feature_importances'):
        importances = model.get_feature_importances()
    # SparkXGBClassifierModel: thu truy cap native booster
    elif hasattr(model, 'get_booster'):
        try:
            booster = model.get_booster()
            score_dict = booster.get_score(importance_type='gain')
            # Map tu ten feature (f0, f1, ...) sang ten thuc
            imp_array = [0.0] * len(feature_cols)
            for key, val in score_dict.items():
                idx = int(key.replace('f', ''))
                if idx < len(imp_array):
                    imp_array[idx] = val
            importances = imp_array
        except Exception:
            pass

    if importances is None:
        return None

    pairs = sorted(
        zip(feature_cols, importances),
        key=lambda x: x[1], reverse=True
    )[:top_n]
    return pairs


def print_report(train_metrics: dict, test_metrics: dict,
                 model,
                 feature_cols: list,
                 predictions_test: DataFrame,
                 top_n: int = 10, label_col: str = 'label'):
    """
    In bao cao danh gia day du ra console.

    Args:
        train_metrics    : Dict metrics tren tap train
        test_metrics     : Dict metrics tren tap test
        model            : Mo hinh da train (RF hoac XGBoost)
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
    predictions_test.groupBy(label_col, 'prediction') \
        .count().orderBy(label_col, 'prediction').show(100)

    # Feature Importances
    pairs = _get_feature_importances(model, feature_cols, top_n)
    if pairs:
        print(f'  Top {top_n} Important Features:')
        for i, (name, score) in enumerate(pairs, 1):
            print(f'    {i:2}. {name:<30} -> {score:.4f}')
    else:
        print('  [INFO] Khong the lay Feature Importances tu mo hinh nay.')
    print('=======================================================')
