import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define integrated data path
integrated_data_path = 'dunnhumby_integrated_data.csv'
plots_dir = 'dunnhumby_plots'

# --- Phase 2: Analysis Execution - KPI Analysis ---
print("--- Dunnhumby KPI 분석: 월별 활성 사용자 (MAU) ---")

try:
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Calculate MAU
    df['YearMonth'] = df['OrderDate'].dt.to_period('M')
    mau = df.groupby('YearMonth')['CustomerID'].nunique()

    print("\n--- 월별 활성 사용자 수 (MAU) ---")
    print(mau)

    # Visualize MAU
    plt.figure(figsize=(15, 7))
    mau.plot(kind='bar', color=sns.color_palette('coolwarm', n_colors=len(mau)))
    plt.title('Dunnhumby Monthly Active Users (MAU)', fontsize=16)
    plt.xlabel('Month')
    plt.ylabel('Number of Unique Customers')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_monthly_active_users.png'))
    plt.close()
    print(f"\n'{plots_dir}/dunnhumby_monthly_active_users.png'에 월별 활성 사용자 수 차트를 저장했습니다.")

    print("\nDunnhumby MAU 분석 완료.")

except FileNotFoundError:
    print(f"오류: '{integrated_data_path}' 파일을 찾을 수 없습니다. 데이터 통합이 먼저 완료되어야 합니다.")
except Exception as e:
    print(f"Dunnhumby MAU 분석 중 오류가 발생했습니다: {e}")
