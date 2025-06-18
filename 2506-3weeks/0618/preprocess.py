'''
🔧 목표
    ** 직렬 vs 병렬
    1. data/raw/ 폴더의 파일들을 하나씩 읽기
    2. 첫 1,000줄을 읽어서 비었으면 스킵
    3. 진행상황을 로그로 찍기
'''
import pandas as pd
import os
import re
import ray
import numpy as np
import warnings

# 경고 메시지 무시
# warnings.filterwarnings("ignore")

# Ray 시스템 초기화
ray.init(include_dashboard=True)

# 원본 데이터 폴더 경로 설정
RAW_PATH = "data/raw"  # 원본 데이터
PREPROCESS_PATH = "data/processed"  # 전처리된 데이터
# 폴더 없으면 만들어줌, 이미 있어도 에러 x
os.makedirs(RAW_PATH, exist_ok=True)  
os.makedirs(PREPROCESS_PATH, exist_ok=True)

file = os.listdir(RAW_PATH)  # 폴더 내 모든 파일 목록 가져오기
# 전처리 대상 파일만 필터링
    # ex. RAW_PATH(data/raw) + f(file, empty_file.csv) -> data/raw/empty_file.csv
csv_files = [os.path.join(RAW_PATH, f)  
             for f in file 
             if f.endswith('.csv')]

# 전처리 함수
def preprocess(df):
    # 문자열, 특수문자 탐지
    special_pattern = r'[|!@#$%^&*()\-=+[\]{};:\'",.<>/?\\]'
    for col in df.select_dtypes(include=['object', 'string']).columns:
        try:
            # 컬럼에 특수문자 포함된 값이 하나라도 있다면
            if df[col].str.contains(special_pattern, na=False).any():
                # 특수문자 기준으로 문자열 나누기 -> 여러 컬럼으로
                split_cols = df[col].str.split(special_pattern, expand=True)
                # 새로 생긴 컬럼에 이름 지정 ex. col_0, col_1, ...
                split_cols.columns = [f"{col}_{i}" for i in range(split_cols.shape[1])]
                # 기존 컬럼 제거 -> 새로 나뉜 컬럼을 df에 병합
                df = pd.concat([df.drop(columns=[col]), split_cols], axis=1)
        except:
            continue  # 오류 발생하면 무시하고 계속 진행

    # 시간 컬럼 처리
    datetime_cols = []
    for col in df.columns:
        try:
            # 컬럼명이 아닌 값 자체를 보고 datetime 변환이 가능한지 판단
            # 날짜 변환에 실패한 값은 NaT(Not a Time)로 처리 = 날짜처럼 안 생긴 값은 버림
            parsed = pd.to_datetime(df[col], errors='coerce')
            # 변환된 결과 중에서 NaT가 아닌 값 개수를 셈
            # 대부분 날짜/시간처럼 생긴 값이라는 것에 대한 판단
            if parsed.notna().sum() > len(df) * 0.5:
                datetime_cols.append(col)  # 진짜 datetime으로 판단된 컬럼명 리스트에 저장
                df[col] = parsed
                df[f'{col}_date'] = df[col].dt.date  # 변환된 datetime에서 날짜 부분만 분리해서 새 컬럼 생성
                df[f'{col}_time'] = df[col].dt.hour  # 변환된 datetime에서 시간만 분리해서 새 컬럼 생성
        except:
            continue
                
    # 이상치 처리
    for col in df.select_dtypes(include=['number']).columns:
        # -1000보다 작거나 1000000보다 큰 값 -> 이상치, NaN으로 처리
        df[col] = df[col].apply(lambda x: np.nan if x < -1000 or x > 1e6 else x)
        
    # 결측치 처리
    df = df.fillna(0)
    
    return df

@ray.remote  # 병렬 처리 가능
def process_file(file_path):
    warnings.filterwarnings("ignore", message="Could not infer format")
    filename = os.path.basename(file_path)  # 파일 이름만 추출
    output_path = os.path.join(PREPROCESS_PATH, filename)  # 전처리된 파일 경로
    # 컬럼, 데이터가 없는 빈 파일
    if os.path.getsize(file_path) == 0:
        return f"[Skip] Empty file(0 byte): {filename}"
        
    try:
        # 첫 1000줄만 읽기 (대용량 대비)
        df = pd.read_csv(file_path, nrows=1000)  
        
        if df.empty:  # 컬럼은 있지만 데이터가 없는 경우
            return f"[SKIP] No data rows: {filename}"
        
        # 파일이 열렸고, 유효한 데이터가 있을 때 전처리 수행
        df = preprocess(df)
        df.to_csv(output_path, index=False)  # 전처리 파일 저장
        
        # 정상 파일일 경우 간단 통계 출력
        return f"[OK] {filename}: shape={df.shape}, columns={df.columns.tolist()}"
            
    except Exception as e:
        return f"[ERROR] failed to read {filename}: {e}"

features = [process_file.remote(path) for path in csv_files]
results = ray.get(features)

with open("log.txt", "a") as f:
    for res in results:    
        f.write(f"{res}\n")
        print(res)
    
    
    
# ------직렬 처리------
# # 파일 순차 처리
# for filename in csv_files:
#     file_path = os.path.join(RAW_PATH, filename)  # 파일 경로 생성
#     print(f"[INFO] Processing: {filename}")  # 현재 처리 중인 파일 출력
    
#     # 컬럼, 데이터가 없는 빈 파일
#     if os.path.getsize(file_path) == 0:
#         print(f"[Skip] Empty file(0 byte): {filename}")  
#         continue 
        
#     try:
#         # 첫 1000줄만 읽기 (대용량 대비)
#         df = pd.read_csv(file_path, nrows=1000)  
        
#         if df.empty:  # 컬럼은 있지만 데이터가 없는 경우
#             print(f"[SKIP] No data rows: {filename}")
#             continue
        
#         # 정상 파일일 경우 간단 통계 출력
#         print(f"[OK] {filename}: shape={df.shape}, columns={df.columns.tolist()}")  
            
#     except Exception as e:
#         print(f"[ERROR] failed to read {filename}: {e}")
