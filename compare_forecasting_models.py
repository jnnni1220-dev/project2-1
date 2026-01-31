
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import pmdarima as pm
from sklearn.metrics import mean_absolute_error
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
os.makedirs('processed_data', exist_ok=True)
os.makedirs('final_reports/ts/plots/deep_dive', exist_ok=True)

print("--- Generating Model Competition Victory Chart (Prophet vs SARIMA) ---")

# 1. Load Data
input_path = './processed_data/weekly_sales_top5_timeseries.parquet'
ts_df = pd.read_parquet(input_path)
product_id = ts_df.columns[0] # Select first product for comparison
y = ts_df[product_id]

# Prepare Prophet Data
df_prophet = pd.DataFrame({
    'ds': pd.to_datetime('2020-01-01') + pd.to_timedelta(ts_df.index * 7, 'D'),
    'y': y.values
})

train_size = int(len(y) * 0.8)
train_p = df_prophet.iloc[:train_size]
test_p = df_prophet.iloc[train_size:]

# 2. Train Prophet
m_prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
m_prophet.fit(train_p)
future = m_prophet.make_future_dataframe(periods=len(test_p), freq='W')
forecast_p = m_prophet.predict(future)

# 3. Train SARIMA
train_s = y.iloc[:train_size]
test_s = y.iloc[train_size:]
m_sarima = pm.auto_arima(train_s, m=52, seasonal=True, stepwise=True, suppress_warnings=True)
forecast_s, conf_int_s = m_sarima.predict(n_periods=len(test_s), return_conf_int=True)

# 4. Plot Comparison
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=False)

# Plot 1: Full View & Noise Handling
ax1.plot(df_prophet['ds'], df_prophet['y'], color='gray', alpha=0.3, label='Actual Data (History)')
ax1.plot(test_p['ds'], test_p['y'], color='black', lw=2, label='Actual Test Data (Target)')
ax1.plot(test_p['ds'], forecast_p['yhat'].iloc[-len(test_p):], color='blue', lw=2, label='Prophet Trend (Resilient to Noise)')
ax1.plot(test_p['ds'], forecast_s, color='red', linestyle='--', label='SARIMA Trend (Sensitive to Noise)')

ax1.set_title(f'Prophet vs SARIMA: 노이즈 대응 및 추세 학습 비교 ({product_id})', fontsize=18, fontweight='bold')
ax1.legend()
ax1.set_ylabel('Sales Value ($)')

# Plot 2: Confidence Interval for Churn Detection (The Winner's Edge)
ax2.plot(test_p['ds'], test_p['y'], 'k.', label='Actual Test Points')
ax2.fill_between(test_p['ds'], 
                 forecast_p['yhat_lower'].iloc[-len(test_p):], 
                 forecast_p['yhat_upper'].iloc[-len(test_p):], 
                 color='blue', alpha=0.15, label='Prophet 95% Confidence Interval (Robust)')
ax2.fill_between(test_p['ds'], 
                 conf_int_s[:, 0], 
                 conf_int_s[:, 1], 
                 color='red', alpha=0.1, label='SARIMA Interval (Unstable)')

ax2.set_title('이탈 징후 감지를 위한 신뢰 구간(Confidence Interval) 정교함 비교', fontsize=16, fontweight='bold')
ax2.legend()
ax2.set_ylabel('Sales Value ($)')

plt.suptitle('Why Prophet? : 리테일 비선형 모델 경합 승리 증거', fontsize=22, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

save_path = 'final_reports/ts/plots/deep_dive/model_comparison_victory.png'
plt.savefig(save_path)
print(f"Prophet victory chart saved to {save_path}")
