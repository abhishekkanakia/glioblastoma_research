# GBM Multi-Paradigm Genomic Discovery & Survival Inference Framework

An advanced bioinformatic pipeline and non-linear causal framework designed to screen, isolate, and validate high-integrity genomic biomarkers in Glioblastoma Multiforme (GBM). This project bridges public high-throughput sequencing data (TCGA cohort) with an automated analytical workflow that tracks survival trajectories across three distinct methodologies: linear multivariable regression, propensity-score matched causal inference, and machine learning ensemble forests.

The pipeline features a unique **Cross-Paradigm Evidence Integration Framework** that strips out background passenger mutations and maps candidate loci into clinical confidence tiers based on mathematical convergence across all modeling tracks.

---

## Project Architecture & Two-Track Design

To decouple baseline historical control targets from genome-wide discovery arrays, the project is divided into two entirely separate, isolated experimental channels:

1. **`EXPERIMENT_1_CANDIDATE_PANEL`**
   * **Scope:** Focused evaluation restricted solely to the historical clinical anchor candidates (`EGFR`, `IDH1`, `TP53`, `BRAF`) to map traditional associative baselines.
2. **`EXPERIMENT_2_DISCOVERY_SCREEN`**
   * **Scope:** An automated, high-dimensional screening engine that processes the **top 100 most frequently mutated genes** across patients through the complete 7-step pipeline to extract novel prognostic drivers.

---

## Dataset & Clinical Cohort Scope

* **Total Analytical Sample Size ($N$):** 253 unique glioblastoma patients successfully isolated following stringent multi-tier quality control (removal of missing survival vectors, truncation of negative timelines, and clinical tracking verification).
* **Baseline Cohort Characteristics:** Mean diagnostic age of $61.8 \pm 12.7$ years; gender distribution of 64.4% Male ($N=163$) and 35.6% Female ($N=90$). MGMT promoter methylation arrays were excluded due to missingness thresholds exceeding structural tolerances.
* **Patient-Level Penetrance Contraction:** Multi-sample sequence duplicates are compressed into binary representations ($1 = \text{Mutated}$, $0 = \text{Wildtype}$) mapped **per unique patient**. Mutation penetrance rankings are evaluated across independent individuals to prevent multi-biopsy sample inflation.

---

## Full 7-Step Operational Framework

```text
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │  Screening   │ ──► │    Step 1    │ ──► │    Step 2    │ ──► │    Step 3    │
 │ Genome Wide  │     │ Cohort Table │     │ Kaplan-Meier │     │ Adjusted Cox │
 └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                        │
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
 │    Step 7    │ ◄── │    Step 6    │ ◄── │    Step 5    │ ◄───────────┘
 │ Final Ledger │     │  ML Forest   │     │ Co-Mutations │
 └──────────────┘     └──────────────┘     └──────────────┘
```

# Genome-Wide Biomarker & Survival Analysis Framework

---

## Pipeline Workflow Steps

### Step 1: Genome-Wide Feature Extraction & Merging
* **Objective:** Ingest somatic variant mutation matrices, isolate the top 100 highest-penetrance targets across unique patients, and merge binary genetic vectors with clinical master logs.
* **Core Outputs:** * `top_100_genes_list.csv` (the immediate quick-read frequency summary)
  * `gbm_merged_data.csv` (the wide analytical matrix spanning 253 patients and 102 active feature variables)

### Step 2: Unadjusted Kaplan-Meier Stratification
* **Objective:** Compute baseline non-parametric survival function estimates across mutated vs. wildtype populations:
$$\hat{S}(t) = \prod_{t_i \le t} \left(1 - \frac{d_i}{n_i}\right)$$
* **Methodology:** Evaluates raw survival trajectory splitting using non-parametric log-rank tests. Uncovers initial high-risk signals (**STAG2** median OS 5.2 mo. vs. 13.7 mo. wildtype; $p = 0.0004$) and protective thresholds (**IDH1** median OS 33.7 mo. vs. 13.0 mo. wildtype; $p = 0.0023$).

