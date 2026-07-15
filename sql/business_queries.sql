-- ============================================================
-- Loan Risk Analysis — Business Queries
-- Database: loan_risk_analysis | Table: loans
-- Dataset: 255,347 retail loan records | Overall default rate: 11.61%
-- ============================================================

-- Query 1: Overall Default Rate
-- Result: 255,347 total loans | 29,653 defaults | 11.61% default rate
SELECT 
    COUNT(*) AS total_loans,
    SUM(Default_Flag) AS total_defaults,
    ROUND(SUM(Default_Flag) * 100.0 / COUNT(*), 2) AS default_rate_pct
FROM loans;


-- Query 2: Default Rate by Employment Type
-- Result: Unemployed (13.55%) > Part-time (11.97%) > Self-employed (11.46%) > Full-time (9.46%)
SELECT 
    EmploymentType,
    COUNT(*) AS total_loans,
    SUM(Default_Flag) AS defaults,
    ROUND(SUM(Default_Flag) * 100.0 / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY EmploymentType
ORDER BY default_rate_pct DESC;


-- Query 3: Default Rate by Income Bracket
-- Result: Below 30K (21.96%) is nearly 2.4x riskier than Above 100K (9.10%)
-- Insight: Income is the strongest single predictor of default in this dataset
SELECT 
    CASE 
        WHEN Income < 30000 THEN 'Below 30K'
        WHEN Income BETWEEN 30000 AND 60000 THEN '30K-60K'
        WHEN Income BETWEEN 60001 AND 100000 THEN '60K-100K'
        ELSE 'Above 100K'
    END AS income_bracket,
    COUNT(*) AS total_loans,
    ROUND(SUM(Default_Flag) * 100.0 / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY income_bracket
ORDER BY default_rate_pct DESC;


-- Query 4: Default Rate by DTI (Debt-to-Income) Ratio Bucket
-- Result: High (12.02%) vs Low (10.36%) — only a ~1.15x spread
-- Insight: Weaker signal than expected; DTI alone is not a strong differentiator here
SELECT 
    CASE 
        WHEN DTIRatio < 0.2 THEN 'Low (<0.2)'
        WHEN DTIRatio BETWEEN 0.2 AND 0.4 THEN 'Medium (0.2-0.4)'
        ELSE 'High (>0.4)'
    END AS dti_bucket,
    COUNT(*) AS total_loans,
    ROUND(SUM(Default_Flag) * 100.0 / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY dti_bucket
ORDER BY default_rate_pct DESC;


-- Query 5: Default Rate by Credit Score Bucket
-- Result: Poor (12.47%) vs Excellent (10.18%) — only a ~1.2x spread
-- Insight: Similarly weak signal; credit score alone underperforms as a sole risk indicator here
SELECT 
    CASE 
        WHEN CreditScore < 580 THEN 'Poor (<580)'
        WHEN CreditScore BETWEEN 580 AND 669 THEN 'Fair (580-669)'
        WHEN CreditScore BETWEEN 670 AND 739 THEN 'Good (670-739)'
        ELSE 'Excellent (740+)'
    END AS credit_bucket,
    COUNT(*) AS total_loans,
    ROUND(SUM(Default_Flag) * 100.0 / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY credit_bucket
ORDER BY default_rate_pct DESC;

-- ============================================================
-- KEY TAKEAWAY FOR RISK SCORING MODEL (feeds into Python step):
-- Income and Employment Type show the strongest gradients and should be
-- weighted more heavily than DTI Ratio and Credit Score when building
-- a rule-based risk score for this dataset.
-- ============================================================
