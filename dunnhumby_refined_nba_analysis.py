import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 깨짐 해결을 위한 폰트 설정 (Windows 기준 Malgun Gothic)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 설정
integrated_data_path = 'dunnhumby_integrated_data.csv'
demographic_path = 'Dunnhumby/archive/hh_demographic.csv' # 원천 데이터 연계
base_output_dir = 'final_reports/nba'
if not os.path.exists(base_output_dir):
    os.makedirs(base_output_dir)

print("--- Dunnhumby 고도화된 NBA 추천 엔진 (Hybrid & Explainable) 시작 ---")

try:
    # 1. 데이터 로드 및 통합 (제안서 4.2 데이터 원천 명시 반영)
    cols = ['CustomerID', 'ProductID', 'ProductName', 'Category', 'TotalAmount']
    df = pd.read_csv(integrated_data_path, usecols=cols)
    demo_df = pd.read_csv(demographic_path)
    
    # 상위 500개 상품 위주 분석
    top_500_products = df['ProductID'].value_counts().nlargest(500).index
    df_nba = df[df['ProductID'].isin(top_500_products)].copy()
    
    # 2. CF 및 CB 유사도 행렬 생성
    item_info = df_nba[['ProductID', 'ProductName', 'Category']].drop_duplicates('ProductID').set_index('ProductID')
    user_item_matrix = df_nba.pivot_table(index='CustomerID', columns='ProductID', values='TotalAmount', aggfunc='sum').fillna(0)
    
    # Item-Item CF
    print("[CF] 아이템 유사도 계산 중...")
    item_similarity = cosine_similarity(user_item_matrix.T)
    item_sim_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)
    
    # Content-Based (Product Name & Category)
    print("[CBF] 컨텐츠 유사도 계산 중...")
    item_info['features'] = item_info['ProductName'] + " " + item_info['Category'].fillna('')
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(item_info['features'])
    content_similarity = cosine_similarity(tfidf_matrix)
    content_sim_df = pd.DataFrame(content_similarity, index=item_info.index, columns=item_info.index)

    # 3. 인구통계학적 그룹 인기 상품 (Cold Start 및 CBF 강화용) - 제안서 3.1 반영
    print("[DEMO] 인구통계 그룹별 인기 상품 분석 중...")
    df_demo_all = df_nba.merge(demo_df[['household_key', 'INCOME_DESC', 'AGE_DESC']], left_on='CustomerID', right_on='household_key', how='inner')
    income_popular = df_demo_all.groupby(['INCOME_DESC', 'ProductID'])['TotalAmount'].sum().reset_index()
    
    # 4. 고도화된 추천 로직 (제안서 3.3 개인화 근거 명시)
    def get_explainable_recommendations(customer_id, top_k=5):
        # 1. 기존 구매 이력 확인
        if customer_id in user_item_matrix.index:
            user_history = user_item_matrix.loc[customer_id]
            purchased_items = user_history[user_history > 0].index.tolist()
            
            # Hybrid Score (CF 0.6 + CB 0.4)
            scores = pd.Series(0.0, index=item_sim_df.index)
            for item in purchased_items:
                scores += item_sim_df[item] * 0.6
                if item in content_sim_df.index:
                    scores += content_sim_df[item] * 0.4
            
            scores = scores.drop(purchased_items, errors='ignore')
            top_recs = scores.sort_values(ascending=False).head(top_k)
            
            results = []
            for pid, score in top_recs.items():
                p_name = item_info.loc[pid, 'ProductName']
                # 근거 생성 (Explainability)
                reason = f"귀하가 과거에 구매하신 '{item_info.loc[purchased_items[0], 'ProductName']}' 품목과 구매 연관성 및 상품 특성이 매우 유사합니다."
                results.append({'ProductID': pid, 'ProductName': p_name, 'Score': score, 'Reason': reason, 'Type': 'Hybrid'})
            return results
        
        # 2. 신규 고객 (Cold Start) 대응 - 소득 수준 기반 추천
        else:
            cust_demo = demo_df[demo_df['household_key'] == customer_id]
            if not cust_demo.empty:
                income = cust_demo.iloc[0]['INCOME_DESC']
                pop_items = income_popular[income_popular['INCOME_DESC'] == income].sort_values('TotalAmount', ascending=False).head(top_k)
                results = []
                for _, row in pop_items.iterrows():
                    pid = row['ProductID']
                    p_name = item_info.loc[pid, 'ProductName'] if pid in item_info.index else "Unknown"
                    reason = f"귀하와 유사한 소득 수준({income})의 가구에서 가장 선호하는 베스트셀러 상품입니다."
                    results.append({'ProductID': pid, 'ProductName': p_name, 'Score': 1.0, 'Reason': reason, 'Type': 'Demographic'})
                return results
            
            return []

    # 5. 다양성(Diversity) 및 의외성(Serendipity) 지표 산출 - 제안서 3.2 반영
    print("[METRICS] 추천의 질적 지표 분석 중...")
    sample_customers = list(user_item_matrix.index[:100]) + list(demo_df['household_key'].unique()[:20])
    all_recs = []
    for cid in sample_customers:
        recs = get_explainable_recommendations(cid)
        for r in recs:
            all_recs.append({'CustomerID': cid, **r})
            
    rec_results_df = pd.DataFrame(all_recs)
    
    # 다양성: 추천된 상품들의 카테고리 고유 개수 비율
    merged_recs = rec_results_df.merge(item_info[['Category']], on='ProductID', how='left')
    cat_diversity = merged_recs['Category'].nunique() / len(item_info['Category'].unique()) * 100
    
    # 의외성 (간이 지표): 하이브리드 추천 중 CB 유사도가 낮은데도 선택된 비율 (새로운 발견)
    serendipity_count = len(rec_results_df[(rec_results_df['Type'] == 'Hybrid') & (rec_results_df['Score'] < 0.5)]) # 임계치
    serendipity_score = (serendipity_count / len(rec_results_df)) * 100 if len(rec_results_df) > 0 else 0

    # 6. 결과 저장
    rec_results_df.to_csv(os.path.join(base_output_dir, 'dunnhumby_explainable_nba_results.csv'), index=False, encoding='utf-8-sig')
    
    with open(os.path.join(base_output_dir, 'nba_advanced_metrics.txt'), 'w', encoding='utf-8') as f:
        f.write(f"추천 다양성 (Category Diversity): {cat_diversity:.2f}%\n")
        f.write(f"추천 의외성 (Serendipity Score): {serendipity_score:.2f}%\n")
        f.write(f"분석 고객 수: {len(sample_customers)}\n")
        f.write(f"엔진 구성: Hybrid CF(0.6) + CBF(0.4) + Demographic Popularity\n")

    print(f"--- NBA 고도화 분석 완료. 결과 파일 생성됨: {base_output_dir} ---")

except Exception as e:
    print(f"NBA 분석 오류: {e}")
    import traceback
    traceback.print_exc()
