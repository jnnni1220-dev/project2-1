
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# Load the dataset
try:
    df = pd.read_csv('Amazon.csv')
    
    print("--- 4단계: 교차 구매 분석 (장바구니 분석) ---")

    # --- Data Preparation for Market Basket Analysis ---

    # Select top 50 most frequent products to reduce dimensionality
    top_n = 50
    top_products = df['ProductName'].value_counts().nlargest(top_n).index
    df_filtered = df[df['ProductName'].isin(top_products)]
    print(f"\n분석 대상을 판매량 기준 상위 {top_n}개 상품으로 제한합니다.")

    # Create transaction baskets
    baskets = df_filtered.groupby('OrderID')['ProductName'].apply(list).values.tolist()
    print("주문별로 상품 묶음(장바구니)을 생성했습니다.")

    # One-hot encode the transaction data
    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    transactions_df = pd.DataFrame(te_ary, columns=te.columns_)
    print("데이터를 분석 가능한 형태로 변환했습니다 (One-hot encoding).")

    # --- Apriori Algorithm ---
    # Find frequent itemsets with a minimum support of 1%
    min_support_threshold = 0.01
    frequent_itemsets = apriori(transactions_df, min_support=min_support_threshold, use_colnames=True)
    print(f"\n최소 지지도({min_support_threshold*100}%) 기준, 빈번하게 발생하는 상품 조합을 찾았습니다.")

    # --- Association Rules ---
    # Generate association rules with a minimum confidence of 5%
    min_confidence_threshold = 0.05
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence_threshold)
    
    # Filter and sort the rules for better insights (high lift and confidence) 
    rules_filtered = rules[rules['lift'] >= 1].sort_values(['lift', 'confidence'], ascending=[False, False])
    print(f"최소 신뢰도({min_confidence_threshold*100}%)와 향상도(1 이상) 기준으로 연관 규칙을 생성했습니다.")

    print("\n\n--- 상위 10개 연관 규칙 (A를 사면 B를 산다) ---")
    # Displaying the result in a more readable format
    rules_to_show = rules_filtered[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10)
    rules_to_show['antecedents'] = rules_to_show['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules_to_show['consequents'] = rules_to_show['consequents'].apply(lambda x: ', '.join(list(x)))
    print(rules_to_show.to_string())

    print("\n\n교차 구매 분석이 완료되었습니다.")
    print("결과 해석: 'A를 구매한 고객'이 'B를 구매할 확률'은 '전체 고객이 B를 구매할 확률'보다 'lift' 배 높습니다.")

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
