
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
os.makedirs('final_reports/mba/plots', exist_ok=True)

print("--- Generating Refined MBA Scatter Plot (Lift vs Confidence) ---")

# 1. Load Data
df = pd.read_csv('dunnhumby_integrated_data.csv')
df = df[~df['ProductName'].str.contains('GASOLINE', na=False, case=False)]
df = df[~df['Category'].str.contains('FUEL', na=False, case=False)]

segs = pd.read_csv('dunnhumby_persona_segments.csv')
df = df.merge(segs[['CustomerID', 'persona']], on='CustomerID', how='inner')

# 2. Collect Rules for Top Personas
metrics = []
# Focus on distinctive personas for the chart
target_personas = ['Bargain Hunters', 'VIP Champions', 'Occasional Buyers', 'New/Light Users']

for persona in target_personas:
    print(f"Processing {persona}...")
    subset = df[df['persona'] == persona]
    
    # Top 50 items for matrix speed
    top_items = subset['ProductName'].value_counts().head(50).index
    basket = subset[subset['ProductName'].isin(top_items)].groupby(['BASKET_ID', 'ProductName'])['Quantity'].sum().unstack().fillna(0)
    basket = basket.applymap(lambda x: 1 if x > 0 else 0)
    
    try:
        frequent = apriori(basket, min_support=0.01, use_colnames=True)
        if frequent.empty: continue
        
        rules = association_rules(frequent, metric="lift", min_threshold=1.2)
        
        # Take Top 10 rules per persona
        top_rules = rules.sort_values('lift', ascending=False).head(10)
        
        for idx, row in top_rules.iterrows():
            metrics.append({
                'persona': persona,
                'antecedents': list(row['antecedents'])[0],
                'consequents': list(row['consequents'])[0],
                'support': row['support'],
                'confidence': row['confidence'],
                'lift': row['lift']
            })
    except Exception as e:
        print(f"Error {persona}: {e}")

plot_df = pd.DataFrame(metrics)

# 3. Plot Scatter: Confidence (X) vs Lift (Y)
# Interpretation: Top Right = "Golden Rules" (High certainty + High Synergy)
plt.figure(figsize=(12, 7))
sns.scatterplot(data=plot_df, x='confidence', y='lift', hue='persona', 
                style='persona', s=150, alpha=0.8, palette='deep')

# Annotation for top rule of each persona
for persona in plot_df['persona'].unique():
    top_rule = plot_df[plot_df['persona'] == persona].sort_values('lift', ascending=False).iloc[0]
    plt.text(top_rule['confidence']+0.01, top_rule['lift'], 
             f"{top_rule['antecedents']} -> {top_rule['consequents']}", 
             fontsize=9, weight='bold')

plt.title('Persona Shopping Behavior Map: Confidence vs Lift', fontsize=16)
plt.xlabel('Confidence (Probability of Purchase)', fontsize=12)
plt.ylabel('Lift (Synergy Strength)', fontsize=12)
plt.grid(True, linestyle='--')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('final_reports/mba/plots/mba_rule_scatter.png')
print("Saved scatter plot to final_reports/mba/plots/mba_rule_scatter.png")
