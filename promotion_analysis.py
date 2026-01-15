
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

    print("--- 3단계: 프로모션 효과 분석 ---")

    # Create a 'Has_Discount' column
    df['Has_Discount'] = df['Discount'] > 0

    # Group by 'Has_Discount' and calculate mean for key metrics
    discount_comparison = df.groupby('Has_Discount')[['TotalAmount', 'Quantity', 'UnitPrice']].mean().round(2)
    discount_comparison.index = ['No Discount', 'Has Discount']

    print("\n--- 할인 여부에 따른 평균 구매 지표 비교 ---")
    print(discount_comparison)

    # Visualize the comparison
    discount_comparison.plot(kind='bar', subplots=True, figsize=(15, 6), layout=(1, 3), legend=False, rot=0,
                             color=['#4C72B0', '#55A868', '#C44E52'])
    plt.suptitle('Comparison of Key Metrics by Discount', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('plots/discount_effect_comparison.png')
    plt.close()
    print("\n'plots/discount_effect_comparison.png'에 할인 효과 비교 차트를 저장했습니다.")


    # Correlation analysis
    print("\n\n--- 할인율과 주요 지표 간의 상관관계 분석 ---")
    correlation_matrix = df[['Discount', 'Quantity', 'UnitPrice', 'TotalAmount']].corr()
    print(correlation_matrix)

    # Visualize the correlation matrix as a heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Discount and Key Metrics', fontsize=16)
    plt.tight_layout()
    plt.savefig('plots/discount_correlation_heatmap.png')
    plt.close()
    print("\n'plots/discount_correlation_heatmap.png'에 상관관계 히트맵을 저장했습니다.")

    print("\n프로모션 효과 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
