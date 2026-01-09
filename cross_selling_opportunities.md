# 교차 판매 기회 리포트 (Cross-Selling Opportunities)

## 1. 요약 (Executive Summary)
- **목적**: 장바구니 크기(객단가) 증대를 위한 고잠재력 상품 번들(조합) 발굴.
- **방법론**: 상위 50개 인기 상품 및 50만 건 샘플 데이터를 활용한 장바구니 분석 (Apriori 알고리즘, 1048개 규칙 도출).
- **핵심 결과**: 대중적인 **'파워 번들' 10개**와 틈새 시장을 위한 **'히든 잼' 10개** 조합 발견.

## 2. 시각화 개요 (Visual Overview)
### 상품 연관성 네트워크 (Product Association Network)
![Network Graph](plots/mba/mba_network_graph.png)
*Fig 1. 주요 상품(Hub)과 강한 연결 관계 시각화 (선이 굵을수록 연관성 높음)*

### 기회 지도 (Opportunity Map: Support vs Lift)
![Scatter Plot](plots/mba/mba_scatter_plot.png)
*Fig 2. 규칙 세분화. 우측 상단일수록 최상의 기회 요소임.*

## 3. Top 10 '파워 번들' (대중적 인기 조합)
발생 빈도(Support)가 높고 연관성(Lift)도 강한 조합입니다. **전략**: 트래픽이 많은 매대나 메인 페이지에 '함께 구매하면 좋은 상품'으로 배치하세요.

| 상품 A (Antecedent) | 상품 B (Consequent) | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |
| :--- | :--- | :--- | :--- | :--- |
| DRY BN/VEG/POTATO/RICE | VEGETABLES - SHELF STABLE | 3.00 | 0.16 | 0.0047 |
| DRY NOODLES/PASTA | VEGETABLES - SHELF STABLE | 2.73 | 0.15 | 0.0038 |
| VEGETABLES - SHELF STABLE | FRUIT - SHELF STABLE | 2.71 | 0.08 | 0.0043 |
| FRUIT - SHELF STABLE | VEGETABLES - SHELF STABLE | 2.71 | 0.15 | 0.0043 |
| DINNER MXS:DRY | VEGETABLES - SHELF STABLE | 2.57 | 0.14 | 0.0038 |
| CONVENIENT BRKFST/WHLSM SNACKS | COLD CEREAL | 2.50 | 0.13 | 0.0040 |
| SOUP | MEAT - SHELF STABLE | 2.47 | 0.08 | 0.0047 |
| FROZEN PIZZA | DINNER MXS:DRY | 2.41 | 0.06 | 0.0036 |
| DINNER MXS:DRY | FROZEN PIZZA | 2.41 | 0.13 | 0.0036 |
| SOUP | DINNER MXS:DRY | 2.39 | 0.06 | 0.0038 |

## 4. Top 10 '히든 잼' (틈새 타겟팅)
전체 발생 빈도는 낮지만, 구매 시 함께 살 확률이 매우 높은 강력한 조합입니다. **전략**: 계산대에서의 개인화 추천이나 타겟 쿠폰 발송에 활용하세요.

| 상품 A (Antecedent) | 상품 B (Consequent) | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |
| :--- | :--- | :--- | :--- | :--- |
| DRY NOODLES/PASTA | PASTA SAUCE | 5.66 | 0.12 | 0.0030 |
| DINNER MXS:DRY | MEAT - SHELF STABLE | 3.73 | 0.12 | 0.0032 |
| DINNER MXS:DRY | DRY BN/VEG/POTATO/RICE | 3.35 | 0.10 | 0.0026 |
| BAKING MIXES | BAKING NEEDS | 3.33 | 0.07 | 0.0017 |
| PWDR/CRYSTL DRNK MX | DINNER MXS:DRY | 3.16 | 0.08 | 0.0014 |
| DINNER MXS:DRY | PWDR/CRYSTL DRNK MX | 3.16 | 0.05 | 0.0014 |
| PASTA SAUCE | DINNER MXS:DRY | 2.97 | 0.08 | 0.0017 |
| DINNER MXS:DRY | PASTA SAUCE | 2.97 | 0.06 | 0.0017 |
| PWDR/CRYSTL DRNK MX | MEAT - SHELF STABLE | 2.94 | 0.09 | 0.0015 |
| DRY BN/VEG/POTATO/RICE | PASTA SAUCE | 2.92 | 0.06 | 0.0018 |

## 5. 전략적 제언 (Strategic Recommendations)
1. **번들 프로모션**: 위 '파워 번들' 상품군에 대해 'A 구매 시 B 10% 할인'과 같은 행사를 기획하십시오.
2. **매장 레이아웃**: 네트워크 그래프에서 식별된 'Hub Product'(중심 상품) 주변에 연관 상품을 근접 배치하십시오.
3. **개인화 마케팅**: '히든 잼' 조합을 활용하여, 최근 상품 A를 구매한 고객에게 상품 B에 대한 타겟 메시지를 발송하십시오.
