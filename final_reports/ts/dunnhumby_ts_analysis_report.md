# [최종 상세 보고서] [Stage 3] Stabilization: 습관의 정착과 안정 (TS)

---

## 🏛️ 0. Executive Decision Summary (임원용 요약)

> [!IMPORTANT]
> **"구매가 멈추기 전에, 데이터로 그 전조(Drift)를 파악하십시오."**
>
> 본 분석은 고객이 발견(Discovery)하고 맥락(Context)을 형성한 상품들이 정기적인 유통 루틴으로 안착했는지 검증합니다. 시계열 모델을 통해 **7개 페르소나**의 구매 주기를 예측하고, 여정의 끊김(Interruption)을 방지하는 안정적 공급망 전략을 지원합니다.
> 
> **핵심 결론**:
> 1.  **The VIP Paradox**: **VIP Champions**의 시계열 안정성 점수는 **46.4%**로 낮게 나타났습니다. 이는 '불안정'이 아니라, 너무 잦은 방문으로 인한 **'자연스러운 변동성(Frequency Variance)'** 때문입니다. **VIP Champions** 전략은 '방문 유도'가 아닌 '객단가 방어'여야 합니다.
> 2.  **At-Risk** 고객은 안정성 점수가 **43.2%**로 가장 낮으며, 이는 방문 주기가 완전히 무너진 '카오스(Chaos)' 상태를 의미합니다. 예측 범위를 벗어난 이들에게는 즉각적인 '루틴 복구 쿠폰'이 필요합니다.
> 3.  **Occasional Buyers**는 오히려 **58.0%**의 높은 방문 예측 가능성을 보였습니다. 이들은 특정 시점(월초, 이벤트)에만 정확히 나타나므로, 캘린더 기반 마케팅이 가장 효과적입니다.

---

## 📌 1. 분석 개요 (Objective & Questions)

### 1.1 분석 목적 (Objective)
고객의 구매 행위가 우발적인 선택을 넘어 정기적 생활 패턴으로 진화했는지 데이터로 입증합니다. 고도화된 Prophet 및 SARIMA 모델을 활용하여 미래 수요를 예측하고, 이를 바탕으로 페르소나별Retention(유지) 전략과 재고 최적화 매뉴얼을 구축합니다.

### 1.2 핵심 질문 및 데이터 기반 해답 (Key Business Questions & Answers)

> **Q1: "재고 부족(Stock-out)으로 인해 핵심 고객의 구매 루틴이 깨질 위험이 가장 큰 품목은 무엇인가?"**
> - **Answer (Data Fact)**: **Bargain Hunters**와 **Loyal Shoppers**의 경우, 방문의 약 **26~31%**가 **'Fluid Milk(우유)'** 구매를 수반합니다. 이 핵심 품목이 품절되면 장바구니 구심점이 사라져 방문 취소로 이어질 확률이 매우 높습니다. 반면 **New/Light Users**는 특정 품목 의존도가 낮아(Risk < 20%) 상대적으로 영향이 적습니다. 
> - **Evidence**: [Stock-out Risk Chart](plots/deep_dive/q1_stockout_risk.png)

> **Q2: "고객의 방문 주기가 시계열 예측 범위를 벗어났을 때, 이를 어떻게 '이탈 징후'로 조기 감지할 것인가?"**
> - **Answer (Data Fact)**: **At-Risk** 그룹은 최근 4주간 평균 방문 횟수가 과거 대비 **-3.9회** 급감했습니다. 이는 단순한 변동이 아니라 '구조적 이탈(Drift)'이 시작되었음을 알리는 명확한 신호입니다. 반면 **VIP Champions**는 오히려 +0.6회 증가하며 건강한 활동성을 유지 중입니다.
> - **Evidence**: [Churn Signal Chart](plots/deep_dive/q2_churn_signal.png)

> **Q3: "페르소나별로 구매 주기의 견고함(Stabilization Index)은 어떻게 다르며, 이를 마케팅 예산 스케줄링에 어떻게 반영할 것인가?"**
> - **Answer (Data Fact)**: 안정성 지수가 55% 이상인 **Bargain Hunters**와 **Occasional Buyers**는 저비용의 'Trigger Marketing'이 유효합니다. 반면 안정성이 45% 이하인 **At-Risk** 그룹은 고비용의 'Recovery' 예산을 투입해야 하는 'Red Zone'에 위치해 있습니다.
> - **Evidence**: [Budget Map](plots/deep_dive/q3_budget_map.png)

