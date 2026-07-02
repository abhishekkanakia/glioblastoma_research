import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import CoxPHFitter
import statsmodels.api as sm

# ==========================================
# 1. SETUP AND DATA PREPARATION
# ==========================================
df = pd.read_csv("../STEP_1/gbm_merged_data.csv")

# Ensure clean binary mapping for survival event indicator
if df['OS_STATUS'].dtype == object:
    df['E'] = df['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
else:
    df['E'] = df['OS_STATUS'].astype(int)

# Map categorical Sex to binary numeric indicator (Male=1, Female=0)
df['SEX_NUM'] = df['SEX'].apply(lambda x: 1 if str(x).upper().startswith('M') else 0)

time_col = 'OS_MONTHS'
event_col = 'E'
features = ['AGE', 'SEX_NUM']
# Isolate primary analytical targets that demonstrated original signals
target_genes = ["EGFR", "IDH1"]

os.makedirs("propensity_plots", exist_ok=True)
iptw_records = []

print("=== STEP 4: RUNNING PROPENSITY SCORE ENHANCED ANALYSIS (IPTW) ===")

# Helper function to calculate Standardized Mean Difference (SMD)
def calculate_smd(data, variable, treatment_col, weight_col=None):
    treated = data[data[treatment_col] == 1]
    untreated = data[data[treatment_col] == 0]
    
    if weight_col is None:
        m1, m0 = treated[variable].mean(), untreated[variable].mean()
        v1, v0 = treated[variable].var(), untreated[variable].var()
    else:
        # Calculate weighted means and variances manually using numpy
        m1 = np.average(treated[variable], weights=treated[weight_col])
        m0 = np.average(untreated[variable], weights=untreated[weight_col])
        v1 = np.average((treated[variable] - m1)**2, weights=treated[weight_col])
        v0 = np.average((untreated[variable] - m0)**2, weights=untreated[weight_col])
        
    smd = np.abs(m1 - m0) / np.sqrt((v1 + v0) / 2)
    return smd

# ==========================================
# 2. CAUSAL PIPELINE LOOP
# ==========================================
for gene in target_genes:
    print(f"\n--- Processing Causal Balance for: {gene} ---")
    
    # Copy working dataframe slice to prevent warnings
    working_df = df[[time_col, event_col, gene] + features].copy()
    
    # Step 4.1: Logistic Regression to estimate propensity scores
    X = sm.add_constant(working_df[features])
    y = working_df[gene]
    logistic_model = sm.Logit(y, X).fit(disp=0)
    working_df['propensity_score'] = logistic_model.predict(X)
    
    # Step 4.2: Compute IPTW stabilized weights
    working_df['iptw_weight'] = working_df.apply(
        lambda row: 1.0 / row['propensity_score'] if row[gene] == 1 
        else 1.0 / (1.0 - row['propensity_score']), axis=1
    )
    
    # Cap weights at the 99th percentile to prevent extreme outlier variance inflation
    max_weight = working_df['iptw_weight'].quantile(0.99)
    working_df['iptw_weight'] = working_df['iptw_weight'].clip(upper=max_weight)
    
    # Step 4.3: Evaluate demographic balance improvements via SMD
    for feat in features:
        smd_raw = calculate_smd(working_df, feat, gene, weight_col=None)
        smd_weighted = calculate_smd(working_df, feat, gene, weight_col='iptw_weight')
        print(f"  {feat:8s} Balance -> Raw SMD: {smd_raw:.4f} | Weighted IPTW SMD: {smd_weighted:.4f}")
    
    # Step 4.4: Generate Propensity Score Overlap Distribution Plot
    plt.figure(figsize=(8, 5))
    sns.kdeplot(data=working_df[working_df[gene] == 1], x='propensity_score', label='Mutated', fill=True, color='#d62728', alpha=0.4)
    sns.kdeplot(data=working_df[working_df[gene] == 0], x='propensity_score', label='Wildtype', fill=True, color='#1f77b4', alpha=0.4)
    plt.title(f"Propensity Score Overlap/Common Support: {gene}", fontsize=12, fontweight='bold')
    plt.xlabel("Estimated Propensity Score $P(\mu \mid X)$", fontsize=11)
    plt.ylabel("Density", fontsize=11)
    plt.legend(frameon=True)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"propensity_plots/{gene}_overlap_plot.png", dpi=300)
    plt.close()
    
    # Step 4.5: Fit Weighted Cox Proportional Hazards Model
    # Passing the calculated IPTW column straight into lifelines' weights framework
    cph_weighted = CoxPHFitter()
    weighted_df_slice = working_df[[time_col, event_col, gene, 'iptw_weight']]
    cph_weighted.fit(weighted_df_slice, duration_col=time_col, event_col=event_col, weights_col='iptw_weight', robust = True)
    
    summary_matrix = cph_weighted.summary.loc[gene]
    
    iptw_records.append({   
        "Biomarker": gene,
        "IPTW_Hazard_Ratio": summary_matrix["exp(coef)"],
        "Lower_95": summary_matrix["exp(coef) lower 95%"],
        "Upper_95": summary_matrix["exp(coef) upper 95%"],
        "IPTW_p_value": summary_matrix["p"]
    })

# Format results display table
iptw_results_df = pd.DataFrame(iptw_records)
iptw_results_df.to_csv("step4_iptw_results_table.csv", index=False)

print("\n=== FINAL COGNIZANT IPTW WEIGHTED SURVIVAL OUTCOMES ===")
print(iptw_results_df.to_string(index=False))