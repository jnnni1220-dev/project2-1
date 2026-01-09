# 교차 판매 기회 및 전략 리포트 (Cross-Selling Strategic Report)

## 1. 분석 방법론 및 프로세스 (Detailed Methodology)
### 1.1 데이터 선정 및 전처리 (Data Preparation)
- **분석 대상**: 총 거래 건수 기준 **상위 50개 Popular Commodities**로 범위를 한정하여 유의미한 패턴 도출에 집중했습니다.
- **샘플링 (Sampling)**: 전체 데이터 중 **500,000건의 거래**를 무작위 추출하여 분석 효율성과 대표성을 확보했습니다.
- **장바구니 구성 (Basketization)**: `BASKET_ID`를 기준으로 상품 포함 여부를 `0/1 (Boolean)` 행렬로 변환했습니다.

### 1.2 분석 알고리즘 (Algorithm & Thresholds)
- **알고리즘**: **Apriori Algorithm**을 사용하여 빈발 항목 집합(Frequent Itemsets)을 탐색했습니다.
- **설정 임계값**:
    - **Minimum Support**: `0.001 (0.1%)` - 희귀하지만 강력한 패턴(Long-tail)을 놓치지 않기 위해 낮게 설정.
    - **Minimum Lift**: `1.01` - 우연에 의한 동시 구매(Lift=1)보다 확실히 연관성이 있는 조합만 필터링.

### 1.3 검증 및 시각화 (Validation & Visualization)
- **교차 검증 (Stability Check)**: 데이터를 두 그룹(Split A/B)으로 나누어 도출된 규칙이 반복적으로 관측되는지 테스트했습니다.
    - **안정성 점수 (Stability Score)**: **93.01%** (매우 높음)
    - *해석*: 점수가 높다는 것은 발견된 '맥주-기저귀' 같은 패턴이 일시적인 현상이 아니라 **구조적이고 지속적인 구매 행동**임을 의미합니다.
- **시각화**: 파이썬 `NetworkX`를 활용한 관계망 분석과 `Seaborn` 히트맵을 통해 직관적인 패턴 인식을 지원합니다.

## 2. 시각화 분석 (Visual Analytics)
### A. 상품 연관성 네트워크 (Association Network)
![Network Graph](plots/mba/mba_network_graph.png)
**[해석 가이드]**
- **노드(점)**: 개별 상품(Category)을 나타냅니다. 크기가 클수록 연결된 다른 상품이 많다는 뜻입니다.
- **엣지(선)**: 두 상품 간의 연관성입니다. **선이 굵을수록 향상도(Lift)가 높아** 함께 구매할 확률이 높습니다.
- **전략**: 중앙에 위치하며 많은 연결선을 가진 **'Hub Product'**를 매장의 메인 동선이나 온라인 몰 홈 화면에 배치하여 트래픽을 분산시키십시오.

### B. 카테고리 히트맵 (Category Heatmap)
![Heatmap](plots/mba/mba_category_heatmap.png)
**[해석 가이드]**
- **X축/Y축**: 선행 상품(Antecedent)과 후행 상품(Consequent)입니다.
- **색상 농도**: 짙은 파란색/녹색일수록 두 카테고리의 **Lift(연관 강도)가 매우 높음**을 의미합니다.
- **전략**: 짙은 색으로 표시된 카테고리 쌍은 물리적으로 인접 진열(Cross-Merchandising)하거나 세트 상품으로 기획해야 할 1순위 후보입니다.

### C. 기회 탐색 지도 (Opportunity Map)
![Scatter Plot](plots/mba/mba_scatter_plot.png)
**[해석 가이드]**
- **X축 (Support)**: 얼마나 자주 팔리는가? (대중성)
- **Y축 (Lift)**: 함께 팔릴 확률이 얼마나 높아지는가? (연관성)
- **우측 상단 (Best)**: 대중적이면서 연관성도 높은 '확실한 수익원(Cash Cow)'입니다.
- **좌측 상단 (Niche)**: 판매량은 적지만 연관성이 폭발적인 '숨겨진 기회(Hidden Gem)'입니다. 정교한 타겟 마케팅이 유효합니다.

## 3. 심층 전략 제언 (Strategic Deep Dive)
**[데이터가 말하는 마케팅 전략]**
본 분석에서 도출된 **'파워 번들'**과 **'히든 잼'**은 각각 다른 접근 방식이 필요합니다. 

