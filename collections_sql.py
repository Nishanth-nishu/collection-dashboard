"""
=============================================================================
PROJECT 2: Collection Intelligence & NPL Recovery (Real-World Case)
SQL Analytics Engine — Production-Grade Edition
=============================================================================
Dataset: LendingClub (Real P2P Loan Performance Data)
Demonstrates:
  - Recovery Rate analysis (Paid Amount vs Original Loan)
  - Delinquency segmentation for prioritize queue logic
  - Running totals for Value-at-Risk across portfolio segments
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
# 1. SCHEMA DESIGN (Lending Performance Schema)
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
CREATE INDEX idx_grade  ON loan_performance(grade);
"""

# ---------------------------------------------------------------------------
# 2. ANALYTICAL SQL QUERIES (Production-Grade Collections Analytics)
# ---------------------------------------------------------------------------

QUERIES = {

    # Query 1: Recovery Status Breakdown (Standard KPI)
    "recovery_metrics_by_grade": """
        SELECT
            grade,
            COUNT(*)                                      AS total_loans,
            ROUND(SUM(loan_amount), 0)                    AS total_disbursed,
            ROUND(SUM(paid_total), 0)                     AS total_recovered,
            ROUND(AVG(paid_total / loan_amount) * 100, 2) AS avg_recovery_rate_pct,
            SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) AS charged_off_count
        FROM loan_performance
        GROUP BY grade
        ORDER BY grade;
    """,

    # Query 2: Agent Priority Queue (Risk-Based Ranking)
    # Target: Customers who are 'Late' with high outstanding balances
    "collections_priority_queue": """
        WITH risk_table AS (
            SELECT
                id,
                loan_status,
                grade,
                loan_amount,
                balance,
                paid_late_fees,
                -- Priority Factor: high balance + low recovery
                (balance * (1.2 - (paid_total / loan_amount))) AS priority_score
            FROM loan_performance
            WHERE loan_status LIKE '%Late%' OR loan_status = 'Charged Off'
        )
        SELECT
            id,
            loan_status,
            grade,
            ROUND(balance, 2) AS current_balance,
            ROUND(priority_score, 2) AS priority_score,
            RANK() OVER (ORDER BY priority_score DESC) AS agent_rank
        FROM risk_table
        LIMIT 25;
    """,

    # Query 3: Running Loss Analysis (Window Functions)
    "cumulative_loss_exposure": """
        WITH monthly_losses AS (
            SELECT
                SUBSTR(issue_month, 5, 4) AS issue_year, 
                SUM(loan_amount - paid_total) AS loss_amt
            FROM loan_performance
            WHERE loan_status = 'Charged Off'
            GROUP BY issue_year
        )
        SELECT
            issue_year,
            ROUND(loss_amt, 0) AS total_loss,
            ROUND(SUM(loss_amt) OVER (ORDER BY issue_year), 0) AS running_total_loss
        FROM monthly_losses;
    """,

    # Query 4: Portfolio Summary (KPI Dashboard)
    "portfolio_kpis": """
        SELECT
            COUNT(*)                                           AS total_loans,
            ROUND(SUM(loan_amount), 0)                        AS total_exposure,
            ROUND(SUM(paid_total), 0)                         AS total_recovered,
            ROUND(SUM(paid_total) * 100.0 / SUM(loan_amount), 2) AS portfolio_recovery_rate_pct,
            ROUND(AVG(int_rate), 2)                           AS avg_interest_rate
        FROM loan_performance;
    """
}

# ---------------------------------------------------------------------------
# 3. EXECUTION ENGINE
# ---------------------------------------------------------------------------

