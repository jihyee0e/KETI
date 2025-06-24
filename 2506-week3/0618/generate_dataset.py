'''
data/raw/ 폴더에 5개의 CSV 파일 생성
목적: 전처리 실습에서 다양한 케이스를 포괄

1) normal - 일반 로딩, 시간 처리
🔍 구성
- 200행, 3개 컬럼: id, value, time
- value: 정수형 (10~99)
- time: 시간 데이터 (2023-01-01 00:00:00부터 1시간 단위)
💡 전처리 연습 포인트
- 일반적인 파일 로딩 (pd.read_csv)
- time 컬럼 → datetime 변환 후 파생 변수 만들기 (dt.hour, dt.date 등)
- 통계 요약 가능 (value.mean(), describe() 등)

2) pipe - 문자열 분해, 컬럼 확장
🔍 구성
- 200행, 3개 컬럼: id, info, extra
- info: 파이프 문자 포함된 문자열 (1|2|3, 2|3|4, ...)
- extra: 0~1 사이 실수
💡 전처리 연습 포인트
- info → .str.split('|', expand=True)로 분해
- 각 분해된 열을 새 컬럼으로 병합
- 문자열 .strip() 및 정수형 변환 등 추가 처리

3) incons - 컬럼 정규화, 누락 컬럼 생성
🔍 구성
- 150행, 2개 컬럼: name, score
- 다른 파일과 컬럼 수 다름
💡 전처리 연습 포인트
- 컬럼 수 정규화
    → 기준 컬럼 리스트로 맞추기 (누락 컬럼 생성 + 0으로 채움)
- 정렬 순서 통일 (df = df[standard_columns])
- score에 이상치 있는지 판단 가능

4) noisy - 이상치/결측/시간 처리
🔍 구성
- 200행, 2개 컬럼: value, time
- value에는 다음 포함:
- NaN, 이상치 9999, -100
💡 전처리 연습 포인트
- 이상치 제거 함수 만들기
- 조건 기반 (<0, >1000) 또는 Z-score, IQR 등
- 결측치 처리 (fillna(0), 또는 제거)
- time 처리 가능

5) empty - 빈 파일 처리, 로깅
🔍 구성
- 0행, 0열 → 완전 빈 CSV
💡 전처리 연습 포인트
- 첫 배치 판단 (if df.empty: or if len(df) == 0)
- try-except 또는 검사 함수 작성해서 스킵 처리
- 로그 출력: "빈 파일로 판단됨: empty_file.csv"
'''

import pandas as pd
import numpy as np
import os

os.makedirs("data/raw", exist_ok=True)

# 정상 데이터 - 200개
normal = pd.DataFrame({
    'id': range(1, 201),
    'value': np.random.randint(10, 100, 200),
    'time': pd.date_range('2023-01-01', periods=200, freq='H')
})
normal.to_csv("data/raw/normal_data.csv", index=False)

# 파이프 문자 포함 열 - ` 포함된 문자열 열, 200개
pipe = pd.DataFrame({
    'id': range(201, 401),
    'info': [f"{x}|{x+1}|{x+2}" for x in range(1, 201)],
    'extra': np.random.rand(200)
})
pipe.to_csv("data/raw/pipe_column.csv", index=False)

# 컬럼 수 다른 파일 - 150개
incons = pd.DataFrame({
    'name': [f"name_{i}" for i in range(1, 151)],
    'score': np.random.randint(60, 100, 150)
})
incons.to_csv("data/raw/inconsistent_cols.csv", index=False)

# 이상치 + 결측 포함 - 200개
values = [1, 2, 3, np.nan, 9999, 5, -100] * 30
noisy = pd.DataFrame({
    'value': values[:200],
    'time': pd.date_range('2023-02-01', periods=200, freq='H')
})
noisy.to_csv("data/raw/noisy_data.csv", index=False)

# 빈 파일
open("data/raw/empty_file.csv", 'w').close()
