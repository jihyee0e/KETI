# 🧪 ReLU vs SiLU 성능 비교
# ✅ 실험 개요
# 데이터셋: MNIST 손글씨 숫자 이미지
# 모델: 작은 MLP (Multi-Layer Perceptron)
# 차이점: ReLU vs SiLU만 바꿔서 정확도 비교
# 목적: 단순 모델에서도 실제 성능 차이가 눈에 띄게 큰가?

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
# 데이터셋 로딩

transform = transforms.ToTensor()
train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
test_dataset  = datasets.MNIST(root='./data', train=False, transform=transform, download=True)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader  = DataLoader(test_dataset, batch_size=1000)

# 모델 정의
class SimpleMLP(nn.Module):
    def __init__(self, activation_fn):
        super().__init__()
        self.model = nn.Sequential(
            nn.Flatten(),  # 28x28 이미지를 벡터로 변환
            nn.Linear(28*28, 256),  # 은닉층1
            activation_fn,  # 외부에서 ReLU() or SiLU() 넣어줄 것임
            nn.Linear(256, 128),  # 은닉층2
            activation_fn,
            nn.Linear(128, 10)  # MNIST 클래스 10개(0~9 숫자) 출력
        )

    def forward(self, x):
        return self.model(x)

# 학습 및 테스트
def train_and_evaluate(activation_fn, name):
    # ReLU 모델이 될지, SiLU 모델이 될지 결정
    model = SimpleMLP(activation_fn).to(device)  # 학습을 GPU에서 돌릴지, CPU에서 돌릴지 자동 설정
    criterion = nn.CrossEntropyLoss()  # 모델이 얼마나 틀렸는지 계산하는 함수
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Adam: 빠르게 수렴

    for epoch in range(5):  # 5번만 학습
        model.train()  # 학습 중 
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)  # x(이미지 데이터), y(정답 숫자)
            optimizer.zero_grad()  # 기울기 초기화 (이전 gradient랑 섞이면 안됨)
            loss = criterion(model(x), y)  # 모델한테 x 넣어보고 예측 결과 반환받음 -> 정답이랑 얼마나 차이나는지 계산
            loss.backward()  # 손실이 얼마나 발생했는지를 각 가중치별로 역전파로 계산(어느 가중치를 얼마나 바꾸면 손실 줄일 수 있을지)
            optimizer.step()  # 위에서 계산한 gradient를 사용해 실제로 가중치를 업데이트

    # 테스트 성능 측정
    model.eval()  # 학습 중이 아님을 명시
    correct = total = 0
    with torch.no_grad():  # 테스트 할 때는 gradient 계산x -> 메모리 아끼고 속도 향상
        for x, y in test_loader:  # 배치 단위로 불러와서 반복
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)  # 모델 예측 결과 → 숫자 0~9에 대한 점수들 중 점수가 가장 높은 것(모델이 예측한 숫자)
            correct += (pred == y).sum().item()  # 예측이 맞았는지 확인하고 맞은 개수만 셈
            total += y.size(0)

    acc = correct / total
    print(f"{name} Accuracy: {acc:.4f}")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

train_and_evaluate(nn.ReLU(), "ReLU")
train_and_evaluate(nn.SiLU(), "SiLU")

