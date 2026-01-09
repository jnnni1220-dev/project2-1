import pandas as pd
import os

# Context
input_rules_path = '.\\results\\cross_selling\\cross_selling_rules.csv'
report_path = 'cross_selling_opportunities.md'
plots_dir = 'plots/mba'

print("--- Generating Cross-Selling Report ---")

# Load Rules
try:
    if not os.path.exists(input_rules_path):
        print(f"Error: {input_rules_path} not found. Analysis might not be complete.")
        exit()
    rules = pd.read_csv(input_rules_path)
    print(f"Loaded {len(rules)} rules.")
except Exception as e:
    print(f"Error loading rules: {e}")
    exit()

# Segregate Rules
# 1. Power Bundles: High Support (Mass Appeal) & Good Lift
# Threshold: Top 25% percentile of support
if len(rules) > 10:
    support_thresh = rules['support'].quantile(0.75)
else:
    support_thresh = 0

power_bundles = rules[rules['support'] >= support_thresh].sort_values('lift', ascending=False).head(10)

# 2. Hidden Gems: Lower Support but Very High Lift (Strong niche association)
# Support < Threshold, Lift sorted desc
hidden_gems = rules[rules['support'] < support_thresh].sort_values('lift', ascending=False).head(10)

# Generate Markdown

# --- Load Stability Metric ---
try:
    with open('mba_stability_metric.txt', 'r') as f:
        lines = f.readlines()
        stability_score = lines[0].strip().split(': ')[1]
except:
    stability_score = "N/A"

# Generate Markdown
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# 교차 판매 기회 및 전략 리포트 (Cross-Selling Strategic Report)\n\n")
    
    f.write("## 1. 개요 및 데이터 검증 (Overview & Validation)\n")
    f.write(f"- **분석 목적**: 장바구니 데이터를 통한 동시 구매 패턴 발견 및 객단가 증대 전략 수립.\n")
    f.write(f"- **데이터 검증 (Stability Check)**:\n")
    f.write(f"    - 전체 데이터를 무작위로 두 그룹(A/B)으로 나누어 교차 검증을 수행했습니다.\n")
    f.write(f"    - **안정성 점수 (Overlap Score)**: **{stability_score}**\n")
    f.write("    - 이 점수가 높을수록 발견된 연관 규칙이 특정 기간이나 고객군에 편향되지 않고 일반적임을 의미합니다.\n\n")
    
    f.write("## 2. 시각화 분석 (Visual Analytics)\n")
    f.write("### A. 상품 연관성 네트워크 (Association Network)\n")
    f.write(f"![Network Graph]({plots_dir}/mba_network_graph.png)\n")
    f.write("*중심 노드(Hub)는 여러 상품과 강하게 연결된 '앵커 상품'입니다. 이들을 매장 중심부에 배치하여 동선을 유도하십시오.*\n\n")
    
    f.write("### B. 카테고리 히트맵 (Category Heatmap)\n")
    f.write(f"![Heatmap]({plots_dir}/mba_category_heatmap.png)\n")
    f.write("*카테고리 간의 상호작용 강도를 나타냅니다. 짙은 색일수록 해당 카테고리 간의 교차 구매가 활발합니다.*\n\n")
    
    f.write("### C. 기회 탐색 지도 (Opportunity Map)\n")
    f.write(f"![Scatter Plot]({plots_dir}/mba_scatter_plot.png)\n")
    f.write("*우측 상단(High Support, High Lift)은 확실한 수익원이며, 좌측 상단(Low Support, High Lift)은 잠재력이 높은 틈새 시장입니다.*\n\n")
    
    f.write("## 3. 심층 전략 제언 (Strategic Deep Dive)\n")
    f.write("**[데이터가 말하는 마케팅 전략]**\n")
    f.write("본 분석에서 도출된 **'파워 번들'**과 **'히든 잼'**은 각각 다른 접근 방식이 필요합니다. \n\n")
    f.write("1.  **매스 마케팅 (Mass Marketing) - 파워 번들 활용**:\n")
    f.write("    - 파워 번들은 이미 고객들에게 인지도가 높은 '국민 조합'입니다. 이들은 수익의 기반(Cash Cow)이므로, **'번들 할인(Bundle Pricing)'**보다는 **'편의성(Convenience)'**에 초점을 맞춰야 합니다. \n")
    f.write("    - 예를 들어, 두 상품을 물리적으로 묶어 진열하거나 거리를 좁히는 것만으로도 구매 전환율을 극대화할 수 있습니다. 할인은 최소화하여 마진을 방어하십시오.\n\n")
    f.write("2.  **타겟 마케팅 (Target Marketing) - 히든 잼 활용**:\n")
    f.write("    - 히든 잼은 특정 취향을 가진 고객층에서만 강하게 나타나는 패턴입니다. 이는 **'개인화 추천 알고리즘'**의 핵심 자산이 됩니다. \n")
    f.write("    - 멤버십 데이터를 활용하여 선행 상품(Antecedent)을 구매한 이력이 있는 고객에게 후행 상품(Consequent) 할인 쿠폰을 발송하십시오. 이는 고객으로 하여금 '나를 알아주는 서비스'라는 인식을 심어주어 충성도를 높입니다.\n\n")
    f.write("3.  **매장 레이아웃 최적화 (Store Layout Optimization)**:\n")
    f.write("    - 안정성 점수({stability_score})가 높은 규칙들은 계절이나 유행을 타지 않는 본질적인 구매 패턴입니다. \n")
    f.write("    - 이러한 패턴을 기반으로 매장 내 'Golden Zone'을 재설계하십시오. 연관성이 높은 카테고리를 인접 배치(Cross-Merchandising)하면 고객의 체류 시간을 늘리고 자연스러운 추가 구매를 유도할 수 있습니다.\n\n")
    
    f.write("## 4. Top 10 '파워 번들' (Mass Appeal)\n")
    f.write("| 상품 A | 상품 B | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for _, row in power_bundles.iterrows():
        f.write(f"| {row['antecedents']} | {row['consequents']} | {row['lift']:.2f} | {row['confidence']:.2f} | {row['support']:.4f} |\n")
    f.write("\n")
    
    f.write("## 5. Top 10 '히든 잼' (Niche Targeting)\n")
    f.write("| 상품 A | 상품 B | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for _, row in hidden_gems.iterrows():
        f.write(f"| {row['antecedents']} | {row['consequents']} | {row['lift']:.2f} | {row['confidence']:.2f} | {row['support']:.4f} |\n")

print(f"Report generated: {report_path}")
