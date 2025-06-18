** 모든 파일은 가상환경에서 실행되었습니다.
가상환경 생성 및 실행
```bash
    python -m venv 가상환경명
    source 가상환경명/bin/activate  
```

## 📄 파일명: 0616_multiprocessing.py

### ✅ 실행
```bash
    python3 0616_multiprocessing.py
```


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

```
2025-06-17 15:07:38,358 INFO worker.py:1879 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
(print_current_time pid=4754) 2025-06-17 15:07:46.837682
(print_current_time pid=4756) 2025-06-17 15:07:46.837779
(print_current_time pid=4755) 2025-06-17 15:07:46.837728
(print_current_time pid=4753) 2025-06-17 15:07:46.837768
결과:  [datetime.datetime(2025, 6, 17, 15, 7, 46, 837728), 
       datetime.datetime(2025, 6, 17, 15, 7, 46, 837779), 
       datetime.datetime(2025, 6, 17, 15, 7, 46, 837682), 
       datetime.datetime(2025, 6, 17, 15, 7, 46, 837768)]
```

📌 .remote()를 통해 병렬 실행된 함수들이 거의 동시에 실행되었음을 확인할 수 있음

📌 ray.get()으로 ObjectRef에서 실제 결과를 동기적으로 수집함

📌 Dashboard는 기본적으로 http://127.0.0.1:8265에서 실행됨 (에러 발생 시 include_dashboard=False로 끌 수 있음)

---

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

<데이터 설명 - data/raw/>
| 파일명                  | 설명                             | 행 개수 |
|-------------------------|----------------------------------|--------|
| `normal_data.csv`       | 정상 구조, `id`, `value`, `time` 포함 | 200 |
| `pipe_column.csv`       | `|` 포함 문자열 열 (`info`)       | 200 |
| `inconsistent_cols.csv` | 컬럼 수 적고, 누락 컬럼 발생 가능 | 150 |
| `noisy_data.csv`        | 이상치(`9999`, `-100`) 및 결측 존재 | 200 |
| `empty_file.csv`        | 완전 빈 파일 (0행, 0열)          | 0   |

```

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


---

## 📝 2506-3weeks 공부 내용 정리
  [병렬처리](https://jihye0e.tistory.com/21)
  
  [Ray-병렬/분산처리](https://jihye0e.tistory.com/22)

  [다양한 데이터 구조 전처리](https://jihye0e.tistory.com/23)