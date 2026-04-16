# Loan Collection & Recovery Dashboard

An analytics-driven approach to optimizing Non-Performing Loan (NPL) recovery. This project identifies repayment probabilities and optimizes collection strategies to prioritize high-value delinquent loans.

## Key Features
- **Roll-Rate Analysis**: Visualizes the probability of recovery across different delinquency buckets (1-30 DPD to 90+ DPD).
- **Collection Prioritization**: Segments loans into "Standard", "High Priority", and **"Self-Healers"** to optimize operational spend.
- **Predictive Modeling**: Uses Logistic Regression to estimate recovery chances based on DPD and principal balance.

## Results
- **Accuracy**: 0.77
- **Business Insight**: Identified that recovery drops by over 50% once a loan crosses the 90-day delinquency mark.

## Project Structure
- `recovery_analysis.py`: Main analysis and classification script.
- `collections_data_generator.py`: Synthetic portfolio data generator.
- `loan_collections_data.csv`: Sample delinquency dataset.
- `*.png`: Visualizations of recovery rates and strategy distribution.

---
