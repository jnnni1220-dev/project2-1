
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define file paths
integrated_data_path = 'dunnhumby_integrated_data.csv'
rfm_segments_path = 'dunnhumby_rfm_segments.csv'
plots_dir = 'dunnhumby_plots'

print("--- Dunnhumby 인구통계학적 특성 분석 ---")

try:
    # 1. Load RFM segments
    rfm_df = pd.read_csv(rfm_segments_path)
    print("RFM 세그먼트 데이터를 로드했습니다.")

    # 2. Load necessary demographic columns from the large integrated data file
    demographic_cols = [
        'CustomerID', 'CustomerAge', 'CustomerIncome', 'MARITAL_STATUS_CODE',
        'HOMEOWNER_DESC', 'HH_COMP_DESC', 'HOUSEHOLD_SIZE_DESC', 'KID_CATEGORY_DESC'
    ]
    # Use an iterator to read the large CSV in chunks if memory is an issue,
    # but for now, we try to load only specific columns.
    # We only need one entry per customer, so we can drop duplicates.
    df_demographics = pd.read_csv(integrated_data_path, usecols=demographic_cols).drop_duplicates(subset=['CustomerID'])
    print("인구통계학적 데이터를 로드하고 중복을 제거했습니다.")

    # 3. Merge RFM data with demographic data
    df_merged = pd.merge(rfm_df, df_demographics, on='CustomerID', how='left')
    print("RFM 데이터와 인구통계학적 데이터를 병합했습니다.")

    # 4. Analyze and visualize the relationship
    
    # Define the order of segments for consistent plotting
    segment_order = ['VIP', 'Loyal Customers', 'Potential Loyalists', 'At-Risk Customers', 'Lost Customers']

    # --- Analysis by Customer Age ---
    plt.figure(figsize=(12, 8))
    sns.countplot(y='CustomerAge', hue='Customer_Segment', data=df_merged, palette='viridis', hue_order=segment_order)
    plt.title('Customer Segment Distribution by Age', fontsize=16)
    plt.xlabel('Number of Customers')
    plt.ylabel('Age Group')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_segment_distribution_by_age.png'))
    plt.close()
    print("나이대별 고객 세그먼트 분포 차트를 저장했습니다.")

    # --- Analysis by Customer Income ---
    plt.figure(figsize=(12, 8))
    sns.countplot(y='CustomerIncome', hue='Customer_Segment', data=df_merged, palette='plasma', hue_order=segment_order)
    plt.title('Customer Segment Distribution by Income', fontsize=16)
    plt.xlabel('Number of Customers')
    plt.ylabel('Income Group')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_segment_distribution_by_income.png'))
    plt.close()
    print("소득 수준별 고객 세그먼트 분포 차트를 저장했습니다.")

    # --- Analysis by Marital Status ---
    plt.figure(figsize=(10, 6))
    sns.countplot(x='MARITAL_STATUS_CODE', hue='Customer_Segment', data=df_merged, palette='magma', hue_order=segment_order)
    plt.title('Customer Segment Distribution by Marital Status', fontsize=16)
    plt.xlabel('Marital Status Code')
    plt.ylabel('Number of Customers')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_segment_distribution_by_marital_status.png'))
    plt.close()
    print("결혼 상태별 고객 세그먼트 분포 차트를 저장했습니다.")
    
    # --- Analysis by Household Composition ---
    plt.figure(figsize=(14, 8))
    sns.countplot(y='HH_COMP_DESC', hue='Customer_Segment', data=df_merged, palette='cividis', hue_order=segment_order)
    plt.title('Customer Segment Distribution by Household Composition', fontsize=16)
    plt.xlabel('Number of Customers')
    plt.ylabel('Household Composition')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'dunnhumby_segment_distribution_by_hh_comp.png'))
    plt.close()
    print("가구 구성별 고객 세그먼트 분포 차트를 저장했습니다.")

    print("\nDunnhumby 인구통계학적 특성 분석 완료.")

except FileNotFoundError as e:
    print(f"오류: 파일을 찾을 수 없습니다: {e.filename}. 경로를 확인해주세요.")
except Exception as e:
    print(f"분석 중 오류가 발생했습니다: {e}")
