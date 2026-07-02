import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.ensemble import RandomSurvivalForest
from sklearn.inspection import permutation_importance

# ==========================================
# 1. SETUP AND DYNAMIC DATA PREPARATION
# ==========================================
data_path = "../../gbm_merged_data.csv"
df = pd.read_csv(data_path)

# Clean column names of any hidden whitespaces
df.columns = df.columns.str.strip()

# Load the dynamic list of 100 genes from Step 1 to use as features
genes_list_path = "../../top_100_genes_list.csv"
df_genes = pd.read_csv(genes_list_path)
discovered_biomarkers = df_genes["Gene"].tolist()

# DYNAMIC FIX FOR 'SEX' -> 'SEX_NUM'
if 'SEX' in df.columns:
    # Safely map common string variations to 1 and 0
    df['SEX_NUM'] = df['SEX'].astype(str).str.upper().str.strip().map({'MALE': 1, 'FEMALE': 0})
    print("🔄 Successfully converted text 'SEX' column to numeric 'SEX_NUM'.")
elif 'SEX_NUM' not in df.columns:
    print("⚠️ Neither 'SEX' nor 'SEX_NUM' found. Defaulting to AGE and genes only.")

# Finalize the available feature columns
feature_cols = [col for col in ['AGE', 'SEX_NUM'] if col in df.columns] + discovered_biomarkers

# Check if EVENT column exists, otherwise fallback to OS_STATUS parsing
if 'EVENT' in df.columns:
    event_col = 'EVENT'
elif 'E' in df.columns:
    event_col = 'E'
else:
    df['EVENT'] = df['OS_STATUS'].apply(lambda x: 1 if 'DECEASED' in str(x).upper() else 0)
    event_col = 'EVENT'

# Format features matrix (X) and convert to float
X = df[feature_cols].astype(float)

# ==========================================
# 2. FORMATTING FOR SCIKIT-SURVIVAL STRUCTURE
# ==========================================
# scikit-survival requires a structured numpy array with boolean status and float time
y_structured = np.array(
    list(zip(df[event_col].astype(bool), df['OS_MONTHS'].astype(float))),
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
print("Computing permutation feature importances across all 102 variables (10x shuffle iterations)...")
result = permutation_importance(rsf, X, y_structured, n_repeats=10, random_state=42)

# Structure all 102 features into a clean ranking table
importance_df = pd.DataFrame({
    "Feature": feature_cols,
    "Importance_Score": result.importances_mean
}).sort_values(by="Importance_Score", ascending=True)

# Export complete 102-feature machine learning importance table to CSV
importance_df.sort_values(by="Importance_Score", ascending=False).to_csv("../RESULTS/step6_rsf_feature_importances.csv", index=False)

print("\n=== TOP 15 MACHINE LEARNING FEATURE IMPORTANCE RANKING ===")
print(importance_df.sort_values(by="Importance_Score", ascending=False).head(15).to_string(index=False))

# ==========================================
# 5. GENERATING RANKING PLOTS FOR PREDICTIVE HITS
# ==========================================
# Extract the top 15 most important features for clean visualization formatting
top_15_importance = importance_df.sort_values(by="Importance_Score", ascending=True).tail(15)

plt.figure(figsize=(10, 7))
colors = ['#1f77b4' if feat in ['AGE', 'SEX_NUM'] else '#d62728' for feat in top_15_importance['Feature']]

plt.barh(top_15_importance['Feature'], top_15_importance['Importance_Score'], color=colors, edgecolor='gray', height=0.6)
plt.xlabel("Permutation Importance (Mean C-index Drop)", fontsize=11)
plt.title(f"Random Survival Forest Top Predictive Features (Model C-index: {c_index:.3f})", fontsize=12, fontweight='bold')
plt.grid(True, axis='x', linestyle=':', alpha=0.6)
plt.tight_layout()

os.makedirs("../RESULTS/ml_plots", exist_ok=True)
plt.savefig("../RESULTS/ml_plots/rsf_feature_importances.png", dpi=300)
plt.close()

print("\nStep 6 completed successfully! Check 'step6_rsf_feature_importances.csv' and 'ml_plots/rsf_feature_importances.png'.")