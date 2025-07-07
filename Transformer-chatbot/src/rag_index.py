import numpy as np
import faiss
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

os.makedirs("rag", exist_ok=True)

# 문서 데이터 구성
documents = [
    "Transformer는 Attention 메커니즘을 기반으로 문장을 처리합니다.",
    "Position Encoding은 순서 정보를 모델에 제공하기 위해 사용됩니다.",
    "RAG는 벡터 검색을 통해 외부 지식을 활용하여 답변을 생성하는 구조입니다.",
    "FAISS는 벡터 유사도 기반 검색을 위한 Facebook의 라이브러리입니다.",
    "Cosine Similarity는 두 벡터 간의 방향 유사도를 나타내는 지표입니다."
]

# TF-IDF 벡터화 (sentence-transformers 대신)
vectorizer = TfidfVectorizer()
embeddings = vectorizer.fit_transform(documents).toarray()

# FAISS 인덱스 생성
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings.astype('float32'))

# 저장
faiss.write_index(index, "rag/rag_index.faiss")
with open("rag/rag_docs.pkl", "wb") as f:
    pickle.dump(documents, f)
with open("rag/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ FAISS 인덱스 및 문서 저장 완료")
