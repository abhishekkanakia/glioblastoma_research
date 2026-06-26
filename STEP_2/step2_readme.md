# Step 2: Single-Mutation Kaplan-Meier Survival Analysis

## Overview
This folder houses the analytical pipeline responsible for conducting unadjusted, single-gene time-to-event statistical forecasting. It partitions the curated glioblastoma patient cohort based on the presence or absence of explicit genomic variations, fits probability functions using the non-parametric Kaplan-Meier estimator, evaluates significance variations with the log-rank test, and exports production-grade visualizations.

---

## Technical Logic & Mathematical Framework

### 1. Data Ingestion & Event Event Re-mapping
* **Input Origin:** Consumes the exact structured output generated from the initial step pipeline (`../STEP_1/gbm_merged_data.csv`).
* **Binary Censoring Alignment:** Somatic data from string event statuses (`OS_STATUS`) is structurally cast to a tight binary representation ($E \in \{0, 1\}$) inside a clean array column `E`:
  * `1` (**Event Observed**): Patient is explicitly recorded as `1:DECEASED`.
  * `0` (**Right-Censored**): Patient is recorded as `0:LIVING`. This bounds survival modeling so that individuals who have not undergone the terminal event within the data collection window are properly treated as right-censored observations.

### 2. Analytical Stratification & Boundary Resiliency
* **Cohorting Matrix:** For each targeted genomic element (e.g., `EGFR`, `TP53`, `IDH1`, etc.), patients are split down logical vector boundaries into two mutually exclusive structural arrays:
  * **Mutated Layer ($1$):** Patients harboring verified mutations or variant profiles in the column.
  * **Wild-Type Layer ($0$):** Patients exhibiting normal genomic expressions or unmutated sequencing.
* **Structural Zero Resiliency Check:** Before executing statistical computations, the algorithm computes a structural sum across the gene binary array (`df[gene].sum() == 0`). If a target variant lacks representation entirely in this temporal data block (as observed with `IDH2` or `ATRX` in specific iterations), the script bypasses it to protect calculations from divide-by-zero errors or matrix rank deficiencies.

### 3. Kaplan-Meier Estimation & Median Lifespan Calculation
* **Mathematical Function:** For both stratified branches, the pipeline fits the standard non-parametric survival function estimator $S(t)$:
$$\hat{S}(t) = \prod_{t_i \le t} \left(1 - \frac{d_i}{n_i}\right)$$
Where $t_i$ represents a point in time where at least one terminal event occurred, $d_i$ is the exact count of documented terminal events (deaths) at moment $t_i$, and $n_i$ corresponds to the surviving total population size at risk immediately prior to $t_i$.
* **Median OS Inference:** The pipeline extracts the exact milestone where the calculated probability boundary crosses 0.5 ($\hat{S}(t) = 0.5$). If a group's cumulative mortality rate never reaches $50\%$ due to small sample size or extensive right-censoring, the value resolves mathematically as `inf` (Infinity), indicating that a median timeframe cannot yet be determined from the available records.

### 4. Log-Rank Significance Testing
* To mathematically assess if the observed deviation between the two probability curves is distinct or merely statistical variance, an unadjusted log-rank test is conducted. 
* The statistical calculation maps the distribution of occurrences across all time intervals to determine a $\chi^2$ value and maps the final significance boundary down to a raw **Log-Rank p-value** output string.

---

## Output File Data Definitions

The structural table artifact exported as `step2_survival_summary_table.csv` maintains the following attributes:

| Variable Column Name | Data Typology | Explicit Definition & Computational Context |
| :--- | :--- | :--- |
| `Biomarker` | Categorical / String | The specific gene sequence targeted for stratification (e.g., `EGFR`, `IDH1`). |
| `Mutated_N` | Integer | The final count of unique individual patients carrying a mutation in that gene who passed clinical filtering. |
| `Mutated_Median_OS` | Floating Point / String | The estimated median survival timeframe for the mutated population, expressed in months. Resolves to `inf` if the survival curve fails to drop to 0.5. |
| `Wildtype_N` | Integer | The final count of unique individual patients tracking as Wild-Type (unmutated) for that specific gene feature. |
| `Wildtype_Median_OS`| Floating Point / String | The estimated median survival timeframe for the wildtype population, expressed in months. |
| `LogRank_p_value` | Floating Point | The precise calculated probability threshold derived from the log-rank test. A metric boundary below $0.05$ indicates a statistically significant difference in survival times between the mutated and wild-type groups. |

---

## Explicit Graphic Visual Explanations

### Saved Assets Directory: `survival_plots/[Gene]_survival_curve.png`
Each visualization represents a high-resolution, independent survival distribution plot capturing several metrics:
* **X-Axis Line:** Timeline tracking patient observation duration, explicitly expressed in **Months**.
* **Y-Axis Curve:** Overall Survival Probability $S(t)$, scaled uniformly from $0.0$ to $1.02$.
* **Blue Shaded Horizon:** The estimated $95\%$ statistical confidence interval surrounding the **Wildtype** population trajectory.
* **Red Shaded Horizon:** The estimated $95\%$ statistical confidence interval surrounding the **Mutated** population trajectory.
* **Floating Text Meta-Box:** An on-chart analytical annotation tracking summary metrics (Log-Rank p-value, Mutated vs Wildtype counts, and median outcomes) to guarantee that observers can parse chart findings independently without cross-referencing core spreadsheets.

---
