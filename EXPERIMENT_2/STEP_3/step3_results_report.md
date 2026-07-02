# Experiment 2 — Step 3: Multivariable Adjusted Cox Proportional Hazards Regression

## Overview
This directory contains the computational outputs for **Experiment 2: Step 3**. 

The primary objective of this phase is to evaluate the independent prognostic impact of our top-performing genomic biomarkers. While the Step 2 Kaplan-Meier analysis calculated unadjusted survival, this step utilizes Cox Proportional Hazards regression to compute Hazard Ratios (HR) before and after adjusting for primary clinical covariates (Age and Sex). This statistical control isolates true genomic risk trends from demographic confounding factors.

---

## Data Schema & Variable Dictionary

The master results spreadsheet (**`step3_cox_regression_results.csv`**) tracks the linear survival dynamics of the target loci using the following parameters:

| Variable Name | Data Type | Definition / Mathematical Meaning |
| :--- | :---: | :--- |
| `Biomarker` | String | HGNC approved symbol for the dynamically screened gene target. |
| `Model_Type` | String | Specification of the statistical design: `Unadjusted` (bivariate gene-only model) or `Adjusted (Age+Sex)` (multivariable model controlling for age as a continuous variable and sex as a binary factor). |
| `HR` | Float | Hazard Ratio. An $HR > 1.0$ indicates increased risk of mortality (hazardous candidate), while an $HR < 1.0$ indicates decreased risk of mortality (protective candidate). |
| `Lower_95` | Float | The lower bound of the 95% Confidence Interval for the calculated Hazard Ratio. |
| `Upper_95` | Float | The upper bound of the 95% Confidence Interval for the calculated Hazard Ratio. |
| `p_value` | Float | The Wald test $p$-value evaluating the null hypothesis ($H_0$) that the biomarker has no independent association with overall survival duration. |

---

## Step 3 Experimental Results Ledger

Below is the structured output mapping both the unadjusted and covariate-adjusted linear survival models for the core predictive hits within our 253-patient cohort:

| Biomarker | Model Type | Hazard Ratio (HR) | Lower 95% CI | Upper 95% CI | $p$-value | Independent Statistical Status ($p < 0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **STAG2** | Unadjusted | 3.66 | 1.69 | 7.92 | 0.00100 | Significant Hazardous Factor |
| **STAG2** | Adjusted (Age+Sex) | 4.12 | 1.89 | 8.96 | 0.00036 | **Robust Independent Risk Driver** |
| **IDH1** | Unadjusted | 0.24 | 0.09 | 0.65 | 0.00513 | Significant Protective Factor |
| **IDH1** | Adjusted (Age+Sex) | 0.44 | 0.16 | 1.24 | 0.12057 | Non-Significant After Clinical Adjustment |
| **DNAH2** | Unadjusted | 2.69 | 1.25 | 5.79 | 0.01150 | Significant Hazardous Factor |
| **DNAH2** | Adjusted (Age+Sex) | 2.32 | 1.07 | 5.01 | 0.03259 | **Robust Independent Risk Driver** |
| **PCLO** | Unadjusted | 1.85 | 1.10 | 3.11 | 0.02119 | Significant Hazardous Factor |
| **PCLO** | Adjusted (Age+Sex) | 1.56 | 0.93 | 2.64 | 0.09389 | Confounded by Clinical Covariates |
| **CALN1** | Unadjusted | 2.38 | 1.05 | 5.43 | 0.03845 | Significant Hazardous Factor |
| **CALN1** | Adjusted (Age+Sex) | 1.99 | 0.87 | 4.56 | 0.10247 | Confounded by Clinical Covariates |
| **DSP** | Unadjusted | 2.36 | 1.04 | 5.38 | 0.04056 | Significant Hazardous Factor |
| **DSP** | Adjusted (Age+Sex) | 1.52 | 0.66 | 3.53 | 0.32548 | Confounded by Clinical Covariates |
| **DNAH8** | Unadjusted | 2.25 | 0.98 | 5.13 | 0.05491 | Borderline Non-Significant |
| **DNAH8** | Adjusted (Age+Sex) | 1.92 | 0.83 | 4.45 | 0.12624 | Non-Significant After Adjustment |
| **FGD5** | Unadjusted | 1.85 | 0.97 | 3.53 | 0.06009 | Non-Significant Trend |
| **FGD5** | Adjusted (Age+Sex) | 1.52 | 0.79 | 2.95 | 0.21358 | Non-Significant After Adjustment |
| **TEX15** | Unadjusted | 2.16 | 0.94 | 4.94 | 0.06959 | Non-Significant Trend |
| **TEX15** | Adjusted (Age+Sex) | 2.46 | 1.07 | 5.66 | 0.03383 | **Suppressed Signal (Significant Post-Adjustment)** |
| **TAF1L** | Unadjusted | 2.02 | 0.89 | 4.60 | 0.09214 | Non-Significant Trend |
| **TAF1L** | Adjusted (Age+Sex) | 1.77 | 0.77 | 4.07 | 0.17944 | Non-Significant After Adjustment |
| **ADAMTS12** | Unadjusted | 0.39 | 0.12 | 1.21 | 0.10276 | Non-Significant Trend |
| **ADAMTS12** | Adjusted (Age+Sex) | 0.32 | 0.10 | 1.00 | 0.04927 | **Suppressed Signal (Significant Post-Adjustment)** |

---

## Bioinformatic Interpretation of Results

1. **Amplified Risk Signaling (`STAG2`):** Controlling for baseline demographics increased the hazard calculation for `STAG2` mutations ($HR = 3.66 \rightarrow HR = 4.12$; $p = 0.00036$). This indicates that `STAG2` is an exceptionally strong, independent driver of poor survival in this glioblastoma cohort, completely unconfounded by patient age or sex.
2. **The Clinical Confounding Drop (`IDH1`):** In the unadjusted model, `IDH1` mutations demonstrated a powerful protective signal ($HR = 0.24, p = 0.00513$). However, upon adding Age and Sex to the model, its independent significance faded ($HR = 0.44, p = 0.12057$). This strongly suggests that `IDH1` status is highly correlated with demographic baseline structures (such as younger age), necessitating the causal adjustments (IPTW) planned in Step 4 to resolve selection bias.
3. **Unmasking Suppressed Targets (`TEX15`, `ADAMTS12`):** Both `TEX15` and `ADAMTS12` failed to cross the significance threshold in unadjusted Kaplan-Meier testing. However, when accounting for clinical clinical parameters, their signals were unmasked. `ADAMTS12` emerged as an independently significant protective marker ($HR = 0.32, p = 0.04927$), while `TEX15` emerged as a significant risk factor ($HR = 2.46, p = 0.03383$).

---

## Codebase Artifacts & Output Specifications
* **`step3_cox_regression_results.csv`**: The master data frame tracking unadjusted and multivariable coefficients, confidence bounds, and Wald statistics across the screen.
* **`plots/forest_plots/`**: The pipeline script generates comparative forest plots for all targets demonstrating a post-adjustment $p$-value $< 0.05$, visually mapping the shifts in Hazard Ratios between model iterations.