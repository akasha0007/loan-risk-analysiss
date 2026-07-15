import pandas as pd
import pymysql

# ============================================================
# STEP 1: Connect to MySQL and pull the data
# ============================================================
print("Connecting to MySQL and fetching data...")

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Rajput@0007',
    database='loan_risk_analysis'
)

df = pd.read_sql("SELECT * FROM loans", conn)
print(f"Loaded {len(df)} rows from MySQL")

# ============================================================
# STEP 2: Feature Engineering
# ============================================================
print("Engineering features...")

# Loan-to-Income ratio: how big is the loan relative to what they earn
df['LoanToIncomeRatio'] = df['LoanAmount'] / df['Income']

# Flag: is this a low-income applicant (below 30K, our riskiest SQL bucket)
df['LowIncomeFlag'] = (df['Income'] < 30000).astype(int)

# Flag: is this applicant unemployed (riskiest employment type from SQL)
df['UnemployedFlag'] = (df['EmploymentType'] == 'Unemployed').astype(int)

# Flag: high DTI ratio (weaker signal, but still relevant)
df['HighDTIFlag'] = (df['DTIRatio'] > 0.4).astype(int)

# Flag: poor credit score (weaker signal, but still relevant)
df['PoorCreditFlag'] = (df['CreditScore'] < 580).astype(int)

# ============================================================
# STEP 3: Weighted Risk Score
# Weights are based on ACTUAL default rate spread from our SQL analysis:
#   - Income showed the strongest spread (21.96% vs 9.10%)   -> weight 0.40
#   - Employment Type showed moderate spread (13.55% vs 9.46%) -> weight 0.30
#   - DTI Ratio showed weak spread (12.02% vs 10.36%)          -> weight 0.15
#   - Credit Score showed weak spread (12.47% vs 10.18%)       -> weight 0.15
# ============================================================
print("Calculating risk scores...")

df['RiskScore'] = (
    df['LowIncomeFlag']   * 0.40 +
    df['UnemployedFlag']  * 0.30 +
    df['HighDTIFlag']     * 0.15 +
    df['PoorCreditFlag']  * 0.15
)

# Convert score (0 to 1) into Low / Medium / High risk buckets
def classify_risk(score):
    if score >= 0.55:
        return 'High'
    elif score >= 0.25:
        return 'Medium'
    else:
        return 'Low'

df['RiskCategory'] = df['RiskScore'].apply(classify_risk)

# ============================================================
# STEP 4: Validate — does our risk score actually work?
# ============================================================
print("\n--- VALIDATION: Default rate by Risk Category ---")
validation = df.groupby('RiskCategory')['Default_Flag'].agg(['count', 'mean'])
validation['default_rate_pct'] = round(validation['mean'] * 100, 2)
print(validation[['count', 'default_rate_pct']])

# ============================================================
# STEP 5: Save results back to MySQL (for Power BI later)
# ============================================================
print("\nSaving results to MySQL...")

cursor = conn.cursor()

# Create a new table for risk-scored results
cursor.execute("DROP TABLE IF EXISTS loan_risk_scores")
cursor.execute("""
    CREATE TABLE loan_risk_scores (
        LoanID VARCHAR(20) PRIMARY KEY,
        Age INT,
        Income INT,
        LoanAmount INT,
        CreditScore INT,
        EmploymentType VARCHAR(30),
        DTIRatio FLOAT,
        LoanToIncomeRatio FLOAT,
        RiskScore FLOAT,
        RiskCategory VARCHAR(10),
        Default_Flag INT
    )
""")

# Prepare data for insert
insert_data = df[['LoanID', 'Age', 'Income', 'LoanAmount', 'CreditScore',
                   'EmploymentType', 'DTIRatio', 'LoanToIncomeRatio',
                   'RiskScore', 'RiskCategory', 'Default_Flag']].values.tolist()

insert_query = """
    INSERT INTO loan_risk_scores 
    (LoanID, Age, Income, LoanAmount, CreditScore, EmploymentType, 
     DTIRatio, LoanToIncomeRatio, RiskScore, RiskCategory, Default_Flag)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

batch_size = 5000
for i in range(0, len(insert_data), batch_size):
    batch = insert_data[i:i+batch_size]
    cursor.executemany(insert_query, batch)
    conn.commit()
    print(f"Saved {min(i+batch_size, len(insert_data))} / {len(insert_data)} rows...")

print("\nDone! Risk scoring complete and saved to 'loan_risk_scores' table.")

# Also save a local CSV copy (useful backup, and for Excel/GitHub if needed)
df.to_csv('risk_scored_loans.csv', index=False)
print("Also saved a local copy: risk_scored_loans.csv")

cursor.close()
conn.close()