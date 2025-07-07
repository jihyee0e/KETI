import tensorflow as tf
import pickle
from src.model import PositionalEncoding, MultiHeadAttention
from src.mask_schedule import create_padding_mask, create_look_ahead_mask, CustomSchedule
# from src.tokenizer import load_tokenizer
# from src.model import transformer
import re
import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

# ===RAG 설정===
# 벡터 DB와 문서 불러오기 
index = faiss.read_index("rag/rag_index.faiss")
with open("rag/rag_docs.pkl", "rb") as f:
    documents = pickle.load(f)
with open("rag/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # 재학습 아님, 그대로 불러서 query 임베딩만

def retrieve_context(query, top_k=1):
    # query_emb = embedding_model.encode([query])
    query_emb = vectorizer.transform([query]).toarray().astype('float32')
    _, I = index.search(query_emb, top_k)
    return "\n".join([documents[i] for i in I[0]])


# ===모델 설정===
MAX_LENGTH = 40

# tokenizer 불러오기
with open('model/tokenizer.pickle', 'rb') as f:
    tokenizer = pickle.load(f)

# 특수 토큰
START_TOKEN, END_TOKEN = [tokenizer.vocab_size], [tokenizer.vocab_size + 1]

# 모델 불러오기
model = tf.keras.models.load_model(
    'model/chatbot_model.keras',
    custom_objects={
        'PositionalEncoding': PositionalEncoding,
        'MultiHeadAttention': MultiHeadAttention,
        'CustomSchedule': CustomSchedule,
        'create_padding_mask': create_padding_mask,
        'create_look_ahead_mask': create_look_ahead_mask
    }
)

# 간단한 전처리
def preprocess_sentence(sentence):
    sentence = re.sub(r"([?.!,])", r" \\1", sentence)
    return sentence.strip()


# def evaluate(sentence):
    # sentence = preprocess_sentence(sentence)
    # encoded = tokenizer.encode(question)
# ===RAG 통합 답변 생성===
def evaluate(question):
    context = retrieve_context(question, top_k=1)
    input_text = f"문맥: {context}\n질문: {question}\n답변:"
    processed = preprocess_sentence(input_text)
    encoded = tokenizer.encode(processed)

    if not encoded:
        print("⚠️ 입력이 너무 짧거나 처리할 수 없습니다.")
        return tf.constant([])

    sentence = tf.expand_dims(START_TOKEN + encoded + END_TOKEN, axis=0)
    output = tf.expand_dims(START_TOKEN, 0)

    prev_token = None  # 직전 예측 토큰 저장
    for _ in range(MAX_LENGTH):
        predictions = model([sentence, output], training=False)
        predictions = predictions[:, -1:, :]  # 마지막 시점의 결과
        predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)

        # 종료 조건 1: EOS 토큰 예측
        if tf.equal(predicted_id, END_TOKEN[0]):
            break
        # 종료 조건 2: 이전 토큰과 같으면 반복 중단
        if prev_token is not None and tf.equal(predicted_id, prev_token):
            print("⚠️ 동일한 토큰 반복 감지. 강제 종료.")
            break

        output = tf.concat([output, predicted_id], axis=-1)
        prev_token = predicted_id  # 현재 토큰을 저장

    return tf.squeeze(output, axis=0)


# def predict(sentence):
#     prediction = evaluate(sentence)
def predict(question):
    prediction = evaluate(question)
    if tf.size(prediction).numpy() == 0:
        return "⚠️ 대답할 수 없습니다."

    decoded = tokenizer.decode([i for i in prediction if i < tokenizer.vocab_size])

    print('Input: {}'.format(question))
    print('Output: {}'.format(decoded))
    
    # print("Raw prediction:", prediction.numpy().tolist())
    # print("Filtered:", [i for i in prediction if i < tokenizer.vocab_size])

    return decoded

# ===대화 실행===
if __name__ == "__main__":
    while True:
        sentence = input("You > ")
        if sentence.lower() == "quit" or sentence.lower() == "q":
            break
        print("Bot >", predict(sentence))