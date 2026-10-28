"""Unigram Language Model with Bayesian Dirichlet Prior Smoothing.

Scores documents by query likelihood under a smoothed unigram multinomial distribution.
"""

from collections import Counter
import math
from typing import List, Tuple, Dict, Any, Set
from src.ir.index import InvertedIndex, tokenize


class LanguageModelRanker:
    """Query Likelihood Model with Dirichlet smoothing."""

    def __init__(self, index: InvertedIndex, mu: float = 2000.0) -> None:
        self.index = index
        self.mu = mu
        # Compute collection frequencies cf(t) for every term
        self.collection_freq: Dict[str, int] = {}
        for term, postings in self.index.postings.items():
            self.collection_freq[term] = sum(tf for _, tf in postings)
        self.total_tokens = self.index.total_tokens if self.index.total_tokens > 0 else 1

    def score_query(self, query: str, top_k: int = 10, min_match_ratio: float = 0.0) -> List[Tuple[str, float]]:
        """Score documents containing at least one query term using Dirichlet smoothed log-likelihood."""
        detailed = self.score_query_detailed(query, top_k=top_k, min_match_ratio=min_match_ratio)
        return [(item["doc_id"], item["score"]) for item in detailed]

    def score_query_detailed(self, query: str, top_k: int = 10, min_match_ratio: float = 0.0) -> List[Dict[str, Any]]:
        """Score documents with Dirichlet smoothing and return detailed diagnostics."""
        query_terms = tokenize(query)
        if not query_terms:
            return []

        unique_terms: Set[str] = set(query_terms)
        num_query_terms = len(unique_terms)

        # Find candidate documents that contain at least one query term
        candidate_docs: Set[str] = set()
        for term in unique_terms:
            for doc_id, _ in self.index.get_postings(term):
                candidate_docs.add(doc_id)

        if not candidate_docs:
            return []

        # Build term frequency lookup per candidate doc for query terms
        doc_term_freq: Dict[str, Dict[str, int]] = {doc_id: {} for doc_id in candidate_docs}
        for term in unique_terms:
            for doc_id, tf in self.index.get_postings(term):
                doc_term_freq[doc_id][term] = tf

        query_counts = Counter(query_terms)
        ranked_results: List[Dict[str, Any]] = []

        for doc_id in candidate_docs:
            doc_len = self.index.doc_lengths.get(doc_id, 0)
            log_prob = 0.0
            matched_terms = [t for t in unique_terms if doc_term_freq[doc_id].get(t, 0) > 0]
            match_ratio = len(matched_terms) / num_query_terms if num_query_terms > 0 else 0.0

            if match_ratio < min_match_ratio:
                continue

            for term, q_count in query_counts.items():
                tf = doc_term_freq[doc_id].get(term, 0)
                cf = self.collection_freq.get(term, 0)
                p_c = cf / self.total_tokens if self.total_tokens > 0 else 1e-9
                if p_c <= 0:
                    p_c = 1e-9

                smoothed_prob = (tf + self.mu * p_c) / (doc_len + self.mu)
                log_prob += q_count * math.log(smoothed_prob)

            ranked_results.append({
                "doc_id": doc_id,
                "score": log_prob,
                "matched_terms": sorted(matched_terms),
                "match_ratio": match_ratio,
                "matched_count": len(matched_terms),
                "total_query_terms": num_query_terms,
            })

        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results[:top_k]
