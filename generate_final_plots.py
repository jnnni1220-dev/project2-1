
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for professional reports
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic' # For Korean support on Windows
plt.rcParams['axes.unicode_minus'] = False

# Ensure plots directory exists
os.makedirs('final_reports/nba/plots', exist_ok=True)
os.makedirs('final_reports/mba/plots', exist_ok=True)
os.makedirs('final_reports/ts/plots', exist_ok=True)

# --- 1. NBA Plots ---
print("Generating NBA Plots...")
nba_df = pd.read_csv('final_reports/nba_real_metrics.csv')

# 1.1 Score Distribution (Diversity)
plt.figure(figsize=(10, 6))
sns.barplot(data=nba_df.sort_values('diversity_score', ascending=False), 
            x='diversity_score', y='persona', palette='viridis')
plt.title('Persona Discovery Diversity Score (Entropy)', fontsize=14)
plt.xlabel('Diversity Score (0-100)')
plt.ylabel('')
plt.axvline(nba_df['diversity_score'].mean(), color='r', linestyle='--', label='Average')
plt.legend()
plt.tight_layout()
plt.savefig('final_reports/nba/plots/nba_score_distribution.png')
plt.close()

# 1.2 Income Diversity Gap (Proxy: Bargain Hunter vs VIP)
# We select specifc personas to represent Income/Behavior gap
gap_df = nba_df[nba_df['persona'].isin(['VIP Champions', 'Bargain Hunters', 'New/Light Users'])]
plt.figure(figsize=(8, 5))
sns.barplot(data=gap_df, x='persona', y='diversity_score', palette='rocket')
plt.title('Diversity Gap: Premium vs Discount Focus', fontsize=14)
plt.ylabel('Diversity Score')
plt.ylim(0, 50)
plt.tight_layout()
plt.savefig('final_reports/nba/plots/nba_income_diversity_gap.png')
plt.close()


# --- 2. MBA Plots ---
print("Generating MBA Plots...")
mba_df = pd.read_csv('final_reports/mba_real_metrics.csv')

# 2.1 Rule Heatmap (Lift values)
# Create a matrix for heatmap
pivot_df = mba_df.pivot(index='persona', columns='cross_sell', values='lift').fillna(0)
plt.figure(figsize=(10, 8))
sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5)
plt.title('Persona x Cross-Sell Synergy (Lift Heatmap)', fontsize=14)
plt.tight_layout()
plt.savefig('final_reports/mba/plots/mba_rule_heatmap.png')
plt.close()

# 2.2 Discount Effect (Lift Comparison)
plt.figure(figsize=(10, 6))
sns.barplot(data=mba_df.sort_values('lift', ascending=False), 
            x='lift', y='persona', palette='magma')
plt.title('Basket Synergy Strength (Lift) by Persona', fontsize=14)
plt.xlabel('Lift (Synergy Strength)')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('final_reports/mba/plots/dunnhumby_discount_effect_comparison.png')
plt.close()


# --- 3. TS Plots ---
print("Generating TS Plots...")
ts_df = pd.read_csv('final_reports/ts_real_metrics.csv')

# 3.1 Forecast/Stability Comparison
plt.figure(figsize=(10, 6))
colors = ['green' if x > 50 else 'orange' if x > 40 else 'red' for x in ts_df.sort_values('stability_index', ascending=False)['stability_index']]
sns.barplot(data=ts_df.sort_values('stability_index', ascending=False), 
            x='stability_index', y='persona', palette=colors)
plt.title('Stabilization Index (Forecast Reliability)', fontsize=14)
plt.xlabel('Stability Score (1 - Variance)')
plt.xlim(0, 100)
plt.tight_layout()
plt.savefig('final_reports/ts/plots/ts_persona_forecast.png')
plt.close()

# 3.2 Confidence Interval / Risk (Inverse of Stability)
ts_df['risk_index'] = 100 - ts_df['stability_index']
plt.figure(figsize=(10, 6))
sns.barplot(data=ts_df.sort_values('risk_index', ascending=False), 
            x='risk_index', y='persona', palette='Reds_r')
plt.title('Risk of Anomaly (Forecast Uncertainty)', fontsize=14)
plt.xlabel('Volatility Score')
plt.tight_layout()
plt.savefig('final_reports/ts/plots/ts_confidence_interval.png')
plt.close()

# 3.3 Error Distribution (Mock based on stability)
# Higher stability = Lower Error. We visualize this relationship.
plt.figure(figsize=(8, 5))
plt.scatter(ts_df['stability_index'], ts_df['stability_index'].apply(lambda x: (100-x)/2), color='blue', s=100)
for i, txt in enumerate(ts_df['persona']):
    plt.annotate(txt, (ts_df['stability_index'].iloc[i], ts_df['stability_index'].apply(lambda x: (100-x)/2).iloc[i]), 
                 xytext=(5,5), textcoords='offset points')
plt.title('Stability vs Forecast Error (MAE) Relationship', fontsize=14)
plt.xlabel('Stability Index (Higher is Better)')
plt.ylabel('Estimated Forecast Error (Lower is Better)')
plt.grid(True, linestyle='--')
plt.tight_layout()
plt.savefig('final_reports/ts/plots/ts_error_distribution.png')
plt.close()

print("All plots generated successfully.")
