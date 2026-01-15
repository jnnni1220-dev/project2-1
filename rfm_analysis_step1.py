
import pandas as pd
import datetime as dt

# Load the dataset
try:
    df = pd.read_csv('Amazon.csv', dtype={'CustomerID': str})

    print("--- 2단계: RFM 분석 및 고객 세분화 ---")

    # --- Data Preparation for RFM ---
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Set a snapshot date for Recency calculation (one day after the last transaction)
    snapshot_date = df['OrderDate'].max() + dt.timedelta(days=1)
    print(f"\n분석 기준일(Snapshot Date): {snapshot_date.strftime('%Y-%m-%d')}")

    # Calculate R, F, M values
    rfm_df = df.groupby('CustomerID').agg({
        'OrderDate': lambda x: (snapshot_date - x.max()).days,
        'OrderID': 'count',
        'TotalAmount': 'sum'
    })

    # Rename columns
    rfm_df.rename(columns={'OrderDate': 'Recency',
                           'OrderID': 'Frequency',
                           'TotalAmount': 'Monetary'}, inplace=True)
    
    print("\n고객별 R, F, M 값을 계산했습니다.")

    # --- RFM Segmentation ---
    # Create R, F, M scores based on quartiles
    r_labels = range(4, 0, -1) # Lower Recency is better
    f_labels = range(1, 5)    # Higher Frequency is better
    m_labels = range(1, 5)    # Higher Monetary is better

    rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=4, labels=r_labels, duplicates='drop').astype(int)
    rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'], q=4, labels=f_labels, duplicates='drop').astype(int)
    rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=4, labels=m_labels, duplicates='drop').astype(int)
    
    # Create RFM Segment and Score
    def join_rfm(x): return str(x['R_Score']) + str(x['F_Score']) + str(x['M_Score'])
    rfm_df['RFM_Segment'] = rfm_df.apply(join_rfm, axis=1)
    rfm_df['RFM_Score'] = rfm_df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    # Define customer segments based on RFM scores
    def segment_customer(df):
        if df['RFM_Score'] >= 9:
            return 'VIP'
        elif (df['RFM_Score'] >= 6) and (df['RFM_Score'] < 9):
            return 'Loyal Customers'
        elif (df['RFM_Score'] >= 4) and (df['RFM_Score'] < 6):
            return 'Potential Loyalists'
        else:
            return 'At-Risk Customers'

    rfm_df['Customer_Segment'] = rfm_df.apply(segment_customer, axis=1)
    
    print("\nRFM 점수를 기반으로 고객을 세분화했습니다.")
    print("세그먼트: VIP, Loyal Customers, Potential Loyalists, At-Risk Customers")

    # Save the result to a CSV file
    rfm_df.to_csv('rfm_segments.csv')
    print("\n분석 결과를 'rfm_segments.csv' 파일로 저장했습니다.")
    
    print("\n--- RFM 분석 결과 (상위 5개) ---")
    print(rfm_df.head())

    print("\nRFM 분석 및 세분화가 완료되었습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
