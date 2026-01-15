
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

    print("--- 1단계: 이커머스 핵심 KPI 계산 (MAU) ---")

    # Convert OrderDate to datetime and extract YearMonth
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    df['YearMonth'] = df['OrderDate'].dt.to_period('M')

    # Calculate Monthly Active Users (MAU)
    mau = df.groupby('YearMonth')['CustomerID'].nunique()
    print("\n--- 월별 활성 사용자 수 (MAU) ---")
    print(mau)

    # Visualize MAU
    plt.figure(figsize=(15, 7))
    mau.plot(kind='bar', color=sns.color_palette('coolwarm'))
    plt.title('Monthly Active Users (MAU)', fontsize=16)
    plt.xlabel('Month')
    plt.ylabel('Number of Unique Customers')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/monthly_active_users.png')
    plt.close()
    print("\n'plots/monthly_active_users.png'에 월별 활성 사용자 수 차트를 저장했습니다.")

    print("\nMAU 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
