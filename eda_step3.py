
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

    # --- Time Series Analysis ---
    print("--- 시간 흐름에 따른 매출 분석 ---")

    # Convert OrderDate to datetime and extract year and month
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    df['Year'] = df['OrderDate'].dt.year
    df['Month'] = df['OrderDate'].dt.month
    df['YearMonth'] = df['OrderDate'].dt.to_period('M')

    # 1. Monthly Sales Trend
    monthly_sales = df.groupby('YearMonth')['TotalAmount'].sum().sort_index()
    print("\n월별 총 매출액을 계산하고 'plots/monthly_sales_trend.png'로 저장합니다.")

    plt.figure(figsize=(15, 7))
    monthly_sales.plot(kind='line', marker='o', linestyle='-')
    plt.title('Monthly Sales Trend', fontsize=16)
    plt.xlabel('Month')
    plt.ylabel('Total Sales Amount')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/monthly_sales_trend.png')
    plt.close()

    # 2. Yearly Sales Trend
    yearly_sales = df.groupby('Year')['TotalAmount'].sum()
    print("\n연도별 총 매출액을 계산하고 'plots/yearly_sales.png'로 저장합니다.")

    plt.figure(figsize=(10, 6))
    yearly_sales.plot(kind='bar', color=sns.color_palette('viridis'))
    plt.title('Yearly Sales Amount', fontsize=16)
    plt.xlabel('Year')
    plt.ylabel('Total Sales Amount')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('plots/yearly_sales.png')
    plt.close()
    
    print("\n시간 흐름 분석이 완료되었습니다. 'plots' 폴더에서 생성된 차트를 확인하세요.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
