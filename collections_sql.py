"""
=============================================================================
PROJECT 2: Collection Intelligence & Operational Strategy
SQL Analytics Engine — Production-Grade Edition
=============================================================================
Dataset: LendingClub (Real P2P Loan Performance Data)
Business Objectives:
  - Operationalize recovery by segmenting borrowers into Buckets (0-90+ days).
  - Generate an Actionable Priority Queue for automated collection workflows.
  - Calculate Expected Recovery Value vs. Cost of Operation.
=============================================================================
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

BASE = Path(".")
DATA_DIR = Path(".")
DB   = BASE / "collections.db"

# ---------------------------------------------------------------------------
# 1. SCHEMA DESIGN
# ---------------------------------------------------------------------------
DDL = """
DROP TABLE IF EXISTS loan_performance;

CREATE TABLE loan_performance (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_amount          REAL NOT NULL,
    term                 INTEGER,
    int_rate             REAL,
    grade                TEXT,
    annual_inc           REAL,
    loan_status          TEXT,
    balance              REAL,
    paid_total           REAL,
    paid_principal       REAL,
    paid_interest        REAL,
    paid_late_fees       REAL,
    issue_month          TEXT,
    ingested_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status ON loan_performance(loan_status);
"""

# ---------------------------------------------------------------------------
# 2. ANALYTICAL SQL QUERIES (BUSINESS & OPERATIONAL LAYERS)
# ---------------------------------------------------------------------------

QUERIES = {

    # Highlight 1: Operational Segment Bucketing
    "delinquency_bucket_analysis": """
        WITH bucketed AS (
            SELECT
                *,
                CASE 
                    WHEN loan_status = 'Current' THEN 'Bucket 0 (Current)'
                    WHEN loan_status LIKE '%Late (16-30 days)%' THEN 'Bucket 1 (16-30d)'
                    WHEN loan_status LIKE '%Late (31-120 days)%' THEN 'Bucket 2 (31-120d)'
                    WHEN loan_status = 'In Grace Period' THEN 'Bucket 0.5 (Grace)'
                    WHEN loan_status = 'Default' OR loan_status = 'Charged Off' THEN 'Bucket 4 (NPL)'
                    ELSE 'Other'
                END AS delinquency_bucket
            FROM loan_performance
        )
        SELECT
            delinquency_bucket,
            COUNT(*)                                      AS customer_count,
            ROUND(SUM(balance), 0)                        AS outstanding_exposure,
            ROUND(AVG(paid_total / loan_amount) * 100, 2) AS recovery_rate_pct
        FROM bucketed
        GROUP BY delinquency_bucket
        ORDER BY delinquency_bucket;
    """,

    # Highlight 2: Operational Action Queue (Agent Prioritization)
    # This query generates the specific "Next Best Action" for agents.
    "final_agent_action_queue": """
        WITH priority_calc AS (
            SELECT
                id,
                loan_status,
                grade,
                balance,
                -- Priority Logic: High balance + High risk (Grade D-G) = High Priority
                CASE 
                    WHEN grade IN ('E', 'F', 'G') AND balance > 5000 THEN 0.95
                    WHEN loan_status LIKE '%Late (31-120 days)%' THEN 0.85
                    WHEN balance > 10000 THEN 0.75
                    ELSE 0.40
                END AS risk_urgency_score
            FROM loan_performance
            WHERE loan_status != 'Fully Paid' AND loan_status != 'Current'
        )
        SELECT
            id,
            loan_status,
            ROUND(balance, 2) AS balance_at_risk,
            CASE 
                WHEN risk_urgency_score >= 0.90 THEN '🔥 CALL IMMEDIATELY (Legal Warning)'
                WHEN risk_urgency_score >= 0.75 THEN '📞 Agent Call (Standard)'
                WHEN risk_urgency_score >= 0.50 THEN '📱 SMS + Automated IVR'
                ELSE '✉️ Email Sequence'
            END AS recommended_action,
            RANK() OVER (ORDER BY risk_urgency_score DESC, balance DESC) AS queue_rank
        FROM priority_calc
        LIMIT 20;
    """,

    # Highlight 3: Recovery Efficiency KPI
    "portfolio_profitability_impact": """
        SELECT
            loan_status,
            COUNT(*) AS count,
            ROUND(SUM(loan_amount), 0) AS initial_exposure,
            ROUND(SUM(paid_total), 0)  AS amount_recovered,
            ROUND(SUM(loan_amount - paid_total), 0) AS realized_loss
        FROM loan_performance
        GROUP BY loan_status;
    """
}

# ---------------------------------------------------------------------------
# 3. EXECUTION ENGINE
# ---------------------------------------------------------------------------

def load_and_run():
    csv_path = DATA_DIR / "lending_club_openintro.csv"
    if not csv_path.exists():
        print(f"❌ Data file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    # Mapping to standard names
    cols = {
        'loan_amount': 'loan_amount', 'term': 'term', 'interest_rate': 'int_rate',
        'grade': 'grade', 'annual_income': 'annual_inc', 'loan_status': 'loan_status',
        'balance': 'balance', 'paid_total': 'paid_total', 'paid_principal': 'paid_principal',
        'paid_late_fees': 'paid_late_fees', 'issue_month': 'issue_month'
    }
    df_clean = df[list(cols.keys())].rename(columns=cols)

    con = sqlite3.connect(DB)
    con.executescript(DDL)
    df_clean.to_sql("loan_performance", con, if_exists="append", index=False)
    con.commit()
    print(f"✅ Lending performance data ingestion complete.")

    # Execute Analytics
    results = {}
    for name, sql in QUERIES.items():
        results[name] = pd.read_sql_query(sql, con)
        print(f"\n🧩 {name.upper()}")
        print(results[name].head(10).to_string(index=False))

    # Visualization
    sns.set_theme(style="whitegrid", palette="muted")
    fig = plt.figure(figsize=(20, 12), facecolor="#f8f9fa")
    fig.suptitle("Fintech Operations — Collections Strategy & Recovery Dashboard",
                 fontsize=22, fontweight="bold", y=0.98)
    
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)

    # Plot 1: Recovery by Bucket
    ax1 = fig.add_subplot(gs[0, 0])
    sns.barplot(x="delinquency_bucket", y="recovery_rate_pct", data=results["delinquency_bucket_analysis"], ax=ax1, palette="viridis")
    ax1.set_title("Recovery Rate Performance by Delinquency Bucket", fontsize=14)
    plt.setp(ax1.get_xticklabels(), rotation=15)

    # Plot 2: NPL Exposure
    ax2 = fig.add_subplot(gs[0, 1])
    d2 = results["delinquency_bucket_analysis"]
    plt.pie(d2['outstanding_exposure'], labels=d2['delinquency_bucket'], autopct='%1.1f%%', colors=sns.color_palette("flare"))
    ax2.set_title("Outstanding Portfolio Exposure by Bucket", fontsize=14)

    # Plot 3: Loss Analysis
    ax3 = fig.add_subplot(gs[1, 0])
    d3 = results["portfolio_profitability_impact"]
    sns.barplot(x="loan_status", y="realized_loss", data=d3[d3['realized_loss'] > 0], ax=ax3, palette="Reds_r")
    ax3.set_title("Realized Losses by Loan Status (Non-Performing Credits)", fontsize=14)
    plt.setp(ax3.get_xticklabels(), rotation=25)

    # Plot 4: Action Queue Preview (Table style)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    q_text = "🎯 TOP PRIORITY ACTIONS (Queue Preview):\n\n"
    for _, row in results["final_agent_action_queue"].head(5).iterrows():
        q_text += f"- ID {int(row['id'])}: {row['recommended_action']} | Amt: ₹{int(row['balance_at_risk']):,}\n"
    ax4.text(0.1, 0.45, q_text, fontsize=15, family="monospace", bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))
    ax4.set_title("Operational Decision Layer", fontsize=16, fontweight="bold")

    plt.savefig(BASE / "collections_sql_dashboard.png", dpi=120, bbox_inches="tight")
    con.close()
    print(f"✅ Dashboard generated: {BASE / 'collections_sql_dashboard.png'}")

if __name__ == "__main__":
    load_and_run()
