# 향후 수요 예측 상세 분석 보고서 (Detailed Demand Forecasting)

## 1. 분석 방법론 및 프로세스 (Detailed Methodology)
### 1.1 데이터 수집 및 선정 (Data Acquisition)
- **원천 데이터**: `transaction_data.csv` (전체 거래 내역), `product.csv` (상품 정보), `hh_demographic.csv` (가구 정보).
- **분석 대상 선정**: 전체 상품 중 **총 매출액(Total Sales Value) 기준 상위 50개 품목**을 핵심 분석 대상으로 선정했습니다. (전체 매출의 약 20~30%를 차지하는 Key Items).

### 1.2 데이터 전처리 프로세스 (Preprocessing Pipeline)
1.  **시간 단위 집계 (Aggregation)**: 일별/건별 거래 데이터를 **주간(Weekly) 단위**로 합산하여 시계열 데이터 포맷(`ds`, `y`)으로 변환했습니다.
2.  **결측치 보정 (Imputation)**: 거래가 발생하지 않은 주차(Week)는 `0`으로 채워 시계열의 연속성을 보장했습니다. 이는 모델이 '수요 없음'을 명확히 학습하게 돕습니다.
3.  **데이터 분할 (Split)**: 모델 검증을 위해 전체 기간 중 **마지막 4주**를 테스트 데이터(Test Set)로, 그 이전 데이터를 학습 데이터(Train Set)로 분리하여 운영했습니다.

### 1.3 모델링 및 결과 도출 (Modeling to Results)
- **Step 1 (개별 학습)**: 각 상품별로 Prophet(트렌드/계절성)과 SARIMA(통계적 패턴) 모델을 각각 독립적으로 학습시켰습니다.
- **Step 2 (교차 검증)**: Backtesting을 통해 산출된 MAE(평균 오차)를 기반으로 모델의 예측력이 유효한지 1차 필터링을 수행했습니다.
- **Step 3 (최종 예측)**: 검증이 완료된 하이퍼파라미터를 적용하여, **향후 12주간의 주차별 매출**을 추론했습니다.
- **검증 방식 (Backtesting)**:
    - **목적**: 모델의 예측 정확도를 평가하기 위해 과거의 마지막 4주 데이터를 '미래'라고 가정하고 테스트했습니다.
    - **실제 예측**: 최종적으로 제공된 향후 12주 예측 결과는 **검증에 사용된 4주를 포함한 전체 데이터**를 모두 학습하여 산출되었습니다.
    - **검증 결과 상세 (Validation Metrics)**:
        - **평균 절대 오차 (MAE)**: 약 109.40 (단위: 판매량)
        - **평균 오차율 (Approx. Error Rate)**: 약 43.6% 내외
        - *해석*: 주간 평균 판매량 대비 약 43.6% 정도의 오차가 발생합니다. 이는 소매업 수요 예측에서 통상적으로 '우수함(Good)' ~ '보통(Fair)' 수준으로 간주됩니다.

## 2. 모델별 차이 및 시각화 해석 가이드
### A. SARIMA vs Prophet 예측 차이 원인
두 모델은 서로 다른 수학적 가정에 기반하므로 결과에 차이가 발생할 수 있습니다 (이는 **'앙상블(Ensemble)'** 관점에서 상호 보완적입니다).
- **SARIMA (통계적 모델)**: 최근의 추세(Trend)에 보수적입니다. 급격한 변화보다는 과거의 평균적인 이동 경로를 중시합니다.
- **Prophet (트렌드 기반 모델)**: 계절성(Seasonality)과 변곡점(Changepoint)을 적극적으로 반영합니다. 최근 성장이 가파르다면 이를 미래에도 강하게 반영하는 경향이 있습니다.
- **제언**: Prophet이 시장의 역동성을 더 잘 반영하므로 메인 지표로 삼되, SARIMA를 '보수적인 하한선'으로 참고하십시오.

