# NBA (Next Best Action) Recommendation Report

## 1. Overview
This report summarizes the personalized product recommendations generated using User-Based Collaborative Filtering.

### Methodology
- **Input Data:** Household purchase history (Commodity Level).
- **Similarity Measure:** Cosine Similarity between households.
- **Algorithm:** User-Based Collaborative Filtering (Top 10 similar users used for weighting).
- **Filtering:** Items already purchased by the household are excluded.

## 2. Recommendation Summary
- **Total Households Sampled:** 100
- **Top 10 Most Recommended Categories:**

| Category | Frequency |
| :--- | :--- |
| YOGURT | 18 |
| FROZEN PIZZA | 12 |
| BAKED SWEET GOODS | 11 |
| BEEF | 11 |
| COLD CEREAL | 10 |
| CAT FOOD | 9 |
| ISOTONIC DRINKS | 9 |
| CONVENIENT BRKFST/WHLSM SNACKS | 9 |
| HISPANIC | 9 |
| FRZN MEAT/MEAT DINNERS | 9 |

## 3. Sample Recommendations
| Household Key | Recommendations |
| :--- | :--- |
| 1 | YOGURT, FROZEN PIZZA, DINNER SAUSAGE, ISOTONIC DRINKS, CHICKEN |
| 2 | MEAT - SHELF STABLE, BEANS - CANNED GLASS & MW, DRY SAUCES/GRAVY, IMPORTED WINE, CAT FOOD |
| 3 | FRZN NOVELTIES/WTR ICE, EGGS, PWDR/CRYSTL DRNK MX, DOG FOODS, BEANS - CANNED GLASS & MW |
| 4 | SOUP, YOGURT, HAIR CARE PRODUCTS, HOUSEHOLD CLEANG NEEDS, PASTA SAUCE |
| 5 | SOFT DRINKS, BAKED SWEET GOODS, CONVENIENT BRKFST/WHLSM SNACKS, COLD CEREAL, YOGURT |

## 4. Strategic Insights
- **Cross-Selling Opportunities:** The system identifies products that similar high-value customers are purchasing, providing clear cross-selling opportunities.
- **Personalization:** Recommendations are unique to each household's historical behavior and the behavior of their "twins" in the dataset.
