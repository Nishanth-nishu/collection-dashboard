import pandas as pd
import numpy as np
import os

def generate_collections_data(n_loans=1000):
    np.random.seed(99)
    
    loan_ids = range(5000, 5000 + n_loans)
    balances = np.random.uniform(500, 5000, size=n_loans)
    
    # Delinquency buckets (Probability distribution)
    # Most are in early buckets, some in later
    buckets = ['1-30 DPD', '31-60 DPD', '61-90 DPD', '90+ DPD']
    dpd_dist = np.random.choice(buckets, p=[0.5, 0.25, 0.15, 0.10], size=n_loans)
    
    # Days past due within bucket
    dpd_days = []
    for b in dpd_dist:
        if b == '1-30 DPD': dpd_days.append(np.random.randint(1, 31))
        elif b == '31-60 DPD': dpd_days.append(np.random.randint(31, 61))
        elif b == '61-90 DPD': dpd_days.append(np.random.randint(61, 91))
        else: dpd_days.append(np.random.randint(91, 180))
        
    # Recovery Probability (Decreases as DPD increases)
    # Formula: Baseline 0.8 - (DPD * 0.004)
    recovery_prob = 0.8 - (np.array(dpd_days) * 0.004)
    recovery_prob = np.clip(recovery_prob, 0.05, 0.95)
    
    recovered = np.random.binomial(1, recovery_prob)
    
    # Self-Healer flag (likelihood to pay without agent contact)
    # High DPD loans rarely self-heal
    self_heal_prob = np.where(np.array(dpd_days) < 15, 0.4, 0.05)
    is_self_healer = np.random.binomial(1, self_heal_prob)
    
    df = pd.DataFrame({
        'loan_id': loan_ids,
        'dpd_bucket': dpd_dist,
        'days_past_due': dpd_days,
        'principal_balance': balances,
        'recovery_status': recovered,
        'is_self_healer': is_self_healer,
        'recovery_probability': recovery_prob
    })
    
    output_path = '/scratch/nishanth.r/pallavi/project_2_collections_analytics/loan_collections_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Collections dataset generated at {output_path}")

if __name__ == "__main__":
    generate_collections_data()
