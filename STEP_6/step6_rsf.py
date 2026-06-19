import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.ensemble import RandomSurvivalForest
from sklearn.inspection import permutation_importance  # Added for proper ML extraction

# ==========================================
# 1. SETUP AND DATA PREPARATION
# ==========================================
data_path = "../STEP_1/gbm_merged_data.csv"
df_clinical = pd.read_csv(data_path)

raw_mutations_path = "gbm_tcga_pub2013/core_data_subset/data_mutations.txt"
if not os.path.exists(raw_mutations_path):
    raw_mutations_path = "../gbm_tcga_pub2013/data_mutations.txt"

df_raw = pd.read_csv(raw_mutations_path, sep="\t", comment="#", low_memory=False)
df_raw.columns = [col.strip() for col in df_raw.columns]
df_raw['Clean_Patient_ID'] = df_raw['Tumor_Sample_Barcode'].apply(lambda x: "-".join(str(x).split("-")[:3]))

discovered_biomarkers = ["FBN3", "STAG2", "ADAMTS12", "LZTR1", "TCHH", "EGFR", "DMD"]

df_raw_filtered = df_raw[df_raw['Hugo_Symbol'].isin(discovered_biomarkers)]
genomic_matrix = pd.crosstab(df_raw_filtered['Clean_Patient_ID'], df_raw_filtered['Hugo_Symbol'])
genomic_matrix = (genomic_matrix > 0).astype(int)

if df_clinical['OS_STATUS'].dtype == object:
    df_clinical['E'] = df_clinical['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
else:
    df_clinical['E'] = df_clinical['OS_STATUS'].astype(int)

df_clinical['SEX_NUM'] = df_clinical['SEX'].apply(lambda x: 1 if str(x).upper().startswith('M') else 0)

model_df = df_clinical[['PATIENT_ID', 'OS_MONTHS', 'E', 'AGE', 'SEX_NUM']].copy()
model_df = model_df.merge(genomic_matrix, left_on='PATIENT_ID', right_index=True, how='left')
model_df[discovered_biomarkers] = model_df[discovered_biomarkers].fillna(0).astype(int)

# ==========================================
# 2. FORMATTING FOR SCIKIT-SURVIVAL
# ==========================================
feature_cols = ['AGE', 'SEX_NUM'] + discovered_biomarkers
X = model_df[feature_cols].astype(float)

y_structured = np.array(
    list(zip(model_df['E'].astype(bool), model_df['OS_MONTHS'])),
    dtype=[('Status', '?'), ('Survival_in_months', '<f8')]
)

print(f"Executing Random Survival Forest across {len(X)} patients using {len(feature_cols)} features...")

# ==========================================
# 3. TRAINING THE RANDOM SURVIVAL FOREST
# ==========================================
rsf = RandomSurvivalForest(
    n_estimators=250,
    min_samples_split=6,
    min_samples_leaf=3,
    n_jobs=-1,
    random_state=42
)

rsf.fit(X, y_structured)
c_index = rsf.score(X, y_structured)
print(f"\n✅ RSF Training Complete!")
print(f"🏅 Overall Model Concordance Index (C-index): {c_index:.4f}")

# ==========================================
# 4. CALCULATING PERMUTATION FEATURE IMPORTANCE (VIMP)
# ==========================================
print("Computing permutation feature importances (this may take a moment)...")
# permute features 10 times to get stable average drop scores
result = permutation_importance(rsf, X, y_structured, n_repeats=10, random_state=42)

# Extract the mean importance drop for each feature
importances = result.importances_mean

# Structure into a clean table
importance_df = pd.DataFrame({
    "Feature": feature_cols,
    "Importance_Score": importances
}).sort_values(by="Importance_Score", ascending=True)

importance_df.to_csv("step6_rsf_feature_importances.csv", index=False)

print("\n=== MACHINE LEARNING FEATURE IMPORTANCE RANKING ===")
print(importance_df.sort_values(by="Importance_Score", ascending=False).to_string(index=False))

# ==========================================
# 5. GENERATING RESPLENDENT PLOTS
# ==========================================
plt.figure(figsize=(10, 6))
colors = ['#1f77b4' if feat in ['AGE', 'SEX_NUM'] else '#d62728' for feat in importance_df['Feature']]

plt.barh(importance_df['Feature'], importance_df['Importance_Score'], color=colors, edgecolor='gray', height=0.6)
plt.xlabel("Permutation Importance (Mean C-index Drop)", fontsize=11)
plt.title(f"Random Survival Forest Feature Importance (Model C-index: {c_index:.3f})", fontsize=13, fontweight='bold')
plt.grid(True, axis='x', linestyle=':', alpha=0.6)
plt.tight_layout()

os.makedirs("ml_plots", exist_ok=True)
plt.savefig("ml_plots/rsf_feature_importances.png", dpi=300)
plt.show()

print("\nStep 6 completed successfully! Check 'ml_plots/rsf_feature_importances.png' to see your ranking visualization.")