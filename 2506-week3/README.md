**모든 파일은 가상환경에서 실행되었습니다.**

가상환경 생성 및 실행
```bash
    python -m venv 가상환경명
    source 가상환경명/bin/activate  
```
<br>

## 📄 파일명: 0616_multiprocessing.py

### ✅ 실행
```bash
    python3 0616_multiprocessing.py
```
<br>

## 📄 파일명: 0617_Ray-test.py

### ✅ 실행 순서
1. Ray 설치 및 확인
```bash
    pip install -U "ray[default]"
    python -c "import ray; print(ray.__version__)"   # 2.46.0
```

2. 파일 실행
```bash
    python3 0617_Ray-test.py    
```

### 🔗 출력 예시

![Image](https://github.com/user-attachments/assets/8a471566-f550-46fa-ad71-9637d55cbde3)
![Image](https://github.com/user-attachments/assets/b94f7021-a0cb-4405-bcbc-4aa8d11978ee)

- .remote()를 통해 병렬 실행된 함수들이 거의 동시에 실행되었음을 확인할 수 있음
- ray.get()으로 ObjectRef에서 실제 결과를 동기적으로 수집함
- Dashboard는 기본적으로 http://127.0.0.1:8265에서 실행됨 (에러 발생 시 include_dashboard=False로 끌 수 있음)

<br>

## 📄 폴더명: 0618

### 📌 목적
- 다양한 구조의 CSV 파일을 대상으로 전처리 실습
- 컬럼 수 불일치, 특수문자 포함, 이상치/결측, 시간 파싱 등 유연한 대응
- 병렬 처리(Ray)와 자동화된 구조 탐색 방식 익히기

### 📂 폴더 구조
```
    0618/   
    ├── data/
    │   ├── raw/   # 생성된 원본 CSV 파일
    │   └── processed/   # 전처리 파일 저장 
    ├── log.txt  # 처리 결과 로그 기록
    ├── preprocess.py # 병렬 전처리 스크립트
    └── generate_dataset.py  # 연습용 데이터 생성 스크립트

```

<데이터 설명 - data/raw/>
| 파일명                  | 설명                             | 행 개수 |
|-------------------------|----------------------------------|--------|
| `normal_data.csv`       | 정상 구조, `id`, `value`, `time` 포함 | 200 |
| `pipe_column.csv`       | `|` 포함 문자열 열 (`info`)       | 200 |
| `inconsistent_cols.csv` | 컬럼 수 적고, 누락 컬럼 발생 가능 | 150 |
| `noisy_data.csv`        | 이상치(`9999`, `-100`) 및 결측 존재 | 200 |
| `empty_file.csv`        | 완전 빈 파일 (0행, 0열)          | 0   |


### ✅ 실행 순서
1. 데이터 생성
```
    python3 generate_dataset.py  # data/raw/ 경로에 5개의 csv 파일 생성
```

2. 전처리 실행
```
    python3 preprocess.py
```

### 🔗 출력 예시
![Image](https://github.com/user-attachments/assets/cc2b45ea-9727-4f77-af22-f32bdaf8c910)

<br>

## 📄 폴더명: 0619

### 📌 목적
- MinIO 데이터 구조 로컬 실습
- 일반 사용자 계정에서 MinIO Web UI 및 CLI 사용 권한 테스트
- Web UI 버킷 목록 표시, 객체 다운로드, 정책 적용 흐름 확인


### 📂 폴더 구조
```
    0619/
    ├── data/
    │   ├── .minio.sys/          # MinIO 내부 시스템 
    │   ├── mybucket-test1/      # 테스트 버킷1 
    │   ├── mybucket-test2/      # 테스트 버킷2 
    ├── test_files/              # testuser 계정으로 다운로드한 결과
    │   └── mybucket-test1/
    │       ├── Finance_data.csv
    │       └── 아카이브.zip
    ├── minio                    # MinIO 실행 파일
    └── README.md
```

### ✅ 실행 순서 or 과정
1. MinIO 실행
```bash
    MINIO_ROOT_USER=rootID MINIO_ROOT_PASSWORD=rootPW ./minio server ./data
```

2. 관리자 계정 등록 및 정책 부여
```bash
    mc alias set myminio http://localhost:9000 rootID rootPW
    mc admin user add myminio testID testPW
    mc admin policy attach myminio readwrite --user testID
```

3. Web UI 접속
```
    주소: http://localhost:9000
    계정: testID / testPW -> 버킷 목록 및 객체 접근 확인
```

4. CLI로 데이터 다운로드 테스트
```
    mc alias set testminio http://localhost:9000 testID testPW
    mc cp --recursive testminio/bucket이름 ./데이터저장파일명
```

### 🧾 비고
- 커스텀 정책(ui-admin.json)은 mc admin policy create에서 지원되지 않아 실패
- MinIO 최신 버전에서는 s3:*, s3:GetObject 등 대부분의 액션 직접 명시 불가
- 실질적으로 Web UI 및 CLI 동작 확인엔 readwrite 정책이 안정적이

---

## 📝 2506-week3 공부 내용 정리
  [병렬처리](https://jihye0e.tistory.com/21)
  
  [Ray-병렬/분산처리](https://jihye0e.tistory.com/22)

  [다양한 데이터 구조 전처리](https://jihye0e.tistory.com/23)

  [MinIO](https://jihye0e.tistory.com/24)
  
  [MinIO-흐름 따라가기](https://jihye0e.tistory.com/25)