# [최종 상세 보고서] [Stage 1] Discovery: 데이터 기반 탐색 엔진 (NBA)

---

## 🏛️ 0. Executive Decision Summary (임원용 요약)

> [!IMPORTANT]
> **"단순한 추천을 넘어, 고객의 다음 탐색 경로를 설계하십시오."**
>
> 본 분석은 Dunnhumby 데이터셋의 259만 건 거래 기록을 바탕으로, **7가지 페르소나**의 각기 다른 탐색 동기를 엔진에 주입했습니다. 
> 
> **핵심 결론**:
> 1.  **VIP Champions**는 **35.4%라는 가장 높은 다양성 점수**와 **99.8%의 재구매율**을 동시에 가진 '이상적인 탐험가'입니다. 이들은 이미 충분히 다양하게 사고 있으므로, 더 과감한 프리미엄 크로스셀링을 시도해야 합니다.
> 2.  **Bargain Hunters**는 **32.4%로 가장 낮은 다양성**을 보입니다. '할인 상품'이라는 좁은 필터에 갇혀 있어, 이들에게는 할인 상품 옆에 필수로 연관 상품을 배치하는 '미끼 전략'이 필요합니다.
> 3.  **New/Light Users**는 재구매 정밀도가 **92.3%로 가장 낮아** 아직 자신만의 '최애 상품'을 찾지 못한 상태입니다. 인기 상품 위주의 안전한 가이드가 시급합니다.

---

## 📌 1. 분석 개요 (Objective & Questions)

### 1.1 분석 목적 (Objective)
고객 여정의 첫 단추인 '상품 발견(Discovery)'을 최적화하기 위해 개인화된 추천 엔진(Next Best Action)을 구축합니다. 팀 표준 **7개 페르소나**의 각기 다른 탐색 동기(할인, 신규성, 습관 등)를 반영하여 고객별 맞춤형 탐색 경로를 제시함으로써, 초기 방문이 실질적인 구매 맥락 형성으로 이어지는 전환율을 극대화합니다.

### 1.2 핵심 질문 (Key Business Questions)
- **Q1**: "어떻게 하면 편향된 추천(Filter Bubble)을 깨고 고객이 새로운 카테고리를 탐험하게 할 것인가?"
- **Q2**: "신규 고객이 단골 고객으로 전환되는 '운명의 상품'을 어떻게 정밀하게 노출할 것인가?"
- **Q3**: "소득 수준과 페르소나별로 추천의 '폭(Diversity)'과 '깊이(Precision)'를 어떻게 다르게 설정해야 하는가?"

---

## 🔬 2. 분석 방법론 (Methodology)

### 2.1 하이브리드 추천 알고리즘 (Hybrid Strategy)
- **Collaborative Filtering (CF)**: 사용자 간 유사한 구매 패턴을 분석합니다. 취향이 확고한 **VIP/Loyal** 그룹에 높은 가중치를 부여합니다.
- **Content-Based Filtering (CBF)**: 상품의 속성(소득 수준별 선호도, 카테고리 특성)을 분석합니다. 데이터가 부족한 **New/Light** 그룹의 콜드-스타트(Cold-start) 방지에 활용합니다.
- **Hybrid Scoring**: `0.6 * CF + 0.4 * CBF` 조합을 기본으로 하되, 페르소나별로 동적 가중치를 적용합니다.

---

## 📊 3. 분석 결과 및 장표 상세 분석 (Results Deep-Dive)

### 3.1 페르소나별 추천 성능 지표 (Data-Driven Fact)
| 페르소나 (분류 기준) | Discovery 다양성 (Entropy) | Precision (재구매율) | 데이터 기반 핵심 발견 (Insight) |
| :--- | :---: | :---: | :--- |
| **VIP Champions** (상위 20% 핵심 고객) | **35.4% (Highest)** | **99.8%** | **"The Real Explorers"**: VIP는 특정 카테고리에 갇히지 않고 매장 전역을 탐색합니다. |
| **Loyal Shoppers** (상위 40% 우량 고객) | 34.7% | 99.7% | **Balanced**: 탐색과 습관 구매가 완벽한 균형을 이룹니다. |
| **At-Risk** (과거 우량, 최근 이탈) | 34.4% | 99.4% | **High Precision**: 이탈 위험군임에도 과거 구매 품목에 대한 의존도가 매우 높습니다. |
| **New/Light Users** (최근 유입, 저구매) | 34.1% | **92.3% (Lowest)** | **Exploration Phase**: 재구매율이 상대적으로 낮아, 아직 '자신만의 상품'을 찾는 중입니다. |
| **Regular Shoppers** (중간 빈도/금액) | 33.5% | 98.8% | **Stable Scope**: 적당한 범위 내에서 안정적인 구매 패턴을 보입니다. |
| **Bargain Hunters** (쿠폰 사용 상위 10%) | **32.4% (Lowest)** | 94.8% | **Price Bubble**: 할인이 적용되는 특정 카테고리만 편식하여 다양성이 가장 낮습니다. |
| **Occasional Buyers** (간헐적 방문) | 34.0% | 99.1% | **Event Driven**: 방문 빈도는 낮으나 구매 시 다양한 품목을 한 번에 비축합니다. |

### 3.2 시각화 장표 상세 분석 (Presentation Slides)