---

## 🔬 2. 분석 방법론 (Methodology)

### 2.1 수요 예측 및 루틴 검증 알고리즘
- **Prophet Algorithm**: 장기 트렌드와 주간 계절성(Seasonality)이 뚜렷한 품목에 적용.
- **SARIMA Model**: 패턴이 반복적이고 데이터의 안정성이 높은 '루틴 상품'들에 대해 Prophet보다 정교한 예측을 위해 경합 실시.
- **Stabilization Index**: 실제 구매가 모델의 신뢰 구간(95% Confidence Interval) 내에 속하는 비율을 점수화하여 '루틴의 견고함'을 측정.

---

## 📊 3. 분석 결과 및 장표 상세 분석 (Results Deep-Dive)

### 3.1 페르소나별 시계열 안정성 및 대응 전략 (Data Fact)
| 페르소나 (분류 기준) | Stability Score (1 - CV) | 주요 특징 | 비즈니스 액션 (So-What?) |
| :--- | :---: | :--- | :--- |
| **Occasional Buyers** (간헐적 방문) | **58.0% (Highest)** | **Event Driven**: 방문 빈도는 낮지만 특정 시점(월초 등)에 규칙적으로 방문함 | **Calendar Trigger**: 해당 시점에 맞춰 대용량 번들 쿠폰 발송 |
| **Bargain Hunters** (쿠폰 사용 상위 10%) | 57.4% | **Promo Sensitive**: 세일 기간에만 정확히 반응하여 변동성이 오히려 낮음 | **Inventory Spike**: 프로모션 기간 물류 집중 배차 |
| **New/Light Users** (최근 유입, 저구매) | 57.3% | **Initial Routine**: 초기 유입 후 탐색 기간 동안은 정기적 방문 패턴 보임 | **Lock-in**: 초기 3개월 동안 결품 경험 0% 목표 관리 |
| **Regular Shoppers** (중간 빈도/금액) | 50.5% | **Flexible**: 필요에 따라 유연하게 방문하여 예측 불확실성 중간 수준 | **Category Cross-sell**: 비목적 구매 유도로 객단가 변동성 완화 |
| **VIP Champions** (상위 20% 핵심 고객) | 46.4% | **High Freq Variance**: 너무 자주 방문하여(주 2-5회) 요일별 편차가 오히려 큼 | **Basket Maintenance**: 방문 횟수보다 '1회 방문 시 구매량' 유지에 집중 |
| **Loyal Shoppers** (상위 40% 우량 고객) | 46.2% | **Habitual**: VIP와 유사한 고빈도 방문 패턴 보유 | **Refill Reminder**: 예상 재구매 시점 D-1 알림으로 루틴 강화 |
| **At-Risk** (과거 우량, 최근 이탈) | **43.2% (Lowest)** | **Broken Routine**: 방문 주기가 완전히 무너져 예측이 불가능한 상태 | **Re-activation**: 정기 배송/구독 모델 제안으로 강제 루틴 형성 |

### 3.2 시각화 장표 상세 분석 (Presentation Slides)

<details>
<summary><b>📉 Slide 1: VIP의 낮은 안정성 점수에 대한 역설 (The Variance of Volume)</b></summary>

![예측 시각화](plots/ts_persona_forecast.png)

- **핵심 발견**: **VIP Champions**의 안정성 점수(46.4%)가 낮게 나온 것은, 그들이 '불안정'해서가 아니라 **'너무 자주 오기 때문'**입니다. 주 3회 올 때도 있고 주 5회 올 때도 있는 자연스러운 변동 폭이 CV(변동계수)를 높였습니다.
- **So-What?**: VIP 관리의 핵심은 '방문 유도'가 아니라, 방문 시 **'객단가(Basket Size) 유지'**입니다. 그들은 이미 매장에 충분히 자주 오고 있습니다.
</details>

<details>
<summary><b>🚨 Slide 2: [At-Risk] 진짜 위험 신호 감지</b></summary>

![신뢰구간](plots/ts_confidence_interval.png)

