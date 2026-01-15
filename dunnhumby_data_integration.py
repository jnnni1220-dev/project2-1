import pandas as pd
import numpy as np
import os

# Define file paths
archive_path = 'Dunnhumby/archive'
transaction_data_path = os.path.join(archive_path, 'transaction_data.csv')
product_path = os.path.join(archive_path, 'product.csv')
hh_demographic_path = os.path.join(archive_path, 'hh_demographic.csv')

# --- Phase 1: Data Understanding and Integration ---
print("--- 1단계: Dunnhumby 데이터 통합 시작 (수정) ---")

try:
    # 1. Load Core Tables
    print(f"'{transaction_data_path}' 로드 중...")
    transactions = pd.read_csv(transaction_data_path)
    print(f"'{transaction_data_path}' 로드 완료. 행: {transactions.shape[0]}, 열: {transactions.shape[1]}")

    print(f"'{product_path}' 로드 중...")
    products = pd.read_csv(product_path)
    print(f"'{product_path}' 로드 완료. 행: {products.shape[0]}, 열: {products.shape[1]}")

    print(f"'{hh_demographic_path}' 로드 중...")
    demographics = pd.read_csv(hh_demographic_path)
    print(f"'{hh_demographic_path}' 로드 완료. 행: {demographics.shape[0]}, 열: {demographics.shape[1]}")

    # 2. Merge `product.csv` with `transaction_data.csv`
    print("\n상품 데이터와 거래 데이터를 병합 중...")
    df_merged = pd.merge(transactions, products, on='PRODUCT_ID', how='left')
    print(f"상품 데이터 병합 완료. 행: {df_merged.shape[0]}, 열: {df_merged.shape[1]}")

    # 3. Merge `hh_demographic.csv` with the result
    print("\n고객 인구통계 데이터와 병합 중...")
    df_merged = pd.merge(df_merged, demographics, on='household_key', how='left')
    print(f"고객 인구통계 데이터 병합 완료. 행: {df_merged.shape[0]}, 열: {df_merged.shape[1]}")

    # 4. Process `DAY` column
    print("\n'DAY' 컬럼을 'OrderDate' (날짜) 형식으로 변환 중...")
    min_day = df_merged['DAY'].min()
    base_date = pd.to_datetime('2020-01-01') - pd.Timedelta(days=min_day - 1)
    df_merged['OrderDate'] = base_date + pd.to_timedelta(df_merged['DAY'] - 1, unit='D')
    print("'DAY' 컬럼 변환 완료.")

    # 5. Clean up / Select relevant columns
    print("\n분석에 필요한 컬럼 선택 및 이름 조정 중...")

    # First, create 'ProductName' from product attributes BEFORE selection
    df_merged['ProductName_combined'] = df_merged['SUB_COMMODITY_DESC'].fillna(df_merged['COMMODITY_DESC'])
    # Handle cases where both are NaN, though unlikely with fillna(COMMODITY_DESC)
    df_merged['ProductName_combined'] = df_merged['ProductName_combined'].fillna('Unknown Product')


    df_analysis = df_merged.rename(columns={
        'household_key': 'CustomerID',
        'PRODUCT_ID': 'ProductID',
        'SALES_VALUE': 'TotalAmount',
        'QUANTITY': 'Quantity',
        'RETAIL_DISC': 'RetailDiscount',
        'COUPON_DISC': 'CouponDiscount',
        'COUPON_MATCH_DISC': 'CouponMatchDiscount',
        'WEEK_NO': 'WeekNumber',
        'DEPARTMENT': 'Category',
        'BRAND': 'Brand',
        'AGE_DESC': 'CustomerAge',
        'INCOME_DESC': 'CustomerIncome'
    })

    # Calculate combined discount for each transaction line item
    # RetailDiscount is already negative for discounts in the raw data
    df_analysis['CombinedDiscount'] = df_analysis['RetailDiscount'].fillna(0) + \
                                     df_analysis['CouponDiscount'].fillna(0) + \
                                     df_analysis['CouponMatchDiscount'].fillna(0)

    # Convert combined discount to absolute positive value if it represents total discount value
    df_analysis['Discount'] = df_analysis['CombinedDiscount'].abs() # Use absolute value for consistency with Amazon.csv discount interpretation

    # Select columns similar to Amazon.csv + new demographic/product info
    df_analysis = df_analysis[[
        'CustomerID', 'OrderDate', 'ProductID', 'ProductName_combined',
        'Category', 'Brand', 'Quantity', 'TotalAmount',
        'RetailDiscount', 'CouponDiscount', 'CouponMatchDiscount', 'Discount', # Individual + Combined
        'CustomerAge', 'CustomerIncome', 'MARITAL_STATUS_CODE', 'HOMEOWNER_DESC',
        'HH_COMP_DESC', 'HOUSEHOLD_SIZE_DESC', 'KID_CATEGORY_DESC',
        'WeekNumber', 'BASKET_ID' # Added BASKET_ID for RFM Frequency calculation
    ]]

    # Rename ProductName_combined to ProductName for consistency with Amazon.csv structure
    df_analysis = df_analysis.rename(columns={'ProductName_combined': 'ProductName'})


    print("통합 분석 데이터셋 생성 완료.")
    print(f"최종 데이터셋 형태: {df_analysis.shape}")
    print("\n--- 최종 통합 데이터셋 샘플 (상위 5개) ---")
    print(df_analysis.head())

    # Save the integrated dataset for future use
    df_analysis.to_csv('dunnhumby_integrated_data.csv', index=False)
    print("\n통합 데이터셋을 'dunnhumby_integrated_data.csv'로 저장했습니다.")

    print("\n--- Dunnhumby 데이터 통합 완료. 다음 단계로 진행합니다. ---")

except FileNotFoundError as e:
    print(f"오류: 파일을 찾을 수 없습니다: {e.filename}. 경로를 확인해주세요.")
except pd.errors.EmptyDataError:
    print("오류: 로드하려는 파일이 비어 있습니다.")
except Exception as e:
    print(f"데이터 통합 중 오류가 발생했습니다: {e}")