import os
import pandas as pd
import numpy as np
from lifelines import CoxPHFitter

# ==========================================
# 1. SETUP AND BASELINE LAYOUT
# ==========================================
# Load the 100 target genes we just discovered
top_100_genes_df = pd.read_csv("top_100_genes_list.csv")
target_genes = top_100_genes_df['Gene'].tolist()

# Load raw mutations to pivot them into patient-specific profiles
raw_mutations_path = "gbm_tcga_pub2013/core_data_subset/data_mutations.txt"
if not os.path.exists(raw_mutations_path):
    raw_mutations_path = "../gbm_tcga_pub2013/core_data_subset/data_mutations.txt"

df_raw = pd.read_csv(raw_mutations_path, sep="\t", comment="#", low_memory=False)
df_raw.columns = [col.strip() for col in df_raw.columns]
df_raw['Clean_Patient_ID'] = df_raw['Tumor_Sample_Barcode'].apply(lambda x: "-".join(str(x).split("-")[:3]))

# Load baseline demographic clinical dataframe from Step 1
# We use this to connect survival metrics (OS_MONTHS, OS_STATUS, AGE, SEX)
df_clinical = pd.read_csv("STEP_1/gbm_merged_data.csv")

if df_clinical['OS_STATUS'].dtype == object:
    df_clinical['E'] = df_clinical['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
else:
    df_clinical['E'] = df_clinical['OS_STATUS'].astype(int)

df_clinical['SEX_NUM'] = df_clinical['SEX'].apply(lambda x: 1 if str(x).upper().startswith('M') else 0)

time_col = 'OS_MONTHS'
event_col = 'E'
covariates = ['AGE', 'SEX_NUM']

print(f"Loaded clinical data for {len(df_clinical)} patients. Reconstructing wide genomic matrix...")

# ==========================================
# 2. DYNAMICALLY BUILD THE 100-GENE PROFILE MATRIX
# ==========================================
# Isolate raw mutations belonging only to our top 100 genes list
df_raw_filtered = df_raw[df_raw['Hugo_Symbol'].isin(target_genes)]

# Create a clean cross-tabulation matrix (Patients as rows, Genes as columns)
# 1 means a mutation exists, 0 means wildtype
genomic_matrix = pd.crosstab(df_raw_filtered['Clean_Patient_ID'], df_raw_filtered['Hugo_Symbol'])
genomic_matrix = (genomic_matrix > 0).astype(int)

# Merge our genomic profiles back into our master clinical tracking matrix
# We match on the patient identifier column
screening_df = df_clinical[['PATIENT_ID', time_col, event_col] + covariates].copy()
screening_df = screening_df.merge(genomic_matrix, left_on='PATIENT_ID', right_index=True, how='left')

# Fill any missing implicit structural gaps with 0 (Wildtype)
screening_df[target_genes] = screening_df[target_genes].fillna(0).astype(int)

# ==========================================
# 3. AUTOMATED MASSIVE SCREENING LOOP
# ==========================================
print(f"Starting automated multi-variable Cox regression screening across all {len(target_genes)} markers...")
screening_records = []

for gene in target_genes:
    # Protect against boundary situations where zero variations exist in this patient slice
    if screening_df[gene].sum() <= 1:
        continue
        
    try:
        # Fit a Cox regression model adjusting for demographics
        cph = CoxPHFitter()
        model_df = screening_df[[time_col, event_col, gene] + covariates]
        cph.fit(model_df, duration_col=time_col, event_col=event_col)
        
        summary = cph.summary.loc[gene]
        
        screening_records.append({
            "Gene": gene,
            "Mutation_Count": int(screening_df[gene].sum()),
            "Adjusted_HR": summary["exp(coef)"],
            "Lower_95": summary["exp(coef) lower 95%"],
            "Upper_95": summary["exp(coef) upper 95%"],
            "p_value": summary["p"]
        })
    except Exception as e:
        # Gracefully handle non-convergence or math limitations for extreme edge profiles
        continue

# Convert data into a structured summary sheet
results_df = pd.DataFrame(screening_records)
results_df = results_df.sort_values(by="p_value")
results_df.to_csv("step6_genome_wide_screening_results.csv", index=False)

# ==========================================
# 4. FILTER AND REVEAL SIGNIFICANT DISCOVERIES
# ==========================================
significant_hits = results_df[results_df["p_value"] < 0.05]

print("\n" + "="*60)
print("🎯 SCREENING RESULTS: POTENTIAL BIOMARKERS IDENTIFIED (p < 0.05)")
print("="*60)
if len(significant_hits) == 0:
    print("No hidden markers crossed the p < 0.05 threshold in this cohort slice.")
else:
    print(significant_hits.to_string(index=False))
print("="*60)

print(f"\nAll results compiled smoothly and exported to 'step6_genome_wide_screening_results.csv'!")