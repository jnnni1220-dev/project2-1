
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create a directory to save plots if it doesn't exist
if not os.path.exists('plots'):
    os.makedirs('plots')

# Load the RFM segments data
try:
    rfm_df = pd.read_csv('rfm_segments.csv')

    print("--- 2단계: 고객 세그먼트별 분포 및 특성 분석 ---")

    # 1. Analyze Segment Distribution
    segment_counts = rfm_df['Customer_Segment'].value_counts()
    segment_percentages = rfm_df['Customer_Segment'].value_counts(normalize=True) * 100

    print("\n--- 고객 세그먼트별 분포 ---")
    dist_df = pd.DataFrame({
        'Count': segment_counts,
        'Percentage (%)': segment_percentages.round(2)
    })
    print(dist_df)

    # Visualize Segment Distribution
    plt.figure(figsize=(10, 6))
    sns.barplot(x=segment_counts.index, y=segment_counts.values, palette='viridis', order=segment_counts.index)
    plt.title('Customer Segment Distribution', fontsize=16)
    plt.xlabel('Customer Segment')
    plt.ylabel('Number of Customers')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/segment_distribution.png')
    plt.close()
    print("\n'plots/segment_distribution.png'에 고객 세그먼트 분포 차트를 저장했습니다.")

    # 2. Analyze RFM Characteristics by Segment
    segment_characteristics = rfm_df.groupby('Customer_Segment').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean'
    }).round(2)

    print("\n\n--- 고객 세그먼트별 평균 RFM 특성 ---")
    print(segment_characteristics)

    # Visualize RFM Characteristics
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
    fig.suptitle('RFM Characteristics by Customer Segment', fontsize=16)

    # Recency
    sns.barplot(ax=axes[0], y=segment_characteristics.index, x=segment_characteristics['Recency'], palette='coolwarm', order=segment_characteristics.sort_values('Recency', ascending=False).index)
    axes[0].set_title('Average Recency')

    # Frequency
    sns.barplot(ax=axes[1], y=segment_characteristics.index, x=segment_characteristics['Frequency'], palette='coolwarm', order=segment_characteristics.sort_values('Frequency').index)
    axes[1].set_title('Average Frequency')
    axes[1].set_ylabel('')

    # Monetary
    sns.barplot(ax=axes[2], y=segment_characteristics.index, x=segment_characteristics['Monetary'], palette='coolwarm', order=segment_characteristics.sort_values('Monetary').index)
    axes[2].set_title('Average Monetary')
    axes[2].set_ylabel('')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('plots/segment_rfm_characteristics.png')
    plt.close()
    print("\n'plots/segment_rfm_characteristics.png'에 세그먼트별 RFM 특성 차트를 저장했습니다.")
    
    print("\n고객 세그먼트 분석이 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'rfm_segments.csv' 파일을 찾을 수 없습니다. 이전 단계가 정상적으로 완료되었는지 확인해주세요.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
