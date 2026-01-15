
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import os

# Define integrated data path
integrated_data_path = 'dunnhumby_integrated_data.csv'

# --- Phase 2: Analysis Execution - Market Basket Analysis ---
print("--- Dunnhumby 교차 구매 분석 (장바구니 분석) ---")

try:
    df = pd.read_csv(integrated_data_path)
    
    # --- Data Preparation for Market Basket Analysis ---
    
    # For Dunnhumby, 'BASKET_ID' is the transaction identifier, 'ProductName' is the item
    # Need to handle potential ProductName (from SUB_COMMODITY_DESC/COMMODITY_DESC) as it might be 'Unknown Product'

    # Filter out 'Unknown Product' if it was assigned due to both being NaN
    df_filtered_products = df[df['ProductName'] != 'Unknown Product']

    # Select top 50 most frequent products to reduce dimensionality
    top_n_products = 50
    # Use value_counts on filtered products
    top_products_list = df_filtered_products['ProductName'].value_counts().nlargest(top_n_products).index

    # Filter the DataFrame to only include transactions with these top N products
    df_mba = df_filtered_products[df_filtered_products['ProductName'].isin(top_products_list)]
    print(f"\n분석 대상을 판매량 기준 상위 {top_n_products}개 상품으로 제한합니다.")

    # Create transaction baskets: group by BASKET_ID, collect ProductNames
    # Use 'BASKET_ID' as the transaction identifier from the integrated data
    baskets = df_mba.groupby('BASKET_ID')['ProductName'].apply(list).values.tolist()
    print(f"총 {len(baskets)}개의 장바구니 데이터를 생성했습니다.")

    # Sample a subset of baskets to reduce memory footprint
    sample_fraction = 0.1 # Sample 10% of the baskets
    if len(baskets) > 10000: # Only sample if there are many baskets
        import random
        random.seed(42) # For reproducibility
        baskets = random.sample(baskets, int(len(baskets) * sample_fraction))
        print(f"\n메모리 최적화를 위해 장바구니 데이터를 {sample_fraction*100:.0f}% 샘플링했습니다. 샘플링된 장바구니 수: {len(baskets)}")

    # One-hot encode the transaction data
    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    transactions_df = pd.DataFrame(te_ary, columns=te.columns_)
    print("데이터를 분석 가능한 형태로 변환했습니다 (One-hot encoding).")


    # --- Apriori Algorithm ---
    # Find frequent itemsets with a minimum support of 0.1% for this larger dataset
    # Given the large number of transactions, a very low support is still significant
    min_support_threshold = 0.001 
    frequent_itemsets = apriori(transactions_df, min_support=min_support_threshold, use_colnames=True)
    print(f"\n최소 지지도({min_support_threshold*100:.2f}%) 기준, 빈번하게 발생하는 상품 조합을 찾았습니다.")

    # --- Association Rules ---
    # Generate association rules with a minimum confidence of 5%
    min_confidence_threshold = 0.05
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence_threshold)
    
    # Filter and sort the rules for better insights (high lift and confidence)
    rules_filtered = rules[rules['lift'] >= 1].sort_values(['lift', 'confidence'], ascending=[False, False])

    print(f"최소 신뢰도({min_confidence_threshold*100:.0f}%)와 향상도(1 이상) 기준으로 연관 규칙을 생성했습니다.")
    print(f"총 {len(rules_filtered)}개의 연관 규칙을 찾았습니다.")

    print("\n\n--- 상위 10개 연관 규칙 (A를 사면 B를 산다) ---")
    # Displaying the result in a more readable format
    rules_to_show = rules_filtered[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10)
    rules_to_show['antecedents'] = rules_to_show['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules_to_show['consequents'] = rules_to_show['consequents'].apply(lambda x: ', '.join(list(x)))
    print(rules_to_show.to_string())

    print("\n\nDunnhumby 교차 구매 분석 완료.")
    print("결과 해석: 'A를 구매한 고객'이 'B를 구매할 확률'은 '전체 고객이 B를 구매할 확률'보다 'lift' 배 높습니다.")

except FileNotFoundError:
    print(f"오류: '{integrated_data_path}' 파일을 찾을 수 없습니다. 데이터 통합이 먼저 완료되어야 합니다.")
except Exception as e:
    print(f"Dunnhumby 교차 구매 분석 중 오류가 발생했습니다: {e}")
