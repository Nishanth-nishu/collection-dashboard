import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score

sns.set_theme(style="whitegrid")

def run_recovery_analysis():
    # 1. Load Data
    df = pd.read_csv('/scratch/nishanth.r/pallavi/project_2_collections_analytics/loan_collections_data.csv')
    
    # 2. Roll-Rate Simulation (Cross-tab of DPD Buckets vs Recovery)
    # This is a key fintech metric
    roll_rate = df.groupby('dpd_bucket')['recovery_status'].mean().sort_index()
    print("\nRecovery Rate by DPD Bucket:")
    print(roll_rate)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=roll_rate.index, y=roll_rate.values, palette="viridis")
    plt.title('Loan Recovery Probability by DPD Bucket')
    plt.ylabel('Probability of Recovery')
    plt.savefig('/scratch/nishanth.r/pallavi/project_2_collections_analytics/recovery_by_bucket.png')
    
    # 3. Recovery Prediction Model
    X = df[['days_past_due', 'principal_balance']]
    y = df['recovery_status']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Using Logistic Regression for explainability in Collections
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"\nRecovery Prediction Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    
    # 4. Strategy Recommendation: "Self-Healers" vs "Contact Immediately"
    # We identify loans with high recovery chance but low contact priority
    df['recovery_prob_pred'] = model.predict_proba(X)[:, 1]
    
    # Self-Healers: High prob of recovery & early DPD
    df['strategy'] = 'Standard Collection'
    df.loc[(df['recovery_prob_pred'] > 0.8) & (df['days_past_due'] < 10), 'strategy'] = 'Soft Reminder (Potential Self-Healer)'
    df.loc[(df['recovery_prob_pred'] < 0.3), 'strategy'] = 'High Priority (Likely Default)'
    
    strategy_counts = df['strategy'].value_counts()
    print("\nCollections Strategy Distribution:")
    print(strategy_counts)
    
    plt.figure()
    strategy_counts.plot(kind='pie', autopct='%1.1f%%', colormap='Set3')
    plt.title('Recommended Collection Strategies')
    plt.ylabel('')
    plt.savefig('/scratch/nishanth.r/pallavi/project_2_collections_analytics/collection_strategy.png')
    
    print("\nSaved Recovery plots and Analysis results.")

if __name__ == "__main__":
    run_recovery_analysis()
