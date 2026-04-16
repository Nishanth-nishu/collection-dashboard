"""
=============================================================================
PROJECT 2: Collection Intelligence & Recovery Modeling
Machine Learning & Financial Impact Engine
=============================================================================
Model: Logistic Regression for Loss Prediction
Business Value:
  - Predicts probability of Charge-off.
  - Calculates "Recovery Efficiency Multiplier" (Simulated ROI).
=============================================================================
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE = Path(".")
DATA_PATH = Path("lending_club_openintro.csv")

def run_ml_impact_analysis():
    print("🚀 Running Recovery Risk ML Engine...")
    df = pd.read_csv(DATA_PATH)

    # Filtering for terminal statuses
    df_model = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])].copy()
    df_model['target'] = (df_model['loan_status'] == 'Charged Off').astype(int)

    features = ['annual_income', 'debt_to_income', 'loan_amount', 'interest_rate']
    X = df_model[features].fillna(df_model[features].median())
    y = df_model['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    model = LogisticRegression(class_weight='balanced')
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]

    # -----------------------------------------------------------------------
    # 1. BUSINESS KPI: RECOVERY EFFICIENCY MULTIPLIER
    # -----------------------------------------------------------------------
    # Simulation: If we call the top 20% of high-risk customers, 
    # how many defaults do we "catch" vs. random calling?
    
    test_results = X_test.copy()
    test_results['Target'] = y_test
    test_results['Prob'] = y_prob
    
    # Sort by risk
    test_results = test_results.sort_values('Prob', ascending=False)
    
    top_20_pct_count = int(len(test_results) * 0.2)
    defaults_caught_model = test_results.head(top_20_pct_count)['Target'].sum()
    
    # Baseline comparison (Random Selection)
    defaults_caught_random = test_results['Target'].sum() * 0.2 
    
    efficiency_multiplier = (defaults_caught_model / defaults_caught_random) if defaults_caught_random > 0 else 1.0
    
    print("\n📈 Business Impact Metrics:")
    print(f"Random Call Baseline (20% sample): {defaults_caught_random:.1f} defaults caught")
    print(f"Risk-Based Priority  (20% sample): {defaults_caught_model:.1f} defaults caught")
    print(f"Recovery Efficiency Multiplier:    {efficiency_multiplier:.2f}x")

    # -----------------------------------------------------------------------
    # 2. VISUALIZATION
    # -----------------------------------------------------------------------
    # Plot 1: Lift Chart (Simplified)
    plt.figure(figsize=(10, 6))
    plt.bar(['Random Strategy', 'Model-Driven Strategy'], [defaults_caught_random, defaults_caught_model], color=['gray', 'blue'])
    plt.title("Business Impact: Defaults Caught at 20% Operational Capacity", fontsize=14)
    plt.ylabel("Number of Predicted Defaults")
    plt.savefig(BASE / "recovery_by_bucket.png")
    
    # Plot 2: Driver impact
    plt.figure(figsize=(10, 6))
    importance = pd.Series(model.coef_[0], index=features).sort_values()
    importance.plot(kind='barh', color='teal')
    plt.title("Key Risk Drivers (Recovery Priority)", fontsize=14)
    plt.savefig(BASE / "collection_strategy.png")

    print(f"✨ Impact analysis generated at {BASE}")

if __name__ == "__main__":
    run_ml_impact_analysis()
