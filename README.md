# 📉 Collection Intelligence & Recovery Prediction
### *Production-Grade SQL + ML Analytics — Pallav Technologies*

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://python.org)
[![SQL](https://img.shields.io/badge/SQL-SQLite%2FPostgreSQL--Compatible-orange?logo=sqlite)](https://sqlite.org)
[![Dataset](https://img.shields.io/badge/Dataset-LendingClub-blue)](https://www.lendingclub.com)

---

## 🎯 Business Problem
Collections yield is the most sensitive metric in retail lending. This project uses real **LendingClub** performance data to optimize recovery strategies. It specifically addresses how to prioritize agent efforts using risk-weighted outstanding balances.

---

## 📊 SQL Analytics Engine (`collections_sql.py`)

The analytics engine calculates real-time recovery metrics and generates an optimized agent queue.

### Key Analysis:
- **Recovery Metrics by Grade**: Real-time tracking of `Amount Recovered vs. Disbursed` across risk grades.
- **Agent Priority Queue**: A risk-weighted ranking system (`Balance * (1.2 - Recovery Rate)`) to identify high-value/high-risk accounts for immediate contact.
- **Cumulative Loss Tracking**: Using `SUM() OVER()` to track loss exposure as the portfolio ages.

---

## 🤖 ML Recovery Modeling (`recovery_analysis.py`)

- **Model**: Logistic Regression (Interpretable Logit).
- **Target**: Charged Off vs. Fully Paid.
- **Insight**: Models the probability of loss based on borrower income, debt-to-income (DTI), and loan installment size.

---

## 📂 Data Sources
This project use a subset of the LendingClub loan performance dataset.
- **Key Features**: Annual Income, DTI, Paid Principal, Interest, Late Fees.
- **Volume**: 10,000 credit records.

---

## 🔍 Visual Insights
Generated dashboards include:
1. **Recovery Rate by Grade**: Visualizing the drop-off in performance for lower-tier loans.
2. **Disbursement vs Recovery**: Volume analysis by loan quality.
3. **Priority Queue Visualization**: Ranking delinquent IDs by predicted recovery value.

---

*Built for Pallav Technologies Portfolio — Advanced Collections Pillar.*
