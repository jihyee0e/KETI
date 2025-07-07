import os
import tensorflow as tf
from src.model import transformer
from src.mask_schedule import create_padding_mask, create_look_ahead_mask, CustomSchedule
from src.tokenizer import load_tokenizer
import urllib.request
import pandas as pd
from sklearn.model_selection import train_test_split
import pickle
import re
import faiss

# Download dataset if not exists
os.makedirs("data", exist_ok=True)
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/songys/Chatbot_data/master/ChatbotData.csv",
    filename="data/ChatBotData.csv"
)

# Read the dataset
train_data = pd.read_csv("data/ChatBotData.csv")

def preprocess_sentence(sentence):
    sentence = re.sub(r"([?.!,])", r" \\1", sentence)
    return sentence.strip()

index = faiss.read_index("rag/rag_index.faiss")
with open("rag/rag_docs.pkl", "rb") as f:
    documents = pickle.load(f)
with open("rag/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# context 검색 함수 정의
def get_context_for_question(question, top_k=1):
    query_emb = vectorizer.transform([question]).toarray().astype('float32')
    _, I = index.search(query_emb, top_k)
    return "\n".join([documents[i] for i in I[0]])

# Extract questions and answers
questions = train_data['Q'].tolist()
answers = train_data['A'].tolist()

questions = [
    f"문맥: {get_context_for_question(q)}\n질문: {q}\n답변:"
    for q in questions
]


# Split into train/validation sets
train_q, val_q, train_a, val_a = train_test_split(questions, answers, test_size=0.2)

# 설정값
MAX_LENGTH = 80
BATCH_SIZE = 32
EPOCHS = 10   # 30~50 사이에서 loss 보고 조절
D_MODEL = 128
NUM_LAYERS = 4
NUM_HEADS = 8
DFF = 512
DROPOUT = 0.1

# Tokenizer
tokenizer = load_tokenizer(train_q + val_q, train_a + val_a)
VOCAB_SIZE = tokenizer.vocab_size + 2

# Tokenize and filter
def tokenize_and_filter(inputs, outputs, max_length=MAX_LENGTH):
    tokenized_inputs, tokenized_outputs = [], []
    for sentence1, sentence2 in zip(inputs, outputs):
        sentence1 = tokenizer.encode(sentence1)
        sentence2 = tokenizer.encode(sentence2)

        if len(sentence1) <= max_length and len(sentence2) <= max_length:
            tokenized_inputs.append(sentence1)
            tokenized_outputs.append(sentence2)

    tokenized_inputs = tf.keras.preprocessing.sequence.pad_sequences(
        tokenized_inputs, maxlen=max_length, padding='post')
    tokenized_outputs = tf.keras.preprocessing.sequence.pad_sequences(
        tokenized_outputs, maxlen=max_length, padding='post')

    return tokenized_inputs, tokenized_outputs

train_inputs, train_outputs = tokenize_and_filter(train_q, train_a)
val_inputs, val_outputs = tokenize_and_filter(val_q, val_a)

# Dataset 구성
train_dataset = tf.data.Dataset.from_tensor_slices((train_inputs, train_outputs))
val_dataset = tf.data.Dataset.from_tensor_slices((val_inputs, val_outputs))

dataset = train_dataset.concatenate(val_dataset)
dataset = dataset.cache()
dataset = dataset.shuffle(10000)
dataset = dataset.batch(BATCH_SIZE)
dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)

# 모델 생성
model = transformer(
    VOCAB_SIZE,
    NUM_LAYERS,
    DFF,
    D_MODEL,
    NUM_HEADS,
    DROPOUT
)

# 옵티마이저, 손실함수
learning_rate = CustomSchedule(D_MODEL)
optimizer = tf.keras.optimizers.Adam(learning_rate,
                                     beta_1=0.9,
                                     beta_2=0.98,
                                     epsilon=1e-9)
# 각 타임스텝에서 정답 토큰과 예측 토큰 사이의 croww entropy 차이 계산 (정답에 가까울수록 loss 0에 수렴)
loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction='none')

def loss_function(y_true, y_pred):
    y_true = tf.reshape(y_true, shape=(-1, MAX_LENGTH - 1))

    loss = tf.keras.losses.SparseCategoricalCrossentropy(
        from_logits=True, reduction='none')(y_true, y_pred)

    mask = tf.cast(tf.not_equal(y_true, 0), tf.float32)
    loss *= mask

    return tf.reduce_mean(loss)

@tf.function
def train_step(inp, tar):
    tar_inp = tar[:, :-1]
    tar_real = tar[:, 1:]
    enc_padding_mask = create_padding_mask(inp)
    look_ahead_mask = create_look_ahead_mask(tar_inp)
    dec_padding_mask = create_padding_mask(inp)

    with tf.GradientTape() as tape:
        predictions = model([inp, tar_inp], training=True)
        loss = loss_function(tar_real, predictions)

    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    return loss

# 학습 루프
for epoch in range(EPOCHS):
    print(f'\nEpoch {epoch+1}/{EPOCHS}')
    total_loss = 0
    for (batch, (inp, tar)) in enumerate(dataset):  
        loss = train_step(inp, tar)
        total_loss += loss

        if batch % 100 == 0:
            print(f"  Batch {batch}, Loss: {loss.numpy():.4f}")

    print(f"Epoch {epoch+1} Loss: {(total_loss / batch):.4f}")

# 모델 저장
os.makedirs('model', exist_ok=True)
model.save('model/chatbot_model.keras')

import pickle

with open('model/tokenizer.pickle', 'wb') as f:
    pickle.dump(tokenizer, f)