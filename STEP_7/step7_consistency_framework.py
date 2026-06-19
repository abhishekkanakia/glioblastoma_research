import pandas as pd
import numpy as np

# Load individual data summaries from past steps
try:
    cox_df = pd.read_csv("../STEP_3/step3_hazard_ratios_table.csv")
    iptw_df = pd.read_csv("../STEP_4/step4_iptw_results_table.csv")
except FileNotFoundError:
    # Backup path check
    cox_df = pd.read_csv("step3_hazard_ratios_table.csv")
    iptw_df = pd.read_csv("step4_iptw_results_table.csv")

rsf_df = pd.read_csv("../STEP_6/step6_rsf_feature_importances.csv")

# Filter Cox to just our adjusted metrics
cox_adj = cox_df[cox_df["Model_Type"] == "Adjusted (Age+Sex)"].copy()

# Merge metrics together into a unified tracking matrix
summary_df = cox_adj[["Biomarker", "HR", "p_value"]].rename(columns={"HR": "Cox_HR", "p_value": "Cox_p"})
summary_df = summary_df.merge(iptw_df[["Biomarker", "IPTW_Hazard_Ratio", "IPTW_p_value"]], on="Biomarker", how="outer")
summary_df = summary_df.merge(rsf_df, left_on="Biomarker", right_on="Feature", how="outer")

# FIX THE NaN NAMES: If Biomarker is empty, fill it with the Feature name from the Random Forest
summary_df["Biomarker"] = summary_df["Biomarker"].fillna(summary_df["Feature"])
summary_df = summary_df.drop(columns=["Feature"]).rename(columns={"Importance_Score": "RSF_VIMP"})

# Drop rows for metadata rows we don't care to rank
summary_df = summary_df[summary_df["Biomarker"].notna()]

# Define a clean, robust confidence tiering system based on your full experiment tracking
def assign_confidence_tier(row):
    # Tier 1: Consistent significance or high importance across all paradigms
    if (row["Cox_p"] < 0.05 or row["IPTW_p_value"] < 0.05) and row["RSF_VIMP"] > 0.01:
        return "Tier 1: High Confidence"
    # Tier 2: Strong signal in ML/Causal but misses traditional linear thresholds
    elif row["IPTW_p_value"] < 0.05 or row["RSF_VIMP"] > 0.001:
        return "Tier 2: Moderate Confidence"
    # Tier 3: Unstable or sparse boundary signal
    else:
        return "Tier 3: Low Confidence / Outlier"

summary_df["Confidence_Tier"] = summary_df.apply(assign_confidence_tier, axis=1)

# Sort logically by performance tier
summary_df = summary_df.sort_values(by="Confidence_Tier")

# Clean up floats for publication-grade viewing
float_cols = ["Cox_HR", "Cox_p", "IPTW_Hazard_Ratio", "IPTW_p_value", "RSF_VIMP"]
summary_df[float_cols] = summary_df[float_cols].round(4)
summary_df = summary_df.fillna("-")

# Export final project ledger
summary_df.to_csv("step7_final_biomarker_ledger.csv", index=False)

print("\n" + "="*85)
print("🎯 STEP 7: FINAL CONFIDENCE-ENHANCED CONSISTENCY LEDGER")
print("="*85)
print(summary_df.to_string(index=False))
print("="*85)