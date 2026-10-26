"""Unit tests for Information Retrieval and Naive Bayes components."""

from pathlib import Path
import pytest
import pyarrow.parquet as pq

from src.ir.index import InvertedIndex, tokenize
from src.ir.bm25 import BM25Ranker
from src.ir.lm import LanguageModelRanker
from src.ir.naive_bayes import MultinomialNaiveBayes
from src.ir.split import run_split


def test_tokenize():
    text = "Fix: Memory Leak in Database Connection Pool!"
    tokens = tokenize(text)
    assert "memory" in tokens
    assert "leak" in tokens
    assert "database" in tokens
    assert "connection" in tokens
    assert "pool" in tokens
    # Stopwords like 'in' should be removed
    assert "in" not in tokens


def test_inverted_index_and_idf():
    idx = InvertedIndex()
    idx.add_document("doc1", "python spark pipeline")
    idx.add_document("doc2", "python duckdb analytics")
    idx.add_document("doc3", "rust microservice")
    idx.finalize()

    assert idx.doc_count == 3
    assert idx.document_frequency("python") == 2
    assert idx.document_frequency("rust") == 1
    assert idx.document_frequency("nonexistent") == 0

    # Rare word 'rust' should have higher IDF than common word 'python'
    assert idx.idf("rust") > idx.idf("python")


def test_bm25_ranking():
    idx = InvertedIndex()
    idx.add_document("doc1", "crash on startup when loading configuration")
    idx.add_document("doc2", "add new button to user profile settings")
    idx.add_document("doc3", "crash in payment processing checkout startup")
    idx.finalize()

    ranker = BM25Ranker(idx)
    results = ranker.score_query("crash startup", top_k=2)

    assert len(results) == 2
    # doc3 and doc1 contain both terms, doc2 contains none
    ranked_ids = [doc_id for doc_id, score in results]
    assert "doc1" in ranked_ids
    assert "doc3" in ranked_ids
    assert "doc2" not in ranked_ids


def test_bm25_empty_query():
    idx = InvertedIndex()
    idx.add_document("doc1", "just a test")
    idx.finalize()
    ranker = BM25Ranker(idx)
    assert ranker.score_query("") == []


def test_language_model_dirichlet():
    idx = InvertedIndex()
    idx.add_document("doc1", "fix security vulnerability in jwt authentication")
    idx.add_document("doc2", "update readme documentation with install steps")
    idx.finalize()

    lm = LanguageModelRanker(idx, mu=100.0)
    results = lm.score_query("jwt vulnerability")

    assert len(results) >= 1
    # doc1 should be the top match
    assert results[0][0] == "doc1"


def test_naive_bayes_classification():
    train_texts = [
        "fix null pointer exception in parser",
        "segmentation fault on startup crash",
        "add dark mode theme to settings",
        "implement export to csv feature",
        "update contributing guide and api docs",
        "fix typo in documentation tutorial",
    ]
    train_labels = [
        "bug",
        "bug",
        "enhancement",
        "enhancement",
        "documentation",
        "documentation",
    ]

    nb = MultinomialNaiveBayes(alpha=1.0)
    nb.fit(train_texts, train_labels)

    pred_bug = nb.predict("crash caused by exception in thread")
    pred_enhancement = nb.predict("add export button for users")
    pred_docs = nb.predict("documentation update for tutorial guide")

    assert pred_bug == "bug"
    assert pred_enhancement == "enhancement"
    assert pred_docs == "documentation"


def test_splits_disjointness():
    splits_file = Path("data/curated/splits.parquet")
    assert splits_file.exists(), "Splits file must exist"

    table = pq.read_table(splits_file)
    event_ids = table["event_id"].to_pylist()
    splits = table["split"].to_pylist()

    train_ids = set()
    val_ids = set()
    test_ids = set()

    for eid, sp in zip(event_ids, splits):
        if sp == "train":
            train_ids.add(eid)
        elif sp == "val":
            val_ids.add(eid)
        elif sp == "test":
            test_ids.add(eid)

    # Mathematical disjointness check
    assert len(train_ids.intersection(val_ids)) == 0, "Train and Val must be disjoint"
    assert len(train_ids.intersection(test_ids)) == 0, "Train and Test must be disjoint"
    assert len(val_ids.intersection(test_ids)) == 0, "Val and Test must be disjoint"
    assert len(train_ids) + len(val_ids) + len(test_ids) == len(event_ids)
