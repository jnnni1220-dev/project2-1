
import pandas as pd
import os

# Define the base path for the data
base_path = '.\dunnhumby.db'

# Define file paths
files_to_load = {
    'transactions': os.path.join(base_path, 'transaction_data.csv'),
    'products': os.path.join(base_path, 'product.csv'),
    'demographics': os.path.join(base_path, 'hh_demographic.csv'),
    'campaign_desc': os.path.join(base_path, 'campaign_desc.csv'),
    'campaign_table': os.path.join(base_path, 'campaign_table.csv'),
    'causal_data': os.path.join(base_path, 'causal_data.csv'),
    'coupon': os.path.join(base_path, 'coupon.csv'),
    'coupon_redempt': os.path.join(base_path, 'coupon_redempt.csv')
}

# Load data into a dictionary of dataframes
# Handling potential memory issues by loading only a subset of columns or rows if needed
# For now, we attempt to load the full files as the initial step.
try:
    print("Loading datasets...")
    # Causal data and transaction data are large, be mindful of memory.
    # For this initial script, we will focus on the smaller, descriptive files first,
    # and then the main transaction file.
    
    dataframes = {}
    for name, path in files_to_load.items():
        print(f"--- Loading {name} ({path}) ---")
        try:
            # For very large files, consider using dtype mapping or chunking later on.
            df = pd.read_csv(path)
            dataframes[name] = df
            
            print(f"Successfully loaded {name}.")
            print("Shape:", df.shape)
            
            print("\nBasic Info:")
            df.info(memory_usage='deep')
            
            print("\nMissing Values:")
            print(df.isnull().sum())
            
            print("\nFirst 5 Rows:")
            print(df.head())
            
            print("-" * 50 + "\n")
            
        except FileNotFoundError:
            print(f"Error: {path} not found.")
        except Exception as e:
            print(f"An error occurred while loading {name}: {e}")

    print("All available datasets have been loaded and inspected.")

except MemoryError:
    print("MemoryError: The dataset is too large to load into memory at once. "
          "Consider using chunking (pd.read_csv with chunksize) or a distributed computing framework like Dask or Spark.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
