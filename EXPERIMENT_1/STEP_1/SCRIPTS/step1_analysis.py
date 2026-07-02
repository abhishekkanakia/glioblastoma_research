import pandas as pd
import numpy as np

# loading csv
df = pd.read_csv("gbm_merged_data.csv")

print("=== TABLE 1: COHORT CHARACTERISTICS ===")
total_patients = len(df)
print(f"Total Analytical Cohort (N) = {total_patients}\n")

# 1. Age characteristics
mean_age = df['AGE'].mean()
std_age = df['AGE'].std()
print(f"Age (Years): {mean_age:.1f} ± {std_age:.1f}")

# 2. gender distribution
if 'SEX' in df.columns:
    sex_counts = df['SEX'].value_counts()
    for sex, count in sex_counts.items():
        percentage = (count / total_patients) * 100
        print(f"Sex - {sex}: {count} ({percentage:.1f}%)")

# 3. MISSINGNESS (e.g., MGMT Status)
mgmt_column = [col for col in df.columns if 'MGMT' in col.upper()]
if mgmt_column:
    col_name = mgmt_column[0]
    missing_mgmt = df[col_name].isna().sum()
    missing_pct = (missing_mgmt / total_patients) * 100
    print(f"Missing MGMT Status: {missing_mgmt} ({missing_pct:.1f}%)")
else:
    print("MGMT Status column not found in this clinical tier spreadsheet.")