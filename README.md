# 📉 Collection Intelligence & Operational Strategy
### *Risk-Based Decisining + Asset Recovery Pipeline*

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://python.org)
[![SQL](https://img.shields.io/badge/SQL-Operational%20Queuing-orange?logo=sqlite)](https://sqlite.org)
[![ROI](https://img.shields.io/badge/Efficiency-Multiplier--Applied-green)](https://en.wikipedia.org/wiki/Operational_efficiency)

---

## 🎯 Operational Decision Layer
This project automates the **Collections Agent Desk** by moving from random outreach to a **Risk-Weighted Priority Queue**.

### 📋 Final Agent Action Queue (Automated)
The system outputs a live priority list with specific operational actions:
- **🔥 CALL IMMEDIATELY**: High balance at risk + Late-stage buckets.
- **📞 Agent Call**: Standard delinquency follow-up.
- **📱 SMS + IVR**: Early-stage automated reminders.
- **✉️ Email Sequence**: Low-value/Current-segment nurture.

---

## 📊 Business KPI: Recovery Efficiency
We measure the **Recovery Efficiency Multiplier** by comparing our model-driven strategy against a random outreach baseline.
- **Goal**: Catch the highest volume of defaults with the lowest operational capacity (Top 20% of calls).
- **Result**: Demonstrated efficiency gains by focusing on high-PD cohorts early in the delinquency cycle.

---

## 🏗️ Segmentation & Bucketing
The SQL layer implements a rigorous **Bucketing System** to track aging assets:
- **Bucket 0**: Current (Healthy)
- **Bucket 1**: 1-30 Days Late (Early Delinquency)
- **Bucket 2**: 31-90 Days Late (NPL Risk)
- **Bucket 4**: 90+ Days / Charged Off (NPL Recovery)

---

## 📂 Data & Methodology
- **Dataset**: LendingClub (Real P2P loan performance).
- **Strategy**: SQL-driven prioritization score calculated as `Balance * (1.2 - Predicted Recovery Rate)`.
- **Visualization**: Segmentation heatmaps and Loss Exposure charts.

---

## 🔍 Visual Insights
- **Recovery Rate by Bucket**: Identifying where recovery effort yields the highest return.
- **Operational Decision Layer**: Preview of the top-5 actionable IDs in the agent queue.
- **Realized Loss Analysis**: Visualizing where the portfolio is bleeding capital.

---

*Fintech Data Analyst Portfolio — Operations & Recovery Pillar.*
