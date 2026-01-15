
import pandas as pd
import numpy as np
import os

print("--- Starting Data Preprocessing and Integration ---")

# Use raw strings for file paths to avoid SyntaxWarning
base_path = r'.\\dunnhumby.db'

# Define file paths
files = {
    'transactions': os.path.join(base_path, 'transaction_data.csv'),
    'products': os.path.join(base_path, 'product.csv'),
    'demographics': os.path.join(base_path, 'hh_demographic.csv')
}

# --- 1. Load Data with Optimized Dtypes ---
print("\n[Step 1/4] Loading data with optimized dtypes...")
try:
    # Dtype optimization to reduce memory usage
    demographics_dtypes = {
        'AGE_DESC': 'category',
        'MARITAL_STATUS_CODE': 'category',
        'INCOME_DESC': 'category',
        'HOMEOWNER_DESC': 'category',
        'HH_COMP_DESC': 'category',
        'HOUSEHOLD_SIZE_DESC': 'category',
        'KID_CATEGORY_DESC': 'category',
        'household_key': 'int32'
    }
    products_dtypes = {
        'PRODUCT_ID': 'int32',
        'MANUFACTURER': 'int32',
        'DEPARTMENT': 'category',
        'BRAND': 'category',
        'COMMODITY_DESC': 'category',
        'SUB_COMMODITY_DESC': 'category'
    }
    # For transactions, we will optimize after loading, but key columns can be set
    transactions_dtypes = {
        'household_key': 'int32',
        'BASKET_ID': 'int64', # Keep as int64 due to its large values
        'DAY': 'int16',
        'PRODUCT_ID': 'int32',
        'QUANTITY': 'int32',
        'STORE_ID': 'int16',
        'WEEK_NO': 'int8'
    }

    df_demo = pd.read_csv(files['demographics'], dtype=demographics_dtypes)
    df_prod = pd.read_csv(files['products'], dtype=products_dtypes)
    df_trans = pd.read_csv(files['transactions'], dtype=transactions_dtypes)
    
    print("Data loaded successfully.")
    print(f"Demographics Memory Usage: {df_demo.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Products Memory Usage: {df_prod.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Transactions Memory Usage: {df_trans.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- 2. Clean Product Data ---
print("\n[Step 2/4] Cleaning product data...")
# Replace placeholder text with np.nan
df_prod['SUB_COMMODITY_DESC'] = df_prod['SUB_COMMODITY_DESC'].replace('NO SUBCOMMODITY DESCRIPTION', np.nan)
df_prod['CURR_SIZE_OF_PRODUCT'] = df_prod['CURR_SIZE_OF_PRODUCT'].str.strip()
df_prod['CURR_SIZE_OF_PRODUCT'] = df_prod['CURR_SIZE_OF_PRODUCT'].replace('', np.nan)

# Convert object columns with high cardinality to category after cleaning
df_prod['CURR_SIZE_OF_PRODUCT'] = df_prod['CURR_SIZE_OF_PRODUCT'].astype('category')

print("Product data cleaned.")
print("Missing values in SUB_COMMODITY_DESC:", df_prod['SUB_COMMODITY_DESC'].isnull().sum())
print("Missing values in CURR_SIZE_OF_PRODUCT:", df_prod['CURR_SIZE_OF_PRODUCT'].isnull().sum())


# --- 3. Merge DataFrames ---
print("\n[Step 3/4] Merging transactions with product and demographic data...")
# Merge transactions with products
merged_df = pd.merge(df_trans, df_prod, on='PRODUCT_ID', how='left')

# Merge with demographics
merged_df = pd.merge(merged_df, df_demo, on='household_key', how='left')

print("Merge complete.")
print(f"Merged DataFrame shape: {merged_df.shape}")
print(f"Merged DataFrame Memory Usage: {merged_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")


# --- 4. Save Processed Data ---
output_dir = '.\\processed_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_path = os.path.join(output_dir, 'master_transaction_table.parquet')
print(f"\n[Step 4/4] Saving processed data to {output_path}...")
try:
    merged_df.to_parquet(output_path, engine='pyarrow')
    print("Successfully saved the merged data as a Parquet file.")
except Exception as e:
    print(f"Error saving data: {e}")

print("\n--- Data Preprocessing and Integration Finished ---")