- **Data Fact**: **At-Risk** 그룹은 43.2%로 가장 낮은 안정성을 보입니다. 이는 단순히 방문이 줄어드는 것을 넘어, 방문 주기 자체가 완전히 무너졌음을(Chaos) 의미합니다.
- **Action**: 이들에게는 '정기 배송'이나 '요일 지정 쿠폰' 같은 **강제적인 루틴 형성 장치**가 시급합니다.
</details>

<details>
<summary><b>📉 Slide 3: 안정성과 예측 오차의 상관관계 (Model Reliability)</b></summary>

![오차 분포](plots/ts_error_distribution.png)

- **분석**: 안정성 지수(Stability Index)가 높은 그룹일수록 예측 오차(Error)가 낮아지는 강한 음의 상관관계를 보입니다. 
- **비즈니스 가치**: Occasional Buyer나 Bargain Hunter 같은 간헐적 방문객도 데이터 패턴만 확실하다면 AI 예측을 통해 재고 낭비를 획기적으로 줄일 수 있음을 증명합니다.
</details>

### 3.3 핵심 질문 검증을 위한 Deep Dive (KBQ Validation)

<details>
<summary><b>🚨 Q1 Validation: 재고 부족이 초래할 치명적 이탈 위험 (Stock-out Risk)</b></summary>

![재고 리스크](plots/deep_dive/q1_stockout_risk.png)

- **핵심 발견**: 모든 페르소나에서 **'Fluid Milk(우유)'**가 구매 루틴의 가장 강력한 앵커(20~30% 방문 점유율)로 나타났습니다. 
- **Business Impact**: 우유와 같은 '초저관여 생필품'은 고객을 매장으로 끌어들이는 **'강력한 자석'**입니다. 이 품목의 결품은 매장 전체의 신뢰도 저하와 직결되므로, [Stage 3]의 예측 모델을 통해 재고 보충 우선순위 1순위로 관리되어야 합니다.
</details>

<details>
<summary><b>📉 Q2 Validation: 이탈 신호 탐지 (Churn Drift Analysis)</b></summary>

![이탈 신호](plots/deep_dive/q2_churn_signal.png)

- **핵심 발견**: **At-Risk** 그룹(가장 왼쪽 붉은 막대)은 최근 4주간 방문 횟수가 과거 평균 대비 **4회 가까이 감소**했습니다. 
- **Action**: 이 수치가 '-2.0'을 돌파하는 순간이 골든타임입니다. 이때 즉시 CRM 시스템이 작동하여 'Win-back Offer'를 발송해야 합니다.
</details>

<details>
<summary><b>💰 Q3 Validation: 안정성 기반 마케팅 예산 지도 (Budget Map)</b></summary>

![예산 지도](plots/deep_dive/q3_budget_map.png)

- **전략**: 
    - **Green Zone (High Stability)**: 저비용 고효율의 'Trigger 알림'으로 충분합니다.
    - **Yellow Zone (Med Stability)**: **VIP Champions**가 포함된 이 영역은 '유지(Maintenance)'를 위한 혜택 강화가 필요합니다.
    - **Red Zone (Low Stability)**: At-Risk가 위치한 이 영역은 고객을 되살리기 위한 '고비용 프로모션(Recovery)'이 정당화되는 구간입니다.
</details>

---

## 💡 4. 비즈니스 안정화 액션 (Action Plan)

| 실행 과제 | 우선순위 | 기대 효과 | 핵심 KPI |
| :--- | :---: | :--- | :--- |
| **신뢰 구간 기반 자동 발주 시스템** | 🔴 High | 발주 업무 효율성 30% 향상 | MAE (오차율) |
| **페르소나별 '루틴 파괴' 조기 경보** | 🔴 High | VIP 이탈률 12% 감소 | Stabilization Index |
| **프로모션 전용 물류 예측 보정** | 🟠 Medium | 과다 재고 비용 15% 절감 | Inventory Turnover |
| **계절성 상품의 MD 진열 최적화** | 🟡 Low | 시즌 상품 매출 8% 신장 | Seasonal Sales Mix |

---

**전략 보고서 연결**: Discovery(NBA) -> Context(MBA) -> Stabilization(TS)의 전 과정을 거친 고객이 창출하는 최종 비즈니스 가치는 [전략 보고서](../dunnhumby_final_strategic_analysis.md)에 통합되어 정리되어 있습니다.
