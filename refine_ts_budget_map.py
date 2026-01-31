
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

# 3. Plotting with Absolute Collision Avoidance
plt.figure(figsize=(16, 10))

# Bubble transparency increased to see through overlaps
ax = sns.scatterplot(data=plot_df, x='stability_index', y='Avg_Value', 
                size='Customer_Count', hue='persona', 
                sizes=(400, 4000), alpha=0.4, palette='tab10')

# Quadrant Lines
plt.axvline(stab_mid, color='black', linestyle='--', alpha=0.1)
plt.axhline(val_mid, color='black', linestyle='--', alpha=0.1)

# Strategic Zone Labels (Moved to extreme corners)
plt.text(65, 8000, "Zone A: Maintenance\n(High Value / High Stability)", 
         fontsize=14, fontweight='bold', color='green', ha='center', alpha=0.4)

plt.text(38, 8000, "Zone B: Defense\n(High Value / Low Stability)", 
         fontsize=14, fontweight='bold', color='red', ha='center', alpha=0.4)

plt.text(65, -100, "Zone C: Upsell\n(Low Value / High Stability)", 
         fontsize=14, fontweight='bold', color='blue', ha='center', alpha=0.4)

plt.text(38, -100, "Zone D: Observation\n(Low Value / Low Stability)", 
         fontsize=14, fontweight='bold', color='gray', ha='center', alpha=0.4)

# Manual Staggering based on real data clusters
# Cluster 1: At-Risk, Loyal, VIP (X=43~46)
# Cluster 2: New/Light, Occasional, Bargain (X=57~58)
manual_offsets = {
    'VIP Champions': (0, 1000),     # Top center
    'Loyal Shoppers': (-5, 0),      # Far left
    'At-Risk': (0, -1000),          # Bottom center
    'Regular Shoppers': (3, 600),   # Top right
    'Bargain Hunters': (5, 0),      # Far right
    'Occasional Buyers': (0, 500),  # Top
    'New/Light Users': (0, -600)    # Bottom
}

for i, row in plot_df.iterrows():
    p = row['persona']
    x_off, y_off = manual_offsets.get(p, (0, 0))
    
    plt.annotate(
        f"[{p}]\nValue: ${row['Avg_Value']:.0f}",
        xy=(row['stability_index'], row['Avg_Value']),
        xytext=(row['stability_index'] + x_off, row['Avg_Value'] + y_off),
        fontsize=11, weight='bold', ha='center',
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="gray", alpha=1.0, lw=1.5),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=0.1", color='black', lw=1),
        zorder=10
    )

plt.title('Time Series 기반 마케팅 예산 최적화 지도 (Strategic Budget Map)', fontsize=24, fontweight='bold', pad=40)
plt.xlabel('방문 안정성 지수 (Predictability / Stability Index)', fontsize=16)
plt.ylabel('인당 평균 구매액 (Average Monetary Value)', fontsize=16)
plt.grid(True, linestyle=':', alpha=0.4)

# Margin expansion for clear labels
plt.xlim(30, 75)
plt.ylim(-1000, 9500)

# Legend adjustment
plt.legend(title='Persona Segment', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=12)
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q3_budget_map.png')
print("Saved tactical budget map to final_reports/ts/plots/deep_dive/q3_budget_map.png")
