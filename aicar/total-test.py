import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO
from io import StringIO
from dotenv import load_dotenv
import re
import os

# .env 파일 로드
load_dotenv()

# 환경변수에서 ZIP 경로 가져오기 (기본값: ./data)
base_dir = Path(os.getenv("ZIP_DATA_DIR", "data"))
zip_paths = list(base_dir.rglob("*.zip"))

log_lines = []  # 로그를 담을 리스트

def is_underline(line):
    # 밑줄(---+---+---) 패턴이면 True
    return bool(re.match(r"^[-+ ]+$", line.strip()))

# 로그를 터미널과 log_lines 양쪽에 출력하는 함수
def log_and_print(line):
    print(line)
    log_lines.append(line)

# 기준 컬럼 추출 함수
# zip 파일 내 특정 CSV 파일을 열어 기준 컬럼 목록을 set 형태로 반환
def get_standard_columns_from_zip(zip_file: zipfile.ZipFile, sample_file: str):
    with zip_file.open(sample_file) as f:
        # sep="|": 파이프 구분자 사용
        # skipinitialspace=True: 구분자 뒤 공백 제거
        # skiprows=1: 첫 행(-----+ 같은 의미 없는 줄) 제거
        # nrows=5: 샘플 5줄만 읽음 (성능 부담 줄이기)
        df = pd.read_csv(f, sep="|", skipinitialspace=True, skiprows=1, nrows=5)
        return set(df.columns.str.strip())  # 컬럼 이름 앞뒤 공백 제거 후 set 반환

# zip 내부 CSV 파일들의 컬럼 구조 비교
# 기준 컬럼과 다르면 예외 리스트에 (파일명, 컬럼 목록 또는 에러 메시지) 추가
def compare_all_csv_columns(zip_file: zipfile.ZipFile, standard_columns: set):
    exceptions = []
    for fname in zip_file.namelist():
        # .csv 확장자면서 Mac 시스템 파일은 제외
        if (
            not fname.endswith('.csv')
            or '__MACOSX/' in fname
            or '/._' in fname
        ):
            continue
        try:
            with zip_file.open(fname) as f:
                df = pd.read_csv(f, sep="|", skipinitialspace=True, skiprows=1, nrows=1)
                current_cols = set(df.columns.str.strip())
                if current_cols != standard_columns:
                    exceptions.append((fname, list(current_cols)))
        except Exception as e:
            exceptions.append((fname, f"읽기 실패: {e}"))
    return exceptions

# zip 파일 내부 zip까지 모두 재귀적으로 처리
def process_zip_file(zip_bytes: bytes, zip_name: str):
    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as z:
            # .csv 파일 수집
            csv_files = [
                f for f in z.namelist()
                if f.endswith('.csv')
                and '__MACOSX/' not in f
                and '/._' not in f
            ]

            # .csv가 없다면 → 내부 .zip 확인
            if not csv_files:
                inner_zips = [f for f in z.namelist() if f.endswith('.zip')]
                if not inner_zips:
                    log_and_print(f"[{zip_name}] - CSV도 없고 내부 ZIP도 없음")
                    return
                for inner_zip_name in inner_zips:
                    try:
                        inner_bytes = z.read(inner_zip_name)
                        process_zip_file(inner_bytes, zip_name + "::" + inner_zip_name)
                    except Exception as e:
                        log_and_print(f"[내부 ZIP 열기 실패] {zip_name}::{inner_zip_name}: {e}")
                return

            # 기준 컬럼 추출
            sample_file = csv_files[0]
            try:
                standard_columns = get_standard_columns_from_zip(z, sample_file)
            except Exception as e:
                log_and_print(f"[기준 컬럼 추출 실패] {zip_name}::{sample_file}: {e}")

                # try:
                #     raw = z.read(sample_file)  # 한 번만 read
                #     buffer = BytesIO(raw)
                #     buffer.seek(0)
                #     lines = buffer.read().decode('utf-8', errors='replace').splitlines()
                #     filtered = [line for line in lines if not is_underline(line)]
                #     try:
                #         # sep=None, engine="python"으로 구분자 자동 감지
                #         df_try = pd.read_csv(StringIO('\n'.join(filtered)), sep=None, engine="python", skipinitialspace=True, skiprows=1, nrows=5, on_bad_lines='skip')
                #         log_and_print("[미리보기]")
                #         log_and_print(df_try.head().to_string(index=False))
                #     except Exception as parse_error:
                #         log_and_print(f"[read_csv() 실패] {parse_error}")
                #         log_and_print(f"[길이: {len(raw)} bytes]")
                #         buffer.seek(0)
                #         preview = buffer.read(2000).decode('utf-8', errors='replace')
                #         log_and_print("[텍스트 미리보기]")
                #         log_and_print(preview)
                # except Exception as eee:
                #     log_and_print(f"[미리보기 실패] {eee}")

                return

            # 컬럼 구조 비교
            exceptions = compare_all_csv_columns(z, standard_columns)

            # 로그 출력 및 저장
            log_and_print(f"\n📦 {zip_name}")
            log_and_print(f" - 기준 컬럼 수: {len(standard_columns)}개")
            log_and_print(f"[기준 컬럼 목록]: {sorted(standard_columns)}")
            log_and_print(f" - 예외 파일 수: {len(exceptions)}개 / 전체 {len(csv_files)}개")

            for fname, info in exceptions[:5]:
                if isinstance(info, list):  # 컬럼 리스트인 경우
                    log_and_print(f"   - {fname} → 컬럼 불일치: {sorted(info)}")
                else:  # 문자열(에러 메시지)인 경우
                    log_and_print(f"   - {fname} → {info}")

            log_and_print("")

            # 예외 파일 내용 미리보기
            for fname, info in exceptions:
                if isinstance(info, list) or (isinstance(info, str) and 'No columns' in info):
                    log_and_print(f"--- {fname} ---")
                    try:
                        with z.open(fname) as f:
                            raw = f.read()
                            log_and_print(f"[길이: {len(raw)} bytes]")
                            log_and_print(raw.decode('utf-8', errors='replace')[:1000])
                    except Exception as e:
                        log_and_print(f"[열기 실패] {e}")
    except Exception as e:
        log_and_print(f"[ZIP 열기 실패] {zip_name}: {e}")

for zip_path in zip_paths:
    log_and_print(f"\n🗂️ 처리 중: {zip_path}")
    with open(zip_path, "rb") as f:
        zip_bytes = f.read()
        process_zip_file(zip_bytes, str(zip_path))

# 로그 파일로 저장 (타임스탬프 포함)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"zip_column_check_log_recursive_{timestamp}.txt"
with open(log_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

log_and_print(f"\n📄 분석 결과가 '{log_file}'로 저장되었습니다.")
