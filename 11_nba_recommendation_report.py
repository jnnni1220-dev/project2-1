
import pandas as pd
import os

print("--- Starting NBA Recommendation Report Generation ---")

# 1. Load Data
nba_path = r'results/nba_recommendations.csv'
if not os.path.exists(nba_path):
    print(f"Error: {nba_path} not found. Please run collaborative filtering first.")
    exit()

df_nba = pd.read_csv(nba_path)

# 2. Analyze Recommendations
# Split the recommendations string and explode to count occurrences
recs_series = df_nba['recommendations'].str.split(', ')
all_recs = [item for sublist in recs_series for item in sublist]
rec_counts = pd.Series(all_recs).value_counts().head(10)

# 3. Create Markdown Report
report_content = f"""# NBA (Next Best Action) Recommendation Report

## 1. Overview
This report summarizes the personalized product recommendations generated using User-Based Collaborative Filtering.

### Methodology
- **Input Data:** Household purchase history (Commodity Level).
- **Similarity Measure:** Cosine Similarity between households.
- **Algorithm:** User-Based Collaborative Filtering (Top 10 similar users used for weighting).
- **Filtering:** Items already purchased by the household are excluded.

## 2. Recommendation Summary
- **Total Households Sampled:** {len(df_nba)}
- **Top 10 Most Recommended Categories:**

| Category | Frequency |
| :--- | :--- |
"""

for category, count in rec_counts.items():
    report_content += f"| {category} | {count} |\n"

report_content += """
## 3. Sample Recommendations
| Household Key | Recommendations |
| :--- | :--- |
"""

for _, row in df_nba.head(5).iterrows():
    report_content += f"| {row['household_key']} | {row['recommendations']} |\n"

report_content += """
## 4. Strategic Insights
- **Cross-Selling Opportunities:** The system identifies products that similar high-value customers are purchasing, providing clear cross-selling opportunities.
- **Personalization:** Recommendations are unique to each household's historical behavior and the behavior of their "twins" in the dataset.
"""

# 4. Save Report
output_path = 'nba_recommendation_report.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"Report saved to {output_path}")
print("--- NBA Recommendation Report Generation Finished ---")
