
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

# 3. Plotting
plt.figure(figsize=(14, 10))

# Custom scatter with point size reflecting customer count
ax = sns.scatterplot(data=plot_df, x='stability_index', y='Avg_Value', 
                size='Customer_Count', hue='persona', 
                sizes=(200, 2000), alpha=0.7, palette='tab10')

# Quadrant Lines
plt.axvline(stab_mid, color='black', linestyle='--', alpha=0.3)
plt.axhline(val_mid, color='black', linestyle='--', alpha=0.3)

# Quadrant Labels & Strategies
plt.text(58, val_mid * 1.5, "Zone A: Maintenance\n(High Value / High Stability)\nStrategy: Automation & Loyalty", 
         fontsize=12, fontweight='bold', color='green', ha='center', bbox=dict(facecolor='white', alpha=0.7))

plt.text(42, val_mid * 1.5, "Zone B: Defense\n(High Value / Low Stability)\nStrategy: Win-back & High Budget", 
         fontsize=12, fontweight='bold', color='red', ha='center', bbox=dict(facecolor='white', alpha=0.7))

plt.text(58, val_mid * 0.5, "Zone C: Upsell\n(Low Value / High Stability)\nStrategy: Category Expansion", 
         fontsize=12, fontweight='bold', color='blue', ha='center', bbox=dict(facecolor='white', alpha=0.7))

plt.text(42, val_mid * 0.5, "Zone D: Observation\n(Low Value / Low Stability)\nStrategy: Minimizing Cost", 
         fontsize=12, fontweight='bold', color='gray', ha='center', bbox=dict(facecolor='white', alpha=0.7))

# Annotate each point
for i in range(len(plot_df)):
    plt.text(plot_df.stability_index[i], plot_df.Avg_Value[i] + 100, 
             plot_df.persona[i], fontsize=11, fontweight='bold', ha='center')

plt.title('Time Series 기반 마케팅 예산 최적화 지도 (Strategic Budget Map)', fontsize=20, fontweight='bold', pad=25)
plt.xlabel('방문 안정성 지수 (Predictability / Stability Index)', fontsize=14)
plt.ylabel('인당 평균 구매액 (Average Monetary Value)', fontsize=14)
plt.grid(True, linestyle=':', alpha=0.6)

# Legend adjustment
plt.legend(title='Persona Segment', bbox_to_anchor=(1.01, 1), loc='upper left')

plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q3_budget_map.png')
print("Saved tactical budget map to final_reports/ts/plots/deep_dive/q3_budget_map.png")
