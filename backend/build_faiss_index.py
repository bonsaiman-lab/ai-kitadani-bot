import json
import numpy as np
import faiss
from pathlib import Path

# 入力・出力パス
KNOWLEDGE_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_all_chunks_with_embeddings.json'
INDEX_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_faiss.index'
META_PATH = Path(__file__).parent.parent / 'knowledge' / 'bonsai_faiss_meta.json'

# データ読み込み
def load_knowledge(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    data = load_knowledge(KNOWLEDGE_PATH)
    embeddings = np.array([chunk['embedding'] for chunk in data]).astype('float32')
    # FAISSインデックス作成（L2距離）
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    # メタ情報（ID→chunk情報）保存
    meta = [
        {
            'title': chunk.get('title'),
            'summary': chunk.get('summary'),
            'category': chunk.get('category'),
            'content': chunk.get('content')
        }
        for chunk in data
    ]
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'FAISSインデックス保存: {INDEX_PATH}')
    print(f'メタ情報保存: {META_PATH}')

if __name__ == '__main__':
    main()
