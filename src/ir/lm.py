"""Unigram Language Model with Bayesian Dirichlet Prior Smoothing.

Scores documents by query likelihood under a smoothed unigram multinomial distribution.
"""

from collections import Counter
import math
from typing import List, Tuple, Dict
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

    def score_query(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Score documents containing at least one query term using Dirichlet smoothed log-likelihood."""
        query_terms = tokenize(query)
        if not query_terms:
            return []

        # Find candidate documents that contain at least one query term
        candidate_docs: set[str] = set()
        for term in set(query_terms):
            for doc_id, _ in self.index.get_postings(term):
                candidate_docs.add(doc_id)

        if not candidate_docs:
            return []

        # Build term frequency lookup per candidate doc for query terms
        doc_term_freq: Dict[str, Dict[str, int]] = {doc_id: {} for doc_id in candidate_docs}
        for term in set(query_terms):
            for doc_id, tf in self.index.get_postings(term):
                doc_term_freq[doc_id][term] = tf

        query_counts = Counter(query_terms)
        scores: Dict[str, float] = {}

        for doc_id in candidate_docs:
            doc_len = self.index.doc_lengths.get(doc_id, 0)
            log_prob = 0.0

            for term, q_count in query_counts.items():
                tf = doc_term_freq[doc_id].get(term, 0)
                cf = self.collection_freq.get(term, 0)
                # Background collection probability P(w|C)
                p_c = cf / self.total_tokens if self.total_tokens > 0 else 1e-9
                if p_c <= 0:
                    p_c = 1e-9

                # Dirichlet smoothed probability: (tf + mu * P(w|C)) / (|D| + mu)
                smoothed_prob = (tf + self.mu * p_c) / (doc_len + self.mu)
                log_prob += q_count * math.log(smoothed_prob)

            scores[doc_id] = log_prob

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
