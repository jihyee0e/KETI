import argparse
import subprocess

def run_rag():
    print("📚 [1/3] 문서 임베딩(RAG 인덱스) 생성 중...")
    subprocess.run(["python3", "src/rag_index.py"], check=True)

def run_train():
    print("🔧 [2/3] 모델 학습 시작...")
    subprocess.run(["python3", "src/train.py"], check=True)

def run_inference():
    print("💬 [3/3] 챗봇 실행 시작...")
    subprocess.run(["python3", "src/inference.py"], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transformer Chatbot Runner")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--rag_index", action="store_true", help="Create RAG index")  # ← 이 줄 추가
    parser.add_argument("--inference", action="store_true", help="Run inference mode")

    args = parser.parse_args()

    if args.rag_index:  
        run_rag()
    elif args.train:
        run_train()
    elif args.inference:
        run_inference()
    else:
        print("❗ 사용법: --train, --rag_index, 또는 --inference 인자를 주세요.")