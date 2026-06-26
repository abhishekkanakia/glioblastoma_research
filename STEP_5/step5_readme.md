# Step 5: Co-Mutation Interaction Analysis

## Overview
This folder contains the analytical pipeline tracking secondary somatic interactions within the Glioblastoma (GBM) cohort. While preceding steps treated genomic alterations as independent features, Step 5 explicitly partitions the cohort into multi-tier mutually exclusive strata. This enables investigation into how discrete combinations of mutations define distinct molecular survival phenotypes or drive synergistic/antagonistic survival changes.

---

## Technical Logic & Stratification Architecture

### 1. Distinct Molecular Stratification (4-Way Split)
For each targeted pair interaction ($Gene_A + Gene_B$), individual patients are categorized into one of four mutually exclusive clinical risk tiers:
* **Neither**: Wild-Type for both genes. Serves as the stable biological baseline control layer.
* **$Gene_A$ Only**: Mutation present exclusively in the first gene column.
* **$Gene_B$ Only**: Mutation present exclusively in the second gene column.
* **Both**: Synchronous dual co-mutation condition harboring variants in both target loci.

### 2. Pre-flight Sample Size Audit
The pipeline records raw patient allocations using explicit frequency counts before compiling downstream scripts. If the synchronous dual co-mutation row count maps to zero ($N=0$), the system logs an omission warning to prevent model overfitting or computational matrix alignment crashes.

### 3. Multivariate Cox Interaction Regression
To quantify the hazard risk gradient across these molecular groups, dummy variables are generated for each categorization layer. 
* **Baseline Omission (Reference Group)**: The dummy column reflecting the `Neither` stratum is structurally omitted from the dataset (`drop_first=False` accompanied by explicit feature slicing). This designates the unmutated state as the mathematical intercept benchmark.
* **Model Configuration**: The remaining three categories are evaluated inside the Cox model alongside standard clinical covariates (Age and Sex):

$$h(t \mid X) = h_0(t) \exp(\beta_1 \cdot \text{Age} + \beta_2 \cdot \text{Sex\_Num} + \beta_3 \cdot \text{Group}_{\text{A\_Only}} + \beta_4 \cdot \text{Group}_{\text{B\_Only}} + \beta_5 \cdot \text{Group}_{\text{Both}})$$

### 4. Boundary Constraint Tolerances
* **ATRX+IDH1**: Missing from output logs entirely due to complete sample size zero constraints ($N=0$) within this specific cohort split, blocking coefficient convergence.
* **TERT+EGFR**: Demonstrates a severe boundary constraint where a single patient populates the `Both` cell ($N=1$). This extreme sample limitation results in an unstable standard error calculation, generating an artificially miniscule Hazard Ratio and an infinite upper confidence bound ($inf$). These statistical artifacts are preserved in the metrics table to flag data limitations.

---

## Output Spreadsheet Data Definitions

The resulting analysis spreadsheet file `step5_comutation_hazard_ratios.csv` maps interaction attributes using the following properties:

| Variable Column Name | Data Typology | Explicit Definition & Interpretation Context |
| :--- | :--- | :--- |
| `Pair` | Categorical / String | The specific gene sequence combination targeted for multi-tier interaction analysis (e.g., `TP53+EGFR`). |
| `CoMut_Group_N` | Integer | The exact sample size count of individual patients simultaneously harboring mutations in **both** target genes. |
| `Adjusted_Interaction_HR` | Floating Point | **Adjusted Tered Hazard Ratio**. Measures the risk of death for the dual-mutated (`Both`) group relative to the completely unmutated baseline (`Neither`), after controlling for age and sex.<br>• $\mathbf{HR > 1.0}$: Indicates a synergistic compounding risk profile.<br>• $\mathbf{HR < 1.0}$: Indicates a protective profile or a slower mortality rate. |
| `Lower_95` | Floating Point | The lower boundary of the 95% Wald Confidence Interval for the dual co-mutation hazard ratio. |
| `Upper_95` | Floating Point | The upper boundary of the 95% Wald Confidence Interval. Resolves to `inf` under extreme single-sample or highly-censored constraints. |
| `p_value` | Floating Point | Wald test probability score measuring interaction significance. Values below $0.05$ indicate that the combination creates a distinct, reproducible survival phenotype that remains significant after controlling for clinical covariates. |

---

## Explicit Graphics Layout Interpretations

### Saved Visualizations Directory: `comutation_plots/[GeneA]_[GeneB]_survival_curve.png`
Unlike single-gene plots, these figures track four separate non-parametric survival function pathways across a single timeline grid to emphasize phenotypic differences:

* **X-Axis Line**: Patient evaluation timeline window, quantified uniformly in **Months**.
* **Y-Axis Curve**: Overall Survival Probability $S(t)$, scaled from $0.0$ to $1.02$.
* **Green Trajectory Line**: Baseline survival trend for the completely unmutated population (`Neither`).
* **Orange Trajectory Line**: Survival trajectory for patients carrying only the first mutation (`Gene A Only`).
* **Blue Trajectory Line**: Survival trajectory for patients carrying only the second mutation (`Gene B Only`).
* **Red Trajectory Line**: Survival trend for the dual-co-mutated subgroup (`Both`). Allows for immediate visual assessment of whether the combination dramatically accelerates mortality compared to single-mutation cohorts.

---