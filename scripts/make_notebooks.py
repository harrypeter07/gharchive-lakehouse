"""Script to generate interactive lab notebooks for IR and Deep Learning."""

import json
from pathlib import Path


def make_notebook(cells, filepath):
    nb = {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.11"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    Path(filepath).write_text(json.dumps(nb, indent=2), encoding="utf-8")


# 1. IR Lab Notebook
ir_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Information Retrieval Lab: Inverted Index, BM25, and Language Model\n",
            "\n",
            "In this lab, we build an end-to-end Information Retrieval (IR) and text classification pipeline\n",
            "from scratch over GitHub Archive issues.\n",
            "\n",
            "### Topics Covered:\n",
            "1. Inverted Indexing & Postings Lists\n",
            "2. Robertson-Sparck Jones IDF\n",
            "3. Okapi BM25 Ranking\n",
            "4. Query Likelihood Model (QLM) with Dirichlet Smoothing\n",
            "5. Multinomial Naive Bayes Classifier with Laplace Smoothing"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "from pathlib import Path\n",
            "# Ensure project root is in sys.path\n",
            "sys.path.append(str(Path('.').resolve()))\n",
            "\n",
            "import pyarrow.parquet as pq\n",
            "from src.ir.index import InvertedIndex, tokenize\n",
            "from src.ir.bm25 import BM25Ranker\n",
            "from src.ir.lm import LanguageModelRanker\n",
            "from src.ir.naive_bayes import MultinomialNaiveBayes\n",
            "\n",
            "print('IR modules imported successfully!')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Load Curated Splits\n",
            "We load the 80/10/10 train/validation/test partitions generated from the cleaned Lakehouse."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "splits_table = pq.read_table('data/curated/splits.parquet')\n",
            "records = splits_table.to_pylist()\n",
            "train_records = [r for r in records if r['split'] == 'train']\n",
            "test_records = [r for r in records if r['split'] == 'test']\n",
            "print(f'Total issues: {len(records)} | Train: {len(train_records)} | Test: {len(test_records)}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Build Inverted Index\n",
            "An inverted index maps terms to a postings list of `(document_id, term_frequency)`."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "index = InvertedIndex()\n",
            "for r in train_records:\n",
            "    index.add_document(r['event_id'], f\"{r['title']} {r['body']}\", metadata=r)\n",
            "index.finalize()\n",
            "print(f'Indexed documents: {index.doc_count}')\n",
            "print(f'Unique vocabulary terms: {len(index.postings)}')\n",
            "print(f'Average document length: {index.avg_doc_length:.2f} tokens')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Okapi BM25 Ranking\n",
            "We rank documents using the Okapi BM25 scoring formula."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "bm25 = BM25Ranker(index, k1=1.5, b=0.75)\n",
            "query = 'database connection pool timeout'\n",
            "results = bm25.score_query(query, top_k=5)\n",
            "for doc_id, score in results:\n",
            "    meta = index.doc_metadata[doc_id]\n",
            "    print(f\"Score: {score:.3f} | [{meta['label']}] {meta['title']} ({meta['repo_name']})\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Query Likelihood Model (Dirichlet Prior)\n",
            "We score documents using Bayesian Dirichlet smoothed unigram language models."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "lm = LanguageModelRanker(index, mu=2000.0)\n",
            "lm_results = lm.score_query(query, top_k=5)\n",
            "for doc_id, score in lm_results:\n",
            "    meta = index.doc_metadata[doc_id]\n",
            "    print(f\"Log-Likelihood: {score:.3f} | [{meta['label']}] {meta['title']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Multinomial Naive Bayes Classifier\n",
            "We train a generative probabilistic classifier with Laplace add-one smoothing."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "train_texts = [f\"{r['title']} {r['body']}\" for r in train_records]\n",
            "train_labels = [r['label'] for r in train_records]\n",
            "test_texts = [f\"{r['title']} {r['body']}\" for r in test_records]\n",
            "test_labels = [r['label'] for r in test_records]\n",
            "\n",
            "nb = MultinomialNaiveBayes(alpha=1.0)\n",
            "nb.fit(train_texts, train_labels)\n",
            "metrics = nb.evaluate(test_texts, test_labels)\n",
            "print(f\"Test Accuracy: {metrics['accuracy']*100:.2f}%\")\n",
            "print(f\"Macro F1-Score: {metrics['macro_f1']*100:.2f}%\")\n",
            "print('\\nPer-Class Metrics:')\n",
            "for c, stats in metrics['per_class'].items():\n",
            "    print(f\"  {c:15s} P={stats['precision']:.3f} R={stats['recall']:.3f} F1={stats['f1']:.3f}\")"
        ]
    }
]

# 2. Deep Learning Lab Notebook
dl_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Deep Learning Lab: 1D-CNN Issue Classifier\n",
            "\n",
            "In this lab, we build, train, and inspect a 1D Convolutional Neural Network (CNN)\n",
            "for categorizing developer issues from GitHub Archive.\n",
            "\n",
            "### Architecture:\n",
            "1. Tokenizer & Embedding Layer (vocab_size -> 64)\n",
            "2. 1D Convolution (filter size 3, 64 channels)\n",
            "3. ReLU Non-Linearity\n",
            "4. Global Max-over-Time Pooling\n",
            "5. Dropout (0.2) & Linear Classification Head (64 -> 4 classes)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "from pathlib import Path\n",
            "sys.path.append(str(Path('.').resolve()))\n",
            "\n",
            "import pyarrow.parquet as pq\n",
            "from src.ml.dataset import IssueVocabulary\n",
            "from src.ml.model import create_issue_cnn\n",
            "\n",
            "print('DL modules imported successfully!')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Load Data and Inspect Vocabulary\n",
            "We build the vocabulary strictly from the training split to prevent data leakage."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "splits_table = pq.read_table('data/curated/splits.parquet')\n",
            "records = splits_table.to_pylist()\n",
            "train_texts = [f\"{r['title']} {r['body']}\" for r in records if r['split'] == 'train']\n",
            "\n",
            "vocab = IssueVocabulary(min_freq=2)\n",
            "vocab.build_from_texts(train_texts)\n",
            "print(f'Training Vocabulary size: {len(vocab):,} unique tokens')\n",
            "\n",
            "sample = 'Fatal panic in go runtime during garbage collection'\n",
            "encoded = vocab.encode(sample, max_len=15)\n",
            "print(f'Sample: {sample}')\n",
            "print(f'Encoded IDs: {encoded}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Inspect Model Architecture\n",
            "We verify layer shapes and parameter counts."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "try:\n",
            "    import torch\n",
            "    model = create_issue_cnn(vocab_size=len(vocab), num_classes=4)\n",
            "    print(model)\n",
            "    total_params = sum(p.numel() for p in model.parameters())\n",
            "    print(f'Total Trainable Parameters: {total_params:,}')\n",
            "except ImportError:\n",
            "    print('PyTorch not yet installed in local environment.')"
        ]
    }
]

if __name__ == "__main__":
    make_notebook(ir_cells, "notebooks/ir_lab.ipynb")
    make_notebook(dl_cells, "notebooks/dl_lab.ipynb")
    print("Successfully generated notebooks/ir_lab.ipynb and notebooks/dl_lab.ipynb")
