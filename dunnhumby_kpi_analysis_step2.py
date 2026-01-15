
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import datetime as dt

# Define integrated data path and plots directory
integrated_data_path = 'dunnhumby_integrated_data.csv'
plots_dir = 'dunnhumby_plots'

# --- Phase 2: Analysis Execution - KPI Analysis ---
print("--- Dunnhumby KPI 분석: 코호트 분석을 통한 고객 유지율 (Retention) ---")

try:
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # --- Cohort Analysis ---
    df['OrderMonth'] = df['OrderDate'].apply(lambda x: x.strftime('%Y-%m'))
    df['CohortMonth'] = df.groupby('CustomerID')['OrderMonth'].transform('min')

    # Calculate cohort index
    # Convert OrderMonth and CohortMonth to datetime objects for calculation
    order_month_dt = pd.to_datetime(df['OrderMonth'])
    cohort_month_dt = pd.to_datetime(df['CohortMonth'])

    years_diff = order_month_dt.dt.year - cohort_month_dt.dt.year
    months_diff = order_month_dt.dt.month - cohort_month_dt.dt.month
    df['CohortIndex'] = years_diff * 12 + months_diff + 1

    # Calculate cohort counts
    cohort_data = df.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
    cohort_count = cohort_data.pivot_table(index='CohortMonth', columns='CohortIndex', values='CustomerID')
    
    # Calculate retention rate
    cohort_size = cohort_count.iloc[:, 0]
    cohort_retention = cohort_count.divide(cohort_size, axis=0)
    cohort_retention.index = pd.to_datetime(cohort_retention.index).strftime('%Y-%m')

    print("\n--- Dunnhumby 고객 유지율 (Retention Rate) 테이블 ---")
    # Display only a subset of columns for readability if there are too many months
    display_retention = (cohort_retention * 100).round(2)
    print(display_retention.head(10).to_string().replace('NaN', '')) # show first 10 cohorts, all indices

    # Visualize the retention rate as a heatmap
    plt.figure(figsize=(18, 14))
    sns.heatmap(cohort_retention, annot=True, fmt='.0%', cmap='coolwarm')
    plt.title('Dunnhumby Monthly Customer Retention Rate', fontsize=16)
    plt.xlabel('Months After First Purchase')
    plt.ylabel('First Purchase Month (Cohort)')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_cohort_retention_heatmap.png'))
    plt.close()
    print(f"\n\n'{plots_dir}/dunnhumby_cohort_retention_heatmap.png'에 코호트 리텐션 히트맵을 저장했습니다.")

    print("\nDunnhumby 코호트 분석 완료.")

except FileNotFoundError:
    print(f"오류: '{integrated_data_path}' 파일을 찾을 수 없습니다. 데이터 통합이 먼저 완료되어야 합니다.")
except Exception as e:
    print(f"Dunnhumby 코호트 분석 중 오류가 발생했습니다: {e}")