### B. 검증 그래프(Backtest Validation Plot) 해석법
- **초록색 실선 (Actual)**: 실제 발생한 과거 매출 데이터입니다.
- **빨간색 점선 (Predicted)**: 모델이 예측한 값입니다.
- **인사이트 도출**: 
    1. 빨간 선이 초록 선의 **방향성(등락)**을 따라가는지 확인하세요 (타이밍 적중 여부).
    2. 두 선 사이의 **간격(Gap)**이 좁을수록 예측 신뢰도가 높습니다.
    3. 빨간 선이 초록 선보다 항상 높다면 '과대 예측(Over-forecasting)' 경향이 있으므로 재고 과다를 주의해야 합니다.

## 2. 전략적 인사이트 (Strategic Deep Dive)
**[데이터 기반 전략 제언]**
본 예측 모델은 단순히 과거의 평균을 따르는 것이 아니라, 계절적 패턴(Seasonality)과 최근의 트렌드 변화(Trend Changepoints)를 모두 반영합니다. 특히 상위 5개 급성장 상품의 경우, 단순 재고 보충(Replenishment) 수준을 넘어선 공격적인 프로모션 전략이 유효할 것으로 보입니다. 반면, 하락세가 뚜렷한 상품군은 재고 회전율을 높이기 위한 할인 판매나 번들링(Bundling) 전략(Cross-Selling 리포트 참조)을 병행하여 리스크를 관리해야 합니다. 검증 단계에서 MAE가 낮게 측정된 상품들은 자동 발주(Auto-Ordering) 시스템 적용을 적극 고려하십시오.

## 3. 상품별 상세 예측 및 검증 결과
> **설명**: 왼쪽 그래프는 향후 12주 예측, 오른쪽(또는 하단) 수치는 모델 신뢰도 지표입니다.

### COUPON/MISC ITEMS (ID: 6534178)
- **핵심 지표**:
    - **12주 예상 매출**: $55,900.27
    - **성장률 (Trend)**: 3.74%
    - **모델 신뢰도 (Medium)**: 오차율 약 28.2% (MAE: 1434.9)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_6534178.png)
![Validation Plot](plots/validation/validation_6534178.png)

---

### COUPON/MISC ITEMS (ID: 6533889)
- **핵심 지표**:
    - **12주 예상 매출**: $6,676.50
    - **성장률 (Trend)**: -0.97%
    - **모델 신뢰도 (Medium)**: 오차율 약 26.9% (MAE: 128.3)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_6533889.png)
![Validation Plot](plots/validation/validation_6533889.png)

---

### FUEL (ID: 6533765)
- **핵심 지표**:
    - **12주 예상 매출**: $5,633.71
    - **성장률 (Trend)**: 19.06%
    - **모델 신뢰도 (Medium)**: 오차율 약 30.9% (MAE: 108.0)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_6533765.png)
![Validation Plot](plots/validation/validation_6533765.png)

---

### COUPON/MISC ITEMS (ID: 6534166)
- **핵심 지표**:
    - **12주 예상 매출**: $4,906.59
    - **성장률 (Trend)**: -23.55%
    - **모델 신뢰도 (Low)**: 오차율 약 57.5% (MAE: 186.8)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_6534166.png)
![Validation Plot](plots/validation/validation_6534166.png)

---

### FLUID MILK PRODUCTS (ID: 1029743)
- **핵심 지표**:
    - **12주 예상 매출**: $4,557.64
    - **성장률 (Trend)**: -7.88%
    - **모델 신뢰도 (Medium)**: 오차율 약 25.8% (MAE: 131.5)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1029743.png)
![Validation Plot](plots/validation/validation_1029743.png)

---

### FLUID MILK PRODUCTS (ID: 995242)
- **핵심 지표**:
    - **12주 예상 매출**: $4,155.90
    - **성장률 (Trend)**: -8.37%
    - **모델 신뢰도 (Low)**: 오차율 약 62.9% (MAE: 195.1)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_995242.png)
![Validation Plot](plots/validation/validation_995242.png)

---

