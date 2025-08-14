import os
import json
import numpy as np
import faiss
from pathlib import Path
from dotenv import load_dotenv
import openai

# .envからAPIキー読み込み
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError('OPENAI_API_KEYが.envに設定されていません')
openai.api_key = OPENAI_API_KEY

# パス定義
INDEX_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_faiss.index'
META_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_faiss_meta.json'
EMBEDDING_MODEL = 'text-embedding-ada-002'

# embedding生成
def get_embedding(text):
    response = openai.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return np.array(response.data[0].embedding, dtype='float32')

# 検索
def search(query, top_k=3):
    # FAISSインデックスとメタ情報ロード
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    # embedding生成
    query_vec = get_embedding(query)
    # 検索
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

def generate_answer(query, top_chunks):
    # ナレッジをプロンプト用に整形
    knowledge_text = "\n\n".join([
        f"タイトル: {c['title']}\nカテゴリ: {c['category']}\n要約: {c['summary']}\n本文: {c['content']}"
        for c in top_chunks
    ])
    system_prompt = (
        "あなたは盆栽のプロフェッショナルです。以下のナレッジのみを根拠に、ユーザーの質問に対して初心者にもわかりやすく日本語で回答してください。"
        "ナレッジ以外の情報や推測は使わず、北谷隆一氏の知識のみを根拠にしてください。"
        "もしナレッジ内に該当情報がなければ『ごめんなさい、この質問には北谷氏の知識の範囲ではお答えできません』と返してください。"
    )
    user_prompt = f"ユーザーの質問: {query}\n\n参照できるナレッジ:\n{knowledge_text}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=512
    )
    answer = response.choices[0].message.content.strip()
    return answer + "\n\n盆栽枯らしたらもったいない。北谷隆一"

if __name__ == '__main__':
    print('盆栽Q&Aベクトル検索＋AI回答生成（FAISS+GPT-4）')
    while True:
        query = input('\n質問を入力してください（終了はexit）: ').strip()
        if query.lower() in ['exit', 'quit', 'q', '']: break
        results = search(query, top_k=3)
        print('\n--- 根拠ナレッジ（上位3件） ---')
        for res in results:
            print(f"\n[{res['rank']}] {res['title']}  <{res['category']}> (score: {res['score']:.4f})")
            print(f"要約: {res['summary']}")
            print(f"本文: {res['content']}")
        print('------------------------------')
        # AIによる自然な回答生成
        answer = generate_answer(query, results)
        print(f'\n--- AIによる回答 ---\n{answer}\n-------------------')
