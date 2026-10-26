"""Text indexing and inverted index engine for Information Retrieval.

Implements text preprocessing, tokenization, vocabulary collection,
and inverted index construction mapping tokens to postings lists (doc_id, term_frequency).
"""

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple, Any

# Standard minimal English stopword list (no external library required)
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

TOKEN_PATTERN = re.compile(r"\b[a-z0-9_]{2,}\b")


def tokenize(text: str) -> List[str]:
    """Lowercase text and extract alphanumeric tokens while dropping stopwords."""
    if not text:
        return []
    words = TOKEN_PATTERN.findall(text.lower())
    return [w for w in words if w not in STOPWORDS]


class InvertedIndex:
    """Inverted index maintaining postings lists, document lengths, and corpus statistics."""

    def __init__(self) -> None:
        self.doc_count: int = 0
        self.doc_lengths: Dict[str, int] = {}
        self.postings: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.total_tokens: int = 0
        self.avg_doc_length: float = 0.0
        self.doc_metadata: Dict[str, Dict[str, Any]] = {}

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        """Tokenize document text and index term frequencies."""
        tokens = tokenize(text)
        doc_len = len(tokens)
        self.doc_lengths[doc_id] = doc_len
        self.total_tokens += doc_len
        self.doc_count += 1
        if metadata:
            self.doc_metadata[doc_id] = metadata

        counts = Counter(tokens)
        for term, freq in counts.items():
            self.postings[term].append((doc_id, freq))

    def finalize(self) -> None:
        """Compute summary statistics after all documents are indexed."""
        self.avg_doc_length = self.total_tokens / self.doc_count if self.doc_count > 0 else 0.0

    def document_frequency(self, term: str) -> int:
        """Return the number of documents containing the term."""
        return len(self.postings.get(term, []))

    def get_postings(self, term: str) -> List[Tuple[str, int]]:
        """Return postings list [(doc_id, term_frequency)] for a given term."""
        return self.postings.get(term, [])

    def idf(self, term: str) -> float:
        """Compute Robertson-Spärck Jones IDF with additive smoothing."""
        df = self.document_frequency(term)
        if df == 0:
            return 0.0
        # Standard Lucene/BM25 IDF formula: ln(1 + (N - df + 0.5) / (df + 0.5))
        numerator = self.doc_count - df + 0.5
        denominator = df + 0.5
        return math.log(1.0 + (numerator / denominator))
