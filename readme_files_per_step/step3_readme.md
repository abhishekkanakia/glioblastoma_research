# Step 3: Adjusted Cox Proportional Hazards Modeling

## Overview
This folder contains the multivariate regression pipeline for the Glioblastoma (GBM) cohort. While Step 2 provided unadjusted, univariate survival curves, Step 3 uses **Cox Proportional Hazards Modeling** to calculate the independent prognostic value of genomic mutations after controlling for key clinical confounding variables (Age and Sex).

---

## Technical Logic & Regression Design

### 1. Confounder Mapping & Covariate Encoding
To prevent clinical characteristics from distorting the calculated effect of genomic alterations, variables are cleaned and converted into structural regression vectors:
* **Event Mapping (`E`)**: Standardized as binary events ($1 = \text{DECEASED}$, $0 = \text{LIVING}$).
* **Categorical Sex Binarization (`SEX_NUM`)**: Converted into a numeric vector to satisfy regression constraints:
  * `1` = **Male** (Any string value starting with 'M' or 'm')
  * `0` = **Female** (Any string value starting with 'F' or 'f')

### 2. Boundary Constraints & Feature Selection
Analysis is strategically narrowed to a sub-panel of 4 target genes (**EGFR, TP53, IDH1, BRAF**). Specific genes from Step 1 are excluded based on statistical and mathematical boundaries:
* `ATRX` & `IDH2`: Bypassed due to complete lack of mutant representations ($N=0$), which prevents convergence.
* `TERT`: Excluded due to a boundary constraint ($N=1$). A sample size of one case violates the empirical event-per-variable requirements needed to compute stable variance matrices.

### 3. Model Architecture
For each included gene, the pipeline executes two separate regressions using the Semiparametric Cox Proportional Hazards framework:

#### A. Unadjusted Model
Evaluates the mutation as a standalone predictor:
$$h(t | x) = h_0(t) \exp(\beta_1 \cdot \text{Gene})$$

#### B. Adjusted Model
Simultaneously evaluates the mutation alongside clinical covariates to isolate its independent baseline risk impact:
$$h(t | x) = h_0(t) \exp(\beta_1 \cdot \text{Gene} + \beta_2 \cdot \text{AGE} + \beta_3 \cdot \text{SEX\_NUM})$$

Where $h(t | x)$ represents the resulting hazard at time $t$, $h_0(t)$ is the baseline hazard function, and $\beta$ values represent the estimated regression coefficients.

---

## Output Spreadsheet Data Definitions

The resulting table file `step3_hazard_ratios_table.csv` tracks regression metrics using the following attributes:

| Variable Column Name | Data Typology | Explicit Definition & Interpretive Context |
| :--- | :--- | :--- |
| `Biomarker` | Categorical / String | The gene targeted for regression modeling (`EGFR`, `TP53`, `IDH1`, `BRAF`). |
| `Model_Type` | Categorical / String | Explains if the row is **Unadjusted** (standalone) or **Adjusted (Age+Sex)** (multivariate model controlling for age and sex). |
| `HR` | Floating Point | **Hazard Ratio ($exp(\beta)$)**. The exponentiated regression coefficient. It measures the relative change in the risk of death per unit change in the feature space.<br>• $\mathbf{HR > 1.0}$: Associated with **increased risk/mortality** (detrimental prognostic biomarker).<br>• $\mathbf{HR < 1.0}$: Associated with a **protective effect** (favorable prognostic biomarker).<br>• $\mathbf{HR = 1.0}$: Absolute null hazard effect. |
| `Lower_95` | Floating Point | The lower boundary of the 95% Wald Confidence Interval for the Hazard Ratio. |
| `Upper_95` | Floating Point | The upper boundary of the 95% Wald Confidence Interval for the Hazard Ratio. |
| `p_value` | Floating Point | Two-sided Wald test probability score measuring significance.<br>• $\mathbf{p < 0.05}$: The association is statistically stable and reproducible.<br>• **Note on Confounding**: If a gene's p-value shifts across thresholds between models (e.g., `IDH1` moving from $0.004$ unadjusted to $0.068$ adjusted), it indicates significant clinical confounding by age or sex. |

---

## Forest Plot Graphic Layout Definitions

### Output Asset: `cox_survival_forest_plot.png`
The generated forest plot visually aggregates and compares the hazard profiles across all models.

* **Y-Axis Positions**: Unique rows assigned to each target biomarker (`EGFR`, `TP53`, `IDH1`, `BRAF`), maintaining a clean top-to-bottom list orientation.
* **X-Axis Values**: Logarithmically scaled linear window mapping raw exponentiated Hazard Ratios (`HR`).
* **Vertical Dashed Line ($x=1.0$)**: The absolute **null intercept marker**. If a gene's horizontal confidence interval line physically crosses or touches this boundary, the mutation's impact on survival is not statistically significant at the 95% confidence level.
* **Red Circles (`o`) & Bars**: Represent **Unadjusted Hazard Ratios** and their accompanying 95% confidence bounds.
* **Blue Squares (`s`) & Bars**: Represent **Adjusted Hazard Ratios** and their accompanying 95% confidence bounds. A vertical offset of $0.15$ is applied to prevent visual overlap between the adjusted and unadjusted models.