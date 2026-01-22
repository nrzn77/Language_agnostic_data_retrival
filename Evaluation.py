import json
import os
import pickle
import numpy as np
import pandas as pd
import torch
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics import ndcg_score
import time

# --- CONFIGURATION ---
INDEX_FOLDER = 'search_index'
GROUND_TRUTH_FILE = 'labeled_queries.csv'
TOP_K_PRECISION = 10
TOP_K_RECALL = 50

# --- 1. LOAD INDICES ---
print("Loading indices and models...")

# Load Metadata
with open(os.path.join(INDEX_FOLDER, 'metadata.pkl'), 'rb') as f:
    metadata = pickle.load(f)

# Load BM25
with open(os.path.join(INDEX_FOLDER, 'bm25_model.pkl'), 'rb') as f:
    bm25_model = pickle.load(f)

# Load Semantic Embeddings
doc_embeddings = np.load(os.path.join(INDEX_FOLDER, 'embeddings.npy'))

# Load Model (CPU/GPU)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
semantic_model = SentenceTransformer('sentence-transformers/LaBSE', device=device)

print("Models loaded successfully.")

# --- 2. SEARCH FUNCTION (REPLICATED FROM YOUR HYBRID SCRIPT) ---
def search(query, top_k=50):
    """
    Performs hybrid search and returns a list of relevant URLs.
    """
    # Tokenize for BM25
    tokenized_query = query.lower().split()
    bm25_scores = bm25_model.get_scores(tokenized_query)
    
    # Encode for Semantic
    query_embedding = semantic_model.encode(query, convert_to_tensor=True, device=device)
    query_embedding = query_embedding.cpu().numpy()
    
    # Cosine Similarity
    semantic_scores = np.dot(doc_embeddings, query_embedding)
    
    # Hybrid Fusion (0.5 BM25 + 0.5 Semantic - Adjust weights if needed)
    # Normalize BM25 to 0-1 range for fair combination
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)
        
    hybrid_scores = (0.5 * bm25_scores) + (0.5 * semantic_scores)
    
    # Get Top K indices
    top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
    
    # Return list of URLs found
    results = [metadata[i]['url'] for i in top_indices]
    return results

# --- 3. EVALUATION METRICS ---
def calculate_metrics(retrieved_urls, true_relevant_urls):
    """
    Calculates Precision@K, Recall@K, MRR, and nDCG.
    """
    # Binary Relevance: 1 if URL is in ground truth, 0 otherwise
    relevance_vector = [1 if url in true_relevant_urls else 0 for url in retrieved_urls]
    
    # 1. Precision@10
    k_prec = min(len(relevance_vector), TOP_K_PRECISION)
    precision_at_k = sum(relevance_vector[:k_prec]) / k_prec
    
    # 2. Recall@50
    # Recall = (Relevant items retrieved) / (Total relevant items in DB)
    total_relevant = len(true_relevant_urls)
    k_rec = min(len(relevance_vector), TOP_K_RECALL)
    recall_at_k = sum(relevance_vector[:k_rec]) / total_relevant if total_relevant > 0 else 0

    # 3. MRR (Mean Reciprocal Rank)
    try:
        first_correct_rank = relevance_vector.index(1) + 1
        mrr = 1.0 / first_correct_rank
    except ValueError:
        mrr = 0.0

    # 4. nDCG@10 (Simplified for binary relevance)
    # We pad with zeros if fewer than 10 results
    y_true = [1] * len(true_relevant_urls) 
    # For nDCG, we need a list of scores. Since we don't have labeled non-relevant docs,
    # we assume the 'true' list is the ideal ordering.
    # This is a simplified nDCG calc using sklearn
    if sum(relevance_vector) == 0:
        ndcg = 0.0
    else:
        # Create a "Ideal" vector (sorted 1s) and "Actual" vector
        actual_scores = relevance_vector[:TOP_K_PRECISION]
        if len(actual_scores) < TOP_K_PRECISION:
            actual_scores += [0] * (TOP_K_PRECISION - len(actual_scores))
            
        ideal_scores = sorted(actual_scores, reverse=True)
        ndcg = ndcg_score([ideal_scores], [actual_scores])

    return precision_at_k, recall_at_k, mrr, ndcg

# --- 4. MAIN LOOP ---
if __name__ == "__main__":
    if not os.path.exists(GROUND_TRUTH_FILE):
        print(f"Error: {GROUND_TRUTH_FILE} not found. Please create it first.")
    else:
        df = pd.read_csv(GROUND_TRUTH_FILE)
        
        # Group by query to get all relevant URLs for a single query
        grouped = df.groupby('query')['relevant_url'].apply(list).to_dict()
        
        total_precision = 0
        total_recall = 0
        total_mrr = 0
        total_ndcg = 0
        count = 0
        
        print(f"\nEvaluating on {len(grouped)} queries...\n")
        print(f"{'Query':<30} | {'P@10':<6} | {'R@50':<6} | {'MRR':<6} | {'nDCG':<6}")
        print("-" * 75)
        
        for query, true_urls in grouped.items():
            start_time = time.time()
            retrieved_urls = search(query, top_k=TOP_K_RECALL)
            
            p, r, mrr, ndcg = calculate_metrics(retrieved_urls, true_urls)
            
            total_precision += p
            total_recall += r
            total_mrr += mrr
            total_ndcg += ndcg
            count += 1
            
            print(f"{query[:28]:<30} | {p:.4f} | {r:.4f} | {mrr:.4f} | {ndcg:.4f}")

        # --- SUMMARY ---
        print("\n" + "="*30)
        print("FINAL EVALUATION RESULTS")
        print("="*30)
        print(f"Mean Precision@10:  {total_precision/count:.4f}  (Target: >= 0.6)")
        print(f"Mean Recall@50:     {total_recall/count:.4f}     (Target: >= 0.5)")
        print(f"Mean MRR:           {total_mrr/count:.4f}        (Target: >= 0.4)")
        print(f"Mean nDCG@10:       {total_ndcg/count:.4f}       (Target: >= 0.5)")
        print("="*30)