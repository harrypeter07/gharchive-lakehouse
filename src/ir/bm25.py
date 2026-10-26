"""Okapi BM25 ranking model for information retrieval.

Scores documents against tokenized user queries using term frequency saturation
and document length penalization.
"""

from typing import List, Tuple
from src.ir.index import InvertedIndex, tokenize


class BM25Ranker:
    """Okapi BM25 ranker over an InvertedIndex."""

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75) -> None:
        self.index = index
        self.k1 = k1
        self.b = b

    def score_query(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Score all matching documents for the query string and return top_k (doc_id, score)."""
        query_terms = tokenize(query)
        if not query_terms:
            return []

        doc_scores: dict[str, float] = {}
        avgdl = self.index.avg_doc_length if self.index.avg_doc_length > 0 else 1.0

        for term in set(query_terms):
            idf = self.index.idf(term)
            if idf <= 0.0:
                continue

            postings = self.index.get_postings(term)
            for doc_id, tf in postings:
                doc_len = self.index.doc_lengths.get(doc_id, 0)
                # Length normalization component
                len_norm = 1.0 - self.b + self.b * (doc_len / avgdl)
                # BM25 TF component
                tf_component = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)
                score = idf * tf_component
                doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + score

        ranked = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
