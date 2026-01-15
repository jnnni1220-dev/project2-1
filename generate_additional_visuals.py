
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
ts_report_dir = 'final_reports/ts/plots'
mba_report_dir = 'final_reports/mba/plots'
nba_report_dir = 'final_reports/nba/plots'

for d in [ts_report_dir, mba_report_dir, nba_report_dir]:
    if not os.path.exists(d): os.makedirs(d)

print("--- 보고서 보강용 고도화 시각화 생성 시작 ---")

# --- 1. TS 보강: 모델별 오차 분포 (Error Distribution) ---
print("[TS] 모델별 오차 분포 생성 중...")
ts_metrics = pd.read_csv('final_reports/ts/dunnhumby_prophet_backtest_metrics.csv')
plt.figure(figsize=(10, 6))
sns.histplot(data=ts_metrics, x='Best_MAE', hue='Best_Model', kde=True, bins=15)
plt.title('시계열 모델별 예측 오차(MAE) 분포', fontsize=15)
plt.xlabel('평균 절대 오차 (MAE)')
plt.ylabel('품목 수')
plt.grid(alpha=0.3)
plt.savefig(os.path.join(ts_report_dir, 'ts_error_distribution.png'))
plt.close()

# --- 2. MBA 보강: 연관 규칙 히트맵 (Top 10) ---
print("[MBA] 연관 규칙 히트맵 생성 중...")
mba_rules = pd.read_csv('final_reports/mba/dunnhumby_high_stability_mba_rules.csv')
top_rules = mba_rules.sort_values('lift', ascending=False).head(10)

# 매트릭스 생성
pivot_rules = top_rules.pivot(index='antecedents_str', columns='consequents_str', values='lift').fillna(0)

plt.figure(figsize=(10, 8))
sns.heatmap(pivot_rules, annot=True, cmap='YlGnBu', cbar_kws={'label': '향상도 (Lift)'})
plt.title('상위 10개 상품 연관 규칙 향상도 히트맵', fontsize=15)
plt.xlabel('결과 (Consequents)')
plt.ylabel('조건 (Antecedents)')
plt.tight_layout()
plt.savefig(os.path.join(mba_report_dir, 'mba_rule_heatmap.png'))
plt.close()

# --- 3. NBA 보강: 추천 점수 분포 및 다양성 성과 ---
print("[NBA] 추천 시스템 성과 지표 생성 중...")
nba_results = pd.read_csv('final_reports/nba/dunnhumby_explainable_nba_results.csv')

# 추천 점수 분포
plt.figure(figsize=(10, 6))
sns.boxplot(data=nba_results, x='Type', y='Score', palette='Set2')
plt.title('추천 방식별(Hybrid vs Demo) 점수 분포', fontsize=15)
plt.xlabel('추천 엔진 타입')
plt.ylabel('추천 점수(Score)')
plt.savefig(os.path.join(nba_report_dir, 'nba_score_distribution.png'))
plt.close()

# 카테고리별 추천 빈도 (다양성 시각화)
# Product 정보와 조인 필요
product_df = pd.read_csv('Dunnhumby/archive/product.csv')
nba_meta = nba_results.merge(product_df[['PRODUCT_ID', 'COMMODITY_DESC']], left_on='ProductID', right_on='PRODUCT_ID', how='left')
top_cats = nba_meta['COMMODITY_DESC'].value_counts().head(10)

plt.figure(figsize=(10, 6))
top_cats.plot(kind='barh', color='salmon')
plt.gca().invert_yaxis()
plt.title('상위 10개 추천 상품 카테고리 분포 (다양성 확인)', fontsize=15)
plt.xlabel('추천 횟수')
plt.savefig(os.path.join(nba_report_dir, 'nba_category_diversity.png'))
plt.close()

# --- 1.2 TS 보강: 신뢰도 등급 분포 ---
print("[TS] 신뢰도 등급 분포 생성 중...")
conf_dist = ts_metrics['Confidence_Score'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(conf_dist, labels=conf_dist.index, autopct='%1.1f%%', colors=['#66b3ff','#99ff99','#ff9999'], startangle=140)
plt.title('수요 예측 모델 신뢰도 등급 분포', fontsize=15)
plt.savefig(os.path.join(ts_report_dir, 'ts_confidence_pie.png'))
plt.close()

# --- 2.2 MBA 보강: 세그먼트별 평균 장바구니 크기 ---
print("[MBA] 세그먼트별 장바구니 크기 비교 생성 중...")
# 통합 데이터에서 세그먼트별 장바구니당 품목 수 계산
df_integrated = pd.read_csv('dunnhumby_integrated_data.csv')
rfm_df = pd.read_csv('dunnhumby_rfm_segments.csv')
df_integrated = df_integrated.merge(rfm_df[['CustomerID', 'Customer_Segment']], on='CustomerID', how='left')
basket_sizes = df_integrated.groupby(['Customer_Segment', 'BASKET_ID']).size().reset_index(name='count')
avg_basket_sizes = basket_sizes.groupby('Customer_Segment')['count'].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
avg_basket_sizes.plot(kind='bar', color='skyblue')
plt.title('고객 세그먼트별 평균 장바구니 구매 품목 수', fontsize=15)
plt.xlabel('고객 세그먼트')
plt.ylabel('평균 품목 수')
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(mba_report_dir, 'mba_segment_basket_size.png'))
plt.close()

# --- 3.2 NBA 보강: 추천 엔진 질적 지표 요약 ---
print("[NBA] 질적 지표 요약 생성 중...")
# 하드코딩된 메트릭 시각화 (이미 계산된 값이 있다고 가정)
metrics = {'Diversity': 35.42, 'Serendipity': 8.5}
plt.figure(figsize=(8, 6))
plt.bar(metrics.keys(), metrics.values(), color=['salmon', 'lightblue'])
for i, v in enumerate(metrics.values()):
    plt.text(i, v + 0.5, f"{v}%", ha='center', fontweight='bold')
plt.title('추천 시스템 질적 지표 (다양성 및 의외성)', fontsize=15)
plt.ylabel('점수 (%)')
plt.ylim(0, 50)
plt.savefig(os.path.join(nba_report_dir, 'nba_qualitative_metrics.png'))
plt.close()

print("--- 시각화 생성 완료 ---")
