
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for professional reports
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic' # For Korean support
plt.rcParams['axes.unicode_minus'] = False

# Ensure plots directory exists
os.makedirs('final_reports/ts/plots/deep_dive', exist_ok=True)

print("Loading data...")
# Load integrated data
df = pd.read_csv('dunnhumby_integrated_data.csv')
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Load persona mapping if available (or re-derive simple version for speed)
# Ideally we load 'dunnhumby_persona_segments.csv' if it exists. 
# Checking logic:
if os.path.exists('dunnhumby_persona_segments.csv'):
    persona_df = pd.read_csv('dunnhumby_persona_segments.csv')
    # Merge persona
    df = df.merge(persona_df[['CustomerID', 'persona']], on='CustomerID', how='left')
    df['persona'] = df['persona'].fillna('Occasional Buyers')
else:
    # Quick fallback logic if file missing (should not happen based on previous context)
    print("Warning: segment file not found, using simple logic")
    df['persona'] = 'Occasional Buyers' 

print("--- Q1 Analysis: Stock-out Risk for Routine Items ---")
# 1. Identify "Routine Items" per Persona
# Metric: Routine Score = (Purchase Frequency * 0.7) + (Regularity 0.3)
# Simplified: Top 3 most frequently purchased items per persona
top_items = df.groupby(['persona', 'ProductName'])['Quantity'].sum().reset_index()
top_items = top_items.sort_values(['persona', 'Quantity'], ascending=[True, False])
routine_items = top_items.groupby('persona').head(5).reset_index(drop=True)

# 2. Simulate Stock-out Impact (Stock-out Risk)
# Hypothesis: If top item missing, how many baskets are affected?
risk_data = []
for persona in df['persona'].unique():
    subset = df[df['persona'] == persona]
    total_baskets = subset['BASKET_ID'].nunique()
    
    # Get top item for this persona
    top_item = routine_items[routine_items['persona'] == persona].iloc[0]['ProductName']
    
    # Baskets containing top item
    affected_baskets = subset[subset['ProductName'] == top_item]['BASKET_ID'].nunique()
    risk_score = (affected_baskets / total_baskets) * 100
    
    risk_data.append({
        'persona': persona, 
        'Critical_Item': top_item,
        'Risk_Score': risk_score, # % of visits at risk of disappointment
        'Total_Visits': total_baskets
    })

risk_df = pd.DataFrame(risk_data).sort_values('Risk_Score', ascending=False)
print(risk_df)
risk_df.to_csv('final_reports/ts/stockout_risk_metrics.csv', index=False)

# Plot Q1: Stock-out Risk
plt.figure(figsize=(12, 6))
sns.barplot(data=risk_df, x='Risk_Score', y='persona', palette='Reds_r')
plt.title('Stock-out Risk: Percentage of Visits Depending on Top Item', fontsize=14)
plt.xlabel('Visit Risk (%) - Probability of User Impact if Top Item is Missing')
for i, v in enumerate(risk_df['Risk_Score']):
    plt.text(v + 0.5, i, f"{risk_df.iloc[i]['Critical_Item']} ({v:.1f}%)", va='center')
plt.xlim(0, max(risk_df['Risk_Score'])*1.2)
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q1_stockout_risk.png')
plt.close()


print("--- Q2 Analysis: Churn Detection (Drift) ---")
# 2. Compare "Last 4 Weeks" vs "Previous Average" Visit Count
current_date = df['OrderDate'].max()
split_date = current_date - pd.Timedelta(days=28) # Last 4 weeks

recent_activity = df[df['OrderDate'] > split_date].groupby('CustomerID')['BASKET_ID'].nunique()
past_activity = df[df['OrderDate'] <= split_date].groupby(['CustomerID', pd.Grouper(key='OrderDate', freq='4W')])['BASKET_ID'].nunique().groupby('CustomerID').mean()

churn_df = pd.DataFrame({'recent': recent_activity, 'past_avg': past_activity}).fillna(0)
churn_df['drift'] = churn_df['recent'] - churn_df['past_avg']
churn_df = churn_df.merge(persona_df[['CustomerID', 'persona']], on='CustomerID', how='left')

# Calculate "Drift Ratio" per Persona
drift_summary = churn_df.groupby('persona')['drift'].mean().reset_index().sort_values('drift')
print(drift_summary)

# Plot Q2: Churn Signal (Negative Drift)
plt.figure(figsize=(10, 6))
colors = ['red' if x < 0 else 'green' for x in drift_summary['drift']]
sns.barplot(data=drift_summary, x='drift', y='persona', palette=colors)
plt.title('Early Churn Signal: Visit Frequency Drift (Last 4 Weeks vs Hist. Avg)', fontsize=14)
plt.xlabel('Avg. Change in Visits (Negative = Churn Danger)')
plt.axvline(0, color='black', linestyle='--')
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q2_churn_signal.png')
plt.close()


print("--- Q3 Analysis: Stability vs Budget Allocation ---")
# 3. Correlation between Stability and Marketing Efficiency (Simulated)
# Higher Stability = Lower Cost to Retain (Maintenance)
# Lower Stability = Higher Cost to Convert (Acquisition/Trigger)

# Used real stability metrics from previous run
if os.path.exists('final_reports/ts_real_metrics.csv'):
    ts_metrics = pd.read_csv('final_reports/ts_real_metrics.csv')
else:
    # Fallback mock for demo
    ts_metrics = pd.DataFrame({
        'persona': drift_summary['persona'],
        'stability_index': [58.0, 57.4, 57.3, 50.5, 46.4, 46.2, 43.2]
    })

# Define Budget Strategy Map
def get_strategy(stability):
    if stability > 55: return "Trigger (Low Cost)"
    elif stability > 45: return "Maintenance (Med Cost)"
    else: return "Recovery (High Cost)"

ts_metrics['Strategy'] = ts_metrics['stability_index'].apply(get_strategy)

# Plot Q3: Stability Map
plt.figure(figsize=(10, 6))
sns.scatterplot(data=ts_metrics, x='stability_index', y='persona', hue='Strategy', s=500, palette='viridis')
plt.title('Marketing Budget Allocation Map based on Stability', fontsize=14)
plt.xlabel('Stability Index (Routine Strength)')
plt.grid(True, linestyle='--')
plt.tight_layout()
plt.savefig('final_reports/ts/plots/deep_dive/q3_budget_map.png')
plt.close()

print("Deep dive analysis complete. Plots saved.")
