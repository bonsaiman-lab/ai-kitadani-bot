import openai
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI embeddingモデル名
EMBED_MODEL = "text-embedding-ada-002"

# embedding生成

def get_embedding(text, api_key=None):
    openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
    response = openai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    )
    return np.array(response.data[0].embedding)

# ナレッジ全チャンクのembeddingをキャッシュしておく（初回のみ計算）
_knowledge_embeddings = None

def get_knowledge_embeddings(knowledge_chunks, api_key=None):
    global _knowledge_embeddings
    if _knowledge_embeddings is None:
        _knowledge_embeddings = [get_embedding(chunk['content'], api_key) for chunk in knowledge_chunks]
    return _knowledge_embeddings

# 類似チャンク検索

def search_knowledge(question_embedding, knowledge_chunks, api_key=None, top_k=1):
    knowledge_embeddings = get_knowledge_embeddings(knowledge_chunks, api_key)
    sims = [cosine_similarity(question_embedding, emb) for emb in knowledge_embeddings]
    best_idx = int(np.argmax(sims))
    return knowledge_chunks[best_idx]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
