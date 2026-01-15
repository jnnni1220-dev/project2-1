
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

    print("--- 주요 카테고리 및 브랜드 분석 (매출 기준) ---")

    # 1. Top 10 Categories by Total Sales Amount
    top_10_categories = df.groupby('Category')['TotalAmount'].sum().nlargest(10)
    print("\n--- 총 매출액 기준 Top 10 카테고리 ---")
    print(top_10_categories)

    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_10_categories.values, y=top_10_categories.index, palette='viridis')
    plt.title('Top 10 Categories by Total Sales Amount', fontsize=16)
    plt.xlabel('Total Sales Amount')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig('plots/top_10_categories_by_amount.png')
    plt.close()
    print("\n'plots/top_10_categories_by_amount.png'에 차트를 저장했습니다.")

    # 2. Top 10 Brands by Total Sales Amount
    top_10_brands = df.groupby('Brand')['TotalAmount'].sum().nlargest(10)
    print("\n\n--- 총 매출액 기준 Top 10 브랜드 ---")
    print(top_10_brands)

    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_10_brands.values, y=top_10_brands.index, palette='plasma')
    plt.title('Top 10 Brands by Total Sales Amount', fontsize=16)
    plt.xlabel('Total Sales Amount')
    plt.ylabel('Brand')
    plt.tight_layout()
    plt.savefig('plots/top_10_brands_by_amount.png')
    plt.close()
    print("\n'plots/top_10_brands_by_amount.png'에 차트를 저장했습니다.")

    print("\n카테고리 및 브랜드 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
