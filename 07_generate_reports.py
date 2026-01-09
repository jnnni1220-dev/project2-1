
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


# --- 6. Load Backtest Metrics ---
try:
    backtest_csv = 'prophet_backtest_metrics.csv'
    if os.path.exists(backtest_csv):
        metrics_df = pd.read_csv(backtest_csv)
        avg_mae = metrics_df['MAE'].mean()
        avg_rmse = metrics_df['RMSE'].mean()
        print(f"Loaded backtest metrics. Avg MAE: {avg_mae:.2f}")
    else:
        metrics_df = pd.DataFrame()
        avg_mae = 0
except Exception as e:
    metrics_df = pd.DataFrame()
    print(f"Error loading backtest metrics: {e}")

# --- 7. Generate Detailed Report with Insights ---
print("Generating Detailed Report...")
with open(detailed_report_path, 'w', encoding='utf-8') as f:
    f.write("# 향후 수요 예측 상세 분석 보고서 (Detailed Demand Forecasting)\n\n")
    
    f.write("## 1. 분석 방법론 및 검증 (Methodology & Validation)\n")
    f.write("- **데이터셋**: 총 매출 기준 상위 50개 상품의 주간(Weekly) 집계 매출 데이터\n")
    f.write("- **검증 방식 (Backtesting)**:\n")
    f.write(f"    - **목적**: 모델의 예측 정확도를 평가하기 위해 과거의 마지막 4주 데이터를 '미래'라고 가정하고 테스트했습니다.\n")
    f.write(f"    - **실제 예측**: 최종적으로 제공된 향후 12주 예측 결과는 **검증에 사용된 4주를 포함한 전체 데이터**를 모두 학습하여 산출되었습니다.\n")
    f.write(f"    - **전체 평균 오차 (Mean Absolute Error)**: 약 {avg_mae:.2f} (Units)\n")
    f.write("    - 오차가 적을수록 모델의 예측 신뢰도가 높음을 의미합니다.\n\n")

    f.write("## 2. 전략적 인사이트 (Strategic Deep Dive)\n")
    f.write("**[데이터 기반 전략 제언]**\n")
    f.write("본 예측 모델은 단순히 과거의 평균을 따르는 것이 아니라, 계절적 패턴(Seasonality)과 최근의 트렌드 변화(Trend Changepoints)를 모두 반영합니다. ")
    f.write("특히 상위 5개 급성장 상품의 경우, 단순 재고 보충(Replenishment) 수준을 넘어선 공격적인 프로모션 전략이 유효할 것으로 보입니다. ")
    f.write("반면, 하락세가 뚜렷한 상품군은 재고 회전율을 높이기 위한 할인 판매나 번들링(Bundling) 전략(Cross-Selling 리포트 참조)을 병행하여 리스크를 관리해야 합니다. ")
    f.write(f"검증 단계에서 MAE가 낮게 측정된 상품들은 자동 발주(Auto-Ordering) 시스템 적용을 적극 고려하십시오.\n\n")
    
    f.write("## 3. 상품별 상세 예측 및 검증 결과\n")
    f.write("> **설명**: 왼쪽 그래프는 향후 12주 예측, 오른쪽(또는 하단) 수치는 모델 신뢰도 지표입니다.\n\n")

    # Iterate over all products
    for _, row in product_stats.iterrows():
        pid = int(row['Product_ID'])
        pname = row['COMMODITY_DESC']
        
        # Get metric for this product
        p_metric = metrics_df[metrics_df['Product_ID'] == pid]
        if not p_metric.empty:
            mae_val = p_metric.iloc[0]['MAE']
            test_mean = p_metric.iloc[0]['Test_Mean']
            # Error percent relative to sales volume
            if test_mean > 0:
                err_pct = (mae_val / test_mean) * 100
                confidence_level = "High" if err_pct < 20 else "Medium" if err_pct < 50 else "Low"
            else:
                confidence_level = "N/A"
                err_pct = 0
        else:
            mae_val = 0
            err_pct = 0
            confidence_level = "Unknown"

        f.write(f"### {pname} (ID: {pid})\n")
        f.write(f"- **핵심 지표**:\n")
        f.write(f"    - **12주 예상 매출**: ${row['Total_Prophet_Forecast']:,.2f}\n")
        f.write(f"    - **성장률 (Trend)**: {row['Growth_Rate']:.2f}%\n")
        f.write(f"    - **모델 신뢰도 ({confidence_level})**: 오차율 약 {err_pct:.1f}% (MAE: {mae_val:.1f})\n")
        
        f.write(f"- **분석 코멘트**:\n")
        if row['Growth_Rate'] > 5:
            f.write(f"    - 뚜렷한 상승세가 관측됩니다. 재고 부족(Stock-out) 방지에 집중하십시오.\n")
        elif row['Growth_Rate'] < -5:
            f.write(f"    - 수요 감소가 예상됩니다. 마케팅 강화를 통한 수요 진작이 필요합니다.\n")
        else:
            f.write(f"    - 안정적인 수요가 유지될 전망입니다. 정기 배송/구독 모델 도입을 검토해볼 수 있습니다.\n")
            
        f.write(f"\n")
        
        # Embed Forecast Plot
        plot_path = f"plots/future_forecasts/forecast_{pid}.png"
        f.write(f"![Forecast Plot]({plot_path})\n")
        
        # Embed Validation Plot
        val_plot_path = f"plots/validation/validation_{pid}.png"
        if os.path.exists(val_plot_path):
             f.write(f"![Validation Plot]({val_plot_path})\n")
        
        f.write("\n---\n\n")

print(f"Detailed report saved to {detailed_report_path}")
print("\n--- Reporting Complete ---")
