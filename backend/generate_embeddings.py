import os
import json
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import openai

# .envからAPIキー読み込み
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError('OPENAI_API_KEYが.envに設定されていません')
openai.api_key = OPENAI_API_KEY

# ナレッジファイルのパス
KNOWLEDGE_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_all_chunks.json'
OUTPUT_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_all_chunks_with_embeddings.json'

# Embeddingモデル
EMBEDDING_MODEL = 'text-embedding-ada-002'

# JSON読み込み
def load_knowledge(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Embedding生成
def get_embedding(text):
    response = openai.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

if __name__ == '__main__':
    knowledge_data = load_knowledge(KNOWLEDGE_PATH)
    results = []
    for chunk in tqdm(knowledge_data, desc='Embedding生成中'):
        content = chunk.get('content', '')
        embedding = get_embedding(content)
        chunk_with_embedding = {
            **chunk,
            'embedding': embedding
        }
        results.append(chunk_with_embedding)
    # 保存
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'保存完了: {OUTPUT_PATH}')
