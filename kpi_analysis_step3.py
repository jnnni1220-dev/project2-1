
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create a directory to save plots if it doesn't exist
if not os.path.exists('plots'):
    os.makedirs('plots')

# Load the dataset
try:
    df = pd.read_csv('Amazon.csv')

    print("--- 1단계: 이커머스 핵심 KPI 계산 (ARPPU) ---")

    # Convert OrderDate to datetime and extract YearMonth
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    df['YearMonth'] = df['OrderDate'].dt.to_period('M')

    # Calculate Monthly Revenue and Paying Users (PU)
    monthly_revenue = df.groupby('YearMonth')['TotalAmount'].sum()
    paying_users = df.groupby('YearMonth')['CustomerID'].nunique()

    # Calculate ARPPU
    arppu = monthly_revenue / paying_users
    arppu.index = arppu.index.to_timestamp() # Convert PeriodIndex to DatetimeIndex for plotting

    print("\n--- 월별 결제 유저당 평균 수익 (ARPPU) ---")
    print(arppu.round(2))

    # Visualize ARPPU
    plt.figure(figsize=(15, 7))
    arppu.plot(kind='line', marker='o', linestyle='-', color='green')
    plt.title('Monthly Average Revenue Per Paying User (ARPPU)', fontsize=16)
    plt.xlabel('Month')
    plt.ylabel('ARPPU ($)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/monthly_arppu.png')
    plt.close()
    print("\n'plots/monthly_arppu.png'에 월별 ARPPU 추이 차트를 저장했습니다.")

    print("\nARPPU 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