### Step 3: Multivariable Adjusted Cox Proportional Hazards
* **Objective:** Isolate independent genomic risk weights while controlling for continuous clinical age metrics and binary sex variables.
* **Methodology:** Semiparametric Cox regression tracking calculated Hazard Ratios (HR) and Wald statistics. Unmasks masked signatures where demographic factors act as suppressors (e.g., **ADAMTS12** adjusts to $HR = 0.32, p = 0.04927$; **TEX15** adjusts to $HR = 2.46, p = 0.03383$).

### Step 4: Causal Inference via Propensity Score Weighting (IPTW)
* **Objective:** Neutralize patient assignment bias and demographic imbalances to isolate true biological causal survival hazards.
* **Methodology:** Computes logistic regression propensity scores $P(\text{Mutation} \mid \text{Age}, \text{Sex})$ to generate Inverse Probability of Treatment Weighting (IPTW) stabilization vectors. Resolves severe linear misspecification errors, rehabilitating the independent causal value of **IDH1** ($HR = 0.35, p = 8.35 \times 10^{-9}$) under perfect baseline covariate balancing.

### Step 5: Stratified Co-Mutation Interaction Analysis
* **Objective:** Evaluate synergistic, multiplicative phenotypic combinations versus additive or mutually exclusive genomic layouts.
* **Methodology:** Partitions patient groups into four mutually exclusive survival tracks. Reveals deep mutual exclusivity constraints for catastrophic structural lines (e.g., **TP53+STAG2** presents an absolute cohort density of $N = 0$, indicating a biologically non-viable cellular profile).

### Step 6: Non-Linear Machine Learning Modeling
* **Objective:** Capture high-dimensional epistatic feature architectures and rank biomarker predictive value without linear constraints.
* **Methodology:** Trains an ensemble Random Survival Forest (RSF) of 250 survival decision trees utilizing log-rank splitting parameters. Measures independent feature value via 10x repeated shuffling Permutation Feature Importance (VIMP) scores based on global C-index drops.
* **Model Accuracy Baseline:** Global Concordance Index (C-index) = 0.7883.

### Step 7: Cross-Paradigm Consensus Integration
* **Objective:** Execute an automated inner-outer join combining stats, causal logic, and machine learning weights to clean out passenger variants and construct the definitive project ledger (`step7_final_biomarker_ledger.csv`).

---

## Final Cross-Paradigm Consistency Ledger

The framework maps features into three strict clinical confidence categories based on criteria checking multivariable linear limits ($p < 0.05$), causal propensity validation ($p < 0.05$), and forest predictive scores ($VIMP \ge 0.003$):

```text
                            [ 100-Biomarker Data Entry ]
                                         │
                                         ▼
              ┌──────────────────────────────────────────────────┐
              │      (Cox_p < 0.05 AND RSF_VIMP >= 0.003)        │─── YES ──► Tier 1: High Confidence
              │          AND (No IPTW OR IPTW_p < 0.05)          │
              └──────────────────────────────────────────────────┘
                                         │
                                         │ NO
                                         ▼
              ┌──────────────────────────────────────────────────┐
              │           IPTW_p < 0.05 OR RSF_VIMP >= 0.005     │─── YES ──► Tier 2: Moderate Confidence
              │                     OR Cox_p < 0.05              │
              └──────────────────────────────────────────────────┘
                                         │
                                         │ NO
                                         ▼
                       Tier 3: Low Confidence Background / Passenger
```

# Top-Tier Discoveries Consolidated Matrix (Experiment 2 Extraction)

