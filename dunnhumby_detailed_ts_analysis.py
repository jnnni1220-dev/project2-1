
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
import logging
import joblib
from prophet import Prophet
import pmdarima as pm
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 경고 무시
warnings.filterwarnings("ignore")
logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

# 한글 깨짐 해결을 위한 폰트 설정 (Windows 기준 Malgun Gothic)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rc('font', family='Malgun Gothic') # 명시적 추가 설정

# 설정
integrated_data_path = 'dunnhumby_integrated_data.csv'
base_output_dir = 'final_reports/ts'
plots_dir = os.path.join(base_output_dir, 'plots/forecasts')
validation_plots_dir = os.path.join(base_output_dir, 'plots/validation')
models_dir = os.path.join(base_output_dir, 'models')

for directory in [base_output_dir, plots_dir, validation_plots_dir, models_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

print("--- Dunnhumby 상품별 수요 예측 고도화 시작 (SARIMA & Prophet) ---")

try:
    # 1. 데이터 로드
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # 상품 정보 매핑 (상세 명칭 포함)
    product_meta = df[['ProductID', 'ProductName', 'Category']].drop_duplicates()
    
    # 총 매출액 기준 상위 10개 상품 + 보고서 삽입용 특정 상품 추출
    top_n_stats = df.groupby('ProductID')['TotalAmount'].sum().sort_values(ascending=False).head(10)
    top_n_products = top_n_stats.index.tolist()
    
    # 보고서 삽입용 특정 상품 ID (가솔린, 유제품, 조리식품, 스낵류)
    special_products = [6534178, 1106523, 1029743, 1082185]
    top_50_products = list(set(top_n_products + special_products))
    print(f"분석 대상 상품 수: {len(top_50_products)} (핵심 품목 집중)")

    # 주간 데이터로 변환 (일요일 기준)
    df['ds'] = df['OrderDate'].dt.to_period('W').dt.start_time
    
    all_forecasts = []
    validation_metrics = []
    forecast_horizon = 12
    backtest_horizon = 4
    min_weeks_required = 12

    # 2. 상품별 루프
    for i, product_id in enumerate(top_50_products):
        # 상품명 가져오기 및 정제 (제안서 1.1 반영)
        p_info = product_meta[product_meta['ProductID'] == product_id].iloc[0]
        p_name = p_info['ProductName']
        p_cat = p_info['Category']
        
        # 불명확 명칭 보완
        if 'COUPON' in p_name.upper() or 'MISC' in p_name.upper():
            p_name = f"{p_name} ({p_cat})"
            
        print(f"\n[{i+1}/50] 상품: {p_name} (ID: {product_id}) 분석 중...")
        
        # 상품별 주간 매출 집합
        prod_df = df[df['ProductID'] == product_id].groupby('ds')['TotalAmount'].sum().reset_index()
        prod_df = prod_df.rename(columns={'TotalAmount': 'y'})
        
        # 누락된 주차 채우기 (0원)
        all_weeks = pd.date_range(start=prod_df['ds'].min(), end=prod_df['ds'].max(), freq='W-MON')
        prod_df = prod_df.set_index('ds').reindex(all_weeks, fill_value=0).reset_index().rename(columns={'index': 'ds'})

        if len(prod_df) < min_weeks_required:
            print(f"  > 데이터 포인트 부재({len(prod_df)}주)로 예측에서 제외합니다. (최소 {min_weeks_required}주 필요)")
            continue

        if prod_df['y'].sum() == 0:
            print(f"  > 매출 데이터가 없어 스킵합니다.")
            continue

        # --- 3. Backtesting (마지막 4주 검증) ---
        best_model_name = "Prophet" # 기본값
        lowest_mae = float('inf')
        confidence_score = "N/A"
        
        try:
            train_df = prod_df.iloc[:-backtest_horizon]
            test_df = prod_df.iloc[-backtest_horizon:]
            
            # --- 3.1 Prophet Validation ---
            m_val = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            m_val.fit(train_df)
            future_val = m_val.make_future_dataframe(periods=backtest_horizon, freq='W')
            forecast_val = m_val.predict(future_val).iloc[-backtest_horizon:]
            
            p_mae = mean_absolute_error(test_df['y'], forecast_val['yhat'])
            
            # --- 3.2 SARIMA Validation ---
            # 데이터가 충분하면 m=52 (제안서 1.2 반영)
            m_val_val = 52 if len(train_df) >= 52 else 1
            sarima_val_model = pm.auto_arima(train_df['y'], seasonal=True, m=m_val_val, suppress_warnings=True, error_action='ignore')
            s_preds_val = sarima_val_model.predict(n_periods=backtest_horizon)
            
            s_mae = mean_absolute_error(test_df['y'], s_preds_val)

            # 최적 모델 선정 (MAE 기준)
            if s_mae < p_mae:
                best_model_name = "SARIMA"
                lowest_mae = s_mae
            else:
                best_model_name = "Prophet"
                lowest_mae = p_mae

            # 신뢰도 점수 계산 ((MAE/평균)) (제안서 1.3 반영)
            test_mean = test_df['y'].mean() if test_df['y'].mean() != 0 else 1
            error_ratio = lowest_mae / test_mean
            if error_ratio < 0.15: confidence_score = "높음 (High)"
            elif error_ratio < 0.30: confidence_score = "보통 (Mid)"
            else: confidence_score = "낮음 (Low)"

            validation_metrics.append({
                'Product_ID': product_id,
                'Product_Name': p_name,
                'Best_Model': best_model_name,
                'Prophet_MAE': p_mae,
                'SARIMA_MAE': s_mae,
                'Best_MAE': lowest_mae,
                'Confidence_Score': confidence_score,
                'Error_Ratio': error_ratio
            })
            
            # 검증 그래프
            plt.figure(figsize=(10, 5))
            plt.plot(prod_df['ds'].iloc[-12:], prod_df['y'].iloc[-12:], label='실측치(Actual)', color='black', marker='o')
            if best_model_name == "Prophet":
                plt.plot(test_df['ds'], forecast_val['yhat'], label='예측치(Prophet - Best)', color='red', linestyle='--')
            else:
                plt.plot(test_df['ds'], s_preds_val, label='예측치(SARIMA - Best)', color='green', linestyle='--')
            
            plt.title(f"백테스트 검증 (상품: {p_name}): 최적={best_model_name}, 신뢰도={confidence_score}")
            plt.xlabel("날짜")
            plt.ylabel("매출액")
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(validation_plots_dir, f'validation_{product_id}.png'))
            plt.close()
            
        except Exception as e:
            print(f"  > Backtest 실패: {e}")

        # --- 4. SARIMA 모델링 (Full Data) ---
        print("  > SARIMA 모델 학습 중...")
        sarima_preds = [None] * forecast_horizon
        sarima_lower = [None] * forecast_horizon
        sarima_upper = [None] * forecast_horizon
        try:
            m_param = 52 if len(prod_df) >= 52 else 1
            sarima_model = pm.auto_arima(prod_df['y'], seasonal=True, m=m_param, suppress_warnings=True, error_action='ignore')
            # 신뢰 구간 포함 (제안서 1.2 반영)
            preds, conf_int = sarima_model.predict(n_periods=forecast_horizon, return_conf_int=True)
            sarima_preds = preds.tolist()
            sarima_lower = conf_int[:, 0].tolist()
            sarima_upper = conf_int[:, 1].tolist()
        except Exception as e:
            print(f"  > SARIMA 실패: {e}")

        # --- 5. Prophet 모델링 (Full Data) ---
        print("  > Prophet 모델 학습 중...")
        prophet_preds = [None] * forecast_horizon
        prophet_lower = [None] * forecast_horizon
        prophet_upper = [None] * forecast_horizon
        try:
            m_full = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            m_full.fit(prod_df)
            
            # 모델 저장
            joblib.dump(m_full, os.path.join(models_dir, f'prophet_model_{product_id}.joblib'))
            
            future = m_full.make_future_dataframe(periods=forecast_horizon, freq='W')
            forecast = m_full.predict(future).iloc[-forecast_horizon:]
            prophet_preds = forecast['yhat'].tolist()
            prophet_lower = forecast['yhat_lower'].tolist()
            prophet_upper = forecast['yhat_upper'].tolist()
        except Exception as e:
            print(f"  > Prophet 실패: {e}")
        
        # --- 6. 결과 정리 ---
        last_date = prod_df['ds'].iloc[-1]
        for j in range(forecast_horizon):
            future_date = last_date + pd.Timedelta(weeks=j+1)
            all_forecasts.append({
                'Product_ID': product_id,
                'Product_Name': p_name,
                'Date': future_date,
                'Forecast_Week': j + 1,
                'SARIMA_Forecast': sarima_preds[j],
                'SARIMA_Lower': sarima_lower[j],
                'SARIMA_Upper': sarima_upper[j],
                'Prophet_Forecast': prophet_preds[j],
                'Prophet_Lower': prophet_lower[j],
                'Prophet_Upper': prophet_upper[j],
                'Best_Model': best_model_name,
                'Confidence_Score': confidence_score
            })

        # 예측 그래프 (제안서 시각화 요구사항 반영)
        plt.figure(figsize=(12, 6))
        plt.plot(prod_df['ds'], prod_df['y'], label='과거 매출(Historical)', color='black')
        future_dates = [last_date + pd.Timedelta(weeks=x+1) for x in range(forecast_horizon)]
        
        if sarima_preds[0] is not None:
            plt.plot(future_dates, sarima_preds, label='SARIMA 예측', color='green', linestyle='--')
            plt.fill_between(future_dates, sarima_lower, sarima_upper, color='green', alpha=0.1)
        if prophet_preds[0] is not None:
            plt.plot(future_dates, prophet_preds, label='Prophet 예측', color='blue', linestyle=':')
            plt.fill_between(future_dates, prophet_lower, prophet_upper, color='blue', alpha=0.1)
        
        plt.title(f'향후 수요 예측 (12주): {p_name} (ID: {product_id})', fontsize=14)
        plt.xlabel("날짜")
        plt.ylabel("매출액")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f'forecast_{product_id}.png'))
        plt.close()

    # 7. 파일 저장
    results_df = pd.DataFrame(all_forecasts)
    results_df.to_csv(os.path.join(base_output_dir, 'dunnhumby_future_demand_forecasts_top50.csv'), index=False)
    
    metrics_df = pd.DataFrame(validation_metrics)
    metrics_df.to_csv(os.path.join(base_output_dir, 'dunnhumby_prophet_backtest_metrics.csv'), index=False)
    
    print(f"\n--- 모든 분석 완료. 결과 저장 위치: {base_output_dir} ---")

except Exception as e:
    print(f"분석 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
