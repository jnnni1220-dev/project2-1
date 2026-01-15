# Dunnhumby 가구별 개인화 추천 상세 보고서

## 1. 하이브리드 추천 엔진 설계 방법론 (Methodology)
본 추천 시스템은 개별 고객에게 가장 유의미한 상품을 제안하기 위해 두 가지 핵심 필터링 기법을 가중 결합(Weighting)했습니다.

- **필터링 로직**:
    1. **협업 필터링 (Collaborative Filtering, 70%)**: 아이템-아이템 유사도를 기반으로, 특정 상품을 구매한 고객과 유사한 구매 패턴을 가진 타 구매자들의 데이터를 분석합니다.
    2. **콘텐츠 기반 필터링 (Content-Based, 30%)**: 상품명과 카테고리의 텍스트 데이터를 TF-IDF로 벡터화하여, 고객이 과거에 구매했던 상품과 물리적으로 유사한 속성을 가진 상품을 추천합니다.
- **콜드 스타트 방지**: 신규 고객이나 데이터가 부족한 경우에도 카테고리 유사성을 통해 최소한의 추천 품질을 유지하도록 설계되었습니다.
- **추천 근거 (Explainability)**: 각 추천 결과에 대해 어떤 과거 구매 상품이 핵심적인 영향을 미쳤는지를 데이터 기반으로 기술하여 마케팅 담당자의 이해를 돕습니다.

## 2. 모델 성능 및 분석 지표
- **추천 다양성 (Category Diversity)**: Recommendation Diversity (Category): 1.00%
- **분석 대상 고객 수**: Sample Customers Analyzed: 100
- **하이브리드 가중치**: Hybrid Weights: CF(0.7), CB(0.3)

