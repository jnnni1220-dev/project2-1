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

print("--- Starting Market Basket Analysis for Cross-Selling ---")

# --- 1. Load Data ---
print("\n[Step 1/5] Loading transaction data...")
try:
    df = pd.read_parquet(input_path)
    print(f"Data loaded: {len(df)} rows")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- 2. Preprocessing ---
print("\n[Step 2/5] Cleaning and preparing baskets...")
df_clean = df.dropna(subset=['COMMODITY_DESC'])
df_clean = df_clean[~df_clean['COMMODITY_DESC'].isin(['NOT AVAILABLE', 'NO COMMODITY DESCRIPTION'])]
df_clean = df_clean[~df_clean['COMMODITY_DESC'].str.contains('COUPON', na=False)]

print(f"Valid transactions rows: {len(df_clean)}")

# --- SAMPLING: Increase to 500k to catch more pairs ---
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
df_filtered = df_clean[df_clean['COMMODITY_DESC'].isin(top_commodities)].copy() # Enforce copy

# IMPORTANT: Remove unused categories to strictly limit columns to 50
if isinstance(df_filtered['COMMODITY_DESC'].dtype, pd.CategoricalDtype):
    df_filtered['COMMODITY_DESC'] = df_filtered['COMMODITY_DESC'].cat.remove_unused_categories()

print(f"Filtered rows: {len(df_filtered)}")

# Create Basket (One-hot encoded)
basket = (df_filtered.groupby(['BASKET_ID', 'COMMODITY_DESC'])['QUANTITY']
          .sum().unstack().reset_index().fillna(0)
          .set_index('BASKET_ID'))

# Convert to boolean
basket_sets = (basket > 0).astype(bool)

print(f"Basket Matrix Shape: {basket_sets.shape} (Transactions x Categories)")

# --- 3. Run Apriori ---
# Min support 0.001 (0.1%) - lowered to find pairs
print("\n[Step 3/5] Generating Frequent Itemsets (Min Support=0.001)...")
frequent_itemsets = apriori(basket_sets, min_support=0.001, use_colnames=True)
print(f"Found {len(frequent_itemsets)} frequent itemsets.")

# --- 4. Generate Association Rules ---
print("\n[Step 4/5] Deriving Rules (Lift > 1.0)...")
if len(frequent_itemsets) > 0:
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.01)

    rules['antecedent_len'] = rules['antecedents'].apply(lambda x: len(x))
    rules['consequent_len'] = rules['consequents'].apply(lambda x: len(x))

    rules_simple = rules[(rules['antecedent_len'] == 1) & (rules['consequent_len'] == 1)].copy()

    rules_simple['antecedents'] = rules_simple['antecedents'].apply(lambda x: list(x)[0])
    rules_simple['consequents'] = rules_simple['consequents'].apply(lambda x: list(x)[0])

    rules_simple['pair'] = rules_simple.apply(lambda x: tuple(sorted([x['antecedents'], x['consequents']])), axis=1)
    rules_unique = rules_simple.drop_duplicates(subset=['pair', 'lift']).sort_values('lift', ascending=False)

    print(f"Generated {len(rules_simple)} simple rules. Pruned to {len(rules_unique)} unique variation pairs.")

    output_file = os.path.join(output_dir, 'cross_selling_rules.csv')
    rules_unique.to_csv(output_file, index=False)
    print(f"Rules saved to {output_file}")

    # --- 5. Visualization ---
    print("\n[Step 5/5] Visualizing Results...")

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
        network_plot_path = os.path.join(plots_dir, 'mba_network_graph.png')
        plt.savefig(network_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Network graph saved to {network_plot_path}")

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=rules_unique, x='support', y='lift', alpha=0.6, size='confidence', sizes=(20, 200))
        plt.title("Support vs Lift")
        plt.axhline(y=1, color='r', linestyle='--')
        scatter_plot_path = os.path.join(plots_dir, 'mba_scatter_plot.png')
        plt.savefig(scatter_plot_path, dpi=300)
        plt.close()
        print(f"Scatter plot saved to {scatter_plot_path}")
    else:
        print("No rules found to visualize.")
else:
    print("No frequent itemsets found.")

print("\n--- Cross-Selling Analysis Complete ---")
