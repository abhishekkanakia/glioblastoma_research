# Step 6: Machine Learning Survival Prediction (Random Survival Forest)

## Overview
This folder contains the machine learning survival prediction pipeline for the Glioblastoma (GBM) cohort. Moving beyond single-gene estimators (Step 2) and semi-parametric linear regressions (Steps 3 & 4), Step 6 implements a non-linear, multi-dimensional **Random Survival Forest (RSF)** ensemble model. This architecture captures high-dimensional interactions between clinical predictors and genomic biomarkers to rank their predictive contribution to overall survival outcomes.

---

## Technical Logic & Machine Learning Framework

### 1. Expanded Genomic Ingestion
* **High-Dimensional Expansion:** This step expands the genomic feature matrix by loading a comprehensive mutation dataset (`data_mutations.txt`). It screens a broader discovery panel of 7 key target features: **FBN3, STAG2, ADAMTS12, LZTR1, TCHH, EGFR, and DMD**.
* **Matrix Pivoting:** Genomic entries are compiled into an cross-tabulated array (`pd.crosstab`), which is compressed into a binary matrix ($1 = \text{Mutated}$, $0 = \text{Wild-Type}$). This matrix is joined back to the primary clinical cohort data sheet using a standard left-merge operation over clean 12-character patient identifiers. Missing data rows are explicitly filled with zero values (`.fillna(0)`) to denote a wild-type presentation.

### 2. Scikit-Survival Structured Array Alignment
Traditional regression architectures accept separate 1D outcome vectors for events and time. However, scikit-survival models require a customized, unified structured 2D NumPy matrix. The survival targets are explicitly cast into a dual-field structured array format:
* **`Status`** *(Boolean, `?`)*: Maps the terminal outcome flag (`True` if the patient is deceased, `False` if right-censored).
* **`Survival_in_months`** *(Floating Point, `<f8`)*: Tracks the continuous continuous duration variable (`OS_MONTHS`).

### 3. Ensemble Model Hyperparameters
The `RandomSurvivalForest` estimator optimizes survival tree splits by evaluating the **Log-Rank score criterion** across complex feature boundaries. The model is locked to the following robust architecture configuration:
* `n_estimators=250`: Generates 250 independent survival decision trees to balance out high-variance predictions.
* `min_samples_split=6` & `min_samples_leaf=3`: Forces structural tree regularization. Prevents single outlier nodes from dominating branch rules, maintaining generalizability.
* `n_jobs=-1`: Directs parallel multi-threaded computation across all active CPU cores.

### 4. Permutation Feature Importance Evaluation (VIMP)
To determine the true predictive impact of each feature without linear assumptions, the model utilizes **Permutation Feature Importance** rather than basic internal Gini splits:
1. The trained model establishes a clear predictive baseline performance score.
2. A single feature column is completely shuffled (permuted) 10 independent times (`n_repeats=10`) to break its relationship with the survival outcome while preserving the baseline data structure.
3. The overall model performance drop is re-calculated for each loop.
4. The difference is averaged to generate a final **Importance_Score**. If a feature's values are crucial for survival prediction, shuffling them will cause a noticeable drop in model accuracy.

---

## Model Evaluation & Data Definitions

### Model Performance Metric
* **Concordance Index (C-index):** Measures the model's ability to correctly order survival times across pairs of patients. A score of `0.5` represents random guessing, while a score of `1.0` represents flawless predictive ranking.

### Importance Table Definitions (`step6_rsf_feature_importances.csv`)

| Variable Column Name | Data Typology | Explicit Definition & Computational Context |
| :--- | :--- | :--- |
| `Feature` | Categorical / String | The precise metric feature evaluated inside the array (Clinical features: `AGE`, `SEX_NUM`; Genomic features: `EGFR`, `FBN3`, etc.). |
| `Importance_Score` | Floating Point | **Mean Concordance Index Drop.** The calculated reduction in model accuracy caused by randomly shuffling that column's values across the cohort.<br>• $\mathbf{Score > 0.0}$: Indicates that the feature actively provides predictive information. Higher drops indicate a more critical variable (e.g., `AGE` at $0.2027$).<br>• $\mathbf{Score = 0.0}$: Indicates the feature provides no predictive utility within the current survival tree model (e.g., `LZTR1`). |

---

## Explicit Visual Plot Interpretations

### Saved Output Asset: `ml_plots/rsf_feature_importances.png`
The generated graphic is a horizontal bar chart displaying features ordered from lowest to highest importance score to clearly show performance drops.
* **Y-Axis Rows:** The unique list of evaluated variables.
* **X-Axis Values:** Measures the continuous mean C-index drop metric, indicating the magnitude of predictive importance.
* **Blue Shaded Horizontal Bars (`#1f77b4`):** Represents **Clinical Variables** (`AGE`, `SEX_NUM`). This color assignment allows users to quickly see how traditional clinical indicators compare against molecular markers.
* **Red Shaded Horizontal Bars (`#d62728`):** Represents **Genomic Biomarker Variables** (e.g., `EGFR`, `FBN3`). This highlights which mutations have the strongest predictive power in the random survival forest model.