1.  **매스 마케팅 (Mass Marketing) - 파워 번들 활용**:
    - 파워 번들은 이미 고객들에게 인지도가 높은 '국민 조합'입니다. 이들은 수익의 기반(Cash Cow)이므로, **'번들 할인(Bundle Pricing)'**보다는 **'편의성(Convenience)'**에 초점을 맞춰야 합니다. 
    - 예를 들어, 두 상품을 물리적으로 묶어 진열하거나 거리를 좁히는 것만으로도 구매 전환율을 극대화할 수 있습니다. 할인은 최소화하여 마진을 방어하십시오.

2.  **타겟 마케팅 (Target Marketing) - 히든 잼 활용**:
    - 히든 잼은 특정 취향을 가진 고객층에서만 강하게 나타나는 패턴입니다. 이는 **'개인화 추천 알고리즘'**의 핵심 자산이 됩니다. 
    - 멤버십 데이터를 활용하여 선행 상품(Antecedent)을 구매한 이력이 있는 고객에게 후행 상품(Consequent) 할인 쿠폰을 발송하십시오. 이는 고객으로 하여금 '나를 알아주는 서비스'라는 인식을 심어주어 충성도를 높입니다.

3.  **매장 레이아웃 최적화 (Store Layout Optimization)**:
    - 안정성 점수({stability_score})가 높은 규칙들은 계절이나 유행을 타지 않는 본질적인 구매 패턴입니다. 
    - 이러한 패턴을 기반으로 매장 내 'Golden Zone'을 재설계하십시오. 연관성이 높은 카테고리를 인접 배치(Cross-Merchandising)하면 고객의 체류 시간을 늘리고 자연스러운 추가 구매를 유도할 수 있습니다.

## 4. Top 10 '파워 번들' (Mass Appeal)
| 상품 A | 상품 B | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |
| :--- | :--- | :--- | :--- | :--- |
| DRY BN/VEG/POTATO/RICE | VEGETABLES - SHELF STABLE | 3.00 | 0.16 | 0.0047 |
| VEGETABLES - SHELF STABLE | DRY NOODLES/PASTA | 2.73 | 0.07 | 0.0038 |
| VEGETABLES - SHELF STABLE | FRUIT - SHELF STABLE | 2.71 | 0.08 | 0.0043 |
| FRUIT - SHELF STABLE | VEGETABLES - SHELF STABLE | 2.71 | 0.15 | 0.0043 |
| VEGETABLES - SHELF STABLE | DINNER MXS:DRY | 2.57 | 0.07 | 0.0038 |
| COLD CEREAL | CONVENIENT BRKFST/WHLSM SNACKS | 2.50 | 0.08 | 0.0040 |
| SOUP | MEAT - SHELF STABLE | 2.47 | 0.08 | 0.0047 |
| FROZEN PIZZA | DINNER MXS:DRY | 2.41 | 0.06 | 0.0036 |
| DINNER MXS:DRY | FROZEN PIZZA | 2.41 | 0.13 | 0.0036 |
| SOUP | DINNER MXS:DRY | 2.39 | 0.06 | 0.0038 |

## 5. Top 10 '히든 잼' (Niche Targeting)
| 상품 A | 상품 B | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |
| :--- | :--- | :--- | :--- | :--- |
| PASTA SAUCE | DRY NOODLES/PASTA | 5.66 | 0.14 | 0.0030 |
| MEAT - SHELF STABLE | DINNER MXS:DRY | 3.73 | 0.10 | 0.0032 |
| DRY BN/VEG/POTATO/RICE | DINNER MXS:DRY | 3.35 | 0.09 | 0.0026 |
| BAKING MIXES | BAKING NEEDS | 3.33 | 0.07 | 0.0017 |
| PWDR/CRYSTL DRNK MX | DINNER MXS:DRY | 3.16 | 0.08 | 0.0014 |
| DINNER MXS:DRY | PWDR/CRYSTL DRNK MX | 3.16 | 0.05 | 0.0014 |
| PASTA SAUCE | DINNER MXS:DRY | 2.97 | 0.08 | 0.0017 |
| DINNER MXS:DRY | PASTA SAUCE | 2.97 | 0.06 | 0.0017 |
| MEAT - SHELF STABLE | PWDR/CRYSTL DRNK MX | 2.94 | 0.05 | 0.0015 |
| PASTA SAUCE | DRY BN/VEG/POTATO/RICE | 2.92 | 0.08 | 0.0018 |
