import torch
from torch import nn
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from torch.optim import AdamW
from datasets import load_dataset
from torch.utils.data import DataLoader
import copy

# 1. 토크나이저 및 원본 모델
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # pad 토큰 설정

model_gelu = GPT2LMHeadModel.from_pretrained("gpt2")
model_relu = copy.deepcopy(model_gelu)

# 2. GELU → ReLU 치환
def replace_gelu_with_relu(model):
    for name, module in model.named_modules():
        if isinstance(module, nn.GELU):
            parent = model
            comps = name.split('.')
            for comp in comps[:-1]:
                parent = getattr(parent, comp)
            setattr(parent, comps[-1], nn.ReLU())

replace_gelu_with_relu(model_relu)

# 3. 데이터셋 준비
dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train[:1%]")

def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=64)

tokenized_dataset = dataset.map(tokenize_function, batched=True)
tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask"])
train_loader = DataLoader(tokenized_dataset, batch_size=2)

# 4. 학습 함수 (loss 기록 포함)
def finetune(model, label):
    model.train()
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    optimizer = AdamW(model.parameters(), lr=5e-5)
    device = next(model.parameters()).device
    losses = []

    for epoch in range(1):
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = input_ids.clone()
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            losses.append(loss.item())
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
    
    avg_loss = sum(losses) / len(losses)
    print(f"[{label}] 평균 Loss: {avg_loss:.4f}")

# 학습 수행
finetune(model_gelu, "GELU")
finetune(model_relu, "ReLU")

# 5. 생성 결과 비교
prompt = "The recipe for making pancakes includes"
inputs = tokenizer(prompt, return_tensors="pt").to(model_gelu.device)

model_gelu.eval()
model_relu.eval()

with torch.no_grad():
    out_gelu = model_gelu.generate(**inputs, max_length=30)
    out_relu = model_relu.generate(**inputs, max_length=30)

print("GELU 결과:", tokenizer.decode(out_gelu[0], skip_special_tokens=True))
print("ReLU 결과:", tokenizer.decode(out_relu[0], skip_special_tokens=True))