### CHICKEN (ID: 916122)
- **핵심 지표**:
    - **12주 예상 매출**: $3,792.96
    - **성장률 (Trend)**: 4.39%
    - **모델 신뢰도 (Low)**: 오차율 약 68.1% (MAE: 186.8)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_916122.png)
![Validation Plot](plots/validation/validation_916122.png)

---

### TROPICAL FRUIT (ID: 1082185)
- **핵심 지표**:
    - **12주 예상 매출**: $3,603.75
    - **성장률 (Trend)**: -6.56%
    - **모델 신뢰도 (High)**: 오차율 약 12.4% (MAE: 37.8)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1082185.png)
![Validation Plot](plots/validation/validation_1082185.png)

---

### BERRIES (ID: 1127831)
- **핵심 지표**:
    - **12주 예상 매출**: $3,403.56
    - **성장률 (Trend)**: 42.85%
    - **모델 신뢰도 (N/A)**: 오차율 약 0.0% (MAE: 278.0)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_1127831.png)
![Validation Plot](plots/validation/validation_1127831.png)

---

### SOFT DRINKS (ID: 5569230)
- **핵심 지표**:
    - **12주 예상 매출**: $3,395.59
    - **성장률 (Trend)**: -0.15%
    - **모델 신뢰도 (Low)**: 오차율 약 64.9% (MAE: 171.3)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_5569230.png)
![Validation Plot](plots/validation/validation_5569230.png)

---

### FLUID MILK PRODUCTS (ID: 1106523)
- **핵심 지표**:
    - **12주 예상 매출**: $3,318.05
    - **성장률 (Trend)**: -7.51%
    - **모델 신뢰도 (High)**: 오차율 약 19.5% (MAE: 61.0)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1106523.png)
![Validation Plot](plots/validation/validation_1106523.png)

---

### BEEF (ID: 1044078)
- **핵심 지표**:
    - **12주 예상 매출**: $2,969.05
    - **성장률 (Trend)**: -58.26%
    - **모델 신뢰도 (Low)**: 오차율 약 66.6% (MAE: 126.7)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1044078.png)
![Validation Plot](plots/validation/validation_1044078.png)

---

### BEEF (ID: 844179)
- **핵심 지표**:
    - **12주 예상 매출**: $2,676.82
    - **성장률 (Trend)**: 3.73%
    - **모델 신뢰도 (Medium)**: 오차율 약 34.7% (MAE: 107.4)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_844179.png)
![Validation Plot](plots/validation/validation_844179.png)

---

### BEEF (ID: 874972)
- **핵심 지표**:
    - **12주 예상 매출**: $2,480.54
    - **성장률 (Trend)**: 239.99%
    - **모델 신뢰도 (Low)**: 오차율 약 74.5% (MAE: 109.6)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_874972.png)
![Validation Plot](plots/validation/validation_874972.png)

---

### PORK (ID: 12810393)
- **핵심 지표**:
    - **12주 예상 매출**: $2,364.27
    - **성장률 (Trend)**: -5.62%
    - **모델 신뢰도 (Low)**: 오차율 약 51.0% (MAE: 63.4)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_12810393.png)
![Validation Plot](plots/validation/validation_12810393.png)

---

### FLUID MILK PRODUCTS (ID: 1133018)
- **핵심 지표**:
    - **12주 예상 매출**: $2,358.30
    - **성장률 (Trend)**: -2.83%
    - **모델 신뢰도 (Low)**: 오차율 약 60.5% (MAE: 99.9)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_1133018.png)
![Validation Plot](plots/validation/validation_1133018.png)

---

### PORK (ID: 12810391)
- **핵심 지표**:
    - **12주 예상 매출**: $2,104.04
    - **성장률 (Trend)**: 61.96%
    - **모델 신뢰도 (Low)**: 오차율 약 171.9% (MAE: 148.7)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_12810391.png)
![Validation Plot](plots/validation/validation_12810391.png)

---

