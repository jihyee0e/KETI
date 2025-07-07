**모든 파일은 가상환경에서 실행되었습니다.**

가상환경 생성 및 실행
```bash
    python -m venv 가상환경명
    source 가상환경명/bin/activate  
```
<br>

## 📄 파일명: 0707

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
** 학습 짧게 진행했으므로 성능 차이는 미미하게 보일 수 있음
** 실험 확장 시: 더 긴 학습, perplexity, BLEU 평가 등 활용 가능


<br>
