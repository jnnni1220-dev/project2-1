
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define integrated data path and plots directory
integrated_data_path = 'dunnhumby_integrated_data.csv'
plots_dir = 'dunnhumby_plots'

# --- Phase 2: Analysis Execution - KPI Analysis ---
print("--- Dunnhumby KPI 분석: 결제 유저당 평균 수익 (ARPPU) ---")

try:
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Calculate Monthly Revenue and Paying Users (PU)
    df['YearMonth'] = df['OrderDate'].dt.to_period('M')
    monthly_revenue = df.groupby('YearMonth')['TotalAmount'].sum()
    paying_users = df.groupby('YearMonth')['CustomerID'].nunique() # PU is unique CustomerID

    # Calculate ARPPU
    arppu = monthly_revenue / paying_users
    arppu.index = arppu.index.to_timestamp() # Convert PeriodIndex to DatetimeIndex for plotting

    print("\n--- 월별 결제 유저당 평균 수익 (ARPPU) ---")
    print(arppu.round(2))

    # Visualize ARPPU
    plt.figure(figsize=(15, 7))
    arppu.plot(kind='line', marker='o', linestyle='-', color='green')
    plt.title('Dunnhumby Monthly Average Revenue Per Paying User (ARPPU)', fontsize=16)
    plt.xlabel('Month')
    plt.ylabel('ARPPU ($)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_monthly_arppu.png'))
    plt.close()
    print(f"\n'{plots_dir}/dunnhumby_monthly_arppu.png'에 월별 ARPPU 추이 차트를 저장했습니다.")

    print("\nDunnhumby ARPPU 분석 완료.")

except FileNotFoundError:
    print(f"오류: '{integrated_data_path}' 파일을 찾을 수 없습니다. 데이터 통합이 먼저 완료되어야 합니다.")
except Exception as e:
    print(f"Dunnhumby ARPPU 분석 중 오류가 발생했습니다: {e}")
