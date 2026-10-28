"""Okapi BM25 ranking model for information retrieval.

Scores documents against tokenized user queries using term frequency saturation,
document length penalization, and query coordination matching.
"""

from collections import defaultdict
from typing import List, Tuple, Dict, Any, Set
from src.ir.index import InvertedIndex, tokenize


class BM25Ranker:
    """Okapi BM25 ranker over an InvertedIndex."""

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75) -> None:
        self.index = index
        self.k1 = k1
        self.b = b

    def score_query(self, query: str, top_k: int = 10, min_match_ratio: float = 0.0) -> List[Tuple[str, float]]:
        """Score all matching documents for the query string and return top_k (doc_id, score)."""
        detailed = self.score_query_detailed(query, top_k=top_k, min_match_ratio=min_match_ratio)
        return [(item["doc_id"], item["score"]) for item in detailed]

    def score_query_detailed(self, query: str, top_k: int = 10, min_match_ratio: float = 0.0) -> List[Dict[str, Any]]:
        """Score documents with query coordination matching and return detailed diagnostics."""
        query_terms = tokenize(query)
        if not query_terms:
            return []

        unique_terms: Set[str] = set(query_terms)
        num_query_terms = len(unique_terms)
        doc_scores: Dict[str, float] = {}
        doc_matched_terms: Dict[str, Set[str]] = defaultdict(set)
        avgdl = self.index.avg_doc_length if self.index.avg_doc_length > 0 else 1.0

        for term in unique_terms:
            idf = self.index.idf(term)
            if idf <= 0.0:
                continue

            postings = self.index.get_postings(term)
            for doc_id, tf in postings:
                doc_matched_terms[doc_id].add(term)
                doc_len = self.index.doc_lengths.get(doc_id, 0)
                len_norm = 1.0 - self.b + self.b * (doc_len / avgdl)
                tf_component = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)
                score = idf * tf_component
                doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + score

        ranked_results: List[Dict[str, Any]] = []
        for doc_id, raw_score in doc_scores.items():
            matched = doc_matched_terms[doc_id]
            match_ratio = len(matched) / num_query_terms if num_query_terms > 0 else 0.0
            if match_ratio < min_match_ratio:
                continue

            # Query coordination matching factor: reward documents satisfying multiple query terms
            coord_factor = 1.0 + 1.2 * (match_ratio ** 2)
            final_score = raw_score * coord_factor

            ranked_results.append({
                "doc_id": doc_id,
                "score": final_score,
                "raw_score": raw_score,
                "matched_terms": sorted(list(matched)),
                "match_ratio": match_ratio,
                "matched_count": len(matched),
                "total_query_terms": num_query_terms,
            })

        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results[:top_k]
