**모든 파일은 가상환경에서 실행되었습니다.**

가상환경 생성 및 실행
```bash
    python -m venv 가상환경명
    source 가상환경명/bin/activate  
```
<br>

## 📄 파일명: 0623_pandasai_test.py

### 📌 목적
- 여러 CSV 파일을 업로드하여 로컬 LLM을 활용한 자연어 기반 데이터 질의 응답 실습
- PandasAI와 Streamlit을 활용한 대화형 데이터 탐색 환경 구현
- LM Studio에서 실행 중인 LLaMA 모델과 연동하여 로컬 기반 처리 수행

### ✅ 실행 순서

1. 가상환경에서 필요 라이브러리 설치
```bash
    pip install -r requirements.txt
```

2. LM Studio 실행 후 모델 활성화
```bash
    ollama pull llama3.1:8b  # 모델명은 원하는 걸로
    ollama serve
```

3. 앱 실행
```bash
    streamlit run pandasai-test.py --server.baseUrlPath=/pandasai --server.enableCORS=false --server.enableXsrfProtection=false
```

### 🔗 동작 방식
- 실행 후 웹 페이지에서 여러 CSV 파일 업로드 가능
- 상위 3개 행 미리 보기 출력
- 자연어로 질문 입력 → PandasAI가 로컬 LLM 통해 답변 생성
    > ⚠️ 컬럼명과 질문을 영어로 하면 더 정확한 답변을 받을 수 있습니다.
    
      ✏️ 예시: What is the maximum Salary? (컬럼명이 Salary일 때)

---

## 📝 2506-week4 공부 내용 정리

[LLM(PandasAI + Ollama Chatbot)](https://jihye0e.tistory.com/26)