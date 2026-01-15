import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create a directory to save plots
if not os.path.exists('plots'):
    os.makedirs('plots')

# Load the dataset
try:
    df = pd.read_csv('Amazon.csv')

    # Convert OrderDate to datetime
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])

    print("--- 데이터 정제 및 시각화 ---")
    print("'OrderDate' 컬럼을 datetime 형식으로 변환했습니다.")

    # --- Numerical Data Analysis ---
    numerical_cols = ['Quantity', 'UnitPrice', 'Discount', 'Tax', 'ShippingCost', 'TotalAmount']
    print(f"\n숫자형 데이터({', '.join(numerical_cols)})의 분포를 히스토그램으로 확인하고 'plots' 폴더에 저장합니다.")

    for col in numerical_cols:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[col], kde=True)
        plt.title(f'Distribution of {col}', fontsize=15)
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.savefig(f'plots/{col}_histogram.png')
        plt.close()

    # --- Categorical Data Analysis ---
    # We'll analyze the top 15 for high-cardinality columns to keep plots readable
    categorical_cols = ['Category', 'Brand', 'PaymentMethod', 'OrderStatus', 'Country', 'State']
    print(f"\n범주형 데이터({', '.join(categorical_cols)})의 빈도를 막대 차트로 확인하고 'plots' 폴더에 저장합니다.")

    for col in categorical_cols:
        plt.figure(figsize=(12, 8))
        if df[col].nunique() > 15:
            top_15 = df[col].value_counts().nlargest(15)
            sns.barplot(x=top_15.index, y=top_15.values, palette='viridis')
            plt.title(f'Top 15 {col} by Frequency', fontsize=15)
        else:
            sns.countplot(y=df[col], order=df[col].value_counts().index, palette='viridis')
            plt.title(f'Frequency of {col}', fontsize=15)

        plt.xlabel('Count')
        plt.ylabel(col)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'plots/{col}_barchart.png')
        plt.close()

    print("\n분석이 완료되었습니다. 'plots' 폴더에서 생성된 차트들을 확인하실 수 있습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
