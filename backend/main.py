import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from utils import get_embedding, search_knowledge

# .envからAPIキーを読み込む
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ナレッジファイルのパス
KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), '../knowledge/bonsai_all_chunks.json')

# ナレッジの読み込み
with open(KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
    knowledge_chunks = json.load(f)

# FastAPIインスタンス作成
app = FastAPI()

# CORS設定（必要に応じて調整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    matched_chunk: dict

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    try:
        # ユーザー質問のembedding生成
        question_embedding = get_embedding(request.question, OPENAI_API_KEY)
        # 類似チャンク検索
        best_chunk = search_knowledge(question_embedding, knowledge_chunks, OPENAI_API_KEY)
        # 回答生成（シンプルにcontent返却。必要に応じて自然文生成も追加）
        answer = best_chunk.get('content', '')
        return AskResponse(answer=answer, matched_chunk=best_chunk)
    except Exception as e:
        import traceback
        print("[ERROR] /ask endpoint exception:", traceback.format_exc())
        return AskResponse(answer=f"エラーが発生しました: {str(e)}", matched_chunk={})
