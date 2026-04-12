import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import time

def main():
    print(">>> [1/5] Loading UNSW-NB15 dataset (Testing set)...")
    df = pd.read_csv('../data/UNSW_NB15_testing-set.csv')
    
    print(f">>> [2/5] Preprocessing data (Total records: {df.shape[0]})...")
    # Drop IDs & highly nested multiclass labels to focus on Binary Classification
    if 'id' in df.columns:
        df = df.drop(['id'], axis=1)
    if 'attack_cat' in df.columns:
        df = df.drop(['attack_cat'], axis=1)
        
    print("           -> Encoding string categorical variables...")
    categorical_cols = df.select_dtypes(include=['object']).columns
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
        
    # Drop empty rows just in case
    df = df.dropna()
    
    # Split input (Features) and target (Label)
    X = df.drop('label', axis=1)
    y = df['label']
    
    print(">>> [3/5] Splitting data into Training (80%) and Evaluation (20%) sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(">>> [4/5] Training Random Forest Classifier (n_estimators=50)...")
    start_time = time.time()
    
    # Init and Train Random Forest Model
    clf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    time_taken = time.time() - start_time
    print(f"           -> Training completed in {time_taken:.2f} seconds!")
    
    print(">>> [5/5] Predicting and calculating Accuracy on Evaluation set...")
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n=======================================================")
    print(f"* MODEL ACCURACY: {accuracy * 100:.2f}%")
    print("=======================================================")
    print("\n[Detailed Classification Report]")
    print(classification_report(y_test, y_pred, target_names=["Normal (0)", "Attack (1)"]))

if __name__ == "__main__":
    main()
