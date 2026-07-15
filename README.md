Loan Risk Analysis — Retail Lending Portfolio
A rule-based credit risk scoring project analyzing 255,000+ retail loan records, built using SQL, Python, and Power BI. Designed to mirror how a bank's risk/credit analytics team evaluates loan applicant risk.
[Dashboard Preview] ( power bi/dashboard_preview.png )
Problem Statement
Banks lose significant value each year to loan defaults. This project analyzes a retail loan portfolio to identify which borrower characteristics are the strongest predictors of default, and builds a transparent, explainable risk-scoring framework to flag high-risk applicants before loans are approved.
Tools Used
SQL (MySQL) — data storage, business query analysis
Python (pandas, pymysql) — feature engineering, rule-based risk scoring
Power BI — interactive risk-monitoring dashboard
Dataset
Source: Loan Default Prediction Dataset — Kaggle
Size: 255,347 loan records, 18 columns
Target variable: `Default` (1 = defaulted, 0 = did not default)
Overall default rate: 11.61%
Methodology
1. Data Engineering (SQL)
Loaded the dataset into MySQL and wrote business queries to analyze default rate across key segments: employment type, income bracket, DTI ratio, and credit score. Full queries in `sql/business_queries.sql`.
Key finding: Income showed the strongest relationship with default risk (a 2.4x spread between the lowest and highest income brackets), notably outperforming DTI ratio and credit score (~1.15–1.2x spread) — the two metrics traditionally treated as primary risk indicators. This counter-intuitive result directly shaped how the risk model was weighted.
Segment	Riskiest Group	Safest Group	Spread
Income	Below 30K (21.96%)	Above 100K (9.10%)	2.4x
Employment Type	Unemployed (13.55%)	Full-time (9.46%)	1.4x
DTI Ratio	High (12.02%)	Low (10.36%)	1.15x
Credit Score	Poor (12.47%)	Excellent (10.18%)	1.2x
2. Risk Scoring (Python)
Rather than a black-box ML model, this project uses a transparent, rule-based weighted risk score — a technique credit teams often prefer because every decision is fully explainable. Weights were derived directly from the SQL analysis above (heavier weight on Income and Employment Type, lighter weight on DTI and Credit Score).
Each loan is scored using engineered flags (low income, unemployment, high DTI, poor credit) and classified into Low / Medium / High risk. Full script in `python/risk_scoring.py`.
3. Validation
The risk score was validated against actual default outcomes:
Risk Category	Total Loans	Actual Default Rate
High	42,275	18.64%
Medium	96,546	11.41%
Low	116,526	9.23%
High-risk loans default at ~2x the rate of low-risk loans — confirming the scoring logic effectively separates risky borrowers from safe ones, without using any machine learning.
A deeper cross-segment cut revealed an even sharper split: High-risk + Part-time borrowers default at 23.28%, compared to just 7.99% for Low-risk + Full-time borrowers — a ~3x spread, showing the model captures compounding risk across multiple factors.
4. Dashboard (Power BI)
An interactive dashboard visualizes overall portfolio health, risk distribution, and segment-level default rates. See `powerbi/` for the `.pbix` file and a static preview image.
Key Business Insight
Traditional credit risk assumptions prioritize DTI ratio and credit score. In this dataset, income and employment stability were far stronger differentiators of default risk — a finding with real implications for how underwriting criteria might be prioritized.
Repository Structure
```
loan-risk-analysis/
├── data/                     # Raw dataset
├── sql/
│   └── business_queries.sql  # 5 business queries with documented insights
├── python/
│   └── risk_scoring.py       # Feature engineering + risk scoring logic
├── powerbi/
│   ├── Loan_Risk_Dashboard.pbix
│   └── dashboard_preview.png
└── README.md
```
How to Reproduce
Load `data/Loan_default.csv` into MySQL using the schema in `sql/business_queries.sql`
Run `python/risk_scoring.py` to generate risk scores (update DB credentials first)
Open `powerbi/Loan_Risk_Dashboard.pbix` in Power BI Desktop, refresh the data connection
Author
Akash Singh
