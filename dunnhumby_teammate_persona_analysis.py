
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Paths
INPUT_FILE = 'dunnhumby_integrated_data.csv'
OUTPUT_FILE = 'dunnhumby_persona_segments.csv'
PLOTS_DIR = 'dunnhumby_plots'
os.makedirs(PLOTS_DIR, exist_ok=True)

print("--- Dunnhumby Teammate Persona Analysis: 7-Persona Classification ---")

try:
    # 1. Load Data
    df = pd.read_csv(INPUT_FILE)
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Analysis Snapshot Date (Current perspective)
    max_date = df['OrderDate'].max()
    print(f"Latest Transaction Date: {max_date}")

    # 2. RFM + Coupon Metrics Calculation
    # Note: Using distinct BASKET_ID for Frequency, TotalAmount for Monetary
    rfm = df.groupby('CustomerID').agg({
        'OrderDate': lambda x: (max_date - x.max()).days,  # Recency
        'BASKET_ID': 'nunique',                           # Frequency
        'TotalAmount': 'sum',                             # Monetary
        'Quantity': 'sum',                                # Total quantity
        'CouponDiscount': lambda x: (x < 0).sum()         # Coupon count (negative values in Dunnhumby)
    }).reset_index()

    rfm.columns = ['CustomerID', 'recency', 'frequency', 'monetary', 'total_quantity', 'coupon_count']

    # 3. Derived Metrics
    rfm['avg_basket_value'] = rfm['monetary'] / rfm['frequency']
    rfm['coupon_rate'] = (rfm['coupon_count'] / rfm['frequency'] * 100).round(2)

    # 4. RFM Scoring (1-5, quintiles)
    # Using 'duplicates=drop' for robustness, mapping to 1-5
    rfm['R_score'] = pd.qcut(rfm['recency'].rank(method='first'), q=5, labels=[5,4,3,2,1]).astype(int)
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)
    
    # Coupon usage score (for reference)
    rfm['C_score'] = pd.qcut(rfm['coupon_rate'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)

    # 5. Teammate's Persona Assignment Logic
    def assign_persona(row):
        R, F, M = row['R_score'], row['F_score'], row['M_score']
        coupon_rate = row['coupon_rate']
        
        # 1. VIP Champions: High Recency, Frequency, Monetary (R>=4, F>=4, M>=4)
        if R >= 4 and F >= 4 and M >= 4:
            return 'VIP Champions'
        # 2. Loyal Shoppers: Good Recency, Frequency, Monetary (R>=3, F>=3, M>=3)
        elif R >= 3 and F >= 3 and M >= 3:
            return 'Loyal Shoppers'
        # 3. Regular Shoppers: Active but moderate frequency/value (R>=3, F>=2, M>=2)
        elif R >= 3 and F >= 2 and M >= 2:
            return 'Regular Shoppers'
        # 4. At-Risk: High history but low recency (R<=2, F>=3, M>=3)
        elif R <= 2 and F >= 3 and M >= 3:
            return 'At-Risk'
        # 5. New/Light Users: Recent but low frequency/value (R>=4, F<=2, M<=2)
        elif R >= 4 and F <= 2 and M <= 2:
            return 'New/Light Users'
        # 6. Bargain Hunters: Top 10% coupon usage rate
        elif coupon_rate >= rfm['coupon_rate'].quantile(0.90):
            return 'Bargain Hunters'
        # 7. Occasional Buyers: The rest
        else:
            return 'Occasional Buyers'

    rfm['persona'] = rfm.apply(assign_persona, axis=1)

    # 6. Output & Visualization
    print("\n--- Persona Distribution ---")
    persona_counts = rfm['persona'].value_counts()
    print(persona_counts)

    # Plot Distribution
    plt.figure(figsize=(12, 6))
    sns.barplot(x=persona_counts.index, y=persona_counts.values, palette='magma')
    plt.title('Teammate-based 7 Persona Distribution', fontsize=16)
    plt.xticks(rotation=45)
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'dunnhumby_teammate_persona_dist.png'))
    plt.close()

    # Persona Characteristics Table
    summary = rfm.groupby('persona').agg({
        'CustomerID': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'coupon_rate': 'mean'
    }).round(2)
    summary.columns = ['Count', 'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Avg_Coupon_Rate (%)']
    print("\n--- Persona Characteristics ---")
    print(summary.sort_values('Avg_Monetary', ascending=False))

    # Save segments
    rfm.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved segments to {OUTPUT_FILE}")
    print(f"Saved plot to {PLOTS_DIR}/dunnhumby_teammate_persona_dist.png")

except Exception as e:
    print(f"Error during persona analysis: {e}")
