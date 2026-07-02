import pandas as pd

mutations_df = pd.read_excel("core_data_subset/data_mutations.xlsx")
clinical_df = pd.read_excel("core_data_subset/data_clinical_patient.xlsx", header = 4)

# getting rid of white space 
clinical_df.columns = clinical_df.columns.str.strip()
mutations_df.columns = mutations_df.columns.str.strip()

#from mutations excel, take the patient ID but only the first 12 digits so it'll match with clinical's format.
mutations_df["PATIENT_ID"] = mutations_df["Tumor_Sample_Barcode"].str.slice(0,12)

#genes we need to focus on
target_genes = ["ATRX", "TERT", "BRAF", "EGFR", "TP53", "IDH1", "IDH2"]

#create a new df with keeping only the rows where the hugo symbol is one of the ones we care about
filtered_mutations_df = mutations_df[mutations_df["Hugo_Symbol"].isin(target_genes)].copy()

#pivot table: rows are patients columns are the hugo symbols
mutation_pivot = filtered_mutations_df.pivot_table(
    index = "PATIENT_ID",
    columns = "Hugo_Symbol",
    aggfunc = "size",
    fill_value=0
)

# if the nums in cell are >0, it'll make it true (1). If 0, it'll make it false so stay 0.
mutation_pivot = (mutation_pivot > 0).astype(int)

#if the gene isnt listed add it to the pivot table with 0 values
for gene in target_genes:
    if gene not in mutation_pivot.columns:
        mutation_pivot[gene] = 0

#remove index
mutation_pivot = mutation_pivot.reset_index()

#merge datasets based off the patient ID
merged_df = pd.merge(clinical_df, mutation_pivot, on="PATIENT_ID")

#clean dataset
merged_df.dropna(subset=["OS_MONTHS"], inplace=True)
merged_df = merged_df[merged_df["OS_MONTHS"] > 0]

merged_df.to_csv("core_data_subset/gbm_merged_data.csv", index=False)