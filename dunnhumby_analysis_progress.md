# Dunnhumby 데이터 분석 진행 상황

## 1. 완료된 작업
다음 작업들은 Dunnhumby 데이터셋에 대한 분석 과정에서 성공적으로 완료되었습니다.

*   **Dunnhumby 데이터 통합 및 저장**:
    *   `transaction_data.csv`, `product.csv`, `hh_demographic.csv` 파일을 병합하여 `dunnhumby_integrated_data.csv`로 저장했습니다. (`BASKET_ID` 컬럼 포함)
    *   `DAY` 컬럼을 `OrderDate` (날짜 형식)으로 변환했습니다.
    *   제품 이름 및 할인 컬럼을 통합하고 정리했습니다.
*   **Dunnhumby KPI 분석: 월별 활성 사용자 (MAU) 계산**:
    *   월별 순수 고객 수를 계산하고 시각화하여 `dunnhumby_plots/dunnhumby_monthly_active_users.png`로 저장했습니다.
    *   초기 성장 후 2021년 말 감소하는 MAU 트렌드를 확인했습니다.
*   **Dunnhumby KPI 분석: 코호트 분석을 통한 고객 유지율(Retention) 분석 및 시각화**:
    *   고객 코호트를 정의하고, 시간이 지남에 따른 고객 유지율을 계산했습니다.
    *   결과를 히트맵으로 시각화하여 `dunnhumby_plots/dunnhumby_cohort_retention_heatmap.png`로 저장했습니다.
    *   Amazon 데이터와 대조적으로 높은 초기 유지율(80%대)과 점진적인 유지율 하락을 확인했습니다.
*   **Dunnhumby KPI 분석: 결제 유저당 평균 수익(ARPPU) 계산**:
    *   월별 결제 유저당 평균 수익을 계산하고 시각화하여 `dunnhumby_plots/dunnhumby_monthly_arppu.png`로 저장했습니다.
    *   2020년 초부터 2021년 말까지 ARPPU의 꾸준한 상승세와 2021년 12월의 급격한 하락을 확인했습니다.
*   **Dunnhumby RFM 분석: R/F/M 값 계산 및 고객 세분화**:
    *   각 고객별 Recency, Frequency, Monetary 값을 계산하고, 이를 기반으로 VIP, Loyal Customers, Potential Loyalists, At-Risk Customers, Lost Customers 세그먼트로 분류했습니다.
    *   결과를 `dunnhumby_rfm_segments.csv` 파일로 저장했습니다.
*   **Dunnhumby RFM 분석: 고객 세그먼트별 분포 및 특성 분석**:
    *   고객 세그먼트별 분포와 각 세그먼트의 평균 RFM 특성을 분석하고 시각화했습니다.
    *   결과를 `dunnhumby_plots/dunnhumby_segment_distribution.png` 및 `dunnhumby_plots/dunnhumby_segment_rfm_characteristics.png`로 저장했습니다.
    *   Dunnhumby 고객들이 높은 충성도와 활성도를 보이며, VIP 고객의 기여도가 크다는 점을 확인했습니다.
*   **Dunnhumby 프로모션 효과 분석: 할인이 구매 행동에 미치는 영향 분석**:
    *   할인 여부에 따른 평균 구매 지표(총 금액, 수량, 단가)를 비교하고, 할인율과 지표 간의 상관관계를 분석했습니다.
    *   결과를 `dunnhumby_plots/dunnhumby_discount_effect_comparison.png` 및 `dunnhumby_plots/dunnhumby_discount_correlation_heatmap.png`로 저장했습니다.
    *   할인이 총 구매 금액을 미세하게 높이는 경향이 있으나, 평균 구매 수량에서 비정상적인 값이 관찰되어 추가 검증이 필요함을 확인했습니다.
*   **Dunnhumby 교차 구매 분석 (장바구니 분석)**:
    *   판매량 기준 상위 50개 상품을 대상으로 장바구니 데이터를 10% 샘플링하여 연관 규칙을 분석했습니다.
    *   높은 향상도(Lift)를 가진 상위 10개 연관 규칙을 도출했습니다.

## 2. 남은 작업
다음 작업들은 Dunnhumby 데이터셋 분석을 완료하기 위해 남아 있습니다.

*   **Dunnhumby 추가 탐색적 분석: 인구통계학적 인사이트**:
    *   `hh_demographic.csv`의 인구통계학적 정보를 활용하여 고객의 연령, 소득, 가구 구성 등이 구매 행동이나 RFM 세그먼트에 미치는 영향을 분석합니다.
*   **Dunnhumby 분석 최종 보고서 생성**:
    *   지금까지 수행된 모든 Dunnhumby 데이터 분석 결과를 종합하고 해석을 포함하여 `dunnhumby_analysis_report.md` 파일로 보고서를 생성합니다.

---

**현재 상태:**
Dunnhumby 데이터셋에 대한 핵심적인 KPI 분석, RFM 분석, 프로모션 효과 분석, 교차 구매 분석이 완료되었습니다. 다음번에는 인구통계학적 데이터를 활용한 추가 탐색적 분석을 진행하여 고객 이해도를 높이고, 마지막으로 전체 분석 결과를 종합한 보고서를 작성할 예정입니다.
