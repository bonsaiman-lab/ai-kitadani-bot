import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import faiss
import numpy as np
import openai

# 既存ロジックのimport
from search_faiss import get_embedding, generate_answer

load_dotenv()

INDEX_PATH = os.path.join(os.path.dirname(__file__), '../knowledge/bonsai_faiss.index')
META_PATH = os.path.join(os.path.dirname(__file__), '../knowledge/bonsai_faiss_meta.json')

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    top_k: int = 3

class ChatResponse(BaseModel):
    answer: str
    knowledge: list

# FAISS検索部分を関数化

def search_faiss(query, top_k=3):
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    query_vec = get_embedding(query)
    D, I = index.search(np.array([query_vec]), top_k)
    results = []
    for i, idx in enumerate(I[0]):
        item = meta[idx]
        results.append({
            'rank': i + 1,
            'title': item.get('title'),
            'category': item.get('category'),
            'summary': item.get('summary'),
            'content': item.get('content'),
            'score': float(D[0][i])
        })
    return results

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        top_chunks = search_faiss(req.question, req.top_k)
        answer = generate_answer(req.question, top_chunks)
        return ChatResponse(answer=answer, knowledge=top_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
