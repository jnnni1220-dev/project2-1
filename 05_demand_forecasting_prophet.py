
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import os
import joblib
import logging

# Suppress verbose logging from Prophet
logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

print("--- Starting Demand Forecasting with Prophet (Top 50) ---")

# --- 1. Load and Prepare Data ---
print("\n[Step 1/5] Loading and preparing time series data...")
input_path = '.\\\\processed_data\\\\weekly_sales_top50_timeseries.parquet'
models_dir = '.\\\\models'
plots_dir = '.\\\\plots'

# Ensure output directories exist
for directory in [models_dir, plots_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

try:
    ts_df = pd.read_parquet(input_path)
    # Prophet requires the columns to be named 'ds' and 'y'
    # Create a dummy date range starting from 2020-01-01 with weekly frequency.
    start_date = pd.to_datetime('2020-01-01')
    ts_df['ds'] = start_date + pd.to_timedelta(ts_df.index * 7, 'D')
    print("Time series data loaded and 'ds' column created.")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Store results for final summary
results = {}

# --- 2. Iterate Through Products and Model ---
product_ids = ts_df.columns.drop('ds')
total_products = len(product_ids)

for i, product_id in enumerate(product_ids):
    print(f"\n--- Processing Product {i+1}/{total_products}: {product_id} ---")

    # --- Prepare data for the current product ---
    product_df = ts_df[['ds', product_id]].rename(columns={product_id: 'y'})
    
    # Skip products with no sales data
    if product_df['y'].sum() == 0:
        print(f"Skipping product {product_id} due to no sales data.")
        continue

    # --- Split data: 80% for training, 20% for testing ---
    train_size = int(len(product_df) * 0.8)
    train_df = product_df.iloc[:train_size]
    test_df = product_df.iloc[train_size:]
    print(f"[Step 2/5] Data split: {len(train_df)} training weeks, {len(test_df)} test weeks.")

    # --- 3. Initialize and Train Prophet Model ---
    print("[Step 3/5] Initializing and training Prophet model...")
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(train_df)

    # --- 4. Forecast for the Next 13 Weeks ---
    forecast_horizon = 13
    if len(test_df) < forecast_horizon:
        print(f"Skipping product {product_id}: Not enough test data ({len(test_df)} weeks) to evaluate a {forecast_horizon}-week forecast.")
        continue
        
    print(f"[Step 4/5] Forecasting for the next {forecast_horizon} weeks...")
    
    # Create a future dataframe for predictions
    future = model.make_future_dataframe(periods=forecast_horizon, freq='W')
    forecast = model.predict(future)

    # Isolate the 13-week forecast to compare with test data
    forecast_to_compare = forecast.iloc[-forecast_horizon:]
    actuals_to_compare = test_df.iloc[:forecast_horizon]

    # --- 5. Evaluate and Visualize ---
    print("[Step 5/5] Evaluating model and visualizing results...")
    mae = mean_absolute_error(actuals_to_compare['y'], forecast_to_compare['yhat'])
    results[product_id] = {'mae': mae}
    print(f"Mean Absolute Error (MAE) for {forecast_horizon} weeks: {mae:.2f}")

    # Plotting the results
    fig = model.plot(forecast)
    ax = fig.gca()
    # Add actuals to the plot
    ax.plot(actuals_to_compare['ds'], actuals_to_compare['y'], 'r.', label=f'Actual Test Data ({forecast_horizon} weeks)')
    ax.set_title(f'Prophet Forecast for Product {product_id}', fontsize=16)
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales Value ($)')
    ax.legend()
    
    # Save the plot
    plot_path = os.path.join(plots_dir, f'prophet_forecast_product_{product_id}.png')
    fig.savefig(plot_path)
    plt.close(fig) # Close the figure to free up memory
    print(f"Forecast plot saved to {plot_path}")

    # Save the model
    model_path = os.path.join(models_dir, f'prophet_model_product_{product_id}.joblib')
    joblib.dump(model, model_path)
    print(f"Trained Prophet model saved to {model_path}")


# --- Final Summary ---
print("\n\n--- Prophet Modeling Complete ---")
if results:
    print("Summary of Mean Absolute Errors (MAE) for 13-week forecast:")
    # Sort results by MAE for easier review
    sorted_results = sorted(results.items(), key=lambda item: item[1]['mae'])
    for product_id, metrics in sorted_results:
        print(f"  - Product {product_id}: {metrics['mae']:.2f}")

    # Save results to a file for later comparison
    results_df = pd.DataFrame(results).T
    results_df.to_csv('prophet_mae_results_top50.csv')
    print("\nResults saved to prophet_mae_results_top50.csv")
else:
    print("No products were successfully modeled.")

print("\n--- Demand Forecasting with Prophet Finished ---")
