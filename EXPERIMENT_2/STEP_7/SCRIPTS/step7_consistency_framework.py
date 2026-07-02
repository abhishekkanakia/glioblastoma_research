import os
import numpy as np
import pandas as pd

# ==========================================
# 1. LOAD DATA ARTIFACTS FROM PREVIOUS STEWS
# ==========================================

# Read Step 3: Multivariable Adjusted Cox Results
step3_path = "../../STEP_3/RESULTS/step3_hazard_ratios_table.csv"
cox_df = pd.read_csv(step3_path)

# Read Step 4: IPTW Causal Inference Results
step4_path = "../../STEP_4/RESULTS/step4_iptw_results_table.csv"
iptw_df = pd.read_csv(step4_path)

# Read Step 6: Machine Learning Random Survival Forest Importances
step6_path = "../../STEP_6/RESULTS/step6_rsf_feature_importances.csv"
rsf_df = pd.read_csv(step6_path)

# ==========================================
# 2. DATA CLEANING AND ALIGNMENT
# ==========================================
# Isolate the multivariable adjusted models from Step 3
cox_adj = cox_df[cox_df["Model_Type"] == "Adjusted (Age+Sex)"].copy()

# Format the base statistics tracker matrix
summary_df = cox_adj[["Biomarker", "HR", "p_value"]].rename(columns={"HR": "Cox_HR", "p_value": "Cox_p"})

# Merge the IPTW causal calculations (will naturally result in NaN for non-targeted genes)
summary_df = summary_df.merge(iptw_df[["Biomarker", "IPTW_Hazard_Ratio", "IPTW_p_value"]], on="Biomarker", how="outer")

# Merge the Random Survival Forest features matrix
summary_df = summary_df.merge(rsf_df, left_on="Biomarker", right_on="Feature", how="outer")

# Correct potential missing string alignments by filling empty biomarkers with their feature label
summary_df["Biomarker"] = summary_df["Biomarker"].fillna(summary_df["Feature"])
summary_df = summary_df.drop(columns=["Feature"]).rename(columns={"Importance_Score": "RSF_VIMP"})

# Filter out standard metadata rows (like AGE or SEX_NUM) to keep the ledger strictly focused on genomic targets
summary_df = summary_df[~summary_df["Biomarker"].isin(["AGE", "SEX_NUM"])]
summary_df = summary_df[summary_df["Biomarker"].notna()]

# ==========================================
# 3. PRODUCTION-GRADE MULTI-PARADIGM TIERING LOGIC
# ==========================================
def assign_confidence_tier(row):
    cox_p = row["Cox_p"]
    iptw_p = row["IPTW_p_value"]
    vimp = row["RSF_VIMP"]
    
    # Handle missing values cleanly for conditional comparison blocks
    has_iptw = not pd.isna(iptw_p)
    
    # Tier 1: Strong Cross-Paradigm Validation (Validated by Classical Stats, Causal Weights, and ML)
    if (cox_p < 0.05) and (vimp >= 0.003) and (not has_iptw or iptw_p < 0.05):
        return "Tier 1: High Confidence Discovery"
        
    # Tier 2: Unmasked Causal or High-Importance Non-Linear Drivers
    # (Catches genes like IDH1/ADAMTS12 that clear causal hurdles, or genes picked up heavily by RSF trees)
    elif (has_iptw and iptw_p < 0.05) or (vimp >= 0.005) or (cox_p < 0.05):
        return "Tier 2: Moderate Confidence Candidate"
        
    # Tier 3: Non-Significant Background Passenger Mutations or Feature Noise
    else:
        return "Tier 3: Low Confidence Background / Passenger"

summary_df["Confidence_Tier"] = summary_df.apply(assign_confidence_tier, axis=1)

# Sort logically by performance tiers (Tier 1 -> Tier 2 -> Tier 3) and sub-sort by ML predictive value
summary_df = summary_df.sort_values(by=["Confidence_Tier", "RSF_VIMP"], ascending=[True, False])

# ==========================================
# 4. PUBLICATION REFORMATTING AND EXPORT
# ==========================================
# Retain numeric precision in a secondary reference frame for calculations, format text view frame
display_df = summary_df.copy()
float_cols = ["Cox_HR", "Cox_p", "IPTW_Hazard_Ratio", "IPTW_p_value", "RSF_VIMP"]

for col in float_cols:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.5f}" if pd.notna(x) and isinstance(x, (int, float)) else "-")

# Save finalized project ledger to disk
summary_df.to_csv("../RESULTS/step7_final_biomarker_ledger.csv", index=False)

print("\n" + "="*95)
print("🎯 STEP 7: FINAL CROSS-PARADIGM CONSISTENCY LEDGER GENERATION COMPLETE")
print("="*95)
print(display_df.to_string(index=False))
print("="*95)
print("\nFinal pipeline execution complete. Results compiled into 'step7_final_biomarker_ledger.csv'.")