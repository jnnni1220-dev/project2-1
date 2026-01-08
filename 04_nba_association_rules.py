
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import os

print("--- Starting Next Basket Analysis (Association Rules) ---")

# --- 1. Load Processed Data ---
print("\n[Step 1/4] Loading processed data...")
input_path = '.\processed_data\master_transaction_table.parquet'
output_dir = '.\results'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    df = pd.read_parquet(input_path)
    print("Processed data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- 2. Prepare Data for Apriori ---
# We will use COMMODITY_DESC for higher-level, more interpretable rules.
# Drop rows where COMMODITY_DESC is null, as they can't be used.
df_cleaned = df.dropna(subset=['COMMODITY_DESC'])
df_cleaned = df_cleaned[df_cleaned['COMMODITY_DESC'] != 'NOT AVAILABLE']

print(f"\n[Step 2/4] Preparing data for Apriori using 'COMMODITY_DESC'. Using {len(df_cleaned)} transactions.")

# Create the basket format: group by basket and one-hot encode commodities.
# We sum the quantities, so if a commodity appears more than once, it gets a higher count.
# Then, we'll binarize it (any count > 0 becomes 1).
basket = df_cleaned.groupby(['BASKET_ID', 'COMMODITY_DESC'])['QUANTITY'].sum().unstack().fillna(0)

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1

basket_sets = basket.applymap(encode_units)

# Drop columns that are too sparse (e.g., appear in only 1 transaction) to reduce memory usage
# This is a simple heuristic. A more robust approach might use a support threshold here.
min_transactions = 5 
item_counts = basket_sets.sum()
items_to_keep = item_counts[item_counts >= min_transactions].index
basket_sets = basket_sets[items_to_keep]

print(f"Data prepared. Shape of one-hot encoded matrix: {basket_sets.shape}")

# --- 3. Run Apriori and Generate Rules ---
print("\n[Step 3/4] Running Apriori to find frequent itemsets...")
# Using a low support threshold to start, as we have many items.
# min_support = 0.01 means the itemset appears in at least 1% of all transactions.
frequent_itemsets = apriori(basket_sets, min_support=0.01, use_colnames=True)
print(f"Found {len(frequent_itemsets)} frequent itemsets.")

print("Generating association rules based on 'lift' metric...")
# We are interested in rules that have a high lift (> 1) and reasonable confidence.
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Sort the rules by lift and confidence
rules = rules.sort_values(['lift', 'confidence'], ascending=[False, False])

# --- 4. Analyze and Save Results ---
print("\n[Step 4/4] Analyzing and saving results...")
output_path = os.path.join(output_dir, 'association_rules.csv')
rules.to_csv(output_path, index=False)

print(f"Saved {len(rules)} association rules to {output_path}")

print("\nTop 20 Association Rules (sorted by Lift):")
# 'antecedents' and 'consequents' are frozensets, make them more readable
rules_to_show = rules.copy()
rules_to_show['antecedents'] = rules_to_show['antecedents'].apply(lambda a: ', '.join(list(a)))
rules_to_show['consequents'] = rules_to_show['consequents'].apply(lambda a: ', '.join(list(a)))

print(rules_to_show.head(20)[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

print("\n--- Next Basket Analysis Finished ---")

# A helper function to apply the encoding; necessary for applymap in older pandas.
# This definition is here to avoid any potential scope issues.
def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1
