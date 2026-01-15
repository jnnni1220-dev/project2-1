
import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

print("--- Starting NBA Collaborative Filtering & Recommendation ---")

# 1. Load Data
input_path = r'processed_data/master_transaction_table.parquet'
if not os.path.exists(input_path):
    print(f"Error: {input_path} not found. Please run preprocessing first.")
    exit()

print("Loading merged transaction data...")
df = pd.read_parquet(input_path)

# Filter for relevant columns
# We use household_key and COMMODITY_DESC or SUB_COMMODITY_DESC for recommendations
# Using COMMODITY_DESC to keep the matrix manageable but still personalized
print("Preparing User-Item Matrix (Household vs Commodity)...")
basket_counts = df.groupby(['household_key', 'COMMODITY_DESC']).size().reset_index(name='count')

# 2. Pivot to Create User-Item Matrix
# Rows: Households, Columns: Commodities
user_item_matrix = basket_counts.pivot(index='household_key', columns='COMMODITY_DESC', values='count').fillna(0)

print(f"User-Item Matrix Shape: {user_item_matrix.shape}")

# 3. Calculate Item Similarity (or User Similarity)
# Given the size, User-User similarity might be large. Let's start with User-User on a subset or Item-Item.
# BUT the request asked for "고객 구매 이력 유사도 계산" (Customer purchase history similarity calculation)
# which implies User-User similarity.

# To handle memory, we use sparse matrix
user_item_sparse = csr_matrix(user_item_matrix.values)

print("Calculating User-User Cosine Similarity...")
user_similarity = cosine_similarity(user_item_sparse)
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

print("Similarity calculation complete.")

# 4. Collaborative Filtering (User-Based) Recommendation Logic
def get_nba_recommendations(target_household, user_similarity_df, user_item_matrix, top_n=5):
    # Get similar users
    similar_users = user_similarity_df[target_household].sort_values(ascending=False)[1:11] # Top 10 similar users (excluding self)
    
    # Get items bought by similar users
    similar_users_indices = similar_users.index
    items_bought_by_similar_users = user_item_matrix.loc[similar_users_indices]
    
    # Weighted score for items
    # Weights are the similarity scores
    weights = similar_users.values
    weighted_items = items_bought_by_similar_users.mul(weights, axis=0)
    
    # Sum weighted scores for each item
    item_scores = weighted_items.sum(axis=0)
    
    # Exclude items target user already bought
    target_user_bought = user_item_matrix.loc[target_household]
    item_scores = item_scores[target_user_bought == 0]
    
    # Get Top N recommendations
    recommendations = item_scores.sort_values(ascending=False).head(top_n)
    return recommendations.index.tolist()

# 5. Generate Recommendations for a sample of households (e.g., first 100 to keep it fast for now)
print("Generating recommendations for sample households...")
sample_households = user_item_matrix.index[:100]
nba_results = []

for household in sample_households:
    recs = get_nba_recommendations(household, user_similarity_df, user_item_matrix)
    nba_results.append({
        'household_key': household,
        'recommendations': ", ".join(recs)
    })

nba_df = pd.DataFrame(nba_results)

# 6. Save Results
output_dir = 'results'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_path = os.path.join(output_dir, 'nba_recommendations.csv')
nba_df.to_csv(output_path, index=False)
print(f"Recommendations saved to {output_path}")

print("--- NBA Collaborative Filtering Finished ---")
