import pandas as pd
import numpy as np

patient_df = pd.read_csv("../../gbm_merged_data.csv") 

# 2. Load your top 100 discovery gene list to pass to downstream steps
genes_df = pd.read_csv("../../top_100_genes_list.csv")
gene_list = genes_df["Gene"].tolist()

print("=== TABLE 1: COHORT CHARACTERISTICS ===")
total_patients = len(patient_df)
print(f"Total Analytical Cohort (N) = {total_patients}\n")

# 1. Age characteristics (calculated across the real patients)
if 'AGE' in patient_df.columns:
    mean_age = patient_df['AGE'].mean()
    std_age = patient_df['AGE'].std()
    print(f"Age (Years): {mean_age:.1f} ± {std_age:.1f}")
else:
    print("Error: 'AGE' column not found in patient dataset.")

# 2. Gender distribution
if 'SEX' in patient_df.columns:
    sex_counts = patient_df['SEX'].value_counts()
    for sex, count in sex_counts.items():
        percentage = (count / total_patients) * 100
        print(f"Sex - {sex}: {count} ({percentage:.1f}%)")

# 3. Missingness (e.g., MGMT Status)
mgmt_column = [col for col in patient_df.columns if 'MGMT' in col.upper()]
if mgmt_column:
    col_name = mgmt_column[0]
    missing_mgmt = patient_df[col_name].isna().sum()
    missing_pct = (missing_mgmt / total_patients) * 100
    print(f"Missing MGMT Status: {missing_mgmt} ({missing_pct:.1f}%)")
else:
    print("MGMT Status column not found in this clinical tier spreadsheet.")