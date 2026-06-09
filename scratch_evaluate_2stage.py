import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
if sys.platform == 'win32':
    os.environ['HADOOP_HOME'] = r'C:\hadoop'
    _bin = r'C:\hadoop\bin'
    if _bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _bin + ';' + os.environ.get('PATH', '')

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.ml import PipelineModel
from pyspark.ml.feature import StringIndexerModel
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = SparkSession.builder.appName("EvalTwoStage").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

model_dir = os.path.join(_here, 'models')
pipeline_path = os.path.join(model_dir, 'two_stage_pipeline')
stage1_path   = os.path.join(model_dir, 'two_stage_model1_binary')
stage2_path   = os.path.join(model_dir, 'two_stage_model2_multi')

fitted_prep = PipelineModel.load(pipeline_path)
model_stage1 = RandomForestClassificationModel.load(stage1_path)
model_stage2 = RandomForestClassificationModel.load(stage2_path)

test_parquet  = os.path.join(_here, 'data', 'processed', 'test_cleaned.parquet')
proc_test = spark.read.parquet(test_parquet)
proc_test = proc_test.withColumn("is_attack", when(col("attack_cat") == "Normal", 0).otherwise(1))

test_data = fitted_prep.transform(proc_test)

# Predict Stage 1
pred_1 = model_stage1.transform(test_data).withColumnRenamed("prediction", "pred_stage1").drop("rawPrediction", "probability")

# Predict Stage 2
pred_2 = model_stage2.transform(pred_1).withColumnRenamed("prediction", "pred_stage2")

normal_index = 0.0 # From previous logs we saw Normal is mapped to 0.0 or something. Let's find out dynamically.
indexer_stage = fitted_prep.stages[-2]
assert isinstance(indexer_stage, StringIndexerModel)
labels_array = indexer_stage.labels
normal_index = float(labels_array.index("Normal"))

final_pred = pred_2.withColumn(
    "final_prediction",
    when(col("pred_stage1") == 0, normal_index).otherwise(col("pred_stage2"))
)

evaluator_acc = MulticlassClassificationEvaluator(labelCol="attack_cat_index", predictionCol="final_prediction", metricName="accuracy")
evaluator_f1 = MulticlassClassificationEvaluator(labelCol="attack_cat_index", predictionCol="final_prediction", metricName="f1")

acc = evaluator_acc.evaluate(final_pred)
f1 = evaluator_f1.evaluate(final_pred)

print(f"TWO_STAGE_ACCURACY={acc * 100:.2f}%")
print(f"TWO_STAGE_F1={f1 * 100:.2f}%")
spark.stop()
