import os
import pandas as pd

# ==========================================
# 1. DEFINE PATH TO RAW MUTATIONS FILE
# ==========================================
# Update this filename/path if yours is .xlsx instead of .txt
raw_mutations_path = "gbm_tcga_pub2013/core_data_subset/data_mutations.txt"

if not os.path.exists(raw_mutations_path):
    # Fallback check if running directly inside a subfolder
    raw_mutations_path = "../gbm_tcga_pub2013/data_mutations.txt"

print(f"Reading raw mutations file from: {raw_mutations_path}...")

# Load the raw file (cBioPortal .txt files use tabs as separators)
if raw_mutations_path.endswith('.txt'):
    # comment='#' skips the metadata header lines at the very top of cBioPortal files
    df_raw = pd.read_csv(raw_mutations_path, sep="\t", comment="#", low_memory=False)
elif raw_mutations_path.endswith('.xlsx'):
    df_raw = pd.read_excel(raw_mutations_path)

# ==========================================
# 2. IDENTIFY COHORT TOTAL FROM PREVIOUS STEP
# ==========================================
# We know your cleaned analytical cohort has exactly 108 patients from Step 1
TOTAL_PATIENTS = 108

# Standardize column names to avoid case-sensitivity issues
df_raw.columns = [col.strip() for col in df_raw.columns]

# Core columns required for cBioPortal mapping
gene_col = 'Hugo_Symbol'
patient_col = 'Tumor_Sample_Barcode'

if gene_col not in df_raw.columns or patient_col not in df_raw.columns:
    print(f"Error: Could not find '{gene_col}' or '{patient_col}' columns in the raw file.")
    print(f"Available columns are: {list(df_raw.columns[:5])}...")
    exit()

# Clean patient IDs to match your core barcode format (e.g., TCGA-06-0125)
df_raw['Clean_Patient_ID'] = df_raw[patient_col].apply(lambda x: "-".join(str(x).split("-")[:3]))

# ==========================================
# 3. CALCULATE MUTATION FREQUENCIES
# ==========================================
print("Calculating unique patient mutation frequencies per gene...")

# Group by Gene and count how many UNIQUE patients have a mutation in that gene
gene_patient_counts = df_raw.groupby(gene_col)['Clean_Patient_ID'].nunique()

# Convert to a summary DataFrame
freq_df = pd.DataFrame({
    'Gene': gene_patient_counts.index,
    'Patient_Count': gene_patient_counts.values
})

# Calculate the true percentage based on your N=108 analytical cohort
freq_df['Frequency_Pct'] = (freq_df['Patient_Count'] / TOTAL_PATIENTS) * 100

# Sort by frequency in descending order
freq_df = freq_df.sort_values(by='Frequency_Pct', ascending=False)

# ==========================================
# 4. ENFORCE MANDATORY DRIVERS (Mirzaei's Request)
# ==========================================
# Ensure PTEN, CDKN2A, and your original significant markers are present
mandatory_drivers = ["PTEN", "CDKN2A", "EGFR", "TP53", "IDH1"]
for driver in mandatory_drivers:
    if driver not in freq_df['Gene'].values:
        # If the gene didn't show up at all in the mutation file, add it with 0
        new_row = pd.DataFrame([{'Gene': driver, 'Patient_Count': 0, 'Frequency_Pct': 0.0}])
        freq_df = pd.concat([new_row, freq_df], ignore_index=True)

# Pull the top 100 genes
top_100_genes = freq_df.head(100)

# Save the list to a text file for our pipeline loops to read dynamically later
top_100_genes.to_csv("top_100_genes_list.csv", index=False)

print("\n=== TOP 20 MOST FREQUENTLY MUTATED GENES IN RAW DATA ===")
print(top_100_genes.head(20).to_string(index=False))

print(f"\nSuccess! Saved the top 100 genes to 'top_100_genes_list.csv'.")