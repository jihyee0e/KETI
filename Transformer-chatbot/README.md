# Transformer-chatbot 

## 📌 프로젝트 목적

  Transformer 기반 챗봇 구현: Transformer 구조를 구현하여 간단한 질의응답 챗봇을 만드는 학습용 프로젝트

## 📂 폴더 구조
```
Transformer-chatbot/   
├── data/
│   └── ChatBotData.csv      ← 학습용 데이터, 최초 실행 시 자동 다운로드
├── model/                   # 학습된 모델 저장 폴더  
│   ├── chatbot_model.keras  ← 학습된 모델 가중치 (.keras)
│   └── tokenizer.pickle     ← 학습된 토크나이저 (.pickle)
├── src/
│   ├── run.py               ← 실행 제어
│   ├── inference.py         ← 챗봇 응답 생성 (모델 + 토크나이저 불러와서 추론)
│   ├── mask_schedule.py     ← 마스크 생성 및 커스텀 학습률 스케줄러 정의
│   ├── model.py             ← Transformer 구조 정의 (인코더, 디코더, 전체 모델)
│   ├── tokenizer.py         ← Subword 토크나이저 생성 함수 정의
│   └── train.py             ← 학습 파이프라인 (모델 학습 + 저장)
├── README.md
└── requirements.txt
```

## 🧱 전체 구조 요약
  ```
  plaintext
  [입력 문장] 
     ↓
  [인코더 (self-attention)]
     ↓
  [디코더 (look-ahead + enc-dec attention)]
     ↓
  [출력층 Dense → 단어 예측]
  ```

## 🧭 챗봇 구현 흐름

  1. 데이터 전처리 및 토크나이징
  2. 마스크 생성 (`create_padding_mask`, `create_look_ahead_mask`)
  3. 인코더/디코더 레이어 구성 (`encoder_layer`, `decoder_layer`)
  4. 전체 모델 구성 (`transformer`)
  5. 학습 루프 및 옵티마이저 설정
  6. 추론 로직: 한 글자씩 생성하며 답변 완성
     
## 실행 순서
```
$ pip install -r requirements.txt
$ PYTHONPATH=. python3 src/run.py --train  # 모델 생성
$ PYTHONPATH=. python3 src/run.py  --inference  # 챗봇 실행
  - You > 입력 후 대화
  - **quit** 입력하면 종료
```


## 🔗 출력 예시
  ```
  Input: 영화 볼까?
  Output: 최신 인기 차트를 찾아보는 걸 추천해요 .
  
  Input: 이사 가고싶어
  Output: 가면 저도 데려가세요 .
  
  Input: 난 바보야
  Output: 사랑해주는 사람이 있을 거예요 .
  ```

## 📚 참고
  - [Attention is All You Need](https://arxiv.org/abs/1706.03762)
  - TensorFlow 공식 문서 및 튜토리얼