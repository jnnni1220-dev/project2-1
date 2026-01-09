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
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# 교차 판매 기회 리포트 (Cross-Selling Opportunities)\n\n")
    
    f.write("## 1. 요약 (Executive Summary)\n")
    f.write(f"- **목적**: 장바구니 크기(객단가) 증대를 위한 고잠재력 상품 번들(조합) 발굴.\n")
    f.write(f"- **방법론**: 상위 50개 인기 상품 및 50만 건 샘플 데이터를 활용한 장바구니 분석 (Apriori 알고리즘, {len(rules)}개 규칙 도출).\n")
    f.write(f"- **핵심 결과**: 대중적인 **'파워 번들' {len(power_bundles)}개**와 틈새 시장을 위한 **'히든 잼' {len(hidden_gems)}개** 조합 발견.\n\n")
    
    f.write("## 2. 시각화 개요 (Visual Overview)\n")
    f.write("### 상품 연관성 네트워크 (Product Association Network)\n")
    f.write(f"![Network Graph]({plots_dir}/mba_network_graph.png)\n")
    f.write("*Fig 1. 주요 상품(Hub)과 강한 연결 관계 시각화 (선이 굵을수록 연관성 높음)*\n\n")
    
    f.write("### 기회 지도 (Opportunity Map: Support vs Lift)\n")
    f.write(f"![Scatter Plot]({plots_dir}/mba_scatter_plot.png)\n")
    f.write("*Fig 2. 규칙 세분화. 우측 상단일수록 최상의 기회 요소임.*\n\n")
    
    f.write("## 3. Top 10 '파워 번들' (대중적 인기 조합)\n")
    f.write("발생 빈도(Support)가 높고 연관성(Lift)도 강한 조합입니다. **전략**: 트래픽이 많은 매대나 메인 페이지에 '함께 구매하면 좋은 상품'으로 배치하세요.\n\n")
    f.write("| 상품 A (Antecedent) | 상품 B (Consequent) | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for _, row in power_bundles.iterrows():
        f.write(f"| {row['antecedents']} | {row['consequents']} | {row['lift']:.2f} | {row['confidence']:.2f} | {row['support']:.4f} |\n")
    f.write("\n")
    
    f.write("## 4. Top 10 '히든 잼' (틈새 타겟팅)\n")
    f.write("전체 발생 빈도는 낮지만, 구매 시 함께 살 확률이 매우 높은 강력한 조합입니다. **전략**: 계산대에서의 개인화 추천이나 타겟 쿠폰 발송에 활용하세요.\n\n")
    f.write("| 상품 A (Antecedent) | 상품 B (Consequent) | 향상도 (Lift) | 신뢰도 (Confidence) | 지지도 (Support) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for _, row in hidden_gems.iterrows():
        f.write(f"| {row['antecedents']} | {row['consequents']} | {row['lift']:.2f} | {row['confidence']:.2f} | {row['support']:.4f} |\n")
    f.write("\n")
    
    f.write("## 5. 전략적 제언 (Strategic Recommendations)\n")
    f.write("1. **번들 프로모션**: 위 '파워 번들' 상품군에 대해 'A 구매 시 B 10% 할인'과 같은 행사를 기획하십시오.\n")
    f.write("2. **매장 레이아웃**: 네트워크 그래프에서 식별된 'Hub Product'(중심 상품) 주변에 연관 상품을 근접 배치하십시오.\n")
    f.write("3. **개인화 마케팅**: '히든 잼' 조합을 활용하여, 최근 상품 A를 구매한 고객에게 상품 B에 대한 타겟 메시지를 발송하십시오.\n")

print(f"Report generated: {report_path}")
