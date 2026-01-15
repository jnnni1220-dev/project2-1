
import pandas as pd
import datetime as dt
import os

# Define integrated data path
integrated_data_path = 'dunnhumby_integrated_data.csv'

# --- Phase 2: Analysis Execution - RFM Analysis ---
print("--- Dunnhumby RFM 분석: R/F/M 값 계산 및 고객 세분화 ---")

try:
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Set a snapshot date for Recency calculation (one day after the last transaction)
    snapshot_date = df['OrderDate'].max() + dt.timedelta(days=1)
    print(f"\n분석 기준일(Snapshot Date): {snapshot_date.strftime('%Y-%m-%d')}")

    # Calculate R, F, M values
    # Frequency: Use BASKET_ID for distinct transactions per customer
    rfm_df = df.groupby('CustomerID').agg(
        Recency=('OrderDate', lambda x: (snapshot_date - x.max()).days),
        Frequency=('BASKET_ID', 'nunique'), # Count distinct baskets for frequency
        Monetary=('TotalAmount', 'sum')
    )
    
    print("\n고객별 R, F, M 값을 계산했습니다.")

    # --- RFM Segmentation ---
    # Create R, F, M scores based on quartiles (using rank for robustness)
    r_labels = range(4, 0, -1) # Lower Recency is better
    f_labels = range(1, 5)    # Higher Frequency is better
    m_labels = range(1, 5)    # Higher Monetary is better

    rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=4, labels=r_labels, duplicates='drop').astype(int)
    rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), q=4, labels=f_labels).astype(int)
    rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), q=4, labels=m_labels).astype(int)
    
    print("\nRFM 점수(R, F, M Score)를 계산했습니다.")

    # Create RFM Segment and Score
    def join_rfm(x): return str(x['R_Score']) + str(x['F_Score']) + str(x['M_Score'])
    rfm_df['RFM_Segment_Code'] = rfm_df.apply(join_rfm, axis=1)
    rfm_df['RFM_Score'] = rfm_df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    # Define customer segments based on RFM scores (adjusted for potentially different distribution)
    # Using the same logic as Amazon project for consistency
    def segment_customer(row):
        if row['RFM_Score'] >= 11:
            return 'VIP'
        elif (row['RFM_Score'] >= 8) and (row['RFM_Score'] < 11):
            return 'Loyal Customers'
        elif (row['RFM_Score'] >= 5) and (row['RFM_Score'] < 8):
            return 'Potential Loyalists'
        elif (row['RFM_Score'] >= 3) and (row['RFM_Score'] < 5):
            return 'At-Risk Customers'
        else:
            return 'Lost Customers'

    rfm_df['Customer_Segment'] = rfm_df.apply(segment_customer, axis=1)
    
    print("\nRFM 점수를 기반으로 고객을 세분화했습니다.")
    print("세그먼트: VIP, Loyal Customers, Potential Loyalists, At-Risk Customers, Lost Customers")

    # Save the result to a CSV file
    rfm_df.to_csv('dunnhumby_rfm_segments.csv')
    print("\n분석 결과를 'dunnhumby_rfm_segments.csv' 파일로 저장했습니다.")
    
    print("\n--- Dunnhumby RFM 분석 결과 (상위 5개) ---")
    print(rfm_df.head())

    print("\nDunnhumby RFM 분석 및 세분화가 완료되었습니다.")

except FileNotFoundError:
    print(f"오류: '{integrated_data_path}' 파일을 찾을 수 없습니다. 데이터 통합이 먼저 완료되어야 합니다.")
except Exception as e:
    print(f"Dunnhumby RFM 분석 중 오류가 발생했습니다: {e}")
