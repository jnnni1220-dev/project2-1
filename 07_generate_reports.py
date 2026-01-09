
import pandas as pd
import os

print("--- Generating Future Demand Reports ---")

# --- 1. Load Forecast Data ---
input_csv = '.\\results\\forecasts\\future_demand_forecasts_top50.csv'
summary_report_path = 'future_demand_summary_report.md'
detailed_report_path = 'future_demand_detailed_report.md'

try:
    df = pd.read_csv(input_csv)
    # Ensure date is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"Loaded {len(df)} forecast records.")
except Exception as e:
    print(f"Error loading forecasts: {e}")
    exit()

# --- 2. Load Product Metadata ---
product_mapping_path = '.\\dunnhumby.db\\product.csv'
try:
    product_mapping = pd.read_csv(product_mapping_path)
    # Select relevant columns and drop duplicates (in case of multiple entries per ID)
    product_mapping = product_mapping[['PRODUCT_ID', 'COMMODITY_DESC']].drop_duplicates(subset=['PRODUCT_ID'])
    print(f"Loaded product mapping for {len(product_mapping)} products.")
except Exception as e:
    print(f"Error loading product mapping: {e}")
    product_mapping = pd.DataFrame(columns=['PRODUCT_ID', 'COMMODITY_DESC'])

# --- 3. Calculate Aggregates (Prophet Focus) ---
# Group by Product_ID to get total forecasted sales for next 12 weeks
product_stats = df.groupby('Product_ID').agg(
    Total_Prophet_Forecast=('Prophet_Forecast', 'sum'),
    Total_SARIMA_Forecast=('SARIMA_Forecast', 'sum'),
    Start_Value=('Prophet_Forecast', 'first'),
    End_Value=('Prophet_Forecast', 'last')
).reset_index()

# Merge with product names
product_stats = product_stats.merge(product_mapping, left_on='Product_ID', right_on='PRODUCT_ID', how='left')
# Fill missing names
product_stats['COMMODITY_DESC'] = product_stats['COMMODITY_DESC'].fillna('Unknown Product')

# Calculate Growth Rate
product_stats['Growth_Rate'] = ((product_stats['End_Value'] - product_stats['Start_Value']) / product_stats['Start_Value']) * 100
product_stats = product_stats.sort_values('Total_Prophet_Forecast', ascending=False)

top_5_products = product_stats.head(5)
top_growers = product_stats.sort_values('Growth_Rate', ascending=False).head(5)

