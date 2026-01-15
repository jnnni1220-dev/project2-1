
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Create a directory to save plots if it doesn't exist
if not os.path.exists('plots'):
    os.makedirs('plots')

# Load the dataset
try:
    df = pd.read_csv('Amazon.csv', dtype={'CustomerID': str})
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])

    print("--- 1단계: 코호트 분석을 통한 고객 유지율(Retention) 분석 ---")

    # --- Cohort Analysis ---
    def get_month(x): return dt.datetime(x.year, x.month, 1)
    df['OrderMonth'] = df['OrderDate'].apply(lambda x: x.strftime('%Y-%m'))
    df['CohortMonth'] = df.groupby('CustomerID')['OrderMonth'].transform('min')

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day

    # Convert OrderMonth and CohortMonth to datetime for calculation
    order_month_dt = pd.to_datetime(df['OrderMonth'])
    cohort_month_dt = pd.to_datetime(df['CohortMonth'])

    # Calculate cohort index
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


    print("\n--- 고객 유지율 (Retention Rate) 테이블 ---")
    print((cohort_retention*100).round(2).to_string().replace('NaN', ''))

    # Visualize the retention rate as a heatmap
    plt.figure(figsize=(18, 14))
    sns.heatmap(cohort_retention, annot=True, fmt='.0%', cmap='coolwarm')
    plt.title('Monthly Customer Retention Rate', fontsize=16)
    plt.xlabel('Months After First Purchase')
    plt.ylabel('First Purchase Month (Cohort)')
    plt.tight_layout()
    plt.savefig('plots/cohort_retention_heatmap.png')
    plt.close()
    print("\n\n'plots/cohort_retention_heatmap.png'에 코호트 리텐션 히트맵을 저장했습니다.")

    print("\n코호트 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
