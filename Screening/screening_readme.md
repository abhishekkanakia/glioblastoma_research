# Screening Step: High-Dimensional Biomarker Discovery & Screening

## Overview
This folder contains the automated high-dimensional screening pipeline designed to systematically discover hidden genomic prognostic biomarkers within the Glioblastoma (GBM) cohort. The pipeline ingests raw, unfiltered somatic mutation data, filters and ranks genes according to custom biological constraints, constructs a wide-format genomic matrix, and executes a high-throughput automated screening loop using adjusted Cox Proportional Hazards regression.

---

## Detailed Gene Selection Methodology & Logic

To ensure absolute transparency for manuscript documentation and peer review, the selection and ranking of the candidate genes in `top_100_genes_list.csv` follow a strict multi-step protocol:

1. **Patient-Level Aggregation (Across Patients vs. Across Samples):**
   * Genes are evaluated and ranked strictly **across unique patients**, not across individual tissue samples or entries. 
   * Raw sample barcodes (`Tumor_Sample_Barcode`) are truncated to their first 12 characters (`Clean_Patient_ID`) to isolate unique participants. The pipeline uses a distinct grouping function (`.groupby('Hugo_Symbol')['Clean_Patient_ID'].nunique()`) to ensure each patient is only counted once per gene, eliminating sample-inflation biases.

2. **Mandatory Canonical Driver Inclusion:**
   * To maintain consistency with established glioblastoma literature and professor directives, a panel of mandatory biological drivers is structurally forced into the matrix: **PTEN, CDKN2A, EGFR, TP53, and IDH1**. 
   * If any of these mandatory genes are absent from a specific raw slice, they are manually appended with baseline frequency metrics of $0$ to keep downstream pipeline loops operational.

3. **Top 100 Isolation:**
   * After calculating patient-level frequencies and embedding mandatory drivers, the entire genome-wide dataset is sorted in descending order. The top 100 highest-frequency genes are extracted to define the screening list.

---

## Metric & Variable Definitions

### 1. Initial Screening File (`top_100_genes_list.csv`)
* `Gene` *(String)*: The official HUGO Gene Nomenclature Committee (HGNC) symbol mapping the mutated locus.
* `Patient_Count` *(Integer)*: The absolute number of unique individual patients in the dataset who harbor at least one non-synonymous somatic mutation in this gene.
* `Frequency_Pct` *(Floating Point)*: **Patient Mutation Frequency Percentage**. This defines the precise proportion of your final analytical cohort ($N = 108$ patients established in Step 1) affected by mutations in the gene.
  * **Mathematical Formula:**
$$\text{Frequency\_Pct} = \left( \frac{\text{Unique Patient Count with Mutation}}{\text{Total Analytical Cohort Size } (N=108)} \right) \times 100$$

### 2. Wide-Format Genomic Matrix (`genomic_matrix`)
* `Clean_Patient_ID` *(Index)*: Cleaned 12-character matching key.
* Columns 1–100 *(Binary Integers)*: Each of the top 100 discovered genes is converted into a structured binary vector:
  * `1`: Patient has one or more documented mutations in this gene.
  * `0` (or `NaN` filled to `0` via `.fillna(0)`): Patient is classified as Wild-Type for this gene.

### 3. Automated Regression Output (`step6_genome_wide_screening_results.csv`)
* `Gene` *(String)*: Target mutation evaluated.
* `Mutation_Count` *(Integer)*: Total absolute cases of the mutation within the active $108$-patient analytical pool.
* `Adjusted_HR` *(Floating Point)*: Exponentiated Cox regression coefficient ($exp(\beta)$) calculated after adjusting for clinical confounders. Values $>1.0$ indicate elevated risk; values $<1.0$ indicate a protective trend.
* `Lower_95` / `Upper_95` *(Floating Point)*: Explicit Wald 95% Confidence Interval boundaries bound to the adjusted hazard coefficient.
* `p_value` *(Floating Point)*: Two-sided Wald test probability score.

---

## Automated Screening Loop Execution & Boundary Constraints

```text
       [ Top 100 Patient-Ranked Genes ]
                     |
                     ▼
       [ Reconstruct Wide Matrix ]
 (Merge with Step 1 Clinical Data on Patient ID)
                     |
                     ▼
     [ Automated Multi-Variable Cox Loop ]
  (Iterate through each gene individually)
                     |
       ┌─────────────┴─────────────┐
       ▼                           ▼
[ Mutation Count ≤ 1 ]     [ Mutation Count > 1 ]
       │                           │
       ▼ (Skip Locus)              ▼ (Fit Adjusted Model)
(Prevents Matrix Singularities)  h(t) = h0(t)*exp(ß1*Gene + ß2*Age + ß3*Sex)
                                   │
                                   ▼
                       [ Document Coefficients ]
                      Filter by Model p_value < 0.05
```
* **Confounder Control:** Every model fitted during the screen automatically incorporates clinical features to isolate true genetic impact:
$$\text{Model Features} = [\text{Gene}_{\text{Target}}, \text{AGE}, \text{SEX\_NUM}]$$

* **Boundary Constraint Filter:** To prevent non-convergence, infinite standard errors, or matrix singularities caused by extremely sparse categories, a logical validation step checks total frequencies: `if screening_df[gene].sum() <= 1: continue`. Any gene where $\le 1$ patient has a mutation is skipped, ensuring robust regression results.

* **Significant Discoveries Extraction:** The master spreadsheet filters all 100 iterations down to a final table of hits where the adjusted covariate baseline crosses standard significance thresholds ($p\_value < 0.05$).

---
