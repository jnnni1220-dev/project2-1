
import pandas as pd
import os

print("--- Starting NBA Summary Report Generation (KR) ---")

# 1. 데이터 로드
nba_path = r'results/nba_recommendations.csv'
if not os.path.exists(nba_path):
    print("Error: NBA recommendations file not found.")
    exit()

df_nba = pd.read_csv(nba_path)

# 2. 주요 지표 계산
recs_series = df_nba['recommendations'].str.split(', ')
all_recs = [item for sublist in recs_series for item in sublist]
top_recs = pd.Series(all_recs).value_counts().head(5)

# 3. 리포트 내용 구성
summary_content = f"""# NBA 추천 분석 최종 요약 보고서 (Summary Report)

## 1. 분석 개요
본 분석은 고객의 과거 구매 이력을 바탕으로 **개인화된 차기 구매 상품(Next Best Action)**을 제안하는 시스템을 구축하고 그 결과를 요약한 것입니다.

- **분석 방법**: 사용자 기반 협업 필터링 (User-Based Collaborative Filtering)
- **핵심 알고리즘**: Cosine Similarity 기반 가구 간 유사도 계산
- **데이터 소스**: dunnhumby 'The Complete Journey' 데이터셋

## 2. 주요 분석 결과 (Key Findings)

### 2.1 추천 빈도 상위 5개 카테고리
전체 가구를 대상으로 가장 높은 추천 점수를 기록한 주요 카테고리 요약입니다.

| 순위 | 상품 카테고리 | 추천 빈도 (건) |
| :--- | :--- | :--- |
"""

for i, (category, count) in enumerate(top_recs.items(), 1):
    summary_content += f"| {i} | {category} | {count} |\n"

summary_content += f"""
### 2.2 추천 결과 요약
- **분석 대상 가구 수**: {len(df_nba)} 가구
- **유사도 기반 매칭**: 각 가구별로 가장 유사한 'Shopping Twins' 10곳의 데이터를 분석하여 상품 도출
- **개인화 수준**: 가구가 기존에 구매하지 않았던 품목 중 유사 가구의 구매도가 높은 품목을 우선순위로 추천

## 3. 전략적 제언 (Strategic Suggestions)
1. **교차 판매(Cross-Selling) 강화**: 상위 추천 품목인 신선식품(Milk, Cheese) 및 음료군을 중심으로 타겟 마케팅을 진행하여 구매 주기를 단축할 수 있습니다.
2. **이탈 방지(Retention)**: 가구별 추천 리스트를 기반으로 맞춤형 할인 쿠폰을 발급하여 고객 플랫폼 고착도(Lock-in)를 강화할 것을 제안합니다.

## 4. 관련 자료 링크
- [**심층 분석 보고서 (Detailed Report)**](https://github.com/jnnni1220-dev/project2-1/blob/main/nba_enhanced_report_kr.md)
- [**추천 데이터 세부 결과 (CSV)**](https://github.com/jnnni1220-dev/project2-1/blob/main/results/nba_recommendations.csv)
- [**분석 실행 코드 (Python)**](https://github.com/jnnni1220-dev/project2-1/blob/main/10_nba_collaborative_filtering.py)
"""

# 4. 리포트 저장
output_path = 'nba_summary_report_kr.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(summary_content)

print(f"Summary report saved to {output_path}")
print("--- NBA Summary Report Generation Finished ---")
