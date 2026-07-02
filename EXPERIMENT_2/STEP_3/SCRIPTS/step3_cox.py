import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from lifelines import CoxPHFitter

# ==========================================
# 1. SETUP AND DATA PREPARATION
# ==========================================
# Read the cleaned data created in Step 1
df = pd.read_csv("../../gbm_merged_data.csv")

# Safely map event status string markers to clean binaries
if df['OS_STATUS'].dtype == object:
    df['E'] = df['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
else:
    df['E'] = df['OS_STATUS'].astype(int)

# Map categorical Sex to a binary numerical column for regression (Male=1, Female=0)
df['SEX_NUM'] = df['SEX'].apply(lambda x: 1 if str(x).upper().startswith('M') else 0)

# Establish target metrics
time_col = 'OS_MONTHS'
event_col = 'E'
covariates = ['AGE', 'SEX_NUM']
# Exclude anything that is not significant.
target_genes = ["STAG2", "IDH1", "DNAH2", "PCLO", "CALN1", "DSP", "DNAH8", "FGD5", "TEX15", "TAF1L", "ADAMTS12"]

cox_records = []

print("=== STEP 3: EXECUTING ADJUSTED COX PH MODELS ===")

# ==========================================
# 2. MODEL FITTING LOOP
# ==========================================
for gene in target_genes:
    # --- A. UNADJUSTED MODEL ---
    cph_unadj = CoxPHFitter()
    unadj_df = df[[time_col, event_col, gene]]
    cph_unadj.fit(unadj_df, duration_col=time_col, event_col=event_col)
    
    # Extract stats summary matrices
    summary_unadj = cph_unadj.summary.loc[gene]
    
    # --- B. ADJUSTED MODEL (Age + Sex Covariates) ---
    cph_adj = CoxPHFitter()
    adj_df = df[[time_col, event_col, gene] + covariates]
    cph_adj.fit(adj_df, duration_col=time_col, event_col=event_col)
    
    summary_adj = cph_adj.summary.loc[gene]
    
    # Save statistics records
    cox_records.append({
        "Biomarker": gene,
        "Model_Type": "Unadjusted",
        "HR": summary_unadj["exp(coef)"],
        "Lower_95": summary_unadj["exp(coef) lower 95%"],
        "Upper_95": summary_unadj["exp(coef) upper 95%"],
        "p_value": summary_unadj["p"]
    })
    
    cox_records.append({
        "Biomarker": gene,
        "Model_Type": "Adjusted (Age+Sex)",
        "HR": summary_adj["exp(coef)"],
        "Lower_95": summary_adj["exp(coef) lower 95%"],
        "Upper_95": summary_adj["exp(coef) upper 95%"],
        "p_value": summary_adj["p"]
    })

# Convert records to structured summary DataFrame
cox_results_df = pd.DataFrame(cox_records)
cox_results_df.to_csv("../RESULTS/step3_hazard_ratios_table.csv", index=False)

print("\n=== EXPONENTIATED HAZARD RATIOS AND REGRESSION RESULTS ===")
print(cox_results_df.to_string(index=False))

# ==========================================
# 3. GENERATING MASTER REGRESSION FOREST PLOT
# ==========================================
plt.figure(figsize=(10, 6))

# Separate the dataset groups to plot them with visual offset distinction
adj_data = cox_results_df[cox_results_df["Model_Type"] == "Adjusted (Age+Sex)"].copy()
unadj_data = cox_results_df[cox_results_df["Model_Type"] == "Unadjusted"].copy()

y_positions = np.arange(len(target_genes))
offset = 0.15

# Plot Unadjusted tracking points and error bands
plt.errorbar(
    x=unadj_data["HR"], y=y_positions + offset,
    xerr=[unadj_data["HR"] - unadj_data["Lower_95"], unadj_data["Upper_95"] - unadj_data["HR"]],
    fmt='o', color='#d62728', elinewidth=2, capsize=4, label='Unadjusted HR'
)

# Plot Adjusted tracking points and error bands
plt.errorbar(
    x=adj_data["HR"], y=y_positions - offset,
    xerr=[adj_data["HR"] - adj_data["Lower_95"], adj_data["Upper_95"] - adj_data["HR"]],
    fmt='s', color='#1f77b4', elinewidth=2, capsize=4, label='Adjusted HR (Age + Sex Adjusted)'
)

# Draw reference benchmark intercept marker line representing absolute null hazard effect (HR = 1.0)
plt.axvline(x=1.0, color='black', linestyle='--', linewidth=1.2, alpha=0.7)

# Format visual plotting window bounds
plt.yticks(y_positions, target_genes, fontsize=11, fontweight='bold')
plt.xlabel("Hazard Ratio (HR) with 95% Confidence Intervals", fontsize=12)
plt.title("Forest Plot: Impact of Genomic Alterations on Overall Survival", fontsize=14, fontweight='bold')
plt.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='gray')
plt.grid(True, linestyle=':', alpha=0.6)
plt.gca().invert_yaxis()  # Keeps genes ordered from top down uniform with script array

plt.tight_layout()
plt.savefig("../RESULTS/cox_survival_forest_plot.png", dpi=300)
plt.show()

print("\nStep 3 Forest Plot successfully compiled and saved to cox_survival_forest_plot.png!")