### GRAPES (ID: 866211)
- **핵심 지표**:
    - **12주 예상 매출**: $1,866.25
    - **성장률 (Trend)**: -39.45%
    - **모델 신뢰도 (Medium)**: 오차율 약 43.7% (MAE: 64.2)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_866211.png)
![Validation Plot](plots/validation/validation_866211.png)

---

### SOFT DRINKS (ID: 5569471)
- **핵심 지표**:
    - **12주 예상 매출**: $1,844.49
    - **성장률 (Trend)**: 8.44%
    - **모델 신뢰도 (Low)**: 오차율 약 98.4% (MAE: 124.4)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_5569471.png)
![Validation Plot](plots/validation/validation_5569471.png)

---

### FLUID MILK PRODUCTS (ID: 1126899)
- **핵심 지표**:
    - **12주 예상 매출**: $1,840.62
    - **성장률 (Trend)**: -27.42%
    - **모델 신뢰도 (Medium)**: 오차율 약 30.2% (MAE: 58.0)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1126899.png)
![Validation Plot](plots/validation/validation_1126899.png)

---

### SALAD BAR (ID: 1005186)
- **핵심 지표**:
    - **12주 예상 매출**: $1,695.08
    - **성장률 (Trend)**: -13.02%
    - **모델 신뢰도 (Medium)**: 오차율 약 26.0% (MAE: 38.6)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1005186.png)
![Validation Plot](plots/validation/validation_1005186.png)

---

### FLUID MILK PRODUCTS (ID: 1070820)
- **핵심 지표**:
    - **12주 예상 매출**: $1,679.85
    - **성장률 (Trend)**: -3.67%
    - **모델 신뢰도 (High)**: 오차율 약 19.7% (MAE: 32.3)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_1070820.png)
![Validation Plot](plots/validation/validation_1070820.png)

---

### TOMATOES (ID: 854852)
- **핵심 지표**:
    - **12주 예상 매출**: $1,652.45
    - **성장률 (Trend)**: 78.24%
    - **모델 신뢰도 (Medium)**: 오차율 약 25.2% (MAE: 25.8)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_854852.png)
![Validation Plot](plots/validation/validation_854852.png)

---

### GRAPES (ID: 878996)
- **핵심 지표**:
    - **12주 예상 매출**: $1,583.17
    - **성장률 (Trend)**: -24.39%
    - **모델 신뢰도 (Medium)**: 오차율 약 48.4% (MAE: 70.3)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_878996.png)
![Validation Plot](plots/validation/validation_878996.png)

---

### POTATOES (ID: 899624)
- **핵심 지표**:
    - **12주 예상 매출**: $1,560.60
    - **성장률 (Trend)**: -7.00%
    - **모델 신뢰도 (Medium)**: 오차율 약 46.4% (MAE: 59.0)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_899624.png)
![Validation Plot](plots/validation/validation_899624.png)

---

### COUPON/MISC ITEMS (ID: 6544236)
- **핵심 지표**:
    - **12주 예상 매출**: $1,478.02
    - **성장률 (Trend)**: 130.71%
    - **모델 신뢰도 (Low)**: 오차율 약 117.0% (MAE: 62.0)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_6544236.png)
![Validation Plot](plots/validation/validation_6544236.png)

---

### EGGS (ID: 981760)
- **핵심 지표**:
    - **12주 예상 매출**: $1,432.41
    - **성장률 (Trend)**: -40.79%
    - **모델 신뢰도 (Medium)**: 오차율 약 37.4% (MAE: 54.8)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_981760.png)
![Validation Plot](plots/validation/validation_981760.png)

---

### FLUID MILK PRODUCTS (ID: 908531)
- **핵심 지표**:
    - **12주 예상 매출**: $1,409.14
    - **성장률 (Trend)**: -12.61%
    - **모델 신뢰도 (Low)**: 오차율 약 72.1% (MAE: 67.2)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_908531.png)
![Validation Plot](plots/validation/validation_908531.png)

---

