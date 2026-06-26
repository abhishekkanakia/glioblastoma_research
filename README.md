# GBM Confidence-Enhanced Survival Inference Project

An advanced genomic data pipeline and statistical framework designed to evaluate the independent prognostic value of high-risk genetic alterations in Glioblastoma (GBM). This project bridges public genomic infrastructure (TCGA via cBioPortal) with multi-paradigm analytical workflows to assess how individual and combined molecular biomarkers impact overall survival (OS) and disease-free survival (DFS).

The framework features a unique **Evidence Integration Framework** that scores and classifies biomarkers into distinct clinical confidence tiers based on their consistency across traditional survival models, causal propensity score adjustments, and machine learning ensemble algorithms.

---

## Clinical Scope & Analytical Dataset

The analysis evaluates a curated panel of genomic alterations known to drive malignant progression, dictate diagnostic boundaries, or emerge from data-driven discovery loops in high-grade gliomas.

### Target Cohort Core Properties
* **Total Analytical Sample Size ($N$):** 108 unique patients (TCGA Glioblastoma cohort) who passed structural filtering (verified survival outcomes and baseline clinical records where $\text{OS\_MONTHS} > 0$).
* **Patient-Level Aggregation:** All genetic alterations are evaluated strictly **across unique patients** rather than individual tissue samples. Multi-variant entries for a single gene are compressed into binary indicators ($1 = \text{Mutated}$, $0 = \text{Wild-Type}$) using a logical ceiling (`> 0`) to prevent sample-inflation bias.

---

## Full 7-Step Operational Framework

The project is structured into standalone pipeline scripts that handle data flow sequentially from initial screening to consensus tiering:

```text
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │  Screening   │ ──► │    Step 1    │ ──► │    Step 2    │ ──► │    Step 3    │
 │ High-Dim Cox │     │ Cohort Table │     │ Kaplan-Meier │     │ Adjusted Cox │
 └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                        │
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
 │    Step 7    │ ◄── │    Step 6    │ ◄── │    Step 5    │ ◄───────────┘
 │ Final Ledger │     │ ML Forest    │     │ Co-Mutations │
 └──────────────┘     └──────────────┘     └──────────────┘
 ```

### High-Dimensional Biomarker Screening
* **Objective:** Automatically evaluate a broad screening pool of the top 100 highest-frequency mutated genes across the cohort.
* **Methodology:** Automatically builds a wide genomic matrix, incorporates core clinical features (`AGE`, `SEX_NUM`) to control for baseline differences, filters out markers with critical boundary constraints ($\le 1$ mutant case), and outputs a sorted list of all discovered prognostic signals based on multivariate significance testing.

### Step 1: Cohort Characterization & Merging
* **Objective:** Clean raw datasets, isolate target panels, filter missing clinical endpoints, and validate baseline demographics.
* **Outputs:** Generates the master processed evaluation table (`gbm_merged_data.csv`), descriptive patient baseline characteristics table (Table 1), and patient mutation frequency plots (`mutation_frequencies.png`).

### Step 2: Single-Mutation Survival Analysis
* **Objective:** Stratify individual mutation arms against wildtype cohorts to estimate survival probabilities over time.
* **Methodology:** Fits non-parametric survival functions using the Kaplan-Meier estimator:
$$\hat{S}(t) = \prod_{t_i \le t} \left(1 - \frac{d_i}{n_i}\right)$$
Evaluates unadjusted curve separation significance using log-rank hypothesis testing. 
* **Outputs:** Independent, print-ready survival charts (`survival_plots/[Gene]_survival_curve.png`) with integrated statistical bounding boxes.

### Step 3: Adjusted Cox Proportional Hazards Modeling
* **Objective:** Measure independent prognostic survival tracking while controlling for clinical confounding variables.
* **Methodology:** Fits unadjusted and multivariate Cox Proportional Hazards models adjusting for patient Age and Sex.
* **Outputs:** Computes exponentiated regression coefficients (Hazard Ratios, HR) and Wald p-values (`step3_hazard_ratios_table.csv`) mapped visually on a master comparative regression forest plot (`cox_survival_forest_plot.png`).

### Step 4: Propensity Score Enhanced Analysis (Causal Inference)
* **Objective:** Verify that primary biomarker survival associations remain robust after eliminating demographic sample assignment bias.
* **Methodology:** Estimates propensity scores $P(\text{Mutation} \mid X)$ using logistic regression models based on baseline clinical features. Computes **Inverse Probability of Treatment Weighting (IPTW)** stabilized weight vectors, clips outlier variance at the 99th percentile, verifies covariate balance using the Standardized Mean Difference ($\text{SMD} < 0.10$), and fits weighted Cox models with robust sandwich variance estimators.
* **Outputs:** Generates common support overlap plots (`propensity_plots/[Gene]_overlap_plot.png`) and causal hazard ledgers (`step4_iptw_results_table.csv`).

### Step 5: Co-Mutation Interaction Analysis
* **Objective:** Identify phenotypic combinations of mutations that alter clinical risk profiles more severely than single alterations alone.
* **Methodology:** Partitions the cohort into four mutually exclusive groups: `Neither` (Baseline Control), `Gene A Only`, `Gene B Only`, and `Both` (Synchronous Co-mutation). Evaluates interaction risk tiers using multivariate Cox models and four-arm KM curves for targets like `TP53+EGFR`, `TP53+IDH1`, `ATRX+IDH1`, and `TERT+EGFR`.
* **Outputs:** Multi-arm survival visualizations (`comutation_plots/[GeneA]_[GeneB]_survival_curve.png`) and interaction hazard metrics (`step5_comutation_hazard_ratios.csv`).

