**모든 파일은 가상환경에서 실행되었습니다.**

가상환경 생성 및 실행
```bash
    python -m venv 가상환경명
    source 가상환경명/bin/activate  
```
<br>

## 📄 폴더명: 0707

### 📌 목적
- GPT2 모델에서 활성화 함수(GELU ↔ ReLU) 를 교체하여 생성 성능 차이를 실험
- 사전학습된 GPT2에 대해 wikitext 일부로 간단한 finetuning 수행
- 같은 입력에 대해 각각의 활성화 함수로 구성된 모델이 어떤 문장을 생성하는지 비교



### ✅ 실행
1. 필수 라이브러리 설치
```bash
    pip install torch transformers datasets
```

2. 스크립트 실행
```bash
    python 0707_relu-llm.py
```

### 🔗 동작 방식
- GPT2LMHeadModel을 기준으로:
    - 원본 GELU 기반 모델 vs ReLU로 내부 활성화 함수를 교체한 모델
- 두 모델 모두 동일한 텍스트 데이터(wikitext-2의 1% 샘플)로 학습
- 학습 후, 동일한 입력 프롬프트에 대해 문장 생성 결과를 비교 출력

### 🔗 출력 예시
<img width="197" height="33" alt="Image" src="https://github.com/user-attachments/assets/486d8702-06e3-45ec-9ad4-cdcfb946cf03" />
<img width="552" height="203" alt="Image" src="https://github.com/user-attachments/assets/d54717ca-2d2f-4b3b-ad61-aa5f79013b3f" />

```
- 학습 짧게 진행했으므로 성능 차이는 미미하게 보일 수 있음
- 실험 확장 시: 더 긴 학습, perplexity, BLEU 평가 등 활용 가능
```

<br>

## 📄 폴더명: llm

### 📌 목적
- 자연어 기반 분석 에이전트 구현
- 사용자의 질의에 따라 데이터를 자동 요약, 시각화 및 질의응답하는 LLM 기반 분석 파이프라인 구성
- LangChain + Streamlit 연동을 위한 기능 단위 구현 및 테스트 포함


### ✅ 실행
1. 스크립트 실행
```bash
    python test.py
```

### 🔗 동작 방식
- analysis_utils.py는 다음과 같은 기능을 포함:

| 함수명                              | 설명                                      |
| --------------------------------- | -------------------------------          |
| `summarize_dataframe(df)`         | 데이터프레임의 기본 통계, 컬럼별 정보 등을 요약     |
| `visualize_from_query(df, query)` | 자연어 질의(query)를 바탕으로 시각화(그래프) 생성  |
| `process_query(df, query)`        | 자연어 질의를 코드로 변환 후 실행하여 결과 출력     |
| `get_all_tools()`                 | 위 함수들을 LangChain용 Tool로 반환           |

### 🔗 출력 예시
<1차>
<img width="675" height="501" alt="Image" src="https://github.com/user-attachments/assets/ba7018ed-bf12-4d58-badf-9b6f88562b27" />
<img width="673" height="419" alt="Image" src="https://github.com/user-attachments/assets/a34baabd-0b0e-44eb-a193-c211746d5e25" />
<img width="499" height="266" alt="Image" src="https://github.com/user-attachments/assets/42e09fe3-67f9-40bb-99f4-1ee31b0b9be0" />
<img width="680" height="556" alt="Image" src="https://github.com/user-attachments/assets/064cc4c4-2348-40de-9cd5-8033d70bdf08" />

<br>
