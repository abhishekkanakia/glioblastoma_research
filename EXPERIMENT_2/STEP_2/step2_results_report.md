# Experiment 2 — Step 2: Unadjusted Kaplan-Meier & Log-Rank Survival Analytics

## Objective & Study Track
This directory contains the computational outputs for **Experiment 2: Step 2**. 

The goal of this phase is to establish the baseline, unadjusted overall survival (OS) trajectories for each of our top 100 dynamically screened genes. By splitting the 253-patient cohort into mutated vs. wildtype strata for each target locus, we estimate median survival thresholds and use mathematical Log-Rank tests to determine if individual genetic mutations alter mortality trajectories before adjusting for secondary clinical confounding vectors.

---

## Data Schema & Variable Dictionary

The master results spreadsheet (**`step2_km_logrank_results.csv`**) tracks the unadjusted statistical properties of all 100 screened genes using the following parameters:

| Variable Name | Data Type | Definition / Mathematical Meaning |
| :--- | :---: | :--- |
| `Biomarker` | String | HGNC approved symbol for the dynamically screened gene target. |
| `Mutated_N` | Integer | Total count of unique patients in the cohort carrying a somatic mutation in this gene. |
| `Mutated_Median_OS` | Float | The timepoint (in months) at which exactly 50% of the mutated patient stratum has succumbed to mortality. Values marked `inf` indicate that the survival curve did not drop below 50% during the documented clinical follow-up window. |
| `Wildtype_N` | Integer | Total count of unique patients in the cohort carrying the wildtype allele ($N_{\text{wt}}$). |
| `Wildtype_Median_OS`| Float | The timepoint (in months) at which exactly 50% of the wildtype patient stratum has succumbed to mortality. |
| `LogRank_p_value` | Float | The statistical probability derived from the non-parametric Log-Rank $\chi^2$ test evaluating the null hypothesis ($H_0$) that there is no difference in survival distribution between the mutated and wildtype strata. |

---

## Unadjusted Step 2 Experimental Results Ledger ($N = 253$)

Below is the complete 100-biomarker Kaplan-Meier survival profile, organized exactly as exported by the automated pipeline:

| Biomarker | Mutated $N$ | Mutated Median OS (Mo.) | Wildtype $N$ | Wildtype Median OS (Mo.) | Log-Rank $p$-value | Preliminary Status ($p < 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **STAG2** | 8 | 5.2 | 245 | 13.7 | **0.0004** | Statistically Significant (High Risk) |
| **IDH1** | 14 | 33.7 | 239 | 13.0 | **0.0023** | Statistically Significant (Protective) |
| **DNAH2** | 7 | 5.4 | 246 | 13.6 | **0.0089** | Statistically Significant (High Risk) |
| **PCLO** | 22 | 10.4 | 231 | 13.7 | **0.0197** | Statistically Significant (High Risk) |
| **CALN1** | 7 | 8.8 | 246 | 13.6 | **0.0334** | Statistically Significant (High Risk) |
| **DSP** | 7 | 12.2 | 246 | 13.6 | **0.0340** | Statistically Significant (High Risk) |
| **DNAH8** | 10 | 7.4 | 243 | 13.6 | **0.0495** | Statistically Significant (High Risk) |
| *FGD5* | 12 | 9.8 | 241 | 13.6 | 0.0556 | Marginally Significant Trend |
| *TEX15* | 10 | 8.4 | 243 | 13.6 | 0.0623 | Marginally Significant Trend |
| *TAF1L* | 8 | 5.4 | 245 | 13.6 | 0.0872 | Marginally Significant Trend |
| *ADAMTS12* | 8 | inf | 245 | 13.3 | 0.0899 | Marginally Significant Trend |
| TTN | 60 | 13.1 | 193 | 13.4 | 0.8425 | Non-Significant Background Variant |
| PTEN | 58 | 13.6 | 195 | 13.3 | 0.6340 | Non-Significant Background Variant |
| EGFR | 57 | 13.6 | 196 | 13.4 | 0.2844 | Non-Significant Background Variant |
| TP53 | 52 | 13.6 | 201 | 13.4 | 0.2540 | Non-Significant Background Variant |
| MUC16 | 43 | 11.7 | 210 | 13.7 | 0.1154 | Non-Significant Background Variant |
| FLG | 29 | 13.6 | 224 | 13.4 | 0.6003 | Non-Significant Background Variant |
| PIK3R1 | 25 | 13.7 | 228 | 13.3 | 0.7493 | Non-Significant Background Variant |
| NF1 | 22 | 11.7 | 231 | 13.6 | 0.5092 | Non-Significant Background Variant |
| SPTA1 | 24 | 12.6 | 229 | 13.7 | 0.3398 | Non-Significant Background Variant |
| RYR2 | 23 | 13.9 | 230 | 13.3 | 0.8298 | Non-Significant Background Variant |
| PIK3CA | 22 | 13.1 | 231 | 13.6 | 0.3805 | Non-Significant Background Variant |
| HMCN1 | 19 | 11.2 | 234 | 13.6 | 0.4919 | Non-Significant Background Variant |
| MUC17 | 20 | 13.9 | 233 | 13.3 | 0.9260 | Non-Significant Background Variant |
| USH2A | 20 | 13.6 | 233 | 13.4 | 0.6276 | Non-Significant Background Variant |
| RB1 | 15 | 12.2 | 238 | 13.6 | 0.6420 | Non-Significant Background Variant |
| AHNAK2 | 17 | 11.7 | 236 | 13.6 | 0.6221 | Non-Significant Background Variant |
| COL6A3 | 15 | 13.6 | 238 | 13.4 | 0.8301 | Non-Significant Background Variant |
| SYNE1 | 15 | 12.2 | 238 | 13.6 | 0.5913 | Non-Significant Background Variant |
| OBSCN | 15 | 13.9 | 238 | 13.3 | 0.8011 | Non-Significant Background Variant |
| RELN | 14 | 12.3 | 239 | 13.4 | 0.5405 | Non-Significant Background Variant |
| DNAH5 | 12 | 10.4 | 241 | 13.6 | 0.5063 | Non-Significant Background Variant |
| GPR98 | 11 | 14.7 | 242 | 13.4 | 0.5931 | Non-Significant Background Variant |
| FRAS1 | 11 | 7.6 | 242 | 13.4 | 0.4873 | Non-Significant Background Variant |
| LRP2 | 14 | 11.8 | 239 | 13.6 | 0.8922 | Non-Significant Background Variant |
| PKHD1 | 12 | 12.3 | 241 | 13.6 | 0.3158 | Non-Significant Background Variant |
| DOCK5 | 13 | 20.4 | 240 | 13.3 | 0.1426 | Non-Significant Background Variant |
| TCHH | 12 | 13.9 | 241 | 13.3 | 0.7232 | Non-Significant Background Variant |
| CNTNAP2 | 9 | 14.9 | 244 | 13.3 | 0.9801 | Non-Significant Background Variant |
| KEL | 13 | 12.3 | 240 | 13.6 | 0.7384 | Non-Significant Background Variant |
| DNAH3 | 11 | 15.0 | 242 | 13.3 | 0.3829 | Non-Significant Background Variant |
| FCGBP | 12 | 11.3 | 241 | 13.6 | 0.5275 | Non-Significant Background Variant |
| PCDHA1 | 11 | 9.9 | 242 | 13.6 | 0.9287 | Non-Significant Background Variant |
| RIMS2 | 11 | 17.1 | 242 | 13.3 | 0.4316 | Non-Significant Background Variant |
| MROH2B | 11 | 11.8 | 242 | 13.4 | 0.7295 | Non-Significant Background Variant |
| RBM47 | 11 | 13.1 | 242 | 13.4 | 0.5036 | Non-Significant Background Variant |
| HRNR | 9 | 15.0 | 244 | 13.3 | 0.5363 | Non-Significant Background Variant |
| DCHS2 | 11 | 10.4 | 242 | 13.6 | 0.1018 | Non-Significant Background Variant |
| SDK1 | 10 | 14.4 | 243 | 13.3 | 0.9165 | Non-Significant Background Variant |
| RYR3 | 11 | 16.9 | 242 | 13.4 | 0.6475 | Non-Significant Background Variant |
| MUC5B | 10 | 11.0 | 243 | 13.4 | 0.3715 | Non-Significant Background Variant |
| FBN3 | 9 | 11.5 | 244 | 13.6 | 0.3759 | Non-Significant Background Variant |
| GABRA6 | 9 | 9.1 | 244 | 13.6 | 0.5473 | Non-Significant Background Variant |
| DNAH11 | 10 | 13.6 | 243 | 13.3 | 0.8015 | Non-Significant Background Variant |
| HCN1 | 9 | 11.8 | 244 | 13.6 | 0.4237 | Non-Significant Background Variant |
| FLG2 | 9 | 11.7 | 244 | 13.6 | 0.9009 | Non-Significant Background Variant |
| APOB | 9 | 7.6 | 244 | 13.4 | 0.3407 | Non-Significant Background Variant |
| CHD5 | 7 | 11.2 | 246 | 13.4 | 0.6133 | Non-Significant Background Variant |
| DMD | 10 | 8.8 | 243 | 13.6 | 0.1981 | Non-Significant Background Variant |
| MACF1 | 7 | 26.7 | 246 | 13.4 | 0.4024 | Non-Significant Background Variant |
| PDGFRA | 10 | 7.0 | 243 | 13.4 | 0.1899 | Non-Significant Background Variant |
| SPAG17 | 8 | 13.7 | 245 | 13.3 | 0.7970 | Non-Significant Background Variant |
| MXRA5 | 8 | 15.3 | 245 | 13.4 | 0.8757 | Non-Significant Background Variant |
| BCOR | 8 | 13.6 | 245 | 13.4 | 0.5685 | Non-Significant Background Variant |
| COL1A2 | 6 | 11.8 | 247 | 13.4 | 0.6829 | Non-Significant Background Variant |
| GRIN2A | 10 | 16.7 | 243 | 13.1 | 0.7551 | Non-Significant Background Variant |
| TMEM132D | 9 | 11.0 | 244 | 13.6 | 0.2350 | Non-Significant Background Variant |
| DSG3 | 8 | 25.4 | 245 | 13.3 | 0.1893 | Non-Significant Background Variant |
| MYH2 | 10 | 10.3 | 243 | 13.6 | 0.1631 | Non-Significant Background Variant |
| PLEKHG4B | 9 | 13.6 | 244 | 13.4 | 0.7321 | Non-Significant Background Variant |
| SEMA3C | 9 | 5.8 | 244 | 13.6 | 0.1138 | Non-Significant Background Variant |
| FAT3 | 8 | 12.5 | 245 | 13.6 | 0.3467 | Non-Significant Background Variant |
| NLRP5 | 9 | 18.0 | 244 | 13.3 | 0.4402 | Non-Significant Background Variant |
| NLRP12 | 8 | 12.0 | 245 | 13.6 | 0.6648 | Non-Significant Background Variant |
| AFF2 | 8 | inf | 245 | 13.3 | 0.1600 | Non-Significant Background Variant |
| GRM8 | 8 | 7.0 | 245 | 13.4 | 0.3948 | Non-Significant Background Variant |
| PIK3CG | 8 | 8.8 | 245 | 13.6 | 0.2652 | Non-Significant Background Variant |
| PRDM9 | 8 | 12.2 | 245 | 13.4 | 0.8560 | Non-Significant Background Variant |
| CHD9 | 7 | 16.9 | 246 | 13.4 | 0.4942 | Non-Significant Background Variant |
| DNAH9 | 7 | 24.2 | 246 | 13.3 | 0.2461 | Non-Significant Background Variant |
| LZTR1 | 6 | 3.7 | 247 | 13.4 | 0.5673 | Non-Significant Background Variant |
| SCN9A | 9 | 10.6 | 244 | 13.6 | 0.5477 | Non-Significant Background Variant |
| TSHZ2 | 8 | 6.1 | 245 | 13.6 | 0.4247 | Non-Significant Background Variant |
| CSMD3 | 7 | 15.0 | 246 | 13.3 | 0.7406 | Non-Significant Background Variant |
| KMT2C | 8 | 13.3 | 245 | 13.6 | 0.1249 | Non-Significant Background Variant |
| TG | 6 | 15.9 | 247 | 13.3 | 0.6959 | Non-Significant Background Variant |
| LAMA1 | 5 | 12.6 | 248 | 13.6 | 0.5704 | Non-Significant Background Variant |
| RPL5 | 8 | 13.9 | 245 | 13.3 | 0.8029 | Non-Significant Background Variant |
| KIF13A | 8 | 12.9 | 245 | 13.6 | 0.6659 | Non-Significant Background Variant |
| ADAM28 | 7 | 13.6 | 246 | 13.4 | 0.3756 | Non-Significant Background Variant |
| RIMBP2 | 5 | 12.9 | 248 | 13.6 | 0.5936 | Non-Significant Background Variant |
| TRPM2 | 7 | inf | 246 | 13.4 | 0.8208 | Non-Significant Background Variant |
| TRPV6 | 7 | 14.5 | 246 | 13.4 | 0.7498 | Non-Significant Background Variant |
| SCN10A | 8 | 26.7 | 245 | 13.1 | 0.1023 | Non-Significant Background Variant |
| OR8K3 | 7 | 17.1 | 246 | 13.3 | 0.9552 | Non-Significant Background Variant |
| ABCC9 | 7 | 11.5 | 246 | 13.4 | 0.9683 | Non-Significant Background Variant |
| SPTBN5 | 6 | 14.4 | 247 | 13.3 | 0.2207 | Non-Significant Background Variant |
| FAT2 | 6 | 15.9 | 247 | 13.4 | 0.7835 | Non-Significant Background Variant |
| PCDHB7 | 6 | 12.7 | 247 | 13.6 | 0.4540 | Non-Significant Background Variant |
| SLCO6A1 | 8 | 15.8 | 245 | 13.4 | 0.7247 | Non-Significant Background Variant |

---

## Core Bioinformatic Observations & Insights

1. **The Core High-Risk Signal (STAG2):** In this 253-patient cohort, STAG2 mutations emerged as a highly severe survival outlier. Patients with mutated STAG2 exhibited an unadjusted median overall survival of just **5.2 months** compared to 13.7 months for wildtype ($p = 0.0004$), highlighting it as a crucial driver candidate for our downstream machine learning validation.
2. **The Secondary Protective Signal (IDH1):** Confirming historical oncology expectations, IDH1 mutations present a highly pronounced protective effect. Mutated individuals survived a median of **33.7 months** vs. 13.0 months for wildtype ($p = 0.0023$). 
3. **Novel Genomic Discoveries:** The expanded 100-gene screen successfully flagged lower-frequency candidates like DNAH2 ($p=0.0089$, median OS 5.4 mo.) and DNAH8 ($p=0.0495$, median OS 7.4 mo.) that would have been completely missed under traditional target panel limits.

---

## Codebase Artifacts & Output Specifications
* **`step2_km_logrank_results.csv`**: The comprehensive master output table containing the calculated statistical limits for all 100 genes, sorted automatically by significance ($p$-value ascending).
* **`plots/km_curves/`**: The automated plot generation pipeline exports publication-ready vector graphics (`.png`) for all top-performing genes displaying significant survival separation ($p < 0.05$).