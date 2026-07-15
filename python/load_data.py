import pandas as pd
import pymysql
import time

print("Reading CSV...")
df = pd.read_csv(r"C:\Users\AKASH SINGH\Downloads\Loan_default.csv")
print(f"Loaded {len(df)} rows from CSV")

df.rename(columns={'Default': 'Default_Flag'}, inplace=True)

# Connect directly with pymysql
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Rajput@0007',
    database='loan_risk_analysis'
)
cursor = conn.cursor()

# Convert dataframe to list of tuples for bulk insert
data = [tuple(row) for row in df.itertuples(index=False)]

insert_query = """
INSERT INTO loans 
(LoanID, Age, Income, LoanAmount, CreditScore, MonthsEmployed, NumCreditLines,
 InterestRate, LoanTerm, DTIRatio, Education, EmploymentType, MaritalStatus,
 HasMortgage, HasDependents, LoanPurpose, HasCoSigner, Default_Flag)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

print("Loading into MySQL... this may take 1-3 minutes, please wait")
start = time.time()

batch_size = 5000
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    cursor.executemany(insert_query, batch)
    conn.commit()
    print(f"Inserted {min(i+batch_size, len(data))} / {len(data)} rows...")

end = time.time()
print(f"Done! Loaded {len(data)} rows in {round(end-start, 1)} seconds")

cursor.close()
conn.close()