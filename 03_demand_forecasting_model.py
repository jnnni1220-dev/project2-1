
import pandas as pd
import pmdarima as pm
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import os
import joblib

print("--- Starting Demand Forecasting Model Training ---")

# --- 1. Load Time Series Data ---
print("\n[Step 1/5] Loading time series data...")
input_path = '.\\processed_data\\weekly_sales_top5_timeseries.parquet'
models_dir = '.\\models'
plots_dir = '.\\plots'

for directory in [models_dir, plots_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

try:
    ts_df = pd.read_parquet(input_path)
    print("Time series data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- 2. Select Product and Split Data ---
# Select the top-selling product (first column)
product_id = ts_df.columns[0]
y = ts_df[product_id]
print(f"\n[Step 2/5] Selected product for modeling: {product_id}")

# Split data: 80% for training, 20% for testing
train_size = int(len(y) * 0.8)
train, test = y[0:train_size], y[train_size:]
print(f"Training set size: {len(train)}")
print(f"Test set size: {len(test)}")

# --- 3. Find Best SARIMA Model ---
print("\n[Step 3/5] Finding best SARIMA model using auto_arima...")
# Looking at the initial plot, a yearly seasonality (52 weeks) seems plausible.
# Let's set m=52 for the seasonal component.
sarima_model = pm.auto_arima(train,
                             start_p=1, start_q=1,
                             test='adf',       # Use ADF test to find 'd'
                             max_p=3, max_q=3, # Max non-seasonal AR and MA order
                             m=52,             # Yearly seasonality
                             d=None,           # Let ADF test determine 'd'
                             seasonal=True,    # Enable seasonality
                             start_P=0,
                             D=1,              # Enforce seasonal differencing
                             trace=True,
                             error_action='ignore',
                             suppress_warnings=True,
                             stepwise=True)

print("\nBest SARIMA model summary:")
print(sarima_model.summary())

# --- 4. Train Model and Forecast ---
print("\n[Step 4/5] Training model and forecasting...")
# The model is already fitted by auto_arima. We can now make predictions.
n_periods = len(test)
forecast, conf_int = sarima_model.predict(n_periods=n_periods, return_conf_int=True)

# Create a DataFrame for the forecast
forecast_df = pd.DataFrame({'forecast': forecast}, index=test.index)

# --- 5. Evaluate and Visualize ---
print("\n[Step 5/5] Evaluating model and visualizing results...")
mae = mean_absolute_error(test, forecast)
print(f"Mean Absolute Error (MAE) on Test Set: {mae:.2f}")

# Plotting the results
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(15, 8))
ax.plot(train, label='Training Data')
ax.plot(test, label='Actual Test Data', color='orange')
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
print(f"Forecast plot saved to {plot_path}")

# Save the model
model_path = os.path.join(models_dir, f'sarima_model_product_{product_id}.joblib')
joblib.dump(sarima_model, model_path)
print(f"Trained SARIMA model saved to {model_path}")

print("\n--- Demand Forecasting Model Training Finished ---")
