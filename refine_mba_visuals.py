
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

# 2. Collect Rules for ALL Personas
metrics = []
# Analyze all personas in the dataset
target_personas = df['persona'].unique()

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
plt.figure(figsize=(16, 9))
sns.scatterplot(data=plot_df, x='confidence', y='lift', hue='persona', 
                style='persona', s=200, alpha=0.6, palette='tab10')

# Advanced Annotation: Sort by X-axis (Confidence) and stagger vertically across 4 tiers
top_points = []
for persona in plot_df['persona'].unique():
    p_data = plot_df[plot_df['persona'] == persona].sort_values('lift', ascending=False).iloc[0]
    top_points.append(p_data)

# Sort points by Confidence to manage horizontal density
top_points_sorted = sorted(top_points, key=lambda x: x['confidence'])

# 4-Tier Staggering Logic
y_offsets = [0.8, -1.2, 0.4, -0.8] # Alternating vertical positions

for i, pt in enumerate(top_points_sorted):
    y_off = y_offsets[i % len(y_offsets)]
    x_off = 0 # No horizontal shift needed if staggered vertically
    
    plt.annotate(
        f"[{pt['persona'][:12]}]\n{pt['antecedents']} \u2192 {pt['consequents']}",
        xy=(pt['confidence'], pt['lift']),
        xytext=(pt['confidence'], pt['lift'] + y_off),
        fontsize=9, weight='bold', ha='center',
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.85),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", color='gray', alpha=0.6)
    )

# Region Annotations (Conceptual) - Adjusted positions for better visibility
plt.text(0.75, 16, "Target: Filter Bubble\n(Locked-in Rules)", fontsize=13, color='#c0392b', weight='bold', alpha=0.7)
plt.text(0.1, 1, "Target: Omni-Explorer Area\n(Loose Synergy)", fontsize=13, color='#2980b9', weight='bold', alpha=0.7)

plt.title('Persona Shopping Behavior Map: Confidence vs Lift', fontsize=20, fontweight='bold', pad=25)
plt.xlabel('Confidence (Probability of Purchase)', fontsize=14)
plt.ylabel('Lift (Synergy Strength)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0., fontsize=11)
plt.tight_layout()
plt.savefig('final_reports/mba/plots/mba_rule_scatter.png')
print("Saved scatter plot to final_reports/mba/plots/mba_rule_scatter.png")
