# Dunnhumby 장바구니 분석 상세 보고서

## 1. 분석 방법론 및 프로세스 (Methodology)
본 분석은 대규모 트랜잭션 데이터에서 유의미한 상품 간 관계를 추출하기 위해 다음과 같은 프로세스를 따랐습니다.

- **분석 알고리즘**: Apriori 알고리즘 활용 (최소 지지도 0.001 이상 규칙 추출)
- **데이터 필터링**: 분석의 집중도를 높이기 위해 판매 빈도가 높은 상위 50개 품목으로 제한
- **데이터 안정성 검증 (Stability Analysis)**: 
    - 전체 데이터를 무작위로 분할하여 동일한 규칙이 얼마나 일관되게 발견되는지 측정 (Cross-validation)
    - 결과: **Stability Score: 79.43%**
- **시점 및 세그먼트 분석**: 기간별 구매 패턴 변화와 RFM 기반 고객 세그먼트별 연관 규칙 차이 분석

## 2. 연관 규칙 분석 지표 해석 가이드
- **지지도 (Support)**: 전체 거래 중 해당 상품 조합이 동시에 나타나는 비율입니다. (절대적 빈도)
- **신뢰도 (Confidence)**: 상품 A를 구매했을 때 상품 B도 구매할 확률입니다. (조건부 확률)
- **향상도 (Lift)**: 두 상품이 서로 독립적일 때보다 얼마나 더 자주 함께 구매되는지를 나타내며, **1보다 클수록 유의미한 연관성**을 가집니다.

## 3. 핵심 연관 규칙 리스트 (Top 20 Rules)
| 순위 | 선행 상품 (A) | 후속 상품 (B) | 지지도 | 신뢰도 | 향상도 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | KIDS CEREAL, SUGAR | SOFT DRINK POWDER POUCHES, MAINSTREAM WHITE BREAD, FLUID MILK WHITE ONLY | 0.0011 | 0.1571 | 36.04 |
| 2 | SOFT DRINK POWDER POUCHES, MAINSTREAM WHITE BREAD, FLUID MILK WHITE ONLY | KIDS CEREAL, SUGAR | 0.0011 | 0.2523 | 36.04 |
| 3 | SOFT DRINK POWDER POUCHES, MAINSTREAM WHITE BREAD | FLUID MILK WHITE ONLY, KIDS CEREAL, SUGAR | 0.0011 | 0.1622 | 30.73 |
| 4 | FLUID MILK WHITE ONLY, KIDS CEREAL, SUGAR | SOFT DRINK POWDER POUCHES, MAINSTREAM WHITE BREAD | 0.0011 | 0.2083 | 30.73 |
| 5 | SOFT DRINK POWDER POUCHES, KIDS CEREAL | MAINSTREAM WHITE BREAD, FLUID MILK WHITE ONLY, SUGAR | 0.0011 | 0.2183 | 30.23 |
| 6 | MAINSTREAM WHITE BREAD, FLUID MILK WHITE ONLY, SUGAR | SOFT DRINK POWDER POUCHES, KIDS CEREAL | 0.0011 | 0.1524 | 30.23 |
| 7 | SOFT DRINK POWDER POUCHES, FLUID MILK WHITE ONLY | MAINSTREAM WHITE BREAD, KIDS CEREAL, SUGAR | 0.0011 | 0.1046 | 29.21 |
| 8 | MAINSTREAM WHITE BREAD, KIDS CEREAL, SUGAR | SOFT DRINK POWDER POUCHES, FLUID MILK WHITE ONLY | 0.0011 | 0.3073 | 29.21 |
| 9 | KIDS CEREAL, SUGAR | SOFT DRINK POWDER POUCHES, MAINSTREAM WHITE BREAD | 0.0014 | 0.1943 | 28.66 |
| 10 | SOFT DRINK POWDER POUCHES, MAINSTREAM WHITE BREAD | KIDS CEREAL, SUGAR | 0.0014 | 0.2006 | 28.66 |
| 11 | SHREDDED CHEESE, SOFT DRINK POWDER POUCHES | KIDS CEREAL, SUGAR | 0.0011 | 0.1986 | 28.37 |
| 12 | KIDS CEREAL, SUGAR | SHREDDED CHEESE, SOFT DRINK POWDER POUCHES | 0.0011 | 0.1600 | 28.37 |
| 13 | SOFT DRINK POWDER POUCHES, FLUID MILK WHITE ONLY, KIDS CEREAL | MAINSTREAM WHITE BREAD, SUGAR | 0.0011 | 0.3005 | 27.27 |
| 14 | MAINSTREAM WHITE BREAD, SUGAR | SOFT DRINK POWDER POUCHES, FLUID MILK WHITE ONLY, KIDS CEREAL | 0.0011 | 0.0998 | 27.27 |
| 15 | SHREDDED CHEESE, SUGAR | SOFT DRINK POWDER POUCHES, KIDS CEREAL | 0.0011 | 0.1242 | 24.64 |
| 16 | SOFT DRINK POWDER POUCHES, KIDS CEREAL | SHREDDED CHEESE, SUGAR | 0.0011 | 0.2222 | 24.64 |
| 17 | SOFT DRINK POWDER POUCHES, KIDS CEREAL | MAINSTREAM WHITE BREAD, SUGAR | 0.0014 | 0.2698 | 24.49 |
| 18 | MAINSTREAM WHITE BREAD, SUGAR | SOFT DRINK POWDER POUCHES, KIDS CEREAL | 0.0014 | 0.1234 | 24.49 |
| 19 | SOFT DRINK POWDER POUCHES, FLUID MILK WHITE ONLY | KIDS CEREAL, SUGAR | 0.0017 | 0.1654 | 23.63 |
| 20 | KIDS CEREAL, SUGAR | SOFT DRINK POWDER POUCHES, FLUID MILK WHITE ONLY | 0.0017 | 0.2486 | 23.63 |

## 4. 전략적 제언 및 가이드
- **고향상도 품목 (Lift > 2.0)**: 매장 내 진열을 인접하게 배치하여 자연스러운 추가 구매 유도.
- **고신뢰도 품목 (Confidence > 0.5)**: 주력 상품(A) 구매 시 보조 상품(B)에 대한 타겟 쿠폰 발송.

---
*원천 데이터셋 정보: dunnhumby_integrated_data.csv / 분석 수행일: 2025-05-22*
