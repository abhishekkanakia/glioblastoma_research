# Step 4: Propensity Score Enhanced Analysis (IPTW)

## Overview
This folder contains the causal survival inference pipeline for the Glioblastoma (GBM) cohort. While multivariate Cox regression (Step 3) arithmetically adjusts for covariates, Step 4 implements an **Inverse Probability of Treatment Weighting (IPTW)** framework. This method utilizes propensity scores to synthetically re-weight the patient population, mimicking a randomized clinical trial setting by creating statistical balance across baseline clinical characteristics (Age and Sex) between the mutated and wild-type groups.

---

## Technical Logic & Causal Framework

### 1. Feature Narrowing
Analysis is focused on the primary analytical targets (**EGFR** and **IDH1**) that demonstrated active prognostic trends or strong data representation in earlier iterations.

### 2. Propensity Score Estimation
For each gene, a logistic regression classifier is built to estimate the probability that a patient would harbor the genomic mutation based strictly on their clinical presentation ($X = [\text{AGE}, \text{SEX\_NUM}]$):
$$P(\text{Mutation} = 1 \mid X) = \frac{1}{1 + \exp(-(\beta_0 + \beta_1 \cdot \text{AGE} + \beta_2 \cdot \text{SEX\_NUM}))}$$

### 3. Stabilized IPTW Weight Computation
To construct a synthetic pseudo-population where baseline clinical attributes are detached from mutation assignments, weights are computed for each unique patient $i$ as follows:
$$w_i = \frac{\text{Mutation}_i}{P(\text{Mutation}_i = 1 \mid X_i)} + \frac{1 - \text{Mutation}_i}{1 - P(\text{Mutation}_i = 1 \mid X_i)}$$

* **Outlier Variance Stabilization/Capping:** Extreme outlier weights are clipped at the 99th percentile (`quantile(0.99)`). This boundary caps extreme propensity values close to 0 or 1, preventing high variance inflation from dominating the downstream weighted model estimates.

### 4. Covariate Balance Assessment (SMD)
To verify that the synthetic weighting effectively eliminated clinical baseline imbalances, the **Standardized Mean Difference (SMD)** is computed for each feature before and after weighting:
$$\text{SMD} = \frac{|\mu_{\text{Mutated}} - \mu_{\text{Wildtype}}|}{\sqrt{\frac{\sigma^2_{\text{Mutated}} + \sigma^2_{\text{Wildtype}}}{2}}}$$

An **SMD < 0.10** after weighting structurally indicates that rigorous clinical balance has been achieved, making the groups directly comparable.

### 5. Weighted Cox Proportional Hazards Fit
An IPTW-weighted Cox Proportional Hazards model is fitted using the calculated synthetic patient weight vectors. The regression is configured with **robust sandwich estimators** (`robust=True`) to correctly estimate standard errors and confidence intervals within the re-weighted pseudo-population.

---

## Output Spreadsheet Data Definitions

The resulting dataset file `step4_iptw_results_table.csv` contains the following metrics:

| Variable Column Name | Data Typology | Explicit Definition & Causal Interpretation |
| :--- | :--- | :--- |
| `Biomarker` | Categorical / String | The specific gene sequence targeted for causal survival evaluation (`EGFR`, `IDH1`). |
| `IPTW_Hazard_Ratio` | Floating Point | **Causal Hazard Ratio**. The risk multiplier isolated after using inverse probability weights to balance baseline characteristics. Reflects the independent biological impact of the mutation on the risk of death. |
| `Lower_95` | Floating Point | The lower limit of the 95% Confidence Interval, calculated using robust sandwich variance estimators. |
| `Upper_95` | Floating Point | The upper limit of the 95% Confidence Interval, calculated using robust sandwich variance estimators. |
| `IPTW_p_value` | Floating Point | Causal significance score. Compares the independent hazard profile across groups in the balanced sample. Values below $0.05$ indicate that the isolated genomic hazard remains robust even after eliminating measured clinical imbalances. |

---

## Explicit Artifact Layout Interpretations

### Saved Visualizations Directory: `propensity_plots/`
These plots display Kernel Density Estimations (KDE) to visualize the **Common Support/Overlap Bound** between the cohorts.
* **X-Axis Line:** Estimated Propensity Score $P(\text{Mutation} \mid X)$ bounded between $0.0$ and $1.0$[cite: 61, 64]. Represents the calculated likelihood of a patient having the mutation based purely on their age and sex[cite: 151].
* **Y-Axis Value:** Kernel Density Estimation of patient distribution density[cite: 52, 60].
* **Red Probability Landscape:** The propensity score distribution for the **Mutated** patient cohort[cite: 53].
* **Blue Probability Landscape:** The propensity score distribution for the **Wild-Type** patient cohort[cite: 53].
* **Interpretation Checklist:** Look for broad shared overlap across the x-axis spectrum[cite: 159]. A high degree of overlap indicates strong **common support**, verifying that both cohorts share comparable clinical profiles (Age/Sex matchings) for reliable causal inference[cite: 4, 47].