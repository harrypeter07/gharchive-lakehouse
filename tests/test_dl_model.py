"""Unit tests for PyTorch 1D-CNN Issue Classifier and Curated Artifacts."""

import json
from pathlib import Path
import pytest
import torch

from src.common.config import CURATED_DATA_DIR
from src.ml.model import create_issue_cnn
from src.ml.dataset import IssueVocabulary


def test_dl_artifacts_exist():
    weights_path = CURATED_DATA_DIR / "cnn_weights.pt"
    vocab_path = CURATED_DATA_DIR / "vocab.json"
    splits_path = CURATED_DATA_DIR / "splits.parquet"
    
    assert weights_path.exists(), "cnn_weights.pt missing"
    assert weights_path.stat().st_size > 1_000_000, "cnn_weights.pt is unexpectedly small"
    assert vocab_path.exists(), "vocab.json missing"
    assert splits_path.exists(), "splits.parquet missing"


def test_model_loading_and_inference():
    vocab_path = CURATED_DATA_DIR / "vocab.json"
    weights_path = CURATED_DATA_DIR / "cnn_weights.pt"
    
    with open(vocab_path, "r", encoding="utf-8") as f:
        token2id = json.load(f)
        
    vocab_size = len(token2id)
    assert vocab_size > 10_000, f"Vocabulary unexpectedly small: {vocab_size}"
    
    model = create_issue_cnn(vocab_size=vocab_size, num_classes=4, embed_dim=64, num_filters=64)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert total_params == vocab_size * 64 + 64 * 64 * 3 + 64 + 64 * 4 + 4
    
    # Load state dict
    state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()
    
    # Run test tensor forward pass
    dummy_input = torch.randint(0, vocab_size, (1, 50), dtype=torch.long)
    with torch.no_grad():
        logits = model(dummy_input)
        
    assert logits.shape == (1, 4)
    probs = torch.softmax(logits, dim=-1)
    assert torch.isclose(probs.sum(), torch.tensor(1.0), atol=1e-4)