## 3. 가구별 상세 추천 리스트 (Top 5 Recommendations)
| 고객 ID | 추천 순위 | 추천 상품명 | 추천 점수 | 추천 근거 (Reason) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 1위 | EGGS - X-LARGE | 14.128 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 1 | 2위 | POTATOES RUSSET (BULK&BAG) | 13.130 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 1 | 3위 | HOT DOG BUNS | 12.819 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 1 | 4위 | GRAPES RED | 12.692 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 1 | 5위 | GRAPES WHITE | 12.646 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 2 | 1위 | EGGS - X-LARGE | 18.770 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 2 | 2위 | PRIMAL | 17.721 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 2 | 3위 | ONIONS YELLOW (BULK&BAG) | 16.975 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 2 | 4위 | CELERY | 16.870 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 2 | 5위 | LEAN | 16.715 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 3 | 1위 | POTATOES RUSSET (BULK&BAG) | 22.197 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 3 | 2위 | EGGS - X-LARGE | 21.045 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 3 | 3위 | IWS SINGLE CHEESE | 20.907 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 3 | 4위 | FLUID MILK WHITE ONLY | 20.464 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 3 | 5위 | SHREDDED CHEESE | 19.937 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 4 | 1위 | HAMBURGER BUNS | 6.549 | 'GRATED CHEESE' 구매 패턴 및 유사 카테고리 기반 |
| 4 | 2위 | EGGS - X-LARGE | 6.460 | 'GRATED CHEESE' 구매 패턴 및 유사 카테고리 기반 |
| 4 | 3위 | PRIMAL | 6.455 | 'GRATED CHEESE' 구매 패턴 및 유사 카테고리 기반 |
| 4 | 4위 | HOT DOG BUNS | 6.404 | 'GRATED CHEESE' 구매 패턴 및 유사 카테고리 기반 |
| 4 | 5위 | SHREDDED CHEESE | 6.064 | 'GRATED CHEESE' 구매 패턴 및 유사 카테고리 기반 |
| 5 | 1위 | HOT DOG BUNS | 4.139 | 'RAMEN NOODLES/RAMEN CUPS' 구매 패턴 및 유사 카테고리 기반 |
| 5 | 2위 | PRIMAL | 4.078 | 'RAMEN NOODLES/RAMEN CUPS' 구매 패턴 및 유사 카테고리 기반 |
| 5 | 3위 | FLUID MILK WHITE ONLY | 4.042 | 'RAMEN NOODLES/RAMEN CUPS' 구매 패턴 및 유사 카테고리 기반 |
| 5 | 4위 | HAMBURGER BUNS | 3.971 | 'RAMEN NOODLES/RAMEN CUPS' 구매 패턴 및 유사 카테고리 기반 |
| 5 | 5위 | POTATOES RUSSET (BULK&BAG) | 3.961 | 'RAMEN NOODLES/RAMEN CUPS' 구매 패턴 및 유사 카테고리 기반 |
| 6 | 1위 | HOT DOG BUNS | 21.161 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 6 | 2위 | CUCUMBERS | 21.003 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 6 | 3위 | POTATOES RUSSET (BULK&BAG) | 20.639 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 6 | 4위 | ONIONS SWEET (BULK&BAG) | 19.945 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 6 | 5위 | HAMBURGER BUNS | 19.937 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 7 | 1위 | POTATOES RUSSET (BULK&BAG) | 16.735 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 7 | 2위 | HOT DOG BUNS | 16.693 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 7 | 3위 | EGGS - X-LARGE | 16.483 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 7 | 4위 | EGGS - LARGE | 15.752 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 7 | 5위 | MAINSTREAM WHITE BREAD | 15.215 | 'ORANGES NAVELS ALL' 구매 패턴 및 유사 카테고리 기반 |
| 8 | 1위 | IWS SINGLE CHEESE | 30.916 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 8 | 2위 | GRAPES WHITE | 28.808 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 8 | 3위 | SHREDDED CHEESE | 27.035 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 8 | 4위 | HEAD LETTUCE | 26.993 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 8 | 5위 | PRIMAL | 26.693 | 'PASTA: CANNED' 구매 패턴 및 유사 카테고리 기반 |
| 9 | 1위 | POTATOES RUSSET (BULK&BAG) | 8.270 | 'HAMBURGER BUNS' 구매 패턴 및 유사 카테고리 기반 |
| 9 | 2위 | PRIMAL | 7.980 | 'HAMBURGER BUNS' 구매 패턴 및 유사 카테고리 기반 |
| 9 | 3위 | EGGS - X-LARGE | 7.884 | 'HAMBURGER BUNS' 구매 패턴 및 유사 카테고리 기반 |
| 9 | 4위 | CORN | 7.741 | 'HAMBURGER BUNS' 구매 패턴 및 유사 카테고리 기반 |
| 9 | 5위 | LEAN | 7.739 | 'HAMBURGER BUNS' 구매 패턴 및 유사 카테고리 기반 |
| 10 | 1위 | HOT DOG BUNS | 3.718 | 'CHEESE: PROCESSED BULK' 구매 패턴 및 유사 카테고리 기반 |
| 10 | 2위 | LEAN | 3.649 | 'CHEESE: PROCESSED BULK' 구매 패턴 및 유사 카테고리 기반 |
| 10 | 3위 | POTATOES RUSSET (BULK&BAG) | 3.610 | 'CHEESE: PROCESSED BULK' 구매 패턴 및 유사 카테고리 기반 |
| 10 | 4위 | MAINSTREAM WHITE BREAD | 3.476 | 'CHEESE: PROCESSED BULK' 구매 패턴 및 유사 카테고리 기반 |
| 10 | 5위 | SUGAR | 3.393 | 'CHEESE: PROCESSED BULK' 구매 패턴 및 유사 카테고리 기반 |

## 4. 마케팅 실행 가이드
- **단계 1 (초개인화)**: 최상위 추천 상품(1위)에 대해 '당신만을 위한 추천 상품' 메시지 발송.
- **단계 2 (교차 구매)**: 추천 상품군이 기존 구매 카테고리와 다른 경우, 해당 카테고리 진입 유도를 위한 소액 할인권 배치.

---
*원천 데이터셋 정보: dunnhumby_integrated_data.csv / 분석 수행일: 2025-05-22*
