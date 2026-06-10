import os
import json
import time
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, roc_auc_score, confusion_matrix
)

# ============================================================
def print_banner(title):
    width = 62
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)

def print_section(title):
    print(f"\n  --- {title} ---")

def format_size(path):
    """Tra ve kich thuoc file theo don vi KB/MB."""
    size = os.path.getsize(path)
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / 1024 / 1024:.1f} MB"

# ============================================================
def main():
    _here     = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(_here, '..', 'data', 'processed', 'train_cleaned.parquet')
    test_path  = os.path.join(_here, '..', 'data', 'processed', 'test_cleaned.parquet')
    model_dir  = os.path.join(_here, '..', 'models')
    os.makedirs(model_dir, exist_ok=True)

    total_start = time.time()

    # ===========================================================
    # BUOC 1: LOAD & PREVIEW DU LIEU
    # ===========================================================
    print_banner("[1/5] LOAD DU LIEU TU BATCH PROCESSING")
    train_df = pd.read_parquet(train_path)
    test_df  = pd.read_parquet(test_path)

    print(f"\n  Train set : {len(train_df):>10,} dong | {train_df.shape[1]} cot")
    print(f"  Test set  : {len(test_df):>10,} dong | {test_df.shape[1]} cot")

    print_section("Phan bo nhan (attack_cat) trong tap TRAIN")
    train_dist = train_df['attack_cat'].value_counts()
    for label, count in train_dist.items():
        pct = count / len(train_df) * 100
        bar = "█" * int(pct / 2)
        print(f"    {label:<20}: {count:>8,}  ({pct:5.2f}%)  {bar}")

    print_section("Phan bo nhan (attack_cat) trong tap TEST")
    test_dist = test_df['attack_cat'].value_counts()
    for label, count in test_dist.items():
        pct = count / len(test_df) * 100
        bar = "█" * int(pct / 2)
        print(f"    {label:<20}: {count:>8,}  ({pct:5.2f}%)  {bar}")

    print_section("Mau 5 dong du lieu sau Batch Processing")
    preview_cols = ['proto', 'service', 'state', 'sbytes', 'dbytes',
                    'spkts', 'dpkts', 'dur', 'attack_cat']
    preview_cols = [c for c in preview_cols if c in train_df.columns]
    print(train_df[preview_cols].head(5).to_string(index=False))

    # ===========================================================
    # TIEN XU LY CHUNG
    # ===========================================================
    train_df['is_attack'] = (train_df['attack_cat'] != 'Normal').astype(int)
    test_df['is_attack']  = (test_df['attack_cat'] != 'Normal').astype(int)

    leaky_cols = ['sttl', 'dttl', 'ct_state_ttl']
    train_df = train_df.drop(columns=[c for c in leaky_cols if c in train_df.columns])
    test_df  = test_df.drop(columns=[c for c in leaky_cols if c in test_df.columns])

    cat_cols = train_df.select_dtypes(include=['object', 'string']).columns.tolist()  # type: ignore
    if 'attack_cat' in cat_cols:
        cat_cols.remove('attack_cat')

    cat_encoders = {}
    for col in cat_cols:
        train_df[col] = train_df[col].astype('category')
        cat_encoders[col] = dict(enumerate(train_df[col].cat.categories))
        train_df[col] = train_df[col].cat.codes
        test_df[col]  = pd.Categorical(
            test_df[col], categories=list(cat_encoders[col].values())
        ).codes

    with open(os.path.join(model_dir, 'categorical_encoders.json'), 'w') as f:
        json.dump(cat_encoders, f)

    attack_classes  = sorted([c for c in train_df['attack_cat'].unique() if c != 'Normal'])
    class_mapping   = {c: i for i, c in enumerate(attack_classes)}
    reverse_mapping = {v: k for k, v in class_mapping.items()}

    with open(os.path.join(model_dir, 'attack_mapping.json'), 'w') as f:
        json.dump(class_mapping, f)

    train_df['attack_label'] = train_df['attack_cat'].map(class_mapping)
    test_df['attack_label']  = test_df['attack_cat'].map(class_mapping)
    features = [c for c in train_df.columns
                if c not in ['attack_cat', 'is_attack', 'attack_label', 'label']]

    # ===========================================================
    # BUOC 2: HUAN LUYEN STAGE 1 — BINARY
    # ===========================================================
    print_banner("[2/5] HUAN LUYEN STAGE 1 — BINARY (Normal vs Attack)")
    t0  = time.time()
    sw1 = compute_sample_weight('balanced', train_df['is_attack'])
    xgb_stage1 = xgb.XGBClassifier(
        n_estimators=100, max_depth=6, random_state=42,
        eval_metric='logloss', verbosity=0
    )
    xgb_stage1.fit(train_df[features], train_df['is_attack'], sample_weight=sw1)
    s1_train_time = time.time() - t0

    # --- Danh gia Stage 1 ---
    pred_s1      = xgb_stage1.predict(test_df[features])
    pred_s1_prob = xgb_stage1.predict_proba(test_df[features])[:, 1]

    s1_acc  = accuracy_score(test_df['is_attack'], pred_s1)
    s1_prec = precision_score(test_df['is_attack'], pred_s1, zero_division=0)
    s1_rec  = recall_score(test_df['is_attack'], pred_s1, zero_division=0)
    s1_f1   = f1_score(test_df['is_attack'], pred_s1, zero_division=0)
    s1_auc  = roc_auc_score(test_df['is_attack'], pred_s1_prob)

    # Confusion matrix de tinh FPR / FNR
    tn, fp, fn, tp = confusion_matrix(test_df['is_attack'], pred_s1).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Negative Rate (nguy hiem nhat)

    print(f"\n  Thoi gian huan luyen : {s1_train_time:.1f}s")
    print(f"  So cay (n_estimators): 100 | Do sau (max_depth): 6")
    print(f"  Tap Test             : {len(test_df):,} dong\n")
    print(f"  {'Accuracy':<28}: {s1_acc  * 100:.4f}%")
    print(f"  {'Precision':<28}: {s1_prec * 100:.4f}%")
    print(f"  {'Recall (Detection Rate)':<28}: {s1_rec  * 100:.4f}%")
    print(f"  {'F1-Score':<28}: {s1_f1   * 100:.4f}%")
    print(f"  {'AUC-ROC':<28}: {s1_auc  * 100:.4f}%")

    print_section("Security Metrics (Quan trong trong An Toan Thong Tin)")
    fpr_icon = "⚠" if fpr > 0.05 else "✓"
    fnr_icon = "⚠" if fnr > 0.03 else "✓"
    print(f"  {'False Positive Rate (FPR)':<28}: {fpr * 100:.4f}%  {fpr_icon}  (Bao dong nham)")
    print(f"  {'False Negative Rate (FNR)':<28}: {fnr * 100:.4f}%  {fnr_icon}  (Bo sot tan cong - NGUY HIEM)")

    print_section("Chi tiet phat hien tan cong")
    total_attacks = int(tp + fn)
    total_normals = int(tn + fp)
    print(f"  Tan cong thuc te  : {total_attacks:>8,}")
    print(f"  Da phat hien (TP) : {int(tp):>8,}  ✓")
    print(f"  Bo sot (FN)       : {int(fn):>8,}  ✗  <- can giam thieu")
    print(f"  Binh thuong that  : {total_normals:>8,}")
    print(f"  Bao dong nham (FP): {int(fp):>8,}  ✗  <- gay alert fatigue")

    # ===========================================================
    # BUOC 3: HUAN LUYEN STAGE 2 — MULTICLASS
    # ===========================================================
    print_banner("[3/5] HUAN LUYEN STAGE 2 — MULTICLASS (9 loai tan cong)")
    attack_train = train_df[train_df['is_attack'] == 1].copy()

    MAX_SAMPLES = 5000
    print(f"\n  Undersampling: gioi han toi da {MAX_SAMPLES:,} mau/nhan")
    print(f"  {'Nhan':<22} {'Truoc':>8}   {'Sau':>6}   Trang thai")
    print(f"  {'-'*55}")
    dfs = []
    for c in sorted(attack_train['attack_cat'].unique()):
        df_c   = attack_train[attack_train['attack_cat'] == c]
        before = len(df_c)
        if len(df_c) > MAX_SAMPLES:
            df_c = df_c.sample(MAX_SAMPLES, random_state=42)
            status = "Cat bot"
        else:
            status = "Giu nguyen"
        print(f"  {c:<22} {before:>8,} -> {len(df_c):>6,}   {status}")
        dfs.append(df_c)

    balanced_attack_train = pd.concat(dfs)
    print(f"\n  Tong mau huan luyen Stage 2: {len(balanced_attack_train):,}")
    sw2 = compute_sample_weight('balanced', balanced_attack_train['attack_label'])

    t0 = time.time()
    xgb_stage2 = xgb.XGBClassifier(
        n_estimators=200, max_depth=8, min_child_weight=1,
        random_state=42, eval_metric='mlogloss', verbosity=0
    )
    xgb_stage2.fit(
        balanced_attack_train[features],
        balanced_attack_train['attack_label'],
        sample_weight=sw2
    )
    s2_train_time = time.time() - t0

    # --- Danh gia Stage 2 ---
    attack_test = test_df[test_df['is_attack'] == 1].copy()
    pred_s2     = xgb_stage2.predict(attack_test[features])
    s2_labels   = sorted(attack_test['attack_label'].dropna().unique().astype(int))
    s2_names    = [reverse_mapping.get(i, str(i)) for i in s2_labels]

    s2_acc = accuracy_score(attack_test['attack_label'], pred_s2)
    s2_mf1 = f1_score(attack_test['attack_label'], pred_s2, average='macro', zero_division=0)
    s2_wf1 = f1_score(attack_test['attack_label'], pred_s2, average='weighted', zero_division=0)

    print(f"\n  Thoi gian huan luyen : {s2_train_time:.1f}s")
    print(f"  So cay (n_estimators): 200 | Do sau (max_depth): 8\n")
    print(f"  {'Accuracy':<28}: {s2_acc * 100:.4f}%")
    print(f"  {'Macro F1-Score':<28}: {s2_mf1 * 100:.4f}%  (trung binh deu cac nhan)")
    print(f"  {'Weighted F1-Score':<28}: {s2_wf1 * 100:.4f}%  (trung binh theo so mau)")

    print_section("Bao cao chi tiet tung loai tan cong")
    print(classification_report(
        attack_test['attack_label'], pred_s2,
        labels=s2_labels, target_names=s2_names,
        digits=4, zero_division=0
    ))

    # Top cap nham lan
    print_section("Top 5 cap nham lan nhieu nhat (Stage 2)")
    cm2 = confusion_matrix(attack_test['attack_label'], pred_s2, labels=s2_labels)
    confusions = []
    for i, true_name in enumerate(s2_names):
        for j, pred_name in enumerate(s2_names):
            if i != j and cm2[i, j] > 0:
                confusions.append((cm2[i, j], true_name, pred_name))
    confusions.sort(reverse=True)
    print(f"  {'That':<20} {'Du doan nham':<20} {'So luong':>8}")
    print(f"  {'-'*50}")
    for count, true_n, pred_n in confusions[:5]:
        print(f"  {true_n:<20} -> {pred_n:<20} {count:>6} lan")

    # ===========================================================
    # BUOC 4: DANH GIA TONG THE (KET HOP 2 GIAI DOAN)
    # ===========================================================
    print_banner("[4/5] DANH GIA TONG THE — MO HINH 2 GIAI DOAN KET HOP")
    print("\n  Dang chay du doan ket hop tren toan bo tap Test...")

    # Lay xac suat Stage 1 de xac dinh Attack
    final_labels  = []
    test_features = test_df[features].values
    s1_preds      = pred_s1              # Da co san tu tren
    s2_input_idx  = np.where(s1_preds == 1)[0]

    # Du doan Stage 2 theo lo (batch) cho nhanh
    s2_preds_all  = np.full(len(test_df), -1, dtype=int)
    if len(s2_input_idx) > 0:
        s2_batch = xgb_stage2.predict(test_df[features].iloc[s2_input_idx.tolist()])
        s2_preds_all[s2_input_idx] = s2_batch

    for i in range(len(test_df)):
        if s1_preds[i] == 0:
            final_labels.append('Normal')
        else:
            idx = int(s2_preds_all[i])
            final_labels.append(reverse_mapping.get(idx, 'Unknown'))

    true_labels = test_df['attack_cat'].tolist()
    all_classes = ['Normal'] + attack_classes

    overall_acc = accuracy_score(true_labels, final_labels)
    overall_mf1 = f1_score(true_labels, final_labels, average='macro',    zero_division=0, labels=all_classes)
    overall_wf1 = f1_score(true_labels, final_labels, average='weighted', zero_division=0, labels=all_classes)

    print(f"\n  Ket qua cuoi cung tren {len(test_df):,} dong test:\n")
    print(f"  {'Accuracy':<28}: {overall_acc * 100:.4f}%")
    print(f"  {'Macro F1-Score':<28}: {overall_mf1 * 100:.4f}%")
    print(f"  {'Weighted F1-Score':<28}: {overall_wf1 * 100:.4f}%")

    print_section("Bao cao chi tiet 10 nhan (Normal + 9 Attack)")
    print(classification_report(
        true_labels, final_labels,
        labels=all_classes, target_names=all_classes,
        digits=4, zero_division=0
    ))

    total_time = time.time() - total_start
    print(f"  Tong thoi gian huan luyen & danh gia: {total_time:.1f}s")

    # ===========================================================
    # BUOC 5: LUU MODEL & METRICS
    # ===========================================================
    print_banner("[5/5] LUU MODEL VA CAU HINH")
    s1_path = os.path.join(model_dir, 'stage1_model.json')
    s2_path = os.path.join(model_dir, 'stage2_model.json')
    fn_path = os.path.join(model_dir, 'feature_names.json')
    mt_path = os.path.join(model_dir, 'model_metrics.json')

    xgb_stage1.save_model(s1_path)
    xgb_stage2.save_model(s2_path)

    with open(fn_path, 'w') as f:
        json.dump(features, f)

    # Chi so day du luu vao JSON de Backend / Dashboard doc
    metrics_summary = {
        "stage1": {
            "accuracy":    round(float(s1_acc),  4),
            "precision":   round(float(s1_prec), 4),
            "recall":      round(float(s1_rec),  4),
            "f1":          round(float(s1_f1),   4),
            "auc_roc":     round(float(s1_auc),  4),
            "fpr":         round(float(fpr),     4),
            "fnr":         round(float(fnr),     4),
            "tp": int(tp), "fp": int(fp),
            "tn": int(tn), "fn": int(fn),
            "n_estimators": 100,
            "max_depth": 6,
            "train_time_sec": round(s1_train_time, 1)
        },
        "stage2": {
            "accuracy":    round(float(s2_acc), 4),
            "macro_f1":    round(float(s2_mf1), 4),
            "weighted_f1": round(float(s2_wf1), 4),
            "n_estimators": 200,
            "max_depth": 8,
            "max_samples_per_class": MAX_SAMPLES,
            "train_time_sec": round(s2_train_time, 1)
        },
        "overall": {
            "accuracy":    round(float(overall_acc), 4),
            "macro_f1":    round(float(overall_mf1), 4),
            "weighted_f1": round(float(overall_wf1), 4),
        },
        "model_files": {
            "stage1_size": format_size(s1_path),
            "stage2_size": format_size(s2_path),
        },
        "total_train_time_sec": round(total_time, 1),
        "is_simulated": False
    }

    with open(mt_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_summary, f, indent=2, ensure_ascii=False)

    print(f"\n  {'File':<35} {'Kich thuoc':>12}")
    print(f"  {'-'*50}")
    for fname in ['stage1_model.json', 'stage2_model.json',
                  'feature_names.json', 'attack_mapping.json',
                  'categorical_encoders.json', 'model_metrics.json']:
        fpath = os.path.join(model_dir, fname)
        if os.path.exists(fpath):
            print(f"  {fname:<35} {format_size(fpath):>12}")

    print(f"\n  [HOAN THANH] Tong thoi gian: {total_time:.1f}s")
    print("  He thong san sang phuc vu API / Kafka Streaming!\n")

if __name__ == '__main__':
    main()