# --- 4. Generate Summary Report ---
print("Generating Summary Report...")
with open(summary_report_path, 'w', encoding='utf-8') as f:
    f.write("# 상품별 향후 수요 예측 최종 요약 보고서\n\n")
    f.write("## 1. 개요\n")
    f.write("- **분석 대상**: 총 매출액 기준 상위 50개 상품\n")
    f.write("- **예측 기간**: 향후 12주\n")
    f.write("- **사용 모델**: Prophet (메인), SARIMA (보조/비교용)\n\n")
    
    f.write("## 2. 핵심 인사이트\n")
    total_prophet = product_stats['Total_Prophet_Forecast'].sum()
    total_sarima = product_stats['Total_SARIMA_Forecast'].sum()
    
    top_product = top_5_products.iloc[0]
    f.write(f"- **총 예측 매출 규모 (12주)**:\n")
    f.write(f"    - **Prophet**: ${total_prophet:,.2f}\n")
    f.write(f"    - **SARIMA**: ${total_sarima:,.2f}\n")
    f.write(f"    - 두 모델 간 차이는 약 ${(total_prophet - total_sarima):,.2f} 입니다.\n")
    f.write(f"- **최고 매출 예상 상품**: `{top_product['COMMODITY_DESC']}` (ID: {int(top_product['Product_ID'])}) - ${top_product['Total_Prophet_Forecast']:,.2f}\n\n")

    f.write("## 3. Top 5 매출 예측 상품 (모델별 비교)\n")
    f.write("| Product Name | Product ID | Prophet Forecast ($) | SARIMA Forecast ($) | Growth Rate (Prophet %) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for _, row in top_5_products.iterrows():
        f.write(f"| {row['COMMODITY_DESC']} | {int(row['Product_ID'])} | ${row['Total_Prophet_Forecast']:,.2f} | ${row['Total_SARIMA_Forecast']:,.2f} | {row['Growth_Rate']:.2f}% |\n")
    f.write("\n")

    f.write("## 4. Top 5 급성장 예상 상품 (성장률 기준)\n")
    f.write("| Product Name | Product ID | Growth Rate (%) | Start Sales | End Sales |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for _, row in top_growers.iterrows():
        f.write(f"| {row['COMMODITY_DESC']} | {int(row['Product_ID'])} | {row['Growth_Rate']:.2f}% | ${row['Start_Value']:,.2f} | ${row['End_Value']:,.2f} |\n")
    f.write("\n")
    
    f.write("## 5. 결론 및 제언\n")
    f.write("- 대부분의 상위 상품은 안정적인 계절성 패턴을 보이고 있습니다.\n")
    f.write("- 급격한 성장이나 하락이 예상되는 상품에 대해서는 재고 관리 및 프로모션 계획의 선제적 조정이 필요합니다.\n")

print(f"Summary report saved to {summary_report_path}")

# --- 5. Generate Detailed Report ---
print("Generating Detailed Report...")
with open(detailed_report_path, 'w', encoding='utf-8') as f:
    f.write("# 향후 수요 예측 상세 분석 보고서\n\n")
    f.write("## 1. 분석 방법론\n")
    f.write("- **데이터셋**: 총 매출 기준 상위 50개 상품의 주간(Weekly) 집계 매출 데이터\n")
    f.write("- **데이터 전처리**:\n")
    f.write("    - **집계 방식**: `WEEK_NO`별 `SALES_VALUE` 합계.\n")
    f.write("    - **결측치 처리**: 매출이 없는 주차는 `0`으로 보간하여 시계열 연속성 유지.\n")
    f.write("    - **분석 대상**: 전체 기간 데이터를 학습(Train)에 사용하여 예측 정확도 극대화.\n\n")

    f.write("## 2. 모델링 상세\n")
    f.write("### A. Prophet (Main Model)\n")
    f.write("- **특징**: Facebook이 개발한 시계열 예측 라이브러리로, 트렌드 변화와 주기성(계절성)을 분해하여 분석.\n")
    f.write("- **설정**:\n")
    f.write("    - `yearly_seasonality=True`: 소매 데이터 특성상 연간 주기를 반영.\n")
    f.write("    - `weekly_seasonality=False`: 주간 데이터이므로 주 단위 계절성은 제외.\n")
    f.write("    - `changepoint_prior_scale`: 기본값 사용 (트렌드 변화 감지 민감도).\n")
    f.write("- **장점**: 결측치나 이상치에 강건하며, 비선형적인 성장 추세도 유연하게 포착.\n\n")

    f.write("### B. SARIMA (Reference Model)\n")
    f.write("- **특징**: 자기회귀(AR), 누적(I), 이동평균(MA)을 결합한 통계적 시계열 모델.\n")
    f.write("- **설정 (Fast Mode)**:\n")
    f.write("    - `auto_arima`를 통한 최적 파라미터(`p,d,q`) 자동 탐색.\n")
    f.write("    - **Non-seasonal**: 대량 처리를 위해 계절성 파라미터(`m`) 탐색 과정을 생략하고 단기 추세 중심 예측 수행.\n")
    f.write("- **역할**: Prophet 모델의 예측값이 통계적 추세와 크게 벗어나지 않는지 검증하는 기준선(Baseline) 활용.\n\n")
    
    f.write("## 3. 상품별 상세 예측 결과\n")
    f.write("> **참고**: 그래프는 `plots/future_forecasts/` 디렉토리에 저장되어 있습니다.\n\n")

    # Iterate over all products in order of total sales
    for _, row in product_stats.iterrows():
        pid = int(row['Product_ID'])
        pname = row['COMMODITY_DESC']
        f.write(f"### {pname} (ID: {pid})\n")
        f.write(f"- **Total Forecast (12w)**: ${row['Total_Prophet_Forecast']:,.2f}\n")
        f.write(f"- **Trend (Growth)**: {row['Growth_Rate']:.2f}%\n")
        f.write(f"- **Models Comparison**:\n")
        f.write(f"    - Prophet: ${row['Total_Prophet_Forecast']:,.2f}\n")
        f.write(f"    - SARIMA: ${row['Total_SARIMA_Forecast']:,.2f}\n\n")
        
        # Embed Plot
        plot_path = f"plots/future_forecasts/forecast_{pid}.png"
        f.write(f"![Forecast Plot for {pid}]({plot_path})\n\n")
        f.write("---\n\n")

print(f"Detailed report saved to {detailed_report_path}")
print("\n--- Reporting Complete ---")
