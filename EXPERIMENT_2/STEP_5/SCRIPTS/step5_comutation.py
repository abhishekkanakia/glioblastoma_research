import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter

# ==========================================
# 1. DATA SETUP
# ==========================================
df = pd.read_csv("../../gbm_merged_data.csv")

if df['OS_STATUS'].dtype == object:
    df['E'] = df['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
else:
    df['E'] = df['OS_STATUS'].astype(int)

df['SEX_NUM'] = df['SEX'].apply(lambda x: 1 if str(x).upper().startswith('M') else 0)

time_col = 'OS_MONTHS'
event_col = 'E'
covariates = ['AGE', 'SEX_NUM']

# Define the 4 target co-mutation pairs requested by the protocol
comut_pairs = [
    ("PTEN", "EGFR"),
    ("TP53", "STAG2"),
    ("TP53", "IDH1"),
    ("TTN", "TEX15")
]

os.makedirs("../RESULTS/comutation_plots", exist_ok=True)
comut_records = []

print("=== STEP 5: RUNNING CO-MUTATION STRATIFICATION ANALYSIS ===")

# ==========================================
# 2. ANALYSIS LOOP
# ==========================================
for geneA, geneB in comut_pairs:
    print(f"\n--- Analyzing Interaction Pair: {geneA} + {geneB} ---")
    
    # Create a temporary labeling column for the 4-way split
    def assign_group(row):
        if row[geneA] == 0 and row[geneB] == 0: return "Neither"
        elif row[geneA] == 1 and row[geneB] == 0: return f"{geneA} Only"
        elif row[geneA] == 0 and row[geneB] == 1: return f"{geneB} Only"
        else: return "Both"

    pair_col_name = f"{geneA}_{geneB}_group"
    df[pair_col_name] = df.apply(assign_group, axis=1)
    
    # Check group sample sizes
    counts = df[pair_col_name].value_counts()
    print("  Group sizes:\n", counts.to_string())
    
    # If a group has 0 patients, we can still plot, but let's log it
    if "Both" not in counts:
        print(f"  Warning: No patients harbor the dual co-mutation for {geneA}+{geneB}.")

    # --- A. PLOT 4-GROUP KAPLAN-MEIER CURVES ---
    plt.figure(figsize=(10, 6))
    colors = {"Neither": "#2ca02c", f"{geneA} Only": "#ff7f0e", f"{geneB} Only": "#1f77b4", "Both": "#d62728"}
    
    km_plotted = 0
    for group_label in ["Neither", f"{geneA} Only", f"{geneB} Only", "Both"]:
        sub_df = df[df[pair_col_name] == group_label]
        if len(sub_df) == 0:
            continue
            
        kmf = KaplanMeierFitter()
        kmf.fit(durations=sub_df[time_col], event_observed=sub_df[event_col], label=f"{group_label} (N={len(sub_df)})")
        kmf.plot_survival_function(color=colors[group_label], linewidth=2.5, ci_show=False)
        km_plotted += 1

    plt.title(f"Co-Mutation Survival Profiles: {geneA} & {geneB}", fontsize=13, fontweight='bold')
    plt.xlabel("Timeline (Months)", fontsize=11)
    plt.ylabel("Overall Survival Probability $S(t)$", fontsize=11)
    plt.ylim(0, 1.02)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(f"../RESULTS/comutation_plots/{geneA}_{geneB}_survival_curve.png", dpi=300)
    plt.close()
    
    # --- B. FIT COX MODEL FOR INTERACTION RISK TIERING ---
    # Create dummy variable columns excluding 'Neither' as the baseline reference
    dummy_df = pd.get_dummies(df[[time_col, event_col, pair_col_name] + covariates], columns=[pair_col_name], drop_first=False)
    
    # Ensure correct baseline reference group exclusion
    baseline_col = f"{pair_col_name}_Neither"
    model_features = [col for col in dummy_df.columns if col.startswith(f"{pair_col_name}_") and col != baseline_col]
    
    # Append clinical covariates
    model_cols = [time_col, event_col] + covariates + model_features
    final_model_df = dummy_df[model_cols].astype(float)
    
    try:
        cph = CoxPHFitter()
        cph.fit(final_model_df, duration_col=time_col, event_col=event_col)
        
        # Save metrics for the "Both" group if it exists
        both_col = f"{pair_col_name}_Both"
        if both_col in cph.summary.index:
            summary = cph.summary.loc[both_col]
            comut_records.append({
                "Pair": f"{geneA}+{geneB}",
                "CoMut_Group_N": counts.get("Both", 0),
                "Adjusted_Interaction_HR": summary["exp(coef)"],
                "Lower_95": summary["exp(coef) lower 95%"],
                "Upper_95": summary["exp(coef) upper 95%"],
                "p_value": summary["p"]
            })
    except Exception as e:
        print(f"  Could not compute regression coefficients for {geneA}+{geneB}: {e}")

# Export summary tracker matrix
if comut_records:
    comut_df = pd.DataFrame(comut_records)
    comut_df.to_csv("../RESULTS/step5_comutation_hazard_ratios.csv", index=False)
    print("\n=== STEP 5 CO-MUTATION COHORT HAZARD ESTIMATES ===")
    print(comut_df.to_string(index=False))