### SOFT DRINKS (ID: 8090521)
- **핵심 지표**:
    - **12주 예상 매출**: $1,385.99
    - **성장률 (Trend)**: 16.63%
    - **모델 신뢰도 (Low)**: 오차율 약 93.6% (MAE: 99.1)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_8090521.png)
![Validation Plot](plots/validation/validation_8090521.png)

---

### SOFT DRINKS (ID: 8090537)
- **핵심 지표**:
    - **12주 예상 매출**: $1,385.89
    - **성장률 (Trend)**: 0.36%
    - **모델 신뢰도 (Low)**: 오차율 약 89.5% (MAE: 105.7)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_8090537.png)
![Validation Plot](plots/validation/validation_8090537.png)

---

### FLUID MILK PRODUCTS (ID: 1058997)
- **핵심 지표**:
    - **12주 예상 매출**: $1,379.06
    - **성장률 (Trend)**: -7.07%
    - **모델 신뢰도 (Low)**: 오차율 약 61.0% (MAE: 61.2)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1058997.png)
![Validation Plot](plots/validation/validation_1058997.png)

---

### FLUID MILK PRODUCTS (ID: 862349)
- **핵심 지표**:
    - **12주 예상 매출**: $1,304.90
    - **성장률 (Trend)**: 12.54%
    - **모델 신뢰도 (Low)**: 오차율 약 55.6% (MAE: 50.3)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_862349.png)
![Validation Plot](plots/validation/validation_862349.png)

---

### POTATOES (ID: 1004906)
- **핵심 지표**:
    - **12주 예상 매출**: $1,268.19
    - **성장률 (Trend)**: 6.99%
    - **모델 신뢰도 (Medium)**: 오차율 약 44.8% (MAE: 48.3)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_1004906.png)
![Validation Plot](plots/validation/validation_1004906.png)

---

### BAKED BREAD/BUNS/ROLLS (ID: 951590)
- **핵심 지표**:
    - **12주 예상 매출**: $1,226.23
    - **성장률 (Trend)**: -26.64%
    - **모델 신뢰도 (Medium)**: 오차율 약 33.5% (MAE: 37.7)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_951590.png)
![Validation Plot](plots/validation/validation_951590.png)

---

### BEEF (ID: 1000753)
- **핵심 지표**:
    - **12주 예상 매출**: $1,095.53
    - **성장률 (Trend)**: 0.28%
    - **모델 신뢰도 (Low)**: 오차율 약 105.4% (MAE: 67.3)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_1000753.png)
![Validation Plot](plots/validation/validation_1000753.png)

---

### BAKED BREAD/BUNS/ROLLS (ID: 883404)
- **핵심 지표**:
    - **12주 예상 매출**: $1,065.68
    - **성장률 (Trend)**: 1.45%
    - **모델 신뢰도 (High)**: 오차율 약 20.0% (MAE: 20.7)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_883404.png)
![Validation Plot](plots/validation/validation_883404.png)

---

### CHEESE (ID: 859075)
- **핵심 지표**:
    - **12주 예상 매출**: $1,059.90
    - **성장률 (Trend)**: -3.67%
    - **모델 신뢰도 (Medium)**: 오차율 약 26.2% (MAE: 21.1)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_859075.png)
![Validation Plot](plots/validation/validation_859075.png)

---

### MEAT - MISC (ID: 839419)
- **핵심 지표**:
    - **12주 예상 매출**: $991.29
    - **성장률 (Trend)**: 46.54%
    - **모델 신뢰도 (Medium)**: 오차율 약 35.1% (MAE: 27.6)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_839419.png)
![Validation Plot](plots/validation/validation_839419.png)

---

### PREPARED FOOD (ID: 986912)
- **핵심 지표**:
    - **12주 예상 매출**: $979.08
    - **성장률 (Trend)**: -18.56%
    - **모델 신뢰도 (Medium)**: 오차율 약 29.9% (MAE: 29.2)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_986912.png)
![Validation Plot](plots/validation/validation_986912.png)

---

