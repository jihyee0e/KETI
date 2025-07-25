# LLM-chatbot 

## 📌 프로젝트 목적

다양한 LLM(예: Qwen2, Llama3, Mistral 등)을 활용하여 일상대화/데이터 분석/시각화가 모두 가능한 멀티 챗봇 구현
- Ollama 기반 LLM 선택, 파일 업로드, 데이터프레임 분석, 시각화 등 제공

## 📂 폴더 구조
```
final_llm/
├── agent/
│   ├── chatbot_agent.py     # LLM 에이전트 생성 및 관리
│   └── tool.py              # 데이터 요약/쿼리/시각화 등 툴 정의
├── components/
│   └── file_manager.py      # 파일 업로드 및 미리보기 컴포넌트
├── pages/
│   └── chatbot_view.py      # 챗봇 UI 및 LLM 연동
├── utils/
│   ├── common.py            # 세션 데이터 저장 등 공통 유틸
│   └── file_utils.py        # 파일 중복 제거 등 파일 유틸
├── app.py                   # Streamlit 메인 앱 (대시보드+챗봇)
└── README.md
```

## 🧭 주요 기능
```
1. 모델 선택
    - Ollama에 설치된 다양한 모델을 드롭바에서 선택
2. 파일 업로드 및 미리보기
    - csv, xlsx, json, parquet, pdf, txt 등 다양한 포맷 지원
3. 일상대화/분석 자동 구분
    - 사용자의 질문 맥락에 따라 LLM이 일상/분석/코딩 등 자연스럽게 구분하여 답변
```


## 실행 순서
1. Ollama 설치 및 LLM 모델 다운로드
```bash
    $ ollama pull llama3:8b  # 필요한 ollama 모델
```
2. 필요한 패키지 설치 
```bash
    $ pip install -r requirements.txt
```
3. 앱 실행
```bash
    $ streamlit run app.py
```

## 🔗 출력 예시
<img width="1070" height="740" alt="Image" src="https://github.com/user-attachments/assets/c210bc8b-abaa-408f-9a72-70dfd8fedc48" />
<img width="1084" height="698" alt="Image" src="https://github.com/user-attachments/assets/fe76a4d6-f4e2-4042-b6a7-faa2919fa02f" />
<img width="1144" height="723" alt="Image" src="https://github.com/user-attachments/assets/5d3ad421-a223-456a-8832-91449d4e1f4e" />
<img width="471" height="197" alt="Image" src="https://github.com/user-attachments/assets/3fc792ed-5f70-4115-b024-e10e3eb82d74" />
<img width="466" height="134" alt="Image" src="https://github.com/user-attachments/assets/e63732f4-0a3f-4cad-9620-4a47a927d3f9" />
<img width="781" height="289" alt="Image" src="https://github.com/user-attachments/assets/e21ae2c7-053b-4bc8-94ed-93c1b1aae356" />
