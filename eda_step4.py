
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

    print("--- 인기 상품 Top 10 분석 ---")

    # 1. Top 10 Products by Total Sales Amount
    top_10_amount = df.groupby('ProductName')['TotalAmount'].sum().nlargest(10)
    print("\n--- 총 매출액 기준 Top 10 상품 ---")
    print(top_10_amount)

    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_10_amount.values, y=top_10_amount.index, palette='plasma')
    plt.title('Top 10 Products by Total Sales Amount', fontsize=16)
    plt.xlabel('Total Sales Amount')
    plt.ylabel('Product Name')
    plt.tight_layout()
    plt.savefig('plots/top_10_products_by_amount.png')
    plt.close()
    print("\n'plots/top_10_products_by_amount.png'에 차트를 저장했습니다.")

    # 2. Top 10 Products by Quantity Sold
    top_10_quantity = df.groupby('ProductName')['Quantity'].sum().nlargest(10)
    print("\n\n--- 판매량 기준 Top 10 상품 ---")
    print(top_10_quantity)

    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_10_quantity.values, y=top_10_quantity.index, palette='magma')
    plt.title('Top 10 Products by Quantity Sold', fontsize=16)
    plt.xlabel('Total Quantity Sold')
    plt.ylabel('Product Name')
    plt.tight_layout()
    plt.savefig('plots/top_10_products_by_quantity.png')
    plt.close()
    print("\n'plots/top_10_products_by_quantity.png'에 차트를 저장했습니다.")

    print("\n인기 상품 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