| Biomarker | Cox HR | Cox p | IPTW HR | IPTW p | RSF VIMP | Assigned Consensus Performance Tier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| STAG2 | 4.11878 | 0.00036 | 3.83594 | 0.00000 | 0.02177 | Tier 1: High Confidence Discovery |
| TEX15 | 2.46277 | 0.03383 | 2.33007 | 0.00811 | 0.00514 | Tier 1: High Confidence Discovery |
| DNAH2 | 2.31728 | 0.03259 | ---- | ---- | 0.00388 | Tier 1: High Confidence Discovery |
| PCLO | 1.56391 | 0.09389 | ---- | ---- | 0.01630 | Tier 2: Moderate Confidence Candidate |
| EGFR | ---- | ---- | ---- | ---- | 0.01374 | Tier 2: Moderate Confidence Candidate |
| IDH1 | 0.44260 | 0.12057 | 0.35006 | 0.00000 | 0.01234 | Tier 2: Moderate Confidence Candidate |
| MUC16 | ---- | ---- | ---- | ---- | 0.00687 | Tier 2: Moderate Confidence Candidate |
| FGD5 | 1.52107 | 0.21358 | ---- | ---- | 0.00603 | Tier 2: Moderate Confidence Candidate |
| DNAH8 | 1.92280 | 0.12624 | ---- | ---- | 0.00542 | Tier 2: Moderate Confidence Candidate |
| TP53 | ---- | ---- | ---- | ---- | 0.00540 | Tier 2: Moderate Confidence Candidate |
| ADAMTS12 | 0.31578 | 0.04927 | 0.41503 | 0.13878 | 0.00255 | Tier 2: Moderate Confidence Candidate |
| TTN | ---- | ---- | ---- | ---- | 0.00357 | Tier 3: Low Confidence Background Passenger |

---

## Repository Layout & Subdirectory Structure

```plaintext
GBM_project/
├── EXPERIMENT_1_CANDIDATE_PANEL/             # Isolated baseline historical candidate tracks
│   ├── STEP_1_COHORT_DESCRIPTIVES/           # 4-gene penetrance and baseline cohort data
│   ├── STEP_2_3_COX_MODELS/                  # Basic unadjusted/adjusted linear modeling
│   ├── STEP_4_CAUSAL_IPTW/                   # Propensity calculation folders
│   └── STEP_5_CO_MUTATION_STRAT/             # Target candidate pair interaction testing
│
└── EXPERIMENT_2_DISCOVERY_SCREEN/            # High-dimensional automated discovery pipeline
    ├── STEP_1/                               # Dynamic top 100 genome extraction & matrix generation
    │   ├── SCRIPTS/step1_analysis.py         
    │   ├── top_100_genes_list.csv            # The immediate quick-read results asset
    │   └── gbm_merged_data.csv               # Wide 102-column master data table
    ├── STEP_2/                               # Unadjusted Kaplan-Meier & Log-Rank math
    │   ├── step2_km_logrank_results.csv      # Complete unadjusted 100-gene summary metrics
    │   └── plots/km_curves/                  
    ├── STEP_3/                               # Adjusted Multivariable Cox Regressions
    │   ├── step3_cox_regression_results.csv  # 100-gene linear covariate adjustment matrix
    │   └── plots/forest_plots/               
    ├── STEP_4/                               # Stabilized Causal Propensity Scoring
    │   └── step4_iptw_causal_results.csv     # Causal hazard ratios for target hits
    ├── STEP_5/                               # Interaction & Stratified Co-Mutation
    │   ├── step5_comutation_results.csv      
    │   └── plots/comutation_curves/          # Includes structural mutual exclusivity charts
    ├── STEP_6/                               # Machine Learning Random Survival Forests
    │   ├── SCRIPTS/step6_rsf.py              # 250-tree scikit-survival training routine
    │   ├── step6_rsf_feature_importances.csv # Complete 102-feature VIMP spreadsheet
    │   └── ml_plots/                         # Horizon validation visualization graphics
    └── STEP_7/                               # Evidence Integration Framework Integration
        ├── SCRIPTS/step7_integration.py      # Automated pipeline ledger builder
        └── step7_final_biomarker_ledger.csv  # Finalized publication ledger tracking all 100 targets
```

## Environment Setup & Scientific Dependencies

To execute or scale either experimental track within this framework, ensure your local Python workspace contains the following specific operational dependencies:

* **scikit-survival ($\ge 0.22.0$):** Powers the high-performance non-linear Random Survival Forest and structures time-to-event outcomes.
* **lifelines ($\ge 0.27.0$):** For non-parametric Kaplan-Meier object calculations and semiparametric Cox baseline regressions.
* **statsmodels ($\ge 0.14.0$):** Handles the binary logistic regression engines to extract propensity weights.
* **scikit-learn ($\ge 1.3.0$):** Executes the structural feature permutation shuffles.
* **pandas, numpy, matplotlib:** Standard array manipulation and vector graphic processing.