<details>
<summary><b>📊 Slide 1: 페르소나별 탐색 다양성 스펙트럼 (Diversity Score)</b></summary>

![점수 분포](plots/nba_score_distribution.png)

- **Data Insight**: 놀랍게도 **VIP Champions**의 추천 다양성 점수가 35.4%로 가장 높게 측정되었습니다. 이는 VIP 고객이 단순히 '우유'만 사는 것이 아니라, 신선식품부터 공산품까지 가장 넓은 카테고리 스펙트럼을 소비하고 있음을 증명합니다.
- **So-What?**: VIP에게는 "살던 것만 추천"하는 보수적 알고리즘보다, **"새로운 프리미엄 라인"**을 제안해도 충분히 수용할 수 있는 '탐색 탄력성'이 존재합니다.
</details>

<details>
<summary><b>🎯 Slide 2: [Bargain Hunters] 할인이 만든 필터 버블 (Filter Bubble)</b></summary>

![소득별 다양성](plots/nba_income_diversity_gap.png)

- **Critical Finding**: **Bargain Hunters** 그룹은 다양성 점수가 32.4%로 전체 페르소나 중 가장 낮습니다. 
- **원인 분석**: 이들은 자신의 '취향'이 아니라 **'가격(Discount)'**이 상품 선택의 제1경로이기 때문에, 세일하지 않는 카테고리(예: 유기농 채소, 프리미엄 델리)는 아예 탐색 경로에서 배제되어 있습니다.
- **Action**: 이들의 필터 버블을 깨기 위해서는 "할인 상품" 옆에 "연관 프리미엄 상품"을 배치하는 **'미끼 추천(Decoy Recommendation)'** 전략이 필수적입니다.
</details>

<details>
<summary><b>🥗 Slide 3: 추천 엔진의 질적 지표 (Diversity & Serendipity)</b></summary>

![질적 지표](plots/nba_qualitative_metrics.png)

- **지표 해설**: 다양성(35.4%)과 의외성(8.5%)이 균형을 이루고 있습니다. 너무 뻔한 상품만 추천하면 고객이 지루함을 느끼고(Filter Bubble), 너무 뜬뚱맞은 상품만 추천하면 신뢰를 잃습니다.
- **비즈니스 효과**: 8.5%의 의외성(Serendipity)은 고객에게 "이런 것도 있었네?"라는 즐거움을 주어 매장 체류 시간과 앱 앱 유지율(Retention)을 높이는 핵심 요소가 됩니다.
</details>

---

## 💡 4. 페르소나별 비즈니스 인사이트 (7 Discovery Insights)

1.  **VIP Champions**: 이들에게는 '의외의 발견'을 위해 고단가 카테고리(Premium Deli) 노출 비중을 20% 상향하십시오. 이미 충성도가 높으므로 새로운 카테고리 진입 장벽이 가장 낮습니다.
2.  **Loyal Shoppers**: 주간 반복 품목 외에 '함께 사는 보완재'의 CF 노출을 강화하여 장바구니 다양성을 15% 개선 시키는 것이 목표입니다.
3.  **Regular Shoppers**: 방문 주기를 단축하기 위해 'Time-Sensitive' 한정 제안(오늘만 할인 등)을 엔진 최상단에 배치하여 탐색의 긴박감을 부여하십시오.
4.  **At-Risk**: 추천 리스트의 70%를 과거 구매 이력이 있는 'Essential' 품목으로 구성하십시오. 새로운 도전보다는 '익숙함'을 통해 복귀의 심리적 허들을 낮추는 것이 급선무입니다.
5.  **New/Light Users**: CBF 가중치를 0.8까지 끌어올려, 유사 인구통계 그룹이 검증한 '안전한 베스트셀러' 위주로 노출하십시오. 첫 구매의 실패를 방지하는 것이 안정화 단계 진입의 핵심입니다.
6.  **Bargain Hunters**: 가격 비교 피로도를 낮추기 위해 '최대 할인율'과 '최다 쿠폰 적용' 품목을 추천 우선순위로 강제 설정(Hard-coding) 할 필요가 있습니다.
7.  **Occasional Users**: 브랜드 친숙도를 높이기 위해 자사 PB 상품(Private Label) 중 평점 4.5 이상의 '입문형 상품'을 집중 추천하여 가성비 경험을 유도하십시오.

---

## 🎯 5. 액션 플랜 (Action Roadmap)

| 액션 아이템 | 대상 페르소나 | 우선순위 | 기대 효과 |
| :--- | :--- | :---: | :--- |
| **개인화 추천 사유 알림 정교화** | VIP, Loyal | 🔴 High | 알림 오픈율 20% 및 CTR 12% 상승 |
| **신규 고객용 '실패 없는 팩' 추천** | New/Light | 🔴 High | 2회차 구매 전환율 15% 개선 |
| **이탈 징후 기반 'Welcome Back' 추천** | At-Risk | 🟠 Medium | 휴면 고객 복귀율 8% 증대 |
| **카테고리 확장 테마 기획전** | Regular, Bargain | 🟡 Low | 교차 구매 성사율 10% 증가 |

---

**다음 여정 연결**: 발견(Discovery)된 상품들이 실제 장바구니에서 어떻게 결합(Context)되는지는 [Stage 2] [MBA 보고서](../mba/dunnhumby_mba_analysis_report.md)에서 확인하십시오.
