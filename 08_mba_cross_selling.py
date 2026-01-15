import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Context
input_path = '.\\processed_data\\master_transaction_table.parquet'
output_dir = '.\\results\\cross_selling'
plots_dir = '.\\plots\\mba'

# Create directories
os.makedirs(output_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

print("--- Starting Market Basket Analysis with Stability Check ---")

# --- 1. Load Data ---
print("\n[Step 1/6] Loading transaction data...")
try:
    df = pd.read_parquet(input_path)
    print(f"Data loaded: {len(df)} rows")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- 2. Preprocessing ---
print("\n[Step 2/6] Cleaning and preparing baskets...")
df_clean = df.dropna(subset=['COMMODITY_DESC'])
df_clean = df_clean[~df_clean['COMMODITY_DESC'].isin(['NOT AVAILABLE', 'NO COMMODITY DESCRIPTION'])]
df_clean = df_clean[~df_clean['COMMODITY_DESC'].str.contains('COUPON', na=False)]

print(f"Valid transactions rows: {len(df_clean)}")

# --- SAMPLING ---
target_sample_size = 500000
if len(df_clean) > target_sample_size:
    print(f"Sampling {target_sample_size} random transactions for analysis...")
    df_clean = df_clean.sample(n=target_sample_size, random_state=42)
else:
    print("Using full dataset.")

# --- Filter Top 50 Commodities ---
top_n = 50
top_commodities = df_clean['COMMODITY_DESC'].value_counts().head(top_n).index
print(f"Filtering for Top {top_n} Commodities by transaction volume...")
df_filtered = df_clean[df_clean['COMMODITY_DESC'].isin(top_commodities)].copy()

if isinstance(df_filtered['COMMODITY_DESC'].dtype, pd.CategoricalDtype):
    df_filtered['COMMODITY_DESC'] = df_filtered['COMMODITY_DESC'].cat.remove_unused_categories()

# --- 3. Stability Analysis (Split Data) ---
print("\n[Step 3/6] Running Stability Analysis (Group A vs Group B)...")

# Split transactions
unique_baskets = df_filtered['BASKET_ID'].unique()
np.random.seed(42)
group_a_baskets = np.random.choice(unique_baskets, size=int(len(unique_baskets)*0.5), replace=False)

df_group_a = df_filtered[df_filtered['BASKET_ID'].isin(group_a_baskets)]
df_group_b = df_filtered[~df_filtered['BASKET_ID'].isin(group_a_baskets)]

def get_rules(df_in, min_sup=0.001):
    basket = (df_in.groupby(['BASKET_ID', 'COMMODITY_DESC'])['QUANTITY']
              .sum().unstack().reset_index().fillna(0)
              .set_index('BASKET_ID'))
    basket_sets = (basket > 0).astype(bool)
    frequent_itemsets = apriori(basket_sets, min_support=min_sup, use_colnames=True)
    if len(frequent_itemsets) > 0:
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.01)
        # Create unique pair ID
        rules['pair'] = rules.apply(lambda x: tuple(sorted([list(x['antecedents'])[0], list(x['consequents'])[0]])), axis=1)
        return rules[['pair', 'lift']].drop_duplicates(subset=['pair'])
    return pd.DataFrame()

rules_a = get_rules(df_group_a)
rules_b = get_rules(df_group_b)

print(f"Rules in Group A: {len(rules_a)}")
print(f"Rules in Group B: {len(rules_b)}")

if not rules_a.empty and not rules_b.empty:
    common_rules = set(rules_a['pair']).intersection(set(rules_b['pair']))
    stability_score = len(common_rules) / max(len(rules_a), len(rules_b)) * 100
    print(f"Stability Score (Overlap %): {stability_score:.2f}%")
    
    # Save validation metric
    with open('mba_stability_metric.txt', 'w') as f:
        f.write(f"Stability Score: {stability_score:.2f}%\n")
        f.write(f"Common Rules Count: {len(common_rules)}\n")

# --- 4. Full Analysis (All Data) ---
print("\n[Step 4/6] Running Full MBA on All Data...")
basket = (df_filtered.groupby(['BASKET_ID', 'COMMODITY_DESC'])['QUANTITY']
          .sum().unstack().reset_index().fillna(0)
          .set_index('BASKET_ID'))
basket_sets = (basket > 0).astype(bool)

frequent_itemsets = apriori(basket_sets, min_support=0.001, use_colnames=True)
if len(frequent_itemsets) > 0:
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.01)
    
    # Preprocessing rules for output
    rules['antecedent_len'] = rules['antecedents'].apply(lambda x: len(x))
    rules['consequent_len'] = rules['consequents'].apply(lambda x: len(x))
    rules_simple = rules[(rules['antecedent_len'] == 1) & (rules['consequent_len'] == 1)].copy()
    
    rules_simple['antecedents'] = rules_simple['antecedents'].apply(lambda x: list(x)[0])
    rules_simple['consequents'] = rules_simple['consequents'].apply(lambda x: list(x)[0])
    rules_simple['pair'] = rules_simple.apply(lambda x: tuple(sorted([x['antecedents'], x['consequents']])), axis=1)
    rules_unique = rules_simple.drop_duplicates(subset=['pair', 'lift']).sort_values('lift', ascending=False)
    
    # Save Rules
    output_file = os.path.join(output_dir, 'cross_selling_rules.csv')
    rules_unique.to_csv(output_file, index=False)
    print(f"Unique Rules saved: {len(rules_unique)}")

    # --- 5. Visualization: Network & Scatter ---
    print("\n[Step 5/6] Visualizing Inputs...")
    if len(rules_unique) > 0:
        top_rules = rules_unique.head(50)
        G = nx.from_pandas_edgelist(top_rules, source='antecedents', target='consequents', edge_attr='lift')

        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G, k=0.5, seed=42)
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue', alpha=0.7)
        nx.draw_networkx_edges(G, pos, width=[d['lift'] for (u, v, d) in G.edges(data=True)], alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
        plt.title("Top 50 Product Association Network")
        plt.axis('off')
        plt.savefig(os.path.join(plots_dir, 'mba_network_graph.png'), dpi=300, bbox_inches='tight')
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=rules_unique, x='support', y='lift', alpha=0.6, size='confidence', sizes=(20, 200))
        plt.title("Support vs Lift")
        plt.axhline(y=1, color='r', linestyle='--')
        plt.savefig(os.path.join(plots_dir, 'mba_scatter_plot.png'), dpi=300)
        plt.close()

    # --- 6. Visualization: Heatmap ---
    print("\n[Step 6/6] Generating Category Heatmap...")
    # Create matrix of Lift values for top commodity pairs
    pivot_table = rules_unique.pivot(index='antecedents', columns='consequents', values='lift')
    # Fill NaN with 0
    pivot_table = pivot_table.fillna(0)
    
    # Select a subset if too large
    if pivot_table.shape[0] > 20:
        # Sort by sum of lift
        keep_idx = pivot_table.sum(axis=1).sort_values(ascending=False).head(20).index
        keep_col = pivot_table.sum(axis=0).sort_values(ascending=False).head(20).index
        pivot_table = pivot_table.loc[keep_idx, keep_col]

    plt.figure(figsize=(14, 12))
    sns.heatmap(pivot_table, cmap="YlGnBu", annot=False)
    plt.title("Category Lift Heatmap (Top 20 Interactions)")
    plt.savefig(os.path.join(plots_dir, 'mba_category_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("All visualizations generated.")

print("\n--- Cross-Selling Analysis Complete ---")
