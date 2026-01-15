
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import os
import random

# 설정
integrated_data_path = 'dunnhumby_integrated_data.csv'
rfm_segments_path = 'dunnhumby_rfm_segments.csv'
base_output_dir = 'final_reports/mba'
if not os.path.exists(base_output_dir):
    os.makedirs(base_output_dir)

print("--- Dunnhumby 고도화된 MBA 분석 (장바구니 및 교차 구매 분석) 시작 ---")

try:
    # 1. 데이터 로드
    df = pd.read_csv(integrated_data_path)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # RFM 세그먼트 정보 로드 (있는 경우)
    has_segments = os.path.exists(rfm_segments_path)
    if has_segments:
        rfm_df = pd.read_csv(rfm_segments_path)
        # CustomerID 기준으로 매핑
        df = df.merge(rfm_df[['CustomerID', 'Customer_Segment']], on='CustomerID', how='left')
        print(f"고객 세그먼트 정보를 로드했습니다. (Segment 종류: {df['Customer_Segment'].unique()})")

    # 2. 전처리
    # 유효한 상품명만 필터링 및 정제
    df_filtered = df[df['ProductName'].notna() & (df['ProductName'] != 'Unknown Product')].copy()
    df_filtered['ProductName'] = df_filtered['ProductName'].astype(str).str.strip()
    
    # 상위 50개 상품으로 분석 범위 설정 (메모리 제약 고려 및 TS 분석과 일관성 유지)
    top_n = 50
    top_products = df_filtered['ProductName'].value_counts().nlargest(top_n).index
    df_mba = df_filtered[df_filtered['ProductName'].isin(top_products)].copy()
    
    def get_baskets(data):
        # 중복 상품 제거 (한 장바구니에 같은 상품이 여러 개일 수 있음)
        return data.groupby('BASKET_ID')['ProductName'].apply(lambda x: sorted(list(set(x)))).values.tolist()

    # --- 3. 데이터 안정성 분석 (Stability Analysis) 고도화 (제안서 2.1 반영) ---
    print("\n[안정성 분석] 데이터를 5개 그룹으로 분할하여 규칙의 변동 계수(CV)를 측정합니다...")
    
    all_basket_ids = df_mba['BASKET_ID'].unique()
    num_splits = 5
    random.shuffle(all_basket_ids)
    basket_groups = np.array_split(all_basket_ids, num_splits)
    
    def get_top_rules(data, limit=5, min_support=0.002):
        baskets = get_baskets(data)
        if not baskets: return pd.DataFrame()
        # 샘플링
        if len(baskets) > 20000:
            baskets = random.sample(baskets, 20000)
        te = TransactionEncoder()
        te_ary = te.fit(baskets).transform(baskets)
        t_df = pd.DataFrame(te_ary, columns=te.columns_)
        f_itemsets = apriori(t_df, min_support=min_support, use_colnames=True)
        if f_itemsets.empty: return pd.DataFrame()
        rules = association_rules(f_itemsets, metric="lift", min_threshold=1.1)
        return rules.sort_values('lift', ascending=False).head(limit)

    group_rules = []
    for g_idx, g_ids in enumerate(basket_groups):
        print(f"  > 그룹 {g_idx+1} 규칙 추출 중...")
        subset_df = df_mba[df_mba['BASKET_ID'].isin(g_ids)]
        baskets = get_baskets(subset_df)
        te = TransactionEncoder()
        te_ary = te.fit(baskets).transform(baskets)
        t_df = pd.DataFrame(te_ary, columns=te.columns_)
        f_itemsets = apriori(t_df, min_support=0.002, use_colnames=True)
        if not f_itemsets.empty:
            rules = association_rules(f_itemsets, metric="lift", min_threshold=1.0)
            rules['group'] = g_idx
            group_rules.append(rules)
            
    if group_rules:
        all_group_rules = pd.concat(group_rules)
        # 규칙 식별자 생성
        all_group_rules['rule_id'] = all_group_rules.apply(lambda x: f"{sorted(list(x['antecedents']))} -> {sorted(list(x['consequents']))}", axis=1)
        
        # 규칙별 지표 변동성 계산
        rule_stats = all_group_rules.groupby('rule_id').agg({
            'lift': ['mean', 'std', 'count'],
            'confidence': ['mean', 'std']
        })
        rule_stats.columns = ['lift_mean', 'lift_std', 'rule_count', 'conf_mean', 'conf_std']
        
        # 변동 계수 (CV = std / mean) 계산
        rule_stats['lift_cv'] = rule_stats['lift_std'] / rule_stats['lift_mean']
        rule_stats['is_stable'] = (rule_stats['rule_count'] >= 3) & (rule_stats['lift_cv'].fillna(0) < 0.2)
        
        stability_score = (rule_stats['is_stable'].sum() / len(rule_stats)) * 100
        avg_lift_cv = rule_stats['lift_cv'].mean()
    else:
        stability_score = 0
        avg_lift_cv = 1.0
    
    print(f"  > 규칙 안정성 지수(Stable Rules Ratio): {stability_score:.2f}%")
    print(f"  > 평균 리프트 변동 계수(Avg Lift CV): {avg_lift_cv:.4f}")

    # --- 4. 시간적 분석 (Temporal Analysis) --- (제안서 2.3 반영)
    print("\n[시간적 분석] 분기별(Quarterly) 구매 패턴 변화를 추적합니다...")
    df_mba['Quarter'] = df_mba['OrderDate'].dt.to_period('Q')
    quarters = sorted(df_mba['Quarter'].unique())
    temporal_results = {}
    for q in quarters:
        print(f"  > {q} 분기 분석 중...")
        q_data = df_mba[df_mba['Quarter'] == q]
        temporal_results[str(q)] = get_top_rules(q_data, limit=3)
    
    # --- 5. 세그먼트별 분석 (Segmented MBA) (제안서 2.2 반영) ---
    # RFM_analysis_report.pdf 의 세그먼트 명칭 반영
    print("\n[세그먼트 분석] RFM 기반 고객 등급별 최적 번들을 도출합니다...")
    # 실제 RFM 데이터가 없을 경우 가상 세그먼트 부여 (검증용)
    if not has_segments:
         print("  > RFM 세그먼트 파일이 없어 임시 세그먼트를 할당합니다.")
         customers = df_mba['CustomerID'].unique()
         temp_rfm = pd.DataFrame({
             'CustomerID': customers,
             'Customer_Segment': random.choices(['Champions', 'Loyal Customers', 'At Risk', 'Hibernating', 'Potential Loyalists'], k=len(customers))
         })
         df_mba = df_mba.merge(temp_rfm, on='CustomerID', how='left')
         has_segments = True

    segment_bundles = {}
    target_segments = ['Champions', 'Loyal Customers', 'At Risk', 'Potential Loyalists']
    for seg in target_segments:
        seg_data = df_mba[df_mba['Customer_Segment'] == seg]
        if not seg_data.empty:
            print(f"  > '{seg}' 세그먼트 분석 중...")
            segment_bundles[seg] = get_top_rules(seg_data, limit=5)

    # --- 6. 전체 연관 분석 및 결과 저장 ---
    print("\n[전체 분석] 최종 고도화 규칙을 생성합니다...")
    full_baskets = get_baskets(df_mba)
    if len(full_baskets) > 50000:
        full_baskets = random.sample(full_baskets, 50000)
        
    te = TransactionEncoder()
    te_ary = te.fit(full_baskets).transform(full_baskets)
    transactions_df = pd.DataFrame(te_ary, columns=te.columns_)
    frequent_itemsets = apriori(transactions_df, min_support=0.001, use_colnames=True)
    final_rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.1)
    
    # 안정성 지표 결합
    final_rules['rule_id'] = final_rules.apply(lambda x: f"{sorted(list(x['antecedents']))} -> {sorted(list(x['consequents']))}", axis=1)
    if group_rules:
        final_rules = final_rules.merge(rule_stats[['lift_cv', 'is_stable']], on='rule_id', how='left')
    
    final_rules = final_rules.sort_values(['is_stable', 'lift'], ascending=False)
    
    # 규칙 가독성 개선
    final_rules['antecedents_str'] = final_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    final_rules['consequents_str'] = final_rules['consequents'].apply(lambda x: ', '.join(list(x)))
    
    # 결과 저장
    final_rules.to_csv(os.path.join(base_output_dir, 'dunnhumby_high_stability_mba_rules.csv'), index=False)
    
    # 시각화 데이터용 요약 파일
    with open(os.path.join(base_output_dir, 'mba_advanced_metrics.txt'), 'w', encoding='utf-8') as f:
        f.write(f"Stability Score: {stability_score:.2f}%\n")
        f.write(f"Average Lift CV: {avg_lift_cv:.4f}\n")
        f.write(f"Total Rules: {len(final_rules)}\n")
        f.write("\n[Temporal Samples - Q4 2021]\n")
        if '2021Q4' in temporal_results:
            f.write(temporal_results['2021Q4'].to_string())
        f.write("\n\n[Segment Bundles - Champions]\n")
        if 'Champions' in segment_bundles:
            f.write(segment_bundles['Champions'].to_string())

    print(f"\n--- MBA 분석 완료. 결과 저장 위치: {base_output_dir} ---")

except Exception as e:
    print(f"MBA 분석 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
