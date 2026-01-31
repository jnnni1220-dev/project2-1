
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
os.makedirs('final_reports/ts/plots/deep_dive', exist_ok=True)

print("--- Generating Strategic Budget Allocation Matrix ---")

# 1. Load Data
segs = pd.read_csv('dunnhumby_persona_segments.csv')
stability = pd.read_csv('final_reports/ts_real_metrics.csv')

# 2. Calculate Avg Value per Persona
# We'll use 'monetary' (Total Spend) as the Value metric
value_metrics = segs.groupby('persona').agg({
    'monetary': 'mean',
    'CustomerID': 'count'
}).reset_index()
value_metrics.rename(columns={'monetary': 'Avg_Value', 'CustomerID': 'Customer_Count'}, inplace=True)

# Merge with stability
plot_df = stability.merge(value_metrics, on='persona', how='inner')

# Normalize metrics for easier quadrant definition (0-100 scale)
# Let's keep original for realism but define midpoints
stab_mid = 50
val_mid = plot_df['Avg_Value'].median()

# 3. Plotting with Collision Avoidance
plt.figure(figsize=(16, 10))

# Bubble transparency increased to see through overlaps
ax = sns.scatterplot(data=plot_df, x='stability_index', y='Avg_Value', 
                size='Customer_Count', hue='persona', 
                sizes=(300, 3000), alpha=0.5, palette='tab10')

# Quadrant Lines
plt.axvline(stab_mid, color='black', linestyle='--', alpha=0.2)
plt.axhline(val_mid, color='black', linestyle='--', alpha=0.2)

# Strategic Zone Labels (Moved to corners to avoid overlap with data points)
plt.text(62, 5000, "Zone A: Maintenance\n(High Value / High Stability)", 
         fontsize=13, fontweight='bold', color='green', ha='center', alpha=0.5)

plt.text(38, 5000, "Zone B: Defense\n(High Value / Low Stability)", 
         fontsize=13, fontweight='bold', color='red', ha='center', alpha=0.5)

plt.text(62, 100, "Zone C: Upsell\n(Low Value / High Stability)", 
         fontsize=13, fontweight='bold', color='blue', ha='center', alpha=0.5)

plt.text(38, 100, "Zone D: Observation\n(Low Value / Low Stability)", 
         fontsize=13, fontweight='bold', color='gray', ha='center', alpha=0.5)

# 4-Tier Vertical Staggering for Labels (Proximity-Aware)
plot_df_sorted = plot_df.sort_values('stability_index')
y_offsets = [-200, -500, 450, 800] # Distinct vertical tracks for labels

for i, row in plot_df_sorted.reset_index(drop=True).iterrows():
    y_off = y_offsets[i % len(y_offsets)]
    
    plt.annotate(
        f"{row['persona']}",
        xy=(row['stability_index'], row['Avg_Value']),
        xytext=(row['stability_index'], row['Avg_Value'] + y_off),
        fontsize=10, weight='bold', ha='center',
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.0", color='gray', alpha=0.4)
    )

plt.title('Time Series 기반 마케팅 예산 최적화 지도 (Strategic Budget Map)', fontsize=22, fontweight='bold', pad=30)
plt.xlabel('방문 안정성 지수 (Predictability / Stability Index)', fontsize=15)
plt.ylabel('인당 평균 구매액 (Average Monetary Value)', fontsize=15)
plt.grid(True, linestyle=':', alpha=0.5)

# Zoom out slightly for clearer margins
plt.xlim(plot_df['stability_index'].min() - 5, plot_df['stability_index'].max() + 5)
plt.ylim(-500, plot_df['Avg_Value'].max() + 1500)

# Legend adjustment
plt.legend(title='Persona Segment', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=11)
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q3_budget_map.png')
print("Saved tactical budget map to final_reports/ts/plots/deep_dive/q3_budget_map.png")
