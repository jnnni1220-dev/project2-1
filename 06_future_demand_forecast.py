
import pandas as pd
import pmdarima as pm
from prophet import Prophet
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import os
import joblib
import warnings
import logging

# Suppress warnings and logs
warnings.filterwarnings("ignore")
logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

print("--- Starting Future Demand Forecasting with Backtesting ---")

# --- 1. Load Data ---
print("\n[Step 1/5] Loading time series data...")

# --- Directories ---
input_path = '.\\processed_data\\weekly_sales_top50_timeseries.parquet'
output_dir = '.\\results\\forecasts'
plots_dir = '.\\plots\\future_forecasts'
validation_plots_dir = '.\\plots\\validation'
models_dir = '.\\models\\prophet_forecast_models'

for directory in [output_dir, plots_dir, validation_plots_dir, models_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

try:
    ts_df = pd.read_parquet(input_path)
    # Create 'ds' column for Prophet
    start_date = pd.to_datetime('2020-01-01')
    ts_df['ds'] = start_date + pd.to_timedelta(ts_df.index * 7, 'D')
    print("Data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# List to store all forecast results
all_forecasts = []
# List to store backtesting metrics
validation_metrics = []

# --- 2. Iterate Through Products ---
product_ids = ts_df.columns.drop('ds')
total_products = len(product_ids)
forecast_horizon = 12
backtest_horizon = 4 # Validation window size (weeks)

print(f"\nForecasting horizon: {forecast_horizon} weeks")
print(f"Backtesting horizon: {backtest_horizon} weeks")

for i, product_id in enumerate(product_ids):
    print(f"\n--- Processing Product {i+1}/{total_products}: {product_id} ---")
    
    # Prepare data
    prod_data = ts_df[['ds', product_id]].rename(columns={product_id: 'y'})
    y = prod_data['y']
    
    if y.sum() == 0:
        print(f"Skipping product {product_id} (no sales).")
        continue

    # --- 3. Backtesting (Validation) ---
    print("  > Running Backtest (Validation)...")
    try:
        # Split Data
        train_df = prod_data.iloc[:-backtest_horizon]
        test_df = prod_data.iloc[-backtest_horizon:]
        
        # Train Prophet on 'train_df'
        m_val = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        m_val.fit(train_df)
        
        # Predict on 'test_df' period
        future_val = m_val.make_future_dataframe(periods=backtest_horizon, freq='W')
        forecast_val = m_val.predict(future_val).iloc[-backtest_horizon:]
        
        # Calculate Metrics
        mae = mean_absolute_error(test_df['y'], forecast_val['yhat'])
        rmse = np.sqrt(mean_squared_error(test_df['y'], forecast_val['yhat']))
        
        metric_res = {
            'Product_ID': product_id,
            'MAE': mae,
            'RMSE': rmse,
            'Test_Mean': test_df['y'].mean()
        }
        validation_metrics.append(metric_res)
        
        # Validation Plot
        plt.figure(figsize=(10, 5))
        plt.plot(prod_data['ds'].iloc[-20:], prod_data['y'].iloc[-20:], label='Actual (Recent)', color='black', alpha=0.5)
        plt.plot(test_df['ds'], test_df['y'], label='Actual (Test)', color='green', marker='o')
        plt.plot(test_df['ds'], forecast_val['yhat'], label='Predicted (Backtest)', color='red', linestyle='--')
        plt.title(f"Backtest Validation (Product {product_id}): MAE={mae:.2f}")
        plt.legend()
        val_plot_path = os.path.join(validation_plots_dir, f'validation_{product_id}.png')
        plt.savefig(val_plot_path)
        plt.close()
        
    except Exception as e:
        print(f"    Backtest Failed: {e}")

    # --- 4. SARIMA Model (Full Data) ---
    print("  > Training SARIMA (Fast Mode)...")
    try:
        sarima_model = pm.auto_arima(y,
                                     start_p=1, start_q=1,
                                     test='adf',
                                     max_p=3, max_q=3,
                                     m=1,
                                     seasonal=False,
                                     start_P=0, D=0,
                                     trace=False,
                                     error_action='ignore',
                                     suppress_warnings=True,
                                     stepwise=True)
        
        sarima_forecast, sarima_conf_int = sarima_model.predict(n_periods=forecast_horizon, return_conf_int=True)
    except Exception as e:
        print(f"    SARIMA Failed: {e}")
        sarima_forecast = pd.Series([None] * forecast_horizon)
        sarima_conf_int = [[None, None]] * forecast_horizon

    # --- 5. Prophet Model (Full Data) ---
    print("  > Training Prophet (Full)...")
    try:
        prophet_model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        prophet_model.fit(prod_data)
        
        # Save Prophet Model
        model_path = os.path.join(models_dir, f'prophet_model_{product_id}.joblib')
        joblib.dump(prophet_model, model_path)
        
        future = prophet_model.make_future_dataframe(periods=forecast_horizon, freq='W')
        prophet_forecast_full = prophet_model.predict(future)
        
        prophet_future = prophet_forecast_full.iloc[-forecast_horizon:]
        prophet_values = prophet_future['yhat'].values
        prophet_lower = prophet_future['yhat_lower'].values
        prophet_upper = prophet_future['yhat_upper'].values
    except Exception as e:
        print(f"    Prophet Failed: {e}")
        prophet_values = [None] * forecast_horizon
        prophet_lower = [None] * forecast_horizon
        prophet_upper = [None] * forecast_horizon

    # --- 6. Compile Results & Plot ---
    last_date = prod_data['ds'].iloc[-1]
    future_dates = [last_date + pd.Timedelta(weeks=x+1) for x in range(forecast_horizon)]
    
    for j in range(forecast_horizon):
        s_val = None
        if isinstance(sarima_forecast, pd.Series):
             s_val = sarima_forecast.iloc[j]
        elif isinstance(sarima_forecast, (list, np.ndarray)):
             s_val = sarima_forecast[j]
             
        all_forecasts.append({
            'Product_ID': product_id,
            'Date': future_dates[j],
            'Forecast_Week': j + 1,
            'SARIMA_Forecast': s_val,
            'Prophet_Forecast': prophet_values[j] if prophet_values[j] is not None else None,
            'Prophet_Lower': prophet_lower[j] if prophet_lower[j] is not None else None,
            'Prophet_Upper': prophet_upper[j] if prophet_upper[j] is not None else None
        })

    # Plotting
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(prod_data['ds'], prod_data['y'], label='Historical Sales', color='black', alpha=0.9, linewidth=1.5)
    
    if isinstance(sarima_forecast, pd.Series) and sarima_forecast.iloc[0] is not None:
        ax.plot(future_dates, sarima_forecast, label='SARIMA Forecast', color='green', linestyle='--', linewidth=2)
    elif isinstance(sarima_forecast, (list, np.ndarray)) and sarima_forecast[0] is not None:
        ax.plot(future_dates, sarima_forecast, label='SARIMA Forecast', color='green', linestyle='--', linewidth=2)

    if prophet_values[0] is not None:
        ax.plot(future_dates, prophet_values, label='Prophet Forecast', color='blue', linestyle=':', linewidth=2)
        ax.fill_between(future_dates, prophet_lower, prophet_upper, color='blue', alpha=0.1)

    ax.set_title(f'Future Demand Forecast (Next 12 Weeks): Product {product_id}', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales Volume')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plot_path = os.path.join(plots_dir, f'forecast_{product_id}.png')
    plt.savefig(plot_path)
    plt.close(fig)

# --- 7. Save CSVs ---
print("\n[Step 5/5] Saving results...")
results_df = pd.DataFrame(all_forecasts)
output_csv = os.path.join(output_dir, 'future_demand_forecasts_top50.csv')
results_df.to_csv(output_csv, index=False)
print(f"Forecasts saved to: {output_csv}")

# Save Metrics
metrics_df = pd.DataFrame(validation_metrics)
metrics_csv = 'prophet_backtest_metrics.csv'
metrics_df.to_csv(metrics_csv, index=False)
print(f"Backtest metrics saved to: {metrics_csv}")

print("\n--- Future Demand Forecasting Complete ---")
