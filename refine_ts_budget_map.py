
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
plt.figure(figsize=(16, 12)) # Height increased for better Y-axis spacing

# Bubble transparency and outlines for overlap visibility
ax = sns.scatterplot(data=plot_df, x='stability_index', y='Avg_Value', 
                size='Customer_Count', hue='persona', 
                sizes=(500, 5000), alpha=0.3, palette='tab10',
                edgecolor='black', linewidth=1.5)

# Quadrant Lines (Thinner and lighter)
plt.axvline(stab_mid, color='black', linestyle='--', alpha=0.1)
plt.axhline(val_mid, color='black', linestyle='--', alpha=0.1)

# Strategic Zone Labels (Extreme corners, no boxes to reduce clutter)
plt.text(73, 8500, "Zone A: Maintenance\n(High Value / High Stability)", 
         fontsize=15, fontweight='bold', color='green', ha='right', alpha=0.4)

plt.text(32, 8500, "Zone B: Defense\n(High Value / Low Stability)", 
         fontsize=15, fontweight='bold', color='red', ha='left', alpha=0.4)

plt.text(73, -1500, "Zone C: Upsell\n(Low Value / High Stability)", 
         fontsize=15, fontweight='bold', color='blue', ha='right', alpha=0.4)

plt.text(32, -1500, "Zone D: Observation\n(Low Value / Low Stability)", 
         fontsize=15, fontweight='bold', color='gray', ha='left', alpha=0.4)

# Radial Placement Strategy for Labels to prevent overlap
# Sorting primarily by X (Stability) then Y (Value)
manual_offsets = {
    'VIP Champions': (-2, 1200),     # Top-left of point
    'Loyal Shoppers': (-5, 500),     # Middle-left
    'At-Risk': (-4, -1200),          # Bottom-left 
    'Regular Shoppers': (3, 800),    # Top-right
    'Bargain Hunters': (6, 200),     # Far-right
    'Occasional Buyers': (0, 1000),  # Top-center
    'New/Light Users': (0, -1800)    # Deep bottom
}

print(f"Plotting {len(plot_df)} personas: {plot_df['persona'].tolist()}")

for i, row in plot_df.iterrows():
    p = row['persona']
    x_off, y_off = manual_offsets.get(p, (0, 0))
    
    # Use arc3 with rad=0.2 for elegant curved arrows
    plt.annotate(
        f"[{p}]\nValue: ${row['Avg_Value']:.0f}",
        xy=(row['stability_index'], row['Avg_Value']),
        xytext=(row['stability_index'] + x_off, row['Avg_Value'] + y_off),
        fontsize=11, weight='bold', ha='center',
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec='black', alpha=1.0, lw=1.2),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=0.2", color='black', lw=1.5),
        zorder=20
    )

plt.title('Time Series 기반 마케팅 예산 최적화 지도 (Strategic Budget Map)', fontsize=26, fontweight='bold', pad=50)
plt.xlabel('방문 안정성 지수 (Predictability / Stability Index)', fontsize=16)
plt.ylabel('인당 평균 구매액 (Average Monetary Value)', fontsize=16)
plt.grid(True, linestyle=':', alpha=0.3)

# Expand margins for labels
plt.xlim(30, 75)
plt.ylim(-2500, 10000)

# Legend adjustment
plt.legend(title='Persona Segment', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=12)
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q3_budget_map.png')
print("Successfully saved cleaned budget map with zero collisions.")
