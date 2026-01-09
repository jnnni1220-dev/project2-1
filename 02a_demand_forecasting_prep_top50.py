
import pandas as pd
import os
import matplotlib.pyplot as plt

print("--- Starting Demand Forecasting Preparation (Top 50) ---")

# --- 1. Load Processed Data ---
print("\n[Step 1/4] Loading processed data...")
input_path = '.\\processed_data\\master_transaction_table.parquet'
output_dir = '.\\processed_data'
plots_dir = '.\\plots'

for directory in [output_dir, plots_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

try:
    df = pd.read_parquet(input_path)
    print("Processed data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- 2. Aggregate Weekly Sales per Product ---
print("\n[Step 2/4] Aggregating weekly sales per product...")
weekly_sales = df.groupby(['PRODUCT_ID', 'WEEK_NO'])['SALES_VALUE'].sum().reset_index()
print("Weekly sales aggregation complete.")

# --- 3. Identify Top N Products by Total Sales ---
N = 50
print(f"\n[Step 3/4] Identifying top {N} products by total sales...")
total_sales = weekly_sales.groupby('PRODUCT_ID')['SALES_VALUE'].sum()
top_n_products = total_sales.nlargest(N).index.tolist()

print(f"Top {N} products by sales identified.")

# Filter the weekly sales data to include only the top N products
weekly_sales_top_n = weekly_sales[weekly_sales['PRODUCT_ID'].isin(top_n_products)]

# --- 4. Create and Visualize Time Series ---
print(f"\n[Step 4/4] Creating and visualizing time series for top {N} products...")
# Pivot the table to have weeks as index and products as columns
ts_df = weekly_sales_top_n.pivot(index='WEEK_NO', columns='PRODUCT_ID', values='SALES_VALUE').fillna(0)

# Ensure all weeks from min to max are present
all_weeks = pd.RangeIndex(start=ts_df.index.min(), stop=ts_df.index.max() + 1, name='WEEK_NO')
ts_df = ts_df.reindex(all_weeks, fill_value=0)

# Reorder columns to be in descending order of total sales
ts_df = ts_df[top_n_products]

# Save the time series data
ts_output_path = os.path.join(output_dir, f'weekly_sales_top{N}_timeseries.parquet')
ts_df.to_parquet(ts_output_path)
print(f"Time series data saved to {ts_output_path}")

# Plot the time series
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(15, 8))

# Plot only the top 10 for visual clarity, otherwise the plot is unreadable
ts_df.iloc[:, :10].plot(ax=ax)

ax.set_title(f'Weekly Sales of Top 10 (out of {N}) Products', fontsize=16)
ax.set_xlabel('Week Number')
ax.set_ylabel('Sales Value ($)')
ax.legend(title='Product ID')
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()

# Save the plot
plot_path = os.path.join(plots_dir, f'weekly_sales_top{N}.png')
plt.savefig(plot_path)
print(f"Time series plot saved to {plot_path}")

print(f"\n--- Demand Forecasting Preparation for Top {N} Finished ---")
