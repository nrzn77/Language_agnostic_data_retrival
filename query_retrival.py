import time
import numpy as np
import jellyfish
from sklearn.metrics.pairwise import cosine_similarity
from Querying import module_b_pipeline

def hybrid_search_final(query_text, docs, bm25, doc_embeddings, model, top_n=30):
    start_time = time.time()

    # --- Module B: Query Processing ---
    query_data = module_b_pipeline(query_text)
    
    # Expand search tokens to include both original and translated for BM25
    search_tokens = query_data['search_terms'][0].split() + query_data['search_terms'][1].split()
    bm25_scores = bm25.get_scores(search_tokens)
    
    # --- Stage 1: Balanced Candidate Retrieval ---
    sorted_indices = np.argsort(bm25_scores)[::-1]
    en_candidates = []
    bn_candidates = []
    
    for idx in sorted_indices:
        lang = docs[idx].get('language', '')
        if lang == 'en' and len(en_candidates) < 50:
            en_candidates.append(idx)
        elif lang == 'bn' and len(bn_candidates) < 50:
            bn_candidates.append(idx)
        if len(en_candidates) >= 50 and len(bn_candidates) >= 50:
            break
    
    # Combine candidates
    candidate_indices = np.array(en_candidates + bn_candidates)
    
    # --- Stage 2: Scoring ---
    # Semantic scores
    query_vec = model.encode([query_text], convert_to_numpy=True)
    candidate_embeddings = doc_embeddings[candidate_indices]
    semantic_scores = cosine_similarity(query_vec, candidate_embeddings)[0]
    
    # Fuzzy scores
    fuzzy_scores = np.array([jellyfish.jaro_winkler_similarity(query_text, docs[idx]['title']) 
                             for idx in candidate_indices])
    
    # Raw BM25 scores for candidates
    c_bm25_raw = bm25_scores[candidate_indices]

    # --- Stage 3: Language-Specific Normalization (The Fix) ---
    final_hybrid_scores = np.zeros(len(candidate_indices))
    
    for lang in ['en', 'bn']:
        # Create a mask for the current language within the candidate list
        mask = [i for i, idx in enumerate(candidate_indices) if docs[idx].get('language') == lang]
        
        if not mask:
            continue
            
        # Extract scores for this specific language
        lang_bm25 = c_bm25_raw[mask]
        lang_semantic = semantic_scores[mask]
        lang_fuzzy = fuzzy_scores[mask]
        
        # Local Normalization Helper
        def min_max_norm(arr):
            denom = (np.max(arr) - np.min(arr) + 1e-9)
            return (arr - np.min(arr)) / denom

        # Normalize components within the language group
        norm_bm25 = min_max_norm(lang_bm25)
        norm_semantic = min_max_norm(lang_semantic)
        norm_fuzzy = min_max_norm(lang_fuzzy)
        
        # Apply Assignment Formula: 0.4 * BM25 + 0.5 * Semantic + 0.1 * Fuzzy
        # This gives the best BN doc a fair shot against the best EN doc
        lang_final_scores = (0.4 * norm_bm25) + (0.5 * norm_semantic) + (0.1 * norm_fuzzy)
        
        # Map back to the main final_hybrid_scores array
        for i, original_pos in enumerate(mask):
            final_hybrid_scores[original_pos] = lang_final_scores[i]

    # --- Stage 4: Final Ranking ---
    rank_indices = np.argsort(final_hybrid_scores)[::-1][:top_n]
    final_docs_indices = candidate_indices[rank_indices]
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    results = []
    for i, idx in enumerate(final_docs_indices):
        confidence = final_hybrid_scores[rank_indices[i]]
        results.append({
            "title": docs[idx]['title'],
            "url": docs[idx]['url'],
            "score": round(float(confidence), 4),
            "language": docs[idx]['language']
        })
        
    warning = None
    if results and results[0]['score'] < 0.20:
        warning = f"Warning: Low matching confidence (score: {results[0]['score']})."

    return {
        "results": results,
        "latency_ms": round(execution_time_ms, 2), 
        "warning": warning,
        "processed_query": query_data['translated']
    }