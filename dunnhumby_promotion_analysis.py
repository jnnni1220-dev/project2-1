
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define integrated data path and plots directory
integrated_data_path = 'dunnhumby_integrated_data.csv'
plots_dir = 'dunnhumby_plots'

# --- Phase 2: Analysis Execution - Promotion Effect Analysis ---
print("--- Dunnhumby 프로모션 효과 분석 ---")

try:
    df = pd.read_csv(integrated_data_path)
    
    # Define 'Has_Discount' based on the 'Discount' column (absolute sum of all discounts)
    df['Has_Discount'] = df['Discount'] > 0

    # Group by 'Has_Discount' and calculate mean for key metrics
    # Note: For UnitPrice, we will calculate average unit price per transaction line item
    # Since TotalAmount and Quantity are already per line item.
    df['UnitPrice'] = df['TotalAmount'] / df['Quantity']
    df['UnitPrice'].replace([np.inf, -np.inf], np.nan, inplace=True) # Handle division by zero if Quantity is 0
    df['UnitPrice'].fillna(0, inplace=True) # Replace NaN (from division by zero) with 0

    discount_comparison = df.groupby('Has_Discount')[['TotalAmount', 'Quantity', 'UnitPrice']].mean().round(2)
    discount_comparison.index = ['No Discount', 'Has Discount']

    print("\n--- 할인 여부에 따른 평균 구매 지표 비교 ---")
    print(discount_comparison)

    # Visualize the comparison
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))
    fig.suptitle('Dunnhumby Comparison of Key Metrics by Discount', fontsize=16)

    sns.barplot(ax=axes[0], x=discount_comparison.index, y=discount_comparison['TotalAmount'], palette='viridis')
    axes[0].set_title('Average Total Amount')
    axes[0].set_ylabel('Average Total Amount ($)')
    axes[0].set_xlabel('')
    axes[0].tick_params(axis='x', rotation=45)

    sns.barplot(ax=axes[1], x=discount_comparison.index, y=discount_comparison['Quantity'], palette='viridis')
    axes[1].set_title('Average Quantity')
    axes[1].set_ylabel('Average Quantity')
    axes[1].set_xlabel('')
    axes[1].tick_params(axis='x', rotation=45)

    sns.barplot(ax=axes[2], x=discount_comparison.index, y=discount_comparison['UnitPrice'], palette='viridis')
    axes[2].set_title('Average Unit Price')
    axes[2].set_ylabel('Average Unit Price ($)')
    axes[2].set_xlabel('')
    axes[2].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.9])
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_discount_effect_comparison.png'))
    plt.close()
    print(f"\n'{plots_dir}/dunnhumby_discount_effect_comparison.png'에 할인 효과 비교 차트를 저장했습니다.")


    # Correlation analysis
    print("\n\n--- 할인율과 주요 지표 간의 상관관계 분석 ---")
    correlation_matrix = df[['Discount', 'Quantity', 'TotalAmount', 'UnitPrice']].corr()
    print(correlation_matrix)

    # Visualize the correlation matrix as a heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Dunnhumby Correlation Matrix of Discount and Key Metrics', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_discount_correlation_heatmap.png'))
    plt.close()
    print(f"\n'{plots_dir}/dunnhumby_discount_correlation_heatmap.png'에 상관관계 히트맵을 저장했습니다.")

    print("\nDunnhumby 프로모션 효과 분석 완료.")

except FileNotFoundError:
    print(f"오류: '{integrated_data_path}' 파일을 찾을 수 없습니다. 데이터 통합이 먼저 완료되어야 합니다.")
except Exception as e:
    print(f"Dunnhumby 프로모션 효과 분석 중 오류가 발생했습니다: {e}")