### Step 6: Survival Machine Learning
* **Objective:** Leverage non-linear machine learning models to capture highly complex genomic feature interactions and rank biomarker predictive importance.
* **Methodology:** Trains an ensemble **Random Survival Forest (RSF)** model (250 estimators, log-rank splitting criteria) optimized for structured time-to-event outcomes. Extracts variable importance scores using **Permutation Feature Importance (VIMP)** across 10 repeated shuffles to evaluate mean Concordance Index (C-index) drops.
* **Outputs:** Predictive ranking spreadsheets (`step6_rsf_feature_importances.csv`) and horizontal classification charts (`ml_plots/rsf_feature_importances.png`).

### Step 7: Confidence Framework Integration
* **Objective:** Consolidate statistical and predictive metrics across all preceding analytical paradigms to assign a final clinical reproducibility tier to each biomarker.
* **Outputs:** The project's final consensus ledger (`step7_final_biomarker_ledger.csv`), which ranks biomarkers based on hazard ratio stability and statistical sign convergence.

---

## Integrative Confidence Tiering Matrix

To resolve data limitations and ensure clear translation to publication manuscripts, the pipeline assigns each candidate biomarker to an explicit performance tier using robust multi-paradigm criteria:

```text
                           [ Biomarker Data Entry ]
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │    (Cox_p < 0.05 OR IPTW_p_value < 0.05)         │─── YES ──► Tier 1: High Confidence
             │             AND RSF_VIMP > 0.01                  │
             └──────────────────────────────────────────────────┘
                                      │
                                      │ NO
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │            IPTW_p_value < 0.05 OR                │─── YES ──► Tier 2: Moderate Confidence
             │               RSF_VIMP > 0.001                   │
             └──────────────────────────────────────────────────┘
                                      │
                                      │ NO
                                      ▼
                       Tier 3: Low Confidence / Outlier
```

### Core Pipeline Discoveries Summary Table

| Biomarker | Cox HR | Cox $p$ | IPTW HR | IPTW $p$ | RSF VIMP | Assigned Performance Tier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`EGFR`** | 1.7270 | 0.0301 | 1.5262 | 0.0856 | 0.0633 | **Tier 1: High Confidence** |
| **`AGE`** | - | - | - | - | 0.2027 | **Tier 2: Moderate Confidence** |
| **`IDH1`** | 0.3608 | 0.0687 | 0.3098 | 0.0000 | - | **Tier 2: Moderate Confidence** |
| **`FBN3`** | - | - | - | - | 0.0125 | **Tier 2: Moderate Confidence** |
| **`ADAMTS12`** | - | - | - | - | 0.0121 | **Tier 2: Moderate Confidence** |
| **`TP53`** | 0.6708 | 0.1088 | - | - | - | **Tier 3: Low Confidence / Outlier** |

---

## Project Structure & Directory Layout

```text
├── README.md                                 # Master documentation and workflow ledger
├── SCREENING/                                # High-dimensional automated screening directory
│   ├── screening_automated_loop.py           # Iterative multivariate Cox engine
│   ├── top_100_genes_list.csv                # Extracted highest-frequency target panel
│   └── step6_genome_wide_screening_results.csv # Resulting p-value sorted discovery matrix
├── STEP_1/                                   # Cohort Characterization & Merging
│   ├── cohort_characterization.py            # Demographic parsing and parsing script
│   └── mutation_frequencies.png              # Cohort gene frequency horizontal chart
├── STEP_2/                                   # Single-Mutation Kaplan-Meier Analysis
│   ├── single_mutation_km.py                 # Core non-parametric survival curves execution
│   ├── step2_survival_summary_table.csv      # Unadjusted median survival and log-rank p-values
│   └── survival_plots/                       # Generated KM plots directory
├── STEP_3/                                   # Adjusted Cox PH Regression Modeling
│   ├── cox_adjusted_models.py                # Semiparametric multivariate regression script
│   ├── step3_hazard_ratios_table.csv         # Regression coefficient matrix
│   └── cox_survival_forest_plot.png          # High-res comparative forest plot chart
├── STEP_4/                                   # Propensity Score Enhanced Causal Analysis
│   ├── causal_iptw_pipeline.py               # Population re-weighting and SMD balance engine
│   ├── step4_iptw_results_table.csv          # Causal hazard ratios output
│   └── propensity_plots/                     # Kernel Density overlap support visualizations
├── STEP_5/                                   # Co-Mutation Interaction Analysis
│   ├── comutation_interaction_split.py       # 4-group stratification script
│   ├── step5_comutation_hazard_ratios.csv    # Interaction hazard ratios table
│   └── comutation_plots/                     # Multi-trajectory survival function charts
├── STEP_6/                                   # Machine Learning Survival Prediction
│   ├── random_survival_forest.py             # RSF ensemble modeling script
│   ├── step6_rsf_feature_importances.csv     # VIMP mean C-index drop mapping matrix
│   └── ml_plots/                             # Permutation importance horizontal bar graphs
└── STEP_7/                                   # Evidence Integration Framework Synthesis
    ├── final_evidence_integration.py         # Consensus merging and tier classification script
    └── step7_final_biomarker_ledger.csv      # Master project ledger

```

## Technical Setup & Dependencies

To execute this pipeline, ensure your Python environment includes the following scientific and statistical libraries:

* **`scikit-survival`** ($\ge 0.22.0$): For Random Survival Forest models and structured survival arrays.
* **`lifelines`** ($\ge 0.27.0$): For non-parametric Kaplan-Meier fitting and Cox Proportional Hazards modeling.
* **`statsmodels`** ($\ge 0.14.0$): For logistic regression propensity score calculations.
* **`scikit-learn`** ($\ge 1.3.0$): For permutation importance calculations.
* **`pandas`**, **`numpy`**, **`matplotlib`**, **`seaborn`**: For primary matrix data structures and visual plotting.