
import pandas as pd
import os
import matplotlib.pyplot as plt

print("--- Starting Demand Forecasting Preparation ---")

# --- 1. Load Processed Data ---
print("\n[Step 1/4] Loading processed data...")
input_path = '.\processed_data\master_transaction_table.parquet'
output_dir = '.\processed_data'
plots_dir = '.\plots'

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
print("\n[Step 3/4] Identifying top 5 products by total sales...")
total_sales = weekly_sales.groupby('PRODUCT_ID')['SALES_VALUE'].sum()
top_5_products = total_sales.nlargest(5).index.tolist()

print(f"Top 5 products by sales: {top_5_products}")

# Filter the weekly sales data to include only the top 5 products
weekly_sales_top5 = weekly_sales[weekly_sales['PRODUCT_ID'].isin(top_5_products)]

# --- 4. Create and Visualize Time Series ---
print("\n[Step 4/4] Creating and visualizing time series for top 5 products...")
# Pivot the table to have weeks as index and products as columns
ts_df = weekly_sales_top5.pivot(index='WEEK_NO', columns='PRODUCT_ID', values='SALES_VALUE').fillna(0)

# Ensure all weeks from min to max are present
all_weeks = pd.RangeIndex(start=ts_df.index.min(), stop=ts_df.index.max() + 1, name='WEEK_NO')
ts_df = ts_df.reindex(all_weeks, fill_value=0)

# Save the time series data
ts_output_path = os.path.join(output_dir, 'weekly_sales_top5_timeseries.parquet')
ts_df.to_parquet(ts_output_path)
print(f"Time series data saved to {ts_output_path}")

# Plot the time series
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(15, 8))

ts_df.plot(ax=ax)

ax.set_title('Weekly Sales of Top 5 Products', fontsize=16)
ax.set_xlabel('Week Number')
ax.set_ylabel('Sales Value ($)')
ax.legend(title='Product ID')
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()

# Save the plot
plot_path = os.path.join(plots_dir, 'weekly_sales_top5.png')
plt.savefig(plot_path)
print(f"Time series plot saved to {plot_path}")

print("\n--- Demand Forecasting Preparation Finished ---")
