
import pandas as pd
import pmdarima as pm
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import os
import joblib
import warnings

warnings.filterwarnings("ignore")

print("--- Starting Demand Forecasting with SARIMA (Top 50) ---")

# --- 1. Load Time Series Data ---
print("\n[Step 1/5] Loading time series data...")
input_path = '.\\processed_data\\weekly_sales_top50_timeseries.parquet'
models_dir = '.\\models'
plots_dir = '.\\plots'

# Ensure output directories exist
for directory in [models_dir, plots_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

try:
    ts_df = pd.read_parquet(input_path)
    print("Time series data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Store results for final summary
results = {}

# --- 2. Iterate Through Products and Model ---
product_ids = ts_df.columns
total_products = len(product_ids)

for i, product_id in enumerate(product_ids):
    print(f"\n--- Processing Product {i+1}/{total_products}: {product_id} ---")
    y = ts_df[product_id]

    # Skip products with no sales data
    if y.sum() == 0:
        print(f"Skipping product {product_id} due to no sales data.")
        continue

    # --- Split data: 80% for training, 20% for testing ---
    train_size = int(len(y) * 0.8)
    train, test = y[0:train_size], y[train_size:]
    print(f"[Step 2/5] Data split: {len(train)} training weeks, {len(test)} test weeks.")

    # --- 3. Find Best SARIMA Model ---
    print("[Step 3/5] Finding best SARIMA model using auto_arima...")
    try:
        sarima_model = pm.auto_arima(train,
                                     start_p=1, start_q=1,
                                     test='adf',
                                     max_p=3, max_q=3,
                                     m=52,             # Yearly seasonality
                                     d=None,
                                     seasonal=True,
                                     start_P=0,
                                     D=1,
                                     trace=False, # Set to False to reduce log spam
                                     error_action='ignore',
                                     suppress_warnings=True,
                                     stepwise=True)

        print(f"Best model for {product_id}: {sarima_model.order}x{sarima_model.seasonal_order}")

    except Exception as e:
        print(f"Could not find a suitable SARIMA model for product {product_id}. Error: {e}")
        results[product_id] = {'mae': -1, 'order': 'Failed'}
        continue

    # --- 4. Train Model and Forecast ---
    forecast_horizon = 13
    if len(test) < forecast_horizon:
        print(f"Skipping product {product_id}: Not enough test data ({len(test)} weeks) to evaluate a {forecast_horizon}-week forecast.")
        continue

    print(f"[Step 4/5] Training model and forecasting for {forecast_horizon} weeks...")
    # The model is already fitted by auto_arima. We can now make predictions.
    forecast, conf_int = sarima_model.predict(n_periods=forecast_horizon, return_conf_int=True)

    # Create a DataFrame for the forecast
    forecast_df = pd.DataFrame({'forecast': forecast}, index=test.index[:forecast_horizon])
    actuals_to_compare = test[:forecast_horizon]

    # --- 5. Evaluate and Visualize ---
    print("[Step 5/5] Evaluating model and visualizing results...")
    mae = mean_absolute_error(actuals_to_compare, forecast_df['forecast'])
    results[product_id] = {'mae': mae, 'order': f"{sarima_model.order}x{sarima_model.seasonal_order}"}
    print(f"Mean Absolute Error (MAE) for {forecast_horizon} weeks: {mae:.2f}")

    # Plotting the results
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.plot(train, label='Training Data')
    ax.plot(actuals_to_compare, label=f'Actual Test Data ({forecast_horizon} weeks)', color='orange')
    ax.plot(forecast_df, label='SARIMA Forecast', color='green', linestyle='--')
    ax.fill_between(forecast_df.index,
                    conf_int[:, 0],
                    conf_int[:, 1],
                    color='green', alpha=0.1, label='95% Confidence Interval')

    ax.set_title(f'SARIMA Forecast for Product {product_id}', fontsize=16)
    ax.set_xlabel('Week Number')
    ax.set_ylabel('Sales Value ($)')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()

    # Save the plot
    plot_path = os.path.join(plots_dir, f'sarima_forecast_product_{product_id}.png')
    plt.savefig(plot_path)
    plt.close(fig) # Close the figure to free up memory
    print(f"Forecast plot saved to {plot_path}")

    # Save the model
    model_path = os.path.join(models_dir, f'sarima_model_product_{product_id}.joblib')
    joblib.dump(sarima_model, model_path)
    print(f"Trained SARIMA model saved to {model_path}")


# --- Final Summary ---
print("\n\n--- SARIMA Modeling Complete ---")
if results:
    print("Summary of Mean Absolute Errors (MAE) for 13-week forecast:")
    # Sort results by MAE for easier review
    sorted_results = sorted(results.items(), key=lambda item: item[1]['mae'])
    for product_id, metrics in sorted_results:
        print(f"  - Product {product_id}: {metrics['mae']:.2f} (Order: {metrics['order']})")

    # Save results to a file for later comparison
    results_df = pd.DataFrame(results).T
    results_df.to_csv('sarima_mae_results_top50.csv')
    print("\nResults saved to sarima_mae_results_top50.csv")
else:
    print("No products were successfully modeled.")

print("\n--- Demand Forecasting with SARIMA Finished ---")
