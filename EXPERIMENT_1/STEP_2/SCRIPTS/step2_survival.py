import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# ==========================================
# 1. SETUP AND DATA LOADING
# ==========================================
# Read the cleaned data created in Step 1
data_path = "../STEP_1/gbm_merged_data.csv"
df = pd.read_csv(data_path)

# Ensure our event indicator is mapped to clean binaries for lifelines
if df['OS_STATUS'].dtype == object:
    df['E'] = df['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
else:
    df['E'] = df['OS_STATUS'].astype(int)

# Set up tracking arrays
time_col = 'OS_MONTHS'
event_col = 'E'
target_genes = ["EGFR", "TP53", "IDH1", "BRAF", "TERT", "ATRX", "IDH2"]

# Ensure output directory for plots exists
output_dir = "survival_plots"
os.makedirs(output_dir, exist_ok=True)

# Container to build our final summary table
summary_records = []

print("=== STEP 2: RUNNING KAPLAN-MEIER SURVIVAL PIPELINE ===")

# ==========================================
# 2. LOOP THROUGH TARGET BIOMARKERS
# ==========================================
for gene in target_genes:
    # Skip processing if the gene completely lacks mutations in this cohort slice
    if df[gene].sum() == 0:
        print(f"Skipping {gene}: No mutated cases found in this cohort.")
        continue
        
    # Split cohorts into Mutated (1) vs Wildtype (0)
    mut_mask = (df[gene] == 1)
    wt_mask = (df[gene] == 0)
    
    df_mut = df[mut_mask]
    df_wt = df[wt_mask]
    
    # Initialize separate fitters
    kmf_mut = KaplanMeierFitter()
    kmf_wt = KaplanMeierFitter()
    
    # Fit the survival models
    kmf_mut.fit(durations=df_mut[time_col], event_observed=df_mut[event_col], label=f"{gene} Mutated")
    kmf_wt.fit(durations=df_wt[time_col], event_observed=df_wt[event_col], label=f"{gene} Wildtype")
    
    # Extract median survival times
    median_mut = kmf_mut.median_survival_time_
    median_wt = kmf_wt.median_survival_time_
    
    # Execute the log-rank statistical test
    lr_results = logrank_test(
        durations_A=df_mut[time_col], durations_B=df_wt[time_col],
        event_observed_A=df_mut[event_col], event_observed_B=df_wt[event_col]
    )
    p_value = lr_results.p_value
    
    # Store calculations for the final reporting array
    summary_records.append({
        "Biomarker": gene,
        "Mutated_N": len(df_mut),
        "Mutated_Median_OS": f"{median_mut:.1f}" if pd.notna(median_mut) else "N/A",
        "Wildtype_N": len(df_wt),
        "Wildtype_Median_OS": f"{median_wt:.1f}" if pd.notna(median_wt) else "N/A",
        "LogRank_p_value": f"{p_value:.4f}"
    })
    
    # ==========================================
    # 3. GENERATE AND FORMAT KM PLOT
    # ==========================================
    plt.figure(figsize=(9, 6))
    
    # Plot curves with shaded 95% confidence intervals
    kmf_wt.plot_survival_function(color="#1f77b4", linewidth=2.5, linestyle="-")
    kmf_mut.plot_survival_function(color="#d62728", linewidth=2.5, linestyle="-")
    
    # Add clear text notations for statistics directly onto the chart image
    stats_text = f"Log-Rank p-value: {p_value:.4f}\n" \
                 f"Mutant Median OS: {median_mut:.1f} mo (N={len(df_mut)})\n" \
                 f"Wildtype Median OS: {median_wt:.1f} mo (N={len(df_wt)})"
    
    plt.gca().text(0.05, 0.05, stats_text, transform=plt.gca().transAxes,
                   bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'), fontsize=10)
    
    plt.title(f"Kaplan-Meier Overall Survival Function: {gene} Stratification", fontsize=13, fontweight='bold')
    plt.xlabel("Timeline (Months)", fontsize=11)
    plt.ylabel("Overall Survival Probability $S(t)$", fontsize=11)
    plt.ylim(0, 1.02)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    
    # Save chart asset
    plt.savefig(f"{output_dir}/{gene}_survival_curve.png", dpi=300)
    plt.close()
    print(f"Processed {gene} -> Saved plot to {output_dir}/{gene}_survival_curve.png")

# ==========================================
# 4. EXPORT SUMMARY AGGREGATION
# ==========================================
summary_df = pd.DataFrame(summary_records)
summary_df.to_csv("step2_survival_summary_table.csv", index=False)

print("\n=== STEP 2 DATA PROCESS SUMMARY ===")
print(summary_df.to_string(index=False))