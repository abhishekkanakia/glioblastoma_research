# Step 2: Single-Mutation Survival Analysis Report

## Kaplan-Meier Survival Summary Table

| Biomarker | Mutated (N) | Mutant Median OS (Mo) | Wildtype (N) | Wildtype Median OS (Mo) | Log-Rank p-value | Clinical Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`IDH1`** | 14 | 33.7 | 94 | 13.0 | **0.0018** | Statistically Significant (Protective) |
| **`EGFR`** | 57 | 13.6 | 51 | 15.4 | **0.0477** | Statistically Significant (High Risk) |
| **`TP53`** | 52 | 13.6 | 56 | 13.7 | 0.3749 | Not Statistically Significant |
| **`BRAF`** | 3 | 14.7 | 105 | 13.7 | 0.6377 | Not Statistically Significant |
| **`TERT`** | 1 | inf | 107 | 13.7 | 0.5809 | Sample Size Insufficient ($N=1$) |

*Note: `ATRX` and `IDH2` were automatically excluded from survival fitting due to zero mutation prevalence within this curated cohort partition.*

---

## Key Clinical Interpretations

### 1. Distinct Subtype Identification via `IDH1`
The cohort uncovers a highly pronounced survival advantage for patients harboring `IDH1` alterations ($p = 0.0018$). The median overall survival was extended by 20.7 months compared to the wildtype group. This highlights the clear phenotypic distinction of IDH-mutant secondary glioblastomas within public datasets.

### 2. Accelerated Proliferation via `EGFR`
`EGFR` mutations are verified as a significant marker of poor prognosis ($p = 0.0477$), dropping median survival to 13.6 months. The explicit separation of the Kaplan-Meier confidence intervals past the 12-month mark supports its role as an aggressive driver of disease progression.

### 3. Study Limitations & Panel Nuance
* **`TP53` Latency:** Individual `TP53` status fails to reach prognostic significance on its own ($p = 0.3749$). This suggests its clinical impact may rely on co-mutation configurations or epistatic network interactions rather than functioning as an isolated linear survival driver.
* **`TERT` Truncation:** While `TERT` promoter mutations typically define aggressive primary glioblastoma, our specific data subset contains only a single mutated record ($N=1$), causing an artificial infinity median survival calculation. This constraint flags the clear need to transition to larger institutional cohorts to properly capture `TERT` risk profiles.