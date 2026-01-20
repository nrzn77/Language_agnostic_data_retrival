import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def reciprocal_rank_fusion(ranked_lists, k=60):
    """
    Combines multiple ranked lists into one using the RRF algorithm.
    """
    fused_scores = {}
    for ranked_list in ranked_lists:
        for rank, doc_id in enumerate(ranked_list):
            # RRF Formula: 1 / (rank + k)
            score = 1.0 / (rank + k)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + score
            
    # Sort by the new fused score
    return sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

def hybrid_retrieval_optimized(query_data, docs, bm25, doc_embeddings, model, top_n=10):
    """
    Module C: Performs parallel search and combines results.
    """
    # 1. Lexical Search (BM25)
    # We use the translated query to ensure we search the target language
    tokenized_query = query_data['translated'].split()
    bm25_scores = bm25.get_scores(tokenized_query)
    # Get top 50 lexical candidates
    lexical_top_indices = np.argsort(bm25_scores)[::-1][:50]
    
    # 2. Semantic Search (LaBSE)
    # We encode the original query (LaBSE is language-agnostic)
    query_vector = model.encode([query_data['query']])
    semantic_similarities = cosine_similarity(query_vector, doc_embeddings)[0]
    # Get top 50 semantic candidates
    semantic_top_indices = np.argsort(semantic_similarities)[::-1][:50]
    
    # 3. Fusion (RRF)
    # Merge the rank lists from both models
    fused_results = reciprocal_rank_fusion([lexical_top_indices, semantic_top_indices])
    
    # 4. Final Ranking
    final_output = []
    for doc_idx, score in fused_results[:top_n]:
        doc = docs[doc_idx]
        final_output.append({
            "id": doc_idx,
            "title": doc['title'],
            "url": doc['url'],
            "score": round(score, 4), # RRF score for Module D
            "language": doc['language']
        })
        
    return final_output

# Example Test:
# results = hybrid_retrieval_optimized(query_data, docs, bm25, embeddings, semantic_model)