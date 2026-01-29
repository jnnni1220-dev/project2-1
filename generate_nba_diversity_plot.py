
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
os.makedirs('final_reports/nba/plots', exist_ok=True)

# Data from report (Section 3.1)
data = {
    'Persona': [
        'VIP Champions', 'Loyal Shoppers', 'At-Risk', 
        'New/Light Users', 'Occasional Buyers', 'Regular Shoppers', 'Bargain Hunters'
    ],
    'Entropy_Score': [35.4, 34.7, 34.4, 34.1, 34.0, 33.5, 32.4],
    'Color': [
        '#3498db', '#95a5a6', '#95a5a6', 
        '#95a5a6', '#95a5a6', '#95a5a6', '#e74c3c' # Blue for VIP (High), Red for Bargain (Low)
    ]
}

df = pd.DataFrame(data)

# Plot
plt.figure(figsize=(10, 6))
ax = sns.barplot(x='Entropy_Score', y='Persona', data=df, palette=df['Color'].tolist())

# Add value labels
for i, v in enumerate(df['Entropy_Score']):
    ax.text(v + 0.1, i, f"{v}%", va='center', fontweight='bold')

plt.xlim(30, 36)  # Zoom in to show the subtle 3% gap clearly
plt.title('Persona Discovery Diversity (Shannon Entropy)', fontsize=14, fontweight='bold')
plt.xlabel('Diversity Score (0-100 normalized)')
plt.ylabel('')
plt.tight_layout()

# Save
plt.savefig('final_reports/nba/plots/nba_diversity_score_comparison.png')
print("Saved plot to final_reports/nba/plots/nba_diversity_score_comparison.png")
