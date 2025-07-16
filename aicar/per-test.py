import zipfile
import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 기준 컬럼 추출 함수
# zip 파일 내 특정 CSV 파일을 열어 기준 컬럼 목록을 set 형태로 반환
def get_standard_columns(zip_path, sample_file):
    with zipfile.ZipFile(zip_path) as z:
        with z.open(sample_file) as f:
            # sep="|": 파이프 구분자 사용
            # skipinitialspace=True: 구분자 뒤 공백 제거
            # skiprows=1: 첫 행(-----+ 같은 의미 없는 줄) 제거
            # nrows=5: 샘플 5줄만 읽음 (성능 부담 줄이기)
            df = pd.read_csv(f, sep="|", skipinitialspace=True, skiprows=1, nrows=5)
            return set(df.columns.str.strip())  # 컬럼 이름 앞뒤 공백 제거 후 set 반환

# 전체 CSV 파일 반복하면서 컬럼 구조 비교
# 기준 컬럼과 다르면 예외 리스트에 (파일명, 컬럼 목록 또는 에러 메시지) 추가
def compare_all_csv_columns(zip_path, standard_columns):
    exceptions = []  # 예외 파일 저장용 리스트
    with zipfile.ZipFile(zip_path) as z:
        for fname in z.namelist():
            if not fname.endswith('.csv'):
                continue  # CSV가 아닌 파일은 무시
            try:
                with z.open(fname) as f:
                    # skiprows=1 사용 이유: 첫 줄이 '------+' 같은 불필요한 구분줄인 경우 방지
                    df = pd.read_csv(f, sep="|", skipinitialspace=True, skiprows=1, nrows=1)
                    current_cols = set(df.columns.str.strip())  # 현재 파일 컬럼 set으로 정리
                    if current_cols != standard_columns:
                        exceptions.append((fname, list(current_cols)))  # 컬럼 다르면 기록
            except Exception as e:
                # 파일이 아예 열리지 않거나 파싱 실패한 경우 에러 메시지 기록
                exceptions.append((fname, f"읽기 실패: {e}"))
    return exceptions  # 예외 파일 리스트 반환

# 메인 실행 흐름 - zip 하나 지정해서 처리
zip_path = os.getenv("SINGLE_ZIP_PATH")

if not zip_path:
    raise ValueError("SINGLE_ZIP_PATH 환경변수가 설정되지 않았습니다.")

# zip 하나 열고 .csv 파일 추출, 대표 파일 선택
with zipfile.ZipFile(zip_path) as z:
    # zip 내부 모든 파일 중 .csv 파일만 필터링
    csv_files = [f for f in z.namelist() if f.endswith('.csv')]
    
    # 기준 컬럼 추출용 대표 파일 1개 선택 - 여기서는 1번째 파일을 기준
    sample_file = csv_files[0]

    # 기준 컬럼 목록 추출
    standard_columns = get_standard_columns(zip_path, sample_file)
    # 기준 컬럼 출력
    print(f"[기준 컬럼 수]: {len(standard_columns)}개")
    print("[기준 컬럼 목록]:", sorted(standard_columns))

    # 전체 파일 컬럼 구조 비교
    exceptions = compare_all_csv_columns(zip_path, standard_columns)

    # 전체 .csv 파일 개수 기준으로 예외 출력
    total_csv_files = len(csv_files)
    num_exceptions = len(exceptions)
    # 예외 결과 출력
    print(f"\n[예외 파일 수]: {num_exceptions}개 / 전체 {total_csv_files}개")

    # 예외가 많을 수 있으니 처음 5개만 출력
    for fname, info in exceptions[:5]:
        print(f" - {fname}: {info}")

    with zipfile.ZipFile(zip_path) as z:
        for fname, _ in exceptions:
            print(f"\n--- {fname} ---")
            try:
                with z.open(fname) as f:
                    raw = f.read()  
                    print(f"[길이: {len(raw)} bytes]")
                    print(raw.decode('utf-8', errors='replace')[:1000])  # 앞 1000자만 미리보기 -> 두 파일 모두 빈 내용 출력 = 파일 자체는 존재하지만 내용 없음
            except Exception as e:
                print(f"[열기 실패] {e}")
