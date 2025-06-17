import argparse
import subprocess
import os

def run_train():
    print("🔧 모델 학습 시작...")
    subprocess.run(["python3", "src/train.py"], check=True)

def run_inference():
    print("💬 챗봇 실행 시작...")
    subprocess.run(["python3", "src/inference.py"], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transformer Chatbot Runner")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--inference", action="store_true", help="Run inference mode")

    args = parser.parse_args()

    if args.train:
        run_train()
    elif args.inference:
        run_inference()
    else:
        print("❗ 사용법: --train 또는 --inference 인자를 주세요.")