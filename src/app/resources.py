"""Cached local artifacts shared by dashboard sections."""
import json
import torch
import pyarrow.parquet as pq
import streamlit as st
from src.common.config import CURATED_DATA_DIR, DL_CPU_THREADS
from src.ml.model import create_issue_cnn
from src.ml.dataset import IssueVocabulary
from src.ir.index import InvertedIndex
from src.ir.naive_bayes import MultinomialNaiveBayes

torch.set_num_threads(DL_CPU_THREADS)

@st.cache_resource
def load_cnn_model():
    """Load PyTorch 1D-CNN and vocabulary directly from curated artifacts."""
    vocab_file = CURATED_DATA_DIR / "vocab.json"
    weights_file = CURATED_DATA_DIR / "cnn_weights.pt"
    if not (vocab_file.exists() and weights_file.exists()):
        return None, None

    with open(vocab_file, "r", encoding="utf-8") as f:
        token2id = json.load(f)
    vocab = IssueVocabulary()
    vocab.token2id = token2id
    vocab.id2token = {int(v): k for k, v in token2id.items()}

    cnn = create_issue_cnn(vocab_size=len(token2id), num_classes=4, embed_dim=64, num_filters=64)
    cnn.load_state_dict(torch.load(weights_file, map_location="cpu", weights_only=True))
    cnn.eval()
    return cnn, vocab


@st.cache_resource
def load_ir_and_nb_models():
    """Load Inverted Index and Naive Bayes from curated training splits."""
    splits_path = CURATED_DATA_DIR / "splits.parquet"
    if not splits_path.exists():
        return None, None, []

    table = pq.read_table(splits_path)
    records = table.to_pylist()
    train_records = [r for r in records if r["split"] == "train"]

    index = InvertedIndex()
    for d in train_records[:8000]:
        index.add_document(d["event_id"], f"{d['title']} {d['body']}", metadata=d)
    index.finalize()

    nb = MultinomialNaiveBayes(alpha=1.0)
    nb.fit([f"{d['title']} {d['body']}" for d in train_records], [d["label"] for d in train_records])

    return index, nb, records

