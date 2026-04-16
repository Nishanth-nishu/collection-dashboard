"""
=============================================================================
PROJECT 2: Collection Intelligence & Recovery Prediction
Machine Learning Analysis for NPL Resolution
=============================================================================
Model: Logistic Regression (Interpretable) for Loss Prediction
Dataset: LendingClub Real Performance Data
Goal: Predict probability of "Charged Off" vs "Fully Paid"
=============================================================================
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE = Path(".")
DATA_PATH = Path("lending_club_openintro.csv")

def train_recovery_model():
    print("🚀 Loading LendingClub data for recovery modeling...")
    df = pd.read_csv(DATA_PATH)

    # We want to predict if a delinquent-prone loan will end up "Charged Off"
    # Filter for completed loans to train effectively
    df_model = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])].copy()
    df_model['target'] = (df_model['loan_status'] == 'Charged Off').astype(int)

    # Feature selection: income, debt-to-income, loan amount, etc.
    features = ['annual_income', 'debt_to_income', 'loan_amount', 'interest_rate']
    
    # Handle missing values
    X = df_model[features].fillna(df_model[features].median())
    y = df_model['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    print("🛠 Training interpretable Logistic Regression for recovery risk...")
    model = LogisticRegression(class_weight='balanced')
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    print("\n📈 Recovery Risk Model Performance:")
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Visualization: Prediction Probability Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(x=y_prob, hue=y_test, element="step", common_norm=False, palette="viridis")
    plt.title("Recovery Risk Probability Distribution (Charged Off vs Paid)", fontsize=14)
    plt.xlabel("Probability of Charge-Off")
    plt.savefig(BASE / "recovery_by_bucket.png")
    
    # Visualization: Coefficient Importance
    plt.figure(figsize=(10, 6))
    coeffs = pd.Series(model.coef_[0], index=features).sort_values()
    coeffs.plot(kind='barh', color='salmon')
    plt.title("Risk Drivers for Charged Off Loans (Logit Coefficients)", fontsize=14)
    plt.savefig(BASE / "collection_strategy.png")

    print(f"✨ Collections models and strategy visuals generated at {BASE}")

if __name__ == "__main__":
    train_recovery_model()
