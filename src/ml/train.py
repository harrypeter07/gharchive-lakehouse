"""Training and evaluation pipeline for 1D-CNN issue classifier.

Trains a 1D-CNN text classifier on curated splits using PyTorch on CPU,
evaluates accuracy and macro-F1, and appends benchmarks to docs/RESULTS.md.
"""

from pathlib import Path
import random
import time
from typing import Dict, Any, List
import pyarrow.parquet as pq

from src.common.config import CURATED_DATA_DIR, GLOBAL_SEED, PROJECT_ROOT
from src.ml.dataset import IssueVocabulary, PAD_IDX
from src.ml.model import create_issue_cnn

LABEL_MAP = {"bug": 0, "enhancement": 1, "documentation": 2, "question": 3}
INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}


def set_seed(seed: int = GLOBAL_SEED) -> None:
    """Set global seeds for reproducibility."""
    import torch
    random.seed(seed)
    torch.manual_seed(seed)


def train_cnn(epochs: int = 4, batch_size: int = 64) -> Dict[str, Any]:
    """Train 1D-CNN on training split and evaluate on test split."""
    import torch
    import torch.nn as nn
    from torch.utils.data import TensorDataset, DataLoader

    set_seed(GLOBAL_SEED)
    splits_path = CURATED_DATA_DIR / "splits.parquet"
    if not splits_path.exists():
        raise FileNotFoundError(f"{splits_path} missing. Run src.ir.split first.")

    table = pq.read_table(splits_path)
    records = table.to_pylist()

    train_records = [r for r in records if r["split"] == "train"]
    val_records = [r for r in records if r["split"] == "val"]
    test_records = [r for r in records if r["split"] == "test"]

    # 1. Build vocabulary strictly on training split
    train_texts = [f"{r['title']} {r['body']}" for r in train_records]
    vocab = IssueVocabulary(min_freq=2)
    vocab.build_from_texts(train_texts)

    # 2. Encode datasets into PyTorch Tensors
    def prepare_tensors(data: List[Dict[str, Any]]):
        X = [vocab.encode(f"{d['title']} {d['body']}") for d in data]
        y = [LABEL_MAP[d["label"]] for d in data]
        return torch.tensor(X, dtype=torch.long), torch.tensor(y, dtype=torch.long)

    X_train, y_train = prepare_tensors(train_records)
    X_val, y_val = prepare_tensors(val_records)
    X_test, y_test = prepare_tensors(test_records)

    train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=batch_size, shuffle=False)

    # 3. Initialize Model, Loss, Optimizer
    model = create_issue_cnn(vocab_size=len(vocab), num_classes=len(LABEL_MAP))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # 4. Training Loop
    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

    # 5. Evaluate on Test Split
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            logits = model(batch_x)
            preds = torch.argmax(logits, dim=1)
            all_preds.extend(preds.tolist())
            all_targets.extend(batch_y.tolist())

    correct = sum(1 for p, y in zip(all_preds, all_targets) if p == y)
    accuracy = correct / len(all_targets) if all_targets else 0.0

    # Macro F1
    num_classes = len(LABEL_MAP)
    f1_scores = []
    for c in range(num_classes):
        tp = sum(1 for p, y in zip(all_preds, all_targets) if p == c and y == c)
        fp = sum(1 for p, y in zip(all_preds, all_targets) if p == c and y != c)
        fn = sum(1 for p, y in zip(all_preds, all_targets) if p != c and y == c)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        f1_scores.append(f1)
    macro_f1 = sum(f1_scores) / num_classes

    # Append to docs/RESULTS.md
    results_path = PROJECT_ROOT / "docs" / "RESULTS.md"
    dl_summary = f"""
## 3. Deep Learning: 1D-CNN Classifier
- **Architecture**: Embedding(dim=64) -> Conv1D(64, kernel=3) -> ReLU -> MaxPool1D -> Dropout(0.2) -> Linear(4)
- **Vocabulary Size (Train Only)**: {len(vocab):,} tokens
- **Training Epochs**: {epochs}
- **Test Accuracy**: **{accuracy * 100:.2f}%**
- **Macro F1-Score**: **{macro_f1 * 100:.2f}%**

### Model Comparison
| Model | Type | Test Accuracy | Macro F1 |
| :--- | :--- | :--- | :--- |
| **Multinomial Naive Bayes** | Probabilistic n-gram | 75.94% | 56.22% |
| **1D-CNN** | Deep Convolutional | **{accuracy * 100:.2f}%** | **{macro_f1 * 100:.2f}%** |
"""
    if results_path.exists():
        existing = results_path.read_text(encoding="utf-8")
        if "## 3. Deep Learning: 1D-CNN Classifier" not in existing:
            results_path.write_text(existing + dl_summary, encoding="utf-8")

    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "vocab_size": len(vocab),
    }


if __name__ == "__main__":
    res = train_cnn()
    print(f"1D-CNN Training Complete: {res}")
