# Step 1: Cohort Characterization & Merging

## Overview
This folder contains the initial data processing pipeline for the Glioblastoma (GBM) cohort. It handles data ingestion, filtering based on explicit clinical criteria, merging genomic and clinical matrices, and generating baseline population statistics (Table 1) and mutation frequency distributions.

---

## Data Selection & Processing Logic

1. **Patient Identifier Matching:**
   * The `Tumor_Sample_Barcode` string from the mutation dataset is truncated to its first 12 characters (`.str.slice(0,12)`) to yield a uniform `PATIENT_ID` that maps directly onto the clinical dataset rows.
2. **Target Gene Filtering:**
   * Analysis is restricted to a precise panel of 7 target genes: **ATRX, TERT, BRAF, EGFR, TP53, IDH1, and IDH2**.
3. **Patient vs. Sample Ranking:**
   * Mutations are aggregated and evaluated **per unique patient (across patients)** rather than per tissue sample. If a patient possesses multiple variant rows for a single gene, the evaluation logic compresses this into a binary indicator ($1 = \text{Mutated}$, $0 = \text{Wild-Type}$) using a logical ceiling (`> 0`).
4. **Clinical Data Inclusions/Exclusions:**
   * All patient rows missing overall survival times (`OS_MONTHS`) are structurally dropped.
   * Patients recorded with an overall survival time of less than or equal to $0$ months (`OS_MONTHS > 0`) are excluded to ensure valid mathematical boundaries for survival forecasting.

---

## Variable Definitions

The final analytical output file (`gbm_merged_data.csv`) includes the following attributes:

### 1. Demographics & Stratification Factors
* `PATIENT_ID` *(String)*: Unique alphanumeric 12-character identifier matching TCGA conventions.
* `AGE` *(Numeric)*: Patient age at time of initial diagnosis, represented in years.
* `SEX` *(Categorical/String)*: Biological sex of the patient (`Male`, `Female`).
* `THERAPY` *(Categorical/String)*: First-line therapeutic intervention administered (e.g., `Standard Radiation`, `TMZ Chemoradiation, TMZ Chemo`).

### 2. Time-to-Event Survival Outcomes
* `OS_STATUS` *(Categorical/String)*: Overall survival status vital event flag (`1:DECEASED`, `0:LIVING`).
* `OS_MONTHS` *(Numeric)*: Time from initial diagnostic confirmation to either death or date of last follow-up contact, quantified in months. 
* `DFS_STATUS` *(Categorical/String)*: Disease-free survival status flag (`1:Recurred/Progressed`, `0:DiseaseFree`).
* `DFS_MONTHS` *(Numeric)*: Time in months from initial treatment completion to disease progression, recurrence, or right-censoring.

### 3. Binary Genomic Mutation Columns
* `ATRX`, `TERT`, `BRAF`, `EGFR`, `TP53`, `IDH1`, `IDH2` *(Binary Numeric)*:
    * `1`: Patient possesses one or more verified mutations in this gene.
    * `0`: Gene is classified as Wild-Type (unmutated or missing somatic variant proof) for this patient.

---

## Explicit Artifact Explanations

### 1. Console Text Output (`Table 1: Cohort Characteristics`)
* **Total Analytical Cohort (N)**: Total row count of patients who passed the biological selection criteria.
* **Age (Years)**: Sample mean ($\mu$) $\pm$ sample standard deviation ($\sigma$) computed directly across all compliant patient ages.
* **Sex - [Category]**: Absolute count and percentage distribution calculated relative to the total analytical cohort ($N$).
* **Missing MGMT Status**: Absolute and percentage count of null elements (`NaN`) specifically discovered within the MGMT clinical matrix feature space.

### 2. Generated Plot: `mutation_frequencies.png`
* **Y-Axis Value (`Mutation Frequency (%)`)**: Represents the absolute percentage of unique **patients** within the curated, filtered cohort who harbor a mutation in that gene. 
* **Mathematical Formula**: 
$$\text{Mutation Frequency} = \left( \frac{\sum_{i=1}^{N} X_{\text{gene}, i}}{N} \right) \times 100$$
Where $X_i \in \{0, 1\}$ represents the binary mutation marker for patient $i$, and $N$ represents the total valid patient count within the processed cohort.

---
