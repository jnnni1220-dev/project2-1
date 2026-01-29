
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
os.makedirs('final_reports/nba/plots', exist_ok=True)

# Data from analysis
data = {
    'Persona': [
        'VIP Champions', 'Loyal Shoppers', 'At-Risk', 
        'Occasional Buyers', 'Regular Shoppers', 'Bargain Hunters', 'New/Light Users'
    ],
    'Repurchase_Rate': [99.8, 99.7, 99.4, 99.1, 98.8, 94.8, 92.3],
    'Color': [
        '#2ecc71', '#2ecc71', '#2ecc71', 
        '#2ecc71', '#2ecc71', '#f1c40f', '#e74c3c' # Green for high, Yellow for mid, Red for low
    ]
}

df = pd.DataFrame(data)

# Plot
plt.figure(figsize=(10, 6))
ax = sns.barplot(x='Repurchase_Rate', y='Persona', data=df, palette=df['Color'].tolist())

# Add value labels
for i, v in enumerate(df['Repurchase_Rate']):
    ax.text(v + 0.5, i, f"{v}%", va='center', fontweight='bold')

plt.xlim(85, 103)  # Zoom in to show differences
plt.title('Persona Repurchase Precision (Recommend Reliability)', fontsize=14, fontweight='bold')
plt.xlabel('Repurchase Rate (%)')
plt.ylabel('')
plt.tight_layout()

# Save
plt.savefig('final_reports/nba/plots/nba_retention_rate_comparison.png')
print("Saved plot to final_reports/nba/plots/nba_retention_rate_comparison.png")
