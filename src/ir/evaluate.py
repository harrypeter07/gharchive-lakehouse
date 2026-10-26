"""Evaluation runner for IR models (BM25, Language Model) and Naive Bayes classifier.

Evaluates BM25 and Unigram LM on standard developer search queries,
trains and evaluates Naive Bayes on curated splits,
and logs metrics to docs/RESULTS.md.
"""

from collections import defaultdict
from pathlib import Path
import json
import time
from typing import Dict, List, Any
import pyarrow.parquet as pq

from src.ir.index import InvertedIndex, tokenize
from src.ir.bm25 import BM25Ranker
from src.ir.lm import LanguageModelRanker
from src.ir.naive_bayes import MultinomialNaiveBayes
from src.common.config import CURATED_DATA_DIR, PROJECT_ROOT

EVAL_QUERIES = [
    "fix null pointer exception",
    "memory leak in connection pool",
    "documentation update install instructions",
    "how to configure ssl certificate",
    "segmentation fault on startup",
    "add dark mode support",
    "timeout error during database query",
    "broken link in readme",
    "support for python 3.12",
    "cors header missing in api response",
    "deadlock when running concurrent transactions",
    "feature request export to excel",
    "update dependencies to latest version",
    "failed to compile rust crate",
    "cannot resolve hostname dns error",
    "add unit tests for parser",
    "improve performance of batch processing",
    "authentication failed invalid token",
    "unexpected end of file json",
    "docker compose healthcheck failing",
]


def load_splits(splits_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load splits parquet into train, val, and test partitions."""
    table = pq.read_table(splits_path)
    records = table.to_pylist()
    partitions = defaultdict(list)
    for r in records:
        partitions[r["split"]].append(r)
    return partitions


def build_corpus_index(documents: List[Dict[str, Any]]) -> InvertedIndex:
    """Build and finalize an inverted index from issue documents."""
    index = InvertedIndex()
    for doc in documents:
        text = f"{doc['title']} {doc['body']}"
        index.add_document(doc["event_id"], text, metadata=doc)
    index.finalize()
    return index


def evaluate_retrieval(index: InvertedIndex, queries: List[str]) -> Dict[str, Any]:
    """Evaluate BM25 and LM rankers across query set."""
    bm25 = BM25Ranker(index)
    lm = LanguageModelRanker(index, mu=2000.0)

    bm25_matches: List[int] = []
    lm_matches: List[int] = []

    for q in queries:
        bm_res = bm25.score_query(q, top_k=10)
        lm_res = lm.score_query(q, top_k=10)
        bm25_matches.append(len(bm_res))
        lm_matches.append(len(lm_res))

    return {
        "num_queries": len(queries),
        "bm25_avg_results_per_query": sum(bm25_matches) / len(bm25_matches),
        "lm_avg_results_per_query": sum(lm_matches) / len(lm_matches),
    }


def run_evaluation() -> Dict[str, Any]:
    """Execute end-to-end evaluation and write docs/RESULTS.md."""
    splits_path = CURATED_DATA_DIR / "splits.parquet"
    if not splits_path.exists():
        raise FileNotFoundError(f"{splits_path} not found. Run src.ir.split first.")

    splits = load_splits(splits_path)
    train_docs = splits["train"]
    val_docs = splits["val"]
    test_docs = splits["test"]

    # 1. Build Index on combined Train + Val (15,324 documents)
    index_corpus = train_docs + val_docs
    index = build_corpus_index(index_corpus)

    # 2. Information Retrieval Evaluation
    ir_results = evaluate_retrieval(index, EVAL_QUERIES)

    # 3. Naive Bayes Classification
    train_texts = [f"{d['title']} {d['body']}" for d in train_docs]
    train_labels = [d["label"] for d in train_docs]

    test_texts = [f"{d['title']} {d['body']}" for d in test_docs]
    test_labels = [d["label"] for d in test_docs]

    nb = MultinomialNaiveBayes(alpha=1.0)
    nb.fit(train_texts, train_labels)
    nb_metrics = nb.evaluate(test_texts, test_labels)

    # 4. Generate docs/RESULTS.md
    results_path = PROJECT_ROOT / "docs" / "RESULTS.md"
    md_content = f"""# Experimental Results & Model Evaluation

Generated on: {time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}

## 1. Information Retrieval (IR) Benchmarks
- **Corpus Size**: {index.doc_count:,} indexed GitHub issue documents
- **Vocabulary Size**: {len(index.postings):,} unique terms
- **Average Document Length**: {index.avg_doc_length:.2f} tokens
- **Test Query Set**: 20 developer and DevOps search queries

| Model | Smoothing / Tuning | Top-10 Retrieval Rate |
| :--- | :--- | :--- |
| **BM25** | $k_1=1.5, b=0.75$ | {ir_results['bm25_avg_results_per_query']:.1f} / 10 results/query |
| **Language Model (QLM)** | Dirichlet prior $\\mu=2000.0$ | {ir_results['lm_avg_results_per_query']:.1f} / 10 results/query |

---

## 2. Multinomial Naive Bayes Issue Classifier
- **Train split**: {len(train_docs):,} samples
- **Test split**: {len(test_docs):,} samples
- **Overall Accuracy**: **{nb_metrics['accuracy'] * 100:.2f}%**
- **Macro F1-Score**: **{nb_metrics['macro_f1'] * 100:.2f}%**

### Per-Class Performance
| Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
"""
    for c, stats in sorted(nb_metrics["per_class"].items()):
        md_content += f"| **{c}** | {stats['precision']:.4f} | {stats['recall']:.4f} | {stats['f1']:.4f} | {stats['support']:,} |\n"

    md_content += "\n### Confusion Matrix (Rows = Actual, Columns = Predicted)\n\n"
    header = "| Actual \\ Predicted | " + " | ".join(sorted(nb.classes)) + " |\n"
    sep = "| :--- | " + " | ".join([":---:"] * len(nb.classes)) + " |\n"
    md_content += header + sep
    for actual in sorted(nb.classes):
        row_vals = [str(nb_metrics["confusion_matrix"][actual].get(pred, 0)) for pred in sorted(nb.classes)]
        md_content += f"| **{actual}** | " + " | ".join(row_vals) + " |\n"

    results_path.write_text(md_content, encoding="utf-8")

    return {
        "ir_results": ir_results,
        "nb_accuracy": nb_metrics["accuracy"],
        "nb_macro_f1": nb_metrics["macro_f1"],
        "results_path": str(results_path),
    }


if __name__ == "__main__":
    res = run_evaluation()
    print(f"Evaluation complete: Accuracy={res['nb_accuracy']}, Macro-F1={res['nb_macro_f1']}")
