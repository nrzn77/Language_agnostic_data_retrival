import json
import re
import os
import pickle
import numpy as np
import torch
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# 1. Setup Folder
INDEX_FOLDER = 'search_index'
if not os.path.exists(INDEX_FOLDER):
    os.makedirs(INDEX_FOLDER)

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

# Load your 10,000+ articles
print("Loading articles...")
bangla_docs = load_jsonl('prothom_alo.jsonl')
english_docs = load_jsonl('dhaka_tribune.jsonl')
all_docs = bangla_docs + english_docs

# 2. Efficient Tokenization
def tokenize(text):
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    return clean_text.split()

print("Building Lexical Index (BM25)...")
tokenized_corpus = [tokenize(doc['body']) for doc in all_docs]
bm25_model = BM25Okapi(tokenized_corpus)

# 3. Fast Semantic Indexing
# Check for GPU (cuda) to speed up from minutes to seconds
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Generating semantic embeddings using {device}...")

semantic_model = SentenceTransformer('sentence-transformers/LaBSE', device=device)

# Speed up with larger batch_size and float16 precision
doc_bodies = [doc['body'] for doc in all_docs]
doc_embeddings = semantic_model.encode(
    doc_bodies, 
    batch_size=64,           # Increased for speed
    show_progress_bar=True, 
    convert_to_numpy=True
)

# 4. Save Everything to the Same Folder
print("Saving indices to disk...")

# Save Metadata (Titles, URLs, etc.)
with open(os.path.join(INDEX_FOLDER, 'metadata.pkl'), 'wb') as f:
    pickle.dump(all_docs, f)

# Save BM25 Model
with open(os.path.join(INDEX_FOLDER, 'bm25_model.pkl'), 'wb') as f:
    pickle.dump(bm25_model, f)

# Save Semantic Embeddings (Binary format is fastest for large arrays)
np.save(os.path.join(INDEX_FOLDER, 'embeddings.npy'), doc_embeddings)

print(f"Indexing complete! Saved 10,000+ articles to '{INDEX_FOLDER}/'")