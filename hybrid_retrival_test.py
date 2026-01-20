# --- Interactive Test Script ---

from Querying import module_b_pipeline
from query_retrival import hybrid_retrieval_optimized
# Ensure UTF-8 output for Windows console
import sys
import io
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load indices and models
INDEX_FOLDER = 'search_index'
with open(os.path.join(INDEX_FOLDER, 'metadata.pkl'), 'rb') as f:
    docs = pickle.load(f)
with open(os.path.join(INDEX_FOLDER, 'bm25_model.pkl'), 'rb') as f:
    bm25 = pickle.load(f)
embeddings = np.load(os.path.join(INDEX_FOLDER, 'embeddings.npy'))
semantic_model = SentenceTransformer('sentence-transformers/LaBSE')

def run_test_query(user_input):
    print(f"\nSearching for: '{user_input}'")
    
    # 1. Process the query through Module B
    query_data = module_b_pipeline(user_input)
    print(f"Detected Lang: {query_data['source_lang']} | Translated: {query_data['translated']}")
    
    # 2. Get the Hybrid RRF Results from Module C
    results = hybrid_retrieval_optimized(query_data, docs, bm25, embeddings, semantic_model)
    
    # 3. Print Results in a readable format
    print(f"\n{'Rank':<5} | {'Score':<8} | {'Lang':<5} | {'Title'}")
    print("-" * 80)
    for i, res in enumerate(results):
        print(f"{i+1:<5} | {res['score']:<8} | {res['language']:<5} | {res['title'][:55]}...")


run_test_query("Climate change in Dhaka")
run_test_query("বাংলাদেশের অর্থনীতি") 
run_test_query("Criket")