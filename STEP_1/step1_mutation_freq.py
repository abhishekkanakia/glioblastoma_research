import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

target_genes = ["ATRX", "TERT", "BRAF", "EGFR", "TP53", "IDH1", "IDH2"]
df = pd.read_csv("gbm_merged_data.csv")

# Calculate frequency (percentage of 1s in each binary column)
frequencies = {}
for gene in target_genes:
    if gene in df.columns:
        # Since columns are 0 or 1, the mean gives the proportion
        frequencies[gene] = df[gene].mean() * 100 
    else:
        frequencies[gene] = 0.0

# Convert to a clean DataFrame for plotting
freq_df = pd.DataFrame(list(frequencies.items()), columns=["Gene", "Frequency"])
freq_df = freq_df.sort_values(by="Frequency", ascending=False)

# Plotting
plt.figure(figsize=(10, 6))
# Added hue mapping to satisfy newer Seaborn versions
sns.barplot(x="Gene", y="Frequency", data=freq_df, hue="Gene", palette="viridis", legend=False)

plt.title("Target Gene Mutation Frequencies in GBM Cohort", fontsize=14, fontweight='bold')
plt.xlabel("Gene Symbol", fontsize=12)
plt.ylabel("Mutation Frequency (%)", fontsize=12)
plt.ylim(0, 100)

# Add percentage labels on top of each bar
for index, row in enumerate(freq_df.values):
    plt.text(index, row[1] + 1, f"{row[1]:.1f}%", color='black', ha="center", va="bottom")

plt.tight_layout()
plt.savefig("mutation_frequencies.png", dpi=300)
plt.show()

print("\nMutation frequencies successfully plotted and saved!")