def load_data():
    csv_path = DATA_DIR / "lending_club_openintro.csv"
    if not csv_path.exists():
        print(f"❌ Data file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Column Selection & Simple Cleaning
    cols_to_keep = {
        'loan_amount': 'loan_amount', 'term': 'term', 'interest_rate': 'int_rate',
        'grade': 'grade', 'annual_income': 'annual_inc', 'loan_status': 'loan_status',
        'balance': 'balance', 'paid_total': 'paid_total', 'paid_principal': 'paid_principal',
        'paid_interest': 'paid_interest', 'paid_late_fees': 'paid_late_fees',
        'issue_month': 'issue_month'
    }
    
    # Filter only relevant columns available in this subset
    available_cols = [c for c in cols_to_keep.keys() if c in df.columns]
    df_clean = df[available_cols].rename(columns=cols_to_keep)

    con = sqlite3.connect(DB)
    con.executescript(DDL)
    df_clean.to_sql("loan_performance", con, if_exists="append", index=False)
    con.commit()
    print(f"✅ Lending performance data loaded: {len(df_clean)} records.")
    return con

def run_analytics(con):
    results = {}
    for name, sql in QUERIES.items():
        try:
            df = pd.read_sql_query(sql, con)
            results[name] = df
            print(f"\n📊 {name.upper().replace('_', ' ')}")
            print(df.head(10).to_string(index=False))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
    return results

def plot_visuals(results):
    sns.set_theme(style="darkgrid", palette="pastel")
    fig = plt.figure(figsize=(22, 12), facecolor="#f8f9fa")
    fig.suptitle("Pallav Technologies — Collection Intelligence Dashboard (Real Lending Data)",
                 fontsize=22, fontweight="bold", y=0.98)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)

    # Plot 1: Recovery Rate by Grade
    ax1 = fig.add_subplot(gs[0, 0])
    d1 = results["recovery_metrics_by_grade"]
    sns.barplot(x="grade", y="avg_recovery_rate_pct", data=d1, ax=ax1, palette="coolwarm")
    ax1.set_title("Average Recovery Rate by Loan Grade (%)", fontsize=15)
    ax1.set_ylabel("Recovery Rate (%)")

    # Plot 2: Recovery Volume
    ax2 = fig.add_subplot(gs[0, 1])
    d1_melted = d1.melt(id_vars="grade", value_vars=["total_disbursed", "total_recovered"])
    sns.barplot(x="grade", y="value", hue="variable", data=d1_melted, ax=ax2)
    ax2.set_title("Disbursement vs Recovery Volume (₹)", fontsize=15)
    ax2.set_ylabel("Amount (₹)")

    # Plot 3: Delinquency Queue (Top priority cases)
    ax3 = fig.add_subplot(gs[1, 0])
    d2 = results["collections_priority_queue"]
    sns.barplot(x="priority_score", y="id", data=d2.head(10), ax=ax3, orient='h', palette="flare")
    ax3.set_title("High-Value Delinquency Priority Queue (Top 10 IDs)", fontsize=15)
    ax3.set_xlabel("Priority Score (Balance * Recovery Gap)")

    # Plot 4: KPI Card
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    kpi = results["portfolio_kpis"].iloc[0]
    summary_text = (
        f"  Total Portfolio View     : {int(kpi['total_loans']):,}\n\n"
        f"  Total Exposure           : ₹{int(kpi['total_exposure']):,}\n"
        f"  Total Amount Recovered   : ₹{int(kpi['total_recovered']):,}\n"
        f"  Portfolio Recovery Rate  : {kpi['portfolio_recovery_rate_pct']}%\n"
        f"  Average Interest Rate    : {kpi['avg_interest_rate']}%\n"
    )
    ax4.text(0.1, 0.4, summary_text, fontsize=17, family="monospace",
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="#0d6efd"))
    ax4.set_title("Portfolio Collections KPIs", fontsize=18, fontweight="bold")

    out_path = BASE / "collections_sql_dashboard.png"
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"✅ Collections Dashboard generated: {out_path}")

if __name__ == "__main__":
    connection = load_data()
    if connection:
        analytical_results = run_analytics(connection)
        plot_visuals(analytical_results)
        connection.close()