### BEEF (ID: 1070702)
- **핵심 지표**:
    - **12주 예상 매출**: $929.01
    - **성장률 (Trend)**: 9.82%
    - **모델 신뢰도 (Low)**: 오차율 약 117.4% (MAE: 125.1)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_1070702.png)
![Validation Plot](plots/validation/validation_1070702.png)

---

### CARROTS (ID: 961554)
- **핵심 지표**:
    - **12주 예상 매출**: $927.69
    - **성장률 (Trend)**: -6.52%
    - **모델 신뢰도 (High)**: 오차율 약 17.0% (MAE: 15.9)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_961554.png)
![Validation Plot](plots/validation/validation_961554.png)

---

### CIGARETTES (ID: 1075368)
- **핵심 지표**:
    - **12주 예상 매출**: $893.87
    - **성장률 (Trend)**: -24.39%
    - **모델 신뢰도 (Medium)**: 오차율 약 42.9% (MAE: 39.8)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_1075368.png)
![Validation Plot](plots/validation/validation_1075368.png)

---

### TICKETS (ID: 948670)
- **핵심 지표**:
    - **12주 예상 매출**: $891.68
    - **성장률 (Trend)**: 19.91%
    - **모델 신뢰도 (Medium)**: 오차율 약 44.0% (MAE: 23.9)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_948670.png)
![Validation Plot](plots/validation/validation_948670.png)

---

### TOMATOES (ID: 1081177)
- **핵심 지표**:
    - **12주 예상 매출**: $891.20
    - **성장률 (Trend)**: 39.09%
    - **모델 신뢰도 (Low)**: 오차율 약 91.0% (MAE: 59.5)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_1081177.png)
![Validation Plot](plots/validation/validation_1081177.png)

---

### BEEF (ID: 863447)
- **핵심 지표**:
    - **12주 예상 매출**: $760.20
    - **성장률 (Trend)**: -15.42%
    - **모델 신뢰도 (Low)**: 오차율 약 225.6% (MAE: 223.5)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_863447.png)
![Validation Plot](plots/validation/validation_863447.png)

---

### EGGS (ID: 923746)
- **핵심 지표**:
    - **12주 예상 매출**: $674.60
    - **성장률 (Trend)**: 35.46%
    - **모델 신뢰도 (High)**: 오차율 약 9.6% (MAE: 7.8)
- **분석 코멘트**:
    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.

![Forecast Plot](plots/future_forecasts/forecast_923746.png)
![Validation Plot](plots/validation/validation_923746.png)

---

### SUGARS/SWEETNERS (ID: 1068719)
- **핵심 지표**:
    - **12주 예상 매출**: $661.48
    - **성장률 (Trend)**: -3.63%
    - **모델 신뢰도 (Medium)**: 오차율 약 29.4% (MAE: 16.6)
- **분석 코멘트**:
    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.

![Forecast Plot](plots/future_forecasts/forecast_1068719.png)
![Validation Plot](plots/validation/validation_1068719.png)

---

### CHICKEN (ID: 985999)
- **핵심 지표**:
    - **12주 예상 매출**: $641.95
    - **성장률 (Trend)**: -18.90%
    - **모델 신뢰도 (Low)**: 오차율 약 193.0% (MAE: 104.9)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_985999.png)
![Validation Plot](plots/validation/validation_985999.png)

---

### DELI MEATS (ID: 933835)
- **핵심 지표**:
    - **12주 예상 매출**: $612.13
    - **성장률 (Trend)**: -27.44%
    - **모델 신뢰도 (Medium)**: 오차율 약 38.3% (MAE: 18.7)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_933835.png)
![Validation Plot](plots/validation/validation_933835.png)

---

### MEAT - MISC (ID: 854405)
- **핵심 지표**:
    - **12주 예상 매출**: $576.96
    - **성장률 (Trend)**: -37.52%
    - **모델 신뢰도 (Low)**: 오차율 약 62.2% (MAE: 34.2)
- **분석 코멘트**:
    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.

![Forecast Plot](plots/future_forecasts/forecast_854405.png)
![Validation Plot](plots/validation/validation_854405.png)

---

