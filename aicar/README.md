## 📄 파일명: per-test.py, total-test.py

### 📌 목적
- 로그 데이터가 저장된 .zip 파일 내 .csv 파일들의 컬럼 구조 일관성 검사 자동화
- 각 .zip 파일에서 대표 .csv 파일을 기준으로 표준 컬럼 목록을 추출한 뒤, 동일한 zip 내의 다른 파일들과 비교 아래 사항들을 탐지하고 로깅
    - 컬럼 불일치
    - 파싱 실패
    - 비어 있는 파일
    - 내부 .zip 포함 여부
- 전처리 이전 데이터 품질 검수 및 사전 진단 단계에서 사용


### ✅ 실행
1. 스크립트 실행
```bash
    python3 per-test.py      # 단일 zip 검사
    python3 total-test.py    # 전체 디렉토리 재귀 zip 검사
```

### 🔗 출력 예시
<img width="1288" height="483" alt="Image" src="https://github.com/user-attachments/assets/04e34432-7f75-430e-93e2-9371ca289661" />

<br>