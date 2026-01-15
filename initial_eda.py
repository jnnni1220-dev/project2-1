
import pandas as pd
import numpy as np

try:
    df = pd.read_csv('Amazon.csv')

    print("--- 데이터 기본 정보 ---")
    print(f"데이터 형태 (행, 열): {df.shape}")
    print("\n--- 컬럼별 데이터 타입 및 결측치 ---")
    df.info()

    print("\n\n--- 데이터 샘플 (상위 5개) ---")
    print(df.head())

    print("\n\n--- 숫자형 데이터 기술 통계 ---")
    print(df.describe())

    print("\n\n--- 컬럼별 결측치 개수 ---")
    print(df.isnull().sum())

    print(f"\n\n--- 전체 중복된 행 개수 ---")
    print(df.duplicated().sum())

except FileNotFoundError:
    print("오류: 'Amazon.csv' 파일을 찾을 수 없습니다. 파일이 현재 디렉토리에 있는지 확인해주세요.")
except Exception as e:
    print(f"데이터 분석 중 오류가 발생했습니다: {e}")
