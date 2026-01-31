
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

# 3. Plotting with Absolute Visibility and Clean Layout
plt.figure(figsize=(16, 12)) 

# Bubble transparency and outlines for overlap visibility
ax = sns.scatterplot(data=plot_df, x='stability_index', y='Avg_Value', 
                size='Customer_Count', hue='persona', 
                sizes=(600, 6000), alpha=0.4, palette='tab10',
                edgecolor='black', linewidth=1.5, zorder=2)

# Quadrant Lines
plt.axvline(stab_mid, color='black', linestyle='--', alpha=0.15, zorder=1)
plt.axhline(val_mid, color='black', linestyle='--', alpha=0.15, zorder=1)

# Strategic Zone Labels (Extreme corners)
plt.text(70, 8800, "Zone A: Maintenance\n(High Value / High Stability)", 
         fontsize=15, fontweight='bold', color='green', ha='center', alpha=0.4)

plt.text(32, 8800, "Zone B: Defense (CRISIS)\n(High Value / Low Stability)", 
         fontsize=15, fontweight='bold', color='red', ha='left', alpha=0.5)

plt.text(70, -1800, "Zone C: Upsell (STABLE)\n(Low Value / High Stability)", 
         fontsize=15, fontweight='bold', color='blue', ha='center', alpha=0.4)

plt.text(32, -1800, "Zone D: Observation\n(Low Value / Low Stability)", 
         fontsize=15, fontweight='bold', color='gray', ha='left', alpha=0.4)

# Manual Staggering - Refined for zero-collision
# VIP and Loyal are close, so they need distinct vertical tracks
# Bargain Hunters is shifted right to clear New/Light
manual_offsets = {
    'VIP Champions': (-2, 1500),      # Way up
    'Loyal Shoppers': (-6, 300),      # Left-mid
    'At-Risk': (-4, -1300),           # Bottom-left
    'Regular Shoppers': (3, 1000),    # Top-right
    'Bargain Hunters': (7, 600),      # Way right, slightly up
    'Occasional Buyers': (0, 1000),   # Top-center
    'New/Light Users': (0, -2000)     # Far bottom
}

for i, row in plot_df.iterrows():
    p = row['persona']
    x_off, y_off = manual_offsets.get(p, (0, 0))
    
    plt.annotate(
        f"[{p}]\nValue: ${row['Avg_Value']:.0f}",
        xy=(row['stability_index'], row['Avg_Value']),
        xytext=(row['stability_index'] + x_off, row['Avg_Value'] + y_off),
        fontsize=12, weight='bold', ha='center',
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec='black', alpha=0.9, lw=1.5),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=0.2", color='black', lw=2),
        zorder=20
    )

plt.title('Time Series 기반 마케팅 예산 최적화 지도 (Strategic Budget Map)', fontsize=28, fontweight='bold', pad=60)
plt.xlabel('방문 안정성 지수 (Predictability / Stability Index)', fontsize=16)
plt.ylabel('인당 평균 구매액 (Average Monetary Value)', fontsize=16)
plt.grid(True, linestyle=':', alpha=0.3)

# Expand margins
plt.xlim(28, 77)
plt.ylim(-3000, 10500)

plt.legend(title='Persona Segment', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=12)
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q3_budget_map.png')
print("Successfully regenerated cleaned budget map.")
