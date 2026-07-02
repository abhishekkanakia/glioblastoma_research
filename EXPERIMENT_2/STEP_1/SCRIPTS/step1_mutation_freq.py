import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load data
hundred_df = pd.read_csv("../../top_100_genes_list.csv")
target_genes = hundred_df["Gene"].tolist()
df = pd.read_csv("../../gbm_merged_data.csv")

# Calculate frequency (percentage of 1s in each binary column)
frequencies = {}
for gene in target_genes:
    if gene in df.columns:
        frequencies[gene] = df[gene].mean() * 100 
    else:
        frequencies[gene] = 0.0

# Convert to a clean DataFrame for plotting
freq_df = pd.DataFrame(list(frequencies.items()), columns=["Gene", "Frequency"])
freq_df = freq_df.sort_values(by="Frequency", ascending=False)

# Ensure the results directory exists
os.makedirs("../RESULTS", exist_ok=True)

# --- 1. SAVE THE DATA TO CSV ---
csv_path = "../RESULTS/mutation_frequencies.csv"
freq_df.to_csv(csv_path, index=False)
print(f"CSV data successfully saved to: {csv_path}")

# --- 2. PLOT THE DATA (Horizontal Approach) ---
# Taller figure size (width=8, height=20) allows all 100 genes to spread out vertically
plt.figure(figsize=(8, 22))

# Swapped x and y to make it horizontal
sns.barplot(x="Frequency", y="Gene", data=freq_df, hue="Gene", palette="viridis", legend=False)

plt.title("Target Gene Mutation Frequencies in GBM Cohort", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Mutation Frequency (%)", fontsize=12)
plt.ylabel("Gene Symbol", fontsize=12)
plt.xlim(0, 105) # Extra padding at the right for text labels

# Adjust tick label sizes for readability
plt.xticks(fontsize=10)
plt.yticks(fontsize=8)

# Add percentage labels to the right of each horizontal bar
for index, row in enumerate(freq_df.values):
    gene_name = row[0]
    frequency_val = row[1]
    # Place text slightly to the right of the bar end (frequency_val + 0.5)
    plt.text(frequency_val + 0.5, index, f"{frequency_val:.1f}%", 
             color='black', ha="left", va="center", fontsize=7.5)

plt.tight_layout()

png_path = "../RESULTS/mutation_frequencies.png"
plt.savefig(png_path, dpi=300)
plt.close()

print(f"Plot successfully saved to: {png_path}")