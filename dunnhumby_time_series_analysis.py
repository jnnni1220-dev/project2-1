
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.metrics import mean_squared_error

# 설정
integrated_data_path = 'dunnhumby_integrated_data.csv'
plots_dir = 'dunnhumby_plots'
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

print("--- Dunnhumby 시계열 매출 예측 분석 (ARIMA & Prophet) ---")

try:
    # 1. 데이터 로드 및 전처리
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # 일별 매출 집계
    daily_sales = df.groupby('OrderDate')['TotalAmount'].sum().reset_index()
    daily_sales = daily_sales.rename(columns={'OrderDate': 'ds', 'TotalAmount': 'y'})
    daily_sales = daily_sales.sort_values('ds')
    
    # 누락된 날짜 채우기 (0원으로 처리)
    all_dates = pd.date_range(start=daily_sales['ds'].min(), end=daily_sales['ds'].max(), freq='D')
    daily_sales = daily_sales.set_index('ds').reindex(all_dates, fill_value=0).reset_index()
    daily_sales = daily_sales.rename(columns={'index': 'ds'})

    print(f"데이터 기간: {daily_sales['ds'].min()} ~ {daily_sales['ds'].max()}")
    print(f"총 데이터 포인트: {len(daily_sales)}일")

    # 2. ARIMA 모델링 (주간 데이터로 리샘플링하여 노이즈 감소)
    weekly_sales = daily_sales.set_index('ds').resample('W').sum()
    
    print("\n--- ARIMA 모델 학습 중... ---")
    # ARIMA(p,d,q) 파라미터는 간단히 설정 (실제로는 최적화 필요)
    arima_model = ARIMA(weekly_sales['y'], order=(5, 1, 0))
    arima_result = arima_model.fit()
    
    # 향후 12주 예측
    arima_forecast = arima_result.get_forecast(steps=12)
    arima_forecast_df = arima_forecast.summary_frame()

    # ARIMA 시각화
    plt.figure(figsize=(15, 7))
    plt.plot(weekly_sales.index, weekly_sales['y'], label='Actual Sales')
    plt.plot(arima_forecast_df.index, arima_forecast_df['mean'], color='red', label='ARIMA Forecast')
    plt.fill_between(arima_forecast_df.index, arima_forecast_df['mean_ci_lower'], arima_forecast_df['mean_ci_upper'], color='pink', alpha=0.3)
    plt.title('Dunnhumby Weekly Sales Forecast (ARIMA)', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Total Sales ($)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_arima_forecast.png'))
    plt.close()
    print(f"ARIMA 예측 차트 저장 완료: {plots_dir}/dunnhumby_arima_forecast.png")

    # 3. Prophet 모델링
    print("\n--- Prophet 모델 학습 중... ---")
    m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    m.fit(daily_sales)
    
    # 향후 90일 예측
    future = m.make_future_dataframe(periods=90)
    forecast = m.predict(future)

    # Prophet 시각화
    plt.figure(figsize=(15, 7))
    m.plot(forecast)
    plt.title('Dunnhumby Daily Sales Forecast (Prophet)', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Total Sales ($)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_prophet_forecast.png'))
    plt.close()
    
    # Prophet 컴포넌트 시각화 (트렌드, 계절성)
    fig2 = m.plot_components(forecast)
    fig2.savefig(os.path.join(plots_dir, 'dunnhumby_prophet_components.png'))
    plt.close()
    print(f"Prophet 예측 및 컴포넌트 차트 저장 완료: {plots_dir}/dunnhumby_prophet_forecast.png")

    print("\n시계열 분석 완료.")

except Exception as e:
    print(f"분석 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
